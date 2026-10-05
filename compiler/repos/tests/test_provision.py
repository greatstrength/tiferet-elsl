"""Compiler Provision Repository Tests"""

# *** imports

# ** core
import inspect
from pathlib import Path

# ** infra
import pytest
from pydantic import ValidationError

# ** app
from ..provision import (
    PROVISION_CONFIG_SECTION,
    ProvisionConfigRepository,
)

# *** functions

# ** function: _row
def _row(body_id: str = None) -> str:
    '''
    Return one valid provision row body.

    :param body_id: An optional body id that must lose to the mapping key.
    :type body_id: str
    :return: YAML for one registration body.
    :rtype: str
    '''

    # The key is reinjected. A body id is included only when the test needs one.
    lines = [
        '    kind: specification',
        '    applies_to: artifact_header',
        "    module_path: compiler.utils.core",
        '    class_name: ImportGroupSpecification',
        '    parameters: {}',
    ]
    if body_id is not None:
        lines.insert(0, f'    id: {body_id}')
    return '\n'.join(lines)

# *** tests

# ** test: repository_lists_registrations_and_ignores_other_keys
def test_repository_lists_registrations_and_ignores_other_keys(
        tmp_path: Path,
    ) -> None:
    '''
    Test that the mapping key wins as id and other top-level keys are ignored.

    :param tmp_path: Temporary directory for the configuration file.
    :type tmp_path: Path
    '''

    # The body id loses. The errors key is not a provision.
    path = tmp_path / 'overlay.yml'
    path.write_text(
        'errors:\n'
        '  APP_ERROR: {name: App}\n'
        'provisions:\n'
        '  common.import_group:\n'
        + _row('loses') + '\n',
        encoding='utf-8',
    )
    listed = ProvisionConfigRepository(str(path)).list()

    # The returned id is the key, and the other section is absent.
    assert PROVISION_CONFIG_SECTION == 'provisions'
    assert len(listed) == 1
    assert listed[0].id == 'common.import_group'
    assert listed[0].id != 'loses'

# ** test: missing_and_null_sections_return_no_rows
@pytest.mark.parametrize('text', [
    'errors:\n  APP_ERROR: {}\n',
    'provisions:\n',
    'provisions: null\n',
])
def test_missing_and_null_sections_return_no_rows(
        tmp_path: Path,
        text: str,
    ) -> None:
    '''
    Test that a missing or null provisions section returns an empty list.

    :param tmp_path: Temporary directory for the configuration file.
    :type tmp_path: Path
    :param text: The configuration document.
    :type text: str
    '''

    # Absence of rows is not an error.
    path = tmp_path / 'overlay.yml'
    path.write_text(text, encoding='utf-8')
    assert ProvisionConfigRepository(str(path)).list() == []

# ** test: non_mapping_section_raises_type_error
def test_non_mapping_section_raises_type_error(tmp_path: Path) -> None:
    '''
    Test that a list section raises TypeError.

    :param tmp_path: Temporary directory for the configuration file.
    :type tmp_path: Path
    '''

    # A list is not a provisions mapping.
    path = tmp_path / 'overlay.yml'
    path.write_text('provisions:\n  - common.import_group\n', encoding='utf-8')
    with pytest.raises(TypeError):
        ProvisionConfigRepository(str(path)).list()

# ** test: invalid_row_propagates_validation_error
def test_invalid_row_propagates_validation_error(tmp_path: Path) -> None:
    '''
    Test that a row failing registration validation is not skipped.

    :param tmp_path: Temporary directory for the configuration file.
    :type tmp_path: Path
    '''

    # A missing kind fails ProvisionRegistration validation.
    path = tmp_path / 'overlay.yml'
    path.write_text(
        'provisions:\n'
        '  common.import_group:\n'
        '    applies_to: artifact_header\n',
        encoding='utf-8',
    )
    with pytest.raises(ValidationError):
        ProvisionConfigRepository(str(path)).list()

# ** test: repository_has_list_only_and_does_not_import
def test_repository_has_list_only_and_does_not_import() -> None:
    '''
    Test that the repository is not a service and does not import a module.
    '''

    # list is the only operation. The source does not name importlib or domain.
    assert hasattr(ProvisionConfigRepository, 'list')
    for name in ('save', 'delete', 'get', 'exists'):
        assert not hasattr(ProvisionConfigRepository, name)
    assert ProvisionConfigRepository.__bases__ == (
        ProvisionConfigRepository.__bases__[0],
    )
    assert 'Service' not in ProvisionConfigRepository.__bases__[0].__name__
    source = inspect.getsource(ProvisionConfigRepository)
    module_source = Path(inspect.getfile(ProvisionConfigRepository)).read_text(
        encoding='utf-8',
    )
    assert 'importlib' not in module_source
    assert 'compiler.domain' not in module_source
    assert 'def list' in source
