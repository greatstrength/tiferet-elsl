"""Parser Domain Events"""

# *** imports

# ** core
import os
from datetime import datetime, timezone
from typing import List, Dict, Any

# ** infra
from tiferet.utils import File
from tiferet_ly.interfaces.grammar import GrammarService
from tiferet_ly.interfaces.production import ProductionService
from tiferet_ly.interfaces.token import TokenService

# ** app
from ..interfaces import ParserService
from ..mappers import TokenAggregate, Decl, DeclarationTransferObject
from ..utils import ScanOutputWriter
from .settings import DomainEvent, a

# *** events

# ** event: perform_syntactic_analysis
class PerformSyntacticAnalysis(DomainEvent):
    '''
    Turn a token list into the module AST a later semantic pass can consume.

    The event lists the injected catalogues and delegates recognition to the
    parser. It does not own grammar YAML or type-check the parse result.
    '''

    # * attribute: parser_service
    parser_service: ParserService

    # * attribute: token_service
    token_service: TokenService

    # * attribute: grammar_service
    grammar_service: GrammarService

    # * attribute: production_service
    production_service: ProductionService

    # * init
    def __init__(self,
            parser_service: ParserService,
            token_service: TokenService,
            grammar_service: GrammarService,
            production_service: ProductionService,
        ) -> None:
        '''
        Initialize the syntactic analysis event with its parse dependencies.

        :param parser_service: The parser that builds a module AST.
        :type parser_service: ParserService
        :param token_service: The service that lists declared token rules.
        :type token_service: TokenService
        :param grammar_service: The service that lists declared grammars.
        :type grammar_service: GrammarService
        :param production_service: The service that lists declared productions.
        :type production_service: ProductionService
        '''

        # Store the parser used to build the module AST.
        self.parser_service = parser_service

        # Store the token catalogue service. The event does not open its YAML.
        self.token_service = token_service

        # Store the grammar catalogue service. The event does not open its YAML.
        self.grammar_service = grammar_service

        # Store the production catalogue service. The event does not open its YAML.
        self.production_service = production_service

    # * method: execute
    @DomainEvent.parameters_required(['tokens'])
    def execute(self,
            source_file: str,
            tokens: List[TokenAggregate],
            **kwargs,
        ) -> Dict[str, Any]:
        '''
        Parse a token list against the injected grammar catalogues.

        :param source_file: Path used to name the module and, when present, to read source text.
        :type source_file: str
        :param tokens: Already-recognized token aggregates.
        :type tokens: List[TokenAggregate]
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The parser result after its module name is set.
        :rtype: Dict[str, Any]
        '''

        # Derive the module name from the source path, or use the unknown default.
        module_name = (
            source_file.rsplit('/', 1)[-1].rsplit('.', 1)[0]
            if source_file else 'unknown_module'
        )

        # Read UTF-8 source text only when the path exists. Do not open catalogues.
        source_text = ''
        if source_file and os.path.exists(source_file):
            with File(source_file, encoding='utf-8') as f:
                source_text = f.read()

        # List the injected catalogues. Do not open grammar, token, or production YAML.
        grammars = self.grammar_service.list()
        token_rules = self.token_service.list()
        production_rules = self.production_service.list()

        # Parse the token list. Do not verify that the result is a Decl.
        ast = self.parser_service.parse(
            module_name,
            tokens,
            grammars,
            token_rules,
            production_rules,
            source_text=source_text,
        )

        # Name the module. A None result fails here.
        ast.set_name(module_name)

        # Return the parser result, including a non-Decl pass-through.
        return ast

# ** event: emit_parse_result
class EmitParseResult(DomainEvent):
    '''
    Record that a parse finished so a caller can keep or persist the module AST.

    The ParseCompleted payload serializes the declaration, and a file write
    replaces the returned payload with an empty string.
    '''

    # * method: execute
    @DomainEvent.parameters_required(['ast'])
    def execute(self,
            ast: Decl,
            tokens: List[TokenAggregate] = None,
            source_file: str = None,
            extract: str = None,
            include_tokens: bool = False,
            output_format: str = 'auto',
            output: str = None,
            **kwargs,
        ) -> Dict[str, Any]:
        '''
        Build a ParseCompleted payload and optionally write it.

        :param ast: The module declaration to serialize.
        :type ast: Decl
        :param tokens: Token aggregates included only when requested.
        :type tokens: List[TokenAggregate]
        :param source_file: Path of the parsed source file.
        :type source_file: str
        :param extract: Optional comma-separated artifact names to record.
        :type extract: str
        :param include_tokens: Whether to add tokens and token_count.
        :type include_tokens: bool
        :param output_format: Serialization format. Defaults to auto.
        :type output_format: str
        :param output: Optional destination path. When set, the write replaces the return value.
        :type output: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The ParseCompleted payload, or an empty string after a file write.
        :rtype: Dict[str, Any]
        '''

        # Reject a missing or non-declaration AST. Do not require tokens.
        self.verify(
            expression=ast and isinstance(ast, Decl),
            error_code='INVALID_AST_STRUCTURE',
            message='Syntactic parser did not return a valid Module AST',
            ast_type=str(type(ast)),
        )

        # Build the payload. Omit tokens unless the caller asks for them.
        result = {
            'event_type': 'ParseCompleted',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'source_file': source_file,
            'ast': DeclarationTransferObject.from_model(ast).to_primitive(),
        }

        # Record extracted artifact names only when the filter is truthy.
        extracted_names = ScanOutputWriter.parse_extract_names(extract)
        if extracted_names:
            result['extracted_artifacts'] = extracted_names

        # Include the token list and count only when requested.
        if include_tokens:
            result['tokens'] = [token.model_dump() for token in tokens] if tokens else []
            result['token_count'] = len(tokens) if tokens else 0

        # Write the payload and return an empty string when a destination is given.
        if output:
            ScanOutputWriter.write(
                result,
                output,
                output_format=output_format,
            )
            return ''

        # Otherwise return the payload.
        return result
