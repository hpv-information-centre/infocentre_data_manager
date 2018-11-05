""" mysql.py

This module includes the codec implementation for MySQL data sources.

"""

import logging
import re
import datetime
import pandas as pd
import numpy as np
import pymysql.cursors
from pymysql import ProgrammingError
from infocentre_data_manager.plugins.codecs.base import Codec

__all__ = ['MySQLCodec', ]

logger = logging.getLogger(__name__)


class MySQLCodec(Codec):
    """
    Plugin that implements the HPV Information Centre data loading from and
    storing to MySQL data sources.
    """

    # When creating a database column, if the current data exceeds this
    # size a TEXT type is assigned instead.
    VARCHAR_SIZE = 200

    def load(self, **kwargs):
        host = kwargs['host']
        db = kwargs['db']
        user = kwargs['user']
        password = kwargs['password']
        table_name = kwargs['table']

        conn = pymysql.connect(host=host,
                               user=user,
                               password=password,
                               db=db,
                               charset='utf8',
                               cursorclass=pymysql.cursors.DictCursor)

        general = pd.read_sql(
            'SELECT table_name, contents, data_manager, comments '
            'FROM info_tables '
            'WHERE table_name = %s',
            con=conn,
            params=[table_name]
        )

        variables = pd.read_sql(
            'SELECT name AS variable, description, semantic_type AS type '
            'FROM info_vars '
            'WHERE data_table = %s'
            'ORDER BY `order` ASC',
            con=conn,
            params=[table_name]
        )

        data = pd.read_sql('SELECT * FROM {}'.format(table_name), conn)

        sources = self._load_ref_data(conn, table_name, 'sources')
        notes = self._load_ref_data(conn, table_name, 'notes')
        methods = self._load_ref_data(conn, table_name, 'methods')
        years = self._load_ref_data(conn, table_name, 'years')

        dates = self._load_dates_data(conn, table_name)

        conn.close()

        return {
            'general': general,
            'variables': variables,
            'data': data,
            'sources': sources,
            'notes': notes,
            'methods': methods,
            'years': years,
            'dates': dates
        }

    def _load_ref_data(self, conn, table_name, ref_type):
        ref_table = 'ref_{}'.format(ref_type)

        refs = pd.read_sql(
            'SELECT iso, strata_variable, strata_value, '
            ' applyto_variable, value '
            'FROM {}_by b '
            'JOIN {} a ON b.id_{} = a.id '
            'WHERE b.data_table = %s'.format(
                ref_table, ref_table, ref_type[:-1]
            ),
            con=conn,
            params=[table_name]
        )
        return refs

    def _load_dates_data(self, conn, table_name):
        dates = pd.read_sql(
            'SELECT iso, strata_variable, strata_value, '
            ' applyto_variable, date_accessed, date_closing, '
            ' date_delivery, date_published '
            'FROM ref_dates_by '
            'WHERE data_table = %s',
            con=conn,
            params=[table_name]
        )
        date_types = ['date_accessed', 'date_closing',
                      'date_delivery', 'date_published']
        if len(dates.index) > 0:
            for date_type in date_types:
                if dates.iloc[0, :][date_type] is not None:
                    dates.iloc[0, :][date_type] = \
                        dates.iloc[0, :][date_type].strftime('%d-%m-%Y')
                else:
                    dates.iloc[0, :][date_type] = ''
        return dates

    def store(self,
              data,
              batch_size=100,
              use_temporal_db=False,
              **kwargs):
        host = kwargs['host']
        db = kwargs['db']
        user = kwargs['user']
        password = kwargs['password']

        conn = pymysql.connect(host=host,
                               user=user,
                               password=password,
                               db=db,
                               charset='utf8',
                               cursorclass=pymysql.cursors.DictCursor)

        try:
            if kwargs.get('create_table', False):
                self._create_table(conn, data, use_temporal_db)
                conn.commit()
            self._store_general_data(conn, data)
            self._store_variable_data(conn, data)
            self._store_raw_data(conn, data, batch_size)
            self._store_ref_data(conn, data, 'sources')
            self._store_ref_data(conn, data, 'notes')
            self._store_ref_data(conn, data, 'methods')
            self._store_ref_data(conn, data, 'years')
            self._store_dates_data(conn, data)
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e from None

        conn.close()

    def _create_table(self,
                      conn,
                      data,
                      use_temporal_db,
                      default_char_type=None):
        columns_clause = []
        if default_char_type is None:
            default_char_type = 'varchar({})'.format(MySQLCodec.VARCHAR_SIZE)
        for col in data['variables'].itertuples():
            if col.variable == 'id':
                col_clause = 'id INT COMMENT \'{}\''.format(
                    col.description.replace('\'', '\'\'')
                )
            else:
                max_length_col_data = \
                    data['data'][col.variable].str.len().max()
                if max_length_col_data > MySQLCodec.VARCHAR_SIZE:
                    char_type = 'TEXT'
                else:
                    char_type = default_char_type
                col_clause = '`{}` {} COMMENT \'{}\''.format(
                    col.variable,
                    char_type,
                    col.description.replace('\'', '\'\'')
                )
            columns_clause.append(col_clause)

        table_name = data['general']['table_name'].iloc[0]
        sql_string = ('CREATE TABLE {} '
                      '({}, CONSTRAINT {}_PK PRIMARY KEY (id)) '
                      'ENGINE=InnoDB DEFAULT CHARSET=utf8 '
                      'COLLATE=utf8_general_ci'.format(
                          table_name,
                          ','.join(columns_clause),
                          table_name
                      ))
        if use_temporal_db:
            sql_string += ' WITH SYSTEM VERSIONING'

        try:
            with conn.cursor() as cursor:
                cursor.execute(sql_string)
        except pymysql.err.InternalError as e:
            if e.args[0] == pymysql.constants.ER.TABLE_EXISTS_ERROR:
                pass  # Table already exists, skipping generation...
            elif e.args[0] == pymysql.constants.ER.TOO_BIG_ROWSIZE \
                    and char_type != 'TEXT':
                self._create_table(conn,
                                   data,
                                   use_temporal_db,
                                   default_char_type='TEXT')
            else:
                raise e from None

    def _store_general_data(self, conn, data):
        table_name = data['general']['table_name'].iloc[0]
        data_manager = data['general']['data_manager'].iloc[0]
        contents = data['general']['contents'].iloc[0]
        comments = data['general']['comments'].iloc[0]
        module_strings = re.findall(r'_m([\d]*)_', table_name)
        if len(module_strings) > 0:
            module = int(module_strings[0])
        else:
            print('Unknown module, to be determined manually')
            module = -9

        # TODO: Category, indicator?
        table_row = pd.read_sql(
            'SELECT table_name FROM info_tables WHERE table_name = %s',
            params=[table_name], con=conn)

        with conn.cursor() as cursor:
            if len(table_row.index) == 0:
                cursor.execute(
                    'INSERT INTO info_tables '
                    '(table_name, module, data_manager, contents, comments) '
                    'VALUES (%s, %s, %s, %s, %s)',
                    (table_name, module, data_manager, contents, comments))
            else:
                cursor.execute(
                    'UPDATE info_tables '
                    'SET module=%s, data_manager=%s, contents=%s, comments=%s'
                    'WHERE table_name=%s',
                    (module, data_manager, contents, comments, table_name))

    def _store_variable_data(self, conn, data):
        table_name = data['general']['table_name'].iloc[0]

        with conn.cursor() as cursor:
            cursor.execute(
                'DELETE FROM info_vars WHERE data_table = %s',
                [table_name])

        for i, var in enumerate(data['variables'].itertuples()):
            with conn.cursor() as cursor:
                cursor.execute(
                    'INSERT INTO info_vars'
                    ' (data_table, name, description, semantic_type, `order`) '
                    'VALUES (%s, %s, %s, %s, %s)',
                    [table_name, var.variable, var.description, var.type, i]
                    )

    def _store_raw_data(self, conn, data, batch_size):
        table_name = data['general']['table_name'].iloc[0]

        table_data = pd.read_sql(
            'SELECT * FROM {}'.format(table_name), con=conn)
        db_ids = set(table_data['id'])
        excel_ids = set(data['data']['id'])
        ids_to_delete = list(db_ids.difference(excel_ids))
        ids_to_replace = list(excel_ids.difference(db_ids))
        ids_changed = list(set(pd.concat([table_data, data['data']]).
                               drop_duplicates(keep=False)['id'].astype(str)))
        ids_changed = [int(id) for id in ids_changed
                       if int(id) not in ids_to_delete]

        if len(ids_changed) > 0:
            logger.debug(
                'Rows inserted or updated for table {}: ids = {}'.format(
                    table_name, ', '.join(
                        [str(id) for id in ids_changed]
                    )
                )
            )
        if len(ids_to_delete) > 0:
            logger.debug('Rows deleted from table {}: ids = {}'.format(
                table_name, ', '.join(
                    [str(id) for id in ids_to_delete]
                )
            ))

        try:
            for i in range(0, len(ids_to_delete), batch_size + 1):
                upper_bound = i + batch_size
                ids_to_delete_str = [str(id) for id in ids_to_delete]
                conn.query('DELETE FROM {} WHERE id IN ({})'.format(
                    table_name,
                    ','.join(ids_to_delete_str[i:upper_bound])))
        except ProgrammingError:
            raise EnvironmentError(
                "Table '{}' does not exist, create it first.".format(
                    table_name
                ))

        data['data'].index = data['data']['id']
        df_to_replace = data['data'].loc[ids_changed, :]

        for i in range(0, len(df_to_replace.index), batch_size + 1):
            with conn.cursor() as cursor:
                # TODO: Refactor insert string generation
                cursor.execute('REPLACE INTO {} ({}) VALUES {}'.format(
                    table_name,
                    ','.join(['`{}`'.format(col)
                              for col in df_to_replace.columns]),
                    ','.join(['({})'.format(','.join(
                                ["'" + v.replace("'", "\\'") + "'"
                                    if isinstance(v, str) else str(v)
                                 for v in row[1].values]))
                             for row
                             in df_to_replace.iloc[
                                i:min(
                                    len(df_to_replace.index),
                                    i + batch_size
                                    ), :
                             ].iterrows()
                             ]
                             )
                ))

    def _store_ref_data(self, conn, data, ref_type):
        table_name = data['general']['table_name'].iloc[0]

        ref_values = set(data[ref_type].loc[:, 'value'])
        for ref in ref_values:
            existing_ref = pd.read_sql(
                'SELECT value FROM ref_{} WHERE value = %s'.format(ref_type),
                params=[str(ref)],
                con=conn
            )
            if len(existing_ref) == 0:
                with conn.cursor() as cursor:
                    cursor.execute(
                        'INSERT INTO ref_{} (value) VALUES (%s)'.format(
                            ref_type),
                        [str(ref)]
                        )

        with conn.cursor() as cursor:
            cursor.execute(
                'DELETE FROM ref_{}_by WHERE data_table = %s'.format(ref_type),
                [table_name])

        for row in data[ref_type].itertuples():
            with conn.cursor() as cursor:
                cursor.execute(
                    'INSERT INTO ref_{}_by (iso, strata_variable, '
                    'strata_value, applyto_variable, data_table, id_{}) '
                    'VALUES (%s, %s, %s, %s, %s, '
                    ' (SELECT id FROM ref_{} WHERE value=%s))'.format(
                        ref_type, ref_type[:-1], ref_type),
                    [row.iso, row.strata_variable, row.strata_value,
                     row.applyto_variable, table_name, str(row.value)])

    def _store_dates_data(self, conn, data):
        table_name = data['general']['table_name'].iloc[0]

        with conn.cursor() as cursor:
            cursor.execute(
                'DELETE FROM ref_dates_by WHERE data_table = %s',
                [table_name])

        for row in data['dates'].itertuples():
            with conn.cursor() as cursor:
                cursor.execute(
                    'INSERT INTO ref_dates_by (iso, strata_variable, '
                    'strata_value, applyto_variable, data_table, '
                    'date_accessed, date_closing, date_delivery, '
                    'date_published) VALUES (%s, %s, %s, %s, %s, '
                    'STR_TO_DATE(%s, "%%d-%%m-%%Y"), '
                    'STR_TO_DATE(%s, "%%d-%%m-%%Y"), '
                    'STR_TO_DATE(%s, "%%d-%%m-%%Y"), '
                    'STR_TO_DATE(%s, "%%d-%%m-%%Y"))',
                    [row.iso, row.strata_variable, row.strata_value,
                     row.applyto_variable, table_name,
                     row.date_accessed
                        if isinstance(row.date_accessed, str) and
                        row.date_accessed != '' else None,
                     row.date_closing
                        if isinstance(row.date_closing, str) and
                        row.date_closing != '' else None,
                     row.date_delivery
                        if isinstance(row.date_delivery, str) and
                        row.date_delivery != '' else None,
                     row.date_published
                        if isinstance(row.date_published, str) and
                        row.date_published != '' else None])
