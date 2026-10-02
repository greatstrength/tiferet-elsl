"""Utils – Compiler CLI Entry Tests"""

# *** imports

# ** core
from pathlib import Path

# ** app
from tiferet import CLI
from ...cli import (
    asset_path,
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
    try:
        CLI(
            'compiler_cli',
            app_config=resolve_boot_config(),
            argv=['-h'],
        )
    except SystemExit as exit_error:
        assert exit_error.code in (0, None)
