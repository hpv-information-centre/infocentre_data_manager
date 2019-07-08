""" base.py

This module includes the base plugin interface for data fetchers.

"""

import logging
from abc import abstractmethod
from infocentre_data_manager.plugins.plugin_module import PluginModule

__all__ = ['DataValidator', ]


class DataValidator(PluginModule):
    """
    Plugin that implements different validation schemes for HPV Information
    Centre data, before uploading to a production database.
    """

    entry_point_group = 'data_validators'

    @abstractmethod
    def validate(self, data_dict, **kwargs):
        raise NotImplementedError(
            'Data validation not implemented for {}'.format(self.__class__))

    @staticmethod
    def apply(data_dict, validators):
        """
        Apply list of validators to data and accumulate the results.

        :param data_dict: Data structure with HPV Information Centre format
        :param validators: List of strings identifying the validators to be
            applied.
        """
        results = []
        for validator in validators:
            id = validator['name']
            kwargs = validator['args']
            validator = DataValidator.get(id, **kwargs)
            try:
                result = validator.validate(data_dict)
            except Exception:
                result = {
                            'info': [],
                            'warnings': [],
                            'errors': [
                                'Error on this validator, please '
                                'fix previous errors and try again.'
                            ]
                         }
            result['type'] = getattr(validator,
                                     'name',
                                     validator.__class__.__name__)
            results.append(result)
        return results
