"""Pipeline Configuration Tests"""

# *** imports

# ** core
from pathlib import Path

# ** infra
import yaml

# *** constants

# ** constant: assets_dir
ASSETS_DIR = Path(__file__).resolve().parent.parent

# ** constant: component_types
COMPONENT_TYPES = (
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
DIALECT_STEPS = (
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
SEMANTIC_BEARING_FEATURES = (
    ('semantic', 'module'),
    ('compile', 'module'),
    ('compile', 'ast'),
)

# *** functions

# ** function: load_yaml
def load_yaml(name: str) -> dict:
    '''
    Load one compiler asset YAML file.

    :param name: The file name under compiler/assets.
    :type name: str
    :return: The parsed document.
    :rtype: dict
    '''

    # Read the asset next to this test package. Do not boot App or CLI.
    path = ASSETS_DIR / name
    with path.open(encoding='utf-8') as handle:
        return yaml.safe_load(handle)

# ** function: command_args
def command_args(cli: dict, group_key: str, key: str) -> list:
    '''
    Return the argument list for one CLI command.

    :param cli: The parsed CLI document.
    :type cli: dict
    :param group_key: The command group.
    :type group_key: str
    :param key: The command key.
    :type key: str
    :return: The command arguments.
    :rtype: list
    '''

    # Missing args are an empty declaration, not a boot failure.
    return cli['cli']['cmds'][group_key][key].get('args') or []

# ** function: component_args
def component_args(args: list) -> list:
    '''
    Return arguments that declare the component flag.

    :param args: The command arguments.
    :type args: list
    :return: Arguments whose flags include -c or --component.
    :rtype: list
    '''

    # Match either flag. A command may declare the shared anchor once.
    return [
        arg for arg in args
        if '-c' in (arg.get('name_or_flags') or [])
        or '--component' in (arg.get('name_or_flags') or [])
    ]

# ** function: feature_steps
def feature_steps(features: dict, group_id: str, feature_key: str) -> list:
    '''
    Return the steps for one feature.

    :param features: The parsed feature document.
    :type features: dict
    :param group_id: The feature group.
    :type group_id: str
    :param feature_key: The feature key.
    :type feature_key: str
    :return: The feature steps.
    :rtype: list
    '''

    # Aliased steps resolve to the anchored mapping.
    return features['features'][group_id][feature_key].get('steps') or []

# *** tests

# ** test: feature_ids_are_module_not_event
def test_feature_ids_are_module_not_event() -> None:
    '''
    Test that pipelines use module and ast keys, not an event key.
    '''

    # Load the feature document without booting the app.
    features = load_yaml('feature.yml')['features']

    # The five neutral pipelines exist.
    assert 'module' in features['scan']
    assert 'module' in features['parse']
    assert 'module' in features['semantic']
    assert 'module' in features['compile']
    assert 'ast' in features['compile']

    # No phase exposes an event command key.
    assert 'event' not in features['scan']
    assert 'event' not in features['parse']
    assert 'event' not in features['semantic']
    assert 'event' not in features['compile']

# ** test: cli_commands_are_module_not_event
def test_cli_commands_are_module_not_event() -> None:
    '''
    Test that the scan command is module, not event.
    '''

    # Load the CLI document without constructing a parser.
    scan = load_yaml('cli.yml')['cli']['cmds']['scan']

    # The neutral module command exists, and no event key is declared.
    assert 'module' in scan
    assert 'event' not in scan

# ** test: component_flag_required_on_semantic_bearing_commands
def test_component_flag_required_on_semantic_bearing_commands() -> None:
    '''
    Test that semantic-bearing commands require the ten component choices.
    '''

    # Load commands without booting the CLI.
    cli = load_yaml('cli.yml')

    # Semantic-bearing commands require the shared component flag.
    for group_key, key in (
        ('semantic', 'module'),
        ('compile', 'module'),
        ('compile', 'ast'),
    ):
        found = component_args(command_args(cli, group_key, key))
        assert len(found) == 1
        assert found[0]['required'] is True
        assert found[0]['choices'] == list(COMPONENT_TYPES)

    # Scan and parse do not declare the flag.
    assert component_args(command_args(cli, 'scan', 'module')) == []
    assert component_args(command_args(cli, 'parse', 'module')) == []

# ** test: gated_dialect_steps_include_di_and_utils
def test_gated_dialect_steps_include_di_and_utils() -> None:
    '''
    Test that semantic-bearing pipelines gate the di and utils dialects.
    '''

    # Load features without importing event classes.
    features = load_yaml('feature.yml')

    # Each semantic-bearing pipeline includes both gated steps.
    for group_id, feature_key in SEMANTIC_BEARING_FEATURES:
        steps = feature_steps(features, group_id, feature_key)
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

    # Load features without importing event classes.
    features = load_yaml('feature.yml')

    # Every dialect is gated in every semantic-bearing pipeline.
    for group_id, feature_key in SEMANTIC_BEARING_FEATURES:
        steps = feature_steps(features, group_id, feature_key)
        for _component, service_id, condition in DIALECT_STEPS:
            assert any(
                step.get('service_id') == service_id
                and step.get('condition') == condition
                for step in steps
            )

# ** test: config_registers_di_and_utils_conformance_events
def test_config_registers_di_and_utils_conformance_events() -> None:
    '''
    Test that DI registers the di and utils conformance events.
    '''

    # Load services without importing the event classes.
    services = load_yaml('config.yml')['services']

    # The landed class names are registered under the TRD service ids.
    assert services['check_di_conformance_event']['class_name'] == 'CheckDIConformance'
    assert services['check_utils_conformance_event']['class_name'] == 'CheckUtilsConformance'

# ** test: findings_data_key_on_conformance_steps
def test_findings_data_key_on_conformance_steps() -> None:
    '''
    Test that common and gated conformance steps accumulate findings.
    '''

    # Load features without importing event classes.
    features = load_yaml('feature.yml')
    conformance_ids = {'check_common_conformance_event'} | {
        service_id for _component, service_id, _condition in DIALECT_STEPS
    }

    # Every conformance step in every semantic-bearing pipeline stores findings.
    for group_id, feature_key in SEMANTIC_BEARING_FEATURES:
        steps = feature_steps(features, group_id, feature_key)
        conformance_steps = [
            step for step in steps
            if step.get('service_id') in conformance_ids
        ]
        assert len(conformance_steps) == len(conformance_ids)
        assert all(step.get('data_key') == 'findings' for step in conformance_steps)

# ** test: no_scan_event_or_compile_event_strings
def test_no_scan_event_or_compile_event_strings() -> None:
    '''
    Test that the pipeline YAML does not name retired event commands.
    '''

    # Read the three pipeline files as text. Do not boot App or CLI.
    for name in ('config.yml', 'feature.yml', 'cli.yml'):
        text = (ASSETS_DIR / name).read_text(encoding='utf-8')
        assert 'scan.event' not in text
        assert 'compile.event' not in text
