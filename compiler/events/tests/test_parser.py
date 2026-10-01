"""Parser Domain Event Tests"""

# *** imports

# ** core
from unittest.mock import Mock

# ** infra
import pytest
from tiferet_ly.interfaces.grammar import GrammarService
from tiferet_ly.interfaces.production import ProductionService
from tiferet_ly.interfaces.token import TokenService

# ** app
from ..parser import EmitParseResult, PerformSyntacticAnalysis
from ..settings import DomainEvent, TiferetError
from ...interfaces import ParserService
from ...mappers import Decl, DeclarationTransferObject, Tok

# *** fixtures

# ** fixture: mock_parser_service
@pytest.fixture
def mock_parser_service() -> Mock:
    '''
    Fixture for a parser service mock.

    :return: The parser service mock.
    :rtype: Mock
    '''

    # Spec the interface so unexpected calls fail.
    return Mock(spec=ParserService)

# ** fixture: mock_token_service
@pytest.fixture
def mock_token_service() -> Mock:
    '''
    Fixture for a token service mock with an empty catalogue.

    :return: The token service mock.
    :rtype: Mock
    '''

    # An empty catalogue is the declared list result.
    service = Mock(spec=TokenService)
    service.list.return_value = []
    return service

# ** fixture: mock_grammar_service
@pytest.fixture
def mock_grammar_service() -> Mock:
    '''
    Fixture for a grammar service mock with an empty catalogue.

    :return: The grammar service mock.
    :rtype: Mock
    '''

    # An empty catalogue is the declared list result.
    service = Mock(spec=GrammarService)
    service.list.return_value = []
    return service

# ** fixture: mock_production_service
@pytest.fixture
def mock_production_service() -> Mock:
    '''
    Fixture for a production service mock with an empty catalogue.

    :return: The production service mock.
    :rtype: Mock
    '''

    # An empty catalogue is the declared list result.
    service = Mock(spec=ProductionService)
    service.list.return_value = []
    return service

# ** fixture: sample_tokens
@pytest.fixture
def sample_tokens() -> list:
    '''
    Fixture for a token aggregate list built with Tok.new.

    :return: The sample token aggregates.
    :rtype: list
    '''

    # Build one recognized token for the parse input.
    return [
        Tok.new(
            type='IDENTIFIER',
            value='Sample',
            lineno=1,
            lexpos=0,
        ),
    ]

# ** fixture: sample_decl
@pytest.fixture
def sample_decl() -> Decl:
    '''
    Fixture for a module declaration named before set_name.

    :return: The sample module declaration.
    :rtype: Decl
    '''

    # The event renames this module from the source path.
    return Decl.new_module_decl(name='unknown_module')

# ** fixture: sample_ast
@pytest.fixture
def sample_ast(sample_decl: Decl) -> dict:
    '''
    Fixture for the primitive form of the sample declaration.

    :param sample_decl: The sample module declaration.
    :type sample_decl: Decl
    :return: The serialized declaration.
    :rtype: dict
    '''

    # Match the serialization the emit event performs.
    return DeclarationTransferObject.from_model(sample_decl).to_primitive()

# *** tests

# ** test: perform_syntactic_analysis_success
def test_perform_syntactic_analysis_success(
        mock_parser_service: Mock,
        mock_token_service: Mock,
        mock_grammar_service: Mock,
        mock_production_service: Mock,
        sample_tokens: list,
        sample_decl: Decl,
    ) -> None:
    '''
    Test that syntactic analysis returns a Decl named from the source path.

    :param mock_parser_service: The parser service mock.
    :type mock_parser_service: Mock
    :param mock_token_service: The token service mock.
    :type mock_token_service: Mock
    :param mock_grammar_service: The grammar service mock.
    :type mock_grammar_service: Mock
    :param mock_production_service: The production service mock.
    :type mock_production_service: Mock
    :param sample_tokens: The token aggregates passed to parse.
    :type sample_tokens: list
    :param sample_decl: The declaration the parser returns.
    :type sample_decl: Decl
    '''

    # The parser returns the sample declaration before the event names it.
    mock_parser_service.parse.return_value = sample_decl

    # Invoke the event only through the domain event handler.
    result = DomainEvent.handle(
        PerformSyntacticAnalysis,
        dependencies={
            'parser_service': mock_parser_service,
            'token_service': mock_token_service,
            'grammar_service': mock_grammar_service,
            'production_service': mock_production_service,
        },
        tokens=sample_tokens,
        source_file='test.py',
    )

    # The handler returns a Decl renamed from the source path.
    assert isinstance(result, Decl)
    assert result.name == 'test'

    # Catalogues are listed once and passed through empty, with no source text.
    mock_grammar_service.list.assert_called_once()
    mock_token_service.list.assert_called_once()
    mock_production_service.list.assert_called_once()
    mock_parser_service.parse.assert_called_once_with(
        'test',
        sample_tokens,
        [],
        [],
        [],
        source_text='',
    )

# ** test: perform_syntactic_analysis_missing_tokens
def test_perform_syntactic_analysis_missing_tokens(
        mock_parser_service: Mock,
        mock_token_service: Mock,
        mock_grammar_service: Mock,
        mock_production_service: Mock,
    ) -> None:
    '''
    Test that omitting tokens raises TiferetError.

    :param mock_parser_service: The parser service mock.
    :type mock_parser_service: Mock
    :param mock_token_service: The token service mock.
    :type mock_token_service: Mock
    :param mock_grammar_service: The grammar service mock.
    :type mock_grammar_service: Mock
    :param mock_production_service: The production service mock.
    :type mock_production_service: Mock
    '''

    # Omitting tokens is a required-parameter failure, not a parse call.
    with pytest.raises(TiferetError) as exc_info:
        DomainEvent.handle(
            PerformSyntacticAnalysis,
            dependencies={
                'parser_service': mock_parser_service,
                'token_service': mock_token_service,
                'grammar_service': mock_grammar_service,
                'production_service': mock_production_service,
            },
            source_file='test.py',
        )

    # The missing parameter is tokens, and the parser is not called.
    assert 'tokens' in exc_info.value.kwargs.get('parameters', [])
    mock_parser_service.parse.assert_not_called()

# ** test: perform_syntactic_analysis_invalid_ast
def test_perform_syntactic_analysis_invalid_ast(
        mock_parser_service: Mock,
        mock_token_service: Mock,
        mock_grammar_service: Mock,
        mock_production_service: Mock,
        sample_tokens: list,
    ) -> None:
    '''
    Test that a non-Decl parse result is returned as-is.

    :param mock_parser_service: The parser service mock.
    :type mock_parser_service: Mock
    :param mock_token_service: The token service mock.
    :type mock_token_service: Mock
    :param mock_grammar_service: The grammar service mock.
    :type mock_grammar_service: Mock
    :param mock_production_service: The production service mock.
    :type mock_production_service: Mock
    :param sample_tokens: The token aggregates passed to parse.
    :type sample_tokens: list
    '''

    # A non-Decl result still receives set_name and is not type-checked.
    invalid_ast = Mock()
    mock_parser_service.parse.return_value = invalid_ast

    # Invoke the event only through the domain event handler.
    result = DomainEvent.handle(
        PerformSyntacticAnalysis,
        dependencies={
            'parser_service': mock_parser_service,
            'token_service': mock_token_service,
            'grammar_service': mock_grammar_service,
            'production_service': mock_production_service,
        },
        tokens=sample_tokens,
        source_file='test.py',
    )

    # The handler returns the same object without requiring a Decl.
    assert result is invalid_ast
    assert not isinstance(result, Decl)
    invalid_ast.set_name.assert_called_once_with('test')

# ** test: perform_syntactic_analysis_none_ast
def test_perform_syntactic_analysis_none_ast(
        mock_parser_service: Mock,
        mock_token_service: Mock,
        mock_grammar_service: Mock,
        mock_production_service: Mock,
        sample_tokens: list,
    ) -> None:
    '''
    Test that a None parse result raises when the module is named.

    :param mock_parser_service: The parser service mock.
    :type mock_parser_service: Mock
    :param mock_token_service: The token service mock.
    :type mock_token_service: Mock
    :param mock_grammar_service: The grammar service mock.
    :type mock_grammar_service: Mock
    :param mock_production_service: The production service mock.
    :type mock_production_service: Mock
    :param sample_tokens: The token aggregates passed to parse.
    :type sample_tokens: list
    '''

    # None has no set_name. The event does not verify the result first.
    mock_parser_service.parse.return_value = None

    # Naming the missing result raises.
    with pytest.raises(AttributeError):
        DomainEvent.handle(
            PerformSyntacticAnalysis,
            dependencies={
                'parser_service': mock_parser_service,
                'token_service': mock_token_service,
                'grammar_service': mock_grammar_service,
                'production_service': mock_production_service,
            },
            tokens=sample_tokens,
            source_file='test.py',
        )

# ** test: emit_parse_result_default
def test_emit_parse_result_default(
        sample_decl: Decl,
        sample_ast: dict,
    ) -> None:
    '''
    Test that the default parse payload is ParseCompleted without tokens.

    :param sample_decl: The module declaration to emit.
    :type sample_decl: Decl
    :param sample_ast: The expected serialized declaration.
    :type sample_ast: dict
    '''

    # Invoke the event only through the domain event handler.
    result = DomainEvent.handle(
        EmitParseResult,
        ast=sample_decl,
        source_file='test.py',
    )

    # The payload names the parse, the source file, and the serialized AST.
    assert result['event_type'] == 'ParseCompleted'
    assert result['source_file'] == 'test.py'
    assert result['ast'] == sample_ast
    assert 'timestamp' in result
    assert result['timestamp']

    # Tokens are omitted unless include_tokens is true.
    assert 'tokens' not in result
    assert 'token_count' not in result

# ** test: emit_parse_result_with_tokens
def test_emit_parse_result_with_tokens(
        sample_decl: Decl,
        sample_tokens: list,
    ) -> None:
    '''
    Test that include_tokens adds the token list and count.

    :param sample_decl: The module declaration to emit.
    :type sample_decl: Decl
    :param sample_tokens: The token aggregates to include.
    :type sample_tokens: list
    '''

    # Invoke the event only through the domain event handler.
    result = DomainEvent.handle(
        EmitParseResult,
        ast=sample_decl,
        tokens=sample_tokens,
        include_tokens=True,
    )

    # The payload includes the dumped tokens and their count.
    assert result['tokens'] == [token.model_dump() for token in sample_tokens]
    assert result['token_count'] == len(sample_tokens)
