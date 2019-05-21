""" excel.py

This module includes the codec implementation for excel data sources.

"""

import logging
import pandas as pd
import numpy as np
import pickle
import joblib
from infocentre_data_manager.plugins.codecs.base import Codec
from infocentre_data_manager.plugins.semantic_types.base import SemanticType

__all__ = ['PickleCodec', ]

logger = logging.getLogger(__name__)


class PickleCodec(Codec):
    """
    Plugin that implements the HPV Information Centre data loading from and
    storing to different data sources.
    """

    def load(self, **kwargs):
        try:
            pickle_file = kwargs['file']
        except KeyError:
            raise ValueError('No "file" parameter provided')
        try:
            data = joblib.load(pickle_file)
            return data
        except Exception as e:
            raise e from None

    def store(self, data, **kwargs):
        try:
            pickle_file = kwargs['file']
        except KeyError:
            raise ValueError('No "file" parameter provided')

        joblib.dump(data, pickle_file)
