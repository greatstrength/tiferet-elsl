"""Tiferet Compiler Console Entry"""

# *** imports

# ** core
import argparse
import sys
from typing import Any

# ** infra
from tiferet.assets import TiferetError

# ** app
from .assets.cli import COMPILER_DEFAULT_COMMANDS
from .blueprints import build_compiler_session

# *** constants

# ** constant: unknown_compiler_command
UNKNOWN_COMPILER_COMMAND = 'UNKNOWN_COMPILER_COMMAND'

# ** constant: command_step
COMMAND_STEP = {
    'scan.module': 'scan',
    'parse.module': 'parse',
    'semantic.module': 'semantic',
    'compile.module': 'compile',
    'compile.ast': 'compile-from-ast',
}

# ** constant: run_kwarg_names
_RUN_KWARG_NAMES = (
    'component',
    'source_file',
    'output',
    'output_format',
    'optimization',
    'include_tokens',
    'include_ast',
    'extract',
)

# *** functions

# ** function: _group_list
def _group_list(grouped: dict, group_key: str, default: list = None) -> list:
    '''
    Return the command list for one group, creating it when absent.

    ``dict.setdefault`` does not accept a keyword, so the optional list is
    passed here.

    :param grouped: Group key to command rows.
    :type grouped: dict
    :param group_key: The catalog group key.
    :type group_key: str
    :param default: The list to store when the group is absent.
    :type default: list
    :return: The command list for the group.
    :rtype: list
    '''

    # Create the group list only when this key has not been seen.
    if group_key not in grouped:
        grouped[group_key] = [] if default is None else default
    return grouped[group_key]

# ** function: _argument_kwargs
def _argument_kwargs(argument: dict) -> dict:
    '''
    Translate one catalog argument into argparse keyword arguments.

    :param argument: A catalog argument row.
    :type argument: dict
    :return: Keyword arguments for add_argument.
    :rtype: dict
    '''

    # Help text is the catalog description. A bool flag consumes no value.
    kwargs = {}
    if argument.get('description') is not None:
        kwargs['help'] = argument['description']
    if argument.get('type') == 'bool':
        kwargs['action'] = 'store_true'
        return kwargs

    # Value-bearing fields stay omitted when the catalog did not declare them.
    if argument.get('choices') is not None:
        kwargs['choices'] = argument['choices']
    if argument.get('default') is not None:
        kwargs['default'] = argument['default']
    if argument.get('required') is not None:
        kwargs['required'] = argument['required']
    return kwargs

# ** function: _forwarded_kwargs
def _forwarded_kwargs(parsed: dict) -> dict:
    '''
    Keep parsed values the session already forwards.

    :param parsed: The argparse namespace as a dictionary.
    :type parsed: dict
    :return: Run kwargs. Absent values stay omitted.
    :rtype: dict
    '''

    # Rename the short optimization flag. Do not pass O.
    values = dict(parsed)
    if 'O' in values:
        values['optimization'] = values['O']

    # Pass a key only when the parsed value is not None.
    forwarded = {}
    for name in _RUN_KWARG_NAMES:
        if name in values and values[name] is not None:
            forwarded[name] = values[name]
    return forwarded

# ** function: translate_command
def translate_command(command_id: str) -> str:
    '''
    Translate one catalog command id into an asked step.

    :param command_id: A compiler catalog command id.
    :type command_id: str
    :return: The asked step.
    :rtype: str
    '''

    # Only the five catalog ids are accepted. Asked steps are not keys.
    if command_id not in COMMAND_STEP:
        TiferetError.raise_error(
            UNKNOWN_COMPILER_COMMAND,
            message=f'Unknown compiler command: {command_id!r}.',
            command_id=command_id,
        )

    # Return the asked step. Do not pass the catalog id onward.
    return COMMAND_STEP[command_id]

# ** function: run_catalog_command
def run_catalog_command(command_id: str, **kwargs) -> Any:
    '''
    Translate a catalog id and run the asked step.

    :param command_id: A compiler catalog command id.
    :type command_id: str
    :param kwargs: Values forwarded to the session run.
    :type kwargs: dict
    :return: The session run result.
    :rtype: Any
    '''

    # Translate before the session is built so a miss never reaches run.
    step = translate_command(command_id)

    # Build a session with the default cache and resolver.
    session = build_compiler_session()

    # Run the asked step. Do not pass the catalog id.
    return session.run(step, **kwargs)

# ** function: parse_compiler_argv
def parse_compiler_argv(argv: list | None = None) -> tuple:
    '''
    Parse argv into a catalog command id and run kwargs.

    :param argv: Explicit argv. Defaults to sys.argv[1:].
    :type argv: list | None
    :return: The catalog command id and the forwarded kwargs.
    :rtype: tuple
    '''

    # Default argv is the process arguments, not a config file.
    if argv is None:
        argv = sys.argv[1:]

    # Build one parser from each catalog row's group, key, and arguments.
    parser = argparse.ArgumentParser()
    group_parsers = parser.add_subparsers(dest='group', required=True)
    grouped = {}
    for command in COMPILER_DEFAULT_COMMANDS.values():
        _group_list(grouped, command['group_key'], default=[]).append(command)
    for group_key, commands in grouped.items():
        group_parser = group_parsers.add_parser(group_key)
        command_parsers = group_parser.add_subparsers(dest='command', required=True)
        for command in commands:
            command_parser = command_parsers.add_parser(
                command['key'],
                help=command.get('description'),
            )
            for argument in command.get('arguments') or []:
                command_parser.add_argument(
                    *argument['name_or_flags'],
                    **_argument_kwargs(argument),
                )

    # The catalog id is the join. Run kwargs are the forwarded values.
    parsed = vars(parser.parse_args(args=argv))
    command_id = f"{parsed['group']}.{parsed['command']}"
    return command_id, _forwarded_kwargs(parsed)

# ** function: main
def main(argv: list | None = None) -> None:
    '''
    Parse compiler argv and run the translated step.

    :param argv: Explicit argv. Defaults to sys.argv[1:].
    :type argv: list | None
    :return: None
    :rtype: None
    '''

    # Parse the catalog command. Do not open a config file.
    command_id, kwargs = parse_compiler_argv(argv=argv)

    # Translate and run. Do not pass the catalog id as a step.
    run_catalog_command(command_id, **kwargs)
