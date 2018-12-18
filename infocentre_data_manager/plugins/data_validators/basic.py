""" base.py

This module includes the validator for variable typing.

"""

import logging
import re
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
