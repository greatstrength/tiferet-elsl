"""Scanner Parser Interface"""

# *** imports

# ** core
from abc import abstractmethod
from typing import Any, List

# ** infra
from tiferet import Service
from tiferet_ly.domain.grammar import Grammar
from tiferet_ly.domain.production import ProductionRule
from tiferet_ly.domain.token import TokenRule

# ** app
from ..mappers import TokenAggregate

# *** interfaces

# ** interface: parser_service
class ParserService(Service):
    '''
    Abstract interface for syntactic analysis of a recognized Tiferet dialect token stream against the declared grammar, token, and production catalogues.
    '''

    # * method: parse
    @abstractmethod
    def parse(self, module_name: str,
              tokens: List[TokenAggregate],
              grammars: List[Grammar],
              token_rules: List[TokenRule],
              production_rules: List[ProductionRule],
              source_text: str = '') -> Any:
        '''
        Parse a recognized token stream into a root module AST.

        :param module_name: Module being parsed.
        :type module_name: str
        :param tokens: Already-recognized token stream.
        :type tokens: List[TokenAggregate]
        :param grammars: Declared grammar catalogue.
        :type grammars: List[Grammar]
        :param token_rules: Declared token-rule catalogue.
        :type token_rules: List[TokenRule]
        :param production_rules: Declared production-rule catalogue.
        :type production_rules: List[ProductionRule]
        :param source_text: Original source text (column calculation). Defaults to an empty string.
        :type source_text: str
        :return: The root module AST.
        :rtype: Any
        '''

        # Abstract contract; concrete parser adapters implement this method.
        raise NotImplementedError()
