"""Tiferet interfaces logging."""

# *** imports

# ** app
from .core import Service

# *** interfaces

# ** interface: logging_service
class LoggingService(Service):
    '''
    Record a log line without the caller choosing the sink.
    '''

    # * method: log
    @abstractmethod
    def log(self, message: str):
        '''
        Record one message.

        :param message: The log message.
        :type message: str
        :return: None
        :rtype: None
        '''

        # The implementation supplies the body.
        raise NotImplementedError('log')
