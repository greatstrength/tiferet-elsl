"""Compiler Core Utilities"""

# *** imports

# ** core
from contextlib import contextmanager
from typing import Any, Callable, ClassVar, Dict, FrozenSet, Iterator, List, Optional

# ** infra
from pydantic import Field

# ** app
from ..mappers import (
    SYMBOL_KIND_CLASS_DEF,
    Declaration,
    ExprKind,
    Expression,
    Provision,
    Rewrite,
    ScopeAggregate,
    Specification,
    Statement,
)

# *** constants

# ** constant: pascal_case_acronyms
PASCAL_CASE_ACRONYMS = frozenset({'di'})

# *** functions

# ** function: child_scope_path
def child_scope_path(parent_path: str, name: str) -> str:
    '''
    Join a parent scope path and a child name.

    :param parent_path: The enclosing scope path.
    :type parent_path: str
    :param name: The child scope segment.
    :type name: str
    :return: The dotted child path.
    :rtype: str
    '''

    # Qualify the child under the parent path.
    return f'{parent_path}.{name}'

# ** function: snake_to_pascal
def snake_to_pascal(snake: str) -> str:
    '''
    Convert a snake_case name to PascalCase, keeping known acronyms capitalized.

    :param snake: The snake_case name.
    :type snake: str
    :return: The PascalCase name.
    :rtype: str
    '''

    # Capitalize each word, leaving corpus acronyms fully capitalized.
    parts = []
    for word in snake.split('_'):
        if word.lower() in PASCAL_CASE_ACRONYMS:
            parts.append(word.upper())
        else:
            parts.append(word.capitalize())

    # Join without a separator.
    return ''.join(parts)

# ** function: is_function_section
def is_function_section(header_decl: Declaration) -> bool:
    '''
    Report whether a header marks a function or blueprint section.

    :param header_decl: The section header declaration.
    :type header_decl: Declaration
    :return: True when the artifact type is a function or blueprint section.
    :rtype: bool
    '''

    # Function and blueprint sections share the function-section predicate.
    artifact_type = (getattr(header_decl, 'artifact_type', '') or '').strip()
    return artifact_type in ('** function', '** blueprint')

# ** function: collect_member_decorators
def collect_member_decorators(member_decl: Declaration) -> List[str]:
    '''
    Collect encoded decorators that precede a member's inner declaration.

    :param member_decl: The artifact member declaration.
    :type member_decl: Declaration
    :return: Encoded decorator expressions, in source order.
    :rtype: List[str]
    '''

    # Stop at the inner declaration; earlier expressions are decorators.
    decorators = []
    for stmt in member_decl.code:
        if stmt.is_decl:
            break
        if not stmt.is_expr or stmt.expr is None:
            continue

        # Keep only decorators whose encoding is non-empty.
        encoded = stmt.expr.encode()
        if encoded:
            decorators.append(encoded)

    # Return the encoded decorators.
    return decorators

# ** function: types_compatible
def types_compatible(declared: str, actual: str) -> bool:
    '''
    Report whether an actual type may be used where a declared type is expected.

    :param declared: The declared type name.
    :type declared: str
    :param actual: The actual type name.
    :type actual: str
    :return: True on an exact match, or when float accepts int.
    :rtype: bool
    '''

    # Exact matches are compatible, and int widens to float.
    if declared == actual:
        return True
    return declared == 'float' and actual == 'int'

# ** function: get_type_name
def get_type_name(type_obj: Any) -> str:
    '''
    Read a type object's display name.

    :param type_obj: The type object, or a missing value.
    :type type_obj: Any
    :return: ``unknown`` when the type is missing; otherwise its type name.
    :rtype: str
    '''

    # A missing type has no name to report.
    if not type_obj:
        return 'unknown'

    # Return the type's own display name.
    return type_obj.type_name

# ** function: get_return_type_name
def get_return_type_name(type_obj: Any) -> str:
    '''
    Read the display name of a callable type's return type.

    :param type_obj: The callable type, or a missing value.
    :type type_obj: Any
    :return: ``unknown`` when the type or its return type is missing.
    :rtype: str
    '''

    # A missing type, or a type with no return type, is unknown.
    if not type_obj or not getattr(type_obj, 'return_type', None):
        return 'unknown'

    # Return the nested return type's display name.
    return type_obj.return_type.type_name

# ** function: extract_member_name_from_metadata
def extract_member_name_from_metadata(decl: Declaration) -> Optional[str]:
    '''
    Return the member identifier captured from an artifact-header token.

    Member-header identifier capture is out of scope, so this always returns None.

    :param decl: The member header declaration.
    :type decl: Declaration
    :return: None.
    :rtype: Optional[str]
    '''

    # Identifier capture from the header token is deferred.
    del decl
    return None

# ** function: declares_bound_domain_type
def declares_bound_domain_type(candidate: Any, context: Any,
                               class_decl: Declaration) -> bool:
    '''
    Report whether a class declares a bound domain_type attribute.

    A bare None initializer is a type-hint placeholder, not a binding.
    The section header and visit context are accepted so this can be a
    required-base predicate, and they are not consulted.

    :param candidate: The section header. Unused.
    :type candidate: Any
    :param context: The conformance visit context. Unused.
    :type context: Any
    :param class_decl: The class declaration to inspect.
    :type class_decl: Declaration
    :return: True when a domain_type attribute is initialized to a non-None value.
    :rtype: bool
    '''

    # A bound domain_type is an attribute whose initializer is not bare None.
    for member in class_decl.members:
        if getattr(member, 'artifact_role', None) != 'attribute':
            continue
        inner_decl = member.inner_decl
        if inner_decl is None or inner_decl.name != 'domain_type':
            continue
        value = getattr(inner_decl, 'value', None)
        if value is None or getattr(value, 'kind', None) == ExprKind.NONE_VAL:
            continue

        # Any other initializer binds the domain type.
        return True

    # No bound domain_type attribute was found.
    return False

# ** function: binary_op_findings
def _binary_op_findings(expr: Optional[Any], context: 'ConformanceContext') -> List[Dict]:
    '''
    Record a type-mismatch finding for an unsupported binary operation.

    :param expr: The candidate expression, or None.
    :type expr: Optional[Any]
    :param context: The conformance visit context.
    :type context: ConformanceContext
    :return: An empty list when the operation is allowed or unknown; otherwise one finding.
    :rtype: List[Dict]
    '''

    # A missing expression, or a non-binary expression, has nothing to check.
    if expr is None or not getattr(expr, 'is_binary_op', False):
        return []

    # Unknown operand types are not reported as mismatches.
    left_type = context.infer_type(expr.left)
    right_type = context.infer_type(expr.right)
    if left_type in (None, 'unknown') or right_type in (None, 'unknown'):
        return []

    # Numeric pairs, string addition, and string repetition are allowed.
    operation = expr.kind.value
    numeric = ConformanceContext.NUMERIC_TYPES
    if left_type in numeric and right_type in numeric:
        return []
    if operation == 'add' and left_type == 'str' and right_type == 'str':
        return []
    if operation == 'mul' and {left_type, right_type} == {'str', 'int'}:
        return []

    # Every other pair is an unsupported operation.
    return [{
        'error_code': 'TYPE_MISMATCH_OPERATION',
        'message': f'Unsupported operand types for {operation}: {left_type} and {right_type}',
        'node': expr,
        'operation': operation,
        'left_type': left_type,
        'right_type': right_type,
    }]

# ** function: has_not_implemented_body
def _has_not_implemented_body(
        inner: Declaration,
        callee_name: str = 'NotImplementedError') -> bool:
    '''
    Report whether a declaration body is exactly one raise of a named callee.

    :param inner: The inner declaration.
    :type inner: Declaration
    :param callee_name: The expected raise callee.
    :type callee_name: str
    :return: True when the body is one snippet containing one matching raise call.
    :rtype: bool
    '''

    # The body must be exactly one snippet.
    if len(inner.code) != 1 or not inner.code[0].is_snippet:
        return False

    # That snippet must contain exactly one raise statement.
    snippet = inner.code[0]
    if len(snippet.body) != 1 or not snippet.body[0].is_raise:
        return False

    # The raised expression must be a call of the expected callee.
    expr = snippet.body[0].expr
    if expr is None or expr.kind != ExprKind.CALL or expr.left is None:
        return False
    return expr.left.name == callee_name

# *** classes

# ** class: conformance_context
class ConformanceContext:
    '''
    Host context for a Kind 1 specification visit.

    It carries the scope stack and the enclosing statement so a specification
    can look types up without owning the walk.
    '''

    # * attribute: NUMERIC_TYPES
    NUMERIC_TYPES: ClassVar[FrozenSet[str]] = frozenset({'int', 'float'})

    # * attribute: scope_stack
    scope_stack: List[ScopeAggregate]

    # * attribute: stmt
    stmt: Optional[Statement]

    # * attribute: group_name
    group_name: Optional[str]

    # * init
    def __init__(self, scope_stack=None, stmt=None, group_name=None) -> None:
        '''
        Store the scope stack, enclosing statement, and group name.

        :param scope_stack: The scope stack, module scope first.
        :type scope_stack: Optional[List[ScopeAggregate]]
        :param stmt: The enclosing statement, when the visit needs siblings.
        :type stmt: Optional[Statement]
        :param group_name: The innermost tier-1 group name.
        :type group_name: Optional[str]
        :return: None
        :rtype: None
        '''

        # A missing stack starts empty rather than sharing a default list.
        self.scope_stack = scope_stack or []

        # Store the enclosing statement and group for visits that need them.
        self.stmt = stmt
        self.group_name = group_name

    # * method: current_scope
    @property
    def current_scope(self) -> Optional[ScopeAggregate]:
        '''
        Return the innermost scope, if any.

        :return: The last scope on the stack, or None.
        :rtype: Optional[ScopeAggregate]
        '''

        # An empty stack has no current scope.
        if not self.scope_stack:
            return None

        # The innermost scope is the end of the stack.
        return self.scope_stack[-1]

    # * method: infer_type
    def infer_type(self, expr: Optional[Expression]) -> Optional[str]:
        '''
        Infer a shallow type name for an expression.

        :param expr: The expression, or None.
        :type expr: Optional[Expression]
        :return: The inferred type name, or None when it cannot be inferred.
        :rtype: Optional[str]
        '''

        # A missing expression has no type.
        if expr is None:
            return None

        # Literals carry their inferred type on the node.
        if expr.literal_type is not None:
            return expr.literal_type

        # A name reference is resolved through the scope stack.
        if expr.is_name_ref:
            return self.lookup_type(expr)

        # Binary operations cover only the shallow numeric and string cases.
        if expr.is_binary_op:
            return self._infer_binary_type(expr)

        # Other expression kinds are not inferred here.
        return None

    # * method: lookup_type
    def lookup_type(self, expr: Expression) -> Optional[str]:
        '''
        Look up a name reference's type annotation.

        :param expr: The name-reference expression.
        :type expr: Expression
        :return: The type annotation, or None when the name is unbound.
        :rtype: Optional[str]
        '''

        # An empty name cannot be looked up.
        if not expr.name:
            return None

        # A self attribute is resolved on the enclosing class scope.
        if expr.is_self_attribute:
            return self._lookup_self_attribute(expr.name[5:])

        # Walk inner to outer and return the first recorded annotation.
        for scope in reversed(self.scope_stack):
            symbol = scope.get_symbol(expr.name)
            if symbol is not None:
                return symbol.type_annotation

        # No scope defined the name.
        return None

    # * method: types_compatible
    def types_compatible(self, declared: str, actual: str) -> bool:
        '''
        Report whether an actual type may be used where a declared type is expected.

        :param declared: The declared type name.
        :type declared: str
        :param actual: The actual type name.
        :type actual: str
        :return: True on an exact match, or when float accepts int.
        :rtype: bool
        '''

        # Delegate to the shared widening rule.
        return types_compatible(declared, actual)

    # * method: _infer_binary_type
    def _infer_binary_type(self, expr: Expression) -> Optional[str]:
        '''
        Infer the result type of a shallow binary operation.

        :param expr: The binary expression.
        :type expr: Expression
        :return: ``str``, ``int``, ``float``, or None.
        :rtype: Optional[str]
        '''

        # Infer both operands before applying the shallow rules.
        left_type = self.infer_type(expr.left)
        right_type = self.infer_type(expr.right)
        operation = expr.kind.value

        # String addition and string repetition produce str.
        if operation == 'add' and left_type == 'str' and right_type == 'str':
            return 'str'
        if operation == 'mul' and (
                (left_type == 'str' and right_type == 'int')
                or (left_type == 'int' and right_type == 'str')):
            return 'str'

        # Numeric pairs widen to float when either operand is float.
        if left_type in self.NUMERIC_TYPES and right_type in self.NUMERIC_TYPES:
            if left_type == 'float' or right_type == 'float':
                return 'float'
            return 'int'

        # Other pairs are not inferred.
        return None

    # * method: _lookup_self_attribute
    def _lookup_self_attribute(self, attr_name: str) -> Optional[str]:
        '''
        Look up a self attribute on the enclosing class scope.

        :param attr_name: The attribute name with the ``self.`` prefix removed.
        :type attr_name: str
        :return: The class attribute's type annotation, or None.
        :rtype: Optional[str]
        '''

        # Walk inner to outer for the enclosing class definition.
        for scope in reversed(self.scope_stack):
            if scope.kind != SYMBOL_KIND_CLASS_DEF:
                continue

            # Return that class scope's annotation, including when it is unset.
            symbol = scope.get_symbol(attr_name)
            if symbol is None:
                return None
            return symbol.type_annotation

        # No enclosing class scope was on the stack.
        return None

# ** class: production_context
class ProductionContext:
    '''
    Host context for a Kind 2 production visit.

    It carries the scope stack and the host-owned accumulator productions write into.
    '''

    # * attribute: scope_stack
    scope_stack: List[ScopeAggregate]

    # * attribute: accumulator
    accumulator: Optional[Any]

    # * init
    def __init__(self, scope_stack=None, accumulator=None) -> None:
        '''
        Store the scope stack and accumulator.

        :param scope_stack: The scope stack, module scope first.
        :type scope_stack: Optional[List[ScopeAggregate]]
        :param accumulator: The host-owned sink.
        :type accumulator: Optional[Any]
        :return: None
        :rtype: None
        '''

        # A missing stack starts empty rather than sharing a default list.
        self.scope_stack = scope_stack or []

        # Store the sink productions write into.
        self.accumulator = accumulator

    # * method: current_scope
    @property
    def current_scope(self) -> Optional[ScopeAggregate]:
        '''
        Return the innermost scope, if any.

        :return: The last scope on the stack, or None.
        :rtype: Optional[ScopeAggregate]
        '''

        # An empty stack has no current scope.
        if not self.scope_stack:
            return None

        # The innermost scope is the end of the stack.
        return self.scope_stack[-1]

    # * method: find_enclosing_scope
    def find_enclosing_scope(self, kind: str) -> Optional[ScopeAggregate]:
        '''
        Find the innermost scope of a given kind.

        Trunk scope kinds are the ``SYMBOL_KIND_*`` strings. ``SymbolKind`` is
        not re-exported by ``compiler.mappers``.

        :param kind: The scope kind to find.
        :type kind: str
        :return: The innermost matching scope, or None.
        :rtype: Optional[ScopeAggregate]
        '''

        # Walk inner to outer and return the first matching kind.
        for scope in reversed(self.scope_stack):
            if scope.kind == kind:
                return scope

        # No enclosing scope had that kind.
        return None

# ** class: rewrite_context
class RewriteContext:
    '''
    Host context for a Kind 3 rewrite visit.

    This story adds the context only. Kind 3 hosts arrive later.
    '''

    # * attribute: host
    host: Any

    # * attribute: qualifier
    qualifier: Optional[str]

    # * attribute: event
    event: Optional[Any]

    # * attribute: accumulator
    accumulator: Optional[Any]

    # * init
    def __init__(self,
            host=None,
            qualifier=None,
            event=None,
            accumulator=None) -> None:
        '''
        Store the host, qualifier, event, and accumulator.

        :param host: The rewrite host.
        :type host: Any
        :param qualifier: The optional qualifier the host is emitting under.
        :type qualifier: Optional[str]
        :param event: The optional event the host is rewriting.
        :type event: Optional[Any]
        :param accumulator: The optional host-owned sink.
        :type accumulator: Optional[Any]
        :return: None
        :rtype: None
        '''

        # Store each host argument without interpreting it.
        self.host = host
        self.qualifier = qualifier
        self.event = event
        self.accumulator = accumulator

# ** class: statement_walker
class StatementWalker:
    '''
    Shared AST-walking mechanics for later hosts.

    Subclasses supply the provision list and the visit context. They do not
    copy statement dispatch, the scope stack, or the attaches_to loop.
    '''

    # * attribute: scopes
    scopes: Dict[str, ScopeAggregate]

    # * attribute: scope_stack
    scope_stack: List[ScopeAggregate]

    # * attribute: provisions
    provisions: List[Provision]

    # * init
    def __init__(self, scopes=None, provisions=None) -> None:
        '''
        Store the scope registry and provision list.

        :param scopes: The flat path-to-scope registry.
        :type scopes: Optional[Dict[str, ScopeAggregate]]
        :param provisions: The provisions this host invokes.
        :type provisions: Optional[List[Provision]]
        :return: None
        :rtype: None
        '''

        # Preserve an explicitly empty registry; only None becomes a new mapping.
        self.scopes = scopes if scopes is not None else {}
        self.provisions = provisions if provisions is not None else []

        # The walk starts outside every scope.
        self.scope_stack = []

    # * method: _invoke
    def _invoke(self, provision: Provision, candidate: Any, context: Any) -> Any:
        '''
        Invoke one provision as a callable.

        :param provision: The provision to invoke.
        :type provision: Provision
        :param candidate: The node being visited.
        :type candidate: Any
        :param context: The host visit context.
        :type context: Any
        :return: The provision result.
        :rtype: Any
        '''

        # Hosts invoke provisions as callables, not by kind-specific method names.
        return provision(candidate, context)

    # * method: apply_provisions
    def apply_provisions(self, visit: str, candidate: Any, context: Any) -> List[Any]:
        '''
        Invoke every provision whose hook matches the visit.

        :param visit: The visit hook.
        :type visit: str
        :param candidate: The node being visited.
        :type candidate: Any
        :param context: The host visit context.
        :type context: Any
        :return: Results in provision-list order.
        :rtype: List[Any]
        '''

        # This is the only attaches_to loop. Preserve provision-list order.
        results = []
        for provision in self.provisions:
            if provision.attaches_to(visit):
                results.append(self._invoke(provision, candidate, context))

        # Return the matching results, including when none matched.
        return results

    # * method: current_scope
    @property
    def current_scope(self) -> Optional[ScopeAggregate]:
        '''
        Return the innermost scope, if any.

        :return: The last scope on the stack, or None.
        :rtype: Optional[ScopeAggregate]
        '''

        # An empty stack has no current scope.
        if not self.scope_stack:
            return None

        # The innermost scope is the end of the stack.
        return self.scope_stack[-1]

    # * method: entering_child_scope
    @contextmanager
    def entering_child_scope(self, name: str) -> Iterator[Optional[ScopeAggregate]]:
        '''
        Push a registered child scope for the duration of a nested walk.

        :param name: The child scope segment.
        :type name: str
        :return: The child scope, or None when it is not registered.
        :rtype: Iterator[Optional[ScopeAggregate]]
        '''

        # Look the child up only when a current scope can qualify the path.
        child = None
        if self.current_scope is not None:
            child = self.scopes.get(child_scope_path(self.current_scope.path, name))

        # A missing child does not push.
        if child is None:
            yield None
            return

        # Push the registered child and pop it even when the body raises.
        self.scope_stack.append(child)
        try:
            yield child
        finally:
            self.scope_stack.pop()

    # * method: walk_statements
    def walk_statements(self, statements: List[Statement]) -> None:
        '''
        Dispatch each statement to the first matching handler.

        :param statements: The statements to walk.
        :type statements: List[Statement]
        :return: None
        :rtype: None
        '''

        # First matching predicate wins. Unlisted kinds are ignored.
        for stmt in statements:
            if stmt.is_artifact:
                self.handle_artifact(stmt)
            elif stmt.is_decl:
                self.handle_decl(stmt)
            elif stmt.is_expr:
                self.handle_expr(stmt)
            elif stmt.is_snippet:
                self.handle_snippet(stmt)
            elif stmt.is_return:
                self.handle_return(stmt)
            elif stmt.is_import_from:
                self.handle_import_from(stmt)
            elif stmt.is_import:
                self.handle_import(stmt)
            elif stmt.is_if_else:
                self.handle_if_else(stmt)
            elif stmt.is_for:
                self.handle_for(stmt)
            elif stmt.is_while:
                self.handle_while(stmt)
            elif stmt.is_try_except:
                self.handle_try_except(stmt)
            elif stmt.is_with:
                self.handle_with(stmt)
            elif stmt.is_raise:
                self.handle_raise(stmt)
            elif stmt.is_assert:
                self.handle_assert(stmt)
            elif stmt.is_del:
                self.handle_del(stmt)

    # * method: handle_artifact
    def handle_artifact(self, stmt: Statement) -> None:
        '''
        Recurse into an artifact wrapper's body.

        :param stmt: The artifact statement.
        :type stmt: Statement
        :return: None
        :rtype: None
        '''

        # Artifact wrappers always recurse when they have a body.
        if stmt.body:
            self.walk_statements(stmt.body)

    # * method: handle_snippet
    def handle_snippet(self, stmt: Statement) -> None:
        '''
        Recurse into a snippet wrapper's body.

        :param stmt: The snippet statement.
        :type stmt: Statement
        :return: None
        :rtype: None
        '''

        # Snippet wrappers always recurse when they have a body.
        if stmt.body:
            self.walk_statements(stmt.body)

    # * method: handle_decl
    def handle_decl(self, stmt: Statement) -> None:
        '''
        Ignore a declaration statement unless a subclass overrides this.

        :param stmt: The declaration statement.
        :type stmt: Statement
        :return: None
        :rtype: None
        '''

        # Unoverridden statement kinds silently no-op.
        del stmt

    # * method: handle_expr
    def handle_expr(self, stmt: Statement) -> None:
        '''
        Ignore an expression statement unless a subclass overrides this.

        :param stmt: The expression statement.
        :type stmt: Statement
        :return: None
        :rtype: None
        '''

        # Unoverridden statement kinds silently no-op.
        del stmt

    # * method: handle_return
    def handle_return(self, stmt: Statement) -> None:
        '''
        Ignore a return statement unless a subclass overrides this.

        :param stmt: The return statement.
        :type stmt: Statement
        :return: None
        :rtype: None
        '''

        # Unoverridden statement kinds silently no-op.
        del stmt

    # * method: handle_import
    def handle_import(self, stmt: Statement) -> None:
        '''
        Ignore an import statement unless a subclass overrides this.

        :param stmt: The import statement.
        :type stmt: Statement
        :return: None
        :rtype: None
        '''

        # Unoverridden statement kinds silently no-op.
        del stmt

    # * method: handle_import_from
    def handle_import_from(self, stmt: Statement) -> None:
        '''
        Ignore an import-from statement unless a subclass overrides this.

        :param stmt: The import-from statement.
        :type stmt: Statement
        :return: None
        :rtype: None
        '''

        # Unoverridden statement kinds silently no-op.
        del stmt

    # * method: handle_if_else
    def handle_if_else(self, stmt: Statement) -> None:
        '''
        Ignore an if statement unless a subclass overrides this.

        :param stmt: The if statement.
        :type stmt: Statement
        :return: None
        :rtype: None
        '''

        # Unoverridden statement kinds silently no-op.
        del stmt

    # * method: handle_for
    def handle_for(self, stmt: Statement) -> None:
        '''
        Ignore a for statement unless a subclass overrides this.

        :param stmt: The for statement.
        :type stmt: Statement
        :return: None
        :rtype: None
        '''

        # Unoverridden statement kinds silently no-op.
        del stmt

    # * method: handle_while
    def handle_while(self, stmt: Statement) -> None:
        '''
        Ignore a while statement unless a subclass overrides this.

        :param stmt: The while statement.
        :type stmt: Statement
        :return: None
        :rtype: None
        '''

        # Unoverridden statement kinds silently no-op.
        del stmt

    # * method: handle_try_except
    def handle_try_except(self, stmt: Statement) -> None:
        '''
        Ignore a try statement unless a subclass overrides this.

        :param stmt: The try statement.
        :type stmt: Statement
        :return: None
        :rtype: None
        '''

        # Unoverridden statement kinds silently no-op.
        del stmt

    # * method: handle_with
    def handle_with(self, stmt: Statement) -> None:
        '''
        Ignore a with statement unless a subclass overrides this.

        :param stmt: The with statement.
        :type stmt: Statement
        :return: None
        :rtype: None
        '''

        # Unoverridden statement kinds silently no-op.
        del stmt

    # * method: handle_raise
    def handle_raise(self, stmt: Statement) -> None:
        '''
        Ignore a raise statement unless a subclass overrides this.

        :param stmt: The raise statement.
        :type stmt: Statement
        :return: None
        :rtype: None
        '''

        # Unoverridden statement kinds silently no-op.
        del stmt

    # * method: handle_assert
    def handle_assert(self, stmt: Statement) -> None:
        '''
        Ignore an assert statement unless a subclass overrides this.

        :param stmt: The assert statement.
        :type stmt: Statement
        :return: None
        :rtype: None
        '''

        # Unoverridden statement kinds silently no-op.
        del stmt

    # * method: handle_del
    def handle_del(self, stmt: Statement) -> None:
        '''
        Ignore a del statement unless a subclass overrides this.

        :param stmt: The del statement.
        :type stmt: Statement
        :return: None
        :rtype: None
        '''

        # Unoverridden statement kinds silently no-op.
        del stmt

# ** class: import_group_specification
class ImportGroupSpecification(Specification):
    '''
    Require import sections to use a permitted group and contain only imports.

    The candidate is a tier-1 imports header. Other headers are skipped.
    '''

    # * attribute: valid_import_groups
    VALID_IMPORT_GROUPS: ClassVar[FrozenSet[str]] = frozenset({'core', 'infra', 'app'})

    # * method: evaluate
    def evaluate(self, candidate: Any, context: Any) -> List[Dict]:
        '''
        Evaluate import-group and import-content rules.

        :param candidate: The tier-1 header declaration.
        :type candidate: Any
        :param context: The conformance visit context.
        :type context: Any
        :return: Findings for invalid groups or non-import content.
        :rtype: List[Dict]
        '''

        # Skip unless this is the tier-1 imports header.
        header_decl = candidate
        if getattr(header_decl, 'name', None) != 'imports':
            return []
        if getattr(header_decl, 'artifact_type', None) != '***':
            return []

        # Walk artifact sections in the enclosing statement body.
        findings = []
        for section in getattr(getattr(context, 'stmt', None), 'body', None) or []:
            if not getattr(section, 'is_artifact', False) or section.decl is None:
                continue
            findings.extend(self._section_findings(section))

        # Return every section finding.
        return findings

    # * method: _section_findings
    def _section_findings(self, section: Statement) -> List[Dict]:
        '''
        Record group and content findings for one import section.

        :param section: The nested artifact section.
        :type section: Statement
        :return: Findings for this section.
        :rtype: List[Dict]
        '''

        # The section name is the header declaration name.
        section_header = section.decl
        section_name = section_header.name
        findings = []
        if section_name not in self.VALID_IMPORT_GROUPS:
            findings.append({
                'error_code': 'INVALID_IMPORT_GROUP',
                'message': (
                    f"Import group '{section_name}' must be one of: core, infra, app"
                ),
                'node': section_header,
                'group_name': section_name,
            })

        # Record at most one non-import finding, then stop scanning this section.
        for child in section.body or []:
            if child.is_import:
                continue
            kind = getattr(child, 'kind', None)
            findings.append({
                'error_code': 'INVALID_IMPORT_CONTENT',
                'message': (
                    f"Import section '{section_name}' contains non-import statements"
                ),
                'node': section_header,
                'section_name': section_name,
                'found_kind': kind.value if kind is not None else 'unknown',
            })
            break

        # Return this section's findings.
        return findings

# ** class: section_class_name_specification
class SectionClassNameSpecification(Specification):
    '''
    Require a section's class declaration to match the section name in PascalCase.

    Non-section headers, and sections with no class, are skipped.
    '''

    # * method: evaluate
    def evaluate(self, candidate: Any, context: Any) -> List[Dict]:
        '''
        Evaluate the section class-name rule.

        :param candidate: The section header declaration.
        :type candidate: Any
        :param context: The conformance visit context.
        :type context: Any
        :return: A mismatch finding, or an empty list.
        :rtype: List[Dict]
        '''

        # Skip headers that are not sections, and sections with no class.
        header_decl = candidate
        if not getattr(header_decl, 'is_section', False):
            return []
        stmt = getattr(context, 'stmt', None)
        class_decl = stmt.find_class() if stmt is not None else None
        if class_decl is None:
            return []

        # Compare the found class name with the PascalCase section name.
        header_name = header_decl.name
        expected_class_name = snake_to_pascal(header_name)
        found_class_name = class_decl.name
        if found_class_name == expected_class_name:
            return []

        # Record the mismatch against the section header.
        label = getattr(header_decl, 'section_keyword', None) or 'section'
        return [{
            'error_code': 'ARTIFACT_CLASS_NAME_MISMATCH',
            'message': (
                f"Section '{label}: {header_name}' expects class "
                f"'{expected_class_name}' but found '{found_class_name}'"
            ),
            'node': header_decl,
            'expected_class': expected_class_name,
            'actual_class': found_class_name,
        }]

# ** class: function_section_name_specification
class FunctionSectionNameSpecification(Specification):
    '''
    Require a function section's def name to match the section header name.

    Headers that are not function sections, and sections with no function, are skipped.
    '''

    # * attribute: section_keyword
    SECTION_KEYWORD: ClassVar[str] = 'function'

    # * method: evaluate
    def evaluate(self, candidate: Any, context: Any) -> List[Dict]:
        '''
        Evaluate the function-name rule.

        :param candidate: The section header declaration.
        :type candidate: Any
        :param context: The conformance visit context.
        :type context: Any
        :return: A mismatch finding, or an empty list.
        :rtype: List[Dict]
        '''

        # Skip headers that are not function or blueprint sections.
        header_decl = candidate
        if not is_function_section(header_decl):
            return []

        # Skip when the section body has no function declaration.
        func_decl = self._find_func(getattr(context, 'stmt', None))
        if func_decl is None:
            return []

        # Compare the def name with the section header name.
        header_name = header_decl.name
        if func_decl.name == header_name:
            return []

        # Record the mismatch against the section header.
        section_keyword = getattr(header_decl, 'section_keyword', None) or self.SECTION_KEYWORD
        return [{
            'error_code': 'FUNCTION_NAME_MISMATCH',
            'message': (
                f"Function section '{section_keyword}: {header_name}' expects "
                f"def '{header_name}' but found '{func_decl.name}'"
            ),
            'node': header_decl,
            'expected_function': header_name,
            'actual_function': func_decl.name,
        }]

    # * method: _find_func
    def _find_func(self, stmt: Optional[Statement]) -> Optional[Declaration]:
        '''
        Find the first function declaration in a section body.

        :param stmt: The enclosing section statement.
        :type stmt: Optional[Statement]
        :return: The function declaration, or None.
        :rtype: Optional[Declaration]
        '''

        # A missing statement has no function to compare.
        if stmt is None:
            return None

        # Return the first declaration whose type is a function.
        for child in stmt.body or []:
            if child.is_decl and child.decl is not None and child.decl.is_func:
                return child.decl

        # No function declaration was found.
        return None

# ** class: attribute_member_specification
class AttributeMemberSpecification(Specification):
    '''
    Require an attribute member to wrap a variable, not a function or nested class.

    Non-attribute members, and members with no inner declaration, are skipped.
    '''

    # * method: evaluate
    def evaluate(self, candidate: Any, context: Any) -> List[Dict]:
        '''
        Evaluate the attribute-member rules.

        :param candidate: The member header declaration.
        :type candidate: Any
        :param context: The conformance visit context.
        :type context: Any
        :return: Type or name findings, or an empty list.
        :rtype: List[Dict]
        '''

        # The context is unused; attribute checks read the member itself.
        del context

        # Skip non-attribute members and members with no inner declaration.
        decl = candidate
        if (getattr(decl, 'name', None) or '') != 'attribute':
            return []
        inner_decl = getattr(decl, 'inner_decl', None)
        if inner_decl is None:
            return []

        # Name capture is out of scope, so the name-mismatch rule does not fire yet.
        expected_name = extract_member_name_from_metadata(decl)
        findings = []
        self._append_type_finding(findings, decl, inner_decl, expected_name)
        if expected_name and inner_decl.name != expected_name:
            findings.append({
                'error_code': 'ATTRIBUTE_MEMBER_NAME_MISMATCH',
                'message': (
                    f"Attribute member expects '{expected_name}' "
                    f"but declaration is '{inner_decl.name}'"
                ),
                'node': decl,
                'expected_name': expected_name,
                'actual_name': inner_decl.name,
            })

        # Return the type and name findings.
        return findings

    # * method: _append_type_finding
    def _append_type_finding(self, findings: List[Dict], decl: Declaration,
                             inner_decl: Declaration, expected_name: Optional[str]) -> None:
        '''
        Record an invalid attribute type when the inner declaration is not a variable.

        :param findings: The finding list to extend.
        :type findings: List[Dict]
        :param decl: The member header.
        :type decl: Declaration
        :param inner_decl: The inner declaration.
        :type inner_decl: Declaration
        :param expected_name: The expected member name, or None.
        :type expected_name: Optional[str]
        :return: None
        :rtype: None
        '''

        # A missing inner type is not a function or nested class.
        inner_type = inner_decl.type
        if inner_type is None:
            return

        # A property accessor is a permitted function-shaped attribute.
        is_nested_class = inner_type.is_class and inner_decl.name == inner_type.name
        is_property_accessor = (
            inner_type.is_func and 'property' in collect_member_decorators(decl)
        )
        if not ((inner_type.is_func or is_nested_class) and not is_property_accessor):
            return

        # Record whether the illegal member is a function or a class.
        kind_label = 'function' if inner_type.is_func else 'class'
        attribute_name = expected_name or inner_decl.name
        findings.append({
            'error_code': 'INVALID_ATTRIBUTE_MEMBER_TYPE',
            'message': (
                f"Attribute member '{attribute_name}' must be a variable "
                f"declaration, not a {kind_label}"
            ),
            'node': decl,
            'attribute_name': attribute_name,
            'found_type': kind_label,
        })

# ** class: method_member_specification
class MethodMemberSpecification(Specification):
    '''
    Require a method or init member to wrap a well-formed function declaration.

    Other members, and members with no inner declaration, are skipped.
    '''

    # * attribute: validator_qualifier
    VALIDATOR_QUALIFIER: ClassVar[str] = 'validator'

    # * attribute: static_qualifier
    STATIC_QUALIFIER: ClassVar[str] = 'static'

    # * method: classify_decorators (static)
    @staticmethod
    def classify_decorators(decorators: List[str]) -> Dict[str, bool]:
        '''
        Classify encoded decorators used by method-member rules.

        :param decorators: Encoded decorator strings.
        :type decorators: List[str]
        :return: Flags for staticmethod, classmethod, and model_validator.
        :rtype: Dict[str, bool]
        '''

        # Match bare names exactly, and model_validator by its call encoding.
        return {
            'is_static': 'staticmethod' in decorators,
            'is_classmethod': 'classmethod' in decorators,
            'is_model_validator': any(
                encoded.startswith('Call(model_validator')
                for encoded in decorators
            ),
        }

    # * method: evaluate
    def evaluate(self, candidate: Any, context: Any) -> List[Dict]:
        '''
        Evaluate the method-member rules.

        :param candidate: The member header declaration.
        :type candidate: Any
        :param context: The conformance visit context.
        :type context: Any
        :return: Method-member findings, or an empty list.
        :rtype: List[Dict]
        '''

        # The context is unused; method checks read the member itself.
        del context

        # Skip members that are not method or init, and members with no inner declaration.
        decl = candidate
        if getattr(decl, 'name', None) not in ('method', 'init'):
            return []
        inner_decl = getattr(decl, 'inner_decl', None)
        if inner_decl is None:
            return []

        # A non-function inner declaration is the only finding recorded.
        expected_name = extract_member_name_from_metadata(decl)
        if not inner_decl.is_func:
            inner_type = inner_decl.type
            found_type = inner_type.kind.value if inner_type is not None else 'unknown'
            return [{
                'error_code': 'INVALID_METHOD_MEMBER_TYPE',
                'message': (
                    f"Method member '{expected_name or inner_decl.name}' "
                    f"must be a function declaration"
                ),
                'node': decl,
                'method_name': expected_name or inner_decl.name,
                'found_type': found_type,
            }]

        # Collect the remaining findings in table order.
        findings = []
        decorators = collect_member_decorators(decl)
        flags = self.classify_decorators(decorators)
        qualifier = getattr(decl, 'artifact_qualifier', None)
        self._append_name_finding(findings, decl, inner_decl, expected_name)
        self._append_receiver_findings(findings, inner_decl, flags)
        self._append_qualifier_findings(
            findings, inner_decl, qualifier, decorators, flags,
        )
        return findings

    # * method: _append_name_finding
    def _append_name_finding(self, findings: List[Dict], decl: Declaration,
                             inner_decl: Declaration, expected_name: Optional[str]) -> None:
        '''
        Record a method name mismatch when a captured name disagrees.

        :param findings: The finding list to extend.
        :type findings: List[Dict]
        :param decl: The member header.
        :type decl: Declaration
        :param inner_decl: The inner declaration.
        :type inner_decl: Declaration
        :param expected_name: The expected member name, or None.
        :type expected_name: Optional[str]
        :return: None
        :rtype: None
        '''

        # Init members, and members with no captured name, do not compare names.
        if decl.name != 'method' or not expected_name or inner_decl.name == expected_name:
            return

        # Record the mismatch against the member header.
        findings.append({
            'error_code': 'METHOD_MEMBER_NAME_MISMATCH',
            'message': (
                f"Method member expects '{expected_name}' "
                f"but declaration is '{inner_decl.name}'"
            ),
            'node': decl,
            'expected_name': expected_name,
            'actual_name': inner_decl.name,
        })

    # * method: _append_receiver_findings
    def _append_receiver_findings(self, findings: List[Dict], inner_decl: Declaration,
                                  flags: Dict[str, bool]) -> None:
        '''
        Record a missing cls or self receiver.

        :param findings: The finding list to extend.
        :type findings: List[Dict]
        :param inner_decl: The inner function declaration.
        :type inner_decl: Declaration
        :param flags: Decorator classification flags.
        :type flags: Dict[str, bool]
        :return: None
        :rtype: None
        '''

        # A staticmethod has no self or cls requirement.
        if flags['is_static']:
            return

        # Read the first parameter, which may be absent.
        params = inner_decl.type.params if inner_decl.type is not None else []
        first_param = params[0].name if params else None
        needs_cls = flags['is_classmethod'] or inner_decl.name == '__new__'
        if needs_cls and first_param not in ('cls', 'mcs'):
            findings.append({
                'error_code': 'METHOD_MISSING_CLS',
                'message': (
                    f"Classmethod '{inner_decl.name}' must have 'cls' as first parameter"
                ),
                'node': inner_decl,
                'method_name': inner_decl.name,
                'first_param': first_param,
            })
            return

        # An ordinary method must take self.
        if not needs_cls and first_param != 'self':
            findings.append({
                'error_code': 'METHOD_MISSING_SELF',
                'message': (
                    f"Method '{inner_decl.name}' must have 'self' as first parameter"
                ),
                'node': inner_decl,
                'method_name': inner_decl.name,
                'first_param': first_param,
            })

    # * method: _append_qualifier_findings
    def _append_qualifier_findings(self, findings: List[Dict], inner_decl: Declaration,
                                   qualifier: Optional[str], decorators: List[str],
                                   flags: Dict[str, bool]) -> None:
        '''
        Record validator, return-type, and static-qualifier findings.

        :param findings: The finding list to extend.
        :type findings: List[Dict]
        :param inner_decl: The inner function declaration.
        :type inner_decl: Declaration
        :param qualifier: The member qualifier, or None.
        :type qualifier: Optional[str]
        :param decorators: Encoded decorator strings.
        :type decorators: List[str]
        :param flags: Decorator classification flags.
        :type flags: Dict[str, bool]
        :return: None
        :rtype: None
        '''

        # A validator must be a classmethod model_validator that returns a value.
        ret = inner_decl.type.return_type if inner_decl.type is not None else None
        if qualifier == self.VALIDATOR_QUALIFIER:
            if not (flags['is_model_validator'] and flags['is_classmethod']):
                findings.append({
                    'error_code': 'INVALID_VALIDATOR_MEMBER',
                    'message': (
                        f"Validator method '{inner_decl.name}' must be decorated "
                        f"with @model_validator and @classmethod"
                    ),
                    'node': inner_decl,
                    'method_name': inner_decl.name,
                    'decorators': decorators,
                })
            if ret is not None and ret.kind.value == 'None':
                findings.append({
                    'error_code': 'VALIDATOR_MISSING_RETURN',
                    'message': (
                        f"Validator method '{inner_decl.name}' must return a value"
                    ),
                    'node': inner_decl,
                    'method_name': inner_decl.name,
                })

        # A present return type must be a valid return kind.
        if ret is not None and not ret.is_valid_return_type:
            findings.append({
                'error_code': 'INVALID_METHOD_RETURN_TYPE',
                'message': (
                    f"Method '{inner_decl.name}' has invalid return type '{ret.kind.value}'"
                ),
                'node': inner_decl,
                'method_name': inner_decl.name,
                'return_type': ret.kind.value,
            })

        # The static qualifier and the staticmethod decorator must agree.
        if qualifier == self.STATIC_QUALIFIER and not flags['is_static']:
            findings.append({
                'error_code': 'INVALID_STATIC_MEMBER',
                'message': (
                    f"Method '{inner_decl.name}' labelled (static) "
                    f"must be decorated @staticmethod"
                ),
                'node': inner_decl,
                'method_name': inner_decl.name,
                'decorators': decorators,
            })
        if flags['is_static'] and qualifier != self.STATIC_QUALIFIER:
            findings.append({
                'error_code': 'STATIC_MEMBER_MISSING_QUALIFIER',
                'message': (
                    f"Method '{inner_decl.name}' decorated @staticmethod "
                    f"must be labelled (static)"
                ),
                'node': inner_decl,
                'method_name': inner_decl.name,
            })

# ** class: assignment_type_specification
class AssignmentTypeSpecification(Specification):
    '''
    Require an assignment's value type to be compatible with the target's declared type.

    Non-assignments, and assignments whose types cannot be resolved, are skipped.
    '''

    # * method: evaluate
    def evaluate(self, candidate: Any, context: Any) -> List[Dict]:
        '''
        Evaluate the assignment type rule.

        :param candidate: The assignment expression.
        :type candidate: Any
        :param context: The conformance visit context.
        :type context: Any
        :return: A mismatch finding, or an empty list.
        :rtype: List[Dict]
        '''

        # Skip expressions that are not assignments with both sides present.
        expr = candidate
        if not getattr(expr, 'is_assignment', False):
            return []
        if expr.left is None or expr.right is None:
            return []

        # Skip when either type cannot be resolved.
        target_type = context.lookup_type(expr.left)
        value_type = context.infer_type(expr.right)
        if not target_type or not value_type:
            return []
        if context.types_compatible(target_type, value_type):
            return []

        # Record the incompatible assignment.
        return [{
            'error_code': 'TYPE_MISMATCH_ASSIGNMENT',
            'message': (
                f'Cannot assign {value_type} to variable declared as {target_type}'
            ),
            'node': expr,
            'expected_type': target_type,
            'actual_type': value_type,
            'target_name': expr.left.name or '',
        }]

# ** class: binary_op_type_specification
class BinaryOpTypeSpecification(Specification):
    '''
    Require a binary expression to use a supported operand pair.

    The intended visit hook is ``expression``.
    '''

    # * method: evaluate
    def evaluate(self, candidate: Any, context: Any) -> List[Dict]:
        '''
        Evaluate the binary-operation type rule.

        :param candidate: The expression.
        :type candidate: Any
        :param context: The conformance visit context.
        :type context: Any
        :return: A mismatch finding, or an empty list.
        :rtype: List[Dict]
        '''

        # Delegate to the shared binary-operation findings.
        return _binary_op_findings(candidate, context)

# ** class: return_binary_op_type_specification
class ReturnBinaryOpTypeSpecification(Specification):
    '''
    Require a returned binary expression to use a supported operand pair.

    The intended visit hook is ``return``. The candidate is a statement.
    '''

    # * method: evaluate
    def evaluate(self, candidate: Any, context: Any) -> List[Dict]:
        '''
        Evaluate the returned binary-operation type rule.

        :param candidate: The return statement.
        :type candidate: Any
        :param context: The conformance visit context.
        :type context: Any
        :return: A mismatch finding, or an empty list.
        :rtype: List[Dict]
        '''

        # The candidate is a statement; the checked expression is its expr.
        expr = getattr(candidate, 'expr', None)
        return _binary_op_findings(expr, context)

# ** class: permitted_group_specification
class PermittedGroupSpecification(Specification):
    '''
    Permit only a fixed set of tier-1 groups in one component module.

    The permitted names are constructor data. The class does not hard-code an actor dialect.
    '''

    # * attribute: permitted_groups
    permitted_groups: FrozenSet[str] = Field(
        default_factory=lambda: frozenset({
            'imports',
            'constants',
            'functions',
            'classes',
            'exports',
        }),
        description='Permitted tier-1 group names, or the assets default.',
    )

    # * attribute: error_code
    error_code: str = Field(
        'DISALLOWED_ASSET_GROUP',
        description='The finding code for a disallowed group.',
    )

    # * attribute: module_label
    module_label: str = Field(
        'an assets module',
        description='The module kind inserted in the finding message.',
    )

    # * method: evaluate
    def evaluate(self, candidate: Declaration,
                 context: ConformanceContext) -> List[Dict]:
        '''
        Evaluate the permitted-group rule.

        :param candidate: The artifact header declaration.
        :type candidate: Declaration
        :param context: The conformance visit context.
        :type context: ConformanceContext
        :return: A disallowed-group finding, or an empty list.
        :rtype: List[Dict]
        '''

        # Only tier-1 groups are judged.
        header_decl = candidate
        if getattr(header_decl, 'artifact_type', None) != '***':
            return []

        # A permitted name is satisfactory.
        header_name = getattr(header_decl, 'name', None)
        if header_name in self.permitted_groups:
            return []

        # Record the group this module does not permit.
        permitted = ', '.join(sorted(self.permitted_groups))
        return [{
            'error_code': self.error_code,
            'message': (
                f"Group '{header_name}' is not permitted in {self.module_label}. "
                f"Permitted groups are: {permitted}."
            ),
            'node': header_decl,
            'group_name': header_name,
        }]

# ** class: app_import_specification
class AppImportSpecification(Specification):
    '''
    Permit only constructor-listed component types in an app import group.

    Same-package siblings are allowed unless the constructor turns that off.
    Events do not instantiate this rule.
    '''

    # * attribute: allowed_components
    allowed_components: FrozenSet[str] = Field(
        default_factory=frozenset,
        description='Component types permitted besides siblings.',
    )

    # * attribute: error_code
    error_code: str = Field(
        ...,
        description='The finding code for a disallowed import.',
    )

    # * attribute: message
    message: str = Field(
        ...,
        description='The finding template. It may contain ``{module_path}``.',
    )

    # * attribute: allow_siblings
    allow_siblings: bool = Field(
        True,
        description='Whether a single-dot relative import is allowed.',
    )

    # * attribute: allow_framework_root_alias
    allow_framework_root_alias: bool = Field(
        False,
        description='Whether ``from .. import a`` is allowed.',
    )

    # * method: evaluate
    def evaluate(self, candidate: Declaration,
                 context: ConformanceContext) -> List[Dict]:
        '''
        Evaluate app imports under an imports group.

        :param candidate: The artifact header declaration.
        :type candidate: Declaration
        :param context: The conformance visit context.
        :type context: ConformanceContext
        :return: One finding per disallowed app import.
        :rtype: List[Dict]
        '''

        # Only the imports group has an app import sub-group to judge.
        header_decl = candidate
        if getattr(header_decl, 'artifact_type', None) != '***':
            return []
        if getattr(header_decl, 'name', None) != 'imports':
            return []

        # Walk each app section and record every disallowed import.
        findings = []
        stmt = getattr(context, 'stmt', None)
        for section in (stmt.body if stmt is not None else None) or []:
            if not self._is_app_section(section):
                continue
            for sub in section.body or []:
                finding = self._import_finding(sub)
                if finding is not None:
                    findings.append(finding)

        # Return every disallowed app import.
        return findings

    # * method: _is_app_section
    def _is_app_section(self, section: Statement) -> bool:
        '''
        Report whether a statement is the app import section.

        :param section: A statement in the imports group.
        :type section: Statement
        :return: True when the statement is an artifact section named app.
        :rtype: bool
        '''

        # Only an artifact section named app is judged.
        return (
            getattr(section, 'is_artifact', False)
            and section.decl is not None
            and section.decl.name == 'app'
        )

    # * method: _import_finding
    def _import_finding(self, sub: Statement) -> Optional[Dict]:
        '''
        Record a finding for one disallowed import, or skip it.

        :param sub: A statement in the app section.
        :type sub: Statement
        :return: A finding, or None when the statement is allowed or not an import.
        :rtype: Optional[Dict]
        '''

        # Import-from keeps the module on init_expr. A plain import keeps it on expr.
        if getattr(sub, 'is_import_from', False):
            module_path = getattr(sub.init_expr, 'name', None) or ''
        elif getattr(sub, 'is_import', False):
            module_path = getattr(sub.expr, 'name', None) or ''
        else:
            return None
        if self._is_allowed(module_path, sub):
            return None

        # Record the path this dialect does not permit.
        return {
            'error_code': self.error_code,
            'message': self.message.format(module_path=module_path),
            'node': sub,
            'module_path': module_path,
        }

    # * method: _is_allowed
    def _is_allowed(self, module_path: str, sub: Statement) -> bool:
        '''
        Report whether an app import path is allowed.

        :param module_path: The imported module path.
        :type module_path: str
        :param sub: The import statement.
        :type sub: Statement
        :return: True when any allowance matches.
        :rtype: bool
        '''

        # A single leading dot is a same-package sibling, not a parent import.
        if (
            self.allow_siblings
            and module_path.startswith('.')
            and not module_path.startswith('..')
        ):
            return True

        # A listed component may be the path, a prefix, or a dotted segment.
        if any(
            module_path == component
            or module_path.startswith(f'{component}.')
            or f'.{component}' in module_path
            for component in self.allowed_components
        ):
            return True

        # The framework root alias is the parent import of ``a`` only.
        return (
            self.allow_framework_root_alias
            and module_path == '..'
            and getattr(sub.expr, 'name', None) == 'a'
        )

# ** class: required_base_specification
class RequiredBaseSpecification(Specification):
    '''
    Require a typed section's class to declare an acceptable base.

    When no required base is given, any declared base satisfies the rule.
    A predicate that returns false skips the section.
    '''

    # * attribute: section_keyword
    section_keyword: str = Field(
        ...,
        description='The section keyword this rule judges.',
    )

    # * attribute: error_code
    error_code: str = Field(
        ...,
        description='The finding code for a missing or wrong base.',
    )

    # * attribute: message
    message: str = Field(
        ...,
        description='The finding template.',
    )

    # * attribute: name_key
    name_key: Optional[str] = Field(
        None,
        description='Optional extra finding key for the header name.',
    )

    # * attribute: required_base
    required_base: Optional[str] = Field(
        None,
        description='The required base name, or None when any base satisfies.',
    )

    # * attribute: predicate
    predicate: Optional[Callable[..., bool]] = Field(
        None,
        description='Optional skip predicate. False skips the rule.',
    )

    # * method: evaluate
    def evaluate(self, candidate: Declaration,
                 context: ConformanceContext) -> List[Dict]:
        '''
        Evaluate the required-base rule.

        :param candidate: The section header declaration.
        :type candidate: Declaration
        :param context: The conformance visit context.
        :type context: ConformanceContext
        :return: A missing-base finding, or an empty list.
        :rtype: List[Dict]
        '''

        # Skip headers that are not this section keyword.
        header_decl = candidate
        if getattr(header_decl, 'section_keyword', None) != self.section_keyword:
            return []

        # Skip when the section has no class declaration.
        stmt = getattr(context, 'stmt', None)
        class_decl = stmt.find_class() if stmt is not None else None
        if class_decl is None:
            return []

        # A false predicate skips the rule for this class.
        if self.predicate is not None and not self.predicate(
            header_decl,
            context,
            class_decl,
        ):
            return []

        # Any declared base satisfies when no specific base is required.
        base = class_decl.type.subtype if class_decl.type else None
        if self.required_base is None and base is not None:
            return []
        if (
            self.required_base is not None
            and base is not None
            and base.name == self.required_base
        ):
            return []

        # Record the missing or unacceptable base against the section header.
        finding = {
            'error_code': self.error_code,
            'message': self.message.format(
                header_name=header_decl.name,
                class_name=class_decl.name,
                required_base=self.required_base,
            ),
            'node': header_decl,
            'class_name': class_decl.name,
        }
        if self.name_key is not None:
            finding[self.name_key] = header_decl.name
        return [finding]

# ** class: event_section_specification
class EventSectionSpecification(Specification):
    '''
    Require an event section's class to declare an execute method.

    Non-event headers, and event sections with no class, are skipped.
    '''

    # * attribute: section_keyword
    SECTION_KEYWORD: ClassVar[str] = 'event'

    # * method: evaluate
    def evaluate(self, candidate: Any, context: Any) -> List[Dict]:
        '''
        Evaluate the event execute-method rule.

        :param candidate: The section header declaration.
        :type candidate: Any
        :param context: The conformance visit context.
        :type context: Any
        :return: A missing-execute finding, or an empty list.
        :rtype: List[Dict]
        '''

        # Skip headers that are not event sections.
        header_decl = candidate
        if getattr(header_decl, 'section_keyword', None) != self.SECTION_KEYWORD:
            return []

        # Skip when the section has no class declaration.
        stmt = getattr(context, 'stmt', None)
        class_decl = stmt.find_class() if stmt is not None else None
        if class_decl is None:
            return []
        if class_decl.has_method('execute'):
            return []

        # Record the missing execute method.
        return [{
            'error_code': 'EVENT_MISSING_EXECUTE',
            'message': (
                f"Event '{header_decl.name}' class '{class_decl.name}' "
                f"must declare an 'execute' method"
            ),
            'node': header_decl,
            'event_name': header_decl.name,
            'class_name': class_decl.name,
        }]

# ** class: group_section_agreement_specification
class GroupSectionAgreementSpecification(Specification):
    '''
    Require nested sections to use the keyword expected by their tier-1 group.

    Headers that are not a known tier-1 group are skipped.
    '''

    # * attribute: group_section_keywords
    GROUP_SECTION_KEYWORDS: ClassVar[Dict[str, str]] = {
        'constants': 'constant',
        'functions': 'function',
        'classes': 'class',
        'models': 'model',
        'mappers': 'mapper',
        'blueprints': 'blueprint',
    }

    # * method: evaluate
    def evaluate(self, candidate: Any, context: Any) -> List[Dict]:
        '''
        Evaluate the group and section keyword agreement.

        :param candidate: The tier-1 header declaration.
        :type candidate: Any
        :param context: The conformance visit context.
        :type context: Any
        :return: Mismatch findings for nested sections.
        :rtype: List[Dict]
        '''

        # Skip headers that are not a known tier-1 group.
        header_decl = candidate
        if getattr(header_decl, 'artifact_type', None) != '***':
            return []
        header_name = getattr(header_decl, 'name', None)
        expected_keyword = self.GROUP_SECTION_KEYWORDS.get(header_name)
        if expected_keyword is None:
            return []

        # Compare each nested artifact section with the expected keyword.
        findings = []
        stmt = getattr(context, 'stmt', None)
        for child in (stmt.body if stmt is not None else None) or []:
            finding = self._child_finding(child, header_name, expected_keyword)
            if finding is not None:
                findings.append(finding)

        # Return every mismatched section.
        return findings

    # * method: _child_finding
    def _child_finding(self, child: Statement, header_name: str,
                       expected_keyword: str) -> Optional[Dict]:
        '''
        Record a mismatch for one nested section, or skip it.

        :param child: A statement in the group body.
        :type child: Statement
        :param header_name: The tier-1 group name.
        :type header_name: str
        :param expected_keyword: The keyword that group permits.
        :type expected_keyword: str
        :return: A mismatch finding, or None when the child is skipped or agrees.
        :rtype: Optional[Dict]
        '''

        # Only artifact sections participate.
        if not getattr(child, 'is_artifact', False) or child.decl is None:
            return None
        section_header = child.decl
        if is_function_section(section_header):
            actual_keyword = getattr(section_header, 'section_keyword', None) or 'function'
        elif getattr(section_header, 'is_section', False):
            actual_keyword = section_header.section_keyword
        else:
            return None
        if actual_keyword == expected_keyword:
            return None

        # Record the keyword the group does not permit.
        return {
            'error_code': 'SECTION_GROUP_MISMATCH',
            'message': (
                f"Section '{actual_keyword}: {section_header.name}' is not permitted "
                f"under the '{header_name}' group; expected '{expected_keyword}' sections."
            ),
            'node': section_header,
            'group_name': header_name,
            'expected_keyword': expected_keyword,
            'actual_keyword': actual_keyword,
        }

# ** class: constant_section_name_specification
class ConstantSectionNameSpecification(Specification):
    '''
    Require a constant section's assignment target to be the uppercased section name.

    Non-constant headers, and sections with no inner declaration, are skipped.
    '''

    # * attribute: section_keyword
    SECTION_KEYWORD: ClassVar[str] = 'constant'

    # * method: evaluate
    def evaluate(self, candidate: Any, context: Any) -> List[Dict]:
        '''
        Evaluate the constant-name rule.

        :param candidate: The section header declaration.
        :type candidate: Any
        :param context: The conformance visit context.
        :type context: Any
        :return: A mismatch finding, or an empty list.
        :rtype: List[Dict]
        '''

        # Skip headers that are not constant sections.
        header_decl = candidate
        if getattr(header_decl, 'section_keyword', None) != self.SECTION_KEYWORD:
            return []

        # Skip when the section body has no declaration.
        const_decl = self._find_decl(getattr(context, 'stmt', None))
        if const_decl is None:
            return []

        # Compare the assignment target with the uppercased section name.
        expected_name = header_decl.name.upper()
        if const_decl.name == expected_name:
            return []

        # Record the mismatch against the section header.
        return [{
            'error_code': 'ASSET_CONSTANT_NAME_MISMATCH',
            'message': (
                f"Constant section 'constant: {header_decl.name}' expects "
                f"assignment target '{expected_name}' but found '{const_decl.name}'"
            ),
            'node': header_decl,
            'expected_name': expected_name,
            'actual_name': const_decl.name,
        }]

    # * method: _find_decl
    def _find_decl(self, stmt: Optional[Statement]) -> Optional[Declaration]:
        '''
        Find the first declaration in a section body.

        :param stmt: The enclosing section statement.
        :type stmt: Optional[Statement]
        :return: The declaration, or None.
        :rtype: Optional[Declaration]
        '''

        # A missing statement has no declaration to compare.
        if stmt is None:
            return None

        # Return the first nested declaration.
        for child in stmt.body or []:
            if child.is_decl and child.decl is not None:
                return child.decl

        # No declaration was found.
        return None

# ** class: domain_attribute_specification
class DomainAttributeSpecification(Specification):
    '''
    Require a model attribute to be typed and initialized with Field(description=...).

    Attributes outside the models group, private names, and ClassVar attributes are skipped.
    '''

    # * attribute: field_callee
    FIELD_CALLEE: ClassVar[str] = 'Field'

    # * attribute: description_kwarg
    DESCRIPTION_KWARG: ClassVar[str] = 'description'

    # * method: evaluate
    def evaluate(self, candidate: Any, context: Any) -> List[Dict]:
        '''
        Evaluate the domain-attribute rules.

        :param candidate: The member header declaration.
        :type candidate: Any
        :param context: The conformance visit context.
        :type context: Any
        :return: Missing-type, Field, or description findings.
        :rtype: List[Dict]
        '''

        # Skip unless this is a models-group attribute with an inner declaration.
        decl = candidate
        if getattr(context, 'group_name', None) != 'models':
            return []
        if (getattr(decl, 'name', None) or '') != 'attribute':
            return []
        inner_decl = getattr(decl, 'inner_decl', None)
        if inner_decl is None:
            return []
        if inner_decl.name.startswith('_'):
            return []
        if inner_decl.type is not None and inner_decl.type.name == 'ClassVar':
            return []

        # Record each missing domain-attribute requirement.
        findings = []
        if inner_decl.type is None:
            findings.append(self._finding(
                'DOMAIN_ATTRIBUTE_MISSING_TYPE',
                f"Attribute '{inner_decl.name}' must be typed",
                inner_decl,
            ))
        if not self._is_field_call(inner_decl.value):
            findings.append(self._finding(
                'DOMAIN_ATTRIBUTE_MISSING_FIELD',
                f"Attribute '{inner_decl.name}' must be initialized with Field(...)",
                inner_decl,
            ))
        elif not self._has_description(inner_decl.value):
            findings.append(self._finding(
                'DOMAIN_ATTRIBUTE_MISSING_DESCRIPTION',
                (
                    f"Attribute '{inner_decl.name}' Field(...) call must carry "
                    f"a description keyword argument"
                ),
                inner_decl,
            ))

        # Return the recorded requirements.
        return findings

    # * method: _finding
    def _finding(self, error_code: str, message: str, node: Declaration) -> Dict:
        '''
        Build a domain-attribute finding.

        :param error_code: The finding code.
        :type error_code: str
        :param message: The finding message.
        :type message: str
        :param node: The inner declaration.
        :type node: Declaration
        :return: The finding dict.
        :rtype: Dict
        '''

        # Every domain-attribute finding cites the inner declaration.
        return {
            'error_code': error_code,
            'message': message,
            'node': node,
            'attribute_name': node.name,
        }

    # * method: _is_field_call
    def _is_field_call(self, value: Optional[Expression]) -> bool:
        '''
        Report whether an initializer is a Field call.

        :param value: The initializer expression.
        :type value: Optional[Expression]
        :return: True when the initializer calls Field.
        :rtype: bool
        '''

        # A Field initializer is a call whose callee is named Field.
        return (
            value is not None
            and value.kind == ExprKind.CALL
            and value.left is not None
            and value.left.name == self.FIELD_CALLEE
        )

    # * method: _has_description
    def _has_description(self, value: Expression) -> bool:
        '''
        Report whether a Field call carries a description keyword.

        :param value: The Field call.
        :type value: Expression
        :return: True when a description keyword argument is present.
        :rtype: bool
        '''

        # A call with no argument list has no description keyword.
        if value.right is None:
            return False

        # Search the flattened arguments for the description keyword.
        for arg in value.right.flatten_call_args():
            if arg.kind == ExprKind.KWARG and arg.name == self.DESCRIPTION_KWARG:
                return True

        # No description keyword was found.
        return False

# ** class: mapper_roles_attribute_specification
class MapperRolesAttributeSpecification(Specification):
    '''
    Require a mapper ``_ROLES`` attribute to be a ClassVar dict literal.

    Other attributes, and attributes outside the mappers group, are skipped.
    '''

    # * attribute: roles_attribute_name
    ROLES_ATTRIBUTE_NAME: ClassVar[str] = '_ROLES'

    # * attribute: expected_type_name
    EXPECTED_TYPE_NAME: ClassVar[str] = 'ClassVar'

    # * method: evaluate
    def evaluate(self, candidate: Any, context: Any) -> List[Dict]:
        '''
        Evaluate the mapper ``_ROLES`` rules.

        :param candidate: The member header declaration.
        :type candidate: Any
        :param context: The conformance visit context.
        :type context: Any
        :return: ClassVar or dict-literal findings, or an empty list.
        :rtype: List[Dict]
        '''

        # Skip unless this is the mappers-group _ROLES attribute.
        decl = candidate
        if getattr(context, 'group_name', None) != 'mappers':
            return []
        if (getattr(decl, 'name', None) or '') != 'attribute':
            return []
        inner_decl = getattr(decl, 'inner_decl', None)
        if inner_decl is None or inner_decl.name != self.ROLES_ATTRIBUTE_NAME:
            return []

        # Record a missing ClassVar type and a missing dict literal independently.
        findings = []
        type_name = inner_decl.type.name if inner_decl.type is not None else None
        if type_name != self.EXPECTED_TYPE_NAME:
            findings.append({
                'error_code': 'MAPPER_ROLES_MISSING_CLASSVAR_TYPE',
                'message': "'_ROLES' must be typed ClassVar[Dict[str, Dict[str, Any]]]",
                'node': inner_decl,
            })
        if inner_decl.value is None or inner_decl.value.kind != ExprKind.DICT_LITERAL:
            findings.append({
                'error_code': 'MAPPER_ROLES_MISSING_DICT_LITERAL',
                'message': "'_ROLES' must be initialized with a dict literal",
                'node': inner_decl,
            })

        # Return the recorded requirements.
        return findings

# ** class: interface_abstract_method_specification
class InterfaceAbstractMethodSpecification(Specification):
    '''
    Require interface methods to be abstract and raise NotImplementedError.

    The root ABC marker class is skipped. The intended visit hook is ``artifact_header``.
    '''

    # * attribute: section_keyword
    SECTION_KEYWORD: ClassVar[str] = 'interface'

    # * attribute: root_base
    ROOT_BASE: ClassVar[str] = 'ABC'

    # * attribute: not_implemented_callee
    NOT_IMPLEMENTED_CALLEE: ClassVar[str] = 'NotImplementedError'

    # * method: evaluate
    def evaluate(self, candidate: Any, context: Any) -> List[Dict]:
        '''
        Evaluate the interface abstract-method rules.

        :param candidate: The section header declaration.
        :type candidate: Any
        :param context: The conformance visit context.
        :type context: Any
        :return: Abstract-method findings, or an empty list.
        :rtype: List[Dict]
        '''

        # Skip headers that are not interface sections, and sections with no class.
        header_decl = candidate
        if getattr(header_decl, 'section_keyword', None) != self.SECTION_KEYWORD:
            return []
        class_decl = self._find_class(context)
        if class_decl is None or self._is_root_marker(class_decl):
            return []

        # Check every method member for the abstract decorator and the raise body.
        findings = []
        for member, inner in self._method_members(class_decl):
            decorators = collect_member_decorators(member)
            if 'abstractmethod' not in decorators:
                findings.append({
                    'error_code': 'INTERFACE_METHOD_MISSING_ABSTRACTMETHOD',
                    'message': (
                        f"Interface method '{inner.name}' must be decorated @abstractmethod"
                    ),
                    'node': inner,
                    'method_name': inner.name,
                })
            if not _has_not_implemented_body(inner, callee_name=self.NOT_IMPLEMENTED_CALLEE):
                findings.append({
                    'error_code': 'INTERFACE_METHOD_MISSING_NOT_IMPLEMENTED',
                    'message': (
                        f"Interface method '{inner.name}' body must be exactly "
                        f"`raise NotImplementedError(...)`"
                    ),
                    'node': inner,
                    'method_name': inner.name,
                })

        # Return the method findings.
        return findings

    # * method: _find_class
    def _find_class(self, context: Any) -> Optional[Declaration]:
        '''
        Find the class declaration in the enclosing statement.

        :param context: The conformance visit context.
        :type context: Any
        :return: The class declaration, or None.
        :rtype: Optional[Declaration]
        '''

        # A missing statement has no class.
        stmt = getattr(context, 'stmt', None)
        if stmt is None:
            return None

        # Return the class, ignoring class-typed variables.
        return stmt.find_class()

    # * method: _is_root_marker
    def _is_root_marker(self, class_decl: Declaration) -> bool:
        '''
        Report whether a class is the sole-base ABC root marker.

        :param class_decl: The class declaration.
        :type class_decl: Declaration
        :return: True when the sole base is ABC with no further subtype.
        :rtype: bool
        '''

        # The base chain lives on the class type's subtype.
        type_obj = class_decl.type
        base = type_obj.subtype if type_obj is not None else None
        return (
            base is not None
            and base.name == self.ROOT_BASE
            and base.subtype is None
        )

    # * method: _method_members
    def _method_members(self, class_decl: Declaration) -> List[tuple]:
        '''
        List method members and their inner declarations.

        :param class_decl: The class declaration.
        :type class_decl: Declaration
        :return: Pairs of member header and inner declaration.
        :rtype: List[tuple]
        '''

        # Keep method and init members that wrap an inner declaration.
        found = []
        for member in getattr(class_decl, 'members', []):
            role = getattr(member, 'artifact_role', None) or member.name
            if role not in ('method', 'init'):
                continue
            inner = member.inner_decl
            if inner is not None:
                found.append((member, inner))

        # Return the method members.
        return found

# ** class: di_abstract_method_specification
class DIAbstractMethodSpecification(Specification):
    '''
    Require an already-abstract DI method to raise NotImplementedError.

    Undecorated methods are not checked. Non-class headers are skipped.
    '''

    # * attribute: section_keyword
    SECTION_KEYWORD: ClassVar[str] = 'class'

    # * attribute: not_implemented_callee
    NOT_IMPLEMENTED_CALLEE: ClassVar[str] = 'NotImplementedError'

    # * method: evaluate
    def evaluate(self, candidate: Any, context: Any) -> List[Dict]:
        '''
        Evaluate the DI abstract-method body rule.

        :param candidate: The section header declaration.
        :type candidate: Any
        :param context: The conformance visit context.
        :type context: Any
        :return: Missing-body findings, or an empty list.
        :rtype: List[Dict]
        '''

        # Skip headers that are not class sections, and sections with no class.
        header_decl = candidate
        if getattr(header_decl, 'section_keyword', None) != self.SECTION_KEYWORD:
            return []
        stmt = getattr(context, 'stmt', None)
        class_decl = stmt.find_class() if stmt is not None else None
        if class_decl is None:
            return []

        # Only methods already decorated abstractmethod are checked.
        findings = []
        for member in getattr(class_decl, 'members', []):
            role = getattr(member, 'artifact_role', None) or member.name
            if role not in ('method', 'init'):
                continue
            inner = member.inner_decl
            if inner is None:
                continue
            if 'abstractmethod' not in collect_member_decorators(member):
                continue
            if _has_not_implemented_body(inner, callee_name=self.NOT_IMPLEMENTED_CALLEE):
                continue
            findings.append({
                'error_code': 'DI_ABSTRACT_METHOD_MISSING_NOT_IMPLEMENTED',
                'message': (
                    f"DI method '{inner.name}' decorated @abstractmethod must have "
                    f"a body of exactly `raise NotImplementedError(...)`"
                ),
                'node': inner,
                'method_name': inner.name,
            })

        # Return the abstract-method findings.
        return findings

# ** class: context_manager_pairing_specification
class ContextManagerPairingSpecification(Specification):
    '''
    Require a util class's context-manager methods to be a paired enter and exit.

    Non-util headers, and util sections with no class, are skipped.
    '''

    # * attribute: section_keyword
    SECTION_KEYWORD: ClassVar[str] = 'util'

    # * attribute: context_manager_qualifier
    CONTEXT_MANAGER_QUALIFIER: ClassVar[str] = 'context manager'

    # * attribute: enter_name
    ENTER_NAME: ClassVar[str] = '__enter__'

    # * attribute: exit_name
    EXIT_NAME: ClassVar[str] = '__exit__'

    # * attribute: exit_param_count
    EXIT_PARAM_COUNT: ClassVar[int] = 4

    # * method: evaluate
    def evaluate(self, candidate: Any, context: Any) -> List[Dict]:
        '''
        Evaluate the context-manager pairing rules.

        :param candidate: The section header declaration.
        :type candidate: Any
        :param context: The conformance visit context.
        :type context: Any
        :return: Pairing and signature findings, or an empty list.
        :rtype: List[Dict]
        '''

        # Skip headers that are not util sections, and sections with no class.
        header_decl = candidate
        if getattr(header_decl, 'section_keyword', None) != self.SECTION_KEYWORD:
            return []
        stmt = getattr(context, 'stmt', None)
        class_decl = stmt.find_class() if stmt is not None else None
        if class_decl is None:
            return []

        # Inspect only method members labelled as context managers.
        findings = []
        qualified_names = set()
        for member in getattr(class_decl, 'members', []):
            if getattr(member, 'artifact_qualifier', None) != self.CONTEXT_MANAGER_QUALIFIER:
                continue
            role = getattr(member, 'artifact_role', None) or member.name
            if role not in ('method', 'init'):
                continue
            inner = member.inner_decl
            if inner is None:
                continue
            qualified_names.add(inner.name)
            findings.extend(self._member_findings(inner))

        # Exactly one of the pair is a missing partner.
        findings.extend(self._pair_findings(header_decl, class_decl, qualified_names))
        return findings

    # * method: _member_findings
    def _member_findings(self, inner: Declaration) -> List[Dict]:
        '''
        Record name and exit-signature findings for one qualified method.

        :param inner: The inner method declaration.
        :type inner: Declaration
        :return: Findings for this method.
        :rtype: List[Dict]
        '''

        # A qualified method must be enter or exit.
        findings = []
        if inner.name not in {self.ENTER_NAME, self.EXIT_NAME}:
            findings.append({
                'error_code': 'INVALID_CONTEXT_MANAGER_MEMBER',
                'message': (
                    f"Method '{inner.name}' labelled (context manager) "
                    f"must be '__enter__' or '__exit__'"
                ),
                'node': inner,
                'method_name': inner.name,
            })

        # Exit must take self plus the three exception-info parameters.
        if inner.name == self.EXIT_NAME:
            param_count = len(inner.type.params) if inner.type is not None else 0
            if param_count != self.EXIT_PARAM_COUNT:
                findings.append({
                    'error_code': 'INVALID_CONTEXT_MANAGER_EXIT_SIGNATURE',
                    'message': (
                        "'__exit__' must take self plus the three "
                        "standard exception-info parameters"
                    ),
                    'node': inner,
                    'method_name': inner.name,
                    'param_count': param_count,
                })

        # Return this method's findings.
        return findings

    # * method: _pair_findings
    def _pair_findings(self, header_decl: Declaration, class_decl: Declaration,
                       qualified_names: set) -> List[Dict]:
        '''
        Record a missing partner when exactly one of enter or exit is qualified.

        :param header_decl: The section header.
        :type header_decl: Declaration
        :param class_decl: The class declaration.
        :type class_decl: Declaration
        :param qualified_names: Names labelled as context managers.
        :type qualified_names: set
        :return: A pairing finding, or an empty list.
        :rtype: List[Dict]
        '''

        # Both present, or neither present, is not a missing pair.
        enter_present = self.ENTER_NAME in qualified_names
        exit_present = self.EXIT_NAME in qualified_names
        if enter_present == exit_present:
            return []

        # Name the present method and the missing partner.
        present = self.ENTER_NAME if enter_present else self.EXIT_NAME
        missing = self.EXIT_NAME if enter_present else self.ENTER_NAME
        return [{
            'error_code': 'CONTEXT_MANAGER_MISSING_PAIR',
            'message': (
                f"'{present}' is labelled (context manager) but no matching "
                f"'{missing}' was found in the same class"
            ),
            'node': header_decl,
            'class_name': class_decl.name,
        }]

# ** class: repos_crud_method_specification
class ReposCrudMethodSpecification(Specification):
    '''
    Require a repo class to declare exactly the repos CRUD vocabulary.

    Non-repo headers, and repo sections with no class, are skipped.
    '''

    # * attribute: section_keyword
    SECTION_KEYWORD: ClassVar[str] = 'repo'

    # * attribute: crud_methods
    CRUD_METHODS: ClassVar[FrozenSet[str]] = frozenset({'exists', 'get', 'list', 'save', 'delete'})

    # * method: evaluate
    def evaluate(self, candidate: Any, context: Any) -> List[Dict]:
        '''
        Evaluate the repos CRUD vocabulary.

        :param candidate: The section header declaration.
        :type candidate: Any
        :param context: The conformance visit context.
        :type context: Any
        :return: Missing and unexpected method findings, in sorted order.
        :rtype: List[Dict]
        '''

        # Skip headers that are not repo sections, and sections with no class.
        header_decl = candidate
        if getattr(header_decl, 'section_keyword', None) != self.SECTION_KEYWORD:
            return []
        stmt = getattr(context, 'stmt', None)
        class_decl = stmt.find_class() if stmt is not None else None
        if class_decl is None:
            return []

        # Public methods are method members whose names do not start with an underscore.
        public_names = set()
        for member in getattr(class_decl, 'members', []):
            role = getattr(member, 'artifact_role', None) or member.name
            if role not in ('method', 'init'):
                continue
            inner = member.inner_decl
            if inner is None or inner.name.startswith('_'):
                continue
            public_names.add(inner.name)

        # Report missing names, then extra names, each in sorted order.
        findings = []
        for missing in sorted(self.CRUD_METHODS - public_names):
            findings.append(self._finding(
                'REPO_MISSING_CRUD_METHOD',
                (
                    f"Repo '{header_decl.name}' class '{class_decl.name}' "
                    f"is missing required method '{missing}'"
                ),
                header_decl,
                class_decl,
                missing,
            ))
        for extra in sorted(public_names - self.CRUD_METHODS):
            findings.append(self._finding(
                'REPO_UNEXPECTED_PUBLIC_METHOD',
                (
                    f"Repo '{header_decl.name}' class '{class_decl.name}' "
                    f"declares public method '{extra}', which is not part of "
                    f"the repos CRUD vocabulary"
                ),
                header_decl,
                class_decl,
                extra,
            ))
        return findings

    # * method: _finding
    def _finding(self, error_code: str, message: str, header_decl: Declaration,
                 class_decl: Declaration, method_name: str) -> Dict:
        '''
        Build a repos CRUD finding.

        :param error_code: The finding code.
        :type error_code: str
        :param message: The finding message.
        :type message: str
        :param header_decl: The section header.
        :type header_decl: Declaration
        :param class_decl: The class declaration.
        :type class_decl: Declaration
        :param method_name: The missing or unexpected method name.
        :type method_name: str
        :return: The finding dict.
        :rtype: Dict
        '''

        # Every CRUD finding cites the section header and both names.
        return {
            'error_code': error_code,
            'message': message,
            'node': header_decl,
            'repo_name': header_decl.name,
            'class_name': class_decl.name,
            'method_name': method_name,
        }
