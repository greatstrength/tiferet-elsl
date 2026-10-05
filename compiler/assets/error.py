"""Compiler Default Error Catalog"""

# *** imports

# ** infra
from tiferet.assets.core import EN_US, create_default_error_data

# *** constants (ids)

# ** constant: text_extraction_failed_id
TEXT_EXTRACTION_FAILED_ID = 'TEXT_EXTRACTION_FAILED'

# ** constant: lexical_error_detected_id
LEXICAL_ERROR_DETECTED_ID = 'LEXICAL_ERROR_DETECTED'

# ** constant: parser_not_initialized_id
PARSER_NOT_INITIALIZED_ID = 'PARSER_NOT_INITIALIZED'

# ** constant: invalid_ast_structure_id
INVALID_AST_STRUCTURE_ID = 'INVALID_AST_STRUCTURE'

# ** constant: missing_ast_id
MISSING_AST_ID = 'MISSING_AST'

# ** constant: type_mismatch_assignment_id
TYPE_MISMATCH_ASSIGNMENT_ID = 'TYPE_MISMATCH_ASSIGNMENT'

# ** constant: type_mismatch_operation_id
TYPE_MISMATCH_OPERATION_ID = 'TYPE_MISMATCH_OPERATION'

# ** constant: invalid_codegen_schema_id
INVALID_CODEGEN_SCHEMA_ID = 'INVALID_CODEGEN_SCHEMA'

# ** constant: invalid_import_group_id
INVALID_IMPORT_GROUP_ID = 'INVALID_IMPORT_GROUP'

# ** constant: invalid_import_content_id
INVALID_IMPORT_CONTENT_ID = 'INVALID_IMPORT_CONTENT'

# ** constant: artifact_class_name_mismatch_id
ARTIFACT_CLASS_NAME_MISMATCH_ID = 'ARTIFACT_CLASS_NAME_MISMATCH'

# ** constant: invalid_attribute_member_type_id
INVALID_ATTRIBUTE_MEMBER_TYPE_ID = 'INVALID_ATTRIBUTE_MEMBER_TYPE'

# ** constant: attribute_member_name_mismatch_id
ATTRIBUTE_MEMBER_NAME_MISMATCH_ID = 'ATTRIBUTE_MEMBER_NAME_MISMATCH'

# ** constant: invalid_method_member_type_id
INVALID_METHOD_MEMBER_TYPE_ID = 'INVALID_METHOD_MEMBER_TYPE'

# ** constant: method_member_name_mismatch_id
METHOD_MEMBER_NAME_MISMATCH_ID = 'METHOD_MEMBER_NAME_MISMATCH'

# ** constant: method_missing_self_id
METHOD_MISSING_SELF_ID = 'METHOD_MISSING_SELF'

# ** constant: invalid_method_return_type_id
INVALID_METHOD_RETURN_TYPE_ID = 'INVALID_METHOD_RETURN_TYPE'

# ** constant: event_missing_execute_id
EVENT_MISSING_EXECUTE_ID = 'EVENT_MISSING_EXECUTE'

# *** constants (models)

# ** constant: text_extraction_failed_data
TEXT_EXTRACTION_FAILED_DATA = create_default_error_data(
    'Text Extraction Failed',
    [
        (EN_US, 'Failed to extract text blocks from source file: {source_file}'),
    ],
)

# ** constant: lexical_error_detected_data
LEXICAL_ERROR_DETECTED_DATA = create_default_error_data(
    'Lexical Error Detected',
    [
        (EN_US, 'Lexical error detected during tokenization'),
    ],
)

# ** constant: parser_not_initialized_data
PARSER_NOT_INITIALIZED_DATA = create_default_error_data(
    'Parser Not Initialized',
    [
        (EN_US, 'TiferetParser service failed to initialize'),
    ],
)

# ** constant: invalid_ast_structure_data
INVALID_AST_STRUCTURE_DATA = create_default_error_data(
    'Invalid AST Structure',
    [
        (EN_US, 'Syntactic parser did not return a valid Module AST'),
    ],
)

# ** constant: missing_ast_data
MISSING_AST_DATA = create_default_error_data(
    'Missing AST',
    [
        (EN_US, 'No AST received from syntactic analysis'),
    ],
)

# ** constant: type_mismatch_assignment_data
TYPE_MISMATCH_ASSIGNMENT_DATA = create_default_error_data(
    'Type Mismatch in Assignment',
    [
        (EN_US, 'Cannot assign {actual_type} to variable declared as {expected_type}'),
    ],
)

# ** constant: type_mismatch_operation_data
TYPE_MISMATCH_OPERATION_DATA = create_default_error_data(
    'Type Mismatch in Operation',
    [
        (EN_US, 'Unsupported operand types for {operation}: {left_type} and {right_type}'),
    ],
)

# ** constant: invalid_codegen_schema_data
INVALID_CODEGEN_SCHEMA_DATA = create_default_error_data(
    'Invalid Codegen Schema',
    [
        (EN_US, 'Failed to parse codegen schema from {source_file}'),
    ],
)

# ** constant: invalid_import_group_data
INVALID_IMPORT_GROUP_DATA = create_default_error_data(
    'Invalid Import Group',
    [
        (EN_US, "Import group '{group_name}' must be one of: core, infra, app"),
    ],
)

# ** constant: invalid_import_content_data
INVALID_IMPORT_CONTENT_DATA = create_default_error_data(
    'Invalid Import Content',
    [
        (EN_US, "Import section '{section_name}' contains non-import statements"),
    ],
)

# ** constant: artifact_class_name_mismatch_data
ARTIFACT_CLASS_NAME_MISMATCH_DATA = create_default_error_data(
    'Artifact Class Name Mismatch',
    [
        (EN_US, "Section expects class '{expected_class}' but found '{actual_class}'"),
    ],
)

# ** constant: invalid_attribute_member_type_data
INVALID_ATTRIBUTE_MEMBER_TYPE_DATA = create_default_error_data(
    'Invalid Attribute Member Type',
    [
        (EN_US, "Attribute member '{attribute_name}' must be a variable declaration, not a {found_type}"),
    ],
)

# ** constant: attribute_member_name_mismatch_data
ATTRIBUTE_MEMBER_NAME_MISMATCH_DATA = create_default_error_data(
    'Attribute Member Name Mismatch',
    [
        (EN_US, "Attribute member expects '{expected_name}' but declaration is '{actual_name}'"),
    ],
)

# ** constant: invalid_method_member_type_data
INVALID_METHOD_MEMBER_TYPE_DATA = create_default_error_data(
    'Invalid Method Member Type',
    [
        (EN_US, "Method member '{method_name}' must be a function declaration"),
    ],
)

# ** constant: method_member_name_mismatch_data
METHOD_MEMBER_NAME_MISMATCH_DATA = create_default_error_data(
    'Method Member Name Mismatch',
    [
        (EN_US, "Method member expects '{expected_name}' but declaration is '{actual_name}'"),
    ],
)

# ** constant: method_missing_self_data
METHOD_MISSING_SELF_DATA = create_default_error_data(
    'Method Missing Self',
    [
        (EN_US, "Method '{method_name}' must have 'self' as first parameter"),
    ],
)

# ** constant: invalid_method_return_type_data
INVALID_METHOD_RETURN_TYPE_DATA = create_default_error_data(
    'Invalid Method Return Type',
    [
        (EN_US, "Method '{method_name}' has invalid return type '{return_type}'"),
    ],
)

# ** constant: event_missing_execute_data
EVENT_MISSING_EXECUTE_DATA = create_default_error_data(
    'Event Missing Execute',
    [
        (EN_US, "Event '{event_name}' class '{class_name}' must declare an 'execute' method"),
    ],
)

# *** constants (groups)

# ** constant: compiler_default_errors
COMPILER_DEFAULT_ERRORS = {
    TEXT_EXTRACTION_FAILED_ID: TEXT_EXTRACTION_FAILED_DATA,
    LEXICAL_ERROR_DETECTED_ID: LEXICAL_ERROR_DETECTED_DATA,
    PARSER_NOT_INITIALIZED_ID: PARSER_NOT_INITIALIZED_DATA,
    INVALID_AST_STRUCTURE_ID: INVALID_AST_STRUCTURE_DATA,
    MISSING_AST_ID: MISSING_AST_DATA,
    TYPE_MISMATCH_ASSIGNMENT_ID: TYPE_MISMATCH_ASSIGNMENT_DATA,
    TYPE_MISMATCH_OPERATION_ID: TYPE_MISMATCH_OPERATION_DATA,
    INVALID_CODEGEN_SCHEMA_ID: INVALID_CODEGEN_SCHEMA_DATA,
    INVALID_IMPORT_GROUP_ID: INVALID_IMPORT_GROUP_DATA,
    INVALID_IMPORT_CONTENT_ID: INVALID_IMPORT_CONTENT_DATA,
    ARTIFACT_CLASS_NAME_MISMATCH_ID: ARTIFACT_CLASS_NAME_MISMATCH_DATA,
    INVALID_ATTRIBUTE_MEMBER_TYPE_ID: INVALID_ATTRIBUTE_MEMBER_TYPE_DATA,
    ATTRIBUTE_MEMBER_NAME_MISMATCH_ID: ATTRIBUTE_MEMBER_NAME_MISMATCH_DATA,
    INVALID_METHOD_MEMBER_TYPE_ID: INVALID_METHOD_MEMBER_TYPE_DATA,
    METHOD_MEMBER_NAME_MISMATCH_ID: METHOD_MEMBER_NAME_MISMATCH_DATA,
    METHOD_MISSING_SELF_ID: METHOD_MISSING_SELF_DATA,
    INVALID_METHOD_RETURN_TYPE_ID: INVALID_METHOD_RETURN_TYPE_DATA,
    EVENT_MISSING_EXECUTE_ID: EVENT_MISSING_EXECUTE_DATA,
}
