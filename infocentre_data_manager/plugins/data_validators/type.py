""" base.py

This module includes the validator for variable typing.

"""

import logging
from infocentre_data_manager.plugins.data_validators.base import DataValidator
from infocentre_data_manager.plugins.semantic_types.base import SemanticType

__all__ = ['TypeValidator', ]


class TypeValidator(DataValidator):
    """
    Plugin that implements a semantic variable typing validator for HPV
    Information Centre data.
    """

    name = 'Semantic type validator'

    MAX_N_ERRORS_DISPLAYED = 10

    def validate(self, data_dict, **kwargs):
        info = []
        warnings = []
        errors = []

        vars_df = data_dict['variables']
        data_df = data_dict['data']

        for var in data_df:
            n_errors = 0
            invalid_ids = []
            var_type = vars_df.loc[vars_df['variable'] == var, :]
            var_type = var_type.iloc[0]['type']
            if var_type == '':
                var_type = 'string'
            type_validator = SemanticType.get(var_type)
            for i, value in enumerate(data_df[var]):
                is_valid = type_validator.check(value)
                if not is_valid:
                    n_errors += 1
                    invalid_ids.append(data_df.iloc[i]['id'])
            if n_errors > 0:
                invalid_ids = sorted(invalid_ids)
                invalid_ids_str = [str(id)
                                   for id
                                   in invalid_ids[
                                       :TypeValidator.MAX_N_ERRORS_DISPLAYED
                                   ]]
                if len(invalid_ids) > TypeValidator.MAX_N_ERRORS_DISPLAYED:
                    invalid_ids_str.append('...')
                errors.append(
                    '"{}" (type "{}") has {} invalid values in rows '
                    'with id(s) {}.'.format(
                        var,
                        var_type,
                        n_errors,
                        ', '.join(invalid_ids_str)
                    ))

        if len(errors) == 0:
            info.append('No invalid values found.')

        return {
            'info': info,
            'warnings': warnings,
            'errors': errors
        }
