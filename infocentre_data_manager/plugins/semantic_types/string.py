""" base.py

This module includes the validator for variable typing.

"""

import logging
from infocentre_data_manager.plugins.semantic_types.base import SemanticType

__all__ = ['StringType', ]


class StringType(SemanticType):
    """
    Plugin that implements the definition of strings.
    """

    def check(self, value, **kwargs):
        return True

    def help_info(self, **kwargs):
        return 'String'
