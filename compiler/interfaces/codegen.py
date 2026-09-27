"""Codegen Service Interface"""

# *** imports

# ** core
from abc import abstractmethod
from typing import Any, Dict

# ** infra
from tiferet import Service

# *** interfaces

# ** interface: codegen_service
class CodegenService(Service):
    '''
    Abstract interface for code generation from a parsed AST.
    '''

    # * method: generate
    @abstractmethod
    def generate(self, ast: Any, kind: str = 'events') -> Dict[str, Any]:
        '''
        Generate a schema-conforming codegen dict from a parsed AST.

        :param ast: Module-level declaration aggregate from parsing.
        :type ast: Any
        :param kind: Requested component type (`events`, `assets`, …). Defaults to `events`.
        :type kind: str
        :return: Schema-conforming codegen dict.
        :rtype: Dict[str, Any]
        '''

        # Abstract contract; concrete generator adapters implement this method.
        raise NotImplementedError()
