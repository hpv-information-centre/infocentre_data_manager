""" excel.py

This module includes the codec implementation for excel data sources.

"""

import logging
import re
import pandas as pd
import numpy as np
import xlsxwriter
import pymysql
from infocentre_data_manager.plugins.codecs.base import Codec
from infocentre_data_manager.plugins.semantic_types.base import SemanticType

__all__ = ['OldExcelCodec', ]


class OldExcelCodec(Codec):
    """
    Plugin that implements the HPV Information Centre data loading from old
    excel templates (storing not supported, see sqlToExcel.R script)
    """

    def load(self, **kwargs):
        try:
            excel_file = kwargs['file']
        except KeyError:
            raise ValueError('No "file" parameter provided')
        general = pd.read_excel(excel_file,
                                sheet_name='WELCOME',
                                header=None).loc[4:11, [1]].T
        general[pd.isna(general)] = ''
        general.columns = ['contents',
                           '__description',
                           '__update',
                           'data_manager',
                           'comments',
                           '__delivery',
                           'table_name',
                           '__preffix']

        data = pd.read_excel(excel_file, sheet_name='DATA')
        data = data.astype(str)

        variables = pd.read_excel(excel_file, sheet_name='VARIABLES')
        variables.columns = ['__id', 'variable', 'description',
                             '__short_desc', '__type', '__primary']
        variables['variable'] = [v.variable if not pd.isna(v.variable)
                                 else '_var' + str(i)
                                 for i, v in enumerate(variables.itertuples())]
        variables['type'] = ['string' if v.variable != 'id' else 'integer'
                             for v in variables.itertuples()]
        data.columns = list(variables['variable'])
        if 'id' not in variables['variable']:
            variables = pd.concat([pd.DataFrame({
                                    '__id': [''],
                                    'variable': ['id'],
                                    'description': ['Row id'],
                                    '__short_desc': [''],
                                    '__type': [''],
                                    '__primary': [''],
                                    'type': ['integer']
                                    }),
                                   variables], ignore_index=True)
            data.insert(0, 'id', range(1, len(data.index) + 1))

        new_ref_columns = ['__description', 'iso', 'strata_variable',
                           'strata_value', 'applyto_variable', '__table',
                           '__id', 'value']
        sources = pd.read_excel(excel_file, sheet_name='SOURCES', dtype=str)
        sources.columns = new_ref_columns
        notes = pd.read_excel(excel_file, sheet_name='NOTES', dtype=str)
        notes.columns = new_ref_columns
        methods = pd.read_excel(excel_file, sheet_name='METHODS', dtype=str)
        methods.columns = new_ref_columns
        years = pd.read_excel(excel_file, sheet_name='YEARS', dtype=str)
        years.columns = new_ref_columns
        dates = pd.read_excel(excel_file, sheet_name='DATES', dtype=str)
        dates.columns = ['__description', 'iso', 'strata_variable',
                         'strata_value', 'applyto_variable', '__table',
                         'date_accessed', 'date_closing', 'date_delivery']

        host = kwargs['host']
        db = kwargs['db']
        user = kwargs['user']
        password = kwargs['password']
        table_name = general.at[1, 'table_name']

        conn = pymysql.connect(host=host,
                               user=user,
                               password=password,
                               db=db,
                               charset='utf8',
                               cursorclass=pymysql.cursors.DictCursor)
        date_published = pd.read_sql(
            'SELECT datePublicacio '
            'FROM view_relatedinf_date_by '
            'WHERE data_tbl = %s',
            con=conn,
            params=[table_name]
        )['datePublicacio']
        dates['date_published'] = date_published
        for date in ['date_accessed', 'date_closing',
                     'date_delivery', 'date_published']:
            matches = re.findall('(\d{4})-(\d{2})-(\d{2})',
                                 str(dates.at[0, date]))
            if len(matches) == 1:
                year, month, day = matches[0]
                d = '{}/{}/{}'.format(day, month, year)
            else:
                d = None
            dates[date] = d

        variables.fillna('', inplace=True)
        dates.replace('nan', '')

        return {
            'general': general,
            'variables': variables,
            'data': data,
            'sources': sources,
            'notes': notes,
            'methods': methods,
            'years': years,
            'dates': dates,
        }

    def store(self, data, **kwargs):
        raise NotImplementedError(
            'Storing not implemented for old excel templates')
