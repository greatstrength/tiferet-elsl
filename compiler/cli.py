"""Tiferet Compiler Console Entry"""

# *** imports

# ** core
import tempfile
from pathlib import Path
from typing import Any, Optional
from importlib.resources import files

# ** infra
import yaml

# ** app
from tiferet import CLI

# *** functions

# ** function: asset_path
def asset_path(filename: str) -> str:
    '''
    Resolve a compiler asset basename from the installed package.

    ``filename`` is a basename only, such as ``config.yml``, not a
    repository-relative path.

    :param filename: The asset file name under ``compiler/assets``.
    :type filename: str
    :return: The filesystem path of the packaged asset.
    :rtype: str
    '''

    # Resolve through the installed package so the path does not depend on CWD.
    return str(files('compiler').joinpath('assets', filename))

# ** function: rewrite_asset_paths
def rewrite_asset_paths(data: Any, assets_dir: str, catalog_path: Optional[str] = None) -> Any:
    '''
    Replace catalog ``compiler/assets/`` prefixes with an installed assets directory.

    :param data: A loaded configuration value.
    :type data: Any
    :param assets_dir: The installed ``compiler/assets`` directory.
    :type assets_dir: str
    :param catalog_path: The rewritten session catalog that replaces compiler/assets/config.yml, if any.
    :type catalog_path: Optional[str]
    :return: The value with catalog asset prefixes rewritten.
    :rtype: Any
    '''

    # Point the session catalog at the rewritten copy so its const block is package-absolute too.
    if isinstance(data, str) and catalog_path and data == 'compiler/assets/config.yml':
        return catalog_path

    # Replace a catalog asset path and leave unrelated strings unchanged.
    if isinstance(data, str):
        prefix = 'compiler/assets/'
        if data.startswith(prefix):
            return assets_dir + '/' + data[len(prefix):]
        return data

    # Rewrite mappings recursively, including string keys.
    if isinstance(data, dict):
        return {
            rewrite_asset_paths(key, assets_dir, catalog_path=catalog_path):
                rewrite_asset_paths(value, assets_dir, catalog_path=catalog_path)
            for key, value in data.items()
        }

    # Rewrite sequences recursively.
    if isinstance(data, list):
        return [
            rewrite_asset_paths(item, assets_dir, catalog_path=catalog_path)
            for item in data
        ]

    # Leave numbers, booleans, and nulls unchanged.
    return data

# ** function: resolve_boot_config
def resolve_boot_config() -> str:
    '''
    Write a temporary session config whose asset paths are package-absolute.

    :return: The path of the rewritten YAML file.
    :rtype: str
    '''

    # Load the packaged session catalog, not a CWD-relative config.yml.
    with open(asset_path('config.yml'), encoding='utf-8') as handle:
        data = yaml.safe_load(handle)

    # Open the boot file first so the session catalog can point at it.
    handle = tempfile.NamedTemporaryFile(
        suffix='.yml',
        delete=False,
        mode='w',
        encoding='utf-8',
    )

    # Rewrite every catalog asset prefix onto the installed assets directory and the boot file.
    # Persist the rewritten mapping in declaration order so services register before their dependents.
    try:
        assets_dir = str(files('compiler').joinpath('assets'))
        rewritten = rewrite_asset_paths(data, assets_dir, catalog_path=handle.name)
        yaml.safe_dump(
            rewritten,
            handle,
            sort_keys=False,
        )
    except Exception:
        # Remove the unfinished boot file before re-raising.
        handle.close()
        Path(handle.name).unlink(missing_ok=True)
        raise
    finally:
        handle.close()

    # Return the temp path. The caller removes it after dispatch.
    return handle.name

# ** function: main
def main() -> None:
    '''
    Entry point for the tiferet-compiler console script.

    Resolves compiler assets from the installed package and delegates
    to the Tiferet CLI session ``compiler_cli``.

    :return: None
    :rtype: None
    '''

    # Resolve session config so asset paths are package-absolute.
    app_config = resolve_boot_config()

    # Dispatch argv through the compiler CLI session. Do not change CWD.
    try:
        CLI(
            'compiler_cli',
            app_config=app_config,
        )
    finally:
        # Remove the boot file even when the CLI exits or raises.
        Path(app_config).unlink(missing_ok=True)
