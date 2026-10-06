"""Compiler Default CLI Catalog Tests"""

# *** imports

# ** core
from pathlib import Path

# ** infra
from tiferet.assets.core import (
    create_default_cli_argument,
    create_default_cli_command_data,
)
from tiferet.domain.cli import CliCommand

# ** app
from ..cli import COMPILER_DEFAULT_COMMANDS
from ..feature import COMPILER_DEFAULT_FEATURES

# *** constants

# ** constant: component_choices
_COMPONENT_CHOICES = (
    'assets',
    'blueprints',
    'contexts',
    'di',
    'domain',
    'events',
    'interfaces',
    'mappers',
    'repos',
    'utils',
)

# ** constant: command_rows
_COMMAND_ROWS = (
    (
        'scan.module',
        'scan',
        'module',
        'Scan Module',
        'Tokenize a source file. This command does not take a component type.',
    ),
    (
        'parse.module',
        'parse',
        'module',
        'Parse Module',
        'Parse a source file. This command does not take a component type.',
    ),
    (
        'semantic.module',
        'semantic',
        'module',
        'Semantic Module',
        'Analyze a source file. The component type arrives as request data.',
    ),
    (
        'compile.module',
        'compile',
        'module',
        'Compile Module',
        'Compile a source file. The component type arrives as request data.',
    ),
    (
        'compile.ast',
        'compile',
        'ast',
        'Compile AST',
        'Compile a saved JSON AST. The component type arrives as request data.',
    ),
)

# *** functions

# ** function: argument
def argument(flags, **kwargs):
    '''
    Build one expected CLI argument.

    :param flags: The argument names or flags.
    :type flags: list
    :param kwargs: The keys the load had.
    :type kwargs: dict
    :return: The argument dict.
    :rtype: dict
    '''

    # Each call returns a new dict. Do not reuse one across commands.
    return create_default_cli_argument(
        flags,
        **kwargs,
    )

# ** function: component_argument
def component_argument():
    '''
    Build the shared component argument.

    :return: The component argument dict.
    :rtype: dict
    '''

    # Required, with the ten choices in frozen order.
    return argument(
        [
            '-c',
            '--component',
        ],
        description='Component type. Phases are component-agnostic; the type arrives as request data.',
        required=True,
        choices=list(_COMPONENT_CHOICES),
    )

# ** function: source_file_argument
def source_file_argument(description='Path of the source file.'):
    '''
    Build a source-file argument.

    :param description: The source-file description.
    :type description: str
    :return: The source-file argument dict.
    :rtype: dict
    '''

    # compile.ast does not use this description.
    return argument(
        [
            'source_file',
        ],
        description=description,
    )

# ** function: output_argument
def output_argument():
    '''
    Build the shared output argument.

    :return: The output argument dict.
    :rtype: dict
    '''

    # The output path is shared in text, not in object identity.
    return argument(
        [
            '-o',
            '--output',
        ],
        description='Path to YAML/JSON file.',
    )

# ** function: output_format_argument
def output_format_argument(description, default=None, choices=None):
    '''
    Build one output-format argument.

    :param description: The format description.
    :type description: str
    :param default: The optional default.
    :type default: str
    :param choices: The optional choices.
    :type choices: list
    :return: The output-format argument dict.
    :rtype: dict
    '''

    # Pass only the keys this declaration had.
    kwargs = {'description': description}
    if default is not None:
        kwargs['default'] = default
    if choices is not None:
        kwargs['choices'] = choices
    return argument(
        [
            '--output-format',
        ],
        **kwargs,
    )

# ** function: expected_arguments
def expected_arguments():
    '''
    Build the five command argument lists.

    :return: Command id to expected arguments.
    :rtype: dict
    '''

    # The three output-format declarations stay three.
    scan_format = output_format_argument(
        'Serialization format for the scan result.',
    )
    parse_format = output_format_argument(
        'Serialization format. Defaults to auto.',
        default='auto',
    )
    compile_format = output_format_argument(
        'Serialization format. Defaults to auto. Choices are yaml, json, and auto.',
        default='auto',
        choices=[
            'yaml',
            'json',
            'auto',
        ],
    )
    optimization = argument(
        [
            '-O',
        ],
        description='Optimization level. O0 leaves codegen unchanged. O1 shares repeated structures.',
        default='O0',
    )
    include_tokens = argument(
        [
            '--include-tokens',
        ],
        description='Include the token list in the result.',
        type='bool',
    )

    # Scan and parse do not declare the component argument.
    return {
        'scan.module': [
            source_file_argument(),
            output_argument(),
            scan_format,
            argument(
                [
                    '--summary-only',
                ],
                description='Emit a summary only.',
                type='bool',
            ),
        ],
        'parse.module': [
            source_file_argument(),
            output_argument(),
            parse_format,
            include_tokens,
        ],
        'semantic.module': [
            source_file_argument(),
            output_argument(),
            output_format_argument(
                'Serialization format. Defaults to auto.',
                default='auto',
            ),
            argument(
                [
                    '--include-tokens',
                ],
                description='Include the token list in the result.',
                type='bool',
            ),
            argument(
                [
                    '--include-ast',
                ],
                description='Include the dumped AST in the result.',
                type='bool',
            ),
            component_argument(),
        ],
        'compile.module': [
            source_file_argument(),
            output_argument(),
            compile_format,
            optimization,
            component_argument(),
        ],
        'compile.ast': [
            source_file_argument(description='Path of the JSON AST file.'),
            output_argument(),
            output_format_argument(
                'Serialization format. Defaults to auto. Choices are yaml, json, and auto.',
                default='auto',
                choices=[
                    'yaml',
                    'json',
                    'auto',
                ],
            ),
            argument(
                [
                    '-O',
                ],
                description='Optimization level. O0 leaves codegen unchanged. O1 shares repeated structures.',
                default='O0',
            ),
            component_argument(),
        ],
    }

# *** tests

# ** test: compiler_default_commands_match_declared_rows
def test_compiler_default_commands_match_declared_rows() -> None:
    '''
    Test that command keys match feature keys and values omit id.
    '''

    # The five command ids are the five feature ids, in the same order.
    assert list(COMPILER_DEFAULT_COMMANDS) == list(COMPILER_DEFAULT_FEATURES)
    assert list(COMPILER_DEFAULT_COMMANDS) == [key for key, *_rest in _COMMAND_ROWS]
    expected = expected_arguments()

    # The factory emits arguments, not args, and derives id from the split.
    for key, group_key, command_key, name, description in _COMMAND_ROWS:
        value = COMPILER_DEFAULT_COMMANDS[key]
        assert 'id' not in value
        assert 'args' not in value
        assert value == create_default_cli_command_data(
            key=command_key,
            group_key=group_key,
            name=name,
            description=description,
            arguments=expected[key],
        )
        command = CliCommand.model_validate(value)
        assert command.id == key

# ** test: output_format_declarations_differ
def test_output_format_declarations_differ() -> None:
    '''
    Test that the three output-format declarations are not one object.
    '''

    # Find the one output-format argument on each command.
    found = {}
    for key, command in COMPILER_DEFAULT_COMMANDS.items():
        matches = [
            arg for arg in command['arguments']
            if arg.get('name_or_flags') == ['--output-format']
        ]
        assert len(matches) == 1
        found[key] = matches[0]

    # Scan, parse, and compile stay three declarations.
    assert 'default' not in found['scan.module']
    assert 'choices' not in found['scan.module']
    assert found['scan.module']['description'] == 'Serialization format for the scan result.'
    assert found['parse.module'] == found['semantic.module']
    assert found['parse.module'] is not found['semantic.module']
    assert found['compile.module'] == found['compile.ast']
    assert found['compile.module'] is not found['compile.ast']
    assert found['scan.module'] != found['parse.module']
    assert found['parse.module'] != found['compile.module']

    # compile.ast does not reuse the shared source-file sentence.
    ast_source = [
        arg for arg in COMPILER_DEFAULT_COMMANDS['compile.ast']['arguments']
        if arg.get('name_or_flags') == ['source_file']
    ]
    assert len(ast_source) == 1
    assert ast_source[0]['description'] == 'Path of the JSON AST file.'

# ** test: component_argument_is_required_on_semantic_bearing_commands
def test_component_argument_is_required_on_semantic_bearing_commands() -> None:
    '''
    Test that only semantic-bearing commands declare the component argument.
    '''

    # Scan and parse do not gain the flag.
    for key in ('scan.module', 'parse.module'):
        matches = [
            arg for arg in COMPILER_DEFAULT_COMMANDS[key]['arguments']
            if '--component' in (arg.get('name_or_flags') or [])
        ]
        assert matches == []

    # The other three require the ten choices.
    for key in ('semantic.module', 'compile.module', 'compile.ast'):
        matches = [
            arg for arg in COMPILER_DEFAULT_COMMANDS[key]['arguments']
            if '-c' in (arg.get('name_or_flags') or [])
            and '--component' in (arg.get('name_or_flags') or [])
        ]
        assert len(matches) == 1
        assert matches[0]['required'] is True
        assert matches[0]['choices'] == list(_COMPONENT_CHOICES)

# ** test: command_arguments_are_not_shared
def test_command_arguments_are_not_shared() -> None:
    '''
    Test that expanding an anchor does not reuse an argument object.
    '''

    # A later mutation of one command must not change another.
    seen = []
    for command in COMPILER_DEFAULT_COMMANDS.values():
        for arg in command['arguments']:
            assert all(arg is not prior for prior in seen)
            seen.append(arg)

# ** test: console_entry_does_not_open_config
def test_console_entry_does_not_open_config() -> None:
    '''
    Test that the console entry does not open config.yml.
    '''

    # The session repair removes the packaged config open.
    source = Path(__file__).resolve().parents[2] / 'cli.py'
    assert "asset_path('config.yml')" not in source.read_text(encoding='utf-8')
