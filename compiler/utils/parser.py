"""Scanner Parser Utility - PlyParser (tiferet-ly adapter)"""

# *** imports

# ** core
import re
from typing import Any, Callable, List, Optional, Tuple

# ** infra
from tiferet_ly.utils.parse import PlyParser as LyPlyParser

# ** app
from ..mappers import Type
from ..mappers.ast import ExprKind, TypeKind

# *** constants

# ** constant: grammar_id
GRAMMAR_ID = 'tiferet_dialect'

# *** functions

# ** function: parse_artifact_header
def parse_artifact_header(token_value: str) -> tuple:
    '''
    Split an artifact header into its name, qualifier, and type marker.

    :param token_value: The raw header token, including its leading hash.
    :type token_value: str
    :return: ``(name, qualifier, type)``.
    :rtype: tuple
    '''

    # Drop the leading hash and surrounding whitespace before the marker.
    text = token_value.strip().lstrip('#').strip()

    # A bare marker has no declared name.
    parts = text.split(None, 1)
    if len(parts) < 2:
        head = parts[0] if parts else ''
        return (head or 'unknown', None, '')

    marker, rest = parts

    # A trailing parenthetical is the qualifier, not part of the name.
    qualifier = None
    match = re.search(r'\(([^()]*)\)\s*$', rest)
    if match:
        inside = match.group(1).strip()
        qualifier = inside or None
        rest = rest[:match.start()].rstrip()

    # A colon separates the type keyword from the declared name.
    if ':' in rest:
        kind, _, name = rest.partition(':')
        return (name.strip(), qualifier, f'{marker} {kind.strip()}')

    # Otherwise the remainder is the name and the marker is the type.
    return (rest.strip(), qualifier, marker)

# ** function: parse_see_guide_path
def parse_see_guide_path(token_value: str) -> Optional[str]:
    '''
    Extract a ``see:`` guide path from an annotation token.

    Accepts both ``@guides/...`` and ``docs/guides/...``.

    :param token_value: The raw annotation text.
    :type token_value: str
    :return: The stripped guide path, or None when it is missing or empty.
    :rtype: Optional[str]
    '''

    # Search for a see: path anchored at the end of the token.
    match = re.search(r'see:\s*(.+?)\s*$', token_value, re.IGNORECASE)
    if not match:
        return None

    # Drop a whitespace-only capture.
    path = match.group(1).strip()
    return path or None

# ** function: parse_member_kind
def parse_member_kind(artifact_member_value: str) -> str:
    '''
    Read the member role from an artifact member token.

    :param artifact_member_value: The raw member token, such as ``# * method: execute``.
    :type artifact_member_value: str
    :return: The role word, or ``unknown`` when the token is empty.
    :rtype: str
    '''

    # Drop the member prefix, then the surrounding whitespace.
    text = artifact_member_value
    if text.startswith('# * '):
        text = text[len('# * '):]
    text = text.strip()
    if not text:
        return 'unknown'

    # The role is the first word before a colon, or the first word.
    head = text.split(':', 1)[0].strip()
    if not head:
        return 'unknown'
    return head.split(None, 1)[0]

# ** function: parse_member_qualifier
def parse_member_qualifier(artifact_member_value: str) -> Optional[str]:
    '''
    Read a trailing parenthetical qualifier from a member token.

    :param artifact_member_value: The raw member token.
    :type artifact_member_value: str
    :return: The stripped qualifier, or None when it is absent or empty.
    :rtype: Optional[str]
    '''

    # Match a parenthetical only when it ends the token.
    match = re.search(r'\(([^()]*)\)\s*$', artifact_member_value)
    if not match:
        return None

    # An empty pair is the same as no qualifier.
    inside = match.group(1).strip()
    return inside or None

# ** function: get_attribute_type
def get_attribute_type(type_str: str, additional_types: Optional[Type] = None) -> Type:
    '''
    Build a type aggregate from an attribute annotation string.

    :param type_str: The annotation text, such as ``int`` or a class name.
    :type type_str: str
    :param additional_types: The optional subclass chain for a class type.
    :type additional_types: Optional[Type]
    :return: The constructed type aggregate.
    :rtype: Type
    '''

    # None is the null type, not a class named None.
    if type_str == 'None':
        return Type.new_null_type()

    # Map the six primitive names onto their kinds.
    primitive_kinds = {
        'int': TypeKind.INT,
        'str': TypeKind.STR,
        'float': TypeKind.FLOAT,
        'bool': TypeKind.BOOL,
        'list': TypeKind.LIST,
        'dict': TypeKind.DICT,
    }
    if type_str in primitive_kinds:
        return Type.new(kind=primitive_kinds[type_str])

    # Any other name is a class, with the optional subclass chain.
    return Type.new_class_type(
        name=type_str,
        subclasses=additional_types,
    )

# ** function: flatten_args_list
def flatten_args_list(node: Optional[Any]) -> List[Any]:
    '''
    Flatten a right-recursive argument list into call arguments.

    Private to ``render_lambda_body``. Not a rewrite-table key.

    :param node: An argument node, an ``ARGS_LIST`` spine, or None.
    :type node: Optional[Any]
    :return: The leaf arguments in left-to-right order.
    :rtype: List[Any]
    '''

    # A missing spine contributes no arguments.
    if node is None:
        return []

    # An argument list is the concatenation of its two sides.
    if node.kind == ExprKind.ARGS_LIST:
        return flatten_args_list(node.left) + flatten_args_list(node.right)

    # Any other node is one argument.
    return [node]

# ** function: render_lambda_body
def render_lambda_body(expr: Optional[Any]) -> str:
    '''
    Render opaque source-like text for a lambda body expression.

    Covers bare and dotted names and chained calls over literals. It is
    not a general expression printer.

    :param expr: The expression to render, or None.
    :type expr: Optional[Any]
    :return: Source-like text, or an empty string when the expression is missing.
    :rtype: str
    '''

    # A missing expression renders as empty text.
    if expr is None:
        return ''

    # A bare name is its identifier.
    if expr.kind == ExprKind.NAME:
        return expr.name or ''

    # Literal values are their stored text.
    if expr.kind in (
        ExprKind.STR_VAL,
        ExprKind.NUM_VAL,
        ExprKind.INT_VAL,
        ExprKind.BOOL_VAL,
    ):
        return expr.value or ''

    # None is the literal word, not an empty value.
    if expr.kind == ExprKind.NONE_VAL:
        return 'None'

    # An attribute is the receiver, a dot, and the name.
    if expr.kind == ExprKind.ATTRIBUTE:
        return f'{render_lambda_body(expr.left)}.{expr.name}'

    # A call is the callee and its flattened arguments.
    if expr.kind == ExprKind.CALL:
        rendered_args = ', '.join(
            render_lambda_body(arg) for arg in flatten_args_list(expr.right)
        )
        return f'{render_lambda_body(expr.left)}({rendered_args})'

    # Non-empty containers stay opaque.
    if expr.kind == ExprKind.DICT_LITERAL:
        return '{}' if expr.left is None else '{...}'

    if expr.kind == ExprKind.LIST_LITERAL:
        return '[]' if expr.left is None else '[...]'

    # Anything else uses a name or a stored value when one is present.
    return expr.name or expr.value or ''

# ** function: make_position_helpers
def make_position_helpers(
    source_text: str,
) -> Tuple[Callable, Callable, Callable, Callable, Callable, Callable]:
    '''
    Build position closures scoped to one source text.

    :param source_text: The source being parsed.
    :type source_text: str
    :return: ``(pos, find_column, set_last_op_pos, get_last_op_pos, set_last_ident_pos, get_last_ident_pos)``.
    :rtype: Tuple[Callable, Callable, Callable, Callable, Callable, Callable]
    '''

    # Cells default to column zero on line zero and stay private to this parse.
    last_op_pos = [(0, 0)]
    last_ident_pos = [(0, 0)]

    # Column is the offset after the nearest preceding newline.
    def find_column(lexpos: int) -> int:
        '''
        Convert a lexer offset to a 0-based column.

        :param lexpos: The absolute lexer offset.
        :type lexpos: int
        :return: The 0-based column, or the offset when the line has no newline.
        :rtype: int
        '''

        # The start of the text is column zero.
        if lexpos == 0:
            return 0

        # Column is the distance after the nearest preceding newline.
        newline_at = source_text.rfind('\n', 0, lexpos)
        if newline_at < 0:
            return lexpos
        return lexpos - newline_at - 1

    # Pair a grammar symbol's line with its column in this source.
    def pos(p: Any, n: int) -> tuple:
        '''
        Read the line and column of grammar symbol ``n``.

        :param p: The parser slice.
        :type p: Any
        :param n: The symbol index.
        :type n: int
        :return: ``(lineno, column)``.
        :rtype: tuple
        '''

        # Pair the symbol line with its column in this source.
        return (p.lineno(n), find_column(p.lexpos(n)))

    # Remember the last operator position for this parse.
    def set_last_op_pos(value: tuple) -> None:
        '''
        Remember the last operator position for this parse.

        :param value: The ``(lineno, column)`` pair.
        :type value: tuple
        '''

        # Replace the cell; do not share it across parses.
        last_op_pos[0] = value

    # Return the last operator position for this parse.
    def get_last_op_pos() -> tuple:
        '''
        Return the last operator position for this parse.

        :return: The stored ``(lineno, column)`` pair.
        :rtype: tuple
        '''

        # Read the cell closed over by this parse.
        return last_op_pos[0]

    # Remember the last identifier position for this parse.
    def set_last_ident_pos(value: tuple) -> None:
        '''
        Remember the last identifier position for this parse.

        :param value: The ``(lineno, column)`` pair.
        :type value: tuple
        '''

        # Replace the cell; do not share it across parses.
        last_ident_pos[0] = value

    # Return the last identifier position for this parse.
    def get_last_ident_pos() -> tuple:
        '''
        Return the last identifier position for this parse.

        :return: The stored ``(lineno, column)`` pair.
        :rtype: tuple
        '''

        # Read the cell closed over by this parse.
        return last_ident_pos[0]

    # Return the six closures in rewrite-table order.
    return (
        pos,
        find_column,
        set_last_op_pos,
        get_last_op_pos,
        set_last_ident_pos,
        get_last_ident_pos,
    )

# *** utils

# ** util: ply_parser
class PlyParser(LyPlyParser):
    '''
    Extend the published tiferet-ly parser with dialect node mutations.

    Header, type, and expression helpers stay functions because they do not
    mutate their inputs. Annotation and dangling-else updates live here.
    '''

    # * method: apply_annotations (static)
    @staticmethod
    def apply_annotations(decl: Any, annots: Optional[list]) -> None:
        '''
        Store annotations and promote the first SEE note to ``guide_path``.

        :param decl: The declaration to mutate.
        :type decl: Any
        :param annots: Structured SEE, OBSOLETE, or TODO notes, or None.
        :type annots: Optional[list]
        '''

        # Store the list as given, including when it is missing.
        decl.annotations = annots

        # The first SEE wins. Leave guide_path unset when that note has no path.
        for annot in annots or []:
            if not isinstance(annot, dict) or annot.get('kind') != 'SEE':
                continue

            path = parse_see_guide_path(annot.get('text', ''))
            if path:
                decl.guide_path = path
            break

    # * method: attach_dangling_else (static)
    @staticmethod
    def attach_dangling_else(stmts: List[Any], else_body: List[Any]) -> None:
        '''
        Attach an else body to the innermost open if in a statement list.

        :param stmts: The statement list whose last node may be an if.
        :type stmts: List[Any]
        :param else_body: The else statements to attach.
        :type else_body: List[Any]
        '''

        # An empty list has nowhere to attach.
        if not stmts:
            return

        # Walk a chain of if nodes that each hold one nested if.
        target = stmts[-1]
        while (
            target.is_if_else
            and len(target.else_body) == 1
            and target.else_body[0].is_if_else
        ):
            target = target.else_body[0]

        # Attach only when the landed node is itself an if.
        if target.is_if_else:
            target.else_body = else_body
