"""Tiferet Code Generator Utility Tests"""

# *** imports

# ** app
from ...mappers.artifact import (
    ArtifactDeclarationAggregate,
    ArtifactStatementAggregate,
    SnippetStatementAggregate,
)
from ...mappers.ast import (
    DeclarationAggregate,
    ExpressionAggregate,
    ParamListAggregate,
    StatementAggregate,
    TypeAggregate,
)
from ..codegen import GENERATOR_REWRITE_SET, TiferetGenerator

# *** functions

# ** function: module
def _module(name, code=None, doc_string=None):
    '''
    Create a module declaration.

    :param name: The module name.
    :type name: str
    :param code: The module statements, or None.
    :type code: list
    :param doc_string: The optional module docstring.
    :type doc_string: str
    :return: The module declaration.
    :rtype: DeclarationAggregate
    '''

    # The generator walks the module body as top-level groups.
    return DeclarationAggregate.new_module_decl(
        name=name,
        code=code,
        doc_string=doc_string,
    )

# ** function: group
def _group(name, body, qualifier=None):
    '''
    Create a tier-1 artifact group.

    :param name: The group name.
    :type name: str
    :param body: The group body.
    :type body: list
    :param qualifier: The optional parenthetical qualifier.
    :type qualifier: str
    :return: The artifact statement.
    :rtype: ArtifactStatementAggregate
    '''

    # A tier-1 header uses the triple-star marker.
    header = ArtifactDeclarationAggregate.new_artifact_decl(
        name=name,
        artifact_type='***',
        qualifier=qualifier,
    )
    return ArtifactStatementAggregate.new_artifact_stmt(header, body)

# ** function: section
def _section(name, artifact_type, body, qualifier=None):
    '''
    Create a tier-2 artifact section.

    :param name: The section name.
    :type name: str
    :param artifact_type: The section marker, including its keyword.
    :type artifact_type: str
    :param body: The section body.
    :type body: list
    :param qualifier: The optional parenthetical qualifier.
    :type qualifier: str
    :return: The artifact statement.
    :rtype: ArtifactStatementAggregate
    '''

    # The marker carries the section keyword. The name is the declared identifier.
    header = ArtifactDeclarationAggregate.new_artifact_decl(
        name=name,
        artifact_type=artifact_type,
        qualifier=qualifier,
    )
    return ArtifactStatementAggregate.new_artifact_stmt(header, body)

# ** function: decl
def _decl(decl):
    '''
    Wrap a declaration in a declaration statement.

    :param decl: The declaration.
    :type decl: DeclarationAggregate
    :return: The declaration statement.
    :rtype: StatementAggregate
    '''

    # Groups and members store declarations as declaration statements.
    return StatementAggregate.new_decl_stmt(decl)

# ** function: import_from
def _import_from(module, symbols):
    '''
    Create an import-from statement.

    :param module: The module path.
    :type module: str
    :param symbols: The imported symbol names, in source order.
    :type symbols: list
    :return: The import-from statement.
    :rtype: StatementAggregate
    '''

    # The first symbol is a name. Later symbols nest as a multi-import.
    expr = None
    for symbol in symbols:
        if expr is None:
            expr = ExpressionAggregate.new_name_expr(symbol)
        else:
            expr = ExpressionAggregate.new_import_expr_multi(expr, symbol)

    # The module path is the import-from target.
    return StatementAggregate.new_import_stmt_from(
        ExpressionAggregate.new_name_expr(module),
        expr,
    )

# ** function: class_decl
def _class_decl(name, members, doc_string=None, bases=None):
    '''
    Create a class declaration.

    :param name: The class name.
    :type name: str
    :param members: Member declaration statements.
    :type members: list
    :param doc_string: The optional class docstring.
    :type doc_string: str
    :param bases: Base class names, first base first.
    :type bases: list
    :return: The class declaration.
    :rtype: DeclarationAggregate
    '''

    # Chain bases so the first name is type.subtype.name.
    subclasses = None
    for base in reversed(bases or []):
        current = TypeAggregate.new_class_type(name=base)
        if subclasses is not None:
            current.set_subtype(subclasses)
        subclasses = current

    # Members are declaration statements, not bare declarations.
    return DeclarationAggregate.new_class_decl(
        name=name,
        subclasses=subclasses,
        doc_string=doc_string,
        members=members,
    )

# ** function: func
def _func(name, params=None, return_name=None, doc_string=None, body=None):
    '''
    Create a function declaration.

    :param name: The function name.
    :type name: str
    :param params: The parameters, or None.
    :type params: list
    :param return_name: The optional return type name.
    :type return_name: str
    :param doc_string: The optional docstring.
    :type doc_string: str
    :param body: The optional body statements.
    :type body: list
    :return: The function declaration.
    :rtype: DeclarationAggregate
    '''

    # A named return type is a class type so its display name is that name.
    return_type = None
    if return_name is not None:
        return_type = TypeAggregate.new_class_type(name=return_name)

    # The function type is what marks the declaration as a function.
    return DeclarationAggregate.new_func_decl(
        name=name,
        type=TypeAggregate.new_func_type(
            params=params or [],
            return_type=return_type,
        ),
        doc_string=doc_string,
        body=body or [],
    )

# ** function: member
def _member(role, inner, qualifier=None, decorators=None):
    '''
    Wrap an inner declaration as an artifact member statement.

    :param role: The member role.
    :type role: str
    :param inner: The inner declaration.
    :type inner: DeclarationAggregate
    :param qualifier: The optional parenthetical qualifier.
    :type qualifier: str
    :param decorators: Optional decorator names that precede the inner declaration.
    :type decorators: list
    :return: The member declaration statement.
    :rtype: StatementAggregate
    '''

    # Decorators are expression statements before the inner declaration.
    body = []
    for name in decorators or []:
        body.append(StatementAggregate.new_expr_stmt(
            ExpressionAggregate.new_name_expr(name),
        ))
    body.append(_decl(inner))

    # The role is both the member name and the artifact role.
    return _decl(ArtifactDeclarationAggregate.new_member_decl(
        role,
        member_body=body,
        qualifier=qualifier,
    ))

# ** function: snippet
def _snippet(comment, statement):
    '''
    Create a snippet with one comment and one statement.

    :param comment: The comment text, including its hash marker.
    :type comment: str
    :param statement: The executable statement.
    :type statement: StatementAggregate
    :return: The snippet statement.
    :rtype: SnippetStatementAggregate
    '''

    # Comments stay off the executable body.
    return SnippetStatementAggregate.new_snippet_stmt(
        comments=StatementAggregate.new_comment_stmt(
            ExpressionAggregate.new_comment_expr(comment),
        ),
        code=statement,
    )

# ** function: event_module
def _event_module(class_name='GetFeature', section_name='get_feature',
        doc_string=None, class_doc=None, bases=None, members=None):
    '''
    Create a module with one event section.

    :param class_name: The class name.
    :type class_name: str
    :param section_name: The event section name.
    :type section_name: str
    :param doc_string: The optional module docstring.
    :type doc_string: str
    :param class_doc: The optional class docstring.
    :type class_doc: str
    :param bases: Optional base class names.
    :type bases: list
    :param members: Optional member statements.
    :type members: list
    :return: The module declaration.
    :rtype: DeclarationAggregate
    '''

    # Default to a class with no members when the caller does not supply any.
    class_decl = _class_decl(
        class_name,
        members or [],
        doc_string=class_doc,
        bases=bases,
    )
    section = _section(section_name, '** event', [_decl(class_decl)])
    return _module(
        'feature',
        code=[_group('events', [section])],
        doc_string=doc_string,
    )

# ** function: result_event
def result_event(module):
    '''
    Generate a module and return its single event payload.

    :param module: The module declaration.
    :type module: DeclarationAggregate
    :return: The event payload keyed by get_feature.
    :rtype: dict
    '''

    # Tests that build _event_module share this lookup.
    result = TiferetGenerator().generate(module)
    return result['evt_grp']['evts']['get_feature']

# *** tests

# ** test: generate_returns_cmpt_envelope
def test_generate_returns_cmpt_envelope():
    '''
    Test that generate returns a component envelope with name and kind.
    '''

    # An empty named module still has an envelope.
    result = TiferetGenerator().generate(_module('feature'))

    # The envelope root is cmpt, and it always carries name and kind.
    assert result['cmpt']['name'] == 'feature'
    assert result['cmpt']['kind'] == 'events'
    assert 'evt_grp' not in result['cmpt']

# ** test: generate_events_dual_emission
def test_generate_events_dual_emission():
    '''
    Test that kind events dual-emits cmpt and evt_grp.
    '''

    # One event section gives the legacy map something to carry.
    result = TiferetGenerator().generate(
        _event_module(),
        kind='events',
    )

    # Both documents are present. The legacy map has the module name and events.
    assert 'cmpt' in result
    assert result['evt_grp']['name'] == 'feature'
    assert 'get_feature' in result['evt_grp']['evts']

# ** test: generate_assets_kind_omits_evt_grp
def test_generate_assets_kind_omits_evt_grp():
    '''
    Test that a non-events kind omits the legacy event group.
    '''

    # Assets is a component type, not an event document.
    result = TiferetGenerator().generate(_module('ids'), kind='assets')

    # The requested kind is recorded, and evt_grp is absent.
    assert result['cmpt']['kind'] == 'assets'
    assert 'evt_grp' not in result

# ** test: generate_module_docstring_becomes_cmpt_desc
def test_generate_module_docstring_becomes_cmpt_desc():
    '''
    Test that a stripped module docstring becomes cmpt and evt_grp desc.
    '''

    # Triple quotes are stripped before the summary is stored.
    documented = TiferetGenerator().generate(_module(
        'feature',
        doc_string='"""Feature events."""',
    ))
    assert documented['cmpt']['desc'] == 'Feature events.'
    assert documented['evt_grp']['desc'] == 'Feature events.'

    # A missing docstring omits desc rather than storing an empty string.
    bare = TiferetGenerator().generate(_module('feature'))
    assert 'desc' not in bare['cmpt']
    assert 'desc' not in bare['evt_grp']

# ** test: generate_class_docstring_becomes_event_desc
def test_generate_class_docstring_becomes_event_desc():
    '''
    Test that a stripped class docstring becomes the event payload desc.
    '''

    # The event key is the section name. The payload name is the class name.
    result = TiferetGenerator().generate(_event_module(
        class_doc='"""Retrieve a feature by identifier."""',
    ))
    event = result['evt_grp']['evts']['get_feature']

    # Strip removes the delimiters. The class name stays on the payload.
    assert event['desc'] == 'Retrieve a feature by identifier.'
    assert event['name'] == 'GetFeature'

# ** test: generate_function_docstring_becomes_fnc_desc
def test_generate_function_docstring_becomes_fnc_desc():
    '''
    Test that a stripped function docstring becomes fncs[name].desc.
    '''

    # A function section carries the callable and its docstring.
    func = _func(
        'build_app',
        doc_string='"""Build the application."""',
    )
    section = _section('build_app', '** function', [_decl(func)])
    module = _module('app', code=[_group('functions', [section])])

    # The summary is on the function payload, keyed by the function name.
    result = TiferetGenerator().generate(module)
    assert result['evt_grp']['fncs']['build_app']['desc'] == 'Build the application.'

# ** test: generate_execute_has_no_desc_key
def test_generate_execute_has_no_desc_key():
    '''
    Test that an execute payload has no desc even when the method has a docstring.
    '''

    # The execute docstring has a summary and a return field.
    execute = _func(
        'execute',
        params=[ParamListAggregate.new('self')],
        return_name='Feature',
        doc_string='"""Run the event.\n\n:return: The feature.\n"""',
        body=[_snippet(
            '# Return the feature.',
            StatementAggregate.new_return_stmt(
                ExpressionAggregate.new_name_expr('feature'),
            ),
        )],
    )
    module = _event_module(members=[_member('method', execute)])

    # The summary stays off execute. The return spec may still be present.
    execute_payload = result_event(module)['execute']
    assert 'desc' not in execute_payload
    assert execute_payload['returns'] == ['Feature:The feature.']

# ** test: generate_minimal_event_imports
def test_generate_minimal_event_imports():
    '''
    Test that imports collapse by module path under core, infra, and app.
    '''

    # Two symbols from one module collapse. Each category is its own section.
    imports = _group('imports', [
        _section('core', '**', [
            _import_from('typing', ['Any', 'Dict']),
        ]),
        _section('infra', '**', [
            _import_from('tiferet', ['Service']),
        ]),
        _section('app', '**', [
            _import_from('..domain', ['Feature']),
        ]),
    ])
    result = TiferetGenerator().generate(_module('feature', code=[imports]))

    # Categories keep source order and collapsed targets.
    assert result['cmpt']['impt'] == {
        'core': [{'src': 'typing', 'tgts': ['Any', 'Dict']}],
        'infra': [{'src': 'tiferet', 'tgts': ['Service']}],
        'app': [{'src': '..domain', 'tgts': ['Feature']}],
    }

# ** test: generate_minimal_event_event_structure
def test_generate_minimal_event_event_structure():
    '''
    Test that an event carries name, attributes, injections, and execute sections.
    '''

    # Attribute, init, and execute members cover the roles the generator dispatches.
    attribute = DeclarationAggregate.new_attr_decl(
        name='feature_id',
        types=TypeAggregate.new_class_type(name='str'),
        value=ExpressionAggregate.new_name_or_literal_expr('missing'),
    )
    init = _func(
        '__init__',
        params=[
            ParamListAggregate.new('self'),
            ParamListAggregate.new(
                'feature_service',
                type=TypeAggregate.new_class_type(name='FeatureService'),
                required=True,
            ),
        ],
        doc_string='"""Initialize the event.\n\n:param feature_service: The feature service.\n"""',
    )
    execute = _func(
        'execute',
        params=[
            ParamListAggregate.new('self'),
            ParamListAggregate.new(
                'id',
                type=TypeAggregate.new_class_type(name='str'),
                required=True,
            ),
        ],
        return_name='Feature',
        doc_string='"""Run the event.\n\n:param id: The feature id.\n:return: The feature.\n"""',
        body=[_snippet(
            '# Load the feature.',
            StatementAggregate.new_return_stmt(
                ExpressionAggregate.new_name_expr('feature'),
            ),
        )],
    )
    module = _event_module(members=[
        _member('attribute', attribute),
        _member('init', init),
        _member('method', execute),
    ])

    # The payload name is the class. Members match their roles.
    event = result_event(module)
    assert event['name'] == 'GetFeature'
    assert event['attributes'] == [{
        'feature_id': {'type': 'str', 'init': 'missing'},
    }]
    assert event['injections'] == [{
        'feature_service:FeatureService:true::The feature service.': {
            'assign': [{'target': 'feature_service', 'value': 'feature_service'}],
        },
    }]
    assert event['execute']['params'] == ['id:str:true::The feature id.']
    assert event['execute']['returns'] == ['Feature:The feature.']
    assert event['execute']['snpt'] == [{
        'coms': ['Load the feature.'],
        'stmt': ['Return(feature)'],
    }]

# ** test: generate_event_without_base_omits_base
def test_generate_event_without_base_omits_base():
    '''
    Test that a class with no base has no base key.
    '''

    # An event class with no bases, and a classes-group class with no bases.
    event = result_event(_event_module())
    class_decl = _class_decl('Bare', [])
    section = _section('bare', '** class', [_decl(class_decl)])
    classes = TiferetGenerator().generate(_module(
        'models',
        code=[_group('classes', [section])],
    ))

    # Neither payload invents a base key.
    assert 'base' not in event
    assert 'base' not in classes['cmpt']['grps'][0]['clss']['Bare']

# ** test: generate_empty_module
def test_generate_empty_module():
    '''
    Test that an empty module still returns a component envelope.
    '''

    # No groups, no docstring, and an explicit name.
    result = TiferetGenerator().generate(_module('empty', code=[]))

    # The envelope is present even when nothing was walked.
    assert result['cmpt'] == {'name': 'empty', 'kind': 'events'}

# ** test: generate_functions_under_fncs
def test_generate_functions_under_fncs():
    '''
    Test that a functions group appears under grps.fncs, not under evts.
    '''

    # One function section is enough to prove the group shape.
    func = _func('build_app', params=[ParamListAggregate.new('name')])
    section = _section('build_app', '** function', [_decl(func)])
    result = TiferetGenerator().generate(_module(
        'app',
        code=[_group('functions', [section])],
    ))

    # The group entry is functions and carries fncs. Events were not invented.
    group = result['cmpt']['grps'][0]
    assert group['name'] == 'functions'
    assert 'build_app' in group['fncs']
    assert 'evts' not in group
    assert 'evts' not in result['evt_grp']

# ** test: functions_not_emitted_under_evts
def test_functions_not_emitted_under_evts():
    '''
    Test that function names are absent from evts.
    '''

    # A function group and an event group share one module.
    func = _func('build_app')
    function_group = _group('functions', [
        _section('build_app', '** function', [_decl(func)]),
    ])
    event_group = _event_module().code[0]
    result = TiferetGenerator().generate(_module(
        'app',
        code=[function_group, event_group],
    ))

    # The function name is a function, not an event key.
    assert 'build_app' not in result['evt_grp']['evts']
    assert 'build_app' in result['evt_grp']['fncs']

# ** test: blueprints_group_reuses_free_function_payload
def test_blueprints_group_reuses_free_function_payload():
    '''
    Test that a blueprints group is named blueprints and carries fncs callables.
    '''

    # A blueprint section uses the function-section marker.
    func = _func(
        'build_app',
        params=[ParamListAggregate.new(
            'name',
            type=TypeAggregate.new_class_type(name='str'),
        )],
        return_name='App',
    )
    section = _section('build_app', '** blueprint', [_decl(func)])
    result = TiferetGenerator().generate(_module(
        'app',
        code=[_group('blueprints', [section])],
    ))

    # The group name is blueprints. The payload is the callable shape.
    group = result['cmpt']['grps'][0]
    assert group['name'] == 'blueprints'
    assert group['fncs']['build_app']['params'] == ['name:str:true::']
    assert group['fncs']['build_app']['returns'] == ['App:']

# ** test: generate_constants_group
def test_generate_constants_group():
    '''
    Test that constants are keyed by assignment target with an encoded value.
    '''

    # The section name is not the constant key. The assignment target is.
    const = DeclarationAggregate.new_attr_decl(
        name='FEATURE_NOT_FOUND_ID',
        value=ExpressionAggregate.new_name_or_literal_expr('FEATURE_NOT_FOUND'),
    )
    section = _section(
        'feature_not_found_id',
        '** constant',
        [_decl(const)],
        qualifier='ids',
    )
    result = TiferetGenerator().generate(_module(
        'ids',
        code=[_group('constants', [section], qualifier='ids')],
    ), kind='assets')

    # The group carries csts. Assets does not dual-emit evt_grp.
    group = result['cmpt']['grps'][0]
    assert group['name'] == 'constants'
    assert group['qual'] == 'ids'
    assert group['csts'] == {
        'FEATURE_NOT_FOUND_ID': {'value': 'FEATURE_NOT_FOUND'},
    }
    assert 'evt_grp' not in result

# ** test: generator_rewrite_set_order
def test_generator_rewrite_set_order():
    '''
    Test that the published rewrite set matches dispatch order and ids.
    '''

    # Zero-arg construction uses the published set.
    generator = TiferetGenerator()
    assert generator.rewrites is GENERATOR_REWRITE_SET
    assert [(rewrite.id, rewrite.applies_to) for rewrite in GENERATOR_REWRITE_SET] == [
        ('generator.imports_group', 'imports'),
        ('generator.functions_group', 'functions'),
        ('generator.blueprints_group', 'blueprints'),
        ('generator.constants_group', 'constants'),
        ('generator.classes_group', 'classes'),
        ('generator.models_group', 'models'),
        ('generator.mappers_group', 'mappers'),
        ('generator.interfaces_group', 'interfaces'),
        ('generator.utils_group', 'utils'),
        ('generator.contexts_group', 'contexts'),
        ('generator.repos_group', 'repos'),
        ('generator.events_group', 'events'),
        ('generator.attribute_member', 'attribute'),
        ('generator.init_member', 'init'),
        ('generator.execute_member', 'execute'),
        ('generator.method_member', 'method'),
    ]

    # Unknown groups dispatch as events. The exports skip is a generate concern.
    assert generator.resolve_group_hook('widgets') == 'events'

# ** test: generate_skips_exports_group
def test_generate_skips_exports_group():
    '''
    Test that generate skips an exports group before it can be emitted as events.
    '''

    # An exports section would become an event if the skip were removed.
    exported = _class_decl('Public', [])
    exports = _group('exports', [
        _section('public', '** event', [_decl(exported)]),
    ])
    events = _event_module().code[0]
    result = TiferetGenerator().generate(_module(
        'feature',
        code=[exports, events],
    ))

    # Exports is absent from both the component groups and the legacy event map.
    groups = result['cmpt'].get('grps', [])
    assert 'exports' not in [group['name'] for group in groups]
    assert 'public' not in result['evt_grp'].get('evts', {})
    assert 'get_feature' in result['evt_grp']['evts']
