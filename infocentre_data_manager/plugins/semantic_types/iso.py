""" base.py

This module includes the validator for variable typing.

"""

import logging
import pymysql
from infocentre_data_manager.plugins.semantic_types.base import SemanticType

__all__ = ['IsoType', ]


class IsoType(SemanticType):
    """
    Plugin that implements the definition of ISO3 codes.
    """

    def __init__(self, conn_settings):
        conn = pymysql.connect(host=settings,
                               user=user,
                               password=password,
                               db=db,
                               charset='utf8',
                               cursorclass=pymysql.cursors.DictCursor)

    def check(self, value, **kwargs):
        # TODO
        pass

    def help_info(self, **kwargs):
        return 'ISO3 codes'
