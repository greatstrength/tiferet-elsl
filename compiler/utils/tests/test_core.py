"""Compiler Core Utilities Tests"""

# *** imports

# ** infra
import pytest

# ** app
from compiler.domain.artifact import ArtifactDeclaration
from compiler.domain.ast import (
    ExprKind,
    Expression,
    Statement,
    StatementKind,
)
from compiler.domain.semantic import (
    SYMBOL_KIND_CLASS_DEF,
    SYMBOL_KIND_METHOD,
    SYMBOL_KIND_MODULE,
    SYMBOL_KIND_VARIABLE,
    Symbol,
)
from compiler.mappers import AllOf, AnyOf, Not, Production, Rewrite, ScopeAggregate
from ..core import (
    AssignmentTypeSpecification,
    AttributeMemberSpecification,
    BinaryOpTypeSpecification,
    ConformanceContext,
    ConstantSectionNameSpecification,
    ContextManagerPairingSpecification,
    DIAbstractMethodSpecification,
    DomainAttributeSpecification,
    EventSectionSpecification,
    FunctionSectionNameSpecification,
    GroupSectionAgreementSpecification,
    ImportGroupSpecification,
    InterfaceAbstractMethodSpecification,
    MapperRolesAttributeSpecification,
    MethodMemberSpecification,
    ProductionContext,
    Provision,
    ReposCrudMethodSpecification,
    ReturnBinaryOpTypeSpecification,
    RewriteContext,
    SectionClassNameSpecification,
    Specification,
    StatementWalker,
    child_scope_path,
    extract_member_name_from_metadata,
    snake_to_pascal,
)

# *** classes

# ** class: _always_satisfied
class _AlwaysSatisfied(Specification):
    '''
    A specification whose evaluation never records a finding.
    '''

    # * method: evaluate
    def evaluate(self, candidate, context):
        '''
        Return no findings.

        :param candidate: The ignored candidate.
        :type candidate: Any
        :param context: The ignored context.
        :type context: Any
        :return: An empty finding list.
        :rtype: list
        '''

        # This fixture is always satisfied.
        del candidate, context
        return []

# ** class: _always_violated
class _AlwaysViolated(Specification):
    '''
    A specification whose evaluation always records one finding.
    '''

    # * attribute: code
    code: str = 'VIOLATED'

    # * method: evaluate
    def evaluate(self, candidate, context):
        '''
        Return the fixed finding.

        :param candidate: The ignored candidate.
        :type candidate: Any
        :param context: The ignored context.
        :type context: Any
        :return: One finding.
        :rtype: list
        '''

        # This fixture is never satisfied.
        del candidate, context
        return [{'error_code': self.code, 'message': self.code}]

# ** class: _named
class _Named(Specification):
    '''
    A specification whose finding code is its attachment id.
    '''

    # * method: evaluate
    def evaluate(self, candidate, context):
        '''
        Return a finding named for this attachment.

        :param candidate: The ignored candidate.
        :type candidate: Any
        :param context: The ignored context.
        :type context: Any
        :return: One finding.
        :rtype: list
        '''

        # The finding code is the attachment id.
        del candidate, context
        return [{'error_code': self.id, 'message': self.id}]

# ** class: _recording_walker
class _RecordingWalker(StatementWalker):
    '''
    A walker that records declaration, expression, and return visits.
    '''

    # * init
    def __init__(self, scopes=None, provisions=None):
        '''
        Start with an empty visit record.

        :param scopes: The scope registry.
        :type scopes: dict
        :param provisions: The provision list.
        :type provisions: list
        '''

        # Record visits after the base walker is initialized.
        super().__init__(scopes=scopes, provisions=provisions)
        self.seen = []

    # * method: handle_decl
    def handle_decl(self, stmt):
        '''
        Record a declaration visit.

        :param stmt: The declaration statement.
        :type stmt: Statement
        '''

        # Keep the statement so dispatch order can be asserted.
        self.seen.append(('decl', stmt))

    # * method: handle_expr
    def handle_expr(self, stmt):
        '''
        Record an expression visit.

        :param stmt: The expression statement.
        :type stmt: Statement
        '''

        # Keep the statement so dispatch order can be asserted.
        self.seen.append(('expr', stmt))

    # * method: handle_return
    def handle_return(self, stmt):
        '''
        Record a return visit.

        :param stmt: The return statement.
        :type stmt: Statement
        '''

        # Keep the statement so dispatch order can be asserted.
        self.seen.append(('return', stmt))

# *** tests

# ** test: provision_requires_id_and_applies_to
def test_provision_requires_id_and_applies_to() -> None:
    '''
    Test that a constructed provision stores its id and visit hook.
    '''

    # Construct a provision with both required values.
    provision = Provision(id='common.import_group', applies_to='artifact_header')

    # Both values are stored, and the base call is not implemented.
    assert provision.id == 'common.import_group'
    assert provision.applies_to == 'artifact_header'
    with pytest.raises(NotImplementedError):
        provision(None, None)

# ** test: attaches_to_matches_hook
def test_attaches_to_matches_hook() -> None:
    '''
    Test that attaches_to is true only for the stored hook.
    '''

    # An expression provision matches only that hook.
    provision = Provision(id='rule', applies_to='expression')
    assert provision.attaches_to('expression') is True
    assert provision.attaches_to('return') is False

# ** test: specification_cannot_be_instantiated_directly
def test_specification_cannot_be_instantiated_directly() -> None:
    '''
    Test that Specification cannot be instantiated.
    '''

    # The abstract evaluate method blocks construction.
    with pytest.raises(TypeError):
        Specification(id='rule', applies_to='expression')

# ** test: is_satisfied_by_true_when_no_findings
def test_is_satisfied_by_true_when_no_findings() -> None:
    '''
    Test that a specification with no findings is satisfied.
    '''

    # An always-satisfied child reports satisfaction.
    spec = _AlwaysSatisfied(id='ok', applies_to='expression')
    assert spec.is_satisfied_by(None, None) is True

# ** test: is_satisfied_by_false_when_findings
def test_is_satisfied_by_false_when_findings() -> None:
    '''
    Test that a specification with findings is not satisfied.
    '''

    # An always-violated child reports dissatisfaction.
    spec = _AlwaysViolated(id='bad', applies_to='expression')
    assert spec.is_satisfied_by(None, None) is False

# ** test: production_cannot_be_instantiated_directly
def test_production_cannot_be_instantiated_directly() -> None:
    '''
    Test that Production cannot be instantiated.
    '''

    # The abstract apply method blocks construction.
    with pytest.raises(TypeError):
        Production(id='rule', applies_to='expression')

# ** test: rewrite_cannot_be_instantiated_directly
def test_rewrite_cannot_be_instantiated_directly() -> None:
    '''
    Test that Rewrite cannot be instantiated.
    '''

    # The abstract apply method blocks construction.
    with pytest.raises(TypeError):
        Rewrite(id='rule', applies_to='expression')

# ** test: all_of_satisfied_when_every_child_satisfied
def test_all_of_satisfied_when_every_child_satisfied() -> None:
    '''
    Test that AllOf is satisfied when every child is satisfied.
    '''

    # Two satisfied children leave the conjunction satisfied.
    spec = AllOf(
        id='all',
        applies_to='expression',
        specs=[
            _AlwaysSatisfied(id='a', applies_to='expression'),
            _AlwaysSatisfied(id='b', applies_to='expression'),
        ],
    )
    assert spec.is_satisfied_by(None, None) is True

# ** test: all_of_concatenates_findings
def test_all_of_concatenates_findings() -> None:
    '''
    Test that AllOf concatenates child findings in child order.
    '''

    # Two violated children contribute findings in the order they were given.
    spec = AllOf(
        id='all',
        applies_to='expression',
        specs=[
            _AlwaysViolated(id='a', applies_to='expression', code='FIRST'),
            _AlwaysViolated(id='b', applies_to='expression', code='SECOND'),
        ],
    )
    assert [item['error_code'] for item in spec.evaluate(None, None)] == ['FIRST', 'SECOND']

# ** test: any_of_satisfied_when_one_child_satisfied
def test_any_of_satisfied_when_one_child_satisfied() -> None:
    '''
    Test that AnyOf is satisfied when one child is satisfied.
    '''

    # One satisfied child satisfies the disjunction.
    spec = AnyOf(
        id='any',
        applies_to='expression',
        specs=[
            _AlwaysViolated(id='a', applies_to='expression'),
            _AlwaysSatisfied(id='b', applies_to='expression'),
        ],
    )
    assert spec.is_satisfied_by(None, None) is True

# ** test: any_of_surfaces_findings_when_no_child_satisfied
def test_any_of_surfaces_findings_when_no_child_satisfied() -> None:
    '''
    Test that AnyOf concatenates findings when every child fails.
    '''

    # Every child failed, so both findings surface in child order.
    spec = AnyOf(
        id='any',
        applies_to='expression',
        specs=[
            _AlwaysViolated(id='a', applies_to='expression', code='FIRST'),
            _AlwaysViolated(id='b', applies_to='expression', code='SECOND'),
        ],
    )
    assert [item['error_code'] for item in spec.evaluate(None, None)] == ['FIRST', 'SECOND']

# ** test: not_satisfied_when_child_violated
def test_not_satisfied_when_child_violated() -> None:
    '''
    Test that Not is satisfied when its child is violated.
    '''

    # Negating a violation is satisfaction.
    spec = Not(
        id='negated',
        applies_to='expression',
        spec=_AlwaysViolated(id='child', applies_to='expression'),
    )
    assert spec.is_satisfied_by(None, None) is True

# ** test: not_violated_when_child_satisfied
def test_not_violated_when_child_satisfied() -> None:
    '''
    Test that Not emits an uppercased violation code when its child is satisfied.
    '''

    # Negating satisfaction records one uppercased violation.
    spec = Not(
        id='rule_check',
        applies_to='expression',
        spec=_AlwaysSatisfied(id='child', applies_to='expression'),
    )
    findings = spec.evaluate(None, None)
    assert findings[0]['error_code'] == 'RULE_CHECK_VIOLATION'

# ** test: infer_type_literal
def test_infer_type_literal() -> None:
    '''
    Test that integer and string literals infer int and str.
    '''

    # Literals carry their inferred type on the node.
    context = ConformanceContext()
    integer = Expression(kind=ExprKind.INT_VAL, value='1')
    text = Expression(kind=ExprKind.STR_VAL, value='a')
    assert context.infer_type(integer) == 'int'
    assert context.infer_type(text) == 'str'

# ** test: infer_type_numeric_widening
def test_infer_type_numeric_widening() -> None:
    '''
    Test that numeric binary operations infer int or float.
    '''

    # Two ints stay int; a float operand widens the result to float.
    context = ConformanceContext()
    int_add = Expression(
        kind=ExprKind.ADD,
        left=Expression(kind=ExprKind.INT_VAL, value='1'),
        right=Expression(kind=ExprKind.INT_VAL, value='2'),
    )
    float_add = Expression(
        kind=ExprKind.ADD,
        left=Expression(kind=ExprKind.INT_VAL, value='1'),
        right=Expression(kind=ExprKind.NUM_VAL, value='2.0'),
    )
    assert context.infer_type(int_add) == 'int'
    assert context.infer_type(float_add) == 'float'

# ** test: infer_type_string_concatenation_and_repetition
def test_infer_type_string_concatenation_and_repetition() -> None:
    '''
    Test that string addition and string repetition infer str.
    '''

    # str+str and str*int are the shallow string cases.
    context = ConformanceContext()
    text = Expression(kind=ExprKind.STR_VAL, value='a')
    integer = Expression(kind=ExprKind.INT_VAL, value='2')
    concatenated = Expression(kind=ExprKind.ADD, left=text, right=text)
    repeated = Expression(kind=ExprKind.MUL, left=text, right=integer)
    assert context.infer_type(concatenated) == 'str'
    assert context.infer_type(repeated) == 'str'

# ** test: lookup_type_walks_scope_chain
def test_lookup_type_walks_scope_chain() -> None:
    '''
    Test that name lookup walks from the inner scope to the outer scope.
    '''

    # The inner scope shadows the outer annotation for the same name.
    outer = ScopeAggregate(name='module', kind=SYMBOL_KIND_MODULE, path='module')
    outer.add_symbol(Symbol(
        name='x',
        kind=SYMBOL_KIND_VARIABLE,
        scope_path='module',
        type_annotation='str',
    ))
    inner = ScopeAggregate(name='execute', kind=SYMBOL_KIND_METHOD, path='module.Ping.execute')
    inner.add_symbol(Symbol(
        name='x',
        kind=SYMBOL_KIND_VARIABLE,
        scope_path='module.Ping.execute',
        type_annotation='int',
    ))
    context = ConformanceContext(scope_stack=[outer, inner])
    assert context.lookup_type(Expression(kind=ExprKind.NAME, name='x')) == 'int'

# ** test: lookup_type_self_attribute_uses_class_scope
def test_lookup_type_self_attribute_uses_class_scope() -> None:
    '''
    Test that a self attribute uses the enclosing class scope.
    '''

    # self.x ignores a method-local x and reads the class attribute.
    class_scope = ScopeAggregate(name='Ping', kind=SYMBOL_KIND_CLASS_DEF, path='module.Ping')
    class_scope.add_symbol(Symbol(
        name='x',
        kind=SYMBOL_KIND_VARIABLE,
        scope_path='module.Ping',
        type_annotation='str',
    ))
    method_scope = ScopeAggregate(
        name='execute',
        kind=SYMBOL_KIND_METHOD,
        path='module.Ping.execute',
    )
    method_scope.add_symbol(Symbol(
        name='x',
        kind=SYMBOL_KIND_VARIABLE,
        scope_path='module.Ping.execute',
        type_annotation='int',
    ))
    context = ConformanceContext(scope_stack=[class_scope, method_scope])
    assert context.lookup_type(Expression(kind=ExprKind.NAME, name='self.x')) == 'str'

# ** test: types_compatible_widening
def test_types_compatible_widening() -> None:
    '''
    Test that float accepts int and the reverse is false.
    '''

    # Widening is one direction only.
    context = ConformanceContext()
    assert context.types_compatible('float', 'int') is True
    assert context.types_compatible('int', 'float') is False

# ** test: child_scope_path_joins_with_dot
def test_child_scope_path_joins_with_dot() -> None:
    '''
    Test that child scope paths join with a dot, including a nested path.
    '''

    # Module plus class, then that path plus a method.
    assert child_scope_path('module', 'Ping') == 'module.Ping'
    assert child_scope_path('module.Ping', 'execute') == 'module.Ping.execute'

# ** test: walk_statements_dispatches_to_overridden_handlers
def test_walk_statements_dispatches_to_overridden_handlers() -> None:
    '''
    Test that declaration, expression, and return statements dispatch to overrides.
    '''

    # Three statement kinds reach the recording overrides in order.
    decl = Statement(kind=StatementKind.DECL)
    expr = Statement(kind=StatementKind.EXPR)
    returned = Statement(kind=StatementKind.RETURN)
    walker = _RecordingWalker()
    walker.walk_statements([decl, expr, returned])
    assert walker.seen == [('decl', decl), ('expr', expr), ('return', returned)]

# ** test: walk_statements_unhandled_kind_is_a_no_op
def test_walk_statements_unhandled_kind_is_a_no_op() -> None:
    '''
    Test that an unoverridden statement kind does not raise.
    '''

    # Import and if statements use the default no-op handlers.
    walker = _RecordingWalker()
    walker.walk_statements([
        Statement(kind=StatementKind.IF_ELSE),
        Statement(kind=StatementKind.IMPORT),
    ])
    assert walker.seen == []

# ** test: handle_artifact_and_snippet_recurse_into_body
def test_handle_artifact_and_snippet_recurse_into_body() -> None:
    '''
    Test that artifact and snippet wrappers recurse into their bodies.
    '''

    # Nested declaration and expression statements are visited through the wrappers.
    decl = Statement(kind=StatementKind.DECL)
    expr = Statement(kind=StatementKind.EXPR)
    artifact = Statement(kind=StatementKind.ARTIFACT, body=[decl])
    snippet = Statement(kind=StatementKind.SNIPPET, body=[expr])
    walker = _RecordingWalker()
    walker.walk_statements([artifact, snippet])
    assert walker.seen == [('decl', decl), ('expr', expr)]

# ** test: entering_child_scope_pushes_and_pops_when_found
def test_entering_child_scope_pushes_and_pops_when_found() -> None:
    '''
    Test that a registered child scope is pushed and then popped.
    '''

    # The child path is the current scope path plus the entered name.
    parent = ScopeAggregate(name='module', kind=SYMBOL_KIND_MODULE, path='module')
    child = ScopeAggregate(name='Ping', kind=SYMBOL_KIND_CLASS_DEF, path='module.Ping')
    walker = StatementWalker(scopes={'module.Ping': child})
    walker.scope_stack.append(parent)
    with walker.entering_child_scope('Ping') as entered:
        assert entered is child
        assert walker.current_scope is child

    # The child is popped when the context exits.
    assert walker.current_scope is parent

# ** test: entering_child_scope_yields_none_when_not_found
def test_entering_child_scope_yields_none_when_not_found() -> None:
    '''
    Test that a missing child yields None without pushing.
    '''

    # An unregistered name does not change the stack.
    parent = ScopeAggregate(name='module', kind=SYMBOL_KIND_MODULE, path='module')
    walker = StatementWalker()
    walker.scope_stack.append(parent)
    with walker.entering_child_scope('Missing') as entered:
        assert entered is None
        assert walker.current_scope is parent
    assert walker.scope_stack == [parent]

# ** test: apply_provisions_invokes_matching_callables
def test_apply_provisions_invokes_matching_callables() -> None:
    '''
    Test that only provisions for the visit hook are invoked.
    '''

    # The return provision is not invoked for an expression visit.
    calls = []

    class _RecordingSpec(Specification):
        '''
        A specification that records that it was called.
        '''

        def evaluate(self, candidate, context):
            '''
            Record this provision id.

            :param candidate: The ignored candidate.
            :param context: The ignored context.
            :return: No findings.
            '''

            del candidate, context
            calls.append(self.id)
            return []

    matched = _RecordingSpec(id='matched', applies_to='expression')
    skipped = _RecordingSpec(id='skipped', applies_to='return')
    walker = StatementWalker(provisions=[matched, skipped])
    result = walker.apply_provisions('expression', None, None)
    assert calls == ['matched']
    assert result == [[]]

# ** test: specification_call_delegates_to_evaluate
def test_specification_call_delegates_to_evaluate() -> None:
    '''
    Test that calling a specification equals evaluating it.
    '''

    # The callable contract returns the same findings as evaluate.
    spec = _Named(id='named', applies_to='expression')
    assert spec(None, None) == spec.evaluate(None, None)

# ** test: snake_to_pascal_acronyms
def test_snake_to_pascal_acronyms() -> None:
    '''
    Test snake_to_pascal for an ordinary name and the di acronym.
    '''

    # Ordinary words capitalize; di stays fully capitalized.
    assert snake_to_pascal('add_error') == 'AddError'
    assert snake_to_pascal('di_service') == 'DIService'

# ** test: unique_kind1_specifications_skip_non_matching_candidates
def test_unique_kind1_specifications_skip_non_matching_candidates() -> None:
    '''
    Test that each unique Kind 1 class subclasses Specification and skips a non-match.
    '''

    # A plain declaration fails every header and member skip predicate.
    header = ArtifactDeclaration(name='other')
    context = ConformanceContext()
    name_expr = Expression(kind=ExprKind.NAME, name='x')
    classes = [
        ImportGroupSpecification,
        SectionClassNameSpecification,
        FunctionSectionNameSpecification,
        AttributeMemberSpecification,
        MethodMemberSpecification,
        AssignmentTypeSpecification,
        BinaryOpTypeSpecification,
        ReturnBinaryOpTypeSpecification,
        EventSectionSpecification,
        GroupSectionAgreementSpecification,
        ConstantSectionNameSpecification,
        DomainAttributeSpecification,
        MapperRolesAttributeSpecification,
        InterfaceAbstractMethodSpecification,
        DIAbstractMethodSpecification,
        ContextManagerPairingSpecification,
        ReposCrudMethodSpecification,
    ]
    for spec_cls in classes:
        assert issubclass(spec_cls, Specification)
        spec = spec_cls(id='rule', applies_to='artifact_header')
        candidate = name_expr if 'Type' in spec_cls.__name__ and 'Section' not in spec_cls.__name__ else header
        if spec_cls is ReturnBinaryOpTypeSpecification:
            candidate = Statement(kind=StatementKind.PASS)
        assert spec.evaluate(candidate, context) == []

    # Member-name capture stays out of scope.
    assert extract_member_name_from_metadata(header) is None

# ** test: production_context_finds_enclosing_scope
def test_production_context_finds_enclosing_scope() -> None:
    '''
    Test that find_enclosing_scope walks inner to outer for a kind.
    '''

    # The method scope is inner, so the class scope is still found behind it.
    class_scope = ScopeAggregate(name='Ping', kind=SYMBOL_KIND_CLASS_DEF, path='module.Ping')
    method_scope = ScopeAggregate(
        name='execute',
        kind=SYMBOL_KIND_METHOD,
        path='module.Ping.execute',
    )
    context = ProductionContext(scope_stack=[class_scope, method_scope])
    assert context.find_enclosing_scope(SYMBOL_KIND_CLASS_DEF) is class_scope
    assert context.find_enclosing_scope('missing') is None

# ** test: rewrite_context_stores_host_arguments
def test_rewrite_context_stores_host_arguments() -> None:
    '''
    Test that RewriteContext stores host, qualifier, event, and accumulator.
    '''

    # Each constructor argument is stored without interpretation.
    context = RewriteContext(
        host='generator',
        qualifier='static',
        event='compile',
        accumulator=[],
    )
    assert context.host == 'generator'
    assert context.qualifier == 'static'
    assert context.event == 'compile'
    assert context.accumulator == []
