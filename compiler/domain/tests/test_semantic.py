"""Domain – Semantic Domain Objects Tests"""

# *** imports

# ** infra
import pytest
from pydantic import ValidationError

# ** app
from ..semantic import (
    ResolutionResult,
    ResolvedName,
    Scope,
    Symbol,
    SymbolKind,
    UnresolvedName,
)

# *** tests

# ** test: symbol_kind_values
def test_symbol_kind_values() -> None:
    '''
    Test that every SymbolKind member equals its declared string and that there are no extras.
    '''

    # Define the expected symbol-kind vocabulary.
    expected = {
        'MODULE': 'module',
        'IMPORT': 'import',
        'CLASS_DEF': 'class_def',
        'METHOD': 'method',
        'ATTRIBUTE': 'attribute',
        'PARAMETER': 'parameter',
        'VARIABLE': 'variable',
    }

    # Assert the member count and each string value.
    assert len(SymbolKind) == 7
    assert {member.name: member.value for member in SymbolKind} == expected
    for name, value in expected.items():
        assert SymbolKind[name] == value

# ** test: symbol_creation
def test_symbol_creation() -> None:
    '''
    Test that a class symbol stores its required fields and leaves optionals unset.
    '''

    # Construct a class symbol with only the required fields.
    symbol = Symbol(
        name='Ping',
        kind=SymbolKind.CLASS_DEF,
        scope_path='module',
    )

    # Assert the required fields and the unset optionals.
    assert symbol.name == 'Ping'
    assert symbol.kind == SymbolKind.CLASS_DEF
    assert symbol.scope_path == 'module'
    assert symbol.type_annotation is None
    assert symbol.source_module is None

# ** test: symbol_creation_with_type_annotation
def test_symbol_creation_with_type_annotation() -> None:
    '''
    Test that optional type annotation and source module persist.
    '''

    # Construct a symbol with both optional fields set.
    symbol = Symbol(
        name='List',
        kind=SymbolKind.IMPORT,
        scope_path='module',
        type_annotation='str',
        source_module='typing',
    )

    # Assert the optional fields persist.
    assert symbol.type_annotation == 'str'
    assert symbol.source_module == 'typing'

# ** test: scope_creation
def test_scope_creation() -> None:
    '''
    Test that a module scope starts with empty maps and no parent.
    '''

    # Construct a module scope with only the required fields.
    scope = Scope(
        name='module',
        kind=SymbolKind.MODULE,
        path='module',
    )

    # Assert the empty maps and absent parent.
    assert scope.name == 'module'
    assert scope.kind == SymbolKind.MODULE
    assert scope.path == 'module'
    assert scope.symbols == {}
    assert scope.children == {}
    assert scope.parent_path is None

# ** test: scope_creation_with_parent
def test_scope_creation_with_parent() -> None:
    '''
    Test that a nested scope stores its parent path and symbol and child maps.
    '''

    # Construct a parameter symbol defined in the nested method scope.
    symbol = Symbol(
        name='id',
        kind=SymbolKind.PARAMETER,
        scope_path='module.Ping.execute',
    )

    # Construct a method scope under its class parent.
    scope = Scope(
        name='execute',
        kind=SymbolKind.METHOD,
        path='module.Ping.execute',
        parent_path='module.Ping',
        symbols={'id': symbol},
        children={'inner': 'module.Ping.execute.inner'},
    )

    # Assert the parent path and both maps persist.
    assert scope.parent_path == 'module.Ping'
    assert scope.symbols == {'id': symbol}
    assert scope.children == {'inner': 'module.Ping.execute.inner'}

# ** test: resolved_name_creation
def test_resolved_name_creation() -> None:
    '''
    Test that a resolved name stores all three required fields.
    '''

    # Construct a resolved name reference.
    resolved = ResolvedName(
        name='Ping',
        scope_path='module',
        resolved_to='module',
    )

    # Assert each required field persists.
    assert resolved.name == 'Ping'
    assert resolved.scope_path == 'module'
    assert resolved.resolved_to == 'module'

# ** test: unresolved_name_creation
def test_unresolved_name_creation() -> None:
    '''
    Test that an unresolved name stores both required fields.
    '''

    # Construct an unresolved name reference.
    unresolved = UnresolvedName(
        name='missing',
        scope_path='module.Ping.execute',
    )

    # Assert both required fields persist.
    assert unresolved.name == 'missing'
    assert unresolved.scope_path == 'module.Ping.execute'

# ** test: resolution_result_defaults
def test_resolution_result_defaults() -> None:
    '''
    Test that a new resolution result starts with empty lookup lists.
    '''

    # Construct a resolution result with no lookups.
    result = ResolutionResult()

    # Assert both lists are empty.
    assert result.resolved == []
    assert result.unresolved == []

# ** test: resolution_result_with_entries
def test_resolution_result_with_entries() -> None:
    '''
    Test that provided resolved and unresolved lists persist.
    '''

    # Construct one successful lookup and one failed lookup.
    resolved = ResolvedName(
        name='Ping',
        scope_path='module',
        resolved_to='module',
    )
    unresolved = UnresolvedName(
        name='missing',
        scope_path='module',
    )

    # Construct a result that carries both lists.
    result = ResolutionResult(
        resolved=[resolved],
        unresolved=[unresolved],
    )

    # Assert the provided lists persist.
    assert result.resolved == [resolved]
    assert result.unresolved == [unresolved]

# ** test: symbol_missing_name_raises
def test_symbol_missing_name_raises() -> None:
    '''
    Test that Symbol without a name raises ValidationError.
    '''

    # Omitting the required name must raise ValidationError.
    with pytest.raises(ValidationError):
        Symbol(kind=SymbolKind.CLASS_DEF, scope_path='module')

# ** test: scope_missing_path_raises
def test_scope_missing_path_raises() -> None:
    '''
    Test that Scope without a path raises ValidationError.
    '''

    # Omitting the required path must raise ValidationError.
    with pytest.raises(ValidationError):
        Scope(name='module', kind=SymbolKind.MODULE)

# ** test: resolved_name_missing_required_raises
def test_resolved_name_missing_required_raises() -> None:
    '''
    Test that ResolvedName without a required field raises ValidationError.
    '''

    # Omitting any one required field must raise ValidationError.
    with pytest.raises(ValidationError):
        ResolvedName(scope_path='module', resolved_to='module')
    with pytest.raises(ValidationError):
        ResolvedName(name='Ping', resolved_to='module')
    with pytest.raises(ValidationError):
        ResolvedName(name='Ping', scope_path='module')

# ** test: unresolved_name_missing_required_raises
def test_unresolved_name_missing_required_raises() -> None:
    '''
    Test that UnresolvedName without a required field raises ValidationError.
    '''

    # Omitting either required field must raise ValidationError.
    with pytest.raises(ValidationError):
        UnresolvedName(scope_path='module')
    with pytest.raises(ValidationError):
        UnresolvedName(name='missing')
