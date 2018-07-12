""" base.py

This module includes the base plugin interface for data fetchers.

"""

import logging
from infocentre.plugins.data_parsers import DataParser

__all__ = ['ExcelParser', ]


class ExcelParser(DataParser):
    """
    Plugin that implements the HPV Information Centre data loading from and
    storing to different data sources.
    """

    def load(self, load_info):
        raise NotImplementedError(
            'Data loading not implemented for {}'.format(self.__class__))

    def store(self, data_dict):
        raise NotImplementedError(
            'Data storing not implemented for {}'.format(self.__class__))
