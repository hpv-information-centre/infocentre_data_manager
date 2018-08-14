""" mysql.py

This module includes the codec implementation for MySQL data sources.

"""

import logging
import re
import datetime
import pandas as pd
import numpy as np
import pymysql.cursors
from infocentre_data_manager.plugins.codecs.base import Codec

__all__ = ['MySQLCodec', ]


class MySQLCodec(Codec):
    """
    Plugin that implements the HPV Information Centre data loading from and
    storing to MySQL data sources.
    """

    BATCH_SIZE = 20

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
            'SELECT var AS variable, description, semantic_type AS type '
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
        for date_type in date_types:
            if dates.loc[0, date_type] is not None:
                dates.loc[0, date_type] = \
                    dates.loc[0, date_type].strftime('%d/%m/%Y')
            else:
                dates.loc[0, date_type] = ''
        return dates

    def store(self, data, **kwargs):
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

        self._store_general_data(conn, data)
        self._store_variable_data(conn, data)
        self._store_raw_data(conn, data)
        self._store_ref_data(conn, data, 'sources')
        self._store_ref_data(conn, data, 'notes')
        self._store_ref_data(conn, data, 'methods')
        self._store_ref_data(conn, data, 'years')
        self._store_dates_data(conn, data)

        conn.commit()
        conn.close()

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
            module = -9999

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
                    ' (data_table, var, description, semantic_type, `order`) '
                    'VALUES (%s, %s, %s, %s, %s)',
                    [table_name, var.variable, var.description, var.type, i]
                    )

    def _store_raw_data(self, conn, data):
        table_name = data['general']['table_name'].iloc[0]

        try:
            conn.query('TRUNCATE {}'.format(table_name))
        except ProgrammingError:
            raise EnvironmentError(
                "Table '{}' does not exist, create it first.")

        n_rows = len(data['data'].index)
        for i in range(0, len(data['data'].index), MySQLCodec.BATCH_SIZE + 1):
            with conn.cursor() as cursor:
                # TODO: Refactor insert string generation
                cursor.execute('INSERT INTO {} ({}) VALUES {}'.format(
                    table_name,
                    ','.join(data['data'].columns),
                    ','.join(['({})'.format(','.join(
                                ["'" + v.replace("'", "\\'") + "'"
                                    if isinstance(v, str) else str(v)
                                 for v in row[1].values]))
                             for row
                             in data['data'].loc[
                                i:min(
                                    n_rows,
                                    i + MySQLCodec.BATCH_SIZE
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
                params=[ref],
                con=conn
            )
            if len(existing_ref) == 0:
                with conn.cursor() as cursor:
                    cursor.execute(
                        'INSERT INTO ref_{} (value) VALUES (%s)'.format(
                            ref_type),
                        [ref]
                        )

        with conn.cursor() as cursor:
            cursor.execute(
                'DELETE FROM ref_{}_by WHERE data_table = %s'.format(ref_type),
                [table_name])

        n_rows = len(data[ref_type].index)
        for row in data[ref_type].itertuples():
            with conn.cursor() as cursor:
                cursor.execute(
                    'INSERT INTO ref_{}_by (iso, strata_variable, '
                    'strata_value, applyto_variable, data_table, id_{}) '
                    'VALUES (%s, %s, %s, %s, %s, '
                    ' (SELECT id FROM ref_{} WHERE value=%s))'.format(
                        ref_type, ref_type[:-1], ref_type),
                    [row.iso, row.strata_variable, row.strata_value,
                     row.applyto_variable, table_name, row.value])

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
                    'STR_TO_DATE(%s, "%%d/%%m/%%Y"), '
                    'STR_TO_DATE(%s, "%%d/%%m/%%Y"), '
                    'STR_TO_DATE(%s, "%%d/%%m/%%Y"), '
                    'STR_TO_DATE(%s, "%%d/%%m/%%Y"))',
                    [row.iso, row.strata_variable, row.strata_value,
                     row.applyto_variable, table_name,
                     row.date_accessed
                        if isinstance(row.date_accessed, str) else None,
                     row.date_closing
                        if isinstance(row.date_closing, str) else None,
                     row.date_delivery
                        if isinstance(row.date_delivery, str) else None,
                     row.date_published
                        if isinstance(row.date_published, str) else None])
