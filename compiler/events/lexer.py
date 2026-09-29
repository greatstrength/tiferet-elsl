"""Scanner Domain Events"""

# *** imports

# ** core
from datetime import datetime, timezone
from typing import Dict, Any, List

# ** infra
from tiferet.utils import File
from tiferet_ly.interfaces.grammar import GrammarService
from tiferet_ly.interfaces.token import TokenService

# ** app
from .settings import DomainEvent
from ..interfaces import LexerService
from ..mappers import TokenAggregate
from ..utils import ScanOutputWriter

# *** events

# ** event: perform_lexical_analysis
class PerformLexicalAnalysis(DomainEvent):
    '''
    Turn a source file into the token list a later parse can consume.

    The event reads the file and delegates recognition to the injected lexer
    and catalogues. It does not own token rules, grammar YAML, or indent layout.
    '''

    # * attribute: lexer_service
    lexer_service: LexerService

    # * attribute: token_service
    token_service: TokenService

    # * attribute: grammar_service
    grammar_service: GrammarService

    # * init
    def __init__(self,
            lexer_service: LexerService,
            token_service: TokenService,
            grammar_service: GrammarService,
        ) -> None:
        '''
        Initialize the lexical analysis event with its scan dependencies.

        :param lexer_service: The lexer that tokenizes source text.
        :type lexer_service: LexerService
        :param token_service: The service that lists declared token rules.
        :type token_service: TokenService
        :param grammar_service: The service that lists declared grammars.
        :type grammar_service: GrammarService
        '''

        # Store the lexer used to tokenize source text.
        self.lexer_service = lexer_service

        # Store the token catalogue service. The event does not open its YAML.
        self.token_service = token_service

        # Store the grammar catalogue service. The event does not open its YAML.
        self.grammar_service = grammar_service

    # * method: execute
    @DomainEvent.parameters_required(['source_file'])
    def execute(self, source_file: str, **kwargs) -> List[TokenAggregate]:
        '''
        Tokenize a source file against the injected token and grammar catalogues.

        :param source_file: Path of the UTF-8 source file to scan.
        :type source_file: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The token aggregates recognized in the file.
        :rtype: List[TokenAggregate]
        '''

        # Read the source file as UTF-8 text. Do not accept an in-memory string.
        with File(source_file, encoding='utf-8') as f:
            text = f.read()

        # List the injected catalogues. Do not open tokens.yml or grammars.yml.
        tokens = self.token_service.list()
        grammars = self.grammar_service.list()

        # Tokenize the file text. Indent and dedent stay in the lexer, not here.
        return self.lexer_service.tokenize(text, tokens, grammars)

# ** event: emit_scan_result
class EmitScanResult(DomainEvent):
    '''
    Record that a scan finished so a caller can keep or persist the token list.

    The TokensScanned payload always includes the tokens and their count, and
    a file write does not replace that return value.
    '''

    # * method: execute
    def execute(self,
            source_file: str = None,
            tokens: List[TokenAggregate] = None,
            output_format: str = 'yaml',
            output: str = None,
            **kwargs,
        ) -> Dict[str, Any]:
        '''
        Build a TokensScanned payload and optionally write it.

        :param source_file: Path of the scanned source file.
        :type source_file: str
        :param tokens: Token aggregates to include. None is an empty scan.
        :type tokens: List[TokenAggregate]
        :param output_format: Serialization format. Defaults to yaml, not auto.
        :type output_format: str
        :param output: Optional destination path. Omitted when no file is written.
        :type output: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The TokensScanned payload, including after a file write.
        :rtype: Dict[str, Any]
        '''

        # Build the payload. Always include tokens and token_count.
        result = {
            'event_type': 'TokensScanned',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'source_file': source_file,
            'tokens': [t.model_dump() for t in tokens] if tokens else [],
            'token_count': len(tokens) if tokens else 0,
        }

        # Write the payload when a destination path is given.
        if output:
            ScanOutputWriter.write(
                result,
                output,
                output_format=output_format,
            )

        # Return the payload, including when a file was written.
        return result
