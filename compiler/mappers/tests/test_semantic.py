"""Tests for Semantic Analysis Mapper Objects"""

# *** imports

# ** app
from ...domain.semantic import (
    SYMBOL_KIND_CLASS_DEF,
    SYMBOL_KIND_IMPORT,
    SYMBOL_KIND_METHOD,
    SYMBOL_KIND_MODULE,
    Symbol,
)
from .. import SymbolScope
from ..semantic import ScopeAggregate

# *** tests

# ** test: new_module_scope
def test_new_module_scope() -> None:
    '''
    Test that a module scope ignores the module name and starts empty.
    '''

    # Build a root scope with a name that must not be stored.
    scope = ScopeAggregate.new_module_scope('ping')

    # Assert the fixed root identity and the empty maps.
    assert scope.name == 'module'
    assert scope.kind == SYMBOL_KIND_MODULE
    assert scope.path == 'module'
    assert scope.parent_path is None
    assert scope.symbols == {}
    assert scope.children == {}

# ** test: new_class_scope
def test_new_class_scope() -> None:
    '''
    Test that a class scope is qualified under its parent path.
    '''

    # Build a class scope under the module root.
    scope = ScopeAggregate.new_class_scope('Ping', 'module')

    # Assert the qualified path, kind, and parent.
    assert scope.path == 'module.Ping'
    assert scope.kind == SYMBOL_KIND_CLASS_DEF
    assert scope.parent_path == 'module'

# ** test: new_method_scope
def test_new_method_scope() -> None:
    '''
    Test that a method scope is qualified under its class path.
    '''

    # Build a method scope under the class path.
    scope = ScopeAggregate.new_method_scope('execute', 'module.Ping')

    # Assert the qualified path and method kind.
    assert scope.path == 'module.Ping.execute'
    assert scope.kind == SYMBOL_KIND_METHOD

# ** test: add_symbol
def test_add_symbol() -> None:
    '''
    Test that an import symbol is stored under its name.
    '''

    # Construct an import symbol and an empty module scope.
    symbol = Symbol(
        name='DomainEvent',
        kind=SYMBOL_KIND_IMPORT,
        scope_path='module',
        source_module='.settings',
    )
    scope = ScopeAggregate.new_module_scope('ping')

    # Store the symbol.
    scope.add_symbol(symbol)

    # Assert the import is indexed by its name.
    assert scope.symbols['DomainEvent'] is symbol

# ** test: add_child
def test_add_child() -> None:
    '''
    Test that a child scope path is recorded under its name.
    '''

    # Start from an empty module scope.
    scope = ScopeAggregate.new_module_scope('ping')

    # Record the class child path.
    scope.add_child('Ping', 'module.Ping')

    # Assert the child map.
    assert scope.children == {'Ping': 'module.Ping'}

# ** test: remove_child
def test_remove_child() -> None:
    '''
    Test that removing a recorded child leaves an empty child map.
    '''

    # Record a child, then remove it.
    scope = ScopeAggregate.new_module_scope('ping')
    scope.add_child('Ping', 'module.Ping')
    scope.remove_child('Ping')

    # Assert the child map is empty.
    assert scope.children == {}

# ** test: remove_child_missing
def test_remove_child_missing() -> None:
    '''
    Test that removing a missing child does not raise.
    '''

    # An empty scope has no child to remove.
    scope = ScopeAggregate.new_module_scope('ping')

    # A missing name is a no-op.
    scope.remove_child('Ping')

    # Assert the child map is unchanged.
    assert scope.children == {}

# ** test: has_symbol
def test_has_symbol() -> None:
    '''
    Test that symbol membership is false before add and true after.
    '''

    # Construct the symbol that will be added.
    symbol = Symbol(
        name='DomainEvent',
        kind=SYMBOL_KIND_IMPORT,
        scope_path='module',
    )
    scope = ScopeAggregate.new_module_scope('ping')

    # Assert absence before the add.
    assert scope.has_symbol('DomainEvent') is False

    # Store the symbol and assert presence.
    scope.add_symbol(symbol)
    assert scope.has_symbol('DomainEvent') is True

# ** test: get_symbol
def test_get_symbol() -> None:
    '''
    Test that get_symbol returns None before add and the symbol after.
    '''

    # Construct a symbol that carries a type annotation.
    symbol = Symbol(
        name='items',
        kind=SYMBOL_KIND_IMPORT,
        scope_path='module',
        type_annotation='List[str]',
    )
    scope = ScopeAggregate.new_module_scope('ping')

    # Assert absence before the add.
    assert scope.get_symbol('items') is None

    # Store the symbol and assert it is returned with its annotation.
    scope.add_symbol(symbol)
    stored = scope.get_symbol('items')
    assert stored is symbol
    assert stored.type_annotation == 'List[str]'

# ** test: symbol_scope_alias
def test_symbol_scope_alias() -> None:
    '''
    Test that the package facade exports ScopeAggregate as SymbolScope.
    '''

    # The facade alias is the aggregate class, not a second type.
    assert SymbolScope is ScopeAggregate
