"""Tiferet interfaces app."""

# *** imports

# ** app
from ..mappers.app import AppSession
from .core import Service

# *** interfaces

# ** interface: app_service
class AppService(Service):
    '''
    Manage an app session without binding the caller to storage.
    '''

    # * method: exists
    @abstractmethod
    def exists(self, id: str) -> bool:
        '''
        Report whether an app session exists.

        :param id: The app session identifier.
        :type id: str
        :return: True when the session exists.
        :rtype: bool
        '''

        # The implementation supplies the body.
        raise NotImplementedError('exists')

    # * method: get
    @abstractmethod
    def get(self, id: str):
        '''
        Retrieve an app session by identifier.

        :param id: The app session identifier.
        :type id: str
        :return: The app session.
        :rtype: AppSession
        '''

        # The implementation supplies the body.
        raise NotImplementedError('get')
