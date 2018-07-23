""" base.py

This module includes the base plugin interface for data fetchers.

"""

import logging
import pandas as pd
import xlsxwriter
from infocentre_data_manager.plugins.codecs.base import DataParser

__all__ = ['ExcelParser', ]


class ExcelParser(DataParser):
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
                           'comments',
                           'date_accessed',
                           'date_closing',
                           'date_published',
                           'date_delivery']
        dates = pd.DataFrame(general)
        dates = dates[['date_accessed',
                       'date_closing',
                       'date_published',
                       'date_delivery']]
        general = general[['table_name',
                           'contents',
                           'data_manager',
                           'comments']]

        variables = pd.read_excel(excel_file, sheet_name='VARIABLES')
        data = pd.read_excel(excel_file, sheet_name='DATA')
        sources = pd.read_excel(excel_file, sheet_name='SOURCES')
        notes = pd.read_excel(excel_file, sheet_name='NOTES')
        methods = pd.read_excel(excel_file, sheet_name='METHODS')
        years = pd.read_excel(excel_file, sheet_name='YEARS')
        logs = pd.read_excel(excel_file, sheet_name='LOGS')

        return {
            'general': general,
            'variables': variables,
            'data': data,
            'sources': sources,
            'notes': notes,
            'methods': methods,
            'years': years,
            'dates': dates,
            'logs': logs,
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
        # self._create_dates_sheet(data, workbook)
        self._create_logs_sheet(data, workbook)

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
                            'COMMENTS',
                            'ACCESS DATE',
                            'CLOSING DATE',
                            'PUBLICATION DATE',
                            'DELIVERY DATE'),
                           cell_format=label_format)
        general_data = pd.concat([
            data['general'].loc[1, :],
            data['dates'].loc[1, :]
        ], ignore_index=True)
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

        sheet.write_row('A1',
                        (
                            'Variable',
                            'Description',
                            'Type',
                        ),
                        cell_format=header_format)

        data['variables'] = data['variables'].fillna('')
        for i, column in enumerate(data['variables'].columns):
            cell_format = None
            if i == 0:
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

    def _create_logs_sheet(self, data, workbook):
        sheet = workbook.add_worksheet(name='LOGS')
        expected_columns = [
            'author',
            'date',
            'message',
            'action',
            'variables',
            'data',
            'sources',
            'notes',
            'methods',
            'dates'
        ]
        self._validate_sheet_columns('logs', data, expected_columns)
        df = data['logs'][expected_columns]
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
