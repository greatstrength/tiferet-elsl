"""Tiferet interfaces file."""

# *** imports

# ** app
from .core import Service

# *** interfaces

# ** interface: file_service
class FileService(Service):
    '''
    Open a file stream without the caller owning the path rules.
    '''

    # * method: open
    @abstractmethod
    def open(self, path: str):
        '''
        Open one file path.

        :param path: The file path.
        :type path: str
        :return: The open stream.
        :rtype: object
        '''

        # The implementation supplies the body.
        raise NotImplementedError('open')
