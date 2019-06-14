""" hpv_types.py

This module includes the validator for HPV types.

"""

import logging
import pymysql
import pandas as pd
from infocentre_data_manager.plugins.semantic_types.base import SemanticType

__all__ = ['HPVType', ]


class HPVType(SemanticType):
    """
    Plugin that implements the HPV types (e.g. 16, 18, ...)
    """

    def __init__(self, **kwargs):
        conn = pymysql.connect(host=kwargs['HOST'],
                               user=kwargs['USER'],
                               password=kwargs['PASSWORD'],
                               db=kwargs['NAME'],
                               charset='utf8',
                               cursorclass=pymysql.cursors.DictCursor)
        self.available_types = \
            set(pd.read_sql('SELECT hpvtype '
                            'FROM dict_hpv_types', conn)['hpvtype'])

    def check(self, value, **kwargs):
        return value in self.available_types

    def help_info(self, **kwargs):
        return 'HPV types'
