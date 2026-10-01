"""Tiferet cache contexts."""

# *** contexts

# ** context: cache_context
class CacheContext(object):
    '''
    Store namespaced values without binding a domain type.
    '''

    # * method: get
    def get(self, key):
        '''
        Retrieve one cached value.

        :param key: The cache key.
        :type key: str
        :return: The key.
        :rtype: str
        '''

        # The key names the value.
        return key
