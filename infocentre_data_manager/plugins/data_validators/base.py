""" base.py

This module includes the base plugin interface for data fetchers.

"""

import logging
from abc import abstractmethod
from infocentre_data_manager.plugins.plugin_module import PluginModule

__all__ = ['DataValidator', ]


class DataValidator(PluginModule):
    """
    Plugin that implements different validation schemes for HPV Information
    Centre data, before uploading to a production database.
    """

    entry_point_group = 'data_validators'

    @abstractmethod
    def validate(self, data_dict):
        raise NotImplementedError(
            'Data validation not implemented for {}'.format(self.__class__))
