"""Domain – Codegen Domain Objects Tests"""

# *** imports

# ** infra
import pytest
from pydantic import ValidationError

# ** app
from .. import codegen as codegen_module
from ..codegen import (
    CallableData,
    CollaboratorData,
    ComponentEnvelope,
    ConstantData,
    EventData,
    GroupEntry,
    ImportEntry,
    SnippetData,
)

# *** tests

# ** test: import_entry_required_fields
def test_import_entry_required_fields() -> None:
    '''
    Test that an import entry requires only `src` and defaults `tgts` to an empty list.

    :return: None
    :rtype: None
    '''

    # Construct an import entry with only the module path.
    entry = ImportEntry(src='tiferet.events')

    # Assert the path is stored and targets default empty.
    assert entry.src == 'tiferet.events'
    assert entry.tgts == []

# ** test: import_entry_with_tgts
def test_import_entry_with_tgts() -> None:
    '''
    Test that supplied import targets persist.

    :return: None
    :rtype: None
    '''

    # Construct an import entry with explicit targets.
    entry = ImportEntry(src='typing', tgts=['List', 'Dict'])

    # Assert the targets persist in order.
    assert entry.tgts == ['List', 'Dict']

# ** test: import_entry_missing_src_raises
def test_import_entry_missing_src_raises() -> None:
    '''
    Test that a missing `src` raises ValidationError.

    :return: None
    :rtype: None
    '''

    # Omitting the module path must fail validation.
    with pytest.raises(ValidationError):
        ImportEntry()

# ** test: snippet_data_defaults
def test_snippet_data_defaults() -> None:
    '''
    Test that a snippet defaults both lists to empty.

    :return: None
    :rtype: None
    '''

    # Construct a snippet with no arguments.
    snippet = SnippetData()

    # Assert both collections default empty.
    assert snippet.comments == []
    assert snippet.statements == []

# ** test: snippet_data_with_values
def test_snippet_data_with_values() -> None:
    '''
    Test that snippet comments and statements persist.

    :return: None
    :rtype: None
    '''

    # Construct a snippet with both lists populated.
    snippet = SnippetData(
        comments=['Retrieve the feature.'],
        statements=["feature = self.feature_service.get(id)"],
    )

    # Assert both lists persist.
    assert snippet.comments == ['Retrieve the feature.']
    assert snippet.statements == ["feature = self.feature_service.get(id)"]

# ** test: constant_data_required_value
def test_constant_data_required_value() -> None:
    '''
    Test that a constant stores `value` and rejects a missing value.

    :return: None
    :rtype: None
    '''

    # A supplied initializer is stored unchanged.
    constant = ConstantData(value="'X'")
    assert constant.value == "'X'"

    # Omitting the initializer must fail validation.
    with pytest.raises(ValidationError):
        ConstantData()

# ** test: callable_data_defaults
def test_callable_data_defaults() -> None:
    '''
    Test that callable collections default empty and optional scalars default to None.

    :return: None
    :rtype: None
    '''

    # Construct a callable with no arguments.
    callable_data = CallableData()

    # Assert list fields default empty and optional scalars are None.
    assert callable_data.deco == []
    assert callable_data.params == []
    assert callable_data.returns == []
    assert callable_data.snpt == []
    assert callable_data.desc is None
    assert callable_data.idempotent is None

# ** test: callable_data_with_values
def test_callable_data_with_values() -> None:
    '''
    Test that every callable field persists, including `idempotent=True`.

    :return: None
    :rtype: None
    '''

    # Build a body snippet to nest under the callable.
    snippet = SnippetData(
        comments=['Return the feature.'],
        statements=['return feature'],
    )

    # Construct a callable with every field set.
    callable_data = CallableData(
        desc='Retrieve a feature by ID.',
        deco=['@DomainEvent.parameters_required'],
        params=['id:str:true::The feature ID.'],
        returns=['Feature:The Feature domain object.'],
        snpt=[snippet],
        idempotent=True,
    )

    # Assert every field persists.
    assert callable_data.desc == 'Retrieve a feature by ID.'
    assert callable_data.deco == ['@DomainEvent.parameters_required']
    assert callable_data.params == ['id:str:true::The feature ID.']
    assert callable_data.returns == ['Feature:The Feature domain object.']
    assert callable_data.snpt == [snippet]
    assert callable_data.idempotent is True

# ** test: event_data_required_fields
def test_event_data_required_fields() -> None:
    '''
    Test that `EventData` requires only `name` and defaults collections and extras.

    :return: None
    :rtype: None
    '''

    # Construct a class payload with only its name.
    event = EventData(name='Ping')

    # Assert optional collections are empty and dialect extras are None.
    assert event.name == 'Ping'
    assert event.desc is None
    assert event.attributes == []
    assert event.injections == []
    assert event.execute is None
    assert event.methods == {}
    assert event.base is None
    assert event.maps is None
    assert event.kind is None
    assert event.implements is None
    assert event.collaborators == []

# ** test: event_data_with_all_fields
def test_event_data_with_all_fields() -> None:
    '''
    Test that class-payload fields persist, including dialect extras.

    :return: None
    :rtype: None
    '''

    # Build the nested execute method and a non-execute method.
    execute = CallableData(desc='Run the event.')
    format_method = CallableData(desc='Format the result.')
    collaborator = CollaboratorData(name='error_service', type='ErrorService')

    # Construct a class payload with every field set.
    event = EventData(
        name='GetFeature',
        desc='Retrieve a feature by its identifier.',
        attributes=[
            {'id': 'str'},
            {'count': {'type': 'int', 'init': '0'}},
        ],
        injections=[
            {
                'feature_service:FeatureService:true::The feature service.': {
                    'assign': [{'target': 'feature_service', 'value': 'feature_service'}],
                },
            },
        ],
        execute=execute,
        methods={'format': format_method},
        base='DomainEvent',
        maps='Feature',
        kind='aggregate',
        implements='FeatureService',
        collaborators=[collaborator],
    )

    # Assert the required persistence set and the dialect extras.
    assert event.desc == 'Retrieve a feature by its identifier.'
    assert event.attributes[0] == {'id': 'str'}
    assert event.attributes[1]['count']['init'] == '0'
    assert event.injections[0]['feature_service:FeatureService:true::The feature service.']['assign'][0]['target'] == 'feature_service'
    assert event.execute is execute
    assert event.methods['format'] is format_method
    assert event.base == 'DomainEvent'
    assert event.maps == 'Feature'
    assert event.kind == 'aggregate'
    assert event.implements == 'FeatureService'
    assert event.collaborators == [collaborator]

# ** test: event_data_missing_name_raises
def test_event_data_missing_name_raises() -> None:
    '''
    Test that constructing `EventData` without a name raises ValidationError.

    :return: None
    :rtype: None
    '''

    # Omitting the class name must fail validation.
    with pytest.raises(ValidationError):
        EventData()

# ** test: group_entry_ordered_qualifiers
def test_group_entry_ordered_qualifiers() -> None:
    '''
    Test that qualified groups with the same name coexist and omitted `qual` is None.

    :return: None
    :rtype: None
    '''

    # Build two qualified groups that repeat the same name, plus an unqualified one.
    ids = GroupEntry(name='constants', qual='ids')
    groups = GroupEntry(name='constants', qual='groups')
    plain = GroupEntry(name='constants')
    ordered = [ids, groups, plain]

    # Assert the qualifiers coexist in source order and the omitted qualifier is None.
    assert [entry.name for entry in ordered] == ['constants', 'constants', 'constants']
    assert ordered[0].qual == 'ids'
    assert ordered[1].qual == 'groups'
    assert plain.qual is None

# ** test: group_entry_payload_keys
def test_group_entry_payload_keys() -> None:
    '''
    Test that the nine payload dicts store independently.

    :return: None
    :rtype: None
    '''

    # Populate each payload dict with a distinct key.
    entry = GroupEntry(
        name='mixed',
        csts={'A': ConstantData(value="'A'")},
        fncs={'build': CallableData()},
        clss={'Helper': EventData(name='Helper')},
        mdls={'Token': EventData(name='Token')},
        mprs={'TokenAggregate': EventData(name='TokenAggregate')},
        ifcs={'TokenService': EventData(name='TokenService')},
        ctxs={'TokenContext': EventData(name='TokenContext')},
        repos={'TokenYamlRepository': EventData(name='TokenYamlRepository')},
        evts={'GetToken': EventData(name='GetToken')},
    )

    # Assert each payload keeps its own key and does not collapse into another dict.
    assert set(entry.csts) == {'A'}
    assert entry.csts['A'].value == "'A'"
    assert set(entry.fncs) == {'build'}
    assert set(entry.clss) == {'Helper'}
    assert set(entry.mdls) == {'Token'}
    assert set(entry.mprs) == {'TokenAggregate'}
    assert set(entry.ifcs) == {'TokenService'}
    assert set(entry.ctxs) == {'TokenContext'}
    assert set(entry.repos) == {'TokenYamlRepository'}
    assert set(entry.evts) == {'GetToken'}
    assert entry.csts is not entry.fncs
    assert entry.clss is not entry.evts

# ** test: component_envelope_required_fields
def test_component_envelope_required_fields() -> None:
    '''
    Test that an envelope requires `name` and `kind` and defaults the rest.

    :return: None
    :rtype: None
    '''

    # Construct an events envelope with only the required fields.
    envelope = ComponentEnvelope(name='error', kind='events')

    # Assert the summary is None and the collections default empty.
    assert envelope.name == 'error'
    assert envelope.kind == 'events'
    assert envelope.desc is None
    assert envelope.impt == {}
    assert envelope.grps == []

# ** test: component_envelope_not_event_only
def test_component_envelope_not_event_only() -> None:
    '''
    Test that an assets envelope stores constants and has no `evt_grp` attribute.

    :return: None
    :rtype: None
    '''

    # Construct a non-event envelope whose only group is constants.
    envelope = ComponentEnvelope(
        name='constants',
        kind='assets',
        grps=[
            GroupEntry(
                name='constants',
                csts={'FEATURE_NOT_FOUND_ID': ConstantData(value="'FEATURE_NOT_FOUND'")},
            ),
        ],
    )

    # Assert the component type is assets and there is no event-group field or class.
    assert envelope.kind == 'assets'
    assert envelope.grps[0].csts['FEATURE_NOT_FOUND_ID'].value == "'FEATURE_NOT_FOUND'"
    assert not hasattr(envelope, 'evt_grp')
    assert 'evt_grp' not in type(envelope).model_fields
    assert not hasattr(codegen_module, 'EventGroup')

# ** test: component_envelope_missing_kind_raises
def test_component_envelope_missing_kind_raises() -> None:
    '''
    Test that a missing `kind` or `name` raises ValidationError.

    :return: None
    :rtype: None
    '''

    # Omitting kind must fail validation.
    with pytest.raises(ValidationError):
        ComponentEnvelope(name='error')

    # Omitting name must fail validation.
    with pytest.raises(ValidationError):
        ComponentEnvelope(kind='events')
