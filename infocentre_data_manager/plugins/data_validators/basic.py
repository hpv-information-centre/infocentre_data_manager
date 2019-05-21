""" base.py

This module includes the validator for variable typing.

"""

import logging
import re
from datetime import datetime
from infocentre_data_manager.plugins.data_validators.base import DataValidator

__all__ = ['BasicValidator', ]


class BasicValidator(DataValidator):
    """
    Plugin that implements a variable typing validator for HPV Information
    Centre data.
    """

    name = 'Basic validator'

    def __init__(self, **kwargs):
        pass

    def validate(self, data_dict, **kwargs):
        self.info = []
        self.warnings = []
        self.errors = []

        self._check_vars_match(data_dict)
        self._check_general_row(data_dict)
        self._check_table_content_description(data_dict)
        self._check_no_description_vars(data_dict)
        self._check_invalid_vars(data_dict)
        self._check_dates(data_dict)

        if len(self.errors) + len(self.warnings) == 0:
            self.info.append('No problems found.')

        return {
            'info': self.info,
            'warnings': self.warnings,
            'errors': self.errors
        }

    def _check_vars_match(self, data_dict):
        var_names = data_dict['variables']['variable']
        data_var_names = data_dict['data'].columns
        if list(var_names) != list(data_var_names):
            self.errors.append(
               "Variable names don't match the data columns."
            )

    def _check_general_row(self, data_dict):
        if len(data_dict['general']) == 0:
            self.errors.append('Data table general info is missing.')
        elif len(data_dict['general']) > 1:
            self.errors.append('More than one row of general info.')

    def _check_table_content_description(self, data_dict):
        if data_dict['general']['contents'].iloc[0] == '':
            self.warnings.append('Data table content description is empty.')

    def _check_no_description_vars(self, data_dict):
        no_description_vars = [var.variable
                               for var in data_dict['variables'].itertuples()
                               if var.description == '']

        if len(no_description_vars) > 0:
            self.warnings.append(
                'The variable(s) {} have no description.'.format(
                    ', '.join(no_description_vars)
                ))

    def _check_invalid_vars(self, data_dict):
        invalid_var_names = [var.variable
                             for var in data_dict['variables'].itertuples()
                             if not bool(re.fullmatch(r'[a-zA-Z0-9_]+',
                                         var.variable))]

        if len(invalid_var_names) > 0:
            self.errors.append(
                'The variable name(s) {} are invalid, only names with '
                'lowercase and uppercase letters, numbers and '
                'underscores are allowed.'.format(
                    ', '.join(invalid_var_names)
                ))

    def _check_dates(self, data_dict):
        date_types = ['date_accessed',
                      'date_closing',
                      'date_published',
                      'date_delivery']
        nrows = len(data_dict['dates'].index)
        if nrows == 0:
            self.errors.append('No dates defined')
            return
        if nrows > 1:
            self.errors.append('More than one set of dates defined.')
            return

        for date_type in date_types:
            # Check if it exists
            try:
                d = data_dict['dates'].loc[0, date_type]
            except:
                self.errors.append('No {} defined'.format(date_type))
                continue

            # Check if its type is 'datetime'
            if isinstance(d, datetime):
                continue

            # Check if its a valid number code (-9999, -6666)
            try:
                d_num = int(d)
                if d_num not in [-9999, -6666]:
                    self.errors.append('Invalid {}: {}'.format(
                        date_type, d_num
                    ))
                continue
            except ValueError:
                pass  # Not a number

            # Check if its an empty string
            if d == '':
                continue

            # Check if it is a string with an accepted format (YYYY-MM-DD)
            try:
                str(d)
            except ValueError:
                self.errors.append('Invalid {}: {}'.format(date_type, d))
                continue
            try:
                datetime.strptime(d, '%Y-%m-%d')
            except ValueError:
                self.errors.append('{} is not in YYYY-MM-DD format: {}'.format(
                    date_type, d
                ))
                continue
