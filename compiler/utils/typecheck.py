"""Conformance Checking Utilities"""

# *** imports

# ** core
from typing import Any, Dict, List, Optional

# ** app
from ..mappers import Declaration, Statement
from ..mappers.typecheck import TypeErrorCollection
from .core import (
    AppImportSpecification,
    AssignmentTypeSpecification,
    AttributeMemberSpecification,
    BinaryOpTypeSpecification,
    ConformanceContext,
    DIAbstractMethodSpecification,
    DomainAttributeSpecification,
    EventSectionSpecification,
    FunctionSectionNameSpecification,
    GroupSectionAgreementSpecification,
    ImportGroupSpecification,
    MethodMemberSpecification,
    PermittedGroupSpecification,
    RequiredBaseSpecification,
    ReturnBinaryOpTypeSpecification,
    SectionClassNameSpecification,
    Specification,
    StatementWalker,
)

# *** constants

# ** constant: common_rule_set
COMMON_RULE_SET: List[Specification] = [
    ImportGroupSpecification(
        id='common.import_group',
        applies_to='artifact_header',
    ),
    SectionClassNameSpecification(
        id='common.section_class_name',
        applies_to='artifact_header',
    ),
    FunctionSectionNameSpecification(
        id='common.function_section_name',
        applies_to='artifact_header',
    ),
    AttributeMemberSpecification(
        id='common.attribute_member',
        applies_to='member',
    ),
    MethodMemberSpecification(
        id='common.method_member',
        applies_to='member',
    ),
    AssignmentTypeSpecification(
        id='common.assignment_type',
        applies_to='expression',
    ),
    BinaryOpTypeSpecification(
        id='common.binary_op_expression',
        applies_to='expression',
    ),
    ReturnBinaryOpTypeSpecification(
        id='common.binary_op_return',
        applies_to='return',
    ),
]

# ** constant: event_rule_set
EVENT_RULE_SET: List[Specification] = [
    EventSectionSpecification(
        id='event.section',
        applies_to='artifact_header',
    ),
]

# ** constant: domain_rule_set
DOMAIN_RULE_SET: List[Specification] = [
    PermittedGroupSpecification(
        id='domain.permitted_group',
        applies_to='artifact_header',
        permitted_groups=frozenset({
            'imports',
            'constants',
            'functions',
            'classes',
            'models',
            'exports',
        }),
        error_code='DISALLOWED_DOMAIN_GROUP',
        module_label='a domain module',
    ),
    AppImportSpecification(
        id='domain.app_import',
        applies_to='artifact_header',
        error_code='INVALID_DOMAIN_APP_IMPORT',
        message=(
            "Domain 'app' import group may only import same-package sibling "
            "modules or the assets component type; found '{module_path}'."
        ),
        allowed_components=frozenset({'assets'}),
    ),
    GroupSectionAgreementSpecification(
        id='domain.group_section_agreement',
        applies_to='artifact_header',
    ),
    RequiredBaseSpecification(
        id='domain.model_base_class',
        applies_to='artifact_header',
        section_keyword='model',
        error_code='MODEL_MISSING_DOMAIN_OBJECT_BASE',
        message=(
            "Model '{header_name}' class '{class_name}' declares no base class; "
            "it must extend DomainObject"
        ),
        name_key='model_name',
    ),
    DomainAttributeSpecification(
        id='domain.attribute',
        applies_to='member',
    ),
]

# ** constant: di_rule_set
DI_RULE_SET: List[Specification] = [
    PermittedGroupSpecification(
        id='di.permitted_group',
        applies_to='artifact_header',
        permitted_groups=frozenset({
            'imports',
            'constants',
            'functions',
            'classes',
            'exports',
        }),
        error_code='DISALLOWED_DI_GROUP',
        module_label='a di module',
    ),
    AppImportSpecification(
        id='di.app_import',
        applies_to='artifact_header',
        error_code='INVALID_DI_APP_IMPORT',
        message=(
            "DI 'app' import group may only import same-package sibling "
            "modules or the domain/interfaces component types; found '{module_path}'."
        ),
        allowed_components=frozenset({
            'domain',
            'interfaces',
        }),
    ),
    DIAbstractMethodSpecification(
        id='di.abstract_method',
        applies_to='artifact_header',
    ),
]

# *** utils

# ** util: conformance_checker
class ConformanceChecker(StatementWalker):
    '''
    Walk a module once and collect findings for the attached rule set.

    Behavior varies only by which specifications are in the rule set. A later
    dialect story adds a constant list, not a subclass.
    '''

    # * attribute: rule_set
    rule_set: List[Specification]

    # * attribute: _finding_collection
    _finding_collection: TypeErrorCollection

    # * attribute: _group_stack
    _group_stack: List[str]

    # * init
    def __init__(self, scopes: Dict[str, Any],
                 rule_set: List[Specification]) -> None:
        '''
        Store the scope registry and the specifications this checker applies.

        :param scopes: The flat path-to-scope registry.
        :type scopes: Dict[str, Any]
        :param rule_set: The specifications to attach.
        :type rule_set: List[Specification]
        :return: None
        :rtype: None
        '''

        # The attachment list is the rule set. The walk starts with no findings.
        super().__init__(scopes=scopes, attachments=rule_set)
        self.rule_set = rule_set
        self._finding_collection = TypeErrorCollection()
        self._group_stack = []

    # * method: check
    def check(self, module_decl: Declaration) -> List[Dict]:
        '''
        Check one module declaration and return every collected finding.

        :param module_decl: The module declaration to walk.
        :type module_decl: Declaration
        :return: Flattened finding dicts, empty when the module scope is missing.
        :rtype: List[Dict]
        '''

        # A fresh check does not keep findings or a stack from a previous walk.
        self.scope_stack = []
        self._finding_collection.reset()
        self._group_stack = []

        # Without a module scope there is nothing to check against.
        module_scope = self.scopes.get('module')
        if module_scope is None:
            return self._finding_collection.to_list()

        # Walk the body inside the module scope, then take the findings.
        self.scope_stack.append(module_scope)
        if module_decl.code:
            self.walk_statements(module_decl.code)
        return self._finding_collection.to_list()

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
        for result in self.apply_attachments(visit, candidate, context):
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

        :param decl: The class declaration.
        :type decl: Declaration
        :return: None
        :rtype: None
        '''

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
