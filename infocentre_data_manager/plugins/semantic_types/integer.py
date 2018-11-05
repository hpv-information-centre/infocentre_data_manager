""" base.py

This module includes the validator for variable typing.

"""

import logging
from infocentre_data_manager.plugins.semantic_types.base import SemanticType

__all__ = ['IntegerType', ]


class IntegerType(SemanticType):
    """
    Plugin that implements the definition of integers.
    """

    def __init__(self, **kwargs):
        pass

    def check(self, value, **kwargs):
        try:
            int(value)
            return True
        except Exception:
            return False

    def help_info(self, **kwargs):
        return 'Integer'
