"""Scanner Domain Event Tests"""

# *** imports

# ** core
from pathlib import Path
from unittest.mock import Mock

# ** infra
import pytest
from tiferet_ly.interfaces.grammar import GrammarService
from tiferet_ly.interfaces.token import TokenService

# ** app
from ..lexer import EmitScanResult, PerformLexicalAnalysis
from ..settings import DomainEvent, TiferetError
from ...interfaces import LexerService
from ...mappers import TokenAggregate

# *** fixtures

# ** fixture: sample_source_file
@pytest.fixture
def sample_source_file(tmp_path: Path) -> str:
    '''
    Fixture for a temporary source file containing scan markers.

    :param tmp_path: Temporary directory for the source file.
    :type tmp_path: Path
    :return: The source file path.
    :rtype: str
    '''

    # Write source text that includes the required scan markers.
    source_path = tmp_path / 'sample.py'
    source_path.write_text(
        '# *** imports\n\nclass SampleEvent:\n    pass\n',
        encoding='utf-8',
    )

    # Return the path the event will open.
    return str(source_path)

# ** fixture: mock_lexer_service
@pytest.fixture
def mock_lexer_service() -> Mock:
    '''
    Fixture for a lexer service mock.

    :return: The lexer service mock.
    :rtype: Mock
    '''

    # Spec the interface so unexpected calls fail.
    return Mock(spec=LexerService)

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

# *** tests

# ** test: perform_lexical_analysis_success
def test_perform_lexical_analysis_success(
        sample_source_file: str,
        mock_lexer_service: Mock,
        mock_token_service: Mock,
        mock_grammar_service: Mock,
    ) -> None:
    '''
    Test that lexical analysis returns the mock token list for a source file.

    :param sample_source_file: Temporary source file path.
    :type sample_source_file: str
    :param mock_lexer_service: The lexer service mock.
    :type mock_lexer_service: Mock
    :param mock_token_service: The token service mock.
    :type mock_token_service: Mock
    :param mock_grammar_service: The grammar service mock.
    :type mock_grammar_service: Mock
    '''

    # The lexer returns one constructed token aggregate.
    expected = [
        TokenAggregate.new(
            type='IDENTIFIER',
            value='SampleEvent',
            lineno=3,
            lexpos=16,
        ),
    ]
    mock_lexer_service.tokenize.return_value = expected

    # Invoke the event only through the domain event handler.
    result = DomainEvent.handle(
        PerformLexicalAnalysis,
        dependencies={
            'lexer_service': mock_lexer_service,
            'token_service': mock_token_service,
            'grammar_service': mock_grammar_service,
        },
        source_file=sample_source_file,
    )

    # The handler returns the mock token list unchanged.
    assert result is expected

    # Catalogues are listed once and passed through empty.
    file_text = Path(sample_source_file).read_text(encoding='utf-8')
    mock_token_service.list.assert_called_once()
    mock_grammar_service.list.assert_called_once()
    mock_lexer_service.tokenize.assert_called_once_with(file_text, [], [])

    # The file text is what was tokenized, including both scan markers.
    assert '# *** imports' in file_text
    assert 'class SampleEvent' in file_text

# ** test: perform_lexical_analysis_missing_source_file
def test_perform_lexical_analysis_missing_source_file(
        mock_lexer_service: Mock,
        mock_token_service: Mock,
        mock_grammar_service: Mock,
    ) -> None:
    '''
    Test that omitting source_file raises TiferetError.

    :param mock_lexer_service: The lexer service mock.
    :type mock_lexer_service: Mock
    :param mock_token_service: The token service mock.
    :type mock_token_service: Mock
    :param mock_grammar_service: The grammar service mock.
    :type mock_grammar_service: Mock
    '''

    # Omitting source_file is a required-parameter failure, not a tokenize call.
    with pytest.raises(TiferetError) as exc_info:
        DomainEvent.handle(
            PerformLexicalAnalysis,
            dependencies={
                'lexer_service': mock_lexer_service,
                'token_service': mock_token_service,
                'grammar_service': mock_grammar_service,
            },
        )

    # The missing parameter is source_file, and the lexer is not called.
    assert 'source_file' in exc_info.value.kwargs.get('parameters', [])
    mock_lexer_service.tokenize.assert_not_called()

# ** test: emit_scan_result_default
def test_emit_scan_result_default() -> None:
    '''
    Test that the default scan payload is TokensScanned with one token.
    '''

    # Build one token aggregate for the payload.
    token = TokenAggregate.new(
        type='KEYWORD',
        value='class',
        lineno=1,
        lexpos=0,
    )

    # Invoke the event only through the domain event handler.
    result = DomainEvent.handle(
        EmitScanResult,
        source_file='test.py',
        tokens=[token],
    )

    # The payload names the scan, the source file, and the token count.
    assert result['event_type'] == 'TokensScanned'
    assert result['source_file'] == 'test.py'
    assert result['token_count'] == 1
    assert 'tokens' in result
    assert len(result['tokens']) == 1
    assert result['tokens'][0]['type'] == 'KEYWORD'
    assert result['tokens'][0]['value'] == 'class'
    assert 'timestamp' in result
    assert result['timestamp']

    # The payload has no summary-only flag and no extracted artifacts.
    assert 'summary_only' not in result
    assert 'extracted_artifacts' not in result

# ** test: emit_scan_result_no_tokens
def test_emit_scan_result_no_tokens() -> None:
    '''
    Test that a missing token list becomes an empty scan payload.
    '''

    # None is an empty scan, not an omitted payload field.
    result = DomainEvent.handle(
        EmitScanResult,
        tokens=None,
    )

    # Count and list are present and empty.
    assert result['token_count'] == 0
    assert result['tokens'] == []

# ** test: emit_scan_result_write_yaml
def test_emit_scan_result_write_yaml(tmp_path: Path) -> None:
    '''
    Test that a .yaml output path receives a TokensScanned payload.

    :param tmp_path: Temporary directory for the output file.
    :type tmp_path: Path
    '''

    # Write the default yaml payload to a .yaml path.
    output_path = tmp_path / 'scan.yaml'
    token = TokenAggregate.new(
        type='IDENTIFIER',
        value='SampleEvent',
        lineno=1,
        lexpos=0,
    )
    result = DomainEvent.handle(
        EmitScanResult,
        source_file='test.py',
        tokens=[token],
        output=str(output_path),
    )

    # The file contains the event type, and the handler still returns the payload.
    text = output_path.read_text(encoding='utf-8')
    assert 'TokensScanned' in text
    assert result['event_type'] == 'TokensScanned'
    assert 'tokens' in result

# ** test: emit_scan_result_write_json
def test_emit_scan_result_write_json(tmp_path: Path) -> None:
    '''
    Test that a .json output path with json format contains the event type key.

    :param tmp_path: Temporary directory for the output file.
    :type tmp_path: Path
    '''

    # Write an explicit json payload to a .json path.
    output_path = tmp_path / 'scan.json'
    token = TokenAggregate.new(
        type='IDENTIFIER',
        value='SampleEvent',
        lineno=1,
        lexpos=0,
    )
    result = DomainEvent.handle(
        EmitScanResult,
        source_file='test.py',
        tokens=[token],
        output=str(output_path),
        output_format='json',
    )

    # The file is JSON, and the handler still returns the payload.
    text = output_path.read_text(encoding='utf-8')
    assert '"event_type"' in text
    assert result['event_type'] == 'TokensScanned'
