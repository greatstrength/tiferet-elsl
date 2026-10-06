"""Compiler – Schema Freeze Tests"""

# *** imports

# ** core
from pathlib import Path
from typing import List

# ** app
import compiler
from ..assets.app import COMPILER_DEFAULT_APP_SESSIONS
from ..assets.cli import COMPILER_DEFAULT_COMMANDS
from ..assets.feature import COMPILER_DEFAULT_FEATURES
from ..domain.ast import ParamList, Statement, Type
from ..events.typecheck import CheckDomainConformance
from ..mappers.artifact import (
    ArtifactDeclarationAggregate,
    ArtifactStatementAggregate,
)
from ..mappers.ast import (
    DeclarationAggregate,
    ExpressionAggregate,
    StatementAggregate,
    TypeAggregate,
)
from ..mappers.codegen import EventAccumulator, SnippetAccumulator
from ..mappers.transfer import (
    DeclarationTransferObject,
    ParamListTransferObject,
    StatementTransferObject,
    TypeTransferObject,
)
from ..blueprints.core import build_cache
from ..contexts.provision import COMPILER_PROVISION_CACHE_PREFIX
from ..utils.codegen import TiferetGenerator
from ..utils.semantic import SymbolTableBuilder

# *** tests

# ** test: version_is_1_1_0b1
def test_version_is_1_1_0b1():
    '''
    Test that the compiler package version is the open prototype beta.
    '''

    # The version is the package attribute, not a second project file.
    assert compiler.__version__ == '1.1.0b1'

    # The distribution name is tiferet-elsl. Retired names stay off the surface.
    repo_root = Path(__file__).resolve().parents[2]
    assert not (repo_root / 'compiler' / 'pyproject.toml').exists()
    project = (repo_root / 'pyproject.toml').read_text(encoding='utf-8')
    assert 'name = "tiferet-elsl"' in project
    assert 'name = "tiferet-compiler"' not in project
    assert 'tiferet-command-parser-edu' not in project

# ** test: cli_command_surface
def test_cli_command_surface():
    '''
    Test that the CLI names only the five frozen module commands.
    '''

    # Command ids are the catalog keys. Order is the document order.
    found = list(COMPILER_DEFAULT_COMMANDS)
    assert found == [
        'scan.module',
        'parse.module',
        'semantic.module',
        'compile.module',
        'compile.ast',
    ]

    # Each value's group_key and key are that split.
    for command_id, command in COMPILER_DEFAULT_COMMANDS.items():
        group_key, key = command_id.split('.', 1)
        assert command['group_key'] == group_key
        assert command['key'] == key

    # Retired event commands are absent.
    assert 'scan.event' not in COMPILER_DEFAULT_COMMANDS
    assert 'compile.event' not in COMPILER_DEFAULT_COMMANDS

# ** test: component_choices
def test_component_choices():
    '''
    Test that semantic-bearing commands require the ten component choices.
    '''

    # Read arguments from the command catalog. Do not construct a parser.
    choices = [
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
    ]

    # semantic.module and both compile commands require -c / --component.
    for command_id in (
        'semantic.module',
        'compile.module',
        'compile.ast',
    ):
        matches = [
            arg for arg in COMPILER_DEFAULT_COMMANDS[command_id]['arguments']
            if '-c' in (arg.get('name_or_flags') or [])
            and '--component' in (arg.get('name_or_flags') or [])
        ]
        assert len(matches) == 1
        assert matches[0]['required'] is True
        assert matches[0]['choices'] == choices

# ** test: session_and_asset_files
def test_session_and_asset_files():
    '''
    Test that the frozen session ids are the application catalog keys.
    '''

    # The two app sessions are the frozen session ids, in document order.
    assert list(COMPILER_DEFAULT_APP_SESSIONS) == [
        'compiler',
        'compiler_cli',
    ]

# ** test: codegen_envelope_keys
def test_codegen_envelope_keys():
    '''
    Test that generate keeps cmpt, and evt_grp only for events.
    '''

    # A documented module records desc. A bare module omits it.
    documented = DeclarationAggregate.new_module_decl(
        name='feature',
        doc_string='"""Feature events."""',
    )
    bare = DeclarationAggregate.new_module_decl(name='feature')
    events = TiferetGenerator().generate(documented, kind='events')
    domain = TiferetGenerator().generate(bare, kind='domain')

    # cmpt is always present. evt_grp is dual-emitted only for events.
    assert set(events) == {'cmpt', 'evt_grp'}
    assert 'evt_grp' not in events['cmpt']
    assert events['cmpt']['name'] == 'feature'
    assert events['cmpt']['kind'] == 'events'
    assert isinstance(events['cmpt']['name'], str)
    assert events['cmpt']['desc'] == 'Feature events.'
    assert set(events['evt_grp']) <= {'name', 'desc', 'impt', 'fncs', 'evts'}
    assert events['evt_grp']['name'] == 'feature'
    assert events['evt_grp']['desc'] == 'Feature events.'
    assert 'evt_grp' not in domain
    assert domain['cmpt']['kind'] == 'domain'
    assert 'desc' not in domain['cmpt']

    # Short names are the emitted keys. Long replacements stay absent.
    imports = ArtifactStatementAggregate.new_artifact_stmt(
        ArtifactDeclarationAggregate.new_artifact_decl(
            name='imports',
            artifact_type='***',
        ),
        [
            ArtifactStatementAggregate.new_artifact_stmt(
                ArtifactDeclarationAggregate.new_artifact_decl(
                    name='core',
                    artifact_type='**',
                ),
                [
                    StatementAggregate.new_import_stmt_from(
                        ExpressionAggregate.new_name_expr('typing'),
                        ExpressionAggregate.new_name_expr('Any'),
                    ),
                ],
            ),
        ],
    )
    function = ArtifactStatementAggregate.new_artifact_stmt(
        ArtifactDeclarationAggregate.new_artifact_decl(
            name='functions',
            artifact_type='***',
        ),
        [
            ArtifactStatementAggregate.new_artifact_stmt(
                ArtifactDeclarationAggregate.new_artifact_decl(
                    name='build_app',
                    artifact_type='** function',
                ),
                [
                    StatementAggregate.new_decl_stmt(
                        DeclarationAggregate.new_func_decl(
                            name='build_app',
                            type=TypeAggregate.new_func_type(params=[]),
                            body=[],
                        ),
                    ),
                ],
            ),
        ],
    )
    event_group = ArtifactStatementAggregate.new_artifact_stmt(
        ArtifactDeclarationAggregate.new_artifact_decl(
            name='events',
            artifact_type='***',
        ),
        [
            ArtifactStatementAggregate.new_artifact_stmt(
                ArtifactDeclarationAggregate.new_artifact_decl(
                    name='get_feature',
                    artifact_type='** event',
                ),
                [
                    StatementAggregate.new_decl_stmt(
                        DeclarationAggregate.new_class_decl(
                            name='GetFeature',
                            subclasses=None,
                            doc_string=None,
                            members=[],
                        ),
                    ),
                ],
            ),
        ],
    )
    filled = TiferetGenerator().generate(
        DeclarationAggregate.new_module_decl(
            name='feature',
            code=[imports, function, event_group],
        ),
        kind='events',
    )

    # Optional envelope keys use the short names when they are present.
    assert set(filled['cmpt']) <= {'name', 'kind', 'desc', 'impt', 'grps'}
    assert 'impt' in filled['cmpt']
    assert 'grps' in filled['cmpt']
    assert set(filled['evt_grp']) <= {'name', 'desc', 'impt', 'fncs', 'evts'}
    assert 'fncs' in filled['evt_grp']
    assert 'evts' in filled['evt_grp']
    assert 'imports' not in filled['cmpt']
    assert 'functions' not in filled['evt_grp']
    assert 'events' not in filled['evt_grp']
    assert 'component' not in filled
    assert 'event_group' not in filled

    # Snippet and event dicts keep their short serialization keys.
    snippet = SnippetAccumulator()
    snippet.add_comment('Load the feature.')
    snippet.add_statement('Return(feature)')
    assert snippet.to_dict() == {
        'coms': ['Load the feature.'],
        'stmt': ['Return(feature)'],
    }
    event = EventAccumulator(name='GetFeature', desc='Retrieve a feature.')
    event.add_attribute('feature_id', 'str')
    payload = event.to_dict()
    assert payload['name'] == 'GetFeature'
    assert set(payload) <= {
        'name',
        'desc',
        'attributes',
        'injections',
        'execute',
        'methods',
    }
    assert 'attributes' in payload

# ** test: transfer_next_chain
def test_transfer_next_chain():
    '''
    Test that .next exists only on the persistence transfer chains.
    '''

    # Parameters and statements persist as a chain, not a list.
    assert 'next' in ParamListTransferObject.model_fields
    assert 'next' in StatementTransferObject.model_fields
    params = TypeTransferObject.model_fields['params'].annotation
    code = DeclarationTransferObject.model_fields['code'].annotation
    assert params == ParamListTransferObject | None
    assert code == StatementTransferObject | None

    # Runtime lists keep their list shape and have no .next link.
    assert 'next' not in ParamList.model_fields
    assert 'next' not in Statement.model_fields
    assert Type.model_fields['params'].annotation == List[ParamList]

# ** test: findings_accumulate
def test_findings_accumulate():
    '''
    Test that conformance execute accumulates finding dicts.
    '''

    # Conformance steps share the findings data key.
    steps = []
    for feature in COMPILER_DEFAULT_FEATURES.values():
        steps.extend(feature.get('steps') or [])
    conformance = [
        step for step in steps
        if str(step.get('service_id', '')).startswith('check_')
        and str(step.get('service_id', '')).endswith('_conformance_event')
    ]
    assert conformance
    assert all(step.get('data_key') == 'findings' for step in conformance)

    # A disallowed group produces a finding without booting the pipeline.
    group = ArtifactStatementAggregate.new_artifact_stmt(
        ArtifactDeclarationAggregate.new_artifact_decl(
            name='events',
            artifact_type='***',
        ),
        [],
    )
    ast = DeclarationAggregate.new_module_decl(name='bad_domain', code=[group])
    cache = build_cache()
    semantic = {
        'symbol_table': SymbolTableBuilder(
            cache,
            COMPILER_PROVISION_CACHE_PREFIX,
        ).build(ast),
    }

    # The first call seeds the list. The second call prepends that list.
    event = CheckDomainConformance()
    first = event.execute(
        ast=ast,
        semantic=semantic,
        cache=cache,
        provision_prefix=COMPILER_PROVISION_CACHE_PREFIX,
        findings=None,
    )
    assert isinstance(first, list)
    second = event.execute(
        ast=ast,
        semantic=semantic,
        cache=cache,
        provision_prefix=COMPILER_PROVISION_CACHE_PREFIX,
        findings=first,
    )
    assert isinstance(second, list)
    assert len(second) >= len(first)
    assert all(
        isinstance(item, dict) and 'error_code' in item and 'message' in item
        for item in second
    )
