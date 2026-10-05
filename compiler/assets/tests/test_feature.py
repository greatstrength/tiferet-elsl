"""Compiler Default Feature Catalog Tests"""

# *** imports

# ** infra
from tiferet.domain.feature import Feature

# ** app
from ..app import COMPILER_DEFAULT_SERVICES
from ..feature import COMPILER_DEFAULT_FEATURES

# *** constants

# ** constant: feature_rows
_FEATURE_ROWS = (
    (
        'scan.module',
        'Scan Module',
        'scan',
        'module',
        'Tokenize a source file. This phase does not take a component type.',
    ),
    (
        'parse.module',
        'Parse Module',
        'parse',
        'module',
        'Parse a source file. This phase does not take a component type.',
    ),
    (
        'semantic.module',
        'Semantic Module',
        'semantic',
        'module',
        'Analyze a source file. Dialect checks are gated on the requested component type.',
    ),
    (
        'compile.module',
        'Compile Module',
        'compile',
        'module',
        'Compile a source file. Dialect checks are gated on the requested component type.',
    ),
    (
        'compile.ast',
        'Compile AST',
        'compile',
        'ast',
        'Compile a saved AST. Dialect checks are gated on the requested component type.',
    ),
)

# ** constant: gated_steps
_GATED_STEPS = (
    (
        'Check Event Conformance',
        'check_event_conformance_event',
        "$r.component == 'events'",
    ),
    (
        'Check Asset Conformance',
        'check_asset_conformance_event',
        "$r.component == 'assets'",
    ),
    (
        'Check Domain Conformance',
        'check_domain_conformance_event',
        "$r.component == 'domain'",
    ),
    (
        'Check Mapper Conformance',
        'check_mapper_conformance_event',
        "$r.component == 'mappers'",
    ),
    (
        'Check Interface Conformance',
        'check_interface_conformance_event',
        "$r.component == 'interfaces'",
    ),
    (
        'Check DI Conformance',
        'check_di_conformance_event',
        "$r.component == 'di'",
    ),
    (
        'Check Utils Conformance',
        'check_utils_conformance_event',
        "$r.component == 'utils'",
    ),
    (
        'Check Context Conformance',
        'check_context_conformance_event',
        "$r.component == 'contexts'",
    ),
    (
        'Check Blueprints Conformance',
        'check_blueprints_conformance_event',
        "$r.component == 'blueprints'",
    ),
    (
        'Check Repos Conformance',
        'check_repos_conformance_event',
        "$r.component == 'repos'",
    ),
)

# *** functions

# ** function: step
def step(name,
        service_id,
        data_key=None,
        condition=None,
        parameters=None):
    '''
    Build one expected feature step.

    :param name: The step name.
    :type name: str
    :param service_id: The step service id.
    :type service_id: str
    :param data_key: The optional data key.
    :type data_key: str
    :param condition: The optional gate.
    :type condition: str
    :param parameters: The optional parameter mapping.
    :type parameters: dict
    :return: The step dict.
    :rtype: dict
    '''

    # Absent keys stay absent. Do not fill them with None.
    built = {
        'name': name,
        'service_id': service_id,
    }
    if data_key is not None:
        built['data_key'] = data_key
    if condition is not None:
        built['condition'] = condition
    if parameters is not None:
        built['parameters'] = parameters

    # Return a fresh expected step.
    return built

# ** function: gated_steps
def gated_steps():
    '''
    Build the ten gated conformance steps.

    :return: The gated steps, in pipeline order.
    :rtype: list
    '''

    # Each gate stores findings and its own condition.
    return [
        step(name, service_id, data_key='findings', condition=condition)
        for name, service_id, condition in _GATED_STEPS
    ]

# ** function: expected_steps
def expected_steps():
    '''
    Build the five pipeline step lists.

    :return: Feature id to expected steps.
    :rtype: dict
    '''

    # Shared shapes are rebuilt here. They are not catalog objects.
    tokenize = step(
        'Tokenize',
        'perform_lexical_analysis_event',
        data_key='tokens',
    )
    emit_scan = step('Emit Scan Result', 'emit_scan_result_event')
    parse = step(
        'Parse',
        'perform_syntactic_analysis_event',
        data_key='ast',
    )
    emit_parse = step('Emit Parse Result', 'emit_parse_result_event')
    symbols = step(
        'Build Symbols',
        'perform_semantic_analysis_event',
        data_key='semantic',
    )
    common = step(
        'Check Common Conformance',
        'check_common_conformance_event',
        data_key='findings',
    )
    emit_semantic = step('Emit Semantic Result', 'emit_semantic_result_event')
    generate = step(
        'Generate Code',
        'generate_code_event',
        data_key='codegen',
        parameters={'codegen_service': 'codegen_service'},
    )
    optimize = step(
        'Optimize Code',
        'optimize_code_event',
        data_key='codegen',
        parameters={'optimizer_service': 'optimizer_service'},
    )
    emit_codegen = step('Emit Codegen Result', 'emit_codegen_result_event')
    load = step(
        'Load From AST',
        'load_from_ast_event',
        data_key='ast',
    )
    gated = gated_steps()

    # Counts are 2, 3, 15, 17, 16. compile.ast does not gain scan or parse.
    return {
        'scan.module': [
            tokenize,
            emit_scan,
        ],
        'parse.module': [
            tokenize,
            parse,
            emit_parse,
        ],
        'semantic.module': [
            tokenize,
            parse,
            symbols,
            common,
            *gated,
            emit_semantic,
        ],
        'compile.module': [
            tokenize,
            parse,
            symbols,
            common,
            *gated,
            generate,
            optimize,
            emit_codegen,
        ],
        'compile.ast': [
            load,
            symbols,
            common,
            *gated,
            generate,
            optimize,
            emit_codegen,
        ],
    }

# *** tests

# ** test: compiler_default_features_match_declared_rows
def test_compiler_default_features_match_declared_rows() -> None:
    '''
    Test that the feature catalog has the five declared pipelines.
    '''

    # Insertion order is the declared order.
    assert list(COMPILER_DEFAULT_FEATURES) == [key for key, *_rest in _FEATURE_ROWS]
    expected = expected_steps()
    assert [len(steps) for steps in expected.values()] == [2, 3, 15, 17, 16]

    # Each value omits id and params_schema. Steps store parameters, not params.
    for key, name, group_id, feature_key, description in _FEATURE_ROWS:
        value = COMPILER_DEFAULT_FEATURES[key]
        assert 'id' not in value
        assert 'params_schema' not in value
        assert set(value) == {
            'name',
            'group_id',
            'feature_key',
            'steps',
            'description',
        }
        assert value['name'] == name
        assert value['group_id'] == group_id
        assert value['feature_key'] == feature_key
        assert value['description'] == description
        assert value['steps'] == expected[key]
        assert all('params' not in step for step in value['steps'])

        # Reinjecting the key validates as a Feature.
        feature = Feature.model_validate({
            **value,
            'id': key,
        })
        assert feature.id == key
        assert len(feature.steps) == len(expected[key])

    # compile.ast does not gain a scan step or a parse step.
    ast_ids = [
        step['service_id']
        for step in COMPILER_DEFAULT_FEATURES['compile.ast']['steps']
    ]
    assert 'perform_lexical_analysis_event' not in ast_ids
    assert 'perform_syntactic_analysis_event' not in ast_ids

# ** test: feature_steps_are_not_shared
def test_feature_steps_are_not_shared() -> None:
    '''
    Test that expanding an anchor does not reuse a step object.
    '''

    # A later mutation of one pipeline must not change another.
    seen = []
    seen_parameters = []
    for feature in COMPILER_DEFAULT_FEATURES.values():
        for item in feature['steps']:
            assert all(item is not prior for prior in seen)
            seen.append(item)
            parameters = item.get('parameters')
            if parameters is None:
                continue
            assert all(parameters is not prior for prior in seen_parameters)
            seen_parameters.append(parameters)

# ** test: feature_step_service_ids_are_registered
def test_feature_step_service_ids_are_registered() -> None:
    '''
    Test that every feature step names a service catalog key.
    '''

    # Step service ids are literals. They still have to be employed services.
    for feature in COMPILER_DEFAULT_FEATURES.values():
        for item in feature['steps']:
            assert item['service_id'] in COMPILER_DEFAULT_SERVICES
