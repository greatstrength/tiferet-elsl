"""Compiler Assets Core"""

# *** imports

# ** core
from typing import Any, Dict

# *** functions

# ** function: create_default_provision_data
def create_default_provision_data(
        kind: str,
        applies_to: str,
        module_path: str,
        class_name: str,
        parameters: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
    '''
    Build one provision registration value.

    The id is omitted because the group-dict key is the id. Legal kinds are
    ``specification``, ``production``, and ``rewrite``. ``parameters`` holds
    constructor keyword arguments other than ``id`` and ``applies_to``.

    :param kind: The provision kind.
    :type kind: str
    :param applies_to: The visit hook this provision handles.
    :type applies_to: str
    :param module_path: The module that defines the class.
    :type module_path: str
    :param class_name: The class to resolve later.
    :type class_name: str
    :param parameters: Constructor keyword arguments other than id and applies_to.
    :type parameters: Dict[str, Any]
    :return: The five registration fields.
    :rtype: Dict[str, Any]
    '''

    # Copy parameters and return the five registration fields.
    return {
        'kind': kind,
        'applies_to': applies_to,
        'module_path': module_path,
        'class_name': class_name,
        'parameters': dict(parameters) if parameters else {},
    }
