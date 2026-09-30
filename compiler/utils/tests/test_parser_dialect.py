"""Assets – Declared Grammar Productions Catalogue Tests"""

# *** imports

# ** core
import re
from pathlib import Path

# ** infra
import yaml
from tiferet_ly.utils.translation import RuleTranslator

# *** constants

# ** constant: assets_dir
_ASSETS_DIR = Path(__file__).resolve().parents[2] / 'assets'

# ** constant: grammar_id
_GRAMMAR_ID = 'tiferet_dialect'

# ** constant: omit_action
_OMIT_ACTION = (
    'super_cls_list_single',
    'type_atom_name',
    'decorator_arg_literal',
    'method_param_list_no_self',
    'opt_else',
    'for_target',
    'opt_comments',
    'exc_target_single',
    'operation_expr',
    'subscript_index',
    'section_body_import',
    'function_name',
    'function_param_list',
    'member_body_single',
)

# ** constant: shorthands
_SHORTHANDS = (
    '$decl',
    '$stmt',
    '$expr',
    '$type',
    '$param_list',
    '$artifact_decl',
    '$artifact_stmt',
    '$snippet_stmt',
    '$parse_artifact_header',
    '$parse_see_guide_path',
    '$apply_annotations',
    '$parse_member_kind',
    '$parse_member_qualifier',
    '$get_attribute_type',
    '$render_lambda_body',
    '$attach_dangling_else',
    '$pos',
    '$find_column',
    '$set_last_op_pos',
    '$get_last_op_pos',
    '$set_last_ident_pos',
    '$get_last_ident_pos',
)

# ** constant: const_group_specs
_CONST_GROUP_SPECS = {
    'const_decl': 'const_decl : IDENTIFIER EQUALS assign_rhs NEWLINE',
    'const_decl_typed': 'const_decl : IDENTIFIER COLON attr_types EQUALS assign_rhs NEWLINE',
    'const_block_single': 'const_block : const_decl',
    'const_block_multi': 'const_block : const_block const_decl',
    'section_body_const': 'section_body : const_block',
}

# ** constant: tuple_yield_specs
_TUPLE_YIELD_SPECS = {
    'stmt_yield': 'stmt : YIELD yield_values NEWLINE',
    'yield_values_single': 'yield_values : operation_expr',
    'yield_values_multi': 'yield_values : yield_values COMMA operation_expr',
}

# ** constant: ordered_productions
_ORDERED_PRODUCTIONS = (
    (
        'import_block_single',
        'import_block : import_stmt',
        'p[0] = [p[1]]',
    ),
    (
        'import_block_multi',
        'import_block : import_block import_stmt',
        'p[1].append(p[2])\np[0] = p[1]',
    ),
    (
        'import_stmt',
        'import_stmt : IMPORT import_expr NEWLINE',
        'ln, col = $pos(p, 1)\np[0] = $stmt.new_import_stmt(p[2], lineno=ln, col=col)',
    ),
    (
        'import_stmt_from',
        'import_stmt : FROM from_expr IMPORT import_expr NEWLINE',
        'ln, col = $pos(p, 1)\np[0] = $stmt.new_import_stmt_from(p[2], p[4], lineno=ln, col=col)',
    ),
    (
        'import_expr',
        'import_expr : IDENTIFIER',
        'p[0] = $expr.new_name_expr(p[1])',
    ),
    (
        'import_expr_paren',
        'import_expr : LPAREN import_expr RPAREN',
        'p[0] = p[2]',
    ),
    (
        'import_expr_as',
        'import_expr : import_expr AS IDENTIFIER',
        'p[0] = $expr.new_import_expr_as(p[1], p[3])',
    ),
    (
        'import_expr_multi',
        'import_expr : import_expr COMMA IDENTIFIER',
        'p[0] = $expr.new_import_expr_multi(p[1], p[3])',
    ),
    (
        'import_expr_trailing_comma',
        'import_expr : import_expr COMMA',
        'p[0] = p[1]',
    ),
    (
        'import_expr_dot',
        'import_expr : import_expr DOT IDENTIFIER',
        "p[1].name += '.' + p[3]\np[0] = p[1]",
    ),
    (
        'from_expr',
        'from_expr : IDENTIFIER',
        'p[0] = $expr.new_name_expr(p[1])',
    ),
    (
        'from_expr_dot_only',
        'from_expr : DOT',
        "p[0] = $expr.new_name_expr('.')",
    ),
    (
        'from_expr_dot',
        'from_expr : DOT from_expr',
        "p[2].name = '.' + p[2].name\np[0] = p[2]",
    ),
    (
        'from_expr_dot_middle',
        'from_expr : from_expr DOT IDENTIFIER',
        "p[1].name += '.' + p[3]\np[0] = p[1]",
    ),
    (
        'class_def',
        'class_def : CLASS IDENTIFIER LPAREN super_cls_list RPAREN COLON NEWLINE INDENT class_body DEDENT',
        "ln, col = $pos(p, 1)\np[0] = $decl.new_class_decl( name=p[2], subclasses=p[4], doc_string=p[9].get('docstring', None), members=[$stmt.new_decl_stmt(m) for m in (p[9].get('members') or [])], lineno=ln, col=col, )",
    ),
    (
        'class_def_no_parens',
        'class_def : CLASS IDENTIFIER COLON NEWLINE INDENT class_body DEDENT',
        "ln, col = $pos(p, 1)\np[0] = $decl.new_class_decl( name=p[2], subclasses=None, doc_string=p[6].get('docstring', None), members=[$stmt.new_decl_stmt(m) for m in (p[6].get('members') or [])], lineno=ln, col=col, )",
    ),
    (
        'class_body_doc',
        'class_body : DOCSTRING NEWLINE member_list',
        "p[0] = {'docstring': p[1], 'members': p[3]}",
    ),
    (
        'class_body_nodoc',
        'class_body : member_list',
        "p[0] = {'docstring': None, 'members': p[1]}",
    ),
    (
        'class_body_doc_pass',
        'class_body : DOCSTRING NEWLINE PASS NEWLINE',
        "p[0] = {'docstring': p[1], 'members': []}",
    ),
    (
        'super_cls_list_empty',
        'super_cls_list :',
        'p[0] = None',
    ),
    (
        'super_cls_list_single',
        'super_cls_list : super_cls',
        None,
    ),
    (
        'super_cls_multi',
        'super_cls : super_cls COMMA super_cls',
        'p[1].set_subtype(p[3])\np[0] = p[1]',
    ),
    (
        'super_cls',
        'super_cls : IDENTIFIER',
        'p[0] = $type.new_class_type(name=p[1])',
    ),
    (
        'super_cls_kwarg',
        'super_cls : IDENTIFIER EQUALS IDENTIFIER',
        'p[0] = $type.new_class_type(name=p[3])',
    ),
    (
        'attr_decl',
        'attr_decl : IDENTIFIER NEWLINE',
        'ln, col = $pos(p, 1)\np[0] = $decl.new_attr_decl(name=p[1], lineno=ln, col=col)',
    ),
    (
        'attr_decl_type',
        'attr_decl : IDENTIFIER COLON attr_types NEWLINE',
        'ln, col = $pos(p, 1)\np[0] = $decl.new_attr_decl(name=p[1], types=p[3], lineno=ln, col=col)',
    ),
    (
        'attr_decl_type_init',
        'attr_decl : IDENTIFIER COLON attr_types EQUALS assign_rhs NEWLINE',
        'ln, col = $pos(p, 1)\np[0] = $decl.new_attr_decl(name=p[1], types=p[3], value=p[5], lineno=ln, col=col)',
    ),
    (
        'attr_decl_init',
        'attr_decl : IDENTIFIER EQUALS assign_rhs NEWLINE',
        'ln, col = $pos(p, 1)\np[0] = $decl.new_attr_decl(name=p[1], value=p[3], lineno=ln, col=col)',
    ),
    (
        'const_decl',
        'const_decl : IDENTIFIER EQUALS assign_rhs NEWLINE',
        'ln, col = $pos(p, 1)\np[0] = $decl.new_attr_decl(name=p[1], value=p[3], lineno=ln, col=col)',
    ),
    (
        'const_decl_typed',
        'const_decl : IDENTIFIER COLON attr_types EQUALS assign_rhs NEWLINE',
        'ln, col = $pos(p, 1)\np[0] = $decl.new_attr_decl(name=p[1], types=p[3], value=p[5], lineno=ln, col=col)',
    ),
    (
        'const_block_single',
        'const_block : const_decl',
        'p[0] = [p[1]]',
    ),
    (
        'const_block_multi',
        'const_block : const_block const_decl',
        'p[1].append(p[2])\np[0] = p[1]',
    ),
    (
        'type_atom_name',
        'type_atom : IDENTIFIER',
        None,
    ),
    (
        'type_atom_dot',
        'type_atom : type_atom DOT IDENTIFIER',
        'p[0] = p[3]',
    ),
    (
        'type_atom_subscript',
        'type_atom : IDENTIFIER LBRACK subscript_index RBRACK',
        'p[0] = p[1]',
    ),
    (
        'type_atom_none',
        'type_atom : NONE',
        "p[0] = 'None'",
    ),
    (
        'type_atom_forward_ref',
        'type_atom : STRING_LITERAL',
        'p[0] = p[1].strip(\'\\\'"\')',
    ),
    (
        'attr_types_single',
        'attr_types : type_atom',
        'p[0] = $get_attribute_type(p[1])',
    ),
    (
        'attr_types_multi',
        'attr_types : attr_types PIPE type_atom',
        'p[1].set_subtype($get_attribute_type(p[3]))\np[0] = p[1]',
    ),
    (
        'decorator_stmt',
        'decorator_stmt : AT decorator_call NEWLINE',
        'p[0] = $stmt.new_expr_stmt(p[2])',
    ),
    (
        'decorator_stmt_bare',
        'decorator_stmt : AT decorator_ident NEWLINE',
        'p[0] = $stmt.new_expr_stmt(p[2])',
    ),
    (
        'decorator_call',
        'decorator_call : decorator_ident LPAREN decorator_args RPAREN',
        'p[0] = $expr.new_call_expr(p[1], p[3])',
    ),
    (
        'decorator_ident',
        'decorator_ident : IDENTIFIER',
        'p[0] = $expr.new_name_expr(p[1])',
    ),
    (
        'decorator_ident_dot',
        'decorator_ident : decorator_ident DOT IDENTIFIER',
        "ln, col = $pos(p, 1)\np[0] = $expr.new_name_expr(name=p[1].name + '.' + p[3], lineno=ln, col=col)",
    ),
    (
        'decorator_params_single',
        'decorator_args : decorator_arg',
        'p[0] = $expr.new_args_list_expr(p[1])',
    ),
    (
        'decorator_args_multi',
        'decorator_args : decorator_args COMMA decorator_arg',
        'p[0] = $expr.new_args_list_expr(p[1], p[3])',
    ),
    (
        'decorator_arg_literal',
        'decorator_arg : name_or_literal_expr',
        None,
    ),
    (
        'decorator_arg_kwarg',
        'decorator_arg : IDENTIFIER EQUALS name_or_literal_expr',
        'p[0] = $expr.new_kwarg_expr(name=p[1], value=p[3])',
    ),
    (
        'method_decl',
        'method_decl : DEF method_name method_type COLON NEWLINE INDENT method_doc_string snippet_list DEDENT',
        'ln, col = $pos(p, 1)\np[0] = $decl.new_func_decl( name=p[2], type=p[3], doc_string=p[7], body=p[8], lineno=ln, col=col, )',
    ),
    (
        'method_name',
        'method_name : IDENTIFIER\n| INIT',
        'p[0] = p[1]',
    ),
    (
        'method_type',
        'method_type : LPAREN method_param_list RPAREN ret_annot',
        'p[0] = $type.new_func_type(params=p[2], return_type=p[4])',
    ),
    (
        'method_doc_string',
        'method_doc_string : DOCSTRING NEWLINE',
        'p[0] = p[1]',
    ),
    (
        'method_doc_string_empty',
        'method_doc_string :',
        'p[0] = None',
    ),
    (
        'method_param_list',
        'method_param_list : SELF COMMA param_list',
        'self_param = $param_list.new(name=p[1], type=$type.new_unknown_type())\np[0] = [self_param] + p[3]',
    ),
    (
        'method_param_list_self_only',
        'method_param_list : SELF',
        'p[0] = [$param_list.new(name=p[1], type=$type.new_unknown_type())]',
    ),
    (
        'method_param_list_no_self',
        'method_param_list : param_list',
        None,
    ),
    (
        'method_param_list_empty',
        'method_param_list :',
        'p[0] = []',
    ),
    (
        'method_param_list_single',
        'param_list : param',
        'p[0] = [p[1]]',
    ),
    (
        'method_param_list_multi',
        'param_list : param_list COMMA param',
        'p[1].append(p[3])\np[0] = p[1]',
    ),
    (
        'param_list_trailing_comma',
        'param_list : param_list COMMA',
        'p[0] = p[1]',
    ),
    (
        'method_param',
        'param : IDENTIFIER',
        'p[0] = $param_list.new(name=p[1])',
    ),
    (
        'method_param_args',
        'param : STAR IDENTIFIER',
        'p[0] = $param_list.new_args_param(name=p[2])',
    ),
    (
        'method_param_kwargs',
        'param : DOUBLESTAR IDENTIFIER',
        'p[0] = $param_list.new_kwargs_param(name=p[2])',
    ),
    (
        'method_param_type',
        'param : param COLON param_types',
        'p[1].set_type(p[3])\np[0] = p[1]',
    ),
    (
        'param_default',
        'param : param EQUALS unary_expr',
        'p[1].set_default(p[3])\np[0] = p[1]',
    ),
    (
        'param_newline',
        'param : NEWLINE param',
        'p[0] = p[2]',
    ),
    (
        'method_param_types_single',
        'param_types : type_atom',
        'p[0] = $get_attribute_type(p[1])',
    ),
    (
        'method_param_types_multi',
        'param_types : param_types PIPE type_atom',
        'subtype = $get_attribute_type(p[3])\np[1].set_subtype(subtype)\np[0] = p[1]',
    ),
    (
        'ret_annot',
        'ret_annot : ARROW ret_types',
        'p[0] = p[2]',
    ),
    (
        'ret_annot_empty',
        'ret_annot :',
        'p[0] = $type.new_null_type()',
    ),
    (
        'ret_types_single',
        'ret_types : type_atom',
        'p[0] = $get_attribute_type(p[1])',
    ),
    (
        'ret_types_multi',
        'ret_types : ret_types PIPE type_atom',
        'ret_type = $get_attribute_type(p[3])\np[1].set_return_type(ret_type)\np[0] = p[1]',
    ),
    (
        'snippet_list',
        'snippet_list : snippet_list snippet',
        'p[1].append(p[2])\np[0] = p[1]',
    ),
    (
        'snippet_list_newline',
        'snippet_list : snippet_list NEWLINE',
        'p[0] = p[1]',
    ),
    (
        'snippet_list_empty',
        'snippet_list :',
        'p[0] = []',
    ),
    (
        'snippet_list_else_attach',
        'snippet_list : snippet_list comment_list else_clause',
        'if p[1]:\n    $attach_dangling_else(p[1][-1].body, p[3])\np[0] = p[1]',
    ),
    (
        'snippet_comment',
        'snippet : comment_list stmt_list',
        'p[0] = $snippet_stmt.new_snippet_stmt(comments=p[1], code=p[2])',
    ),
    (
        'snippet_nocomment',
        'snippet : stmt_list',
        'p[0] = $snippet_stmt.new_snippet_stmt(code=p[1])',
    ),
    (
        'comment_list_single',
        'comment_list : comment_stmt',
        'p[0] = [p[1]]',
    ),
    (
        'comment_list_multi',
        'comment_list : comment_list comment_stmt',
        'p[1].append(p[2])\np[0] = p[1]',
    ),
    (
        'comment_stmt',
        'comment_stmt : LINE_COMMENT NEWLINE',
        'ln, col = $pos(p, 1)\nexpr = $expr.new_comment_expr(p[1], lineno=ln, col=col)\np[0] = $stmt.new_comment_stmt(expr, lineno=ln, col=col)',
    ),
    (
        'stmt_list_single',
        'stmt_list : stmt',
        'p[0] = [p[1]]',
    ),
    (
        'stmt_list',
        'stmt_list : stmt_list stmt',
        'p[1].append(p[2])\np[0] = p[1]',
    ),
    (
        'stmt_list_newline',
        'stmt_list : stmt_list NEWLINE',
        'p[0] = p[1]',
    ),
    (
        'stmt_list_empty',
        'stmt_list :',
        'p[0] = []',
    ),
    (
        'stmt_return',
        'stmt : RETURN return_expr NEWLINE',
        'ln, col = $pos(p, 1)\np[0] = $stmt.new_return_stmt(return_expr=p[2], lineno=ln, col=col)',
    ),
    (
        'stmt_yield',
        'stmt : YIELD yield_values NEWLINE',
        'ln, col = $pos(p, 1)\nyielded = $expr.new_tuple_expr(elements=p[2], lineno=ln, col=col)\np[0] = $stmt.new_expr_stmt(yielded, lineno=ln, col=col)',
    ),
    (
        'yield_values_single',
        'yield_values : operation_expr',
        'p[0] = $expr.new_args_list_expr(p[1])',
    ),
    (
        'yield_values_multi',
        'yield_values : yield_values COMMA operation_expr',
        'p[0] = $expr.new_args_list_expr(p[1], p[3])',
    ),
    (
        'stmt_assign',
        'stmt : assign_expr NEWLINE',
        'ln, col = $pos(p, 1)\np[0] = $stmt.new_expr_stmt(p[1], lineno=ln, col=col)',
    ),
    (
        'stmt_annotated_assign',
        'stmt : IDENTIFIER COLON attr_types EQUALS assign_rhs NEWLINE',
        'ln, col = $pos(p, 1)\ntarget = $expr.new_name_expr(p[1], lineno=ln, col=col)\nassign = $expr.new_assign_expr(target=target, value=p[5], lineno=ln, col=col)\np[0] = $stmt.new_expr_stmt(assign, lineno=ln, col=col)',
    ),
    (
        'stmt_operator',
        'stmt : operation_expr NEWLINE',
        'ln, col = $pos(p, 1)\np[0] = $stmt.new_expr_stmt(p[1], lineno=ln, col=col)',
    ),
    (
        'stmt_call',
        'stmt : call_expr NEWLINE',
        'ln, col = $pos(p, 1)\np[0] = $stmt.new_expr_stmt(p[1], lineno=ln, col=col)',
    ),
    (
        'stmt_import_local',
        'stmt : import_stmt',
        'p[0] = p[1]',
    ),
    (
        'block_body_stmt',
        'block_body : stmt',
        'p[0] = [p[1]]',
    ),
    (
        'block_body_comment',
        'block_body : comment_stmt',
        'p[0] = [p[1]]',
    ),
    (
        'block_body_extend_stmt',
        'block_body : block_body stmt',
        'p[1].append(p[2])\np[0] = p[1]',
    ),
    (
        'block_body_extend_comment',
        'block_body : block_body comment_stmt',
        'p[1].append(p[2])\np[0] = p[1]',
    ),
    (
        'block_body_newline',
        'block_body : block_body NEWLINE',
        'p[0] = p[1]',
    ),
    (
        'block_body_empty',
        'block_body :',
        'p[0] = []',
    ),
    (
        'block_body_else_attach',
        'block_body : block_body comment_list else_clause',
        '$attach_dangling_else(p[1], p[3])\np[0] = p[1]',
    ),
    (
        'stmt_if',
        'stmt : IF operation_expr COLON NEWLINE INDENT block_body DEDENT opt_else',
        'ln, col = $pos(p, 1)\np[0] = $stmt.new_if_stmt(condition=p[2], body=p[6], else_body=p[8], lineno=ln, col=col)',
    ),
    (
        'stmt_if_inline',
        'stmt : IF operation_expr COLON stmt',
        'ln, col = $pos(p, 1)\np[0] = $stmt.new_if_stmt(condition=p[2], body=p[4], lineno=ln, col=col)',
    ),
    (
        'opt_else',
        'opt_else : else_clause',
        None,
    ),
    (
        'opt_else_empty',
        'opt_else :',
        'p[0] = None',
    ),
    (
        'else_clause',
        'else_clause : ELSE COLON NEWLINE INDENT block_body DEDENT',
        'p[0] = p[5]',
    ),
    (
        'else_clause_inline',
        'else_clause : ELSE COLON stmt',
        'p[0] = [p[3]]',
    ),
    (
        'elif_clause',
        'else_clause : ELIF operation_expr COLON NEWLINE INDENT block_body DEDENT opt_else',
        'ln, col = $pos(p, 1)\np[0] = [$stmt.new_if_stmt(condition=p[2], body=p[6], else_body=p[8], lineno=ln, col=col)]',
    ),
    (
        'elif_clause_inline',
        'else_clause : ELIF operation_expr COLON stmt',
        'ln, col = $pos(p, 1)\np[0] = [$stmt.new_if_stmt(condition=p[2], body=p[4], lineno=ln, col=col)]',
    ),
    (
        'stmt_raise',
        'stmt : RAISE operation_expr NEWLINE\n| RAISE call_expr NEWLINE',
        'ln, col = $pos(p, 1)\np[0] = $stmt.new_raise_stmt(expr=p[2], lineno=ln, col=col)',
    ),
    (
        'stmt_raise_from',
        'stmt : RAISE operation_expr FROM operation_expr NEWLINE\n| RAISE call_expr FROM operation_expr NEWLINE',
        'ln, col = $pos(p, 1)\np[0] = $stmt.new_raise_stmt(expr=p[2], lineno=ln, col=col)',
    ),
    (
        'stmt_raise_bare',
        'stmt : RAISE NEWLINE',
        'ln, col = $pos(p, 1)\np[0] = $stmt.new_raise_stmt(lineno=ln, col=col)',
    ),
    (
        'stmt_pass',
        'stmt : PASS NEWLINE',
        'ln, col = $pos(p, 1)\np[0] = $stmt.new_pass_stmt(lineno=ln, col=col)',
    ),
    (
        'stmt_for',
        'stmt : FOR for_target IN operation_expr COLON NEWLINE INDENT block_body DEDENT',
        'ln, col = $pos(p, 1)\np[0] = $stmt.new_for_stmt(target=p[2], iterable=p[4], body=p[8], lineno=ln, col=col)',
    ),
    (
        'stmt_for_inline',
        'stmt : FOR for_target IN operation_expr COLON stmt',
        'ln, col = $pos(p, 1)\np[0] = $stmt.new_for_stmt(target=p[2], iterable=p[4], body=p[6], lineno=ln, col=col)',
    ),
    (
        'for_target',
        'for_target : ident_expr',
        None,
    ),
    (
        'for_target_tuple',
        'for_target : for_target COMMA ident_expr',
        'p[0] = $expr.new_tuple_expr($expr.new_args_list_expr(p[1], p[3]))',
    ),
    (
        'stmt_while',
        'stmt : WHILE operation_expr COLON NEWLINE INDENT block_body DEDENT',
        'ln, col = $pos(p, 1)\np[0] = $stmt.new_while_stmt(condition=p[2], body=p[6], lineno=ln, col=col)',
    ),
    (
        'stmt_while_inline',
        'stmt : WHILE operation_expr COLON stmt',
        'ln, col = $pos(p, 1)\np[0] = $stmt.new_while_stmt(condition=p[2], body=p[4], lineno=ln, col=col)',
    ),
    (
        'opt_comments',
        'opt_comments : comment_list',
        None,
    ),
    (
        'opt_comments_empty',
        'opt_comments :',
        'p[0] = None',
    ),
    (
        'stmt_try',
        'stmt : TRY COLON NEWLINE INDENT block_body DEDENT opt_comments except_clauses opt_finally',
        'ln, col = $pos(p, 1)\np[0] = $stmt.new_try_stmt(body=p[5], except_body=p[8], finally_body=p[9], lineno=ln, col=col)',
    ),
    (
        'opt_finally',
        'opt_finally : FINALLY COLON NEWLINE INDENT block_body DEDENT',
        'p[0] = p[5]',
    ),
    (
        'opt_finally_empty',
        'opt_finally :',
        'p[0] = None',
    ),
    (
        'except_clauses_single',
        'except_clauses : except_clause',
        'p[0] = [p[1]]',
    ),
    (
        'except_clauses_multi',
        'except_clauses : except_clauses except_clause',
        'p[1].append(p[2])\np[0] = p[1]',
    ),
    (
        'except_clause',
        'except_clause : EXCEPT COLON NEWLINE INDENT block_body DEDENT',
        'ln, col = $pos(p, 1)\np[0] = $stmt.new_if_stmt(condition=None, body=p[5], lineno=ln, col=col)',
    ),
    (
        'except_clause_inline',
        'except_clause : EXCEPT COLON stmt',
        'ln, col = $pos(p, 1)\np[0] = $stmt.new_if_stmt(condition=None, body=p[3], lineno=ln, col=col)',
    ),
    (
        'exc_target_single',
        'exc_target : ident_expr',
        None,
    ),
    (
        'exc_target_tuple',
        'exc_target : LPAREN except_types RPAREN',
        'p[0] = $expr.new_tuple_expr(elements=p[2])',
    ),
    (
        'except_types_single',
        'except_types : ident_expr',
        'p[0] = $expr.new_args_list_expr(p[1])',
    ),
    (
        'except_types_multi',
        'except_types : except_types COMMA ident_expr',
        'p[0] = $expr.new_args_list_expr(p[1], p[3])',
    ),
    (
        'except_clause_type',
        'except_clause : EXCEPT exc_target COLON NEWLINE INDENT block_body DEDENT',
        'ln, col = $pos(p, 1)\np[0] = $stmt.new_if_stmt(condition=p[2], body=p[6], lineno=ln, col=col)',
    ),
    (
        'except_clause_type_inline',
        'except_clause : EXCEPT exc_target COLON stmt',
        'ln, col = $pos(p, 1)\np[0] = $stmt.new_if_stmt(condition=p[2], body=p[4], lineno=ln, col=col)',
    ),
    (
        'except_clause_type_as',
        'except_clause : EXCEPT exc_target AS IDENTIFIER COLON NEWLINE INDENT block_body DEDENT',
        'ln, col = $pos(p, 1)\nalias = $expr.new_import_expr_as(p[2], p[4])\np[0] = $stmt.new_if_stmt(condition=alias, body=p[8], lineno=ln, col=col)',
    ),
    (
        'except_clause_type_as_inline',
        'except_clause : EXCEPT exc_target AS IDENTIFIER COLON stmt',
        'ln, col = $pos(p, 1)\nalias = $expr.new_import_expr_as(p[2], p[4])\np[0] = $stmt.new_if_stmt(condition=alias, body=p[6], lineno=ln, col=col)',
    ),
    (
        'stmt_with',
        'stmt : WITH operation_expr AS ident_expr COLON NEWLINE INDENT block_body DEDENT',
        'ln, col = $pos(p, 1)\np[0] = $stmt.new_with_stmt(context_expr=p[2], target=p[4], body=p[8], lineno=ln, col=col)',
    ),
    (
        'stmt_with_inline',
        'stmt : WITH operation_expr AS ident_expr COLON stmt',
        'ln, col = $pos(p, 1)\np[0] = $stmt.new_with_stmt(context_expr=p[2], target=p[4], body=p[6], lineno=ln, col=col)',
    ),
    (
        'stmt_with_no_as',
        'stmt : WITH operation_expr COLON NEWLINE INDENT block_body DEDENT',
        'ln, col = $pos(p, 1)\np[0] = $stmt.new_with_stmt(context_expr=p[2], target=None, body=p[6], lineno=ln, col=col)',
    ),
    (
        'stmt_with_no_as_inline',
        'stmt : WITH operation_expr COLON stmt',
        'ln, col = $pos(p, 1)\np[0] = $stmt.new_with_stmt(context_expr=p[2], target=None, body=p[4], lineno=ln, col=col)',
    ),
    (
        'stmt_with_call',
        'stmt : WITH call_expr AS ident_expr COLON NEWLINE INDENT block_body DEDENT',
        'ln, col = $pos(p, 1)\np[0] = $stmt.new_with_stmt(context_expr=p[2], target=p[4], body=p[8], lineno=ln, col=col)',
    ),
    (
        'stmt_with_call_inline',
        'stmt : WITH call_expr AS ident_expr COLON stmt',
        'ln, col = $pos(p, 1)\np[0] = $stmt.new_with_stmt(context_expr=p[2], target=p[4], body=p[6], lineno=ln, col=col)',
    ),
    (
        'stmt_assert',
        'stmt : ASSERT operation_expr NEWLINE',
        'ln, col = $pos(p, 1)\np[0] = $stmt.new_assert_stmt(expr=p[2], lineno=ln, col=col)',
    ),
    (
        'stmt_assert_msg',
        'stmt : ASSERT operation_expr COMMA operation_expr NEWLINE',
        'ln, col = $pos(p, 1)\np[0] = $stmt.new_assert_stmt(expr=p[2], msg=p[4], lineno=ln, col=col)',
    ),
    (
        'stmt_continue',
        'stmt : CONTINUE NEWLINE',
        'ln, col = $pos(p, 1)\np[0] = $stmt.new_continue_stmt(lineno=ln, col=col)',
    ),
    (
        'stmt_break',
        'stmt : BREAK NEWLINE',
        'ln, col = $pos(p, 1)\np[0] = $stmt.new_break_stmt(lineno=ln, col=col)',
    ),
    (
        'stmt_del',
        'stmt : DEL ident_expr NEWLINE',
        'ln, col = $pos(p, 1)\np[0] = $stmt.new_del_stmt(expr=p[2], lineno=ln, col=col)',
    ),
    (
        'stmt_nested_func',
        'stmt : method_decl',
        'p[0] = $stmt.new_decl_stmt(p[1])',
    ),
    (
        'stmt_async_func',
        'stmt : ASYNC method_decl',
        "p[2].metadata['async'] = True\np[0] = $stmt.new_decl_stmt(p[2])",
    ),
    (
        'assign_expr',
        'assign_expr : ident_expr EQUALS assign_rhs',
        'ln, col = $pos(p, 2)\np[0] = $expr.new_assign_expr(target=p[1], value=p[3], lineno=ln, col=col)',
    ),
    (
        'assign_expr_tuple_unpack',
        'assign_expr : tuple_unpack_target EQUALS assign_rhs',
        'ln, col = $pos(p, 2)\np[0] = $expr.new_assign_expr(target=p[1], value=p[3], lineno=ln, col=col)',
    ),
    (
        'assign_expr_subscript',
        'assign_expr : postfix_subscript EQUALS assign_rhs',
        'ln, col = $pos(p, 2)\np[0] = $expr.new_assign_expr(target=p[1], value=p[3], lineno=ln, col=col)',
    ),
    (
        'tuple_unpack_target_pair',
        'tuple_unpack_target : ident_expr COMMA ident_expr',
        'p[0] = $expr.new_tuple_expr(elements=$expr.new_args_list_expr(p[1], p[3]))',
    ),
    (
        'tuple_unpack_target_multi',
        'tuple_unpack_target : tuple_unpack_target COMMA ident_expr',
        'p[0] = $expr.new_tuple_expr(elements=$expr.new_args_list_expr(p[1], p[3]))',
    ),
    (
        'assign_rhs',
        'assign_rhs : operation_expr\n| call_expr',
        'p[0] = p[1]',
    ),
    (
        'return_expr',
        'return_expr : operation_expr\n| call_expr',
        'p[0] = p[1]',
    ),
    (
        'return_expr_tuple',
        'return_expr : return_expr COMMA operation_expr',
        'p[0] = $expr.new_tuple_expr(elements=$expr.new_args_list_expr(p[1], p[3]))',
    ),
    (
        'return_empty_expr',
        'return_expr :',
        'p[0] = None',
    ),
    (
        'operation_expr',
        'operation_expr : or_expr',
        None,
    ),
    (
        'operation_expr_ternary',
        'operation_expr : or_expr IF or_expr ELSE operation_expr',
        'ln, col = $pos(p, 2)\np[0] = $expr.new_ternary_expr(true_val=p[1], condition=p[3], false_val=p[5], lineno=ln, col=col)',
    ),
    (
        'or_expr',
        'or_expr : or_expr OR and_expr\n| and_expr',
        'if len(p) == 4:\n    ln, col = $pos(p, 2)\n    p[0] = $expr.new_operator_expr(left=p[1], operator=p[2], right=p[3], lineno=ln, col=col)\nelse:\n    p[0] = p[1]',
    ),
    (
        'and_expr',
        'and_expr : and_expr AND not_expr\n| not_expr',
        'if len(p) == 4:\n    ln, col = $pos(p, 2)\n    p[0] = $expr.new_operator_expr(left=p[1], operator=p[2], right=p[3], lineno=ln, col=col)\nelse:\n    p[0] = p[1]',
    ),
    (
        'not_expr',
        'not_expr : NOT not_expr\n| comparison_expr',
        'if len(p) == 3:\n    ln, col = $pos(p, 1)\n    p[0] = $expr.new_not_expr(operand=p[2], lineno=ln, col=col)\nelse:\n    p[0] = p[1]',
    ),
    (
        'comparison_expr',
        'comparison_expr : additive_expr comparison_op additive_expr\n| additive_expr',
        'if len(p) == 4:\n    ln, col = $get_last_op_pos()\n    p[0] = $expr.new_operator_expr(left=p[1], operator=p[2], right=p[3], lineno=ln, col=col)\nelse:\n    p[0] = p[1]',
    ),
    (
        'comparison_op',
        'comparison_op : EQEQ\n| NOTEQ\n| LT\n| GT\n| LTEQ\n| GTEQ\n| PIPE\n| AMPERSAND\n| IS\n| IN',
        'p[0] = p[1]\n$set_last_op_pos($pos(p, 1))',
    ),
    (
        'comparison_op_is_not',
        'comparison_op : IS NOT',
        "p[0] = 'is not'\n$set_last_op_pos($pos(p, 1))",
    ),
    (
        'comparison_op_not_in',
        'comparison_op : NOT IN',
        "p[0] = 'not in'\n$set_last_op_pos($pos(p, 1))",
    ),
    (
        'additive_expr',
        'additive_expr : additive_expr PLUS multiplicative_expr\n| additive_expr MINUS multiplicative_expr\n| multiplicative_expr',
        'if len(p) == 4:\n    ln, col = $pos(p, 2)\n    p[0] = $expr.new_operator_expr(left=p[1], operator=p[2], right=p[3], lineno=ln, col=col)\nelse:\n    p[0] = p[1]',
    ),
    (
        'multiplicative_expr',
        'multiplicative_expr : multiplicative_expr STAR exponential_expr\n| multiplicative_expr SLASH exponential_expr\n| multiplicative_expr DOUBLESLASH exponential_expr\n| multiplicative_expr PERCENT exponential_expr\n| exponential_expr',
        'if len(p) == 4:\n    ln, col = $pos(p, 2)\n    p[0] = $expr.new_operator_expr(left=p[1], operator=p[2], right=p[3], lineno=ln, col=col)\nelse:\n    p[0] = p[1]',
    ),
    (
        'exponential_expr',
        'exponential_expr : unary_expr DOUBLESTAR exponential_expr\n| unary_expr',
        'if len(p) == 4:\n    ln, col = $pos(p, 2)\n    p[0] = $expr.new_operator_expr(left=p[1], operator=p[2], right=p[3], lineno=ln, col=col)\nelse:\n    p[0] = p[1]',
    ),
    (
        'unary_expr',
        'unary_expr : MINUS unary_expr\n| postfix_expr',
        'if len(p) == 3:\n    ln, col = $pos(p, 1)\n    p[0] = $expr.new_unary_minus_expr(operand=p[2], lineno=ln, col=col)\nelse:\n    p[0] = p[1]',
    ),
    (
        'postfix_expr',
        'postfix_expr : name_or_literal_expr\n| postfix_subscript\n| call_expr',
        'p[0] = p[1]',
    ),
    (
        'postfix_subscript',
        'postfix_subscript : name_or_literal_expr LBRACK subscript_index RBRACK',
        'ln, col = $pos(p, 1)\np[0] = $expr.new_subscript_expr(target=p[1], index=p[3], lineno=ln, col=col)',
    ),
    (
        'postfix_subscript_on_call',
        'postfix_subscript : call_expr LBRACK subscript_index RBRACK',
        'ln, col = $pos(p, 1)\np[0] = $expr.new_subscript_expr(target=p[1], index=p[3], lineno=ln, col=col)',
    ),
    (
        'subscript_index',
        'subscript_index : operation_expr',
        None,
    ),
    (
        'subscript_index_multi',
        'subscript_index : subscript_index COMMA operation_expr',
        'p[0] = $expr.new_args_list_expr(p[1], p[3])',
    ),
    (
        'subscript_slice',
        'subscript_index : operation_expr COLON operation_expr',
        'p[0] = $expr.new_slice_expr(start=p[1], stop=p[3])',
    ),
    (
        'subscript_slice_start_only',
        'subscript_index : operation_expr COLON',
        'p[0] = $expr.new_slice_expr(start=p[1])',
    ),
    (
        'subscript_slice_stop_only',
        'subscript_index : COLON operation_expr',
        'p[0] = $expr.new_slice_expr(stop=p[2])',
    ),
    (
        'subscript_slice_empty',
        'subscript_index : COLON',
        'p[0] = $expr.new_slice_expr()',
    ),
    (
        'await_expr',
        'call_expr : AWAIT call_expr\n| AWAIT ident_expr',
        'ln, col = $pos(p, 1)\np[0] = $expr.new_await_expr(operand=p[2], lineno=ln, col=col)',
    ),
    (
        'call_expr',
        'call_expr : ident_expr LPAREN call_args RPAREN',
        'ln, col = $pos(p, 1)\np[0] = $expr.new_call_expr(p[1], p[3], lineno=ln, col=col)',
    ),
    (
        'call_expr_chained',
        'call_expr : postfix_expr DOT IDENTIFIER LPAREN call_args RPAREN',
        'ln, col = $pos(p, 1)\ncallee = $expr.new_attribute_expr(receiver=p[1], attr=p[3], lineno=ln, col=col)\np[0] = $expr.new_call_expr(callee, p[5], lineno=ln, col=col)',
    ),
    (
        'call_expr_chained_init',
        'call_expr : postfix_expr DOT INIT LPAREN call_args RPAREN',
        'ln, col = $pos(p, 1)\ncallee = $expr.new_attribute_expr(receiver=p[1], attr=p[3], lineno=ln, col=col)\np[0] = $expr.new_call_expr(callee, p[5], lineno=ln, col=col)',
    ),
    (
        'call_args_empty',
        'call_args :',
        'p[0] = None',
    ),
    (
        'call_args_single',
        'call_args : call_arg',
        'p[0] = $expr.new_args_list_expr(p[1])',
    ),
    (
        'call_args_multi',
        'call_args : call_args COMMA call_arg',
        'p[0] = $expr.new_args_list_expr(p[1], p[3])',
    ),
    (
        'call_args_trailing_comma',
        'call_args : call_args COMMA',
        'p[0] = p[1]',
    ),
    (
        'call_arg',
        'call_arg : operation_expr\n| call_expr',
        'p[0] = p[1]',
    ),
    (
        'call_arg_genexpr',
        'call_arg : operation_expr FOR for_target IN postfix_expr',
        'ln, col = $pos(p, 2)\nfor_clause = $expr.new_for_comp_expr(target=p[3], iterable=p[5])\np[0] = $expr.new_comprehension_expr(output=p[1], iterators=for_clause, lineno=ln, col=col)',
    ),
    (
        'call_arg_genexpr_if',
        'call_arg : operation_expr FOR for_target IN postfix_expr IF operation_expr',
        'ln, col = $pos(p, 2)\nfor_clause = $expr.new_for_comp_expr(target=p[3], iterable=p[5], condition=p[7])\np[0] = $expr.new_comprehension_expr(output=p[1], iterators=for_clause, lineno=ln, col=col)',
    ),
    (
        'call_arg_kwarg',
        'call_arg : IDENTIFIER EQUALS operation_expr\n| IDENTIFIER EQUALS call_expr',
        'p[0] = $expr.new_kwarg_expr(name=p[1], value=p[3])',
    ),
    (
        'call_arg_star',
        'call_arg : STAR operation_expr',
        'p[0] = $expr.new_star_expr(operand=p[2])',
    ),
    (
        'call_arg_doublestar',
        'call_arg : DOUBLESTAR operation_expr',
        'p[0] = $expr.new_double_star_expr(operand=p[2])',
    ),
    (
        'call_arg_newline',
        'call_arg : NEWLINE call_arg',
        'p[0] = p[2]',
    ),
    (
        'literal_expr',
        'literal_expr : STRING_LITERAL\n| NUMBER_LITERAL\n| TRUE\n| FALSE',
        'ln, col = $pos(p, 1)\np[0] = $expr.new_name_or_literal_expr(p[1], lineno=ln, col=col)',
    ),
    (
        'literal_prefixed_string',
        'literal_expr : IDENTIFIER STRING_LITERAL',
        'ln, col = $pos(p, 1)\np[0] = $expr.new_name_or_literal_expr(p[1] + p[2], lineno=ln, col=col)',
    ),
    (
        'literal_concat_string',
        'literal_expr : literal_expr STRING_LITERAL',
        "ln, col = $pos(p, 1)\nprev_val = getattr(p[1], 'value', '') or ''\np[0] = $expr.new_name_or_literal_expr(prev_val + p[2], lineno=ln, col=col)",
    ),
    (
        'literal_concat_prefixed_string',
        'literal_expr : literal_expr IDENTIFIER STRING_LITERAL',
        "ln, col = $pos(p, 1)\nprev_val = getattr(p[1], 'value', '') or ''\np[0] = $expr.new_name_or_literal_expr(prev_val + p[2] + p[3], lineno=ln, col=col)",
    ),
    (
        'none_expr',
        'literal_expr : NONE',
        'ln, col = $pos(p, 1)\np[0] = $expr.new_none_expr(lineno=ln, col=col)',
    ),
    (
        'ellipsis_expr',
        'literal_expr : ELLIPSIS',
        'ln, col = $pos(p, 1)\np[0] = $expr.new_ellipsis_expr(lineno=ln, col=col)',
    ),
    (
        'name_or_literal_expr',
        'name_or_literal_expr : ident_expr\n| literal_expr\n| list_literal\n| dict_literal\n| set_literal\n| paren_expr',
        'p[0] = p[1]',
    ),
    (
        'set_literal',
        'set_literal : LBRACE set_items RBRACE',
        'ln, col = $pos(p, 1)\np[0] = $expr.new_set_literal_expr(elements=p[2], lineno=ln, col=col)',
    ),
    (
        'set_items_single',
        'set_items : operation_expr',
        'p[0] = $expr.new_args_list_expr(p[1])',
    ),
    (
        'set_items_multi',
        'set_items : set_items COMMA operation_expr',
        'p[0] = $expr.new_args_list_expr(p[1], p[3])',
    ),
    (
        'set_items_trailing_comma',
        'set_items : set_items COMMA',
        'p[0] = p[1]',
    ),
    (
        'list_literal_empty',
        'list_literal : LBRACK RBRACK',
        'ln, col = $pos(p, 1)\np[0] = $expr.new_list_literal_expr(lineno=ln, col=col)',
    ),
    (
        'list_literal',
        'list_literal : LBRACK list_items RBRACK',
        'ln, col = $pos(p, 1)\np[0] = $expr.new_list_literal_expr(elements=p[2], lineno=ln, col=col)',
    ),
    (
        'list_items_single',
        'list_items : operation_expr\n| call_expr',
        'p[0] = $expr.new_args_list_expr(p[1])',
    ),
    (
        'list_items_multi',
        'list_items : list_items COMMA operation_expr\n| list_items COMMA call_expr',
        'p[0] = $expr.new_args_list_expr(p[1], p[3])',
    ),
    (
        'list_items_newline',
        'list_items : list_items NEWLINE\n| NEWLINE list_items',
        'p[0] = p[1] if not isinstance(p[1], str) else p[2]',
    ),
    (
        'list_items_trailing_comma',
        'list_items : list_items COMMA',
        'p[0] = p[1]',
    ),
    (
        'dict_literal_empty',
        'dict_literal : LBRACE RBRACE',
        'ln, col = $pos(p, 1)\np[0] = $expr.new_dict_literal_expr(lineno=ln, col=col)',
    ),
    (
        'dict_literal',
        'dict_literal : LBRACE dict_items RBRACE',
        'ln, col = $pos(p, 1)\np[0] = $expr.new_dict_literal_expr(entries=p[2], lineno=ln, col=col)',
    ),
    (
        'dict_items_single',
        'dict_items : dict_entry',
        'p[0] = $expr.new_args_list_expr(p[1])',
    ),
    (
        'dict_items_multi',
        'dict_items : dict_items COMMA dict_entry',
        'p[0] = $expr.new_args_list_expr(p[1], p[3])',
    ),
    (
        'dict_items_trailing_comma',
        'dict_items : dict_items COMMA',
        'p[0] = p[1]',
    ),
    (
        'dict_items_newline',
        'dict_items : dict_items NEWLINE\n| NEWLINE dict_items',
        'p[0] = p[1] if not isinstance(p[1], str) else p[2]',
    ),
    (
        'dict_entry',
        'dict_entry : operation_expr COLON operation_expr\n| operation_expr COLON call_expr',
        'p[0] = $expr.new_dict_entry_expr(key=p[1], value=p[3])',
    ),
    (
        'dict_entry_unpack',
        'dict_entry : DOUBLESTAR operation_expr',
        'p[0] = $expr.new_double_star_expr(operand=p[2])',
    ),
    (
        'paren_empty',
        'paren_expr : LPAREN RPAREN',
        'ln, col = $pos(p, 1)\np[0] = $expr.new_tuple_expr(lineno=ln, col=col)',
    ),
    (
        'paren_genexpr',
        'paren_expr : LPAREN operation_expr FOR for_target IN postfix_expr RPAREN',
        'ln, col = $pos(p, 1)\nfor_clause = $expr.new_for_comp_expr(target=p[4], iterable=p[6])\np[0] = $expr.new_comprehension_expr(output=p[2], iterators=for_clause, lineno=ln, col=col)',
    ),
    (
        'paren_genexpr_if',
        'paren_expr : LPAREN operation_expr FOR for_target IN postfix_expr IF operation_expr RPAREN',
        'ln, col = $pos(p, 1)\nfor_clause = $expr.new_for_comp_expr(target=p[4], iterable=p[6], condition=p[8])\np[0] = $expr.new_comprehension_expr(output=p[2], iterators=for_clause, lineno=ln, col=col)',
    ),
    (
        'paren_expr',
        'paren_expr : LPAREN operation_expr RPAREN',
        'p[0] = p[2]',
    ),
    (
        'paren_tuple',
        'paren_expr : LPAREN tuple_items RPAREN',
        'ln, col = $pos(p, 1)\np[0] = $expr.new_tuple_expr(elements=p[2], lineno=ln, col=col)',
    ),
    (
        'paren_tuple_single',
        'paren_expr : LPAREN operation_expr COMMA RPAREN',
        'ln, col = $pos(p, 1)\np[0] = $expr.new_tuple_expr(elements=$expr.new_args_list_expr(p[2]), lineno=ln, col=col)',
    ),
    (
        'tuple_items',
        'tuple_items : operation_expr COMMA operation_expr',
        'p[0] = $expr.new_args_list_expr(p[1], p[3])',
    ),
    (
        'tuple_items_multi',
        'tuple_items : tuple_items COMMA operation_expr',
        'p[0] = $expr.new_args_list_expr(p[1], p[3])',
    ),
    (
        'tuple_items_trailing_comma',
        'tuple_items : tuple_items COMMA',
        'p[0] = p[1]',
    ),
    (
        'list_comprehension',
        'list_literal : LBRACK operation_expr FOR for_target IN postfix_expr RBRACK',
        'ln, col = $pos(p, 1)\nfor_clause = $expr.new_for_comp_expr(target=p[4], iterable=p[6])\np[0] = $expr.new_comprehension_expr(output=p[2], iterators=for_clause, lineno=ln, col=col)',
    ),
    (
        'list_comprehension_cond',
        'list_literal : LBRACK operation_expr FOR for_target IN postfix_expr IF operation_expr RBRACK',
        'ln, col = $pos(p, 1)\nfor_clause = $expr.new_for_comp_expr(target=p[4], iterable=p[6], condition=p[8])\np[0] = $expr.new_comprehension_expr(output=p[2], iterators=for_clause, lineno=ln, col=col)',
    ),
    (
        'dict_comprehension',
        'dict_literal : LBRACE operation_expr COLON operation_expr FOR for_target IN postfix_expr RBRACE',
        'ln, col = $pos(p, 1)\nentry = $expr.new_dict_entry_expr(key=p[2], value=p[4])\nfor_clause = $expr.new_for_comp_expr(target=p[6], iterable=p[8])\np[0] = $expr.new_comprehension_expr(output=entry, iterators=for_clause, lineno=ln, col=col)',
    ),
    (
        'dict_comprehension_cond',
        'dict_literal : LBRACE operation_expr COLON operation_expr FOR for_target IN postfix_expr IF operation_expr RBRACE',
        'ln, col = $pos(p, 1)\nentry = $expr.new_dict_entry_expr(key=p[2], value=p[4])\nfor_clause = $expr.new_for_comp_expr(target=p[6], iterable=p[8], condition=p[10])\np[0] = $expr.new_comprehension_expr(output=entry, iterators=for_clause, lineno=ln, col=col)',
    ),
    (
        'set_comprehension',
        'dict_literal : LBRACE operation_expr FOR for_target IN postfix_expr RBRACE',
        'ln, col = $pos(p, 1)\nfor_clause = $expr.new_for_comp_expr(target=p[4], iterable=p[6])\np[0] = $expr.new_comprehension_expr(output=p[2], iterators=for_clause, lineno=ln, col=col)',
    ),
    (
        'lambda_expr',
        'unary_expr : LAMBDA lambda_params COLON postfix_expr',
        "ln, col = $pos(p, 1)\nparams_str = ', '.join(p[2])\nbody_str = $render_lambda_body(p[4])\nvalue = f'lambda {params_str}: {body_str}' if params_str else f'lambda: {body_str}'\np[0] = $expr.new_name_or_literal_expr(value, lineno=ln, col=col)",
    ),
    (
        'lambda_params_empty',
        'lambda_params :',
        'p[0] = []',
    ),
    (
        'lambda_params_single',
        'lambda_params : IDENTIFIER',
        'p[0] = [p[1]]',
    ),
    (
        'lambda_params_multi',
        'lambda_params : lambda_params COMMA IDENTIFIER',
        'p[1].append(p[3])\np[0] = p[1]',
    ),
    (
        'ident_expr',
        'ident_expr : ident\n| ident_dot',
        'ln, col = $get_last_ident_pos()\np[0] = $expr.new_name_expr(p[1], lineno=ln, col=col)',
    ),
    (
        'ident',
        'ident : IDENTIFIER\n| SELF',
        'p[0] = p[1]\n$set_last_ident_pos($pos(p, 1))',
    ),
    (
        'ident_dot',
        'ident_dot : ident DOT IDENTIFIER\n| ident_dot DOT IDENTIFIER\n| ident DOT INIT\n| ident_dot DOT INIT',
        "p[0] = p[1] + '.' + p[3]",
    ),
    (
        'module',
        'module : group_list',
        "p[0] = $decl.new_module_decl(name='__main__', code=p[1])",
    ),
    (
        'module_doc',
        'module : DOCSTRING NEWLINE module',
        'p[3].set_doc_string(p[1])\np[0] = p[3]',
    ),
    (
        'group_list',
        'group_list : group_list group',
        'p[1].append(p[2])\np[0] = p[1]',
    ),
    (
        'group_list_empty',
        'group_list :',
        'p[0] = []',
    ),
    (
        'group_list_comment',
        'group_list : group_list comment_stmt',
        'p[1].append(p[2])\np[0] = p[1]',
    ),
    (
        'group',
        'group : group_header NEWLINE section_list',
        'p[0] = $artifact_stmt.new_artifact_stmt(p[1], p[3])',
    ),
    (
        'group_with_imports',
        'group : group_header NEWLINE import_block',
        "ln, col = p[1].lineno or 0, p[1].col or 0\nimplicit_header = $artifact_decl.new_artifact_decl('core', '**', lineno=ln, col=col)\nimplicit_section = $artifact_stmt.new_artifact_stmt(implicit_header, p[3])\np[0] = $artifact_stmt.new_artifact_stmt(p[1], implicit_section)",
    ),
    (
        'group_header_start',
        'group_header : ARTIFACT_START',
        'name, qualifier, type = $parse_artifact_header(p[1])\nln, col = $pos(p, 1)\np[0] = $artifact_decl.new_artifact_decl(name, type, qualifier=qualifier, lineno=ln, col=col)',
    ),
    (
        'section_list',
        'section_list : section_list section',
        'p[1].append(p[2])\np[0] = p[1]',
    ),
    (
        'section_list_empty',
        'section_list :',
        'p[0] = []',
    ),
    (
        'section_list_comment',
        'section_list : section_list comment_stmt',
        'p[1].append(p[2])\np[0] = p[1]',
    ),
    (
        'section',
        'section : section_header NEWLINE section_body',
        'p[0] = $artifact_stmt.new_artifact_stmt(p[1], p[3])',
    ),
    (
        'section_annotated',
        'section : annots section_header NEWLINE section_body',
        '$apply_annotations(p[2], p[1])\np[0] = $artifact_stmt.new_artifact_stmt(p[2], p[4])',
    ),
    (
        'section_post_annotated',
        'section : section_header NEWLINE annots section_body',
        '$apply_annotations(p[1], p[3])\np[0] = $artifact_stmt.new_artifact_stmt(p[1], p[4])',
    ),
    (
        'section_header_section',
        'section_header : ARTIFACT_SECTION',
        'name, qualifier, type = $parse_artifact_header(p[1])\nln, col = $pos(p, 1)\np[0] = $artifact_decl.new_artifact_decl(name, type, qualifier=qualifier, lineno=ln, col=col)',
    ),
    (
        'annots_single',
        'annots : annot',
        'p[0] = [p[1]]',
    ),
    (
        'annots_multi',
        'annots : annots annot',
        'p[0] = p[1] + [p[2]]',
    ),
    (
        'annot_obsolete',
        'annot : OBSOLETE NEWLINE',
        "p[0] = {'type': 'Annot', 'kind': 'OBSOLETE', 'text': p[1]}",
    ),
    (
        'annot_todo',
        'annot : TODO NEWLINE',
        "p[0] = {'type': 'Annot', 'kind': 'TODO', 'text': p[1]}",
    ),
    (
        'annot_see',
        'annot : SEE NEWLINE',
        "p[0] = {'type': 'Annot', 'kind': 'SEE', 'text': p[1]}",
    ),
    (
        'section_body_class',
        'section_body : class_def',
        'p[0] = [$stmt.new_decl_stmt(p[1])]',
    ),
    (
        'section_body_import',
        'section_body : import_block',
        None,
    ),
    (
        'section_body_function',
        'section_body : function_decl',
        'p[0] = [$stmt.new_decl_stmt(p[1])]',
    ),
    (
        'section_body_decorated',
        'section_body : decorator_stmt section_body',
        'p[0] = [p[1]] + p[2]',
    ),
    (
        'section_body_const',
        'section_body : const_block',
        'p[0] = [$stmt.new_decl_stmt(d) for d in p[1]]',
    ),
    (
        'function_decl',
        'function_decl : DEF function_name function_type COLON NEWLINE INDENT function_doc_string snippet_list DEDENT',
        'ln, col = $pos(p, 1)\np[0] = $decl.new_func_decl( name=p[2], type=p[3], doc_string=p[7], body=p[8], lineno=ln, col=col, )',
    ),
    (
        'function_name',
        'function_name : IDENTIFIER',
        None,
    ),
    (
        'function_type',
        'function_type : LPAREN function_param_list RPAREN ret_annot',
        'p[0] = $type.new_func_type(params=p[2], return_type=p[4])',
    ),
    (
        'function_param_list',
        'function_param_list : param_list',
        None,
    ),
    (
        'function_param_list_empty',
        'function_param_list :',
        'p[0] = []',
    ),
    (
        'function_doc_string',
        'function_doc_string : DOCSTRING NEWLINE',
        'p[0] = p[1]',
    ),
    (
        'function_doc_string_empty',
        'function_doc_string :',
        'p[0] = None',
    ),
    (
        'member_list',
        'member_list : member_list member',
        'p[1].append(p[2])\np[0] = p[1]',
    ),
    (
        'member_list_single',
        'member_list : member',
        'p[0] = [p[1]]',
    ),
    (
        'member_list_empty',
        'member_list :',
        'p[0] = []',
    ),
    (
        'member_decl',
        'member : ARTIFACT_MEMBER NEWLINE member_body',
        'kind = $parse_member_kind(p[1])\nqualifier = $parse_member_qualifier(p[1])\nln, col = $pos(p, 1)\np[0] = $artifact_decl.new_member_decl(kind, p[3], qualifier=qualifier, lineno=ln, col=col)',
    ),
    (
        'member_annotated',
        'member : annots ARTIFACT_MEMBER NEWLINE member_body',
        'kind = $parse_member_kind(p[2])\nqualifier = $parse_member_qualifier(p[2])\nln, col = $pos(p, 2)\np[0] = $artifact_decl.new_member_decl(kind, p[4], annots=p[1], qualifier=qualifier, lineno=ln, col=col)\n$apply_annotations(p[0], p[1])',
    ),
    (
        'member_post_annotated',
        'member : ARTIFACT_MEMBER NEWLINE annots member_body',
        'kind = $parse_member_kind(p[1])\nqualifier = $parse_member_qualifier(p[1])\nln, col = $pos(p, 1)\np[0] = $artifact_decl.new_member_decl(kind, p[4], annots=p[3], qualifier=qualifier, lineno=ln, col=col)\n$apply_annotations(p[0], p[3])',
    ),
    (
        'member_body_single',
        'member_body : member_stmt',
        None,
    ),
    (
        'member_body_multi',
        'member_body : member_body member_stmt',
        'p[1].extend(p[2])\np[0] = p[1]',
    ),
    (
        'member_attr_stmt',
        'member_stmt : attr_decl',
        'p[0] = [$stmt.new_decl_stmt(p[1])]',
    ),
    (
        'member_body_method',
        'member_stmt : method_decl',
        'p[0] = [$stmt.new_decl_stmt(p[1])]',
    ),
    (
        'member_body_async_method',
        'member_stmt : ASYNC method_decl',
        "p[2].metadata['async'] = True\np[0] = [$stmt.new_decl_stmt(p[2])]",
    ),
    (
        'member_stmt_method_decorated',
        'member_stmt : decorator_stmt member_stmt',
        'p[0] = [p[1]] + p[2]',
    ),
)

# *** functions

# ** function: load_document
def load_document() -> dict:
    '''
    Load the declared production catalogue document.

    :return: The YAML document.
    :rtype: dict
    '''

    # Read the production catalogue with a safe YAML loader.
    with (_ASSETS_DIR / 'productions.yml').open(encoding='utf-8') as handle:
        return yaml.safe_load(handle)

# ** function: load_productions
def load_productions() -> list:
    '''
    Load the declared production_rules list.

    :return: The production rule list.
    :rtype: list
    '''

    # Return the single catalogue list.
    return load_document()['production_rules']

# ** function: expand_productions
def expand_productions() -> list:
    '''
    Expand each production item to a name and body pair.

    :return: Ordered (name, body) pairs.
    :rtype: list
    '''

    # Expand each single-key production map.
    return [next(iter(item.items())) for item in load_productions()]

# ** function: rewrite_table
def rewrite_table() -> dict:
    '''
    Build unique stub bindings for the declared shorthand vocabulary.

    :return: Shorthand-to-class bindings.
    :rtype: dict
    '''

    # Each shorthand compiles to its own class name.
    return {
        shorthand: type(shorthand[1:], (), {})
        for shorthand in _SHORTHANDS
    }

# *** tests

# ** test: production_catalogue_count
def test_production_catalogue_count() -> None:
    '''
    Test that production_rules has 285 items.
    '''

    # The document has one top-level list of the declared length.
    document = load_document()
    assert list(document) == ['production_rules']
    assert len(document['production_rules']) == 285

# ** test: production_catalogue_identifiers
def test_production_catalogue_identifiers() -> None:
    '''
    Test that the identifier list equals the declared order.
    '''

    # Expand the catalogue in file order.
    pairs = expand_productions()
    names = [name for name, _body in pairs]

    # Each item is a single-key map in §4.5 order.
    assert all(len(item) == 1 for item in load_productions())
    assert names == [name for name, _spec, _action in _ORDERED_PRODUCTIONS]

# ** test: production_catalogue_grammar_id
def test_production_catalogue_grammar_id() -> None:
    '''
    Test that every production belongs to tiferet_dialect.
    '''

    # Every body carries the declared grammar id and no extra fields.
    for _name, body in expand_productions():
        assert body['grammar_id'] == _GRAMMAR_ID
        assert set(body) <= {'grammar_id', 'spec', 'action'}

# ** test: production_catalogue_specs
def test_production_catalogue_specs() -> None:
    '''
    Test that every spec equals the declared grammar pattern.
    '''

    # Compare each spec with the §4.5 pattern.
    expected = {
        name: spec for name, spec, _action in _ORDERED_PRODUCTIONS
    }
    for name, body in expand_productions():
        assert body['spec'] == expected[name]

# ** test: production_catalogue_action_omit_set
def test_production_catalogue_action_omit_set() -> None:
    '''
    Test that only the 14 pass-through productions omit action.
    '''

    # Index the catalogue by name.
    by_name = dict(expand_productions())
    expected_actions = {
        name: action for name, _spec, action in _ORDERED_PRODUCTIONS
    }

    # Pass-through productions omit the key; every other action matches.
    for name in _OMIT_ACTION:
        assert 'action' not in by_name[name]
        assert expected_actions[name] is None
    for name, body in by_name.items():
        if name in _OMIT_ACTION:
            continue
        assert body['action'].strip()
        assert body['action'].strip() == expected_actions[name]

# ** test: production_catalogue_const_group
def test_production_catalogue_const_group() -> None:
    '''
    Test that the DI constants-group productions have the declared specs.
    '''

    # Index the catalogue by name.
    by_name = dict(expand_productions())

    # Each constants-group production is present with its §4.3 spec.
    for name, spec in _CONST_GROUP_SPECS.items():
        assert name in by_name
        assert by_name[name]['spec'] == spec
        assert by_name[name]['action'].strip()

# ** test: production_catalogue_tuple_yield
def test_production_catalogue_tuple_yield() -> None:
    '''
    Test that tuple-valued yield productions build a tuple expression statement.
    '''

    # Index the catalogue by name.
    by_name = dict(expand_productions())

    # Each yield production is present with its §4.4 spec.
    for name, spec in _TUPLE_YIELD_SPECS.items():
        assert name in by_name
        assert by_name[name]['spec'] == spec

    # stmt_yield builds a tuple expression, then an expression statement.
    action = by_name['stmt_yield']['action']
    tuple_at = action.index('$expr.new_tuple_expr')
    stmt_at = action.index('$stmt.new_expr_stmt')
    assert tuple_at < stmt_at

# ** test: production_catalogue_shorthands
def test_production_catalogue_shorthands() -> None:
    '''
    Test that actions call only the declared rewrite shorthands.
    '''

    # Collect every shorthand token from the catalogue actions.
    used = set()
    for _name, body in expand_productions():
        action = body.get('action') or ''
        used.update(re.findall(r'\$[A-Za-z_][A-Za-z0-9_]*', action))

    # No action introduces a shorthand outside §4.2.
    assert used <= set(_SHORTHANDS)

# ** test: production_catalogue_actions_compile
def test_production_catalogue_actions_compile() -> None:
    '''
    Test that every action compiles inside the rewrite evaluator.
    '''

    # Bind each declared shorthand to a uniquely named stub.
    rewrites = rewrite_table()

    # Compile each action the way tiferet-ly compiles a production body.
    for name, body in expand_productions():
        action = body.get('action')
        if action is None:
            continue
        RuleTranslator._compile_action(
            f'p_{name}',
            'p',
            action,
            name,
            rewrites=rewrites,
        )

# ** test: parser_modules_absent
def test_parser_modules_absent() -> None:
    '''
    Test that hand-written parser modules are not part of this catalogue.
    '''

    # Neither the assets parser nor the utils parser module exists.
    assert not (_ASSETS_DIR / 'parser.py').exists()
    assert not (_ASSETS_DIR.parent / 'utils' / 'python_parser.py').exists()
