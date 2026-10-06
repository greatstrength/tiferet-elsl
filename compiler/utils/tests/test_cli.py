"""Utils – Compiler CLI Entry Tests"""

# *** imports

# ** core
import json
from pathlib import Path

# ** infra
import pytest
from tiferet.assets import TiferetError

# ** app
from ...cli import (
    main,
    run_catalog_command,
    translate_command,
)

# *** constants

# ** constant: cli_path
_CLI_PATH = Path(__file__).resolve().parents[2] / 'cli.py'

# *** tests

# ** test: cli_source_drops_boot
def test_cli_source_drops_boot() -> None:
    '''
    Test that the console no longer opens a session config.
    '''

    # The boot names and the handler name stay out of the console source.
    source = _CLI_PATH.read_text(encoding='utf-8')
    assert "asset_path('config.yml')" not in source
    assert 'resolve_boot_config' not in source
    assert 'CLI(' not in source
    assert 'get_feature' not in source

# ** test: translate_command_maps_catalog_ids
def test_translate_command_maps_catalog_ids() -> None:
    '''
    Test that the five catalog ids become asked steps.
    '''

    # compile.ast is the hyphenated ask. scan.module is scan.
    assert translate_command('compile.ast') == 'compile-from-ast'
    assert translate_command('scan.module') == 'scan'

# ** test: unknown_command_does_not_run
def test_unknown_command_does_not_run(monkeypatch) -> None:
    '''
    Test that an asked step is not a catalog id.

    :param monkeypatch: The pytest monkeypatch fixture.
    :type monkeypatch: object
    '''

    # A miss raises before a session is built, so run is never called.
    def fail(*args, **kwargs):
        raise AssertionError('run')

    monkeypatch.setattr('compiler.cli.build_compiler_session', fail)
    with pytest.raises(TiferetError) as exc:
        translate_command('scan')
    payload = json.loads(str(exc.value))
    assert payload['error_code'] == 'UNKNOWN_COMPILER_COMMAND'
    assert payload['command_id'] == 'scan'
    assert payload['message'] == "Unknown compiler command: 'scan'."

# ** test: run_catalog_command_translates_before_run
def test_run_catalog_command_translates_before_run(monkeypatch) -> None:
    '''
    Test that a catalog id is translated before the session runs.

    :param monkeypatch: The pytest monkeypatch fixture.
    :type monkeypatch: object
    '''

    # The session sees the asked step and the forwarded kwargs only.
    seen = {}

    class Session:
        def run(self, step, **kwargs):
            seen['step'] = step
            seen['kwargs'] = kwargs
            return 'ok'

    monkeypatch.setattr('compiler.cli.build_compiler_session', lambda: Session())
    assert run_catalog_command('compile.ast', source_file='a.py') == 'ok'
    assert seen['step'] == 'compile-from-ast'
    assert seen['kwargs'] == {'source_file': 'a.py'}
    assert 'marker' not in seen['kwargs']
    assert 'feature_id' not in seen['kwargs']
    assert 'get_feature' not in _CLI_PATH.read_text(encoding='utf-8')

# ** test: parsed_optimization_flag_is_not_o
def test_parsed_optimization_flag_is_not_o(monkeypatch) -> None:
    '''
    Test that a parsed -O value is the optimization kwarg.

    :param monkeypatch: The pytest monkeypatch fixture.
    :type monkeypatch: object
    '''

    # The console renames O before run. The catalog id does not reach run.
    seen = {}

    class Session:
        def run(self, step, **kwargs):
            seen['step'] = step
            seen['kwargs'] = kwargs

    monkeypatch.setattr('compiler.cli.build_compiler_session', lambda: Session())
    main(argv=['compile', 'ast', 'tree.json', '-c', 'domain', '-O', 'O1'])
    assert seen['step'] == 'compile-from-ast'
    assert seen['kwargs']['optimization'] == 'O1'
    assert 'O' not in seen['kwargs']
    assert 'compile.ast' not in seen['kwargs'].values()
