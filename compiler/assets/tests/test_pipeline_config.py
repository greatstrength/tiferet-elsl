"""Pipeline Configuration Tests"""

# *** imports

# ** core
from pathlib import Path

# ** app
from ..app import COMPILER_DEFAULT_SERVICES
from ..cli import COMPILER_DEFAULT_COMMANDS
from ..feature import COMPILER_DEFAULT_FEATURES

# *** constants

# ** constant: assets_dir
_ASSETS_DIR = Path(__file__).resolve().parent.parent

# ** constant: component_types
_COMPONENT_TYPES = (
    'assets',
    'blueprints',
    'contexts',
    'di',
    'domain',
    'events',
    'interfaces',
    'mappers',
    'repos',
    'utils',
)

# ** constant: dialect_steps
_DIALECT_STEPS = (
    ('assets', 'check_asset_conformance_event', "$r.component == 'assets'"),
    ('blueprints', 'check_blueprints_conformance_event', "$r.component == 'blueprints'"),
    ('contexts', 'check_context_conformance_event', "$r.component == 'contexts'"),
    ('di', 'check_di_conformance_event', "$r.component == 'di'"),
    ('domain', 'check_domain_conformance_event', "$r.component == 'domain'"),
    ('events', 'check_event_conformance_event', "$r.component == 'events'"),
    ('interfaces', 'check_interface_conformance_event', "$r.component == 'interfaces'"),
    ('mappers', 'check_mapper_conformance_event', "$r.component == 'mappers'"),
    ('repos', 'check_repos_conformance_event', "$r.component == 'repos'"),
    ('utils', 'check_utils_conformance_event', "$r.component == 'utils'"),
)

# ** constant: semantic_bearing_features
_SEMANTIC_BEARING_FEATURES = (
    'semantic.module',
    'compile.module',
    'compile.ast',
)

# *** functions

# ** function: command_arguments
def command_arguments(command_id: str) -> list:
    '''
    Return the argument list for one CLI command.

    :param command_id: The command id.
    :type command_id: str
    :return: The command arguments.
    :rtype: list
    '''

    # Arguments live on the command catalog, not a document key.
    return COMPILER_DEFAULT_COMMANDS[command_id]['arguments']

# ** function: component_args
def component_args(args: list) -> list:
    '''
    Return arguments that declare the component flag.

    :param args: The command arguments.
    :type args: list
    :return: Arguments whose flags include -c or --component.
    :rtype: list
    '''

    # Match either flag. A command declares the flag once.
    return [
        arg for arg in args
        if '-c' in (arg.get('name_or_flags') or [])
        or '--component' in (arg.get('name_or_flags') or [])
    ]

# ** function: feature_steps
def feature_steps(feature_id: str) -> list:
    '''
    Return the steps for one feature.

    :param feature_id: The feature id.
    :type feature_id: str
    :return: The feature steps.
    :rtype: list
    '''

    # Steps live on the feature catalog, not a nested document.
    return COMPILER_DEFAULT_FEATURES[feature_id]['steps']

# *** tests

# ** test: feature_ids_are_module_not_event
def test_feature_ids_are_module_not_event() -> None:
    '''
    Test that pipelines use module and ast keys, not an event key.
    '''

    # The five neutral pipelines exist, in document order.
    assert list(COMPILER_DEFAULT_FEATURES) == [
        'scan.module',
        'parse.module',
        'semantic.module',
        'compile.module',
        'compile.ast',
    ]

    # No phase exposes an event command key.
    assert 'scan.event' not in COMPILER_DEFAULT_FEATURES
    assert 'parse.event' not in COMPILER_DEFAULT_FEATURES
    assert 'semantic.event' not in COMPILER_DEFAULT_FEATURES
    assert 'compile.event' not in COMPILER_DEFAULT_FEATURES

# ** test: cli_commands_are_module_not_event
def test_cli_commands_are_module_not_event() -> None:
    '''
    Test that the scan command is module, not event.
    '''

    # The neutral module command exists, and no event key is declared.
    assert 'scan.module' in COMPILER_DEFAULT_COMMANDS
    assert 'scan.event' not in COMPILER_DEFAULT_COMMANDS

# ** test: component_flag_required_on_semantic_bearing_commands
def test_component_flag_required_on_semantic_bearing_commands() -> None:
    '''
    Test that semantic-bearing commands require the ten component choices.
    '''

    # Semantic-bearing commands require the component flag.
    for command_id in (
        'semantic.module',
        'compile.module',
        'compile.ast',
    ):
        found = component_args(command_arguments(command_id))
        assert len(found) == 1
        assert found[0]['required'] is True
        assert found[0]['choices'] == list(_COMPONENT_TYPES)

    # Scan and parse do not declare the flag.
    assert component_args(command_arguments('scan.module')) == []
    assert component_args(command_arguments('parse.module')) == []

# ** test: gated_dialect_steps_include_di_and_utils
def test_gated_dialect_steps_include_di_and_utils() -> None:
    '''
    Test that semantic-bearing pipelines gate the di and utils dialects.
    '''

    # Each semantic-bearing pipeline includes both gated steps.
    for feature_id in _SEMANTIC_BEARING_FEATURES:
        steps = feature_steps(feature_id)
        assert any(
            step.get('service_id') == 'check_di_conformance_event'
            and step.get('condition') == "$r.component == 'di'"
            for step in steps
        )
        assert any(
            step.get('service_id') == 'check_utils_conformance_event'
            and step.get('condition') == "$r.component == 'utils'"
            for step in steps
        )

# ** test: all_ten_dialects_have_gated_steps
def test_all_ten_dialects_have_gated_steps() -> None:
    '''
    Test that each component type has a gated conformance step.
    '''

    # Every dialect is gated in every semantic-bearing pipeline.
    for feature_id in _SEMANTIC_BEARING_FEATURES:
        steps = feature_steps(feature_id)
        for _component, service_id, condition in _DIALECT_STEPS:
            assert any(
                step.get('service_id') == service_id
                and step.get('condition') == condition
                for step in steps
            )

# ** test: config_registers_di_and_utils_conformance_events
def test_config_registers_di_and_utils_conformance_events() -> None:
    '''
    Test that the service catalog registers the di and utils conformance events.
    '''

    # The landed class names are registered under the service ids.
    assert COMPILER_DEFAULT_SERVICES['check_di_conformance_event']['class_name'] == 'CheckDIConformance'
    assert COMPILER_DEFAULT_SERVICES['check_utils_conformance_event']['class_name'] == 'CheckUtilsConformance'

# ** test: findings_data_key_on_conformance_steps
def test_findings_data_key_on_conformance_steps() -> None:
    '''
    Test that common and gated conformance steps accumulate findings.
    '''

    # Common plus the ten gated dialects.
    conformance_ids = {'check_common_conformance_event'} | {
        service_id for _component, service_id, _condition in _DIALECT_STEPS
    }

    # Every conformance step in every semantic-bearing pipeline stores findings.
    for feature_id in _SEMANTIC_BEARING_FEATURES:
        steps = feature_steps(feature_id)
        conformance_steps = [
            step for step in steps
            if step.get('service_id') in conformance_ids
        ]
        assert len(conformance_steps) == len(conformance_ids)
        assert all(step.get('data_key') == 'findings' for step in conformance_steps)

# ** test: no_scan_event_or_compile_event_strings
def test_no_scan_event_or_compile_event_strings() -> None:
    '''
    Test that the pipeline catalogs do not name retired event commands.
    '''

    # Read the three catalog modules as text. Do not boot App or CLI.
    for name in ('app.py', 'feature.py', 'cli.py'):
        text = (_ASSETS_DIR / name).read_text(encoding='utf-8')
        assert 'scan.event' not in text
        assert 'compile.event' not in text
