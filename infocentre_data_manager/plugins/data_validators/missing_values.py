""" missing_values.py

This module includes the validator for detecting missing values.

"""

import logging
from infocentre_data_manager.plugins.data_validators.base import DataValidator

__all__ = ['MissingValuesValidator', ]


class MissingValuesValidator(DataValidator):
    """
    Plugin that implements a missing values validator for HPV Information
    Centre data.
    """

    name = 'Missing values validator'

    def __init__(self, **kwargs):
        pass

    def validate(self, data_dict, **kwargs):
        raise NotImplementedError(
            'Data validation not implemented for {}'.format(self.__class__))
