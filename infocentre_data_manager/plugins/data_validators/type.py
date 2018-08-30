""" base.py

This module includes the validator for variable typing.

"""

import logging
from infocentre_data_manager.plugins.data_validators.base import DataValidator

__all__ = ['TypeValidator', ]


class TypeValidator(DataValidator):
    """
    Plugin that implements a variable typing validator for HPV Information
    Centre data.
    """

    def validate(self, data_dict):
        raise NotImplementedError(
            'Data validation not implemented for {}'.format(self.__class__))
