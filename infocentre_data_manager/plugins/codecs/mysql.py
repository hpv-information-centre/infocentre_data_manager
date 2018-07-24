""" base.py

This module includes the base plugin interface for data fetchers.

"""

import logging
import pandas as pd
import pymysql.cursors
from infocentre_data_manager.plugins.codecs.base import Codec

__all__ = ['MySQLParser', ]


class MySQLParser(Codec):
    """
    Plugin that implements the HPV Information Centre data loading from and
    storing to different data sources.
    """

    def load(self, **kwargs):
        host = kwargs['host']
        db = kwargs['db']
        user = kwargs['user']
        password = kwargs['password']
        table = kwargs['table']

        conn = pymysql.connect(host=host,
                               user=user,
                               password=password,
                               db=db,
                               charset='utf8',
                               cursorclass=pymysql.cursors.DictCursor)
        data = pd.read_sql('SELECT * FROM {}'.format(table), conn)
        return data

    def store(self, data, **kwargs):
        raise NotImplementedError(
            'Data storing not implemented for {}'.format(self.__class__))
