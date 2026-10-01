"""Token and AST navigation helpers for parser tests."""

# *** imports

# ** core
from typing import Any, List, Optional

# ** app
from ...mappers import Tok

# *** functions

# ** function: tok
def tok(type: str, value: Optional[str] = None, lineno: int = 1, lexpos: int = 0):
    '''
    Build one token aggregate for a synthetic stream.

    :param type: The token type name.
    :type type: str
    :param value: The token text. Defaults to the type name.
    :type value: Optional[str]
    :param lineno: The 1-based source line.
    :type lineno: int
    :param lexpos: The 0-based offset.
    :type lexpos: int
    :return: The constructed token aggregate.
    :rtype: TokenAggregate
    '''

    # A missing value is the type name, not an empty string.
    return Tok.new(
        type=type,
        value=value if value is not None else type,
        lineno=lineno,
        lexpos=lexpos,
    )

# ** function: collect
def collect(node: Any, attr: str = 'next') -> List[Any]:
    '''
    Copy a list, or walk a linked node chain.

    :param node: A list, a linked node, or None.
    :type node: Any
    :param attr: The link attribute. Defaults to ``next``.
    :type attr: str
    :return: The collected nodes.
    :rtype: List[Any]
    '''

    # A list is copied so callers cannot mutate the original by accident.
    if isinstance(node, list):
        return list(node)

    # Walk the link until it is missing.
    items = []
    current = node
    while current is not None:
        items.append(current)
        current = getattr(current, attr, None)
    return items

# ** function: get_group
def get_group(module: Any, idx: int = 0) -> Any:
    '''
    Return one top-level group statement.

    :param module: The parsed module declaration.
    :type module: Any
    :param idx: The group index.
    :type idx: int
    :return: The group statement.
    :rtype: Any
    '''

    # Groups are the module body, in source order.
    return module.code[idx]

# ** function: get_section
def get_section(module: Any, g: int = 0, s: int = 0) -> Any:
    '''
    Return one section statement inside a group.

    :param module: The parsed module declaration.
    :type module: Any
    :param g: The group index.
    :type g: int
    :param s: The section index.
    :type s: int
    :return: The section statement.
    :rtype: Any
    '''

    # Sections are the group body, in source order.
    return get_group(module, g).body[s]

# ** function: get_class_decl
def get_class_decl(module: Any, g: int = 0, s: int = 0) -> Any:
    '''
    Return the class declaration in a section.

    :param module: The parsed module declaration.
    :type module: Any
    :param g: The group index.
    :type g: int
    :param s: The section index.
    :type s: int
    :return: The class declaration.
    :rtype: Any
    '''

    # The section body opens with the class declaration statement.
    return get_section(module, g, s).body[0].decl

# ** function: get_member
def get_member(module: Any, idx: int = 0, g: int = 0, s: int = 0) -> Any:
    '''
    Return one class member declaration.

    :param module: The parsed module declaration.
    :type module: Any
    :param idx: The member index.
    :type idx: int
    :param g: The group index.
    :type g: int
    :param s: The section index.
    :type s: int
    :return: The member declaration.
    :rtype: Any
    '''

    # Members are declaration statements on the class body.
    return get_class_decl(module, g, s).code[idx].decl

# ** function: get_func_decl
def get_func_decl(module: Any, member_idx: int = 0) -> Any:
    '''
    Return the function declaration nested in a class member.

    :param module: The parsed module declaration.
    :type module: Any
    :param member_idx: The member index.
    :type member_idx: int
    :return: The function declaration.
    :rtype: Any
    '''

    # The member body opens with the function declaration statement.
    return get_member(module, member_idx).code[0].decl

# ** function: get_function_decl
def get_function_decl(module: Any, g: int = 0, s: int = 0) -> Any:
    '''
    Return a module-level function declaration.

    :param module: The parsed module declaration.
    :type module: Any
    :param g: The group index.
    :type g: int
    :param s: The section index.
    :type s: int
    :return: The function declaration.
    :rtype: Any
    '''

    # A function section opens with the function declaration statement.
    return get_section(module, g, s).body[0].decl

# ** function: make_method_tokens
def make_method_tokens(
    name: str = 'execute',
    params: Optional[list] = None,
    body: Optional[list] = None,
    ret: Optional[str] = None,
    doc: Optional[str] = None,
    member_kind: str = 'method',
) -> List[Any]:
    '''
    Build tokens from an artifact member header through its dedent.

    ``SELF`` is always the first parameter. A missing body is ``return result``.

    :param name: The method name.
    :type name: str
    :param params: Extra parameter token lists inserted after ``SELF``.
    :type params: Optional[list]
    :param body: Body tokens. Defaults to ``return result``.
    :type body: Optional[list]
    :param ret: Optional return-annotation name.
    :type ret: Optional[str]
    :param doc: Optional docstring text, including quotes.
    :type doc: Optional[str]
    :param member_kind: The member role written on the header.
    :type member_kind: str
    :return: The member token list.
    :rtype: List[Any]
    '''

    # Init headers have no colon name. Other roles do.
    if member_kind == 'init':
        header = '# * init'
    else:
        header = f'# * {member_kind}: {name}'

    # The published lexer uses INIT for __init__, not IDENTIFIER.
    name_type = 'INIT' if name == '__init__' else 'IDENTIFIER'
    tokens = [
        tok('ARTIFACT_MEMBER', header),
        tok('NEWLINE', '\n'),
        tok('DEF', 'def'),
        tok(name_type, name),
        tok('LPAREN', '('),
        tok('SELF', 'self'),
    ]

    # Extra parameters follow the receiver.
    for param in params or []:
        tokens.append(tok('COMMA', ','))
        tokens.extend(param)

    # Close the parameter list, then the optional return annotation.
    tokens.append(tok('RPAREN', ')'))
    if ret is not None:
        tokens.extend([
            tok('ARROW', '->'),
            tok('IDENTIFIER', ret),
        ])

    # The body is indented. A missing body returns result.
    tokens.extend([
        tok('COLON', ':'),
        tok('NEWLINE', '\n'),
        tok('INDENT', ''),
    ])
    if doc is not None:
        tokens.extend([
            tok('DOCSTRING', doc),
            tok('NEWLINE', '\n'),
        ])
    if body is None:
        tokens.extend([
            tok('RETURN', 'return'),
            tok('IDENTIFIER', 'result'),
            tok('NEWLINE', '\n'),
        ])
    else:
        tokens.extend(body)
    tokens.append(tok('DEDENT', ''))
    return tokens

# ** function: make_function_tokens
def make_function_tokens(
    name: str = 'helper',
    params: Optional[list] = None,
    body: Optional[list] = None,
    ret: Optional[str] = None,
    doc: Optional[str] = None,
) -> List[Any]:
    '''
    Build a section-level function with no ``SELF`` parameter.

    A missing body is ``return value``.

    :param name: The function name.
    :type name: str
    :param params: Parameter token lists.
    :type params: Optional[list]
    :param body: Body tokens. Defaults to ``return value``.
    :type body: Optional[list]
    :param ret: Optional return-annotation name.
    :type ret: Optional[str]
    :param doc: Optional docstring text, including quotes.
    :type doc: Optional[str]
    :return: The function token list.
    :rtype: List[Any]
    '''

    # A module-level function has no receiver.
    tokens = [
        tok('DEF', 'def'),
        tok('IDENTIFIER', name),
        tok('LPAREN', '('),
    ]
    for index, param in enumerate(params or []):
        if index:
            tokens.append(tok('COMMA', ','))
        tokens.extend(param)
    tokens.append(tok('RPAREN', ')'))
    if ret is not None:
        tokens.extend([
            tok('ARROW', '->'),
            tok('IDENTIFIER', ret),
        ])

    # The body is indented. A missing body returns value.
    tokens.extend([
        tok('COLON', ':'),
        tok('NEWLINE', '\n'),
        tok('INDENT', ''),
    ])
    if doc is not None:
        tokens.extend([
            tok('DOCSTRING', doc),
            tok('NEWLINE', '\n'),
        ])
    if body is None:
        tokens.extend([
            tok('RETURN', 'return'),
            tok('IDENTIFIER', 'value'),
            tok('NEWLINE', '\n'),
        ])
    else:
        tokens.extend(body)
    tokens.append(tok('DEDENT', ''))
    return tokens

# ** function: make_event_module
def make_event_module(
    member_tokens: List[Any],
    cls_name: str = 'Sample',
    base: str = 'DomainEvent',
    cls_doc: Optional[str] = None,
) -> List[Any]:
    '''
    Wrap member tokens in an events group, a sample section, and a class.

    :param member_tokens: Tokens placed inside the class body.
    :type member_tokens: List[Any]
    :param cls_name: The class name.
    :type cls_name: str
    :param base: The single base-class name.
    :type base: str
    :param cls_doc: Optional class docstring, including quotes.
    :type cls_doc: Optional[str]
    :return: The module token list.
    :rtype: List[Any]
    '''

    # The section name follows the class name in the default sample shape.
    tokens = [
        tok('ARTIFACT_START', '# *** events'),
        tok('NEWLINE', '\n'),
        tok('ARTIFACT_SECTION', f'# ** event: {cls_name.lower()}'),
        tok('NEWLINE', '\n'),
        tok('CLASS', 'class'),
        tok('IDENTIFIER', cls_name),
        tok('LPAREN', '('),
        tok('IDENTIFIER', base),
        tok('RPAREN', ')'),
        tok('COLON', ':'),
        tok('NEWLINE', '\n'),
        tok('INDENT', ''),
    ]
    if cls_doc is not None:
        tokens.extend([
            tok('DOCSTRING', cls_doc),
            tok('NEWLINE', '\n'),
        ])
    tokens.extend(member_tokens)
    tokens.append(tok('DEDENT', ''))
    return tokens

# ** function: make_functions_module
def make_functions_module(function_sections: List[List[Any]]) -> List[Any]:
    '''
    Build a functions group around the given section token lists.

    :param function_sections: Section token lists, including their headers.
    :type function_sections: List[List[Any]]
    :return: The module token list.
    :rtype: List[Any]
    '''

    # The group header is the only token this helper adds.
    tokens = [
        tok('ARTIFACT_START', '# *** functions'),
        tok('NEWLINE', '\n'),
    ]
    for section in function_sections:
        tokens.extend(section)
    return tokens
