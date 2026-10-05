"""Utils – ASTPrinter Tests"""

# *** imports

# ** core
import inspect

# ** app
from ...domain.ast import (
    Declaration,
    ExprKind,
    Expression,
    ParamList,
    Statement,
    StatementKind,
    Type,
    TypeKind,
)
from ...mappers.ast import (
    DeclarationAggregate,
    ExpressionAggregate,
    StatementAggregate,
)
from .. import ASTPrinter as exported_ast_printer
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

# ** test: ast_printer_remains_exported
def test_ast_printer_remains_exported() -> None:
    '''
    Test that compiler.utils still exports ASTPrinter.
    '''

    # The package export is the printer class.
    assert exported_ast_printer is ASTPrinter

# ** test: printer_methods_stay_static
def test_printer_methods_stay_static() -> None:
    '''
    Test that the printer methods stay static and keep their parameter names.
    '''

    # Names and parameters are the host contract, not a new walker.
    expected = {
        'print_ast': ['decl', 'indent'],
        'print_statement': ['stmt', 'indent'],
        'print_expression': ['expr', 'indent'],
        'print_type': ['type_node', 'indent'],
        'print_param_list': ['params', 'indent'],
        'print_symbol_table': ['symbol_table'],
    }

    # Each method stays static, named, and returns None.
    for name, parameters in expected.items():
        signature = inspect.signature(getattr(ASTPrinter, name))
        assert isinstance(inspect.getattr_static(ASTPrinter, name), staticmethod)
        assert list(signature.parameters) == parameters
        assert signature.return_annotation is None

        # Indent still defaults to zero when the method takes it.
        if 'indent' in signature.parameters:
            assert signature.parameters['indent'].default == 0

# ** test: declaration_does_not_define_print
def test_declaration_does_not_define_print() -> None:
    '''
    Test that Declaration does not define print.
    '''

    # The walk is not a method on the declaration.
    assert 'print' not in Declaration.__dict__

# ** test: walk_methods_do_not_format_the_line
def test_walk_methods_do_not_format_the_line() -> None:
    '''
    Test that the five walks do not format a diagnostic line.
    '''

    # The host must not rebuild the line or call the kind helper.
    forbidden = (
        '_token',
        '[Declaration]',
        '[Statement]',
        '[Expression]',
        '[Type]',
        '[Param]',
    )
    for method in (
        ASTPrinter.print_ast,
        ASTPrinter.print_statement,
        ASTPrinter.print_expression,
        ASTPrinter.print_type,
        ASTPrinter.print_param_list,
    ):
        source = inspect.getsource(method)
        for token in forbidden:
            assert token not in source

# ** test: print_symbol_table_does_not_call_describe
def test_print_symbol_table_does_not_call_describe() -> None:
    '''
    Test that the symbol-table printer does not call describe.
    '''

    # Symbol-table rows are not the five diagnostic lines.
    assert 'describe' not in inspect.getsource(ASTPrinter.print_symbol_table)

# ** test: print_ast_empty_declaration_exact_line
def test_print_ast_empty_declaration_exact_line(capsys) -> None:
    '''
    Test that an empty declaration prints only its describe line.

    :param capsys: The stdout capture fixture.
    :type capsys: CaptureFixture
    '''

    # A name-only declaration has no children.
    ASTPrinter.print_ast(Declaration(name='empty_mod'))

    # The host writes the declaration line and a newline.
    assert capsys.readouterr().out == '[Declaration] name=empty_mod\n'

# ** test: print_ast_writes_describe_sentinel
def test_print_ast_writes_describe_sentinel(capsys) -> None:
    '''
    Test that the host writes describe() instead of a formatted declaration line.

    :param capsys: The stdout capture fixture.
    :type capsys: CaptureFixture
    '''

    # A test-local subclass replaces the diagnostic line.
    class SentinelDeclaration(Declaration):
        '''
        Test-local declaration whose diagnostic line is a sentinel.
        '''

        def describe(self) -> str:
            '''
            Return the sentinel line.

            :return: The sentinel.
            :rtype: str
            '''

            # Return the sentinel without a declaration tag.
            return 'SENTINEL'

    # Print a childless sentinel declaration.
    ASTPrinter.print_ast(SentinelDeclaration(name='ignored'))

    # The host wrote the sentinel and not a formatted line.
    assert capsys.readouterr().out == 'SENTINEL\n'

# ** test: print_statement_expression_indent_exact
def test_print_statement_expression_indent_exact(capsys) -> None:
    '''
    Test that a child expression is indented by two spaces.

    :param capsys: The stdout capture fixture.
    :type capsys: CaptureFixture
    '''

    # The expression is the statement's only visited child.
    stmt = Statement(
        kind=StatementKind.EXPR,
        expr=Expression(kind=ExprKind.NAME, name='alpha'),
    )
    ASTPrinter.print_statement(stmt)

    # The expression line is two spaces, then the statement line.
    assert capsys.readouterr().out == (
        '  [Expression] kind=name name=alpha\n'
        '[Statement] kind=expr\n'
    )

# ** test: print_ast_type_line_before_declaration
def test_print_ast_type_line_before_declaration(capsys) -> None:
    '''
    Test that a declaration type prints before the declaration line.

    :param capsys: The stdout capture fixture.
    :type capsys: CaptureFixture
    '''

    # Visiting type still prints the type line. describe only suffixes the kind.
    decl = Declaration(
        name='Widget',
        type=Type(kind=TypeKind.CLASS, name='Widget'),
    )
    ASTPrinter.print_ast(decl)

    # The type line is indented. The declaration line does not repeat it.
    assert capsys.readouterr().out == (
        '  [Type] kind=class name=Widget\n'
        '[Declaration] name=Widget : class\n'
    )

# ** test: print_param_list_exact
def test_print_param_list_exact(capsys) -> None:
    '''
    Test that each parameter prints its type, then its own describe line.

    :param capsys: The stdout capture fixture.
    :type capsys: CaptureFixture
    '''

    # The first parameter has a type. The second does not.
    ASTPrinter.print_param_list([
        ParamList(
            name='x',
            required=True,
            type=Type(kind=TypeKind.INT),
        ),
        ParamList(name='y'),
    ])

    # Requiredness comes from describe, not from the host.
    assert capsys.readouterr().out == (
        '  [Type] kind=int\n'
        '[Param] name=x required\n'
        '[Param] name=y optional\n'
    )

# ** test: print_statement_skips_finally_and_next
def test_print_statement_skips_finally_and_next(capsys) -> None:
    '''
    Test that finally_body and next_expr are not diagnostic visits.

    :param capsys: The stdout capture fixture.
    :type capsys: CaptureFixture
    '''

    # Body and else body are visits. Finally and next are not.
    stmt = Statement(
        kind=StatementKind.IF_ELSE,
        body=[Statement(kind=StatementKind.PASS)],
        else_body=[Statement(kind=StatementKind.BREAK)],
        finally_body=[Statement(kind=StatementKind.CONTINUE)],
        next_expr=Expression(kind=ExprKind.NAME, name='next'),
    )
    ASTPrinter.print_statement(stmt)

    # Order is body, else body, parent. Finally and next are absent.
    assert capsys.readouterr().out == (
        '  [Statement] kind=pass\n'
        '  [Statement] kind=break\n'
        '[Statement] kind=if_else\n'
    )

# ** test: print_symbol_table_named_module_exact
def test_print_symbol_table_named_module_exact(capsys) -> None:
    '''
    Test that a named empty symbol table prints the header and a blank line.

    :param capsys: The stdout capture fixture.
    :type capsys: CaptureFixture
    '''

    # An empty scope map still prints the header.
    ASTPrinter.print_symbol_table({
        'module_name': 'error',
        'scopes': {},
    })

    # The header is followed by the blank line print already writes.
    assert capsys.readouterr().out == '=== Symbol Table: error ===\n\n'

# ** test: print_symbol_table_missing_module_name
def test_print_symbol_table_missing_module_name(capsys) -> None:
    '''
    Test that a missing module name prints unknown.

    :param capsys: The stdout capture fixture.
    :type capsys: CaptureFixture
    '''

    # Absence is not an empty string.
    ASTPrinter.print_symbol_table({
        'scopes': {},
    })

    # A missing name becomes unknown.
    assert capsys.readouterr().out == '=== Symbol Table: unknown ===\n\n'

# ** test: print_symbol_table_empty_module_name
def test_print_symbol_table_empty_module_name(capsys) -> None:
    '''
    Test that an empty module name stays empty.

    :param capsys: The stdout capture fixture.
    :type capsys: CaptureFixture
    '''

    # A present empty string is not missing.
    ASTPrinter.print_symbol_table({
        'module_name': '',
        'scopes': {},
    })

    # The header keeps the empty name.
    assert capsys.readouterr().out == '=== Symbol Table:  ===\n\n'

# ** test: print_symbol_table_scope_rows
def test_print_symbol_table_scope_rows(capsys) -> None:
    '''
    Test that a dumped scope prints symbols and children, not root_scope_path.

    :param capsys: The stdout capture fixture.
    :type capsys: CaptureFixture
    '''

    # The dumped mapping is the shape SymbolTableBuilder.build returns.
    ASTPrinter.print_symbol_table({
        'module_name': 'demo',
        'root_scope_path': 'module',
        'scopes': {
            'module': {
                'kind': 'module',
                'symbols': {
                    'Widget': {
                        'name': 'Widget',
                        'kind': 'class_def',
                        'type_annotation': 'class',
                        'source_module': 'app.widget',
                    },
                },
                'children': {
                    'Widget': 'module.Widget',
                },
            },
        },
    })

    # Scope order is mapping order. root_scope_path and parent are absent.
    assert capsys.readouterr().out == (
        '=== Symbol Table: demo ===\n'
        '\n'
        'Scope: module [module]\n'
        '  Symbols:\n'
        '    Widget [class_def] type=class from=app.widget\n'
        '  Children:\n'
        '    Widget -> module.Widget\n'
        '\n'
    )
