"""AST Post-Order Traversal Printer and Symbol Table Printer Utilities"""

# *** imports

# ** core
from typing import Any, Dict, List

# ** app
from ..mappers import Declaration, Expression, ParamList, Statement, Type

# *** utils

# ** util: ast_printer
class ASTPrinter:
    '''
    Print an AST and a symbol table to stdout for diagnostics.

    Walks are post-order and static so a caller can inspect a tree without
    registering a pipeline step or a service.
    '''

    # * method: _read (static)
    @staticmethod
    def _read(node: Any, name: str, default: Any = None) -> Any:
        '''
        Read a field from a dumped mapping or a live object.

        :param node: A dict-like scope or symbol, or an object.
        :type node: Any
        :param name: The field name.
        :type name: str
        :param default: The value when the field is absent.
        :type default: Any
        :return: The field value, or the default.
        :rtype: Any
        '''

        # Dumped symbol tables are mappings. Live objects use attributes.
        if isinstance(node, dict):
            return node.get(name, default)

        # Fall back to the attribute when the node was not dumped.
        return getattr(node, name, default)

    # * method: _token (static)
    @staticmethod
    def _token(value: Any) -> Any:
        '''
        Return an enum kind's value, or the value itself.

        :param value: A kind enum or an already-rendered token.
        :type value: Any
        :return: The kind token.
        :rtype: Any
        '''

        # Enum kinds stringify to TypeKind.CLASS on this runtime; print the token.
        return getattr(value, 'value', value)

    # * method: print_ast (static)
    @staticmethod
    def print_ast(decl: Declaration, indent: int = 0) -> None:
        '''
        Print a declaration after its body, value, and type.

        :param decl: The declaration to print.
        :type decl: Declaration
        :param indent: The indent level, two spaces per level.
        :type indent: int
        :return: None
        :rtype: None
        '''

        # Visit body statements before the declaration line.
        for stmt in decl.code:
            ASTPrinter.print_statement(stmt, indent + 1)

        # Visit an initializer when the declaration has one.
        if decl.value:
            ASTPrinter.print_expression(decl.value, indent + 1)

        # Visit the declaration type when it is set.
        if decl.type:
            ASTPrinter.print_type(decl.type, indent + 1)

        # Format the optional type and truncated docstring suffixes.
        prefix = '  ' * indent
        type_str = f' : {ASTPrinter._token(decl.type.kind)}' if decl.type else ''
        doc_str = ''
        if decl.doc_string:
            doc = decl.doc_string
            if len(doc) > 40:
                doc = doc[:40] + '...'
            doc_str = f' doc="{doc}"'

        # Print the declaration after its children.
        print(f'{prefix}[Declaration] name={decl.name}{type_str}{doc_str}')

    # * method: print_statement (static)
    @staticmethod
    def print_statement(stmt: Statement, indent: int = 0) -> None:
        '''
        Print a statement after its bodies, declaration, and expressions.

        :param stmt: The statement to print.
        :type stmt: Statement
        :param indent: The indent level, two spaces per level.
        :type indent: int
        :return: None
        :rtype: None
        '''

        # Visit body children, then else-body children.
        for child in stmt.body:
            ASTPrinter.print_statement(child, indent + 1)
        for child in stmt.else_body:
            ASTPrinter.print_statement(child, indent + 1)

        # Visit a nested declaration when the statement carries one.
        if stmt.decl:
            ASTPrinter.print_ast(stmt.decl, indent + 1)

        # Visit the initializer expression, then the primary expression.
        if stmt.init_expr:
            ASTPrinter.print_expression(stmt.init_expr, indent + 1)
        if stmt.expr:
            ASTPrinter.print_expression(stmt.expr, indent + 1)

        # Print the statement after its children.
        prefix = '  ' * indent
        print(f'{prefix}[Statement] kind={ASTPrinter._token(stmt.kind)}')

    # * method: print_expression (static)
    @staticmethod
    def print_expression(expr: Expression, indent: int = 0) -> None:
        '''
        Print an expression after its left and right children.

        :param expr: The expression to print.
        :type expr: Expression
        :param indent: The indent level, two spaces per level.
        :type indent: int
        :return: None
        :rtype: None
        '''

        # Visit the left child, then the right child.
        if expr.left:
            ASTPrinter.print_expression(expr.left, indent + 1)
        if expr.right:
            ASTPrinter.print_expression(expr.right, indent + 1)

        # Format optional name and value suffixes.
        prefix = '  ' * indent
        name = f' name={expr.name}' if expr.name else ''
        val = f' value={expr.value}' if expr.value else ''

        # Print the expression after its children.
        print(f'{prefix}[Expression] kind={ASTPrinter._token(expr.kind)}{name}{val}')

    # * method: print_type (static)
    @staticmethod
    def print_type(type_node: Type, indent: int = 0) -> None:
        '''
        Print a type after its subtype, return type, and parameters.

        :param type_node: The type to print.
        :type type_node: Type
        :param indent: The indent level, two spaces per level.
        :type indent: int
        :return: None
        :rtype: None
        '''

        # Visit the subtype, then the return type.
        if type_node.subtype:
            ASTPrinter.print_type(type_node.subtype, indent + 1)
        if type_node.return_type:
            ASTPrinter.print_type(type_node.return_type, indent + 1)

        # Visit parameters when the type carries them.
        if type_node.params:
            ASTPrinter.print_param_list(type_node.params, indent + 1)

        # Print the type after its children.
        prefix = '  ' * indent
        name = f' name={type_node.name}' if type_node.name else ''
        print(f'{prefix}[Type] kind={ASTPrinter._token(type_node.kind)}{name}')

    # * method: print_param_list (static)
    @staticmethod
    def print_param_list(params: List[ParamList], indent: int = 0) -> None:
        '''
        Print each parameter after its default and type.

        :param params: The parameters to print.
        :type params: List[ParamList]
        :param indent: The indent level, two spaces per level.
        :type indent: int
        :return: None
        :rtype: None
        '''

        # Visit each parameter's default and type before its own line.
        for param in params:
            if param.default:
                ASTPrinter.print_expression(param.default, indent + 1)
            if param.type:
                ASTPrinter.print_type(param.type, indent + 1)

            # Requiredness is a suffix, not a separate node.
            prefix = '  ' * indent
            req = ' required' if param.required else ' optional'
            print(f'{prefix}[Param] name={param.name}{req}')

    # * method: print_symbol_table (static)
    @staticmethod
    def print_symbol_table(symbol_table: Dict[str, Any]) -> None:
        '''
        Print a dumped or live symbol table to stdout.

        :param symbol_table: The symbol table, including module name and scopes.
        :type symbol_table: Dict[str, Any]
        :return: None
        :rtype: None
        '''

        # Head the dump with the module name, defaulting when it is absent.
        module_name = symbol_table.get('module_name', 'unknown')
        print(f'=== Symbol Table: {module_name} ===')
        print()

        # Print each scope, then a blank line.
        scopes = symbol_table.get('scopes') or {}
        for scope_path, scope_data in scopes.items():
            kind = ASTPrinter._read(scope_data, 'kind')
            parent_path = ASTPrinter._read(scope_data, 'parent_path')
            parent = f' (parent: {parent_path})' if parent_path else ''
            print(f'Scope: {scope_path} [{kind}]{parent}')

            # Print symbols when the scope defines any.
            symbols = ASTPrinter._read(scope_data, 'symbols') or {}
            if symbols:
                print('  Symbols:')
                if isinstance(symbols, dict):
                    symbol_rows = symbols.items()
                else:
                    symbol_rows = (
                        (ASTPrinter._read(symbol, 'name'), symbol)
                        for symbol in symbols
                    )
                for symbol_name, symbol in symbol_rows:
                    symbol_kind = ASTPrinter._read(symbol, 'kind')
                    type_annotation = ASTPrinter._read(symbol, 'type_annotation')
                    source_module = ASTPrinter._read(symbol, 'source_module')
                    extras = ''
                    if type_annotation:
                        extras += f' type={type_annotation}'
                    if source_module:
                        extras += f' from={source_module}'
                    name = symbol_name or ASTPrinter._read(symbol, 'name')
                    print(f'    {name} [{symbol_kind}]{extras}')

            # Print child scope paths when the scope has any.
            children = ASTPrinter._read(scope_data, 'children') or {}
            if children:
                print('  Children:')
                for child_name, child_path in children.items():
                    print(f'    {child_name} -> {child_path}')

            # Separate scopes with a blank line.
            print()
