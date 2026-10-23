"""Utils – Compiler CLI Entry Tests"""

# *** imports

# ** core
import sys
import tempfile
from pathlib import Path

# ** infra
import yaml

# ** app
from tiferet import CLI
from ...cli import (
    asset_path,
    main,
    resolve_boot_config,
    rewrite_asset_paths,
)

# *** tests

# ** test: asset_path_independent_of_cwd
def test_asset_path_independent_of_cwd(tmp_path: Path, monkeypatch) -> None:
    '''
    Test that a packaged asset resolves after leaving the repository root.

    :param tmp_path: A temporary directory outside the repository.
    :type tmp_path: Path
    :param monkeypatch: The pytest monkeypatch fixture.
    :type monkeypatch: MonkeyPatch
    '''

    # A CWD-relative compiler/assets path would miss from here.
    monkeypatch.chdir(tmp_path)

    # The basename still names an existing packaged file.
    path = asset_path('config.yml')
    assert path.endswith('assets/config.yml')
    assert Path(path).is_file()

# ** test: rewrite_asset_paths_rewrites_prefix
def test_rewrite_asset_paths_rewrites_prefix() -> None:
    '''
    Test that catalog asset prefixes are rewritten and unrelated strings are not.
    '''

    # Only strings that start with the catalog prefix change.
    rewritten = rewrite_asset_paths(
        {
            'const': {'token_config': 'compiler/assets/tokens.yml'},
            'name': 'compiler',
        },
        '/pkg/assets',
    )
    assert rewritten == {
        'const': {'token_config': '/pkg/assets/tokens.yml'},
        'name': 'compiler',
    }

# ** test: main_help_off_cwd
def test_main_help_off_cwd(tmp_path: Path, monkeypatch) -> None:
    '''
    Test that CLI help from another working directory does not miss packaged assets.

    :param tmp_path: A temporary directory outside the repository.
    :type tmp_path: Path
    :param monkeypatch: The pytest monkeypatch fixture.
    :type monkeypatch: MonkeyPatch
    '''

    # Leave the repository root so CWD-relative asset paths would fail.
    monkeypatch.chdir(tmp_path)

    # Help may exit 0. A missing packaged asset must not raise FileNotFoundError.
    boot_path = resolve_boot_config()
    try:
        CLI(
            'compiler_cli',
            app_config=boot_path,
            argv=['-h'],
        )
    except SystemExit as exit_error:
        assert exit_error.code in (0, None)
    finally:
        # Remove the boot file so the test leaves no temp file behind.
        Path(boot_path).unlink(missing_ok=True)

# ** test: rewrite_asset_paths_retargets_catalog
def test_rewrite_asset_paths_retargets_catalog() -> None:
    '''
    Test that the session catalog path is retargeted onto the rewritten boot file.
    '''

    # The catalog path is replaced; other asset paths keep the prefix rewrite.
    rewritten = rewrite_asset_paths(
        {
            'di_config': 'compiler/assets/config.yml',
            'feature_config': 'compiler/assets/feature.yml',
        },
        '/pkg/assets',
        catalog_path='/tmp/boot.yml',
    )
    assert rewritten == {
        'di_config': '/tmp/boot.yml',
        'feature_config': '/pkg/assets/feature.yml',
    }

# ** test: resolve_boot_config_const_package_absolute
def test_resolve_boot_config_const_package_absolute(tmp_path: Path, monkeypatch) -> None:
    '''
    Test that the boot file const block is package-absolute and sessions read the boot file.

    :param tmp_path: A temporary directory for the boot file.
    :type tmp_path: Path
    :param monkeypatch: The pytest monkeypatch fixture.
    :type monkeypatch: MonkeyPatch
    '''

    # Write the boot file under the test directory.
    monkeypatch.setattr(tempfile, 'tempdir', str(tmp_path))
    boot_path = resolve_boot_config()

    # Load the boot file as written.
    with open(boot_path, encoding='utf-8') as handle:
        data = yaml.safe_load(handle)

    # The top-level const block names existing packaged files.
    assert Path(data['const']['token_config']).is_file()
    assert Path(data['const']['grammar_config']).is_file()
    assert Path(data['const']['production_config']).is_file()

    # Every session reads the boot file itself as its DI catalog.
    for session in data['sessions'].values():
        assert session['const']['di_config'] == boot_path

# ** test: main_scan_off_cwd
def test_main_scan_off_cwd(tmp_path: Path, monkeypatch) -> None:
    '''
    Test that a real scan runs from another working directory and leaves no boot file.

    :param tmp_path: A temporary directory outside the repository.
    :type tmp_path: Path
    :param monkeypatch: The pytest monkeypatch fixture.
    :type monkeypatch: MonkeyPatch
    '''

    # Leave the repository root and send boot files to an empty directory.
    monkeypatch.chdir(tmp_path)
    boot_dir = tmp_path / 'boot'
    boot_dir.mkdir()
    monkeypatch.setattr(tempfile, 'tempdir', str(boot_dir))

    # Scan the packaged compiler/cli.py module into a YAML file.
    source_file = str(Path(asset_path('config.yml')).parent.parent / 'cli.py')
    output_file = tmp_path / 'scan.yml'
    argv = [
        'tiferet-compiler',
        'scan',
        'module',
        source_file,
        '-o',
        str(output_file),
    ]
    monkeypatch.setattr(sys, 'argv', argv)
    main()

    # The scan result is written and the boot file is removed.
    with open(output_file, encoding='utf-8') as handle:
        result = yaml.safe_load(handle)
    assert result['event_type'] == 'TokensScanned'
    assert list(boot_dir.iterdir()) == []

# ** test: resolve_boot_config_removes_file_on_dump_failure
def test_resolve_boot_config_removes_file_on_dump_failure(tmp_path: Path, monkeypatch) -> None:
    '''
    Test that a failed boot file dump removes the unfinished file and re-raises.

    :param tmp_path: A temporary directory for the boot file.
    :type tmp_path: Path
    :param monkeypatch: The pytest monkeypatch fixture.
    :type monkeypatch: MonkeyPatch
    '''

    # Send boot files to an empty directory.
    boot_dir = tmp_path / 'boot'
    boot_dir.mkdir()
    monkeypatch.setattr(tempfile, 'tempdir', str(boot_dir))

    # Make the dump fail after the boot file is opened.
    def fail_dump(*args, **kwargs):
        raise RuntimeError('dump failed')
    monkeypatch.setattr(yaml, 'safe_dump', fail_dump)

    # The dump error propagates and no boot file remains.
    try:
        resolve_boot_config()
    except RuntimeError as error:
        assert str(error) == 'dump failed'
    else:
        raise AssertionError('resolve_boot_config did not raise')
    assert list(boot_dir.iterdir()) == []
