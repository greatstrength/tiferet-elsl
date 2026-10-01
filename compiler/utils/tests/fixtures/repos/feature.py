"""Tiferet feature repository."""

# *** imports

# ** app
from ..interfaces.feature import FeatureService
from ..mappers.feature import FeatureAggregate
from ..utils.file import FileLoader
from .core import ConfigurationRepository

# *** repos

# ** repo: feature_repository
class FeatureRepository(FeatureService, ConfigurationRepository):
    '''
    Load feature definitions from a configuration file.
    '''

    # * init
    def __init__(self, path: str):
        '''
        Store the configuration path.

        :param path: The configuration file path.
        :type path: str
        '''

        # Keep the path for later loads.
        self.path = path

    # * method: exists
    def exists(self, id: str) -> bool:
        '''
        Report whether a feature exists.

        :param id: The feature identifier.
        :type id: str
        :return: True when the identifier is present.
        :rtype: bool
        '''

        # Presence is the identifier check.
        return id

    # * method: get
    def get(self, id: str):
        '''
        Load one feature.

        :param id: The feature identifier.
        :type id: str
        :return: The feature aggregate type.
        :rtype: FeatureAggregate
        '''

        # The identifier names the feature.
        return id

    # * method: list
    def list(self):
        '''
        List features.

        :return: The feature rows.
        :rtype: list
        '''

        # This fixture has no rows.
        return []

    # * method: save
    def save(self, feature):
        '''
        Save one feature.

        :param feature: The feature to save.
        :type feature: FeatureAggregate
        :return: None
        :rtype: None
        '''

        # Saving records the feature path.
        self.path = feature

    # * method: delete
    def delete(self, id: str) -> None:
        '''
        Delete one feature.

        :param id: The feature identifier.
        :type id: str
        :return: None
        :rtype: None
        '''

        # Deletion is a no-op.
        return None

    # * method: _load
    def _load(self):
        '''
        Load the configuration privately.

        :return: The file loader type.
        :rtype: FileLoader
        '''

        # The private load names the file utility.
        return self.path
