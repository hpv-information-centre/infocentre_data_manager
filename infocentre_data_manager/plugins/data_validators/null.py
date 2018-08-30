""" base.py

This module includes the validator for variable typing.

"""

import logging
from infocentre_data_manager.plugins.data_validators.base import DataValidator

__all__ = ['NullValidator', ]


class NullValidator(DataValidator):
    """
    Plugin that implements a null validator that returns the results as passed
    via parameters.
    """

    name = 'Null validator'

    def validate(self, data_dict, **kwargs):
        info = kwargs.get('info', ['Info example'])
        warnings = kwargs.get('warnings',
                              ['Warning example 1', 'Warning example 2'])
        errors = kwargs.get('errors', [])
        return {
            'info': info,
            'warnings': warnings,
            'errors': errors
        }
