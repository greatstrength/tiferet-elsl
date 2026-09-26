"""Domain – Type Check Domain Objects Tests"""

# *** imports

# ** infra
import pytest
from pydantic import ValidationError

# ** app
from ..typecheck import TypeCheckError

# *** tests

# ** test: type_check_error_required_fields
def test_type_check_error_required_fields() -> None:
    '''
    Test that a finding stores its required fields and leaves optionals unset.
    '''

    # Construct a finding with only the required fields.
    finding = TypeCheckError(
        error_code='X',
        message='m',
        scope_path='module',
    )

    # Assert the required fields and the default optionals.
    assert finding.error_code == 'X'
    assert finding.message == 'm'
    assert finding.scope_path == 'module'
    assert finding.lineno is None
    assert finding.col is None
    assert finding.context == {}

# ** test: type_check_error_with_optional_fields
def test_type_check_error_with_optional_fields() -> None:
    '''
    Test that line, column, and context persist when provided.
    '''

    # Construct a finding with the optional location and context set.
    finding = TypeCheckError(
        error_code='X',
        message='m',
        scope_path='module',
        lineno=12,
        col=4,
        context={'attr': 'x'},
    )

    # Assert the optional fields persist.
    assert finding.lineno == 12
    assert finding.col == 4
    assert finding.context == {'attr': 'x'}

# ** test: type_check_error_missing_required_raises
def test_type_check_error_missing_required_raises() -> None:
    '''
    Test that omitting any required finding field raises ValidationError.
    '''

    # Define a complete set of required finding fields.
    complete = dict(
        error_code='X',
        message='m',
        scope_path='module',
    )

    # Omitting any one required field must raise ValidationError.
    for field in ('error_code', 'message', 'scope_path'):
        data = dict(complete)
        data.pop(field)
        with pytest.raises(ValidationError):
            TypeCheckError(**data)
