"""Tiferet core assets."""

# *** imports

# ** core
from typing import Dict

# *** constants

# ** constant: en_us
EN_US = 'en_US'

# ** constant: tiferet
TIFERET = 'tiferet'

# *** functions

# ** function: create_service_dependency
def create_service_dependency(module_path, class_name):
    '''
    Build a service dependency definition.

    :param module_path: The implementation module path.
    :type module_path: str
    :param class_name: The implementation class name.
    :type class_name: str
    :return: The dependency definition.
    :rtype: Dict
    '''

    # The class name names the dependency.
    return class_name
