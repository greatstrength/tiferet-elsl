"""Domain – Provision Domain Objects Tests"""

# *** imports

# ** core
import ast
import inspect
from pathlib import Path
from typing import Callable, ClassVar, Optional, get_origin

# ** infra
import pytest
from pydantic import ValidationError

# ** app
from compiler.blueprints.core import build_cache
from compiler.contexts.provision import COMPILER_PROVISION_CACHE_PREFIX
from compiler.utils import codegen, core, optimizer, semantic, typecheck
from compiler.utils.core import (
    AppImportSpecification,
    ConformanceContext,
    PermittedGroupSpecification,
    ProductionContext,
    RequiredBaseSpecification,
    RewriteContext,
    StatementWalker,
    declares_bound_domain_type,
)
from compiler.utils.semantic import SymbolTableBuilder
from compiler.utils.typecheck import ConformanceChecker
from ..provision import (
    PROVISION_KIND_PRODUCTION,
    PROVISION_KIND_REWRITE,
    PROVISION_KIND_SPECIFICATION,
    AllOf,
    AnyOf,
    Not,
    Production,
    Provision,
    ProvisionRegistration,
    Rewrite,
    Specification,
)

# *** tests

# ** test: provision_constructs_and_matches_hook
def test_provision_constructs_and_matches_hook() -> None:
    '''
    Test that a provision stores its hook and rejects an unknown field.
    '''

    # A provision is constructible and matches only its hook.
    provision = Provision(id='r', applies_to='expression')
    assert provision.attaches_to('expression') is True
    assert provision.attaches_to('member') is False
    with pytest.raises(NotImplementedError):
        provision(None, None)

    # extra='forbid' rejects an undeclared field.
    with pytest.raises(ValidationError):
        Provision(id='r', applies_to='expression', extra='x')

# ** test: kinds_are_abstract_direct_subclasses
def test_kinds_are_abstract_direct_subclasses() -> None:
    '''
    Test that each kind extends Provision directly and cannot be instantiated.
    '''

    # Each kind is a direct Provision subclass and stays abstract.
    for kind in (Specification, Production, Rewrite):
        assert kind.__bases__[0] is Provision
        with pytest.raises(TypeError):
            kind(id='r', applies_to='expression')

    # No provision writes findings by printing, logging, or formatting them.
    for cls in (Provision, Specification, Production, Rewrite, AllOf, AnyOf, Not):
        for name in ('print', 'log', 'format'):
            assert name not in cls.__dict__

# ** test: concrete_rules_extend_one_kind
def test_concrete_rules_extend_one_kind() -> None:
    '''
    Test that every concrete rule extends exactly one kind, never Provision.
    '''

    # Rule classes stay in the modules that already hold them.
    kinds = (Specification, Production, Rewrite)
    for module in (core, semantic, codegen, optimizer):
        for obj in vars(module).values():
            if not inspect.isclass(obj) or obj.__module__ != module.__name__:
                continue
            if not issubclass(obj, Provision):
                continue

            # The direct base is one kind, and the class defines no constructor.
            matched = [kind for kind in kinds if kind in obj.__bases__]
            assert matched == [next(kind for kind in kinds if issubclass(obj, kind))]
            assert Provision not in obj.__bases__
            assert '__init__' not in obj.__dict__

            # Class constants are ClassVar annotations, not model fields.
            for name in obj.__dict__:
                if not name.isupper():
                    continue
                annotation = obj.__annotations__[name]
                assert get_origin(annotation) is ClassVar
                assert name not in obj.model_fields

# ** test: retired_names_are_absent
def test_retired_names_are_absent() -> None:
    '''
    Test that no compiler module defines the retired class or walker method.
    '''

    # Build the retired names so this file does not reintroduce them.
    retired_class = 'Attach' + 'ment'
    retired_method = 'apply_' + 'attachments'
    root = Path(__file__).resolve().parents[2]
    for path in root.rglob('*.py'):
        tree = ast.parse(path.read_text(encoding='utf-8'))
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                assert node.name != retired_class
                for item in node.body:
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        assert item.name != retired_method
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                names = [alias.name for alias in node.names]
                names.extend(alias.asname for alias in node.names if alias.asname)
                assert retired_class not in names

    # Utils modules import provisions through mappers, not domain.
    for path in (root / 'utils').glob('*.py'):
        tree = ast.parse(path.read_text(encoding='utf-8'))
        for node in ast.walk(tree):
            if not isinstance(node, ast.ImportFrom) or not node.level or not node.module:
                continue
            assert node.module.split('.')[0] != 'domain'

# ** test: combinators_keep_child_instances
def test_combinators_keep_child_instances() -> None:
    '''
    Test that AllOf keeps its child and Not requires its spec.
    '''

    # The child instance is stored, not copied.
    child = AppImportSpecification(
        id='child',
        applies_to='member',
        error_code='INVALID_DOMAIN_APP_IMPORT',
        message='found {module_path}',
    )
    combo = AllOf(id='a', applies_to='member', specs=[child])
    assert combo.specs[0] is child

    # Not has no default child.
    with pytest.raises(ValidationError):
        Not(id='n', applies_to='member')

# ** test: keyword_call_sites_keep_field_values
def test_keyword_call_sites_keep_field_values() -> None:
    '''
    Test that existing keyword constructions expose the same field values.
    '''

    # The domain rows are instantiated from the seeded cache, not a module list.
    cache = build_cache()
    domain = ConformanceChecker(
        {},
        cache,
        'domain.',
        COMPILER_PROVISION_CACHE_PREFIX,
    ).provisions
    permitted = next(
        item for item in domain
        if item.id == 'domain.permitted_group'
    )
    app_import = next(
        item for item in domain
        if item.id == 'domain.app_import'
    )
    assert isinstance(permitted, PermittedGroupSpecification)
    assert permitted.permitted_groups == frozenset({
        'imports',
        'constants',
        'functions',
        'classes',
        'models',
        'exports',
    })
    assert permitted.error_code == 'DISALLOWED_DOMAIN_GROUP'
    assert permitted.module_label == 'a domain module'
    assert isinstance(app_import, AppImportSpecification)
    assert app_import.allowed_components == frozenset({'assets'})
    assert app_import.allow_siblings is True
    assert app_import.allow_framework_root_alias is False

    # The contexts row still carries a callable predicate, not a string.
    contexts = ConformanceChecker(
        {},
        cache,
        'contexts.',
        COMPILER_PROVISION_CACHE_PREFIX,
    ).provisions
    required = next(
        item for item in contexts
        if item.id == 'contexts.base_class'
    )
    assert isinstance(required, RequiredBaseSpecification)
    assert required.predicate is declares_bound_domain_type
    assert callable(required.predicate)
    assert RequiredBaseSpecification.__annotations__['predicate'] == Optional[Callable[..., bool]]

# ** test: walker_and_contexts_are_not_provisions
def test_walker_and_contexts_are_not_provisions() -> None:
    '''
    Test that the walker and host contexts stay outside the provision hierarchy.
    '''

    # None of the host types is a provision. The walker exposes the new names.
    for host in (
        StatementWalker,
        ConformanceContext,
        ProductionContext,
        RewriteContext,
    ):
        assert not issubclass(host, Provision)
    walker = StatementWalker()
    assert walker.provisions == []
    assert callable(walker.apply_provisions)

# ** test: registration_fields_and_reinjected_id
def test_registration_fields_and_reinjected_id() -> None:
    '''
    Test that a registration accepts a reinjected id and no other keys.
    '''

    # The field set is closed.
    assert set(ProvisionRegistration.model_fields) == {
        'id',
        'kind',
        'applies_to',
        'module_path',
        'class_name',
        'parameters',
    }

    # The asset body omits id. The seeder reinjects the group-dict key.
    body = {
        'kind': PROVISION_KIND_SPECIFICATION,
        'applies_to': 'artifact_header',
        'module_path': 'compiler.utils.core',
        'class_name': 'ImportGroupSpecification',
    }
    key = 'common.import_group'
    registration = ProvisionRegistration.model_validate({**body, 'id': key})
    assert registration.id == key
    assert registration.parameters == {}

    # An undeclared key still fails under extra='forbid'.
    with pytest.raises(ValidationError):
        ProvisionRegistration.model_validate({**body, 'id': key, 'extra': 'x'})

# ** test: registration_kind_and_parameters
def test_registration_kind_and_parameters() -> None:
    '''
    Test that kind is closed and parameters round-trip data only.
    '''

    # The three constants are the closed kind vocabulary.
    assert PROVISION_KIND_SPECIFICATION == 'specification'
    assert PROVISION_KIND_PRODUCTION == 'production'
    assert PROVISION_KIND_REWRITE == 'rewrite'
    with pytest.raises(ValidationError):
        ProvisionRegistration(
            id='k',
            kind='visitor',
            applies_to='expression',
            module_path='compiler.utils.core',
            class_name='ImportGroupSpecification',
        )

    # A bool, a list of strings, and a dotted string stay data.
    dotted = 'compiler.utils.core.declares_bound_domain_type'
    registration = ProvisionRegistration(
        id='k',
        kind=PROVISION_KIND_REWRITE,
        applies_to='imports',
        module_path='compiler.utils.codegen',
        class_name='ImportsGroupRewrite',
        parameters={
            'allow_siblings': True,
            'allowed_components': ['assets', 'domain'],
            'predicate': dotted,
        },
    )
    assert registration.parameters['allow_siblings'] is True
    assert registration.parameters['allowed_components'] == ['assets', 'domain']
    assert registration.parameters['predicate'] == dotted
    assert isinstance(registration.parameters['predicate'], str)

# ** test: registration_is_not_a_provision
def test_registration_is_not_a_provision() -> None:
    '''
    Test that a registration is not a provision and defines no public method.
    '''

    # Inherited model methods are not methods of this class.
    own_public = [
        name for name, value in ProvisionRegistration.__dict__.items()
        if not name.startswith('_') and callable(value)
    ]
    assert not issubclass(ProvisionRegistration, Provision)
    assert own_public == []

# ** test: rule_sets_still_construct
def test_rule_sets_still_construct() -> None:
    '''
    Test that the published rule sets and production sets still construct.
    '''

    # The lists are gone. The seeded cache still constructs both kinds.
    assert not hasattr(typecheck, 'COMMON_RULE_SET')
    assert not hasattr(semantic, 'BUILDER_PRODUCTION_SET')
    cache = build_cache()
    common = ConformanceChecker(
        {},
        cache,
        'common.',
        COMPILER_PROVISION_CACHE_PREFIX,
    ).provisions
    productions = SymbolTableBuilder(
        cache,
        COMPILER_PROVISION_CACHE_PREFIX,
    ).productions
    assert common
    assert all(isinstance(item, Specification) for item in common)
    assert productions
    assert all(isinstance(item, Production) for item in productions)
