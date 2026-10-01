"""Tiferet interfaces middleware."""

# *** imports

# ** app
from .core import Service

# *** interfaces

# ** interface: middleware_service
class MiddlewareService(Service):
    '''
    Wrap a feature step without the caller knowing the wrapper.
    '''

    # * method: handle
    @abstractmethod
    def handle(self, request):
        '''
        Handle one request.

        :param request: The request to wrap.
        :type request: object
        :return: The handled request.
        :rtype: object
        '''

        # The implementation supplies the body.
        raise NotImplementedError('handle')
