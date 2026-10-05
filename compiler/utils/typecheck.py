"""Conformance Checking Utilities"""

# *** imports

# ** core
from typing import Any, Dict, List, Optional

# ** app
from ..mappers import (
    PROVISION_KIND_SPECIFICATION,
    Declaration,
    Statement,
)
from ..mappers.typecheck import TypeErrorCollection
from .core import (
    ConformanceContext,
    StatementWalker,
)
from .provision import collect_owned_provisions

# *** utils

# ** util: conformance_checker
class ConformanceChecker(StatementWalker):
    '''
    Walk a module once and collect findings for one dialect selector.

    Behavior varies by the specification prefix the caller selects. The
    checker does not own the catalog and does not walk every specification.
    '''

    # * attribute: provision_findings
    provision_findings: List[Dict]

    # * attribute: _finding_collection
    _finding_collection: TypeErrorCollection

    # * attribute: _group_stack
    _group_stack: List[str]

    # * init
    def __init__(self, scopes: Dict[str, Any], cache, selector: str,
            provision_prefix: tuple) -> None:
        '''
        Store the scope registry and attach the selected specifications.

        :param scopes: The flat path-to-scope registry.
        :type scopes: Dict[str, Any]
        :param cache: The cache whose provision namespace is read once.
        :type cache: Any
        :param selector: The owned id prefix, including the trailing dot.
        :type selector: str
        :param provision_prefix: The namespace prefix the caller passes.
        :type provision_prefix: tuple
        :return: None
        :rtype: None
        '''

        # Read the namespace once. A later check does not read it again.
        rows = cache.get_by_prefix(*provision_prefix)
        provisions, self.provision_findings = collect_owned_provisions(
            rows,
            owned_prefix=selector,
            kind=PROVISION_KIND_SPECIFICATION,
        )

        # The provision list is the selected specifications. The walk starts empty.
        super().__init__(scopes=scopes, provisions=provisions)
        self._finding_collection = TypeErrorCollection()
        self._group_stack = []

    # * method: check
    def check(self, module_decl: Declaration) -> List[Dict]:
        '''
        Check one module declaration and return every collected finding.

        Instantiation findings come first, including when the module scope
        is missing. The module hook runs after that scope is pushed and
        before the body walk. Walk findings stay on the collection.

        :param module_decl: The module declaration to walk.
        :type module_decl: Declaration
        :return: Instantiation findings followed by walk findings.
        :rtype: List[Dict]
        '''

        # A fresh check does not keep walk findings or a stack from a previous walk.
        self.scope_stack = []
        self._finding_collection.reset()
        self._group_stack = []

        # Without a module scope there is nothing to check against.
        module_scope = self.scopes.get('module')
        if module_scope is None:
            return list(self.provision_findings) + self._finding_collection.to_list()

        # Section order sees the module declaration before its body is walked.
        self.scope_stack.append(module_scope)
        self.apply('module', module_decl)
        if module_decl.code:
            self.walk_statements(module_decl.code)
        return list(self.provision_findings) + self._finding_collection.to_list()

    # * method: apply
    def apply(self, visit: str, candidate: Any,
              stmt: Optional[Statement] = None) -> None:
        '''
        Apply the specifications attached to one visit hook.

        :param visit: The visit hook.
        :type visit: str
        :param candidate: The node being visited.
        :type candidate: Any
        :param stmt: The enclosing statement, when the visit needs siblings.
        :type stmt: Optional[Statement]
        :return: None
        :rtype: None
        '''

        # The innermost tier-1 group is the name specifications may cite.
        group_name = self._group_stack[-1] if self._group_stack else None
        context = ConformanceContext(
            scope_stack=list(self.scope_stack),
            stmt=stmt,
            group_name=group_name,
        )

        # Record each finding against the current scope, or the module path.
        scope_path = self.current_scope.path if self.scope_stack else 'module'
        for result in self.apply_provisions(visit, candidate, context):
            for finding in result or []:
                self._finding_collection.add(scope_path=scope_path, **finding)

    # * method: handle_artifact
    def handle_artifact(self, stmt: Statement) -> None:
        '''
        Check an artifact header, then walk its body.

        A tier-1 group pushes its name for the body walk and pops it afterward.

        :param stmt: The artifact statement.
        :type stmt: Statement
        :return: None
        :rtype: None
        '''

        # Header rules see the declaration and the enclosing statement.
        header_decl = self.extract_artifact_header(stmt)
        if header_decl is not None:
            self.apply('artifact_header', header_decl, stmt=stmt)

        # Only tier-1 groups contribute a name to the group stack.
        pushed = (
            header_decl is not None
            and getattr(header_decl, 'artifact_type', None) == '***'
        )
        if pushed:
            self._group_stack.append(header_decl.name or '')
        try:
            if stmt.body:
                self.walk_statements(stmt.body)
        finally:
            if pushed:
                self._group_stack.pop()

    # * method: extract_artifact_header
    def extract_artifact_header(self, stmt: Statement) -> Optional[Declaration]:
        '''
        Return the artifact header declaration, if the statement has one.

        :param stmt: The artifact statement.
        :type stmt: Statement
        :return: The header declaration, or None.
        :rtype: Optional[Declaration]
        '''

        # The header is the statement declaration when one is present.
        if stmt.decl:
            return stmt.decl
        return None

    # * method: handle_decl
    def handle_decl(self, stmt: Statement) -> None:
        '''
        Dispatch a declaration to the first matching conformance path.

        :param stmt: The declaration statement.
        :type stmt: Statement
        :return: None
        :rtype: None
        '''

        # A statement without a declaration has nothing to check.
        if not stmt.decl:
            return

        # Artifact members are checked, then their body is walked without a new scope.
        decl = stmt.decl
        if getattr(decl, 'is_artifact_member', False):
            self.apply('member', decl)
            self.handle_artifact_member(decl)
            return

        # A class opens its child scope. A function opens a method scope.
        if decl.is_class:
            self.handle_class_decl(decl)
            return
        if decl.is_func:
            self.handle_func_decl(decl)

    # * method: handle_expr
    def handle_expr(self, stmt: Statement) -> None:
        '''
        Check the expression on an expression statement.

        :param stmt: The expression statement.
        :type stmt: Statement
        :return: None
        :rtype: None
        '''

        # Skip a statement that has no expression to check.
        if stmt.expr:
            self.apply('expression', stmt.expr)

    # * method: handle_return
    def handle_return(self, stmt: Statement) -> None:
        '''
        Check a return statement.

        :param stmt: The return statement.
        :type stmt: Statement
        :return: None
        :rtype: None
        '''

        # Return rules see the statement, not a nested expression.
        self.apply('return', stmt)

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
        Walk a class body in its registered child scope.

        The class hook runs before the body walk.

        :param decl: The class declaration.
        :type decl: Declaration
        :return: None
        :rtype: None
        '''

        # Member order sees the class declaration before its body is walked.
        self.apply('class', decl)

        # A missing child scope does not push. The body is still walked.
        with self.entering_child_scope(decl.name):
            if decl.code:
                self.walk_statements(decl.code)

    # * method: handle_func_decl
    def handle_func_decl(self, decl: Declaration) -> None:
        '''
        Walk a function body in its registered child scope.

        :param decl: The function declaration.
        :type decl: Declaration
        :return: None
        :rtype: None
        '''

        # A missing child scope does not push. The body is still walked.
        with self.entering_child_scope(decl.name):
            if decl.code:
                self.walk_statements(decl.code)
