"""Compiler Default Production Catalog Tests"""

# *** imports

# ** app
from ..grammar import TIFERET_DIALECT_ID
from ..production import COMPILER_DEFAULT_PRODUCTIONS

# *** constants

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

# *** tests

# ** test: compiler_default_productions_endpoints
def test_compiler_default_productions_endpoints() -> None:
    '''
    Test the production count, endpoints, and omitted-action set.
    '''

    # Declared order starts and ends at the published endpoints.
    names = list(COMPILER_DEFAULT_PRODUCTIONS)
    assert len(names) == 285
    assert names[0] == 'import_block_single'
    assert names[-1] == 'member_stmt_method_decorated'

    # Exactly the fourteen pass-through productions omit action.
    omitted = {
        name
        for name, body in COMPILER_DEFAULT_PRODUCTIONS.items()
        if 'action' not in body
    }
    assert omitted == set(_OMIT_ACTION)

# ** test: import_block_single_spec_and_action
def test_import_block_single_spec_and_action() -> None:
    '''
    Test the first production's spec and action.
    '''

    # The action keeps the loaded trailing newline. Shorthand calls are not rewritten.
    body = COMPILER_DEFAULT_PRODUCTIONS['import_block_single']
    assert body['spec'] == 'import_block : import_stmt'
    assert body['action'] == 'p[0] = [p[1]]\n'

# ** test: production_grammar_ids_omit_name
def test_production_grammar_ids_omit_name() -> None:
    '''
    Test that every production names the dialect id and omits name.
    '''

    # Present actions end in one newline. Absent actions are omitted, not empty.
    for body in COMPILER_DEFAULT_PRODUCTIONS.values():
        assert body['grammar_id'] is TIFERET_DIALECT_ID
        assert 'name' not in body
        assert '' not in body.values()
        action = body.get('action')
        if action is None:
            assert 'action' not in body
            continue
        assert action.endswith('\n')
        assert not action.endswith('\n\n')
