"""Mapper – Accumulator Tests"""

# *** imports

# ** app
from ..semantic import ResolutionAccumulator

# *** tests

# ** test: resolution_accumulator_record_resolved
def test_resolution_accumulator_record_resolved() -> None:
    '''
    Test that a resolved name is recorded and unresolved stays empty.
    '''

    # Record one successful lookup.
    accumulator = ResolutionAccumulator()
    accumulator.record_resolved('Ping', 'module.Ping.execute', 'module')

    # Assert the resolved row and the empty unresolved list.
    assert len(accumulator.resolved) == 1
    assert accumulator.resolved[0].name == 'Ping'
    assert accumulator.resolved[0].scope_path == 'module.Ping.execute'
    assert accumulator.resolved[0].resolved_to == 'module'
    assert accumulator.unresolved == []

# ** test: resolution_accumulator_record_unresolved
def test_resolution_accumulator_record_unresolved() -> None:
    '''
    Test that an unresolved name is recorded and resolved stays empty.
    '''

    # Record one failed lookup.
    accumulator = ResolutionAccumulator()
    accumulator.record_unresolved('missing', 'module')

    # Assert the unresolved row and the empty resolved list.
    assert len(accumulator.unresolved) == 1
    assert accumulator.unresolved[0].name == 'missing'
    assert accumulator.unresolved[0].scope_path == 'module'
    assert accumulator.resolved == []

# ** test: resolution_accumulator_reset
def test_resolution_accumulator_reset() -> None:
    '''
    Test that reset clears recorded lookups from the result.
    '''

    # Record one of each, then clear the collector.
    accumulator = ResolutionAccumulator()
    accumulator.record_resolved('Ping', 'module', 'module')
    accumulator.record_unresolved('missing', 'module')
    accumulator.reset()

    # The result after reset has both lists empty.
    result = accumulator.to_result()
    assert result.resolved == []
    assert result.unresolved == []

# ** test: resolution_accumulator_to_result
def test_resolution_accumulator_to_result() -> None:
    '''
    Test that a mixed recording produces one resolved and one unresolved row.
    '''

    # Record one successful lookup and one failed lookup.
    accumulator = ResolutionAccumulator()
    accumulator.record_resolved('Ping', 'module', 'module')
    accumulator.record_unresolved('missing', 'module.Ping.execute')

    # Assert both counts on the result.
    result = accumulator.to_result()
    assert len(result.resolved) == 1
    assert len(result.unresolved) == 1
