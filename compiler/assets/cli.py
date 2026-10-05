"""Compiler Default CLI Catalog"""

# *** imports

# ** infra
from tiferet.assets.core import (
    create_default_cli_argument,
    create_default_cli_command_data,
)

# *** constants (ids)

# ** constant: scan_module_cli_cmd_id
SCAN_MODULE_CLI_CMD_ID = 'scan.module'

# ** constant: parse_module_cli_cmd_id
PARSE_MODULE_CLI_CMD_ID = 'parse.module'

# ** constant: semantic_module_cli_cmd_id
SEMANTIC_MODULE_CLI_CMD_ID = 'semantic.module'

# ** constant: compile_module_cli_cmd_id
COMPILE_MODULE_CLI_CMD_ID = 'compile.module'

# ** constant: compile_ast_cli_cmd_id
COMPILE_AST_CLI_CMD_ID = 'compile.ast'

# *** constants (models)

# ** constant: scan_module_cli_cmd_data
SCAN_MODULE_CLI_CMD_DATA = create_default_cli_command_data(
    key='module',
    group_key='scan',
    name='Scan Module',
    description='Tokenize a source file. This command does not take a component type.',
    arguments=[
        create_default_cli_argument(
            [
                'source_file',
            ],
            description='Path of the source file.',
        ),
        create_default_cli_argument(
            [
                '-o',
                '--output',
            ],
            description='Path to YAML/JSON file.',
        ),
        create_default_cli_argument(
            [
                '--output-format',
            ],
            description='Serialization format for the scan result.',
        ),
        create_default_cli_argument(
            [
                '--summary-only',
            ],
            description='Emit a summary only.',
            type='bool',
        ),
    ],
)

# ** constant: parse_module_cli_cmd_data
PARSE_MODULE_CLI_CMD_DATA = create_default_cli_command_data(
    key='module',
    group_key='parse',
    name='Parse Module',
    description='Parse a source file. This command does not take a component type.',
    arguments=[
        create_default_cli_argument(
            [
                'source_file',
            ],
            description='Path of the source file.',
        ),
        create_default_cli_argument(
            [
                '-o',
                '--output',
            ],
            description='Path to YAML/JSON file.',
        ),
        create_default_cli_argument(
            [
                '--output-format',
            ],
            description='Serialization format. Defaults to auto.',
            default='auto',
        ),
        create_default_cli_argument(
            [
                '--include-tokens',
            ],
            description='Include the token list in the result.',
            type='bool',
        ),
    ],
)

# ** constant: semantic_module_cli_cmd_data
SEMANTIC_MODULE_CLI_CMD_DATA = create_default_cli_command_data(
    key='module',
    group_key='semantic',
    name='Semantic Module',
    description='Analyze a source file. The component type arrives as request data.',
    arguments=[
        create_default_cli_argument(
            [
                'source_file',
            ],
            description='Path of the source file.',
        ),
        create_default_cli_argument(
            [
                '-o',
                '--output',
            ],
            description='Path to YAML/JSON file.',
        ),
        create_default_cli_argument(
            [
                '--output-format',
            ],
            description='Serialization format. Defaults to auto.',
            default='auto',
        ),
        create_default_cli_argument(
            [
                '--include-tokens',
            ],
            description='Include the token list in the result.',
            type='bool',
        ),
        create_default_cli_argument(
            [
                '--include-ast',
            ],
            description='Include the dumped AST in the result.',
            type='bool',
        ),
        create_default_cli_argument(
            [
                '-c',
                '--component',
            ],
            description='Component type. Phases are component-agnostic; the type arrives as request data.',
            required=True,
            choices=[
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
            ],
        ),
    ],
)

# ** constant: compile_module_cli_cmd_data
COMPILE_MODULE_CLI_CMD_DATA = create_default_cli_command_data(
    key='module',
    group_key='compile',
    name='Compile Module',
    description='Compile a source file. The component type arrives as request data.',
    arguments=[
        create_default_cli_argument(
            [
                'source_file',
            ],
            description='Path of the source file.',
        ),
        create_default_cli_argument(
            [
                '-o',
                '--output',
            ],
            description='Path to YAML/JSON file.',
        ),
        create_default_cli_argument(
            [
                '--output-format',
            ],
            description='Serialization format. Defaults to auto. Choices are yaml, json, and auto.',
            default='auto',
            choices=[
                'yaml',
                'json',
                'auto',
            ],
        ),
        create_default_cli_argument(
            [
                '-O',
            ],
            description='Optimization level. O0 leaves codegen unchanged. O1 shares repeated structures.',
            default='O0',
        ),
        create_default_cli_argument(
            [
                '-c',
                '--component',
            ],
            description='Component type. Phases are component-agnostic; the type arrives as request data.',
            required=True,
            choices=[
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
            ],
        ),
    ],
)

# ** constant: compile_ast_cli_cmd_data
COMPILE_AST_CLI_CMD_DATA = create_default_cli_command_data(
    key='ast',
    group_key='compile',
    name='Compile AST',
    description='Compile a saved JSON AST. The component type arrives as request data.',
    arguments=[
        create_default_cli_argument(
            [
                'source_file',
            ],
            description='Path of the JSON AST file.',
        ),
        create_default_cli_argument(
            [
                '-o',
                '--output',
            ],
            description='Path to YAML/JSON file.',
        ),
        create_default_cli_argument(
            [
                '--output-format',
            ],
            description='Serialization format. Defaults to auto. Choices are yaml, json, and auto.',
            default='auto',
            choices=[
                'yaml',
                'json',
                'auto',
            ],
        ),
        create_default_cli_argument(
            [
                '-O',
            ],
            description='Optimization level. O0 leaves codegen unchanged. O1 shares repeated structures.',
            default='O0',
        ),
        create_default_cli_argument(
            [
                '-c',
                '--component',
            ],
            description='Component type. Phases are component-agnostic; the type arrives as request data.',
            required=True,
            choices=[
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
            ],
        ),
    ],
)

# *** constants (groups)

# ** constant: compiler_default_commands
COMPILER_DEFAULT_COMMANDS = {
    SCAN_MODULE_CLI_CMD_ID: SCAN_MODULE_CLI_CMD_DATA,
    PARSE_MODULE_CLI_CMD_ID: PARSE_MODULE_CLI_CMD_DATA,
    SEMANTIC_MODULE_CLI_CMD_ID: SEMANTIC_MODULE_CLI_CMD_DATA,
    COMPILE_MODULE_CLI_CMD_ID: COMPILE_MODULE_CLI_CMD_DATA,
    COMPILE_AST_CLI_CMD_ID: COMPILE_AST_CLI_CMD_DATA,
}
