"""Utils – ASTPrinter Tests"""

# *** imports

# ** app
from ...mappers.ast import (
    DeclarationAggregate,
    ExpressionAggregate,
    StatementAggregate,
)
from ..printer import ASTPrinter

# *** tests

# ** test: print_ast_empty_module_minimal_output
def test_print_ast_empty_module_minimal_output(capsys) -> None:
    '''
    Test that an empty module prints a declaration line with its name.

    :param capsys: The stdout capture fixture.
    :type capsys: CaptureFixture
    '''

    # An empty module has no body statements.
    module = DeclarationAggregate.new_module_decl('empty_mod')
    ASTPrinter.print_ast(module)

    # The declaration line names the module.
    out = capsys.readouterr().out
    assert '[Declaration]' in out
    assert 'empty_mod' in out

# ** test: print_ast_class_declaration_includes_class_name
def test_print_ast_class_declaration_includes_class_name(capsys) -> None:
    '''
    Test that a class declaration prints its name.

    :param capsys: The stdout capture fixture.
    :type capsys: CaptureFixture
    '''

    # Wrap the class so the module body is a declaration statement.
    klass = DeclarationAggregate.new_class_decl(
        'Widget',
        subclasses=None,
        doc_string=None,
        members=None,
    )
    module = DeclarationAggregate.new_module_decl(
        'demo',
        code=StatementAggregate.new_decl_stmt(klass),
    )
    ASTPrinter.print_ast(module)

    # The class name appears on its declaration line.
    out = capsys.readouterr().out
    assert '[Declaration] name=Widget' in out

# ** test: print_ast_nested_function_is_indented
def test_print_ast_nested_function_is_indented(capsys) -> None:
    '''
    Test that a nested function declaration is indented further than its class.

    :param capsys: The stdout capture fixture.
    :type capsys: CaptureFixture
    '''

    # Nest a function declaration inside the class body.
    func = DeclarationAggregate.new_func_decl('run')
    klass = DeclarationAggregate.new_class_decl(
        'Widget',
        subclasses=None,
        doc_string=None,
        members=StatementAggregate.new_decl_stmt(func),
    )
    module = DeclarationAggregate.new_module_decl(
        'demo',
        code=StatementAggregate.new_decl_stmt(klass),
    )
    ASTPrinter.print_ast(module)

    # Compare leading spaces on the two declaration lines.
    lines = capsys.readouterr().out.splitlines()
    class_line = next(line for line in lines if '[Declaration] name=Widget' in line)
    func_line = next(line for line in lines if '[Declaration] name=run' in line)
    class_indent = len(class_line) - len(class_line.lstrip(' '))
    func_indent = len(func_line) - len(func_line.lstrip(' '))
    assert func_indent > class_indent

# ** test: print_ast_non_null_input_writes_stdout
def test_print_ast_non_null_input_writes_stdout(capsys) -> None:
    '''
    Test that a non-null module AST writes a non-empty stdout string.

    :param capsys: The stdout capture fixture.
    :type capsys: CaptureFixture
    '''

    # Any module declaration is enough to write stdout.
    module = DeclarationAggregate.new_module_decl('present')
    ASTPrinter.print_ast(module)

    # The captured stdout is not empty.
    assert capsys.readouterr().out.strip()

# ** test: print_statement_kind_after_children
def test_print_statement_kind_after_children(capsys) -> None:
    '''
    Test that a child expression prints before the statement kind line.

    :param capsys: The stdout capture fixture.
    :type capsys: CaptureFixture
    '''

    # The expression is a child of the statement, so it prints first.
    stmt = StatementAggregate.new_expr_stmt(
        ExpressionAggregate.new_name_expr('alpha'),
    )
    ASTPrinter.print_statement(stmt)

    # The expression line precedes the statement line.
    out = capsys.readouterr().out
    assert out.index('[Expression]') < out.index('[Statement] kind=')

# ** test: print_symbol_table_includes_module_name
def test_print_symbol_table_includes_module_name(capsys) -> None:
    '''
    Test that the symbol table header includes the module name.

    :param capsys: The stdout capture fixture.
    :type capsys: CaptureFixture
    '''

    # An empty scope map still prints the header.
    ASTPrinter.print_symbol_table({
        'module_name': 'error',
        'scopes': {},
    })

    # The header names the module.
    assert 'Symbol Table: error' in capsys.readouterr().out

# ** test: no_print_tree_method
def test_no_print_tree_method() -> None:
    '''
    Test that ASTPrinter has no print_tree method.
    '''

    # The printer does not expose a print_tree entry point.
    assert not hasattr(ASTPrinter, 'print_tree')
