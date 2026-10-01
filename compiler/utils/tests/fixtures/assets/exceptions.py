"""Tiferet asset exceptions."""

# *** classes

# ** class: tiferet_error
class TiferetError(Exception):
    '''
    A structured failure a caller can name without a raw traceback.
    '''

    # * method: raise_error
    def raise_error(self, code):
        '''
        Raise this error for a code.

        :param code: The error code.
        :type code: str
        :return: None
        :rtype: None
        '''

        # The code names the failure.
        raise TiferetError(code)
