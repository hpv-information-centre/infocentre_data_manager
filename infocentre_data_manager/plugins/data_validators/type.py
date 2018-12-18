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

    def __init__(self, **kwargs):
        self.type_validator_args = kwargs

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
            type_validator = SemanticType.get(var_type,
                                              **self.type_validator_args)
            for i, value in enumerate(data_df[var]):
                is_valid = type_validator.check(value)
                if not is_valid:
                    n_errors += 1
                    invalid_ids.append(
                        (data_df.iloc[i]['id'],
                         data_df.iloc[i][var])
                    )
            if n_errors > 0:
                invalid_ids = sorted(invalid_ids, key=lambda x: x[0])
                invalid_ids_str = ['{} ("{}")'.format(id, value)
                                   for id, value
                                   in invalid_ids[
                                       :TypeValidator.MAX_N_ERRORS_DISPLAYED
                                   ]]
                if len(invalid_ids) > TypeValidator.MAX_N_ERRORS_DISPLAYED:
                    invalid_ids_str.append('...')
                errors.append(
                    'Variable "{}" (type "{}") has {} invalid values '
                    'in rows {}.'.format(
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
