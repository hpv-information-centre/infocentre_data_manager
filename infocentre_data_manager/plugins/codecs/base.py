""" base.py

This module includes the base plugin interface for data fetchers.

"""

import logging
from abc import abstractmethod
from infocentre_data_manager.plugins.plugin_module import PluginModule

__all__ = ['Codec', ]


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

    @staticmethod
    def convert(src_codec, src_params, dst_codec, dst_params):
        """
        Converts HPV Information Centre data from one data source to another.

        :param src_codec: Source codec id (will load the data).
        :param src_params: Parameters passed to the source codec.
        :param dst_codec: Codec id (will store the data).
        :param dst_params: Parameters passed to the destination codec.
        """
        data = Codec.get(src_codec).load(**src_params)
        Codec.get(dst_codec).store(data, **dst_params)
