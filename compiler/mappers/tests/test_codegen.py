"""Mapper – Codegen Accumulator Tests"""

# *** imports

# ** app
from ..codegen import (
    EventAccumulator,
    ImportEntryCollector,
    SnippetAccumulator,
)

# *** tests

# ** test: import_entry_collector_single_module
def test_import_entry_collector_single_module() -> None:
    '''
    Test that two adds for one module collapse to one entry.
    '''

    # Record two symbols from the same module.
    collector = ImportEntryCollector()
    collector.add('tiferet.events', 'Ping')
    collector.add('tiferet.events', 'Pong')

    # One row, with both symbols, in add order.
    assert collector.to_list() == [{
        'src': 'tiferet.events',
        'tgts': ['Ping', 'Pong'],
    }]

# ** test: import_entry_collector_multiple_modules
def test_import_entry_collector_multiple_modules() -> None:
    '''
    Test that distinct modules keep first-seen order and later symbols append.
    '''

    # See two modules, then add another symbol to the first.
    collector = ImportEntryCollector()
    collector.add('tiferet.domain', 'Error')
    collector.add('tiferet.events', 'Ping')
    collector.add('tiferet.domain', 'Feature')

    # First-seen order is preserved; the later symbol appends.
    assert collector.to_list() == [
        {
            'src': 'tiferet.domain',
            'tgts': ['Error', 'Feature'],
        },
        {
            'src': 'tiferet.events',
            'tgts': ['Ping'],
        },
    ]

# ** test: import_entry_collector_empty
def test_import_entry_collector_empty() -> None:
    '''
    Test that a fresh collector serializes to an empty list.
    '''

    # No adds have been recorded.
    collector = ImportEntryCollector()

    # The serialized form is an empty list, not None.
    assert collector.to_list() == []

# ** test: snippet_accumulator_add_and_to_dict
def test_snippet_accumulator_add_and_to_dict() -> None:
    '''
    Test that a filled snippet serializes as coms and stmt.
    '''

    # Record one comment and one statement.
    accumulator = SnippetAccumulator()
    accumulator.add_comment('Load the feature.')
    accumulator.add_statement('feature = self.feature_service.get(id)')

    # Serialization renames the domain fields and drops the domain keys.
    result = accumulator.to_dict()
    assert result == {
        'coms': ['Load the feature.'],
        'stmt': ['feature = self.feature_service.get(id)'],
    }
    assert 'comments' not in result
    assert 'statements' not in result

# ** test: snippet_accumulator_comments_only
def test_snippet_accumulator_comments_only() -> None:
    '''
    Test that comments alone omit stmt.
    '''

    # Record a comment and no statement.
    accumulator = SnippetAccumulator()
    accumulator.add_comment('Nothing to run.')

    # coms is present; stmt is absent.
    result = accumulator.to_dict()
    assert result == {'coms': ['Nothing to run.']}
    assert 'stmt' not in result

# ** test: snippet_accumulator_statements_only
def test_snippet_accumulator_statements_only() -> None:
    '''
    Test that statements alone omit coms.
    '''

    # Record a statement and no comment.
    accumulator = SnippetAccumulator()
    accumulator.add_statement('return feature')

    # stmt is present; coms is absent.
    result = accumulator.to_dict()
    assert result == {'stmt': ['return feature']}
    assert 'coms' not in result

# ** test: snippet_accumulator_empty_returns_none
def test_snippet_accumulator_empty_returns_none() -> None:
    '''
    Test that a snippet with no adds serializes to None.
    '''

    # A fresh accumulator has both lists empty.
    accumulator = SnippetAccumulator()

    # Absence is None, not an empty dict.
    assert accumulator.to_dict() is None

# ** test: snippet_accumulator_ignores_empty_statement
def test_snippet_accumulator_ignores_empty_statement() -> None:
    '''
    Test that blank statements do not create a snippet dict.
    '''

    # Record empty, space-only, and tab-only statements.
    accumulator = SnippetAccumulator()
    accumulator.add_statement('')
    accumulator.add_statement('   ')
    accumulator.add_statement('\t')

    # None of those statements is a body, so serialization is None.
    assert accumulator.to_dict() is None

# ** test: event_accumulator_to_dict_minimal
def test_event_accumulator_to_dict_minimal() -> None:
    '''
    Test that a name-only class payload omits execute.
    '''

    # Construct with the required name and no execute payload.
    result = EventAccumulator(name='Ping').to_dict()

    # Name is present; execute was never set.
    assert result['name'] == 'Ping'
    assert 'execute' not in result

# ** test: event_accumulator_omits_empty_optional_key
def test_event_accumulator_omits_empty_optional_key() -> None:
    '''
    Test that empty optional sections are omitted.
    '''

    # Defaults leave desc, attributes, injections, and methods empty.
    result = EventAccumulator(name='Ping').to_dict()

    # Empty sections are omitted rather than emitted as empty containers.
    assert 'desc' not in result
    assert 'attributes' not in result
    assert 'injections' not in result
    assert 'methods' not in result

# ** test: event_accumulator_add_attribute
def test_event_accumulator_add_attribute() -> None:
    '''
    Test that attributes without init serialize as name-to-type entries.
    '''

    # Record two attributes with no initializer.
    accumulator = EventAccumulator(name='Ping')
    accumulator.add_attribute('id', 'str')
    accumulator.add_attribute('count', 'int')

    # Each entry is the type name, not a nested type/init dict.
    assert accumulator.to_dict()['attributes'] == [
        {'id': 'str'},
        {'count': 'int'},
    ]

# ** test: event_accumulator_add_attribute_with_init
def test_event_accumulator_add_attribute_with_init() -> None:
    '''
    Test that an attribute with init serializes type and init together.
    '''

    # Record one attribute with an encoded initializer.
    accumulator = EventAccumulator(name='Ping')
    accumulator.add_attribute('x', 'str', init='Call(Field)')

    # The value nests type and init.
    assert accumulator.to_dict()['attributes'] == [{
        'x': {
            'type': 'str',
            'init': 'Call(Field)',
        },
    }]

# ** test: event_accumulator_add_injection
def test_event_accumulator_add_injection() -> None:
    '''
    Test that add_injection appends a spec-to-value entry.
    '''

    # Record one constructor injection.
    accumulator = EventAccumulator(name='Ping')
    value = {
        'assign': [{
            'target': 'feature_service',
            'value': 'feature_service',
        }],
    }
    accumulator.add_injection(
        'feature_service:FeatureService:true::The feature service.',
        value,
    )

    # The spec is the key and the value is stored unchanged.
    assert accumulator.to_dict()['injections'] == [{
        'feature_service:FeatureService:true::The feature service.': value,
    }]

# ** test: event_accumulator_set_execute
def test_event_accumulator_set_execute() -> None:
    '''
    Test that set_execute includes the payload under execute.
    '''

    # Store a codegen execute payload.
    accumulator = EventAccumulator(name='Ping')
    payload = {
        'desc': 'Runs the event.',
        'stmt': ['return None'],
    }
    accumulator.set_execute(payload)

    # The serialized execute value is that payload.
    assert accumulator.to_dict()['execute'] == payload

# ** test: event_accumulator_add_method
def test_event_accumulator_add_method() -> None:
    '''
    Test that add_method stores the payload under methods.
    '''

    # Store one non-execute method.
    accumulator = EventAccumulator(name='Ping')
    data = {'desc': 'Helps.'}
    accumulator.add_method('helper', data)

    # The method appears under its name.
    result = accumulator.to_dict()
    assert 'methods' in result
    assert result['methods']['helper'] == data

# ** test: event_accumulator_desc_included_when_set
def test_event_accumulator_desc_included_when_set() -> None:
    '''
    Test that a set class docstring is included as desc.
    '''

    # Construct with a stripped class docstring.
    result = EventAccumulator(
        name='MyEvent',
        desc='Does something.',
    ).to_dict()

    # desc is included when it is truthy.
    assert result['name'] == 'MyEvent'
    assert result['desc'] == 'Does something.'
