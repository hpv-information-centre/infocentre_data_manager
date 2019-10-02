""" excel.py

This module includes the codec implementation for excel data sources.

"""

import logging
import pandas as pd
import numpy as np
import xlsxwriter
import re
from datetime import datetime
from infocentre_data_manager.plugins.codecs.base import Codec
from infocentre_data_manager.plugins.semantic_types.base import SemanticType

__all__ = ['ExcelCodec', ]

logger = logging.getLogger(__name__)


class ExcelCodec(Codec):
    """
    Plugin that implements the HPV Information Centre data loading from and
    storing to different data sources.
    """

    def load(self, **kwargs):
        try:
            excel_file = kwargs['file']
        except KeyError:
            raise ValueError('No "file" parameter provided')
        general = pd.read_excel(excel_file,
                                sheet_name='GENERAL',
                                header=None).loc[4:11, [1]].T
        general[pd.isna(general)] = ''
        general.columns = ['table_name',
                           'contents',
                           'data_manager',
                           'comments']

        excel_content = pd.read_excel(excel_file, sheet_name=None, dtype=str)
        variables = excel_content['VARIABLES']
        variables.fillna('', inplace=True)
        data = excel_content['DATA']
        data['id'] = data['id'].astype(int)
        data = data.replace('nan', '')
        sources = excel_content['SOURCES']
        notes = excel_content['NOTES']
        methods = excel_content['METHODS']
        years = excel_content['YEARS']

        dates = excel_content['DATES']
        dates = dates.replace('nan', '')

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
        try:
            excel_file = kwargs['file']
        except KeyError:
            raise ValueError('No "file" parameter provided')

        workbook = xlsxwriter.Workbook(excel_file, {'nan_inf_to_errors': True})

        self._create_general_sheet(data, workbook)
        self._create_variables_sheet(data, workbook)
        self._create_data_sheet(data, workbook)
        self._create_sources_sheet(data, workbook)
        self._create_notes_sheet(data, workbook)
        self._create_methods_sheet(data, workbook)
        self._create_years_sheet(data, workbook)
        self._create_dates_sheet(data, workbook)

        workbook.close()

    def _create_general_sheet(self, data, workbook):
        sheet = workbook.add_worksheet(name='GENERAL')

        sheet.set_column(0, 0, 30)
        sheet.set_column(1, 1, 55)
        sheet.set_row(0, 50)
        sheet.set_row(1, 25)
        sheet.set_row(2, 25)
        header_format = workbook.add_format({
            'bold':     True,
            'border':   1,
            'align':    'center',
            'valign':   'vcenter',
            'fg_color': '#CCFFFF',
            'font_size': 18,
        })
        sheet.merge_range('A1:B1',
                          'ICO INFORMATION CENTRE ON HPV AND CANCER',
                          header_format)
        sheet.merge_range('A2:B2', 'Data', header_format)
        sheet.merge_range('A3:B3',
                          'Internal use. Not for distribution',
                          header_format)

        label_format = workbook.add_format({
            'bold':     True,
            'border':   1,
            'valign':   'vcenter',
            'fg_color': '#EAEAEA',
            'font_color': '#0000FF',
        })
        value_format = workbook.add_format({
            'border':   1,
            'valign':   'top',
        })
        sheet.set_row(5, 50)
        sheet.set_row(7, 50)
        sheet.write_column('A5',
                           ('DATABASE TABLE NAME',
                            'CONTENTS',
                            'DATA MANAGER',
                            'COMMENTS',),
                           cell_format=label_format)
        general_data = data['general'].iloc[0, :]
        general_data = general_data.loc[[
            'table_name', 'contents', 'data_manager', 'comments'
        ]]
        sheet.write_column('B5',
                           general_data,
                           cell_format=value_format)

    def _create_variables_sheet(self, data, workbook):
        sheet = workbook.add_worksheet(name='VARIABLES')
        sheet.set_column(0, 0, 30)
        sheet.set_column(1, 1, 55)
        sheet.set_column(2, 2, 75)
        sheet.set_column(3, 3, 30)

        for i in range(len(data['variables'])):
            sheet.set_row(i, 20)
        header_format = workbook.add_format({
            'bold':     True,
            'border':   1,
            'valign':   'vcenter',
            'fg_color': '#993366',
            'font_color': 'white'
        })

        variable_columns = ['variable', 'type', 'description']
        sheet.write_row('A1',
                        variable_columns,
                        cell_format=header_format)

        available_types = list(SemanticType.get_plugins().keys())
        sheet.data_validation(1, 1, len(data['variables']), 1,
                              {
                                  'validate': 'list',
                                  'source': available_types,
                              })

        data['variables'] = data['variables'].fillna('')
        for i, column in enumerate(variable_columns):
            cell_format = None
            if column in ['variable', 'type']:
                cell_format = workbook.add_format({
                    'bold':     True,
                    'fg_color': '#EAEAEA',
                    'font_color': '#553E67',
                })
            sheet.write_column(1, i,
                               data['variables'].loc[:, column],
                               cell_format=cell_format)

    def _create_data_sheet(self, data, workbook):
        sheet = workbook.add_worksheet(name='DATA')
        self._create_sheet_from_df(data['data'], sheet, workbook)

    def _create_sources_sheet(self, data, workbook):
        sheet = workbook.add_worksheet(name='SOURCES')
        expected_columns = [
            'iso',
            'strata_variable',
            'strata_value',
            'applyto_variable',
            'value'
        ]
        self._validate_sheet_columns('sources', data, expected_columns)
        df = data['sources'][expected_columns]
        self._create_sheet_from_df(df, sheet, workbook)

    def _create_notes_sheet(self, data, workbook):
        sheet = workbook.add_worksheet(name='NOTES')
        expected_columns = [
            'iso',
            'strata_variable',
            'strata_value',
            'applyto_variable',
            'value'
        ]
        self._validate_sheet_columns('notes', data, expected_columns)
        df = data['notes'][expected_columns]
        self._create_sheet_from_df(df, sheet, workbook)

    def _create_methods_sheet(self, data, workbook):
        sheet = workbook.add_worksheet(name='METHODS')
        expected_columns = [
            'iso',
            'strata_variable',
            'strata_value',
            'applyto_variable',
            'value'
        ]
        self._validate_sheet_columns('methods', data, expected_columns)
        df = data['methods'][expected_columns]
        self._create_sheet_from_df(df, sheet, workbook)

    def _create_years_sheet(self, data, workbook):
        sheet = workbook.add_worksheet(name='YEARS')
        expected_columns = [
            'iso',
            'strata_variable',
            'strata_value',
            'applyto_variable',
            'value'
        ]
        self._validate_sheet_columns('years', data, expected_columns)
        df = data['years'][expected_columns]
        self._create_sheet_from_df(df, sheet, workbook)

    def _create_dates_sheet(self, data, workbook):
        sheet = workbook.add_worksheet(name='DATES')
        expected_columns = [
            'iso',
            'strata_variable',
            'strata_value',
            'applyto_variable',
            'date_accessed',
            'date_closing',
            'date_published',
            'date_delivery'
        ]
        self._validate_sheet_columns('dates', data, expected_columns)
        df = data['dates'][expected_columns]
        self._create_sheet_from_df(df, sheet, workbook)

    def _validate_sheet_columns(self, data_type, data, expected_columns):
        missing_columns = set(expected_columns) - set(data[data_type].columns)
        if len(missing_columns) > 0:
            raise ValueError('"{}" column(s) missing from {} sheet'.format(
                ', '.join(missing_columns),
                data_type
            ))

    def _create_sheet_from_df(self, sheet_data, sheet, workbook):
        for i in range(len(sheet_data.columns)):
            sheet.set_column(i, i, 20)
        for i in range(len(sheet_data) + 1):
            sheet.set_row(i, 20)
        header_format = workbook.add_format({
            'bold':     True,
            'border':   1,
            'valign':   'vcenter',
            'fg_color': '#993366',
            'font_color': 'white'
        })

        sheet.write_row('A1',
                        sheet_data.columns,
                        cell_format=header_format)

        # empty_cells = sheet_data.isna().sum().sum()

        # if empty_cells > 0:
        #     raise ValueError(
        #         'There are {} empty cells on the {} sheet'.format(
        #             empty_cells,
        #             sheet.name))
        for i, column in enumerate(sheet_data.columns):
            cell_format = None
            if i == 0:
                cell_format = workbook.add_format({
                    'bold':     True,
                    'fg_color': '#EAEAEA',
                    'font_color': '#553E67',
                    'top': 1,
                    'bottom': 1,
                })
            else:
                cell_format = workbook.add_format({
                    'top': 1,
                    'bottom': 1,
                })
            sheet.write_column(1, i,
                               sheet_data.loc[:, column],
                               cell_format=cell_format)
