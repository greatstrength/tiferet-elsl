"""Tiferet interfaces feature."""

# *** imports

# ** app
from ..mappers.feature import Feature
from .core import Service

# *** interfaces

# ** interface: feature_service
class FeatureService(Service):
    '''
    Load a feature definition without the caller knowing the store.
    '''

    # * method: exists
    @abstractmethod
    def exists(self, id: str) -> bool:
        '''
        Report whether a feature exists.

        :param id: The feature identifier.
        :type id: str
        :return: True when the feature exists.
        :rtype: bool
        '''

        # The implementation supplies the body.
        raise NotImplementedError('exists')
