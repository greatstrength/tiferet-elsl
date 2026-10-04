"""Compiler Default Error Catalog Tests"""

# *** imports

# ** core
from pathlib import Path

# ** infra
import pytest
from pydantic import ValidationError
from tiferet.assets.core import EN_US, create_default_error_data
from tiferet.contexts.error import add_default_errors
from tiferet.domain.error import Error

# ** app
from ..error import COMPILER_DEFAULT_ERRORS
from ..grammar import TIFERET_DIALECT_DATA
from ..production import COMPILER_DEFAULT_PRODUCTIONS
from ..token import COMPILER_DEFAULT_TOKENS

# *** constants

# ** constant: assets_dir
_ASSETS_DIR = Path(__file__).resolve().parent.parent

# ** constant: catalog_modules
_CATALOG_MODULES = (
    'error.py',
    'grammar.py',
    'token.py',
    'production.py',
)

# ** constant: forbidden_imports
_FORBIDDEN_IMPORTS = (
    'tiferet_ly',
    'yaml',
    'compiler.domain',
    'compiler.events',
    'compiler.mappers',
    'compiler.utils',
    'compiler.contexts',
    'compiler.blueprints',
    'compiler.interfaces',
    '..domain',
    '..events',
    '..mappers',
    '..utils',
    '..contexts',
    '..blueprints',
    '..interfaces',
)

# ** constant: deleted_yaml_names
_DELETED_YAML_NAMES = (
    'errors.yml',
    'tokens.yml',
    'grammars.yml',
    'productions.yml',
)

# ** constant: error_rows
_ERROR_ROWS = (
    (
        'TEXT_EXTRACTION_FAILED',
        'Text Extraction Failed',
        'Failed to extract text blocks from source file: {source_file}',
    ),
    (
        'LEXICAL_ERROR_DETECTED',
        'Lexical Error Detected',
        'Lexical error detected during tokenization',
    ),
    (
        'PARSER_NOT_INITIALIZED',
        'Parser Not Initialized',
        'TiferetParser service failed to initialize',
    ),
    (
        'INVALID_AST_STRUCTURE',
        'Invalid AST Structure',
        'Syntactic parser did not return a valid Module AST',
    ),
    (
        'MISSING_AST',
        'Missing AST',
        'No AST received from syntactic analysis',
    ),
    (
        'TYPE_MISMATCH_ASSIGNMENT',
        'Type Mismatch in Assignment',
        'Cannot assign {actual_type} to variable declared as {expected_type}',
    ),
    (
        'TYPE_MISMATCH_OPERATION',
        'Type Mismatch in Operation',
        'Unsupported operand types for {operation}: {left_type} and {right_type}',
    ),
    (
        'INVALID_CODEGEN_SCHEMA',
        'Invalid Codegen Schema',
        'Failed to parse codegen schema from {source_file}',
    ),
    (
        'INVALID_IMPORT_GROUP',
        'Invalid Import Group',
        "Import group '{group_name}' must be one of: core, infra, app",
    ),
    (
        'INVALID_IMPORT_CONTENT',
        'Invalid Import Content',
        "Import section '{section_name}' contains non-import statements",
    ),
    (
        'ARTIFACT_CLASS_NAME_MISMATCH',
        'Artifact Class Name Mismatch',
        "Section expects class '{expected_class}' but found '{actual_class}'",
    ),
    (
        'INVALID_ATTRIBUTE_MEMBER_TYPE',
        'Invalid Attribute Member Type',
        "Attribute member '{attribute_name}' must be a variable declaration, not a {found_type}",
    ),
    (
        'ATTRIBUTE_MEMBER_NAME_MISMATCH',
        'Attribute Member Name Mismatch',
        "Attribute member expects '{expected_name}' but declaration is '{actual_name}'",
    ),
    (
        'INVALID_METHOD_MEMBER_TYPE',
        'Invalid Method Member Type',
        "Method member '{method_name}' must be a function declaration",
    ),
    (
        'METHOD_MEMBER_NAME_MISMATCH',
        'Method Member Name Mismatch',
        "Method member expects '{expected_name}' but declaration is '{actual_name}'",
    ),
    (
        'METHOD_MISSING_SELF',
        'Method Missing Self',
        "Method '{method_name}' must have 'self' as first parameter",
    ),
    (
        'INVALID_METHOD_RETURN_TYPE',
        'Invalid Method Return Type',
        "Method '{method_name}' has invalid return type '{return_type}'",
    ),
    (
        'EVENT_MISSING_EXECUTE',
        'Event Missing Execute',
        "Event '{event_name}' class '{class_name}' must declare an 'execute' method",
    ),
)

# *** tests

# ** test: compiler_default_errors_match_declared_rows
def test_compiler_default_errors_match_declared_rows() -> None:
    '''
    Test that the error catalog has the eighteen declared rows.
    '''

    # Insertion order is the declared order, not a sorted order.
    assert list(COMPILER_DEFAULT_ERRORS) == [key for key, _name, _text in _ERROR_ROWS]

    # Each value is the factory shape. The key is not copied into the value.
    for key, name, text in _ERROR_ROWS:
        value = COMPILER_DEFAULT_ERRORS[key]
        assert set(value) == {'name', 'message'}
        assert 'id' not in value
        assert 'error_code' not in value
        assert 'description' not in value
        assert value == create_default_error_data(
            name,
            [
                (EN_US, text),
            ],
        )

        # Reinjecting the key validates as an Error and copies id into error_code.
        error = Error.model_validate({
            **value,
            'id': key,
        })
        assert error.id == key
        assert error.error_code == key
        assert error.name == name
        assert len(error.message) == 1
        assert error.message[0].lang == EN_US
        assert error.message[0].text == text

# ** test: add_default_errors_returns_callable
def test_add_default_errors_returns_callable() -> None:
    '''
    Test that the error catalog is a seed argument, not a built cache.
    '''

    # The decorator is returned. This test does not call build_cache.
    assert callable(add_default_errors(COMPILER_DEFAULT_ERRORS))

# ** test: dialect_rows_are_not_errors
def test_dialect_rows_are_not_errors() -> None:
    '''
    Test that dialect catalogs do not validate as Error rows.
    '''

    # One body from each dialect catalog fails even after id reinjection.
    bodies = (
        COMPILER_DEFAULT_TOKENS['ARTIFACT_START'],
        COMPILER_DEFAULT_PRODUCTIONS['import_block_single'],
        TIFERET_DIALECT_DATA,
    )
    for body in bodies:
        with pytest.raises(ValidationError):
            Error.model_validate({
                **body,
                'id': 'NOT_AN_ERROR',
            })

# ** test: catalog_modules_do_not_name_forbidden_imports
def test_catalog_modules_do_not_name_forbidden_imports() -> None:
    '''
    Test that the four catalogs do not import forbidden modules or name deleted YAML.
    '''

    # Provision is another RFP's catalog. It is not defined here.
    assert not (_ASSETS_DIR / 'provision.py').exists()

    # Import lines stay inside the permitted set. Deleted filenames are absent.
    for name in _CATALOG_MODULES:
        source = (_ASSETS_DIR / name).read_text(encoding='utf-8')
        assert 'COMPILER_DEFAULT_PROVISIONS' not in source
        import_lines = [
            line.strip()
            for line in source.splitlines()
            if line.strip().startswith(('import ', 'from '))
        ]
        for line in import_lines:
            for forbidden in _FORBIDDEN_IMPORTS:
                assert forbidden not in line
        for yaml_name in _DELETED_YAML_NAMES:
            assert yaml_name not in source
