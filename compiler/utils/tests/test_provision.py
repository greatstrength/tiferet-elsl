"""Compiler Provision Instantiation Tests"""

# *** imports

# ** core
import ast
import inspect
from pathlib import Path

# ** infra
import pytest

# ** app
from ...blueprints.core import build_cache
from ...contexts.provision import COMPILER_PROVISION_CACHE_PREFIX
from ...domain.provision import ProvisionRegistration
from ...mappers import Specification
import compiler.utils as utils
from ..core import (
    ImportGroupSpecification,
    RequiredBaseSpecification,
    declares_bound_domain_type,
)
from ..provision import (
    BOUND_DOMAIN_TYPE_PREDICATE,
    PROVISION_CLASS_MISMATCH,
    PROVISION_IMPORT_FAILED,
    PROVISION_INIT_FAILED,
    PROVISION_KIND_MISMATCH,
    instantiate_provision,
)
from ..semantic import (
    ImportFromProduction,
    ImportProduction,
    SymbolTableBuilder,
)
from ..typecheck import ConformanceChecker
import compiler.events.semantic as semantic_events
import compiler.events.typecheck as typecheck_events
import compiler.utils.core as core

# *** functions

# ** function: _registration
def _registration(class_name: str = 'ImportGroupSpecification',
        kind: str = 'specification',
        module_path: str = 'compiler.utils.core',
        parameters: dict = None,
        registration_id: str = 'common.import_group') -> ProvisionRegistration:
    '''
    Build one registration for an instantiation test.

    :param class_name: The class to import.
    :type class_name: str
    :param kind: The provision kind.
    :type kind: str
    :param module_path: The module that defines the class.
    :type module_path: str
    :param parameters: Constructor data beyond id and applies_to.
    :type parameters: dict
    :param registration_id: The registration id.
    :type registration_id: str
    :return: The registration.
    :rtype: ProvisionRegistration
    '''

    # The id is the registration field the constructor must receive.
    return ProvisionRegistration(
        id=registration_id,
        kind=kind,
        applies_to='artifact_header',
        module_path=module_path,
        class_name=class_name,
        parameters=parameters or {},
    )

# *** tests

# ** test: subclass_is_constructed_with_registration_id
def test_subclass_is_constructed_with_registration_id() -> None:
    '''
    Test that a subclass receives id, applies_to, and parameters.
    '''

    # The constructed id is registration.id, not a body field.
    registration = _registration()
    instance, finding = instantiate_provision(registration)
    assert finding is None
    assert isinstance(instance, ImportGroupSpecification)
    assert instance.id == registration.id
    assert instance.applies_to == registration.applies_to

# ** test: non_subclass_is_a_class_mismatch
def test_non_subclass_is_a_class_mismatch() -> None:
    '''
    Test that a non-subclass is a finding and is not raised.
    '''

    # A production class is not a specification.
    registration = _registration(
        class_name='ImportProduction',
        module_path='compiler.utils.semantic',
    )
    instance, finding = instantiate_provision(registration)
    assert instance is None
    assert finding['error_code'] == PROVISION_CLASS_MISMATCH
    assert registration.id in finding['message']
    assert finding['scope_path'] == registration.id
    assert 'lineno' not in finding

# ** test: missing_module_is_an_import_failure
def test_missing_module_is_an_import_failure() -> None:
    '''
    Test that a missing module is PROVISION_IMPORT_FAILED.
    '''

    # The import failure stays a finding.
    registration = _registration(module_path='compiler.utils.missing_module')
    instance, finding = instantiate_provision(registration)
    assert instance is None
    assert finding['error_code'] == PROVISION_IMPORT_FAILED
    assert 'lineno' not in finding

# ** test: constructor_error_is_init_failed
def test_constructor_error_is_init_failed() -> None:
    '''
    Test that a repeated id inside parameters is PROVISION_INIT_FAILED.
    '''

    # The constructor sees id twice and is not allowed to raise out.
    registration = _registration(parameters={'id': 'other'})
    instance, finding = instantiate_provision(registration)
    assert instance is None
    assert finding['error_code'] == PROVISION_INIT_FAILED
    assert finding['scope_path'] == registration.id

# ** test: predicate_string_is_resolved_without_mutating_registration
def test_predicate_string_is_resolved_without_mutating_registration() -> None:
    '''
    Test that the one predicate string is passed as the function.
    '''

    # The registration keeps the catalog string after construction.
    registration = _registration(
        class_name='RequiredBaseSpecification',
        registration_id='contexts.base_class',
        parameters={
            'section_keyword': 'context',
            'error_code': 'CONTEXT_MISSING_BASE_CONTEXT',
            'message': "Context class '{class_name}' must extend 'BaseContext'",
            'required_base': 'BaseContext',
            'predicate': BOUND_DOMAIN_TYPE_PREDICATE,
        },
    )
    instance, finding = instantiate_provision(registration)
    assert finding is None
    assert isinstance(instance, RequiredBaseSpecification)
    assert instance.predicate is declares_bound_domain_type
    assert registration.parameters['predicate'] == BOUND_DOMAIN_TYPE_PREDICATE
    assert isinstance(registration.parameters['predicate'], str)

# ** test: failed_predicate_import_does_not_construct
def test_failed_predicate_import_does_not_construct(monkeypatch) -> None:
    '''
    Test that a failed predicate import is not a constructor error.

    :param monkeypatch: The pytest monkeypatch fixture.
    :type monkeypatch: object
    '''

    # Remove the attribute so the import of that name fails.
    called = []

    def _init(self, *args, **kwargs):
        '''
        Record a constructor call.

        :param args: Positional constructor arguments.
        :param kwargs: Keyword constructor arguments.
        :return: None
        '''

        called.append(kwargs)
        return object.__init__(self)

    monkeypatch.delattr(core, 'declares_bound_domain_type')
    monkeypatch.setattr(RequiredBaseSpecification, '__init__', _init)
    registration = _registration(
        class_name='RequiredBaseSpecification',
        registration_id='contexts.base_class',
        parameters={'predicate': BOUND_DOMAIN_TYPE_PREDICATE},
    )
    instance, finding = instantiate_provision(registration)
    assert instance is None
    assert finding['error_code'] == PROVISION_IMPORT_FAILED
    assert called == []

# ** test: predicate_string_under_another_key_is_not_resolved
def test_predicate_string_under_another_key_is_not_resolved() -> None:
    '''
    Test that the same dotted string under another key stays a string.
    '''

    # message is a string field. It is not the predicate key.
    registration = _registration(
        class_name='RequiredBaseSpecification',
        registration_id='contexts.base_class',
        parameters={
            'section_keyword': 'context',
            'error_code': 'CONTEXT_MISSING_BASE_CONTEXT',
            'message': BOUND_DOMAIN_TYPE_PREDICATE,
            'required_base': 'BaseContext',
        },
    )
    instance, finding = instantiate_provision(registration)
    assert finding is None
    assert instance.message == BOUND_DOMAIN_TYPE_PREDICATE
    assert not callable(instance.message)

# ** test: builder_rejects_wrong_kind_and_replaced_class
def test_builder_rejects_wrong_kind_and_replaced_class() -> None:
    '''
    Test that a wrong builder kind is not attached and a replacement wins.
    '''

    # Seed the catalog, then replace one builder id and add a wrong kind.
    cache = build_cache()
    prefix = COMPILER_PROVISION_CACHE_PREFIX
    replacement = ProvisionRegistration(
        id='builder.import',
        kind='production',
        applies_to='import',
        module_path='compiler.utils.semantic',
        class_name='ImportFromProduction',
    )
    wrong = ProvisionRegistration(
        id='builder.bad',
        kind='specification',
        applies_to='artifact_header',
        module_path='compiler.utils.core',
        class_name='ImportGroupSpecification',
    )
    rewrite = ProvisionRegistration(
        id='rewrite.keep',
        kind='rewrite',
        applies_to='imports',
        module_path='compiler.utils.core',
        class_name='ImportGroupSpecification',
    )
    cache.set('builder.import', replacement, *prefix)
    cache.set(wrong.id, wrong, *prefix)
    cache.set(rewrite.id, rewrite, *prefix)
    builder = SymbolTableBuilder(cache, prefix)
    attached = {item.id: item for item in builder.productions}

    # The replacement class is attached. The wrong kind and the rewrite are not.
    assert isinstance(attached['builder.import'], ImportFromProduction)
    assert not isinstance(attached['builder.import'], ImportProduction)
    assert 'builder.bad' not in attached
    assert 'rewrite.keep' not in attached
    assert any(
        finding['error_code'] == PROVISION_KIND_MISMATCH
        and finding['scope_path'] == 'builder.bad'
        for finding in builder.provision_findings
    )
    assert all(
        finding['scope_path'] != 'rewrite.keep'
        for finding in builder.provision_findings
    )

# ** test: checker_does_not_attach_another_selector
def test_checker_does_not_attach_another_selector() -> None:
    '''
    Test that a checker attaches only specifications under its selector.
    '''

    # event. does not attach common. specifications.
    cache = build_cache()
    checker = ConformanceChecker(
        {},
        cache,
        'event.',
        COMPILER_PROVISION_CACHE_PREFIX,
    )
    assert checker.provisions
    assert all(item.id.startswith('event.') for item in checker.provisions)
    assert all(isinstance(item, Specification) for item in checker.provisions)
    assert not any(item.id.startswith('common.') for item in checker.provisions)
    assert not hasattr(checker, 'rule_set')

# ** test: readers_and_events_do_not_import_contexts
def test_readers_and_events_do_not_import_contexts() -> None:
    '''
    Test that utils and events do not import the cache builder or the overlay.
    '''

    # Import lines are the boundary. Comments may still describe the caller.
    root = Path(__file__).resolve().parents[2]
    for relative in (
        'utils/semantic.py',
        'utils/typecheck.py',
        'utils/provision.py',
        'events/semantic.py',
        'events/typecheck.py',
    ):
        tree = ast.parse((root / relative).read_text(encoding='utf-8'))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                names = [alias.name for alias in node.names]
                module = node.module or ''
            elif isinstance(node, ast.Import):
                names = [alias.name for alias in node.names]
                module = ''
            else:
                continue
            rendered = ' '.join([module, *names])
            assert 'compiler.contexts' not in rendered
            assert 'compiler.blueprints' not in rendered
            assert 'apply_provision_overlay' not in rendered
            assert 'ProvisionConfigRepository' not in rendered
            assert 'build_cache' not in rendered
    assert 'build_cache' not in inspect.getsource(semantic_events.PerformSemanticAnalysis)
    assert 'build_cache' not in inspect.getsource(typecheck_events.ConformanceEvent)
    assert not hasattr(utils, 'instantiate_provision')
