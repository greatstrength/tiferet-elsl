"""Semantic Analysis Builder and Name Resolver Utilities"""

# *** imports

# ** core
from typing import Any, Dict, List, Optional

# ** app
from ..mappers import (
    SYMBOL_KIND_ATTRIBUTE,
    SYMBOL_KIND_CLASS_DEF,
    SYMBOL_KIND_IMPORT,
    SYMBOL_KIND_METHOD,
    SYMBOL_KIND_PARAMETER,
    Declaration,
    Expression,
    ExpressionAggregate,
    ParamList,
    Production,
    ScopeAggregate,
    Statement,
)
from ..mappers.semantic import (
    ResolutionAccumulator,
    ResolutionResult,
    Symbol,
)
from .core import (
    ProductionContext,
    StatementWalker,
)

# *** classes

# ** class: import_from_production
class ImportFromProduction(Production):
    '''
    Register names introduced by an import-from statement.

    Later resolution treats those names as defined in the current scope,
    and keeps the module they were imported from.
    '''

    # * method: apply
    def apply(self, candidate: Any, context: Any) -> None:
        '''
        Register each imported name with its source module.

        :param candidate: The import-from statement.
        :type candidate: Any
        :param context: The production visit context.
        :type context: Any
        :return: None
        :rtype: None
        '''

        # Skip a candidate that is not an import-from statement in a scope.
        if not isinstance(candidate, Statement) or context.current_scope is None:
            return

        # The module path is the from-clause name when one is present.
        module_path = ''
        if candidate.init_expr is not None and candidate.init_expr.name:
            module_path = candidate.init_expr.name

        # Register each collected name as an import in the current scope.
        for name in ExpressionAggregate.collect_import_names(candidate.expr):
            context.current_scope.add_symbol(Symbol(
                name=name,
                kind=SYMBOL_KIND_IMPORT,
                scope_path=context.current_scope.path,
                source_module=module_path,
            ))

# ** class: import_production
class ImportProduction(Production):
    '''
    Register names introduced by a plain import statement.

    The imported name is defined in the current scope without a separate
    source-module annotation.
    '''

    # * method: apply
    def apply(self, candidate: Any, context: Any) -> None:
        '''
        Register each imported name in the current scope.

        :param candidate: The import statement.
        :type candidate: Any
        :param context: The production visit context.
        :type context: Any
        :return: None
        :rtype: None
        '''

        # Skip a candidate that is not an import statement in a scope.
        if not isinstance(candidate, Statement) or context.current_scope is None:
            return

        # Register each collected name as an import, without a source module.
        for name in ExpressionAggregate.collect_import_names(candidate.expr):
            context.current_scope.add_symbol(Symbol(
                name=name,
                kind=SYMBOL_KIND_IMPORT,
                scope_path=context.current_scope.path,
            ))

# ** class: class_decl_production
class ClassDeclProduction(Production):
    '''
    Register a class declaration in the enclosing scope.

    The base class name is recorded as a type annotation, not checked.
    '''

    # * method: apply
    def apply(self, candidate: Any, context: Any) -> None:
        '''
        Register the class symbol, including its base name when present.

        :param candidate: The class declaration.
        :type candidate: Any
        :param context: The production visit context.
        :type context: Any
        :return: None
        :rtype: None
        '''

        # Skip a candidate that is not a declaration in a scope.
        if not isinstance(candidate, Declaration) or context.current_scope is None:
            return

        # The base name lives on the subtype when a base class was declared.
        base_class = None
        if candidate.type is not None and candidate.type.subtype is not None:
            base_class = candidate.type.subtype.name

        # Register the class in the enclosing scope.
        context.current_scope.add_symbol(Symbol(
            name=candidate.name,
            kind=SYMBOL_KIND_CLASS_DEF,
            scope_path=context.current_scope.path,
            type_annotation=base_class,
        ))

# ** class: func_decl_production
class FuncDeclProduction(Production):
    '''
    Register a function or method declaration in the enclosing scope.

    The return-type kind is recorded as a type annotation, not checked.
    '''

    # * method: apply
    def apply(self, candidate: Any, context: Any) -> None:
        '''
        Register the function symbol, including its return type when present.

        :param candidate: The function declaration.
        :type candidate: Any
        :param context: The production visit context.
        :type context: Any
        :return: None
        :rtype: None
        '''

        # Skip a candidate that is not a declaration in a scope.
        if not isinstance(candidate, Declaration) or context.current_scope is None:
            return

        # The return type is the nested kind value when a return type exists.
        return_type = None
        if (
                candidate.type is not None
                and candidate.type.return_type is not None
                and candidate.type.return_type.kind is not None):
            return_type = candidate.type.return_type.kind.value

        # Register the function as a method symbol in the enclosing scope.
        context.current_scope.add_symbol(Symbol(
            name=candidate.name,
            kind=SYMBOL_KIND_METHOD,
            scope_path=context.current_scope.path,
            type_annotation=return_type,
        ))

# ** class: attr_decl_production
class AttrDeclProduction(Production):
    '''
    Register an attribute declaration in the current scope.

    Primitive kinds and class type names are recorded; they are not checked.
    '''

    # * method: apply
    def apply(self, candidate: Any, context: Any) -> None:
        '''
        Register the attribute symbol and its recorded annotation.

        :param candidate: The attribute declaration.
        :type candidate: Any
        :param context: The production visit context.
        :type context: Any
        :return: None
        :rtype: None
        '''

        # Skip a candidate that is not a declaration in a scope.
        if not isinstance(candidate, Declaration) or context.current_scope is None:
            return

        # Primitive kinds contribute their value; class-typed attributes contribute the name.
        decl_type = candidate.type
        type_annotation = None
        if decl_type is not None and decl_type.is_primitive:
            type_annotation = decl_type.kind.value
        elif candidate.is_class and not candidate.code and decl_type is not None:
            type_annotation = decl_type.name

        # Register the attribute in the current scope.
        context.current_scope.add_symbol(Symbol(
            name=candidate.name,
            kind=SYMBOL_KIND_ATTRIBUTE,
            scope_path=context.current_scope.path,
            type_annotation=type_annotation,
        ))

# ** class: self_attr_assign_production
class SelfAttrAssignProduction(Production):
    '''
    Register an implicit attribute from an undeclared ``self.X`` assignment.

    The attribute is added to the enclosing class scope, not the method scope.
    '''

    # * method: apply
    def apply(self, candidate: Any, context: Any) -> None:
        '''
        Register ``self.X`` on the enclosing class when it is not already declared.

        :param candidate: The expression statement.
        :type candidate: Any
        :param context: The production visit context.
        :type context: Any
        :return: None
        :rtype: None
        '''

        # Skip unless the statement assigns to a named self attribute.
        if not isinstance(candidate, Statement) or candidate.expr is None:
            return
        left = candidate.expr.left
        if (
                not candidate.expr.is_assignment
                or left is None
                or not left.is_self_attribute
                or not left.name):
            return

        # Strip the self. prefix and keep the attribute only on a class scope.
        attr_name = left.name[5:]
        class_scope = context.find_enclosing_scope(SYMBOL_KIND_CLASS_DEF)
        if class_scope is None or class_scope.has_symbol(attr_name):
            return

        # Register the implicit attribute on the enclosing class.
        class_scope.add_symbol(Symbol(
            name=attr_name,
            kind=SYMBOL_KIND_ATTRIBUTE,
            scope_path=class_scope.path,
        ))

# ** class: name_production
class NameProduction(Production):
    '''
    Resolve a bare name against the scope stack.

    The first defining scope, from the inside out, is the binding that is recorded.
    '''

    # * method: apply
    def apply(self, candidate: Any, context: Any) -> None:
        '''
        Record a resolved or unresolved bare name.

        :param candidate: The name, already extracted from the expression.
        :type candidate: Any
        :param context: The production visit context.
        :type context: Any
        :return: None
        :rtype: None
        '''

        # Skip a candidate that is not a name in a scope with an accumulator.
        if (
                not isinstance(candidate, str)
                or context.current_scope is None
                or context.accumulator is None):
            return

        # The innermost defining scope wins.
        for scope in reversed(context.scope_stack):
            if scope.has_symbol(candidate):
                context.accumulator.record_resolved(
                    name=candidate,
                    scope_path=context.current_scope.path,
                    resolved_to=scope.path,
                )
                return

        # A miss is recorded against the scope where the name was used.
        context.accumulator.record_unresolved(
            name=candidate,
            scope_path=context.current_scope.path,
        )

# ** class: self_attr_production
class SelfAttrProduction(Production):
    '''
    Resolve a ``self.X`` reference against the enclosing class scope.

    The recorded name keeps the ``self.`` prefix so it is distinct from a bare name.
    '''

    # * method: apply
    def apply(self, candidate: Any, context: Any) -> None:
        '''
        Record a resolved or unresolved self attribute.

        :param candidate: The attribute name, already stripped of ``self.``.
        :type candidate: Any
        :param context: The production visit context.
        :type context: Any
        :return: None
        :rtype: None
        '''

        # Skip a candidate that is not an attribute name in a scope with an accumulator.
        if (
                not isinstance(candidate, str)
                or context.current_scope is None
                or context.accumulator is None):
            return

        # Look only at the innermost class scope, then stop.
        qualified = f'self.{candidate}'
        for scope in reversed(context.scope_stack):
            if scope.kind != SYMBOL_KIND_CLASS_DEF:
                continue

            # A class attribute resolves; a missing one does not.
            if scope.has_symbol(candidate):
                context.accumulator.record_resolved(
                    name=qualified,
                    scope_path=context.current_scope.path,
                    resolved_to=scope.path,
                )
            else:
                context.accumulator.record_unresolved(
                    name=qualified,
                    scope_path=context.current_scope.path,
                )
            return

        # No enclosing class scope means the self attribute cannot resolve.
        context.accumulator.record_unresolved(
            name=qualified,
            scope_path=context.current_scope.path,
        )

# *** constants

# ** constant: builder_production_set
BUILDER_PRODUCTION_SET: List[Production] = [
    ImportFromProduction(
        id='builder.import_from',
        applies_to='import_from',
    ),
    ImportProduction(
        id='builder.import',
        applies_to='import',
    ),
    ClassDeclProduction(
        id='builder.class_decl',
        applies_to='class_decl',
    ),
    FuncDeclProduction(
        id='builder.func_decl',
        applies_to='func_decl',
    ),
    AttrDeclProduction(
        id='builder.attr_decl',
        applies_to='attr_decl',
    ),
    SelfAttrAssignProduction(
        id='builder.self_attr_assign',
        applies_to='expression',
    ),
]

# ** constant: resolver_production_set
RESOLVER_PRODUCTION_SET: List[Production] = [
    NameProduction(
        id='resolver.name',
        applies_to='name',
    ),
    SelfAttrProduction(
        id='resolver.self_attr',
        applies_to='self_attr',
    ),
]

# *** utils

# ** util: symbol_table_builder
class SymbolTableBuilder(StatementWalker):
    '''
    Walk a module once and record the scopes and symbols later resolution looks up.

    Artifact groups, sections, members, and snippets stay transparent: they do not open scopes.
    '''

    # * attribute: productions
    productions: List[Production]

    # * init
    def __init__(self, productions: Optional[List[Production]] = None) -> None:
        '''
        Store the builder productions and start from an empty scope registry.

        :param productions: The productions to attach, or None for the builder set.
        :type productions: Optional[List[Production]]
        :return: None
        :rtype: None
        '''

        # Default to the builder set without copying it.
        self.productions = (
            productions if productions is not None else BUILDER_PRODUCTION_SET
        )

        # The provision list is the production list. The walk starts empty.
        super().__init__(scopes={}, provisions=self.productions)

    # * method: build
    def build(self, module_decl: Declaration) -> dict:
        '''
        Build the symbol table for one module declaration.

        :param module_decl: The module declaration to walk.
        :type module_decl: Declaration
        :return: The module name, dumped scopes, and root scope path.
        :rtype: dict
        '''

        # A fresh build does not keep scopes from a previous walk.
        self.scopes = {}
        self.scope_stack = []

        # Open the root module scope and walk the body when it has one.
        module_name = module_decl.name or 'unknown'
        module_scope = ScopeAggregate.new_module_scope(module_name)
        self.register_scope(module_scope)
        self.scope_stack.append(module_scope)
        if module_decl.code:
            self.walk_statements(module_decl.code)

        # Return dumped scopes so the caller does not depend on live aggregates.
        return {
            'module_name': module_name,
            'scopes': {
                path: scope.model_dump(exclude_none=True)
                for path, scope in self.scopes.items()
            },
            'root_scope_path': 'module',
        }

    # * method: register_scope
    def register_scope(self, scope: ScopeAggregate) -> None:
        '''
        Store a scope in the flat path registry.

        :param scope: The scope to store.
        :type scope: ScopeAggregate
        :return: None
        :rtype: None
        '''

        # Index the scope by the path later lookups will use.
        self.scopes[scope.path] = scope

    # * method: push_scope
    def push_scope(self, scope: ScopeAggregate) -> None:
        '''
        Register a child scope and push it onto the walk stack.

        :param scope: The child scope to enter.
        :type scope: ScopeAggregate
        :return: None
        :rtype: None
        '''

        # Register first so the parent can point at a stored path.
        self.register_scope(scope)
        self.current_scope.add_child(scope.name, scope.path)
        self.scope_stack.append(scope)

    # * method: pop_scope
    def pop_scope(self) -> None:
        '''
        Leave the innermost scope.

        :return: None
        :rtype: None
        '''

        # The matching push owns the scope that is popped.
        self.scope_stack.pop()

    # * method: apply
    def apply(self, visit: str, candidate: Any) -> None:
        '''
        Apply the productions attached to one visit hook.

        :param visit: The visit hook.
        :type visit: str
        :param candidate: The node being visited.
        :type candidate: Any
        :return: None
        :rtype: None
        '''

        # Copy the stack so a production cannot reorder the walk.
        context = ProductionContext(scope_stack=list(self.scope_stack))
        self.apply_provisions(visit, candidate, context)

    # * method: handle_import_from
    def handle_import_from(self, stmt: Statement) -> None:
        '''
        Register names from an import-from statement.

        :param stmt: The import-from statement.
        :type stmt: Statement
        :return: None
        :rtype: None
        '''

        # The import-from production owns the registration.
        self.apply('import_from', stmt)

    # * method: handle_import
    def handle_import(self, stmt: Statement) -> None:
        '''
        Register names from a plain import statement.

        :param stmt: The import statement.
        :type stmt: Statement
        :return: None
        :rtype: None
        '''

        # The import production owns the registration.
        self.apply('import', stmt)

    # * method: handle_decl
    def handle_decl(self, stmt: Statement) -> None:
        '''
        Dispatch a declaration to the first matching registration path.

        :param stmt: The declaration statement.
        :type stmt: Statement
        :return: None
        :rtype: None
        '''

        # A statement without a declaration has nothing to register.
        if not stmt.decl:
            return

        # Artifact members are transparent: walk their body without a new scope.
        decl = stmt.decl
        if getattr(decl, 'is_artifact_member', False):
            self.handle_artifact_member(decl)
            return

        # A class with a body opens a class scope after its symbol is registered.
        if decl.is_class and decl.code:
            self.handle_class_decl(decl)
            return

        # A function opens a method scope after its symbol is registered.
        if decl.is_func:
            self.handle_func_decl(decl)
            return

        # Primitive and class-typed attributes stay in the current scope.
        decl_type = decl.type
        if decl_type and decl_type.is_primitive:
            self.apply('attr_decl', decl)
            return
        if decl.is_class and not decl.code:
            self.apply('attr_decl', decl)

    # * method: handle_artifact_member
    def handle_artifact_member(self, decl: Declaration) -> None:
        '''
        Walk an artifact member body without opening a scope.

        :param decl: The artifact member declaration.
        :type decl: Declaration
        :return: None
        :rtype: None
        '''

        # The member wrapper is not a scope. Its body may contain real declarations.
        if decl.code:
            self.walk_statements(decl.code)

    # * method: handle_class_decl
    def handle_class_decl(self, decl: Declaration) -> None:
        '''
        Register a class, walk its body in a class scope, then leave that scope.

        :param decl: The class declaration.
        :type decl: Declaration
        :return: None
        :rtype: None
        '''

        # Register the class in the parent scope before entering the child.
        self.apply('class_decl', decl)
        self.push_scope(ScopeAggregate.new_class_scope(
            decl.name,
            self.current_scope.path,
        ))
        if decl.code:
            self.walk_statements(decl.code)
        self.pop_scope()

    # * method: handle_func_decl
    def handle_func_decl(self, decl: Declaration) -> None:
        '''
        Register a function, record its parameters, walk its body, then leave the scope.

        :param decl: The function declaration.
        :type decl: Declaration
        :return: None
        :rtype: None
        '''

        # Register the function in the parent scope before entering the method scope.
        self.apply('func_decl', decl)
        self.push_scope(ScopeAggregate.new_method_scope(
            decl.name,
            self.current_scope.path,
        ))
        if decl.type and decl.type.params:
            self.register_params(decl.type.params)
        if decl.code:
            self.walk_statements(decl.code)
        self.pop_scope()

    # * method: register_params
    def register_params(self, params: List[ParamList]) -> None:
        '''
        Register each parameter in the current method scope.

        :param params: The function parameters.
        :type params: List[ParamList]
        :return: None
        :rtype: None
        '''

        # Record the parameter type kind when both the type and its kind exist.
        for current in params:
            type_annotation = None
            if current.type is not None and current.type.kind is not None:
                type_annotation = current.type.kind.value
            self.current_scope.add_symbol(Symbol(
                name=current.name,
                kind=SYMBOL_KIND_PARAMETER,
                scope_path=self.current_scope.path,
                type_annotation=type_annotation,
            ))

    # * method: handle_expr
    def handle_expr(self, stmt: Statement) -> None:
        '''
        Apply expression productions to an expression statement.

        :param stmt: The expression statement.
        :type stmt: Statement
        :return: None
        :rtype: None
        '''

        # Implicit self-attribute assignments are expression productions.
        self.apply('expression', stmt)

# ** util: name_resolver
class NameResolver(StatementWalker):
    '''
    Walk a module against a built symbol table and record which names resolve.

    Unresolved names stay on the result. This walk does not turn them into findings.
    '''

    # * attribute: _accumulator
    _accumulator: ResolutionAccumulator

    # * attribute: productions
    productions: List[Production]

    # * init
    def __init__(self, scopes: Dict[str, ScopeAggregate],
                 productions: Optional[List[Production]] = None) -> None:
        '''
        Store the scope registry and start an empty resolution accumulator.

        :param scopes: The flat path-to-scope registry from a builder.
        :type scopes: Dict[str, ScopeAggregate]
        :param productions: The productions to attach, or None for the resolver set.
        :type productions: Optional[List[Production]]
        :return: None
        :rtype: None
        '''

        # Default to the resolver set without copying it.
        self.productions = (
            productions if productions is not None else RESOLVER_PRODUCTION_SET
        )

        # The provision list is the production list. Scopes come from the builder.
        super().__init__(scopes=scopes, provisions=self.productions)
        self._accumulator = ResolutionAccumulator()

    # * method: resolve
    def resolve(self, module_decl: Declaration) -> ResolutionResult:
        '''
        Resolve names in one module declaration.

        :param module_decl: The module declaration to walk.
        :type module_decl: Declaration
        :return: The collected resolution result.
        :rtype: ResolutionResult
        '''

        # A fresh resolve does not keep lookups or a stack from a previous walk.
        self.scope_stack = []
        self._accumulator.reset()

        # Without a module scope there is nothing to resolve against.
        module_scope = self.scopes.get('module')
        if module_scope is None:
            return self._accumulator.to_result()

        # Walk the body inside the module scope, then take the result.
        self.scope_stack.append(module_scope)
        if module_decl.code:
            self.walk_statements(module_decl.code)
        return self._accumulator.to_result()

    # * method: apply
    def apply(self, visit: str, candidate: Any) -> None:
        '''
        Apply the productions attached to one visit hook.

        :param visit: The visit hook.
        :type visit: str
        :param candidate: The node or name being visited.
        :type candidate: Any
        :return: None
        :rtype: None
        '''

        # Copy the stack and pass the host-owned accumulator.
        context = ProductionContext(
            scope_stack=list(self.scope_stack),
            accumulator=self._accumulator,
        )
        self.apply_provisions(visit, candidate, context)

    # * method: handle_decl
    def handle_decl(self, stmt: Statement) -> None:
        '''
        Dispatch a declaration to the matching resolution path.

        :param stmt: The declaration statement.
        :type stmt: Statement
        :return: None
        :rtype: None
        '''

        # A statement without a declaration has nothing to resolve.
        if not stmt.decl:
            return

        # Artifact members are transparent: walk their body without a new scope.
        decl = stmt.decl
        if getattr(decl, 'is_artifact_member', False):
            self.handle_artifact_member_resolve(decl)
            return

        # A class with a body resolves its base, then its body in the class scope.
        if decl.is_class and decl.code:
            self.handle_class_decl_resolve(decl)
            return

        # A function resolves its body in the method scope.
        if decl.is_func:
            self.handle_func_decl_resolve(decl)

    # * method: handle_artifact_member_resolve
    def handle_artifact_member_resolve(self, decl: Declaration) -> None:
        '''
        Resolve names in an artifact member body without opening a scope.

        :param decl: The artifact member declaration.
        :type decl: Declaration
        :return: None
        :rtype: None
        '''

        # The member wrapper is not a scope. Its body may contain real names.
        if decl.code:
            self.walk_statements(decl.code)

    # * method: handle_class_decl_resolve
    def handle_class_decl_resolve(self, decl: Declaration) -> None:
        '''
        Resolve a class base name, then walk the class body in its child scope.

        :param decl: The class declaration.
        :type decl: Declaration
        :return: None
        :rtype: None
        '''

        # The base name is resolved in the enclosing scope, before the class is entered.
        if (
                decl.type is not None
                and decl.type.subtype is not None
                and decl.type.subtype.name):
            self.apply('name', decl.type.subtype.name)

        # Enter the class scope the builder registered, when it exists.
        with self.entering_child_scope(decl.name):
            if decl.code:
                self.walk_statements(decl.code)

    # * method: handle_func_decl_resolve
    def handle_func_decl_resolve(self, decl: Declaration) -> None:
        '''
        Walk a function body in the method scope the builder registered.

        :param decl: The function declaration.
        :type decl: Declaration
        :return: None
        :rtype: None
        '''

        # Enter the method scope the builder registered, when it exists.
        with self.entering_child_scope(decl.name):
            if decl.code:
                self.walk_statements(decl.code)

    # * method: handle_expr
    def handle_expr(self, stmt: Statement) -> None:
        '''
        Resolve the expression on an expression statement.

        :param stmt: The expression statement.
        :type stmt: Statement
        :return: None
        :rtype: None
        '''

        # Skip a statement that has no expression.
        if stmt.expr:
            self.resolve_expr(stmt.expr)

    # * method: handle_return
    def handle_return(self, stmt: Statement) -> None:
        '''
        Resolve the expression on a return statement.

        :param stmt: The return statement.
        :type stmt: Statement
        :return: None
        :rtype: None
        '''

        # Skip a bare return.
        if stmt.expr:
            self.resolve_expr(stmt.expr)

    # * method: handle_if_else
    def handle_if_else(self, stmt: Statement) -> None:
        '''
        Resolve an if condition, then walk both branches.

        :param stmt: The if statement.
        :type stmt: Statement
        :return: None
        :rtype: None
        '''

        # Resolve the condition before either branch.
        if stmt.expr:
            self.resolve_expr(stmt.expr)
        if stmt.body:
            self.walk_statements(stmt.body)
        if stmt.else_body:
            self.walk_statements(stmt.else_body)

    # * method: handle_for
    def handle_for(self, stmt: Statement) -> None:
        '''
        Resolve a for target and iterable, then walk the body.

        :param stmt: The for statement.
        :type stmt: Statement
        :return: None
        :rtype: None
        '''

        # Resolve both expressions before the body.
        if stmt.init_expr:
            self.resolve_expr(stmt.init_expr)
        if stmt.expr:
            self.resolve_expr(stmt.expr)
        if stmt.body:
            self.walk_statements(stmt.body)

    # * method: handle_while
    def handle_while(self, stmt: Statement) -> None:
        '''
        Resolve a while condition, then walk the body.

        :param stmt: The while statement.
        :type stmt: Statement
        :return: None
        :rtype: None
        '''

        # Resolve the condition before the body.
        if stmt.expr:
            self.resolve_expr(stmt.expr)
        if stmt.body:
            self.walk_statements(stmt.body)

    # * method: handle_try_except
    def handle_try_except(self, stmt: Statement) -> None:
        '''
        Walk a try body and its handlers.

        :param stmt: The try statement.
        :type stmt: Statement
        :return: None
        :rtype: None
        '''

        # Handlers live on else_body. This visit does not resolve a separate expression.
        if stmt.body:
            self.walk_statements(stmt.body)
        if stmt.else_body:
            self.walk_statements(stmt.else_body)

    # * method: handle_with
    def handle_with(self, stmt: Statement) -> None:
        '''
        Resolve a with expression, then walk the body.

        :param stmt: The with statement.
        :type stmt: Statement
        :return: None
        :rtype: None
        '''

        # Resolve the context expression before the body.
        if stmt.expr:
            self.resolve_expr(stmt.expr)
        if stmt.body:
            self.walk_statements(stmt.body)

    # * method: handle_raise
    def handle_raise(self, stmt: Statement) -> None:
        '''
        Resolve the expression on a raise statement.

        :param stmt: The raise statement.
        :type stmt: Statement
        :return: None
        :rtype: None
        '''

        # Skip a bare raise.
        if stmt.expr:
            self.resolve_expr(stmt.expr)

    # * method: handle_assert
    def handle_assert(self, stmt: Statement) -> None:
        '''
        Resolve the expression on an assert statement.

        :param stmt: The assert statement.
        :type stmt: Statement
        :return: None
        :rtype: None
        '''

        # The asserted expression is the primary expression.
        if stmt.expr:
            self.resolve_expr(stmt.expr)

    # * method: handle_del
    def handle_del(self, stmt: Statement) -> None:
        '''
        Resolve the expression on a del statement.

        :param stmt: The del statement.
        :type stmt: Statement
        :return: None
        :rtype: None
        '''

        # The deleted expression is the primary expression.
        if stmt.expr:
            self.resolve_expr(stmt.expr)

    # * method: resolve_expr
    def resolve_expr(self, expr: Expression) -> None:
        '''
        Resolve names in an expression, skipping literals, comments, and bare self.

        :param expr: The expression to resolve.
        :type expr: Expression
        :return: None
        :rtype: None
        '''

        # A missing expression has no names.
        if not expr:
            return

        # Literals and comments are not names.
        if expr.is_literal or expr.kind.value == 'comment':
            return

        # Bare self is the instance, not a looked-up name.
        if expr.is_name_ref and expr.name == 'self':
            return

        # A self attribute is resolved on the enclosing class, not as a bare name.
        if expr.is_name_ref and expr.is_self_attribute:
            self.apply('self_attr', expr.name[5:])
            return

        # Any other name is resolved through the scope stack.
        if expr.is_name_ref and expr.name:
            self.apply('name', expr.name)
            return

        # An assignment resolves its value, not its target.
        if expr.is_assignment:
            if expr.right:
                self.resolve_expr(expr.right)
            return

        # Every other shape resolves its children when they exist.
        if expr.left:
            self.resolve_expr(expr.left)
        if expr.right:
            self.resolve_expr(expr.right)
