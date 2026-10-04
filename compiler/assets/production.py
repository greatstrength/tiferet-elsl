"""Compiler Default Production Catalog"""

# *** imports

# ** app
from .grammar import TIFERET_DIALECT_ID

# *** constants

# ** constant: compiler_default_productions
COMPILER_DEFAULT_PRODUCTIONS = {
    'import_block_single': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'import_block : import_stmt',
        'action': 'p[0] = [p[1]]\n',
    },
    'import_block_multi': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'import_block : import_block import_stmt',
        'action': 'p[1].append(p[2])\np[0] = p[1]\n',
    },
    'import_stmt': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'import_stmt : IMPORT import_expr NEWLINE',
        'action': 'ln, col = $pos(p, 1)\np[0] = $stmt.new_import_stmt(p[2], lineno=ln, col=col)\n',
    },
    'import_stmt_from': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'import_stmt : FROM from_expr IMPORT import_expr NEWLINE',
        'action': 'ln, col = $pos(p, 1)\np[0] = $stmt.new_import_stmt_from(p[2], p[4], lineno=ln, col=col)\n',
    },
    'import_expr': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'import_expr : IDENTIFIER',
        'action': 'p[0] = $expr.new_name_expr(p[1])\n',
    },
    'import_expr_paren': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'import_expr : LPAREN import_expr RPAREN',
        'action': 'p[0] = p[2]\n',
    },
    'import_expr_as': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'import_expr : import_expr AS IDENTIFIER',
        'action': 'p[0] = $expr.new_import_expr_as(p[1], p[3])\n',
    },
    'import_expr_multi': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'import_expr : import_expr COMMA IDENTIFIER',
        'action': 'p[0] = $expr.new_import_expr_multi(p[1], p[3])\n',
    },
    'import_expr_trailing_comma': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'import_expr : import_expr COMMA',
        'action': 'p[0] = p[1]\n',
    },
    'import_expr_dot': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'import_expr : import_expr DOT IDENTIFIER',
        'action': "p[1].name += '.' + p[3]\np[0] = p[1]\n",
    },
    'from_expr': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'from_expr : IDENTIFIER',
        'action': 'p[0] = $expr.new_name_expr(p[1])\n',
    },
    'from_expr_dot_only': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'from_expr : DOT',
        'action': "p[0] = $expr.new_name_expr('.')\n",
    },
    'from_expr_dot': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'from_expr : DOT from_expr',
        'action': "p[2].name = '.' + p[2].name\np[0] = p[2]\n",
    },
    'from_expr_dot_middle': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'from_expr : from_expr DOT IDENTIFIER',
        'action': "p[1].name += '.' + p[3]\np[0] = p[1]\n",
    },
    'class_def': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'class_def : CLASS IDENTIFIER LPAREN super_cls_list RPAREN COLON NEWLINE INDENT class_body DEDENT',
        'action': "ln, col = $pos(p, 1)\np[0] = $decl.new_class_decl( name=p[2], subclasses=p[4], doc_string=p[9].get('docstring', None), members=[$stmt.new_decl_stmt(m) for m in (p[9].get('members') or [])], lineno=ln, col=col, )\n",
    },
    'class_def_no_parens': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'class_def : CLASS IDENTIFIER COLON NEWLINE INDENT class_body DEDENT',
        'action': "ln, col = $pos(p, 1)\np[0] = $decl.new_class_decl( name=p[2], subclasses=None, doc_string=p[6].get('docstring', None), members=[$stmt.new_decl_stmt(m) for m in (p[6].get('members') or [])], lineno=ln, col=col, )\n",
    },
    'class_body_doc': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'class_body : DOCSTRING NEWLINE member_list',
        'action': "p[0] = {'docstring': p[1], 'members': p[3]}\n",
    },
    'class_body_nodoc': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'class_body : member_list',
        'action': "p[0] = {'docstring': None, 'members': p[1]}\n",
    },
    'class_body_doc_pass': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'class_body : DOCSTRING NEWLINE PASS NEWLINE',
        'action': "p[0] = {'docstring': p[1], 'members': []}\n",
    },
    'super_cls_list_empty': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'super_cls_list :',
        'action': 'p[0] = None\n',
    },
    'super_cls_list_single': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'super_cls_list : super_cls',
    },
    'super_cls_multi': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'super_cls : super_cls COMMA super_cls',
        'action': 'p[1].set_subtype(p[3])\np[0] = p[1]\n',
    },
    'super_cls': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'super_cls : IDENTIFIER',
        'action': 'p[0] = $type.new_class_type(name=p[1])\n',
    },
    'super_cls_kwarg': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'super_cls : IDENTIFIER EQUALS IDENTIFIER',
        'action': 'p[0] = $type.new_class_type(name=p[3])\n',
    },
    'attr_decl': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'attr_decl : IDENTIFIER NEWLINE',
        'action': 'ln, col = $pos(p, 1)\np[0] = $decl.new_attr_decl(name=p[1], lineno=ln, col=col)\n',
    },
    'attr_decl_type': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'attr_decl : IDENTIFIER COLON attr_types NEWLINE',
        'action': 'ln, col = $pos(p, 1)\np[0] = $decl.new_attr_decl(name=p[1], types=p[3], lineno=ln, col=col)\n',
    },
    'attr_decl_type_init': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'attr_decl : IDENTIFIER COLON attr_types EQUALS assign_rhs NEWLINE',
        'action': 'ln, col = $pos(p, 1)\np[0] = $decl.new_attr_decl(name=p[1], types=p[3], value=p[5], lineno=ln, col=col)\n',
    },
    'attr_decl_init': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'attr_decl : IDENTIFIER EQUALS assign_rhs NEWLINE',
        'action': 'ln, col = $pos(p, 1)\np[0] = $decl.new_attr_decl(name=p[1], value=p[3], lineno=ln, col=col)\n',
    },
    'const_decl': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'const_decl : IDENTIFIER EQUALS assign_rhs NEWLINE',
        'action': 'ln, col = $pos(p, 1)\np[0] = $decl.new_attr_decl(name=p[1], value=p[3], lineno=ln, col=col)\n',
    },
    'const_decl_typed': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'const_decl : IDENTIFIER COLON attr_types EQUALS assign_rhs NEWLINE',
        'action': 'ln, col = $pos(p, 1)\np[0] = $decl.new_attr_decl(name=p[1], types=p[3], value=p[5], lineno=ln, col=col)\n',
    },
    'const_block_single': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'const_block : const_decl',
        'action': 'p[0] = [p[1]]\n',
    },
    'const_block_multi': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'const_block : const_block const_decl',
        'action': 'p[1].append(p[2])\np[0] = p[1]\n',
    },
    'type_atom_name': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'type_atom : IDENTIFIER',
    },
    'type_atom_dot': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'type_atom : type_atom DOT IDENTIFIER',
        'action': 'p[0] = p[3]\n',
    },
    'type_atom_subscript': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'type_atom : IDENTIFIER LBRACK subscript_index RBRACK',
        'action': 'p[0] = p[1]\n',
    },
    'type_atom_none': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'type_atom : NONE',
        'action': "p[0] = 'None'\n",
    },
    'type_atom_forward_ref': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'type_atom : STRING_LITERAL',
        'action': 'p[0] = p[1].strip(\'\\\'"\')\n',
    },
    'attr_types_single': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'attr_types : type_atom',
        'action': 'p[0] = $get_attribute_type(p[1])\n',
    },
    'attr_types_multi': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'attr_types : attr_types PIPE type_atom',
        'action': 'p[1].set_subtype($get_attribute_type(p[3]))\np[0] = p[1]\n',
    },
    'decorator_stmt': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'decorator_stmt : AT decorator_call NEWLINE',
        'action': 'p[0] = $stmt.new_expr_stmt(p[2])\n',
    },
    'decorator_stmt_bare': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'decorator_stmt : AT decorator_ident NEWLINE',
        'action': 'p[0] = $stmt.new_expr_stmt(p[2])\n',
    },
    'decorator_call': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'decorator_call : decorator_ident LPAREN decorator_args RPAREN',
        'action': 'p[0] = $expr.new_call_expr(p[1], p[3])\n',
    },
    'decorator_ident': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'decorator_ident : IDENTIFIER',
        'action': 'p[0] = $expr.new_name_expr(p[1])\n',
    },
    'decorator_ident_dot': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'decorator_ident : decorator_ident DOT IDENTIFIER',
        'action': "ln, col = $pos(p, 1)\np[0] = $expr.new_name_expr(name=p[1].name + '.' + p[3], lineno=ln, col=col)\n",
    },
    'decorator_params_single': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'decorator_args : decorator_arg',
        'action': 'p[0] = $expr.new_args_list_expr(p[1])\n',
    },
    'decorator_args_multi': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'decorator_args : decorator_args COMMA decorator_arg',
        'action': 'p[0] = $expr.new_args_list_expr(p[1], p[3])\n',
    },
    'decorator_arg_literal': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'decorator_arg : name_or_literal_expr',
    },
    'decorator_arg_kwarg': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'decorator_arg : IDENTIFIER EQUALS name_or_literal_expr',
        'action': 'p[0] = $expr.new_kwarg_expr(name=p[1], value=p[3])\n',
    },
    'method_decl': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'method_decl : DEF method_name method_type COLON NEWLINE INDENT method_doc_string snippet_list DEDENT',
        'action': 'ln, col = $pos(p, 1)\np[0] = $decl.new_func_decl( name=p[2], type=p[3], doc_string=p[7], body=p[8], lineno=ln, col=col, )\n',
    },
    'method_name': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'method_name : IDENTIFIER\n| INIT',
        'action': 'p[0] = p[1]\n',
    },
    'method_type': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'method_type : LPAREN method_param_list RPAREN ret_annot',
        'action': 'p[0] = $type.new_func_type(params=p[2], return_type=p[4])\n',
    },
    'method_doc_string': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'method_doc_string : DOCSTRING NEWLINE',
        'action': 'p[0] = p[1]\n',
    },
    'method_doc_string_empty': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'method_doc_string :',
        'action': 'p[0] = None\n',
    },
    'method_param_list': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'method_param_list : SELF COMMA param_list',
        'action': 'self_param = $param_list.new(name=p[1], type=$type.new_unknown_type())\np[0] = [self_param] + p[3]\n',
    },
    'method_param_list_self_only': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'method_param_list : SELF',
        'action': 'p[0] = [$param_list.new(name=p[1], type=$type.new_unknown_type())]\n',
    },
    'method_param_list_no_self': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'method_param_list : param_list',
    },
    'method_param_list_empty': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'method_param_list :',
        'action': 'p[0] = []\n',
    },
    'method_param_list_single': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'param_list : param',
        'action': 'p[0] = [p[1]]\n',
    },
    'method_param_list_multi': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'param_list : param_list COMMA param',
        'action': 'p[1].append(p[3])\np[0] = p[1]\n',
    },
    'param_list_trailing_comma': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'param_list : param_list COMMA',
        'action': 'p[0] = p[1]\n',
    },
    'method_param': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'param : IDENTIFIER',
        'action': 'p[0] = $param_list.new(name=p[1])\n',
    },
    'method_param_args': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'param : STAR IDENTIFIER',
        'action': 'p[0] = $param_list.new_args_param(name=p[2])\n',
    },
    'method_param_kwargs': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'param : DOUBLESTAR IDENTIFIER',
        'action': 'p[0] = $param_list.new_kwargs_param(name=p[2])\n',
    },
    'method_param_type': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'param : param COLON param_types',
        'action': 'p[1].set_type(p[3])\np[0] = p[1]\n',
    },
    'param_default': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'param : param EQUALS unary_expr',
        'action': 'p[1].set_default(p[3])\np[0] = p[1]\n',
    },
    'param_newline': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'param : NEWLINE param',
        'action': 'p[0] = p[2]\n',
    },
    'method_param_types_single': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'param_types : type_atom',
        'action': 'p[0] = $get_attribute_type(p[1])\n',
    },
    'method_param_types_multi': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'param_types : param_types PIPE type_atom',
        'action': 'subtype = $get_attribute_type(p[3])\np[1].set_subtype(subtype)\np[0] = p[1]\n',
    },
    'ret_annot': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'ret_annot : ARROW ret_types',
        'action': 'p[0] = p[2]\n',
    },
    'ret_annot_empty': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'ret_annot :',
        'action': 'p[0] = $type.new_null_type()\n',
    },
    'ret_types_single': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'ret_types : type_atom',
        'action': 'p[0] = $get_attribute_type(p[1])\n',
    },
    'ret_types_multi': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'ret_types : ret_types PIPE type_atom',
        'action': 'ret_type = $get_attribute_type(p[3])\np[1].set_return_type(ret_type)\np[0] = p[1]\n',
    },
    'snippet_list': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'snippet_list : snippet_list snippet',
        'action': 'p[1].append(p[2])\np[0] = p[1]\n',
    },
    'snippet_list_newline': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'snippet_list : snippet_list NEWLINE',
        'action': 'p[0] = p[1]\n',
    },
    'snippet_list_empty': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'snippet_list :',
        'action': 'p[0] = []\n',
    },
    'snippet_list_else_attach': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'snippet_list : snippet_list comment_list else_clause',
        'action': 'if p[1]:\n    $attach_dangling_else(p[1][-1].body, p[3])\np[0] = p[1]\n',
    },
    'snippet_comment': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'snippet : comment_list stmt_list',
        'action': 'p[0] = $snippet_stmt.new_snippet_stmt(comments=p[1], code=p[2])\n',
    },
    'snippet_nocomment': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'snippet : stmt_list',
        'action': 'p[0] = $snippet_stmt.new_snippet_stmt(code=p[1])\n',
    },
    'comment_list_single': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'comment_list : comment_stmt',
        'action': 'p[0] = [p[1]]\n',
    },
    'comment_list_multi': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'comment_list : comment_list comment_stmt',
        'action': 'p[1].append(p[2])\np[0] = p[1]\n',
    },
    'comment_stmt': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'comment_stmt : LINE_COMMENT NEWLINE',
        'action': 'ln, col = $pos(p, 1)\nexpr = $expr.new_comment_expr(p[1], lineno=ln, col=col)\np[0] = $stmt.new_comment_stmt(expr, lineno=ln, col=col)\n',
    },
    'stmt_list_single': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'stmt_list : stmt',
        'action': 'p[0] = [p[1]]\n',
    },
    'stmt_list': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'stmt_list : stmt_list stmt',
        'action': 'p[1].append(p[2])\np[0] = p[1]\n',
    },
    'stmt_list_newline': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'stmt_list : stmt_list NEWLINE',
        'action': 'p[0] = p[1]\n',
    },
    'stmt_list_empty': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'stmt_list :',
        'action': 'p[0] = []\n',
    },
    'stmt_return': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'stmt : RETURN return_expr NEWLINE',
        'action': 'ln, col = $pos(p, 1)\np[0] = $stmt.new_return_stmt(return_expr=p[2], lineno=ln, col=col)\n',
    },
    'stmt_yield': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'stmt : YIELD yield_values NEWLINE',
        'action': 'ln, col = $pos(p, 1)\nyielded = $expr.new_tuple_expr(elements=p[2], lineno=ln, col=col)\np[0] = $stmt.new_expr_stmt(yielded, lineno=ln, col=col)\n',
    },
    'yield_values_single': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'yield_values : operation_expr',
        'action': 'p[0] = $expr.new_args_list_expr(p[1])\n',
    },
    'yield_values_multi': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'yield_values : yield_values COMMA operation_expr',
        'action': 'p[0] = $expr.new_args_list_expr(p[1], p[3])\n',
    },
    'stmt_assign': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'stmt : assign_expr NEWLINE',
        'action': 'ln, col = $pos(p, 1)\np[0] = $stmt.new_expr_stmt(p[1], lineno=ln, col=col)\n',
    },
    'stmt_annotated_assign': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'stmt : IDENTIFIER COLON attr_types EQUALS assign_rhs NEWLINE',
        'action': 'ln, col = $pos(p, 1)\ntarget = $expr.new_name_expr(p[1], lineno=ln, col=col)\nassign = $expr.new_assign_expr(target=target, value=p[5], lineno=ln, col=col)\np[0] = $stmt.new_expr_stmt(assign, lineno=ln, col=col)\n',
    },
    'stmt_operator': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'stmt : operation_expr NEWLINE',
        'action': 'ln, col = $pos(p, 1)\np[0] = $stmt.new_expr_stmt(p[1], lineno=ln, col=col)\n',
    },
    'stmt_call': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'stmt : call_expr NEWLINE',
        'action': 'ln, col = $pos(p, 1)\np[0] = $stmt.new_expr_stmt(p[1], lineno=ln, col=col)\n',
    },
    'stmt_import_local': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'stmt : import_stmt',
        'action': 'p[0] = p[1]\n',
    },
    'block_body_stmt': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'block_body : stmt',
        'action': 'p[0] = [p[1]]\n',
    },
    'block_body_comment': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'block_body : comment_stmt',
        'action': 'p[0] = [p[1]]\n',
    },
    'block_body_extend_stmt': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'block_body : block_body stmt',
        'action': 'p[1].append(p[2])\np[0] = p[1]\n',
    },
    'block_body_extend_comment': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'block_body : block_body comment_stmt',
        'action': 'p[1].append(p[2])\np[0] = p[1]\n',
    },
    'block_body_newline': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'block_body : block_body NEWLINE',
        'action': 'p[0] = p[1]\n',
    },
    'block_body_empty': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'block_body :',
        'action': 'p[0] = []\n',
    },
    'block_body_else_attach': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'block_body : block_body comment_list else_clause',
        'action': '$attach_dangling_else(p[1], p[3])\np[0] = p[1]\n',
    },
    'stmt_if': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'stmt : IF operation_expr COLON NEWLINE INDENT block_body DEDENT opt_else',
        'action': 'ln, col = $pos(p, 1)\np[0] = $stmt.new_if_stmt(condition=p[2], body=p[6], else_body=p[8], lineno=ln, col=col)\n',
    },
    'stmt_if_inline': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'stmt : IF operation_expr COLON stmt',
        'action': 'ln, col = $pos(p, 1)\np[0] = $stmt.new_if_stmt(condition=p[2], body=p[4], lineno=ln, col=col)\n',
    },
    'opt_else': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'opt_else : else_clause',
    },
    'opt_else_empty': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'opt_else :',
        'action': 'p[0] = None\n',
    },
    'else_clause': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'else_clause : ELSE COLON NEWLINE INDENT block_body DEDENT',
        'action': 'p[0] = p[5]\n',
    },
    'else_clause_inline': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'else_clause : ELSE COLON stmt',
        'action': 'p[0] = [p[3]]\n',
    },
    'elif_clause': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'else_clause : ELIF operation_expr COLON NEWLINE INDENT block_body DEDENT opt_else',
        'action': 'ln, col = $pos(p, 1)\np[0] = [$stmt.new_if_stmt(condition=p[2], body=p[6], else_body=p[8], lineno=ln, col=col)]\n',
    },
    'elif_clause_inline': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'else_clause : ELIF operation_expr COLON stmt',
        'action': 'ln, col = $pos(p, 1)\np[0] = [$stmt.new_if_stmt(condition=p[2], body=p[4], lineno=ln, col=col)]\n',
    },
    'stmt_raise': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'stmt : RAISE operation_expr NEWLINE\n| RAISE call_expr NEWLINE',
        'action': 'ln, col = $pos(p, 1)\np[0] = $stmt.new_raise_stmt(expr=p[2], lineno=ln, col=col)\n',
    },
    'stmt_raise_from': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'stmt : RAISE operation_expr FROM operation_expr NEWLINE\n| RAISE call_expr FROM operation_expr NEWLINE',
        'action': 'ln, col = $pos(p, 1)\np[0] = $stmt.new_raise_stmt(expr=p[2], lineno=ln, col=col)\n',
    },
    'stmt_raise_bare': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'stmt : RAISE NEWLINE',
        'action': 'ln, col = $pos(p, 1)\np[0] = $stmt.new_raise_stmt(lineno=ln, col=col)\n',
    },
    'stmt_pass': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'stmt : PASS NEWLINE',
        'action': 'ln, col = $pos(p, 1)\np[0] = $stmt.new_pass_stmt(lineno=ln, col=col)\n',
    },
    'stmt_for': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'stmt : FOR for_target IN operation_expr COLON NEWLINE INDENT block_body DEDENT',
        'action': 'ln, col = $pos(p, 1)\np[0] = $stmt.new_for_stmt(target=p[2], iterable=p[4], body=p[8], lineno=ln, col=col)\n',
    },
    'stmt_for_inline': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'stmt : FOR for_target IN operation_expr COLON stmt',
        'action': 'ln, col = $pos(p, 1)\np[0] = $stmt.new_for_stmt(target=p[2], iterable=p[4], body=p[6], lineno=ln, col=col)\n',
    },
    'for_target': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'for_target : ident_expr',
    },
    'for_target_tuple': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'for_target : for_target COMMA ident_expr',
        'action': 'p[0] = $expr.new_tuple_expr($expr.new_args_list_expr(p[1], p[3]))\n',
    },
    'stmt_while': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'stmt : WHILE operation_expr COLON NEWLINE INDENT block_body DEDENT',
        'action': 'ln, col = $pos(p, 1)\np[0] = $stmt.new_while_stmt(condition=p[2], body=p[6], lineno=ln, col=col)\n',
    },
    'stmt_while_inline': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'stmt : WHILE operation_expr COLON stmt',
        'action': 'ln, col = $pos(p, 1)\np[0] = $stmt.new_while_stmt(condition=p[2], body=p[4], lineno=ln, col=col)\n',
    },
    'opt_comments': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'opt_comments : comment_list',
    },
    'opt_comments_empty': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'opt_comments :',
        'action': 'p[0] = None\n',
    },
    'stmt_try': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'stmt : TRY COLON NEWLINE INDENT block_body DEDENT opt_comments except_clauses opt_finally',
        'action': 'ln, col = $pos(p, 1)\np[0] = $stmt.new_try_stmt(body=p[5], except_body=p[8], finally_body=p[9], lineno=ln, col=col)\n',
    },
    'opt_finally': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'opt_finally : FINALLY COLON NEWLINE INDENT block_body DEDENT',
        'action': 'p[0] = p[5]\n',
    },
    'opt_finally_empty': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'opt_finally :',
        'action': 'p[0] = None\n',
    },
    'except_clauses_single': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'except_clauses : except_clause',
        'action': 'p[0] = [p[1]]\n',
    },
    'except_clauses_multi': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'except_clauses : except_clauses except_clause',
        'action': 'p[1].append(p[2])\np[0] = p[1]\n',
    },
    'except_clause': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'except_clause : EXCEPT COLON NEWLINE INDENT block_body DEDENT',
        'action': 'ln, col = $pos(p, 1)\np[0] = $stmt.new_if_stmt(condition=None, body=p[5], lineno=ln, col=col)\n',
    },
    'except_clause_inline': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'except_clause : EXCEPT COLON stmt',
        'action': 'ln, col = $pos(p, 1)\np[0] = $stmt.new_if_stmt(condition=None, body=p[3], lineno=ln, col=col)\n',
    },
    'exc_target_single': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'exc_target : ident_expr',
    },
    'exc_target_tuple': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'exc_target : LPAREN except_types RPAREN',
        'action': 'p[0] = $expr.new_tuple_expr(elements=p[2])\n',
    },
    'except_types_single': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'except_types : ident_expr',
        'action': 'p[0] = $expr.new_args_list_expr(p[1])\n',
    },
    'except_types_multi': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'except_types : except_types COMMA ident_expr',
        'action': 'p[0] = $expr.new_args_list_expr(p[1], p[3])\n',
    },
    'except_clause_type': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'except_clause : EXCEPT exc_target COLON NEWLINE INDENT block_body DEDENT',
        'action': 'ln, col = $pos(p, 1)\np[0] = $stmt.new_if_stmt(condition=p[2], body=p[6], lineno=ln, col=col)\n',
    },
    'except_clause_type_inline': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'except_clause : EXCEPT exc_target COLON stmt',
        'action': 'ln, col = $pos(p, 1)\np[0] = $stmt.new_if_stmt(condition=p[2], body=p[4], lineno=ln, col=col)\n',
    },
    'except_clause_type_as': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'except_clause : EXCEPT exc_target AS IDENTIFIER COLON NEWLINE INDENT block_body DEDENT',
        'action': 'ln, col = $pos(p, 1)\nalias = $expr.new_import_expr_as(p[2], p[4])\np[0] = $stmt.new_if_stmt(condition=alias, body=p[8], lineno=ln, col=col)\n',
    },
    'except_clause_type_as_inline': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'except_clause : EXCEPT exc_target AS IDENTIFIER COLON stmt',
        'action': 'ln, col = $pos(p, 1)\nalias = $expr.new_import_expr_as(p[2], p[4])\np[0] = $stmt.new_if_stmt(condition=alias, body=p[6], lineno=ln, col=col)\n',
    },
    'stmt_with': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'stmt : WITH operation_expr AS ident_expr COLON NEWLINE INDENT block_body DEDENT',
        'action': 'ln, col = $pos(p, 1)\np[0] = $stmt.new_with_stmt(context_expr=p[2], target=p[4], body=p[8], lineno=ln, col=col)\n',
    },
    'stmt_with_inline': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'stmt : WITH operation_expr AS ident_expr COLON stmt',
        'action': 'ln, col = $pos(p, 1)\np[0] = $stmt.new_with_stmt(context_expr=p[2], target=p[4], body=p[6], lineno=ln, col=col)\n',
    },
    'stmt_with_no_as': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'stmt : WITH operation_expr COLON NEWLINE INDENT block_body DEDENT',
        'action': 'ln, col = $pos(p, 1)\np[0] = $stmt.new_with_stmt(context_expr=p[2], target=None, body=p[6], lineno=ln, col=col)\n',
    },
    'stmt_with_no_as_inline': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'stmt : WITH operation_expr COLON stmt',
        'action': 'ln, col = $pos(p, 1)\np[0] = $stmt.new_with_stmt(context_expr=p[2], target=None, body=p[4], lineno=ln, col=col)\n',
    },
    'stmt_with_call': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'stmt : WITH call_expr AS ident_expr COLON NEWLINE INDENT block_body DEDENT',
        'action': 'ln, col = $pos(p, 1)\np[0] = $stmt.new_with_stmt(context_expr=p[2], target=p[4], body=p[8], lineno=ln, col=col)\n',
    },
    'stmt_with_call_inline': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'stmt : WITH call_expr AS ident_expr COLON stmt',
        'action': 'ln, col = $pos(p, 1)\np[0] = $stmt.new_with_stmt(context_expr=p[2], target=p[4], body=p[6], lineno=ln, col=col)\n',
    },
    'stmt_assert': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'stmt : ASSERT operation_expr NEWLINE',
        'action': 'ln, col = $pos(p, 1)\np[0] = $stmt.new_assert_stmt(expr=p[2], lineno=ln, col=col)\n',
    },
    'stmt_assert_msg': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'stmt : ASSERT operation_expr COMMA operation_expr NEWLINE',
        'action': 'ln, col = $pos(p, 1)\np[0] = $stmt.new_assert_stmt(expr=p[2], msg=p[4], lineno=ln, col=col)\n',
    },
    'stmt_continue': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'stmt : CONTINUE NEWLINE',
        'action': 'ln, col = $pos(p, 1)\np[0] = $stmt.new_continue_stmt(lineno=ln, col=col)\n',
    },
    'stmt_break': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'stmt : BREAK NEWLINE',
        'action': 'ln, col = $pos(p, 1)\np[0] = $stmt.new_break_stmt(lineno=ln, col=col)\n',
    },
    'stmt_del': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'stmt : DEL ident_expr NEWLINE',
        'action': 'ln, col = $pos(p, 1)\np[0] = $stmt.new_del_stmt(expr=p[2], lineno=ln, col=col)\n',
    },
    'stmt_nested_func': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'stmt : method_decl',
        'action': 'p[0] = $stmt.new_decl_stmt(p[1])\n',
    },
    'stmt_async_func': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'stmt : ASYNC method_decl',
        'action': "p[2].metadata['async'] = True\np[0] = $stmt.new_decl_stmt(p[2])\n",
    },
    'assign_expr': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'assign_expr : ident_expr EQUALS assign_rhs',
        'action': 'ln, col = $pos(p, 2)\np[0] = $expr.new_assign_expr(target=p[1], value=p[3], lineno=ln, col=col)\n',
    },
    'assign_expr_tuple_unpack': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'assign_expr : tuple_unpack_target EQUALS assign_rhs',
        'action': 'ln, col = $pos(p, 2)\np[0] = $expr.new_assign_expr(target=p[1], value=p[3], lineno=ln, col=col)\n',
    },
    'assign_expr_subscript': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'assign_expr : postfix_subscript EQUALS assign_rhs',
        'action': 'ln, col = $pos(p, 2)\np[0] = $expr.new_assign_expr(target=p[1], value=p[3], lineno=ln, col=col)\n',
    },
    'tuple_unpack_target_pair': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'tuple_unpack_target : ident_expr COMMA ident_expr',
        'action': 'p[0] = $expr.new_tuple_expr(elements=$expr.new_args_list_expr(p[1], p[3]))\n',
    },
    'tuple_unpack_target_multi': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'tuple_unpack_target : tuple_unpack_target COMMA ident_expr',
        'action': 'p[0] = $expr.new_tuple_expr(elements=$expr.new_args_list_expr(p[1], p[3]))\n',
    },
    'assign_rhs': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'assign_rhs : operation_expr\n| call_expr',
        'action': 'p[0] = p[1]\n',
    },
    'return_expr': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'return_expr : operation_expr\n| call_expr',
        'action': 'p[0] = p[1]\n',
    },
    'return_expr_tuple': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'return_expr : return_expr COMMA operation_expr',
        'action': 'p[0] = $expr.new_tuple_expr(elements=$expr.new_args_list_expr(p[1], p[3]))\n',
    },
    'return_empty_expr': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'return_expr :',
        'action': 'p[0] = None\n',
    },
    'operation_expr': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'operation_expr : or_expr',
    },
    'operation_expr_ternary': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'operation_expr : or_expr IF or_expr ELSE operation_expr',
        'action': 'ln, col = $pos(p, 2)\np[0] = $expr.new_ternary_expr(true_val=p[1], condition=p[3], false_val=p[5], lineno=ln, col=col)\n',
    },
    'or_expr': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'or_expr : or_expr OR and_expr\n| and_expr',
        'action': 'if len(p) == 4:\n    ln, col = $pos(p, 2)\n    p[0] = $expr.new_operator_expr(left=p[1], operator=p[2], right=p[3], lineno=ln, col=col)\nelse:\n    p[0] = p[1]\n',
    },
    'and_expr': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'and_expr : and_expr AND not_expr\n| not_expr',
        'action': 'if len(p) == 4:\n    ln, col = $pos(p, 2)\n    p[0] = $expr.new_operator_expr(left=p[1], operator=p[2], right=p[3], lineno=ln, col=col)\nelse:\n    p[0] = p[1]\n',
    },
    'not_expr': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'not_expr : NOT not_expr\n| comparison_expr',
        'action': 'if len(p) == 3:\n    ln, col = $pos(p, 1)\n    p[0] = $expr.new_not_expr(operand=p[2], lineno=ln, col=col)\nelse:\n    p[0] = p[1]\n',
    },
    'comparison_expr': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'comparison_expr : additive_expr comparison_op additive_expr\n| additive_expr',
        'action': 'if len(p) == 4:\n    ln, col = $get_last_op_pos()\n    p[0] = $expr.new_operator_expr(left=p[1], operator=p[2], right=p[3], lineno=ln, col=col)\nelse:\n    p[0] = p[1]\n',
    },
    'comparison_op': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'comparison_op : EQEQ\n| NOTEQ\n| LT\n| GT\n| LTEQ\n| GTEQ\n| PIPE\n| AMPERSAND\n| IS\n| IN',
        'action': 'p[0] = p[1]\n$set_last_op_pos($pos(p, 1))\n',
    },
    'comparison_op_is_not': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'comparison_op : IS NOT',
        'action': "p[0] = 'is not'\n$set_last_op_pos($pos(p, 1))\n",
    },
    'comparison_op_not_in': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'comparison_op : NOT IN',
        'action': "p[0] = 'not in'\n$set_last_op_pos($pos(p, 1))\n",
    },
    'additive_expr': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'additive_expr : additive_expr PLUS multiplicative_expr\n| additive_expr MINUS multiplicative_expr\n| multiplicative_expr',
        'action': 'if len(p) == 4:\n    ln, col = $pos(p, 2)\n    p[0] = $expr.new_operator_expr(left=p[1], operator=p[2], right=p[3], lineno=ln, col=col)\nelse:\n    p[0] = p[1]\n',
    },
    'multiplicative_expr': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'multiplicative_expr : multiplicative_expr STAR exponential_expr\n| multiplicative_expr SLASH exponential_expr\n| multiplicative_expr DOUBLESLASH exponential_expr\n| multiplicative_expr PERCENT exponential_expr\n| exponential_expr',
        'action': 'if len(p) == 4:\n    ln, col = $pos(p, 2)\n    p[0] = $expr.new_operator_expr(left=p[1], operator=p[2], right=p[3], lineno=ln, col=col)\nelse:\n    p[0] = p[1]\n',
    },
    'exponential_expr': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'exponential_expr : unary_expr DOUBLESTAR exponential_expr\n| unary_expr',
        'action': 'if len(p) == 4:\n    ln, col = $pos(p, 2)\n    p[0] = $expr.new_operator_expr(left=p[1], operator=p[2], right=p[3], lineno=ln, col=col)\nelse:\n    p[0] = p[1]\n',
    },
    'unary_expr': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'unary_expr : MINUS unary_expr\n| postfix_expr',
        'action': 'if len(p) == 3:\n    ln, col = $pos(p, 1)\n    p[0] = $expr.new_unary_minus_expr(operand=p[2], lineno=ln, col=col)\nelse:\n    p[0] = p[1]\n',
    },
    'postfix_expr': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'postfix_expr : name_or_literal_expr\n| postfix_subscript\n| call_expr',
        'action': 'p[0] = p[1]\n',
    },
    'postfix_subscript': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'postfix_subscript : name_or_literal_expr LBRACK subscript_index RBRACK',
        'action': 'ln, col = $pos(p, 1)\np[0] = $expr.new_subscript_expr(target=p[1], index=p[3], lineno=ln, col=col)\n',
    },
    'postfix_subscript_on_call': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'postfix_subscript : call_expr LBRACK subscript_index RBRACK',
        'action': 'ln, col = $pos(p, 1)\np[0] = $expr.new_subscript_expr(target=p[1], index=p[3], lineno=ln, col=col)\n',
    },
    'subscript_index': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'subscript_index : operation_expr',
    },
    'subscript_index_multi': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'subscript_index : subscript_index COMMA operation_expr',
        'action': 'p[0] = $expr.new_args_list_expr(p[1], p[3])\n',
    },
    'subscript_slice': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'subscript_index : operation_expr COLON operation_expr',
        'action': 'p[0] = $expr.new_slice_expr(start=p[1], stop=p[3])\n',
    },
    'subscript_slice_start_only': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'subscript_index : operation_expr COLON',
        'action': 'p[0] = $expr.new_slice_expr(start=p[1])\n',
    },
    'subscript_slice_stop_only': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'subscript_index : COLON operation_expr',
        'action': 'p[0] = $expr.new_slice_expr(stop=p[2])\n',
    },
    'subscript_slice_empty': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'subscript_index : COLON',
        'action': 'p[0] = $expr.new_slice_expr()\n',
    },
    'await_expr': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'call_expr : AWAIT call_expr\n| AWAIT ident_expr',
        'action': 'ln, col = $pos(p, 1)\np[0] = $expr.new_await_expr(operand=p[2], lineno=ln, col=col)\n',
    },
    'call_expr': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'call_expr : ident_expr LPAREN call_args RPAREN',
        'action': 'ln, col = $pos(p, 1)\np[0] = $expr.new_call_expr(p[1], p[3], lineno=ln, col=col)\n',
    },
    'call_expr_chained': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'call_expr : postfix_expr DOT IDENTIFIER LPAREN call_args RPAREN',
        'action': 'ln, col = $pos(p, 1)\ncallee = $expr.new_attribute_expr(receiver=p[1], attr=p[3], lineno=ln, col=col)\np[0] = $expr.new_call_expr(callee, p[5], lineno=ln, col=col)\n',
    },
    'call_expr_chained_init': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'call_expr : postfix_expr DOT INIT LPAREN call_args RPAREN',
        'action': 'ln, col = $pos(p, 1)\ncallee = $expr.new_attribute_expr(receiver=p[1], attr=p[3], lineno=ln, col=col)\np[0] = $expr.new_call_expr(callee, p[5], lineno=ln, col=col)\n',
    },
    'call_args_empty': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'call_args :',
        'action': 'p[0] = None\n',
    },
    'call_args_single': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'call_args : call_arg',
        'action': 'p[0] = $expr.new_args_list_expr(p[1])\n',
    },
    'call_args_multi': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'call_args : call_args COMMA call_arg',
        'action': 'p[0] = $expr.new_args_list_expr(p[1], p[3])\n',
    },
    'call_args_trailing_comma': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'call_args : call_args COMMA',
        'action': 'p[0] = p[1]\n',
    },
    'call_arg': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'call_arg : operation_expr\n| call_expr',
        'action': 'p[0] = p[1]\n',
    },
    'call_arg_genexpr': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'call_arg : operation_expr FOR for_target IN postfix_expr',
        'action': 'ln, col = $pos(p, 2)\nfor_clause = $expr.new_for_comp_expr(target=p[3], iterable=p[5])\np[0] = $expr.new_comprehension_expr(output=p[1], iterators=for_clause, lineno=ln, col=col)\n',
    },
    'call_arg_genexpr_if': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'call_arg : operation_expr FOR for_target IN postfix_expr IF operation_expr',
        'action': 'ln, col = $pos(p, 2)\nfor_clause = $expr.new_for_comp_expr(target=p[3], iterable=p[5], condition=p[7])\np[0] = $expr.new_comprehension_expr(output=p[1], iterators=for_clause, lineno=ln, col=col)\n',
    },
    'call_arg_kwarg': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'call_arg : IDENTIFIER EQUALS operation_expr\n| IDENTIFIER EQUALS call_expr',
        'action': 'p[0] = $expr.new_kwarg_expr(name=p[1], value=p[3])\n',
    },
    'call_arg_star': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'call_arg : STAR operation_expr',
        'action': 'p[0] = $expr.new_star_expr(operand=p[2])\n',
    },
    'call_arg_doublestar': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'call_arg : DOUBLESTAR operation_expr',
        'action': 'p[0] = $expr.new_double_star_expr(operand=p[2])\n',
    },
    'call_arg_newline': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'call_arg : NEWLINE call_arg',
        'action': 'p[0] = p[2]\n',
    },
    'literal_expr': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'literal_expr : STRING_LITERAL\n| NUMBER_LITERAL\n| TRUE\n| FALSE',
        'action': 'ln, col = $pos(p, 1)\np[0] = $expr.new_name_or_literal_expr(p[1], lineno=ln, col=col)\n',
    },
    'literal_prefixed_string': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'literal_expr : IDENTIFIER STRING_LITERAL',
        'action': 'ln, col = $pos(p, 1)\np[0] = $expr.new_name_or_literal_expr(p[1] + p[2], lineno=ln, col=col)\n',
    },
    'literal_concat_string': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'literal_expr : literal_expr STRING_LITERAL',
        'action': "ln, col = $pos(p, 1)\nprev_val = getattr(p[1], 'value', '') or ''\np[0] = $expr.new_name_or_literal_expr(prev_val + p[2], lineno=ln, col=col)\n",
    },
    'literal_concat_prefixed_string': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'literal_expr : literal_expr IDENTIFIER STRING_LITERAL',
        'action': "ln, col = $pos(p, 1)\nprev_val = getattr(p[1], 'value', '') or ''\np[0] = $expr.new_name_or_literal_expr(prev_val + p[2] + p[3], lineno=ln, col=col)\n",
    },
    'none_expr': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'literal_expr : NONE',
        'action': 'ln, col = $pos(p, 1)\np[0] = $expr.new_none_expr(lineno=ln, col=col)\n',
    },
    'ellipsis_expr': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'literal_expr : ELLIPSIS',
        'action': 'ln, col = $pos(p, 1)\np[0] = $expr.new_ellipsis_expr(lineno=ln, col=col)\n',
    },
    'name_or_literal_expr': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'name_or_literal_expr : ident_expr\n| literal_expr\n| list_literal\n| dict_literal\n| set_literal\n| paren_expr',
        'action': 'p[0] = p[1]\n',
    },
    'set_literal': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'set_literal : LBRACE set_items RBRACE',
        'action': 'ln, col = $pos(p, 1)\np[0] = $expr.new_set_literal_expr(elements=p[2], lineno=ln, col=col)\n',
    },
    'set_items_single': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'set_items : operation_expr',
        'action': 'p[0] = $expr.new_args_list_expr(p[1])\n',
    },
    'set_items_multi': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'set_items : set_items COMMA operation_expr',
        'action': 'p[0] = $expr.new_args_list_expr(p[1], p[3])\n',
    },
    'set_items_trailing_comma': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'set_items : set_items COMMA',
        'action': 'p[0] = p[1]\n',
    },
    'list_literal_empty': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'list_literal : LBRACK RBRACK',
        'action': 'ln, col = $pos(p, 1)\np[0] = $expr.new_list_literal_expr(lineno=ln, col=col)\n',
    },
    'list_literal': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'list_literal : LBRACK list_items RBRACK',
        'action': 'ln, col = $pos(p, 1)\np[0] = $expr.new_list_literal_expr(elements=p[2], lineno=ln, col=col)\n',
    },
    'list_items_single': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'list_items : operation_expr\n| call_expr',
        'action': 'p[0] = $expr.new_args_list_expr(p[1])\n',
    },
    'list_items_multi': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'list_items : list_items COMMA operation_expr\n| list_items COMMA call_expr',
        'action': 'p[0] = $expr.new_args_list_expr(p[1], p[3])\n',
    },
    'list_items_newline': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'list_items : list_items NEWLINE\n| NEWLINE list_items',
        'action': 'p[0] = p[1] if not isinstance(p[1], str) else p[2]\n',
    },
    'list_items_trailing_comma': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'list_items : list_items COMMA',
        'action': 'p[0] = p[1]\n',
    },
    'dict_literal_empty': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'dict_literal : LBRACE RBRACE',
        'action': 'ln, col = $pos(p, 1)\np[0] = $expr.new_dict_literal_expr(lineno=ln, col=col)\n',
    },
    'dict_literal': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'dict_literal : LBRACE dict_items RBRACE',
        'action': 'ln, col = $pos(p, 1)\np[0] = $expr.new_dict_literal_expr(entries=p[2], lineno=ln, col=col)\n',
    },
    'dict_items_single': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'dict_items : dict_entry',
        'action': 'p[0] = $expr.new_args_list_expr(p[1])\n',
    },
    'dict_items_multi': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'dict_items : dict_items COMMA dict_entry',
        'action': 'p[0] = $expr.new_args_list_expr(p[1], p[3])\n',
    },
    'dict_items_trailing_comma': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'dict_items : dict_items COMMA',
        'action': 'p[0] = p[1]\n',
    },
    'dict_items_newline': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'dict_items : dict_items NEWLINE\n| NEWLINE dict_items',
        'action': 'p[0] = p[1] if not isinstance(p[1], str) else p[2]\n',
    },
    'dict_entry': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'dict_entry : operation_expr COLON operation_expr\n| operation_expr COLON call_expr',
        'action': 'p[0] = $expr.new_dict_entry_expr(key=p[1], value=p[3])\n',
    },
    'dict_entry_unpack': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'dict_entry : DOUBLESTAR operation_expr',
        'action': 'p[0] = $expr.new_double_star_expr(operand=p[2])\n',
    },
    'paren_empty': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'paren_expr : LPAREN RPAREN',
        'action': 'ln, col = $pos(p, 1)\np[0] = $expr.new_tuple_expr(lineno=ln, col=col)\n',
    },
    'paren_genexpr': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'paren_expr : LPAREN operation_expr FOR for_target IN postfix_expr RPAREN',
        'action': 'ln, col = $pos(p, 1)\nfor_clause = $expr.new_for_comp_expr(target=p[4], iterable=p[6])\np[0] = $expr.new_comprehension_expr(output=p[2], iterators=for_clause, lineno=ln, col=col)\n',
    },
    'paren_genexpr_if': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'paren_expr : LPAREN operation_expr FOR for_target IN postfix_expr IF operation_expr RPAREN',
        'action': 'ln, col = $pos(p, 1)\nfor_clause = $expr.new_for_comp_expr(target=p[4], iterable=p[6], condition=p[8])\np[0] = $expr.new_comprehension_expr(output=p[2], iterators=for_clause, lineno=ln, col=col)\n',
    },
    'paren_expr': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'paren_expr : LPAREN operation_expr RPAREN',
        'action': 'p[0] = p[2]\n',
    },
    'paren_tuple': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'paren_expr : LPAREN tuple_items RPAREN',
        'action': 'ln, col = $pos(p, 1)\np[0] = $expr.new_tuple_expr(elements=p[2], lineno=ln, col=col)\n',
    },
    'paren_tuple_single': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'paren_expr : LPAREN operation_expr COMMA RPAREN',
        'action': 'ln, col = $pos(p, 1)\np[0] = $expr.new_tuple_expr(elements=$expr.new_args_list_expr(p[2]), lineno=ln, col=col)\n',
    },
    'tuple_items': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'tuple_items : operation_expr COMMA operation_expr',
        'action': 'p[0] = $expr.new_args_list_expr(p[1], p[3])\n',
    },
    'tuple_items_multi': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'tuple_items : tuple_items COMMA operation_expr',
        'action': 'p[0] = $expr.new_args_list_expr(p[1], p[3])\n',
    },
    'tuple_items_trailing_comma': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'tuple_items : tuple_items COMMA',
        'action': 'p[0] = p[1]\n',
    },
    'list_comprehension': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'list_literal : LBRACK operation_expr FOR for_target IN postfix_expr RBRACK',
        'action': 'ln, col = $pos(p, 1)\nfor_clause = $expr.new_for_comp_expr(target=p[4], iterable=p[6])\np[0] = $expr.new_comprehension_expr(output=p[2], iterators=for_clause, lineno=ln, col=col)\n',
    },
    'list_comprehension_cond': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'list_literal : LBRACK operation_expr FOR for_target IN postfix_expr IF operation_expr RBRACK',
        'action': 'ln, col = $pos(p, 1)\nfor_clause = $expr.new_for_comp_expr(target=p[4], iterable=p[6], condition=p[8])\np[0] = $expr.new_comprehension_expr(output=p[2], iterators=for_clause, lineno=ln, col=col)\n',
    },
    'dict_comprehension': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'dict_literal : LBRACE operation_expr COLON operation_expr FOR for_target IN postfix_expr RBRACE',
        'action': 'ln, col = $pos(p, 1)\nentry = $expr.new_dict_entry_expr(key=p[2], value=p[4])\nfor_clause = $expr.new_for_comp_expr(target=p[6], iterable=p[8])\np[0] = $expr.new_comprehension_expr(output=entry, iterators=for_clause, lineno=ln, col=col)\n',
    },
    'dict_comprehension_cond': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'dict_literal : LBRACE operation_expr COLON operation_expr FOR for_target IN postfix_expr IF operation_expr RBRACE',
        'action': 'ln, col = $pos(p, 1)\nentry = $expr.new_dict_entry_expr(key=p[2], value=p[4])\nfor_clause = $expr.new_for_comp_expr(target=p[6], iterable=p[8], condition=p[10])\np[0] = $expr.new_comprehension_expr(output=entry, iterators=for_clause, lineno=ln, col=col)\n',
    },
    'set_comprehension': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'dict_literal : LBRACE operation_expr FOR for_target IN postfix_expr RBRACE',
        'action': 'ln, col = $pos(p, 1)\nfor_clause = $expr.new_for_comp_expr(target=p[4], iterable=p[6])\np[0] = $expr.new_comprehension_expr(output=p[2], iterators=for_clause, lineno=ln, col=col)\n',
    },
    'lambda_expr': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'unary_expr : LAMBDA lambda_params COLON postfix_expr',
        'action': "ln, col = $pos(p, 1)\nparams_str = ', '.join(p[2])\nbody_str = $render_lambda_body(p[4])\nvalue = f'lambda {params_str}: {body_str}' if params_str else f'lambda: {body_str}'\np[0] = $expr.new_name_or_literal_expr(value, lineno=ln, col=col)\n",
    },
    'lambda_params_empty': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'lambda_params :',
        'action': 'p[0] = []\n',
    },
    'lambda_params_single': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'lambda_params : IDENTIFIER',
        'action': 'p[0] = [p[1]]\n',
    },
    'lambda_params_multi': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'lambda_params : lambda_params COMMA IDENTIFIER',
        'action': 'p[1].append(p[3])\np[0] = p[1]\n',
    },
    'ident_expr': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'ident_expr : ident\n| ident_dot',
        'action': 'ln, col = $get_last_ident_pos()\np[0] = $expr.new_name_expr(p[1], lineno=ln, col=col)\n',
    },
    'ident': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'ident : IDENTIFIER\n| SELF',
        'action': 'p[0] = p[1]\n$set_last_ident_pos($pos(p, 1))\n',
    },
    'ident_dot': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'ident_dot : ident DOT IDENTIFIER\n| ident_dot DOT IDENTIFIER\n| ident DOT INIT\n| ident_dot DOT INIT',
        'action': "p[0] = p[1] + '.' + p[3]\n",
    },
    'module': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'module : group_list',
        'action': "p[0] = $decl.new_module_decl(name='__main__', code=p[1])\n",
    },
    'module_doc': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'module : DOCSTRING NEWLINE module',
        'action': 'p[3].set_doc_string(p[1])\np[0] = p[3]\n',
    },
    'group_list': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'group_list : group_list group',
        'action': 'p[1].append(p[2])\np[0] = p[1]\n',
    },
    'group_list_empty': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'group_list :',
        'action': 'p[0] = []\n',
    },
    'group_list_comment': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'group_list : group_list comment_stmt',
        'action': 'p[1].append(p[2])\np[0] = p[1]\n',
    },
    'group': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'group : group_header NEWLINE section_list',
        'action': 'p[0] = $artifact_stmt.new_artifact_stmt(p[1], p[3])\n',
    },
    'group_with_imports': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'group : group_header NEWLINE import_block',
        'action': "ln, col = p[1].lineno or 0, p[1].col or 0\nimplicit_header = $artifact_decl.new_artifact_decl('core', '**', lineno=ln, col=col)\nimplicit_section = $artifact_stmt.new_artifact_stmt(implicit_header, p[3])\np[0] = $artifact_stmt.new_artifact_stmt(p[1], implicit_section)\n",
    },
    'group_header_start': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'group_header : ARTIFACT_START',
        'action': 'name, qualifier, type = $parse_artifact_header(p[1])\nln, col = $pos(p, 1)\np[0] = $artifact_decl.new_artifact_decl(name, type, qualifier=qualifier, lineno=ln, col=col)\n',
    },
    'section_list': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'section_list : section_list section',
        'action': 'p[1].append(p[2])\np[0] = p[1]\n',
    },
    'section_list_empty': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'section_list :',
        'action': 'p[0] = []\n',
    },
    'section_list_comment': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'section_list : section_list comment_stmt',
        'action': 'p[1].append(p[2])\np[0] = p[1]\n',
    },
    'section': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'section : section_header NEWLINE section_body',
        'action': 'p[0] = $artifact_stmt.new_artifact_stmt(p[1], p[3])\n',
    },
    'section_annotated': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'section : annots section_header NEWLINE section_body',
        'action': '$apply_annotations(p[2], p[1])\np[0] = $artifact_stmt.new_artifact_stmt(p[2], p[4])\n',
    },
    'section_post_annotated': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'section : section_header NEWLINE annots section_body',
        'action': '$apply_annotations(p[1], p[3])\np[0] = $artifact_stmt.new_artifact_stmt(p[1], p[4])\n',
    },
    'section_header_section': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'section_header : ARTIFACT_SECTION',
        'action': 'name, qualifier, type = $parse_artifact_header(p[1])\nln, col = $pos(p, 1)\np[0] = $artifact_decl.new_artifact_decl(name, type, qualifier=qualifier, lineno=ln, col=col)\n',
    },
    'annots_single': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'annots : annot',
        'action': 'p[0] = [p[1]]\n',
    },
    'annots_multi': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'annots : annots annot',
        'action': 'p[0] = p[1] + [p[2]]\n',
    },
    'annot_obsolete': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'annot : OBSOLETE NEWLINE',
        'action': "p[0] = {'type': 'Annot', 'kind': 'OBSOLETE', 'text': p[1]}\n",
    },
    'annot_todo': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'annot : TODO NEWLINE',
        'action': "p[0] = {'type': 'Annot', 'kind': 'TODO', 'text': p[1]}\n",
    },
    'annot_see': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'annot : SEE NEWLINE',
        'action': "p[0] = {'type': 'Annot', 'kind': 'SEE', 'text': p[1]}\n",
    },
    'section_body_class': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'section_body : class_def',
        'action': 'p[0] = [$stmt.new_decl_stmt(p[1])]\n',
    },
    'section_body_import': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'section_body : import_block',
    },
    'section_body_function': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'section_body : function_decl',
        'action': 'p[0] = [$stmt.new_decl_stmt(p[1])]\n',
    },
    'section_body_decorated': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'section_body : decorator_stmt section_body',
        'action': 'p[0] = [p[1]] + p[2]\n',
    },
    'section_body_const': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'section_body : const_block',
        'action': 'p[0] = [$stmt.new_decl_stmt(d) for d in p[1]]\n',
    },
    'function_decl': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'function_decl : DEF function_name function_type COLON NEWLINE INDENT function_doc_string snippet_list DEDENT',
        'action': 'ln, col = $pos(p, 1)\np[0] = $decl.new_func_decl( name=p[2], type=p[3], doc_string=p[7], body=p[8], lineno=ln, col=col, )\n',
    },
    'function_name': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'function_name : IDENTIFIER',
    },
    'function_type': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'function_type : LPAREN function_param_list RPAREN ret_annot',
        'action': 'p[0] = $type.new_func_type(params=p[2], return_type=p[4])\n',
    },
    'function_param_list': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'function_param_list : param_list',
    },
    'function_param_list_empty': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'function_param_list :',
        'action': 'p[0] = []\n',
    },
    'function_doc_string': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'function_doc_string : DOCSTRING NEWLINE',
        'action': 'p[0] = p[1]\n',
    },
    'function_doc_string_empty': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'function_doc_string :',
        'action': 'p[0] = None\n',
    },
    'member_list': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'member_list : member_list member',
        'action': 'p[1].append(p[2])\np[0] = p[1]\n',
    },
    'member_list_single': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'member_list : member',
        'action': 'p[0] = [p[1]]\n',
    },
    'member_list_empty': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'member_list :',
        'action': 'p[0] = []\n',
    },
    'member_decl': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'member : ARTIFACT_MEMBER NEWLINE member_body',
        'action': 'kind = $parse_member_kind(p[1])\nqualifier = $parse_member_qualifier(p[1])\nln, col = $pos(p, 1)\np[0] = $artifact_decl.new_member_decl(kind, p[3], qualifier=qualifier, lineno=ln, col=col)\n',
    },
    'member_annotated': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'member : annots ARTIFACT_MEMBER NEWLINE member_body',
        'action': 'kind = $parse_member_kind(p[2])\nqualifier = $parse_member_qualifier(p[2])\nln, col = $pos(p, 2)\np[0] = $artifact_decl.new_member_decl(kind, p[4], annots=p[1], qualifier=qualifier, lineno=ln, col=col)\n$apply_annotations(p[0], p[1])\n',
    },
    'member_post_annotated': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'member : ARTIFACT_MEMBER NEWLINE annots member_body',
        'action': 'kind = $parse_member_kind(p[1])\nqualifier = $parse_member_qualifier(p[1])\nln, col = $pos(p, 1)\np[0] = $artifact_decl.new_member_decl(kind, p[4], annots=p[3], qualifier=qualifier, lineno=ln, col=col)\n$apply_annotations(p[0], p[3])\n',
    },
    'member_body_single': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'member_body : member_stmt',
    },
    'member_body_multi': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'member_body : member_body member_stmt',
        'action': 'p[1].extend(p[2])\np[0] = p[1]\n',
    },
    'member_attr_stmt': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'member_stmt : attr_decl',
        'action': 'p[0] = [$stmt.new_decl_stmt(p[1])]\n',
    },
    'member_body_method': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'member_stmt : method_decl',
        'action': 'p[0] = [$stmt.new_decl_stmt(p[1])]\n',
    },
    'member_body_async_method': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'member_stmt : ASYNC method_decl',
        'action': "p[2].metadata['async'] = True\np[0] = [$stmt.new_decl_stmt(p[2])]\n",
    },
    'member_stmt_method_decorated': {
        'grammar_id': TIFERET_DIALECT_ID,
        'spec': 'member_stmt : decorator_stmt member_stmt',
        'action': 'p[0] = [p[1]] + p[2]\n',
    },
}
