"""Synthetic catalogue for parser adapter tests."""

# *** imports

# ** infra
from tiferet_ly.mappers.grammar import GrammarAggregate
from tiferet_ly.mappers.production import (
    ComplexProductionRuleAggregate,
    SimpleProductionRuleAggregate,
)
from tiferet_ly.mappers.token import SimpleTokenRuleAggregate

# *** constants

# ** constant: simple_grammar_id
SIMPLE_GRAMMAR_ID = 'tiferet_dialect'

# ** constant: simple_grammars
SIMPLE_GRAMMARS = [
    GrammarAggregate(
        id=SIMPLE_GRAMMAR_ID,
        start='module',
    ),
]

# ** constant: simple_token_names
_SIMPLE_TOKEN_NAMES = (
    'ARTIFACT_START',
    'ARTIFACT_SECTION',
    'ARTIFACT_MEMBER',
    'NEWLINE',
    'CLASS',
    'IDENTIFIER',
    'LPAREN',
    'RPAREN',
    'COLON',
    'INDENT',
    'DEDENT',
)

# ** constant: simple_tokens
SIMPLE_TOKENS = [
    SimpleTokenRuleAggregate(
        name=name,
        grammar_id=SIMPLE_GRAMMAR_ID,
        pattern='.',
    )
    for name in _SIMPLE_TOKEN_NAMES
]

# ** constant: simple_productions
SIMPLE_PRODUCTIONS = [
    ComplexProductionRuleAggregate(
        name='module',
        grammar_id=SIMPLE_GRAMMAR_ID,
        spec='module : group_list',
        action="p[0] = $decl.new_module_decl(name='__main__', code=p[1])",
    ),
    ComplexProductionRuleAggregate(
        name='group_list_empty',
        grammar_id=SIMPLE_GRAMMAR_ID,
        spec='group_list :',
        action='p[0] = []',
    ),
    ComplexProductionRuleAggregate(
        name='group_list',
        grammar_id=SIMPLE_GRAMMAR_ID,
        spec='group_list : group_list group',
        action='p[1].append(p[2])\np[0] = p[1]',
    ),
    ComplexProductionRuleAggregate(
        name='group',
        grammar_id=SIMPLE_GRAMMAR_ID,
        spec='group : group_header NEWLINE section_list',
        action='p[0] = $artifact_stmt.new_artifact_stmt(p[1], p[3])',
    ),
    ComplexProductionRuleAggregate(
        name='group_header_start',
        grammar_id=SIMPLE_GRAMMAR_ID,
        spec='group_header : ARTIFACT_START',
        action=(
            'name, qualifier, type = $parse_artifact_header(p[1])\n'
            'ln, col = $pos(p, 1)\n'
            'p[0] = $artifact_decl.new_artifact_decl('
            'name, type, qualifier=qualifier, lineno=ln, col=col)'
        ),
    ),
    ComplexProductionRuleAggregate(
        name='section_list_empty',
        grammar_id=SIMPLE_GRAMMAR_ID,
        spec='section_list :',
        action='p[0] = []',
    ),
    ComplexProductionRuleAggregate(
        name='section_list',
        grammar_id=SIMPLE_GRAMMAR_ID,
        spec='section_list : section_list section',
        action='p[1].append(p[2])\np[0] = p[1]',
    ),
    ComplexProductionRuleAggregate(
        name='section',
        grammar_id=SIMPLE_GRAMMAR_ID,
        spec='section : section_header NEWLINE section_body',
        action='p[0] = $artifact_stmt.new_artifact_stmt(p[1], p[3])',
    ),
    ComplexProductionRuleAggregate(
        name='section_header_section',
        grammar_id=SIMPLE_GRAMMAR_ID,
        spec='section_header : ARTIFACT_SECTION',
        action=(
            'name, qualifier, type = $parse_artifact_header(p[1])\n'
            'ln, col = $pos(p, 1)\n'
            'p[0] = $artifact_decl.new_artifact_decl('
            'name, type, qualifier=qualifier, lineno=ln, col=col)'
        ),
    ),
    ComplexProductionRuleAggregate(
        name='section_body_class',
        grammar_id=SIMPLE_GRAMMAR_ID,
        spec='section_body : class_def',
        action='p[0] = [$stmt.new_decl_stmt(p[1])]',
    ),
    ComplexProductionRuleAggregate(
        name='class_def',
        grammar_id=SIMPLE_GRAMMAR_ID,
        spec=(
            'class_def : CLASS IDENTIFIER LPAREN super_cls_list RPAREN '
            'COLON NEWLINE INDENT class_body DEDENT'
        ),
        action=(
            'ln, col = $pos(p, 1)\n'
            'p[0] = $decl.new_class_decl('
            'name=p[2], subclasses=p[4], '
            "doc_string=p[9].get('docstring', None), "
            'members=[$stmt.new_decl_stmt(m) for m in (p[9].get(\'members\') or [])], '
            'lineno=ln, col=col)'
        ),
    ),
    SimpleProductionRuleAggregate(
        name='super_cls_list_single',
        grammar_id=SIMPLE_GRAMMAR_ID,
        spec='super_cls_list : super_cls',
    ),
    ComplexProductionRuleAggregate(
        name='super_cls',
        grammar_id=SIMPLE_GRAMMAR_ID,
        spec='super_cls : IDENTIFIER',
        action='p[0] = $type.new_class_type(name=p[1])',
    ),
    ComplexProductionRuleAggregate(
        name='class_body_nodoc',
        grammar_id=SIMPLE_GRAMMAR_ID,
        spec='class_body : member_list',
        action="p[0] = {'docstring': None, 'members': p[1]}",
    ),
    ComplexProductionRuleAggregate(
        name='member_list_single',
        grammar_id=SIMPLE_GRAMMAR_ID,
        spec='member_list : member',
        action='p[0] = [p[1]]',
    ),
    ComplexProductionRuleAggregate(
        name='member_list',
        grammar_id=SIMPLE_GRAMMAR_ID,
        spec='member_list : member_list member',
        action='p[1].append(p[2])\np[0] = p[1]',
    ),
    ComplexProductionRuleAggregate(
        name='member_decl',
        grammar_id=SIMPLE_GRAMMAR_ID,
        spec='member : ARTIFACT_MEMBER NEWLINE member_stmt',
        action=(
            'kind = $parse_member_kind(p[1])\n'
            'ln, col = $pos(p, 1)\n'
            'p[0] = $artifact_decl.new_member_decl(kind, p[3], lineno=ln, col=col)'
        ),
    ),
    ComplexProductionRuleAggregate(
        name='member_attr_stmt',
        grammar_id=SIMPLE_GRAMMAR_ID,
        spec='member_stmt : attr_decl',
        action='p[0] = [$stmt.new_decl_stmt(p[1])]',
    ),
    ComplexProductionRuleAggregate(
        name='attr_decl_type',
        grammar_id=SIMPLE_GRAMMAR_ID,
        spec='attr_decl : IDENTIFIER COLON attr_types NEWLINE',
        action=(
            'ln, col = $pos(p, 1)\n'
            'p[0] = $decl.new_attr_decl(name=p[1], types=p[3], lineno=ln, col=col)'
        ),
    ),
    ComplexProductionRuleAggregate(
        name='attr_types_single',
        grammar_id=SIMPLE_GRAMMAR_ID,
        spec='attr_types : type_atom',
        action='p[0] = $get_attribute_type(p[1])',
    ),
    SimpleProductionRuleAggregate(
        name='type_atom_name',
        grammar_id=SIMPLE_GRAMMAR_ID,
        spec='type_atom : IDENTIFIER',
    ),
]
