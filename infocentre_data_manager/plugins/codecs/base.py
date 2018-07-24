""" base.py

This module includes the base plugin interface for data fetchers.

"""

import logging
from abc import abstractmethod
from infocentre_data_manager.plugins.plugin_module import PluginModule

__all__ = ['DataParser', ]


class Codec(PluginModule):
    """
    Plugin that implements the HPV Information Centre data loading from and 
    storing to different data sources.
    """

    entry_point_group = 'codecs'

    @abstractmethod
    def load(self, **kwargs):
        raise NotImplementedError(
            'Data loading not implemented for {}'.format(self.__class__))

    @abstractmethod
    def store(self, data, **kwargs):
        raise NotImplementedError(
            'Data storing not implemented for {}'.format(self.__class__))
