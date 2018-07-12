""" base.py

This module includes the base plugin interface for data fetchers.

"""

import logging
from abc import abstractmethod
from infocentre.plugins.plugin_module import PluginModule

__all__ = ['DataParser', ]


class DataParser(PluginModule):
    """
    Plugin that implements the HPV Information Centre data loading from and 
    storing to different data sources.
    """

    entry_point_group = 'data_parsers'

    @abstractmethod
    def load(self, load_info):
        raise NotImplementedError(
            'Data loading not implemented for {}'.format(self.__class__))

    @abstractmethod
    def store(self, data_dict):
        raise NotImplementedError(
            'Data storing not implemented for {}'.format(self.__class__))
