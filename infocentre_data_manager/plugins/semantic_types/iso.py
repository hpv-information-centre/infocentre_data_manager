""" base.py

This module includes the validator for variable typing.

"""

import logging
import pymysql
import pandas as pd
from infocentre_data_manager.plugins.semantic_types.base import SemanticType

__all__ = ['IsoType', ]


class IsoType(SemanticType):
    """
    Plugin that implements the definition of ISO3 codes.
    """

    def __init__(self, **kwargs):
        conn = pymysql.connect(host=kwargs['HOST'],
                               user=kwargs['USER'],
                               password=kwargs['PASSWORD'],
                               db=kwargs['NAME'],
                               charset='utf8',
                               cursorclass=pymysql.cursors.DictCursor)
        self.available_isos = \
            set(pd.read_sql('SELECT iso3Code '
                            'FROM dict_regions', conn)['iso3Code'])

    def check(self, value, **kwargs):
        return value in self.available_isos

    def help_info(self, **kwargs):
        return 'ISO3 codes'
