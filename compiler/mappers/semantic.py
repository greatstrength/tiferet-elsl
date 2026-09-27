"""Tiferet Compiler Semantic Analysis Mapper Objects"""

# *** imports

# ** core
from typing import List, Optional

# ** app
from ..domain.semantic import (
    SYMBOL_KIND_CLASS_DEF,
    SYMBOL_KIND_METHOD,
    SYMBOL_KIND_MODULE,
    ResolutionResult,
    ResolvedName,
    Scope,
    Symbol,
    UnresolvedName,
)

# *** mappers

# ** mapper: scope_aggregate
class ScopeAggregate(Scope):
    '''
    Aggregate extending Scope with static factories and mutation methods for building symbol tables.

    Symbol tables change as names are defined. This aggregate is the mutation
    layer; Scope stays the read-only description of one scope.
    '''

    # * method: new_module_scope (static)
    @staticmethod
    def new_module_scope(module_name: str) -> 'ScopeAggregate':
        '''
        Create the root module scope.

        ``module_name`` is accepted for call-site symmetry and is not stored.
        The root scope is always named ``module`` at path ``module``.

        :param module_name: Caller module name; not stored on the scope.
        :type module_name: str
        :return: The root module scope.
        :rtype: ScopeAggregate
        '''

        # Accept the module name without storing it on the root scope.
        del module_name

        # The root scope is always the module path, with empty maps.
        return ScopeAggregate(
            name='module',
            kind=SYMBOL_KIND_MODULE,
            path='module',
        )

    # * method: new_class_scope (static)
    @staticmethod
    def new_class_scope(name: str, parent_path: str) -> 'ScopeAggregate':
        '''
        Create a class scope under a parent path.

        :param name: The class scope segment.
        :type name: str
        :param parent_path: The parent scope path.
        :type parent_path: str
        :return: The class scope.
        :rtype: ScopeAggregate
        '''

        # Qualify the class path from the parent and the class name.
        return ScopeAggregate(
            name=name,
            kind=SYMBOL_KIND_CLASS_DEF,
            path=f'{parent_path}.{name}',
            parent_path=parent_path,
        )

    # * method: new_method_scope (static)
    @staticmethod
    def new_method_scope(name: str, parent_path: str) -> 'ScopeAggregate':
        '''
        Create a method scope under a parent path.

        :param name: The method scope segment.
        :type name: str
        :param parent_path: The parent scope path.
        :type parent_path: str
        :return: The method scope.
        :rtype: ScopeAggregate
        '''

        # Qualify the method path from the parent and the method name.
        return ScopeAggregate(
            name=name,
            kind=SYMBOL_KIND_METHOD,
            path=f'{parent_path}.{name}',
            parent_path=parent_path,
        )

    # * method: add_symbol
    def add_symbol(self, symbol: Symbol) -> None:
        '''
        Store a symbol in this scope under its name.

        :param symbol: The symbol to store.
        :type symbol: Symbol
        :return: None
        :rtype: None
        '''

        # Index the symbol by the name later lookups will use.
        self.symbols[symbol.name] = symbol

    # * method: add_child
    def add_child(self, name: str, child_path: str) -> None:
        '''
        Record a child scope path under a name.

        :param name: The child scope segment.
        :type name: str
        :param child_path: The fully qualified child scope path.
        :type child_path: str
        :return: None
        :rtype: None
        '''

        # Map the child name to its qualified path.
        self.children[name] = child_path

    # * method: remove_child
    def remove_child(self, name: str) -> None:
        '''
        Remove a child scope path, ignoring a missing name.

        :param name: The child scope segment to remove.
        :type name: str
        :return: None
        :rtype: None
        '''

        # Drop the child when present; a missing name is a no-op.
        self.children.pop(name, None)

    # * method: has_symbol
    def has_symbol(self, name: str) -> bool:
        '''
        Report whether this scope defines a name.

        :param name: The symbol name to check.
        :type name: str
        :return: True when the name is defined in this scope.
        :rtype: bool
        '''

        # Membership is the definition check for this scope.
        return name in self.symbols

    # * method: get_symbol
    def get_symbol(self, name: str) -> Optional[Symbol]:
        '''
        Return the symbol stored under a name, if any.

        :param name: The symbol name to retrieve.
        :type name: str
        :return: The stored symbol, or None when the name is absent.
        :rtype: Optional[Symbol]
        '''

        # Absent names return None rather than raising.
        return self.symbols.get(name)


# ** mapper: resolution_accumulator
class ResolutionAccumulator:
    '''
    Accumulates resolved and unresolved name references during AST name resolution, then produces a ResolutionResult.

    It is an in-memory collector, not a domain object. Callers record each
    lookup as the walk proceeds, then take one result.
    '''

    # * attribute: resolved
    resolved: List[ResolvedName]

    # * attribute: unresolved
    unresolved: List[UnresolvedName]

    # * init
    def __init__(self) -> None:
        '''
        Initialize empty resolved and unresolved lists.

        :return: None
        :rtype: None
        '''

        # Start with no lookups recorded.
        self.resolved = []
        self.unresolved = []

    # * method: record_resolved
    def record_resolved(self, name: str, scope_path: str,
                        resolved_to: str) -> None:
        '''
        Record a name that resolved to a defining scope.

        :param name: The name that resolved.
        :type name: str
        :param scope_path: The scope where the reference was encountered.
        :type scope_path: str
        :param resolved_to: The scope path of the definition.
        :type resolved_to: str
        :return: None
        :rtype: None
        '''

        # Append the successful lookup without replacing earlier rows.
        self.resolved.append(ResolvedName(
            name=name,
            scope_path=scope_path,
            resolved_to=resolved_to,
        ))

    # * method: record_unresolved
    def record_unresolved(self, name: str, scope_path: str) -> None:
        '''
        Record a name that did not resolve to a definition.

        :param name: The name that did not resolve.
        :type name: str
        :param scope_path: The scope where the reference was encountered.
        :type scope_path: str
        :return: None
        :rtype: None
        '''

        # Append the failed lookup so conformance can report it later.
        self.unresolved.append(UnresolvedName(
            name=name,
            scope_path=scope_path,
        ))

    # * method: reset
    def reset(self) -> None:
        '''
        Clear recorded resolved and unresolved names.

        :return: None
        :rtype: None
        '''

        # Drop both lists so the collector can be reused.
        self.resolved = []
        self.unresolved = []

    # * method: to_result
    def to_result(self) -> ResolutionResult:
        '''
        Produce a resolution result from the recorded lookups.

        :return: The collected resolution result.
        :rtype: ResolutionResult
        '''

        # Hand both lists to the result without a second pass.
        return ResolutionResult(
            resolved=self.resolved,
            unresolved=self.unresolved,
        )
