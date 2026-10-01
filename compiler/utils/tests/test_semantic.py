"""Compiler Semantic Analysis Utility Tests"""

# *** imports

# ** core
import inspect

# ** infra
import pytest

# ** app
from ...domain.ast import TypeKind
from ...domain.semantic import (
    SYMBOL_KIND_ATTRIBUTE,
    SYMBOL_KIND_CLASS_DEF,
    SYMBOL_KIND_IMPORT,
    SYMBOL_KIND_METHOD,
    SYMBOL_KIND_PARAMETER,
)
from ...mappers.ast import (
    DeclarationAggregate,
    ExpressionAggregate,
    ParamListAggregate,
    StatementAggregate,
    TypeAggregate,
)
from ..core import StatementWalker
from ..semantic import (
    BUILDER_PRODUCTION_SET,
    RESOLVER_PRODUCTION_SET,
    NameResolver,
    SymbolTableBuilder,
)

# *** functions

# ** function: _name
def _name(name: str) -> ExpressionAggregate:
    '''
    Create a name expression.

    :param name: The name.
    :type name: str
    :return: The name expression.
    :rtype: ExpressionAggregate
    '''

    # Build a bare name reference.
    return ExpressionAggregate.new_name_expr(name)

# ** function: _import_names
def _import_names(names: list) -> ExpressionAggregate:
    '''
    Create an import-name expression for one or more names.

    :param names: The imported names, in order.
    :type names: list
    :return: The import expression.
    :rtype: ExpressionAggregate
    '''

    # The first name is a name expression. Later names extend a multi-import.
    expr = ExpressionAggregate.new_name_expr(names[0])
    for name in names[1:]:
        expr = ExpressionAggregate.new_import_expr_multi(expr, name)
    return expr

# ** function: _func
def _func(name: str, params: list, body: list,
          return_kind: TypeKind = None) -> DeclarationAggregate:
    '''
    Create a function declaration.

    :param name: The function name.
    :type name: str
    :param params: The parameters.
    :type params: list
    :param body: The body statements.
    :type body: list
    :param return_kind: The optional return-type kind.
    :type return_kind: TypeKind
    :return: The function declaration.
    :rtype: DeclarationAggregate
    '''

    # A missing return kind leaves the return type unset.
    return_type = None
    if return_kind is not None:
        return_type = TypeAggregate.new(kind=return_kind)

    # The function type is what marks the declaration as a function.
    return DeclarationAggregate.new_func_decl(
        name=name,
        type=TypeAggregate.new_func_type(
            params=params,
            return_type=return_type,
        ),
        body=body,
    )

# ** function: _class
def _class(name: str, members: list,
           base: str = None) -> DeclarationAggregate:
    '''
    Create a class declaration.

    :param name: The class name.
    :type name: str
    :param members: The body statements.
    :type members: list
    :param base: The optional base class name.
    :type base: str
    :return: The class declaration.
    :rtype: DeclarationAggregate
    '''

    # A base name is stored as the class type's subtype.
    subclasses = None
    if base is not None:
        subclasses = TypeAggregate.new_class_type(name=base)

    # Members are the class body. An empty body would not open a scope.
    return DeclarationAggregate.new_class_decl(
        name=name,
        subclasses=subclasses,
        doc_string=None,
        members=members,
    )

# ** function: _module
def _module(name: str, code: list) -> DeclarationAggregate:
    '''
    Create a module declaration.

    :param name: The module name.
    :type name: str
    :param code: The module statements.
    :type code: list
    :return: The module declaration.
    :rtype: DeclarationAggregate
    '''

    # The module body is the statement list the walkers start from.
    return DeclarationAggregate.new_module_decl(name=name, code=code)

# ** function: _decl
def _decl(decl: DeclarationAggregate) -> StatementAggregate:
    '''
    Wrap a declaration in a declaration statement.

    :param decl: The declaration.
    :type decl: DeclarationAggregate
    :return: The declaration statement.
    :rtype: StatementAggregate
    '''

    # Walkers dispatch declaration statements, not bare declarations.
    return StatementAggregate.new_decl_stmt(decl)

# ** function: _assign_self
def _assign_self(attr: str, value: str) -> StatementAggregate:
    '''
    Create a ``self.X = name`` expression statement.

    :param attr: The attribute name, without the ``self.`` prefix.
    :type attr: str
    :param value: The assigned name.
    :type value: str
    :return: The expression statement.
    :rtype: StatementAggregate
    '''

    # The target is a self attribute so the builder can register it.
    return StatementAggregate.new_expr_stmt(ExpressionAggregate.new_assign_expr(
        target=_name(f'self.{attr}'),
        value=_name(value),
    ))

# ** function: _resolve
def _resolve(module: DeclarationAggregate):
    '''
    Build a module, then resolve it against the live scope registry.

    :param module: The module declaration.
    :type module: DeclarationAggregate
    :return: The build dict and the resolution result.
    :rtype: tuple
    '''

    # The resolver needs the live aggregates, not the dumped build dict.
    builder = SymbolTableBuilder()
    built = builder.build(module)
    resolved = NameResolver(builder.scopes).resolve(module)
    return built, resolved

# *** fixtures

# ** fixture: imports_only_module
@pytest.fixture
def imports_only_module() -> DeclarationAggregate:
    '''
    Fixture for a module whose body is only imports.

    :return: A module with an import-from and a plain import.
    :rtype: DeclarationAggregate
    '''

    # import-from carries a source module. A plain import does not.
    return _module('events', [
        StatementAggregate.new_import_stmt_from(
            from_expr=_name('.settings'),
            import_expr=_import_names(['DomainEvent', 'ErrorMessage']),
        ),
        StatementAggregate.new_import_stmt(
            import_expr=_name('os'),
        ),
    ])

# ** fixture: minimal_event_module
@pytest.fixture
def minimal_event_module() -> DeclarationAggregate:
    '''
    Fixture for a class that subclasses an imported name and uses one unknown name.

    :return: A module with one event class.
    :rtype: DeclarationAggregate
    '''

    # DomainEvent is imported. MissingName is not defined anywhere.
    execute = _func(
        name='execute',
        params=[
            ParamListAggregate.new(name='self'),
            ParamListAggregate.new(
                name='id',
                type=TypeAggregate.new(kind=TypeKind.STR),
            ),
        ],
        body=[
            StatementAggregate.new_return_stmt(return_expr=_name('DomainEvent')),
            StatementAggregate.new_return_stmt(return_expr=_name('MissingName')),
        ],
        return_kind=TypeKind.NONE,
    )
    return _module('events', [
        StatementAggregate.new_import_stmt_from(
            from_expr=_name('.settings'),
            import_expr=_name('DomainEvent'),
        ),
        _decl(_class('Ping', [_decl(execute)], base='DomainEvent')),
    ])

# ** fixture: injection_event_module
@pytest.fixture
def injection_event_module() -> DeclarationAggregate:
    '''
    Fixture for a constructor that assigns and then reads ``self.service``.

    :return: A module with one injection class.
    :rtype: DeclarationAggregate
    '''

    # The assignment registers the attribute. The return is the lookup.
    init = _func(
        name='__init__',
        params=[
            ParamListAggregate.new(name='self'),
            ParamListAggregate.new(name='service'),
        ],
        body=[
            _assign_self('service', 'service'),
            StatementAggregate.new_return_stmt(return_expr=_name('self.service')),
        ],
    )
    return _module('events', [
        _decl(_class('Inject', [_decl(init)])),
    ])

# ** fixture: multiple_operator_module
@pytest.fixture
def multiple_operator_module() -> DeclarationAggregate:
    '''
    Fixture for two classes whose methods use different parameter names.

    :return: A module with Add and Sub.
    :rtype: DeclarationAggregate
    '''

    # Each parameter is local to its own method scope.
    add = _func(
        name='execute',
        params=[ParamListAggregate.new(name='left')],
        body=[StatementAggregate.new_return_stmt(return_expr=_name('left'))],
    )
    sub = _func(
        name='execute',
        params=[ParamListAggregate.new(name='right')],
        body=[StatementAggregate.new_return_stmt(return_expr=_name('right'))],
    )
    return _module('events', [
        _decl(_class('Add', [_decl(add)])),
        _decl(_class('Sub', [_decl(sub)])),
    ])

# ** fixture: module_level_function_module
@pytest.fixture
def module_level_function_module() -> DeclarationAggregate:
    '''
    Fixture for a module-level function that uses a parameter, an import, and an unknown name.

    :return: A module with one function.
    :rtype: DeclarationAggregate
    '''

    # value is local. Any is imported. missing is not defined.
    helper = _func(
        name='helper',
        params=[ParamListAggregate.new(name='value')],
        body=[
            StatementAggregate.new_return_stmt(return_expr=_name('value')),
            StatementAggregate.new_return_stmt(return_expr=_name('Any')),
            StatementAggregate.new_return_stmt(return_expr=_name('missing')),
        ],
    )
    return _module('events', [
        StatementAggregate.new_import_stmt_from(
            from_expr=_name('typing'),
            import_expr=_name('Any'),
        ),
        _decl(helper),
    ])

# *** tests

# ** test: build_imports_only
def test_build_imports_only(imports_only_module: DeclarationAggregate) -> None:
    '''
    Test that an imports-only module registers import-from names with a source module.

    :param imports_only_module: A module whose body is only imports.
    :type imports_only_module: DeclarationAggregate
    '''

    # Build the module scope and read the registered imports.
    result = SymbolTableBuilder().build(imports_only_module)
    symbols = result['scopes']['module']['symbols']

    # The root path is the module scope the factory assigns.
    assert result['module_name'] == 'events'
    assert result['root_scope_path'] == 'module'
    assert 'module' in result['scopes']

    # import-from names keep the from-clause as their source module.
    assert symbols['DomainEvent']['kind'] == SYMBOL_KIND_IMPORT
    assert symbols['DomainEvent']['source_module'] == '.settings'
    assert symbols['ErrorMessage']['kind'] == SYMBOL_KIND_IMPORT
    assert symbols['ErrorMessage']['source_module'] == '.settings'

    # A plain import is an import symbol without a source module.
    assert symbols['os']['kind'] == SYMBOL_KIND_IMPORT
    assert 'source_module' not in symbols['os']

# ** test: build_minimal_event
def test_build_minimal_event(minimal_event_module: DeclarationAggregate) -> None:
    '''
    Test that a class opens a class scope and its method registers parameters.

    :param minimal_event_module: A module with one event class.
    :type minimal_event_module: DeclarationAggregate
    '''

    # Build the class, method, and parameter scopes.
    result = SymbolTableBuilder().build(minimal_event_module)
    module_symbols = result['scopes']['module']['symbols']
    class_symbols = result['scopes']['module.Ping']['symbols']
    method_symbols = result['scopes']['module.Ping.execute']['symbols']

    # The class is a class definition in the module scope, with a child scope.
    assert module_symbols['Ping']['kind'] == SYMBOL_KIND_CLASS_DEF
    assert module_symbols['Ping']['type_annotation'] == 'DomainEvent'
    assert result['scopes']['module']['children']['Ping'] == 'module.Ping'

    # execute is a method of the class and opens a method scope.
    assert class_symbols['execute']['kind'] == SYMBOL_KIND_METHOD
    assert result['scopes']['module.Ping']['children']['execute'] == 'module.Ping.execute'

    # Parameters are recorded in the method scope, including their type kind.
    assert method_symbols['self']['kind'] == SYMBOL_KIND_PARAMETER
    assert method_symbols['id']['kind'] == SYMBOL_KIND_PARAMETER
    assert method_symbols['id']['type_annotation'] == 'str'

# ** test: build_minimal_injection_event
def test_build_minimal_injection_event(
        injection_event_module: DeclarationAggregate) -> None:
    '''
    Test that an undeclared ``self.X = ...`` registers an attribute on the class.

    :param injection_event_module: A module with one injection class.
    :type injection_event_module: DeclarationAggregate
    '''

    # Build the constructor assignment.
    result = SymbolTableBuilder().build(injection_event_module)
    class_symbols = result['scopes']['module.Inject']['symbols']
    method_symbols = result['scopes']['module.Inject.__init__']['symbols']

    # The attribute lands on the class, not as a second method-scope attribute.
    assert class_symbols['service']['kind'] == SYMBOL_KIND_ATTRIBUTE
    assert method_symbols['service']['kind'] == SYMBOL_KIND_PARAMETER
    assert 'service' not in result['scopes']['module.Inject.__init__'].get(
        'children',
        {},
    )

# ** test: build_multiple_operator_events
def test_build_multiple_operator_events(
        multiple_operator_module: DeclarationAggregate) -> None:
    '''
    Test that each class declaration opens its own child scope under the module.

    :param multiple_operator_module: A module with Add and Sub.
    :type multiple_operator_module: DeclarationAggregate
    '''

    # Build both class scopes.
    result = SymbolTableBuilder().build(multiple_operator_module)
    children = result['scopes']['module']['children']

    # Each class is a child of the module and a class definition there.
    assert children['Add'] == 'module.Add'
    assert children['Sub'] == 'module.Sub'
    assert result['scopes']['module']['symbols']['Add']['kind'] == SYMBOL_KIND_CLASS_DEF
    assert result['scopes']['module']['symbols']['Sub']['kind'] == SYMBOL_KIND_CLASS_DEF
    assert 'module.Add' in result['scopes']
    assert 'module.Sub' in result['scopes']

# ** test: build_module_level_function
def test_build_module_level_function(
        module_level_function_module: DeclarationAggregate) -> None:
    '''
    Test that a module-level function registers a method and opens a method scope.

    :param module_level_function_module: A module with one function.
    :type module_level_function_module: DeclarationAggregate
    '''

    # Build the function on the module scope.
    result = SymbolTableBuilder().build(module_level_function_module)

    # The function is a method symbol and a child method scope.
    assert result['scopes']['module']['symbols']['helper']['kind'] == SYMBOL_KIND_METHOD
    assert result['scopes']['module']['children']['helper'] == 'module.helper'
    assert result['scopes']['module.helper']['kind'] == SYMBOL_KIND_METHOD

# ** test: resolve_minimal_event
def test_resolve_minimal_event(minimal_event_module: DeclarationAggregate) -> None:
    '''
    Test that an imported name used in a class resolves and an unknown name does not.

    :param minimal_event_module: A module with one event class.
    :type minimal_event_module: DeclarationAggregate
    '''

    # Resolve after the builder has registered the import.
    _, result = _resolve(minimal_event_module)
    domain_event = [row for row in result.resolved if row.name == 'DomainEvent']
    missing = [row for row in result.unresolved if row.name == 'MissingName']

    # Every use of the import resolves to the module. The unknown name does not.
    assert domain_event
    assert all(row.resolved_to == 'module' for row in domain_event)
    assert missing
    assert missing[0].scope_path == 'module.Ping.execute'

# ** test: resolve_injection_event
def test_resolve_injection_event(
        injection_event_module: DeclarationAggregate) -> None:
    '''
    Test that ``self.X`` resolves against the class scope.

    :param injection_event_module: A module with one injection class.
    :type injection_event_module: DeclarationAggregate
    '''

    # Resolve the read of the attribute the constructor registered.
    _, result = _resolve(injection_event_module)
    matches = [row for row in result.resolved if row.name == 'self.service']

    # The binding is the class scope, recorded from the method that used it.
    assert len(matches) == 1
    assert matches[0].resolved_to == 'module.Inject'
    assert matches[0].scope_path == 'module.Inject.__init__'

# ** test: resolve_multiple_operators
def test_resolve_multiple_operators(
        multiple_operator_module: DeclarationAggregate) -> None:
    '''
    Test that each class resolves its names in its own method scope.

    :param multiple_operator_module: A module with Add and Sub.
    :type multiple_operator_module: DeclarationAggregate
    '''

    # Resolve both method bodies.
    _, result = _resolve(multiple_operator_module)
    left = [row for row in result.resolved if row.name == 'left']
    right = [row for row in result.resolved if row.name == 'right']

    # The names do not leak across the two class scopes.
    assert len(left) == 1
    assert left[0].resolved_to == 'module.Add.execute'
    assert left[0].scope_path == 'module.Add.execute'
    assert len(right) == 1
    assert right[0].resolved_to == 'module.Sub.execute'
    assert right[0].scope_path == 'module.Sub.execute'

# ** test: resolve_module_level_function
def test_resolve_module_level_function(
        module_level_function_module: DeclarationAggregate) -> None:
    '''
    Test that names in a module-level function resolve from the method scope outward.

    :param module_level_function_module: A module with one function.
    :type module_level_function_module: DeclarationAggregate
    '''

    # Resolve the parameter, the import, and the unknown name.
    _, result = _resolve(module_level_function_module)
    value = [row for row in result.resolved if row.name == 'value']
    any_name = [row for row in result.resolved if row.name == 'Any']
    missing = [row for row in result.unresolved if row.name == 'missing']

    # The parameter binds in the method. The import binds in the module.
    assert len(value) == 1
    assert value[0].resolved_to == 'module.helper'
    assert value[0].scope_path == 'module.helper'
    assert len(any_name) == 1
    assert any_name[0].resolved_to == 'module'
    assert any_name[0].scope_path == 'module.helper'
    assert len(missing) == 1
    assert missing[0].scope_path == 'module.helper'

# ** test: self_is_skipped
def test_self_is_skipped() -> None:
    '''
    Test that bare self is not recorded as resolved or unresolved.
    '''

    # The only name use is bare self, which is also a parameter.
    module = _module('events', [
        _decl(_class('Ping', [
            _decl(_func(
                name='execute',
                params=[ParamListAggregate.new(name='self')],
                body=[StatementAggregate.new_expr_stmt(_name('self'))],
            )),
        ])),
    ])

    # Bare self is skipped even though the parameter would otherwise resolve.
    _, result = _resolve(module)
    names = [row.name for row in result.resolved] + [
        row.name for row in result.unresolved
    ]
    assert 'self' not in names
    assert result.resolved == []
    assert result.unresolved == []

# ** test: comments_skipped
def test_comments_skipped() -> None:
    '''
    Test that a comment expression is not resolved.
    '''

    # A comment sits beside a real imported name so the walk is not empty.
    module = _module('events', [
        StatementAggregate.new_import_stmt_from(
            from_expr=_name('.settings'),
            import_expr=_name('DomainEvent'),
        ),
        _decl(_func(
            name='helper',
            params=[],
            body=[
                StatementAggregate.new_expr_stmt(
                    ExpressionAggregate.new_comment_expr('keep me out'),
                ),
                StatementAggregate.new_return_stmt(return_expr=_name('DomainEvent')),
            ],
        )),
    ])

    # The comment text is absent. The imported name still resolves.
    _, result = _resolve(module)
    names = [row.name for row in result.resolved] + [
        row.name for row in result.unresolved
    ]
    assert 'keep me out' not in names
    assert names == ['DomainEvent']

# ** test: builder_uses_apply_attachments
def test_builder_uses_apply_attachments(monkeypatch) -> None:
    '''
    Test that SymbolTableBuilder.apply calls StatementWalker.apply_attachments.

    :param monkeypatch: The pytest monkeypatch fixture.
    :type monkeypatch: object
    '''

    # The host does not copy the attaches_to loop.
    source = inspect.getsource(SymbolTableBuilder.apply)
    assert 'apply_attachments' in source
    assert 'attaches_to' not in source
    assert SymbolTableBuilder.apply_attachments is StatementWalker.apply_attachments

    # The default set is the builder production set, in TRD order.
    builder = SymbolTableBuilder()
    assert builder.productions is BUILDER_PRODUCTION_SET
    assert [
        (item.id, type(item).__name__, item.applies_to)
        for item in builder.productions
    ] == [
        ('builder.import_from', 'ImportFromProduction', 'import_from'),
        ('builder.import', 'ImportProduction', 'import'),
        ('builder.class_decl', 'ClassDeclProduction', 'class_decl'),
        ('builder.func_decl', 'FuncDeclProduction', 'func_decl'),
        ('builder.attr_decl', 'AttrDeclProduction', 'attr_decl'),
        ('builder.self_attr_assign', 'SelfAttrAssignProduction', 'expression'),
    ]

    # apply delegates to the walker method rather than invoking productions itself.
    calls = []

    def spy(self, visit, candidate, context):
        '''
        Record the apply_attachments call.

        :param self: The walker.
        :param visit: The visit hook.
        :param candidate: The candidate.
        :param context: The visit context.
        :return: An empty result list.
        '''

        # Keep the call so the test can see that apply reached the walker.
        calls.append((self, visit, candidate))
        return []

    monkeypatch.setattr(StatementWalker, 'apply_attachments', spy)
    builder.apply('import', 'candidate')
    assert calls == [(builder, 'import', 'candidate')]

# ** test: resolver_uses_apply_attachments
def test_resolver_uses_apply_attachments(monkeypatch) -> None:
    '''
    Test that NameResolver.apply calls StatementWalker.apply_attachments.

    :param monkeypatch: The pytest monkeypatch fixture.
    :type monkeypatch: object
    '''

    # The host does not copy the attaches_to loop.
    source = inspect.getsource(NameResolver.apply)
    assert 'apply_attachments' in source
    assert 'attaches_to' not in source
    assert NameResolver.apply_attachments is StatementWalker.apply_attachments

    # The default set is the resolver production set, in TRD order.
    resolver = NameResolver(scopes={})
    assert resolver.productions is RESOLVER_PRODUCTION_SET
    assert [
        (item.id, type(item).__name__, item.applies_to)
        for item in resolver.productions
    ] == [
        ('resolver.name', 'NameProduction', 'name'),
        ('resolver.self_attr', 'SelfAttrProduction', 'self_attr'),
    ]

    # apply delegates to the walker method and passes the accumulator.
    calls = []

    def spy(self, visit, candidate, context):
        '''
        Record the apply_attachments call.

        :param self: The walker.
        :param visit: The visit hook.
        :param candidate: The candidate.
        :param context: The visit context.
        :return: An empty result list.
        '''

        # Keep the accumulator so the test can see that the host owns the sink.
        calls.append((self, visit, candidate, context.accumulator))
        return []

    monkeypatch.setattr(StatementWalker, 'apply_attachments', spy)
    resolver.apply('name', 'DomainEvent')
    assert calls == [(resolver, 'name', 'DomainEvent', resolver._accumulator)]
