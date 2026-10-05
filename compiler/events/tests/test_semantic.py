"""Semantic Analysis Domain Event Tests"""

# *** imports

# ** core
from pathlib import Path

# ** infra
import pytest

# ** app
from ...blueprints.core import build_cache
from ...contexts.provision import COMPILER_PROVISION_CACHE_PREFIX
from ..semantic import EmitSemanticResult, PerformSemanticAnalysis
from ..settings import DomainEvent, TiferetError
from ...domain.semantic import SYMBOL_KIND_CLASS_DEF
from ...mappers import Decl, Expr, Stmt

# *** functions

# ** function: _provision_kwargs
def _provision_kwargs() -> dict:
    '''
    Return the cache and prefix semantic analysis now requires.

    :return: Keyword arguments for the analysis event.
    :rtype: dict
    '''

    # The event does not seed a cache. The test supplies one.
    if not hasattr(_provision_kwargs, 'cache'):
        _provision_kwargs.cache = build_cache()
    return {
        'cache': _provision_kwargs.cache,
        'provision_prefix': COMPILER_PROVISION_CACHE_PREFIX,
    }

# *** fixtures

# ** fixture: sample_module
@pytest.fixture
def sample_module() -> Decl:
    '''
    Fixture for a module with one imported name and one class.

    :return: The sample module declaration.
    :rtype: Decl
    '''

    # A non-empty class body is what registers the class, not an attribute.
    return Decl.new_module_decl(
        name='events',
        code=[
            Stmt.new_import_stmt_from(
                from_expr=Expr.new_name_expr('.settings'),
                import_expr=Expr.new_name_expr('DomainEvent'),
            ),
            Stmt.new_decl_stmt(Decl.new_class_decl(
                name='Ping',
                subclasses=None,
                doc_string=None,
                members=[
                    Stmt.new_decl_stmt(Decl.new_func_decl(name='execute')),
                ],
            )),
        ],
    )

# ** fixture: sample_semantic
@pytest.fixture
def sample_semantic() -> dict:
    '''
    Fixture for a semantic result the emitter can pass through.

    :return: The symbol table and resolution payload.
    :rtype: dict
    '''

    # The emitter copies these keys. It does not rebuild them.
    return {
        'symbol_table': {
            'module_name': 'events',
            'scopes': {},
        },
        'resolution': {
            'resolved': [],
            'unresolved': [],
        },
    }

# *** tests

# ** test: perform_semantic_analysis_returns_symbol_table_and_resolution
def test_perform_semantic_analysis_returns_symbol_table_and_resolution(
        sample_module: Decl,
    ) -> None:
    '''
    Test that analysis returns a symbol table and a resolution.

    :param sample_module: The module declaration to analyze.
    :type sample_module: Decl
    '''

    # Invoke the event only through the domain event handler.
    result = DomainEvent.handle(
        PerformSemanticAnalysis,
        ast=sample_module,
        source_file='events.py',
        **_provision_kwargs(),
    )

    # The result names the module and includes both required tables.
    assert 'symbol_table' in result
    assert 'resolution' in result
    assert result['provision_findings'] == []
    assert result['symbol_table']['module_name'] == 'events'
    assert 'scopes' in result['symbol_table']
    assert 'module' in result['symbol_table']['scopes']

# ** test: perform_semantic_analysis_registers_class_in_module_scope
def test_perform_semantic_analysis_registers_class_in_module_scope(
        sample_module: Decl,
    ) -> None:
    '''
    Test that a class declaration is registered in the module scope.

    :param sample_module: The module declaration to analyze.
    :type sample_module: Decl
    '''

    # Invoke the event only through the domain event handler.
    result = DomainEvent.handle(
        PerformSemanticAnalysis,
        ast=sample_module,
        **_provision_kwargs(),
    )

    # The class is a class definition in the module scope.
    symbols = result['symbol_table']['scopes']['module']['symbols']
    assert symbols['Ping']['kind'] == SYMBOL_KIND_CLASS_DEF

# ** test: perform_semantic_analysis_rejects_invalid_ast
def test_perform_semantic_analysis_rejects_invalid_ast() -> None:
    '''
    Test that a non-declaration AST raises INVALID_AST_STRUCTURE.
    '''

    # A truthy non-Decl fails verification, not the required-parameter check.
    with pytest.raises(TiferetError) as exc_info:
        DomainEvent.handle(
            PerformSemanticAnalysis,
            ast='not-a-decl',
            **_provision_kwargs(),
        )

    # The verify code is the string. Catalog registration is a later story.
    assert exc_info.value.error_code == 'INVALID_AST_STRUCTURE'

# ** test: emit_semantic_result_returns_payload_without_output
def test_emit_semantic_result_returns_payload_without_output(
        sample_semantic: dict,
    ) -> None:
    '''
    Test that omitting output returns a SemanticAnalysisCompleted payload.

    :param sample_semantic: The analysis result to emit.
    :type sample_semantic: dict
    '''

    # Invoke the event only through the domain event handler.
    result = DomainEvent.handle(
        EmitSemanticResult,
        semantic=sample_semantic,
        source_file='events.py',
    )

    # The payload names the analysis and keeps symbol-table data when there are no findings.
    assert result['event_type'] == 'SemanticAnalysisCompleted'
    assert result['source_file'] == 'events.py'
    assert result['timestamp'].endswith('+00:00')
    assert result['symbol_table'] == sample_semantic['symbol_table']
    assert result['resolution'] == sample_semantic['resolution']

# ** test: emit_semantic_result_omits_symbol_table_when_findings
def test_emit_semantic_result_omits_symbol_table_when_findings(
        sample_semantic: dict,
        capsys: pytest.CaptureFixture,
    ) -> None:
    '''
    Test that findings omit symbol-table data and are printed.

    :param sample_semantic: The analysis result to emit.
    :type sample_semantic: dict
    :param capsys: The pytest capture fixture.
    :type capsys: pytest.CaptureFixture
    '''

    # One finding has a location. The other uses the printed defaults.
    findings = [
        {
            'error_code': 'UNRESOLVED_NAME',
            'scope_path': 'module.Ping',
            'lineno': 4,
            'col': 8,
            'message': 'name is undefined',
        },
        {
            'message': 'missing fields',
        },
    ]

    # Invoke the event only through the domain event handler.
    result = DomainEvent.handle(
        EmitSemanticResult,
        semantic=sample_semantic,
        findings=findings,
    )

    # Findings replace the symbol table and resolution in the payload.
    assert result['event_type'] == 'SemanticAnalysisCompleted'
    assert 'timestamp' in result
    assert 'symbol_table' not in result
    assert 'resolution' not in result

    # Each finding is printed in the type-error format.
    assert capsys.readouterr().out == (
        'Type Error [UNRESOLVED_NAME] in module.Ping (line 4, col 8): name is undefined\n'
        'Type Error [UNKNOWN] in ?: missing fields\n'
    )

# ** test: emit_semantic_result_writes_file_when_output_set
def test_emit_semantic_result_writes_file_when_output_set(
        sample_semantic: dict,
        tmp_path: Path,
    ) -> None:
    '''
    Test that a destination path writes the payload and returns an empty string.

    :param sample_semantic: The analysis result to emit.
    :type sample_semantic: dict
    :param tmp_path: Temporary directory for the output file.
    :type tmp_path: Path
    '''

    # A non-json path is written as YAML by the output writer.
    output_path = tmp_path / 'semantic.yaml'

    # Invoke the event only through the domain event handler.
    result = DomainEvent.handle(
        EmitSemanticResult,
        semantic=sample_semantic,
        output=str(output_path),
    )

    # The write replaces the payload, and the file contains the event type.
    assert result == ''
    assert output_path.is_file()
    assert 'SemanticAnalysisCompleted' in output_path.read_text(encoding='utf-8')
