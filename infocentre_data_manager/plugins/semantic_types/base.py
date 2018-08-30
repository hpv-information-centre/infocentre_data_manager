""" base.py

This module includes the base plugin interface for semantic type definition.

"""

import logging
from abc import abstractmethod
from infocentre_data_manager.plugins.plugin_module import PluginModule

__all__ = ['SemanticType', ]


class SemanticType(PluginModule):
    """
    Plugin that represents different semantic types used to standardize and
    validate external data.
    """

    entry_point_group = 'semantic_types'

    @abstractmethod
    def check(self, value, **kwargs):
        raise NotImplementedError(
            'Type validation not implemented for {}'.format(self.__class__))

    @property
    @abstractmethod
    def help_info(self, **kwargs):
        return 'No help available'
