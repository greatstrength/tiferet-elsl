"""Code Generation Domain Event Tests"""

# *** imports

# ** core
import json
from pathlib import Path
from unittest.mock import Mock

# ** infra
import pytest

# ** app
from ..codegen import (
    EmitCodegenResult,
    GenerateCode,
    LoadFromAST,
    OptimizeCode,
)
from ..settings import DomainEvent, TiferetError
from ...interfaces import CodegenService, OptimizerService
from ...mappers import Decl, DeclarationTransferObject

# *** fixtures

# ** fixture: mock_codegen_service
@pytest.fixture
def mock_codegen_service() -> Mock:
    '''
    Fixture for a code generator service mock.

    :return: The code generator service mock.
    :rtype: Mock
    '''

    # Spec the interface so unexpected calls fail.
    return Mock(spec=CodegenService)

# ** fixture: mock_optimizer_service
@pytest.fixture
def mock_optimizer_service() -> Mock:
    '''
    Fixture for an optimizer service mock.

    :return: The optimizer service mock.
    :rtype: Mock
    '''

    # Spec the interface so unexpected calls fail.
    return Mock(spec=OptimizerService)

# ** fixture: sample_ast
@pytest.fixture
def sample_ast() -> Decl:
    '''
    Fixture for a module declaration the generator receives.

    :return: The sample module declaration.
    :rtype: Decl
    '''

    # The event passes this through. It does not inspect it.
    return Decl.new_module_decl(name='events')

# ** fixture: sample_codegen
@pytest.fixture
def sample_codegen() -> dict:
    '''
    Fixture for a codegen dict the optimizer and emitter pass through.

    :return: The sample codegen dict.
    :rtype: dict
    '''

    # The events do not walk this dict.
    return {
        'module': 'events',
        'cmpt': [],
    }

# ** fixture: sample_transfer
@pytest.fixture
def sample_transfer(sample_ast: Decl) -> dict:
    '''
    Fixture for the transfer-shaped form of the sample declaration.

    :param sample_ast: The sample module declaration.
    :type sample_ast: Decl
    :return: The serialized declaration.
    :rtype: dict
    '''

    # Match the serialization LoadFromAST validates.
    return DeclarationTransferObject.from_model(sample_ast).to_primitive()

# *** tests

# ** test: generate_code_success
def test_generate_code_success(
        mock_codegen_service: Mock,
        sample_ast: Decl,
        sample_codegen: dict,
    ) -> None:
    '''
    Test that generation calls the service with the default kind and returns its dict.

    :param mock_codegen_service: The code generator service mock.
    :type mock_codegen_service: Mock
    :param sample_ast: The module declaration to generate from.
    :type sample_ast: Decl
    :param sample_codegen: The dict the generator returns.
    :type sample_codegen: dict
    '''

    # The generator returns the sample dict.
    mock_codegen_service.generate.return_value = sample_codegen

    # Invoke the event only through the domain event handler.
    result = DomainEvent.handle(
        GenerateCode,
        dependencies={
            'codegen_service': mock_codegen_service,
        },
        ast=sample_ast,
    )

    # The default component is passed as kind, and the handler returns that dict.
    mock_codegen_service.generate.assert_called_once_with(
        sample_ast,
        kind='events',
    )
    assert result == sample_codegen

# ** test: generate_code_passes_component_as_kind
def test_generate_code_passes_component_as_kind(
        mock_codegen_service: Mock,
        sample_ast: Decl,
    ) -> None:
    '''
    Test that a component argument is passed as the generator kind.

    :param mock_codegen_service: The code generator service mock.
    :type mock_codegen_service: Mock
    :param sample_ast: The module declaration to generate from.
    :type sample_ast: Decl
    '''

    # The return value is unused beyond the call assertion.
    mock_codegen_service.generate.return_value = {'module': 'assets'}

    # Invoke the event only through the domain event handler.
    DomainEvent.handle(
        GenerateCode,
        dependencies={
            'codegen_service': mock_codegen_service,
        },
        ast=sample_ast,
        component='assets',
    )

    # assets is the kind, not a separate generator argument.
    mock_codegen_service.generate.assert_called_once_with(
        sample_ast,
        kind='assets',
    )

# ** test: generate_code_missing_ast
def test_generate_code_missing_ast(
        mock_codegen_service: Mock,
    ) -> None:
    '''
    Test that omitting ast raises the parameters-required error.

    :param mock_codegen_service: The code generator service mock.
    :type mock_codegen_service: Mock
    '''

    # Omitting ast is a required-parameter failure, not a generate call.
    with pytest.raises(TiferetError) as exc_info:
        DomainEvent.handle(
            GenerateCode,
            dependencies={
                'codegen_service': mock_codegen_service,
            },
        )

    # The missing parameter is ast, and the generator is not called.
    assert 'ast' in exc_info.value.kwargs.get('parameters', [])
    mock_codegen_service.generate.assert_not_called()

# ** test: optimize_code_o0_passthrough
def test_optimize_code_o0_passthrough(
        mock_optimizer_service: Mock,
        sample_codegen: dict,
    ) -> None:
    '''
    Test that the default level and O0 return the input dict without optimizing.

    :param mock_optimizer_service: The optimizer service mock.
    :type mock_optimizer_service: Mock
    :param sample_codegen: The codegen dict to pass through.
    :type sample_codegen: dict
    '''

    # The default level is O0.
    default_result = DomainEvent.handle(
        OptimizeCode,
        dependencies={
            'optimizer_service': mock_optimizer_service,
        },
        codegen=sample_codegen,
    )

    # An explicit O0 request is the same passthrough.
    explicit_result = DomainEvent.handle(
        OptimizeCode,
        dependencies={
            'optimizer_service': mock_optimizer_service,
        },
        codegen=sample_codegen,
        O='O0',
    )

    # Neither call optimizes, and both return the same dict.
    mock_optimizer_service.optimize.assert_not_called()
    assert default_result is sample_codegen
    assert explicit_result is sample_codegen

# ** test: optimize_code_success
def test_optimize_code_success(
        mock_optimizer_service: Mock,
        sample_codegen: dict,
    ) -> None:
    '''
    Test that O1 calls the optimizer and returns its result.

    :param mock_optimizer_service: The optimizer service mock.
    :type mock_optimizer_service: Mock
    :param sample_codegen: The codegen dict to optimize.
    :type sample_codegen: dict
    '''

    # The optimizer returns a distinct dict.
    optimized = {
        'module': 'events',
        'optimized': True,
    }
    mock_optimizer_service.optimize.return_value = optimized

    # Invoke the event only through the domain event handler.
    result = DomainEvent.handle(
        OptimizeCode,
        dependencies={
            'optimizer_service': mock_optimizer_service,
        },
        codegen=sample_codegen,
        O='O1',
    )

    # O1 optimizes once and returns that result.
    mock_optimizer_service.optimize.assert_called_once_with(sample_codegen)
    assert result is optimized

# ** test: optimize_code_missing_codegen
def test_optimize_code_missing_codegen(
        mock_optimizer_service: Mock,
    ) -> None:
    '''
    Test that omitting codegen raises the parameters-required error.

    :param mock_optimizer_service: The optimizer service mock.
    :type mock_optimizer_service: Mock
    '''

    # Omitting codegen is a required-parameter failure, not an optimize call.
    with pytest.raises(TiferetError) as exc_info:
        DomainEvent.handle(
            OptimizeCode,
            dependencies={
                'optimizer_service': mock_optimizer_service,
            },
            O='O1',
        )

    # The missing parameter is codegen, and the optimizer is not called.
    assert 'codegen' in exc_info.value.kwargs.get('parameters', [])
    mock_optimizer_service.optimize.assert_not_called()

# ** test: emit_codegen_result_returns_dict
def test_emit_codegen_result_returns_dict(
        sample_codegen: dict,
    ) -> None:
    '''
    Test that omitting output returns the codegen dict.

    :param sample_codegen: The codegen dict to emit.
    :type sample_codegen: dict
    '''

    # Invoke the event only through the domain event handler.
    result = DomainEvent.handle(
        EmitCodegenResult,
        codegen=sample_codegen,
        source_file='events.py',
    )

    # No destination means the dict is returned unchanged.
    assert result == sample_codegen

# ** test: emit_codegen_result_writes_yaml
def test_emit_codegen_result_writes_yaml(
        sample_codegen: dict,
        tmp_path: Path,
    ) -> None:
    '''
    Test that a yaml destination writes the dict and returns an empty string.

    :param sample_codegen: The codegen dict to emit.
    :type sample_codegen: dict
    :param tmp_path: Temporary directory for the output file.
    :type tmp_path: Path
    '''

    # A .yaml path is written as YAML by the output writer.
    output_path = tmp_path / 'codegen.yaml'

    # Invoke the event only through the domain event handler.
    result = DomainEvent.handle(
        EmitCodegenResult,
        codegen=sample_codegen,
        output=str(output_path),
    )

    # The write replaces the dict, and the file contains the module name.
    assert result == ''
    assert output_path.is_file()
    assert 'module: events' in output_path.read_text(encoding='utf-8')

# ** test: emit_codegen_result_writes_json
def test_emit_codegen_result_writes_json(
        sample_codegen: dict,
        tmp_path: Path,
    ) -> None:
    '''
    Test that a json destination writes the dict and returns an empty string.

    :param sample_codegen: The codegen dict to emit.
    :type sample_codegen: dict
    :param tmp_path: Temporary directory for the output file.
    :type tmp_path: Path
    '''

    # A .json path is written as JSON by the output writer.
    output_path = tmp_path / 'codegen.json'

    # Invoke the event only through the domain event handler.
    result = DomainEvent.handle(
        EmitCodegenResult,
        codegen=sample_codegen,
        output=str(output_path),
    )

    # The write replaces the dict, and the file is the codegen payload.
    assert result == ''
    assert output_path.is_file()
    assert json.loads(output_path.read_text(encoding='utf-8')) == sample_codegen

# ** test: emit_codegen_result_missing_codegen
def test_emit_codegen_result_missing_codegen() -> None:
    '''
    Test that omitting codegen raises the parameters-required error.
    '''

    # Omitting codegen is a required-parameter failure.
    with pytest.raises(TiferetError) as exc_info:
        DomainEvent.handle(EmitCodegenResult)

    # The missing parameter is codegen.
    assert 'codegen' in exc_info.value.kwargs.get('parameters', [])

# ** test: load_from_ast_rebuilds_declaration
def test_load_from_ast_rebuilds_declaration(
        sample_transfer: dict,
        tmp_path: Path,
    ) -> None:
    '''
    Test that a transfer-shaped JSON AST maps back to a declaration with the same name.

    :param sample_transfer: The serialized module declaration.
    :type sample_transfer: dict
    :param tmp_path: Temporary directory for the JSON file.
    :type tmp_path: Path
    '''

    # Write a bare AST dict, not a parse-result envelope.
    source_path = tmp_path / 'events.json'
    source_path.write_text(
        json.dumps(sample_transfer),
        encoding='utf-8',
    )

    # Invoke the event only through the domain event handler.
    result = DomainEvent.handle(
        LoadFromAST,
        source_file=str(source_path),
    )

    # The mapped declaration keeps the module name.
    assert isinstance(result, Decl)
    assert result.name == 'events'

# ** test: load_from_ast_unwraps_parse_payload
def test_load_from_ast_unwraps_parse_payload(
        sample_transfer: dict,
        tmp_path: Path,
    ) -> None:
    '''
    Test that a parse-result payload still maps the nested AST.

    :param sample_transfer: The serialized module declaration.
    :type sample_transfer: dict
    :param tmp_path: Temporary directory for the JSON file.
    :type tmp_path: Path
    '''

    # Wrap the transfer dict the way a parse result does.
    source_path = tmp_path / 'parse.json'
    source_path.write_text(
        json.dumps({
            'ast': sample_transfer,
            'event_type': 'ParseCompleted',
        }),
        encoding='utf-8',
    )

    # Invoke the event only through the domain event handler.
    result = DomainEvent.handle(
        LoadFromAST,
        source_file=str(source_path),
    )

    # Unwrapping the ast key still yields the named declaration.
    assert isinstance(result, Decl)
    assert result.name == 'events'

# ** test: load_from_ast_missing_file_raises
def test_load_from_ast_missing_file_raises(tmp_path: Path) -> None:
    '''
    Test that a missing source file raises.

    :param tmp_path: Temporary directory that does not contain the file.
    :type tmp_path: Path
    '''

    # The path is a JSON name that was never written.
    missing = tmp_path / 'missing.json'

    # The file layer raises. This event does not add an error code.
    with pytest.raises(Exception):
        DomainEvent.handle(
            LoadFromAST,
            source_file=str(missing),
        )

# ** test: no_perform_type_check_name
def test_no_perform_type_check_name() -> None:
    '''
    Test that the codegen event module does not define PerformTypeCheck.
    '''

    # Import the module under test. The name must not be defined.
    from .. import codegen as codegen_events

    # Code generation does not own a type-check event.
    assert not hasattr(codegen_events, 'PerformTypeCheck')
