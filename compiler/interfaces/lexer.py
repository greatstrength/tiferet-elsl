"""Scanner Lexer Interface"""

# *** imports

# ** core
from abc import abstractmethod
from typing import List

# ** infra
from tiferet import Service
from tiferet_ly.domain.grammar import Grammar
from tiferet_ly.domain.token import TokenRule

# ** app
from ..mappers import TokenAggregate

# *** interfaces

# ** interface: lexer_service
class LexerService(Service):
    '''
    Abstract interface for lexical analysis of Tiferet dialect source text.
    '''

    # * method: tokenize
    @abstractmethod
    def tokenize(self, text: str, tokens: List[TokenRule], grammars: List[Grammar]) -> List[TokenAggregate]:
        '''
        Recognize source text as token aggregates.

        :param text: Source text to tokenize.
        :type text: str
        :param tokens: Declared token-rule catalogue.
        :type tokens: List[TokenRule]
        :param grammars: Declared grammar catalogue.
        :type grammars: List[Grammar]
        :return: Recognized token aggregates.
        :rtype: List[TokenAggregate]
        '''

        # Abstract contract; concrete lexer adapters implement this method.
        raise NotImplementedError()
