""" base.py

This module includes the base plugin interface for data fetchers.

"""

import logging
from infocentre.plugins.data_validators import DataValidator

__all__ = ['TypeValidator', ]


class TypeValidator(DataValidator):
    """
    Plugin that implements different validation schemes for HPV Information
    Centre data, before uploading to a production database.
    """

    def validate(self, data_dict):
        raise NotImplementedError(
            'Data validation not implemented for {}'.format(self.__class__))
