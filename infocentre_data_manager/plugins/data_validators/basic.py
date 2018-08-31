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

    def validate(self, data_dict, **kwargs):
        self.info = []
        self.warnings = []
        self.errors = []

        self._check_num_vars(data_dict)
        self._check_order_vars(data_dict)
        self._check_table_content_description(data_dict)
        self._check_no_description_vars(data_dict)
        self._check_invalid_vars(data_dict)

        if len(self.errors) == 0:
            self.info.append('No errors found')

        return {
            'info': self.info,
            'warnings': self.warnings,
            'errors': self.errors
        }

    def _check_num_vars(self, data_dict):
        if len(data_dict['variables']['variable']) != \
           len(data_dict['data'].columns):
            self.errors.append(
                'The number of variables in the definition is different '
                'than in the data.'
            )

    def _check_order_vars(data_dict):
        var_names = data_dict['variables']['variable']
        data_var_names = data_dict['data'].columns
        if set(var_names) = set(data_var_names) and \
                var_names != data_var_names:
            self.warnings.append(
               'Variables as defined are in different order than in the data.'
            )

    def _check_table_content_description(data_dict):
        if data_dict['general']['contents'] == '':
            self.warnings.append('Data table content description is empty')

    def _check_no_description_vars(data_dict):
        no_description_vars = [var.variable
                               for var in data_dict['variables'].itertuples()
                               if var.description == '']

        if len(no_description_vars) > 0:
            self.warnings.append(
                'The variable(s) {} have no description.'.format(
                    no_description_vars
                ))

    def _check_invalid_vars(data_dict):
        invalid_var_names = [var.variable
                             for var in data_dict['variables'].itertuples()
                             if bool(re.fullmatch(r'[a-zA-Z0-9_]+',
                                     var.variable))]

        if len(invalid_var_names) > 0:
            self.errors.append(
                'The variable names {} are invalid, only names with '
                'lowercase and uppercase letters, numbers and '
                'underscores are allowed.'.format(
                    invalid_var_names
                ))
