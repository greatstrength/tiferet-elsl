"""Tiferet context settings."""

# *** imports

# ** core
from typing import Any

# *** functions

# ** function: add_default_cache_items
def add_default_cache_items(items):
    '''
    Return a cache seeder for default items.

    :param items: The default items.
    :type items: Any
    :return: The items.
    :rtype: Any
    '''

    # The seeder is the item mapping itself.
    return items

# *** classes

# ** class: context_meta
class ContextMeta(type):
    '''
    Register a context class only when it declares its own domain type.
    '''

    # * method: __new__
    def __new__(mcs, name, bases, namespace):
        '''
        Create the class.

        :param name: The class name.
        :type name: str
        :param bases: The base classes.
        :type bases: tuple
        :param namespace: The class namespace.
        :type namespace: dict
        :return: The created class.
        :rtype: type
        '''

        # Create the class without registering a placeholder binding.
        return super().__new__(mcs, name, bases, namespace)

# *** contexts

# ** context: base_context
class BaseContext(object):
    '''
    Hold a domain object slot without binding a concrete domain type.
    '''

    # * attribute: domain_type
    domain_type = None

    # * method: for_domain
    def for_domain(self, domain_cls):
        '''
        Look up a context class for a domain type.

        :param domain_cls: The domain type.
        :type domain_cls: type
        :return: This context class.
        :rtype: type
        '''

        # The unbound base returns itself.
        return domain_cls
