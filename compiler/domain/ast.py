"""Tiferet Compiler AST Domain Objects"""

# *** imports

# ** core
from enum import Enum
from typing import Any, ClassVar, Dict, FrozenSet, List, Optional

# ** infra
from pydantic import Field, model_validator

# ** app
from tiferet.domain.core import DomainObject

# *** enums

# ** enum: type_kind
class TypeKind(str, Enum):
    '''
    Enumeration of valid type kinds in the Tiferet AST.
    '''

    # * attribute: unknown
    UNKNOWN = 'unknown'

    # * attribute: none
    NONE = 'None'

    # * attribute: bool
    BOOL = 'bool'

    # * attribute: str
    STR = 'str'

    # * attribute: int
    INT = 'int'

    # * attribute: float
    FLOAT = 'float'

    # * attribute: list
    LIST = 'list'

    # * attribute: dict
    DICT = 'dict'

    # * attribute: class
    CLASS = 'class'

    # * attribute: func
    FUNC = 'func'

    # * attribute: artifact
    ARTIFACT = 'artifact'

    # * attribute: module
    MODULE = 'module'

# ** enum: statement_kind
class StatementKind(str, Enum):
    '''
    Enumeration of valid statement kinds in the Tiferet AST.
    '''

    # * attribute: decl
    DECL = 'decl'

    # * attribute: expr
    EXPR = 'expr'

    # * attribute: if_else
    IF_ELSE = 'if_else'

    # * attribute: for
    FOR = 'for'

    # * attribute: while
    WHILE = 'while'

    # * attribute: print
    PRINT = 'print'

    # * attribute: return
    RETURN = 'return'

    # * attribute: block
    BLOCK = 'block'

    # * attribute: import
    IMPORT = 'import'

    # * attribute: import_from
    IMPORT_FROM = 'import_from'

    # * attribute: artifact
    ARTIFACT = 'artifact'

    # * attribute: comment
    COMMENT = 'comment'

    # * attribute: snippet
    SNIPPET = 'snippet'

    # * attribute: try_except
    TRY_EXCEPT = 'try_except'

    # * attribute: with
    WITH = 'with'

    # * attribute: raise
    RAISE = 'raise'

    # * attribute: assert
    ASSERT = 'assert'

    # * attribute: pass
    PASS = 'pass'

    # * attribute: continue
    CONTINUE = 'continue'

    # * attribute: break
    BREAK = 'break'

    # * attribute: del
    DEL = 'del'

# ** enum: expr_kind
class ExprKind(str, Enum):
    '''
    Enumeration of valid expression kinds in the Tiferet AST.
    '''

    # * attribute: add
    ADD = 'add'

    # * attribute: sub
    SUB = 'sub'

    # * attribute: mul
    MUL = 'mul'

    # * attribute: div
    DIV = 'div'

    # * attribute: mod
    MOD = 'mod'

    # * attribute: exp
    EXP = 'exp'

    # * attribute: floordiv
    FLOORDIV = 'floordiv'

    # * attribute: eq
    EQ = 'eq'

    # * attribute: neq
    NEQ = 'neq'

    # * attribute: lt
    LT = 'lt'

    # * attribute: lte
    LTE = 'lte'

    # * attribute: gt
    GT = 'gt'

    # * attribute: gte
    GTE = 'gte'

    # * attribute: name
    NAME = 'name'

    # * attribute: num_val
    NUM_VAL = 'num_val'

    # * attribute: int_val
    INT_VAL = 'int_val'

    # * attribute: str_val
    STR_VAL = 'str_val'

    # * attribute: bool_val
    BOOL_VAL = 'bool_val'

    # * attribute: none_val
    NONE_VAL = 'none_val'

    # * attribute: ellipsis_val
    ELLIPSIS_VAL = 'ellipsis_val'

    # * attribute: assign
    ASSIGN = 'assign'

    # * attribute: args_list
    ARGS_LIST = 'args_list'

    # * attribute: call
    CALL = 'call'

    # * attribute: attribute
    ATTRIBUTE = 'attribute'

    # * attribute: import
    IMPORT = 'import'

    # * attribute: import_as
    IMPORT_AS = 'import_as'

    # * attribute: import_multi
    IMPORT_MULTI = 'import_multi'

    # * attribute: artifact
    ARTIFACT = 'artifact'

    # * attribute: comment
    COMMENT = 'comment'

    # * attribute: not
    NOT = 'not'

    # * attribute: and
    AND = 'and'

    # * attribute: or
    OR = 'or'

    # * attribute: is
    IS = 'is'

    # * attribute: is_not
    IS_NOT = 'is_not'

    # * attribute: in
    IN = 'in'

    # * attribute: not_in
    NOT_IN = 'not_in'

    # * attribute: unary_minus
    UNARY_MINUS = 'unary_minus'

    # * attribute: list_literal
    LIST_LITERAL = 'list_literal'

    # * attribute: dict_literal
    DICT_LITERAL = 'dict_literal'

    # * attribute: set_literal
    SET_LITERAL = 'set_literal'

    # * attribute: tuple
    TUPLE = 'tuple'

    # * attribute: subscript
    SUBSCRIPT = 'subscript'

    # * attribute: slice
    SLICE = 'slice'

    # * attribute: ternary
    TERNARY = 'ternary'

    # * attribute: comprehension
    COMPREHENSION = 'comprehension'

    # * attribute: for_comp
    FOR_COMP = 'for_comp'

    # * attribute: fstring
    FSTRING = 'fstring'

    # * attribute: await
    AWAIT = 'await'

    # * attribute: kwarg
    KWARG = 'kwarg'

    # * attribute: star_expr
    STAR_EXPR = 'star_expr'

    # * attribute: double_star_expr
    DOUBLE_STAR_EXPR = 'double_star_expr'

    # * attribute: dict_entry
    DICT_ENTRY = 'dict_entry'

# *** functions

# ** function: encode_block
def encode_block(stmts: Optional[List['Statement']] = None) -> str:
    '''
    Encode a statement list, dropping empty encodings.

    :param stmts: The statements to encode.
    :type stmts: Optional[List['Statement']]
    :return: A bracketed, comma-separated encoding.
    :rtype: str
    '''

    # Keep only statements whose own encoding is non-empty.
    parts = []
    for current in stmts or []:
        encoded = current.encode()
        if encoded:
            parts.append(encoded)

    # Return the bracketed block.
    return '[' + ', '.join(parts) + ']'

# ** function: encode_handlers
def encode_handlers(handlers: Optional[List['Statement']] = None) -> str:
    '''
    Encode except handlers, with or without an exception type.

    :param handlers: The handler statements.
    :type handlers: Optional[List['Statement']]
    :return: A bracketed, comma-separated handler encoding.
    :rtype: str
    '''

    # Format each handler from its exception expression and body.
    parts = []
    for handler in handlers or []:
        exc = handler.expr.encode() if handler.expr else ''
        body = encode_block(handler.body)
        if exc:
            parts.append(f'Except({exc}, {body})')
        else:
            parts.append(f'Except({body})')

    # Return the bracketed handler list.
    return '[' + ', '.join(parts) + ']'

# *** models

# ** model: param_list
class ParamList(DomainObject):
    '''
    A parameter in a method or function type.

    Carries the name, type, and requiredness a callable type needs before
    expression nodes exist to hold a default value.
    '''

    # * attribute: name
    name: str = Field(
        ...,
        description='Parameter name.',
    )

    # * attribute: type
    type: Optional['Type'] = Field(
        None,
        description='Parameter type.',
    )

    # * attribute: required
    required: bool = Field(
        False,
        description='Whether the parameter is required.',
    )

    # * attribute: default
    default: Optional['Expression'] = Field(
        None,
        description='Default value expression when the parameter is optional.',
    )

# ** model: type
class Type(DomainObject):
    '''
    A type in the Tiferet AST (declaration type, method return type, or constant type).

    One type object covers primitives, classes, and functions so later AST
    nodes share a single classification instead of a parallel type checker.
    '''

    # * attribute: kind
    kind: TypeKind = Field(
        ...,
        description='Type kind.',
    )

    # * attribute: name
    name: Optional[str] = Field(
        None,
        description='Explicit name (class types).',
    )

    # * attribute: subtype
    subtype: Optional['Type'] = Field(
        None,
        description='Element / nested type (lists, base-class chain).',
    )

    # * attribute: return_type
    return_type: Optional['Type'] = Field(
        None,
        description='Function return type.',
    )

    # * attribute: params
    params: List[ParamList] = Field(
        default_factory=list,
        description='Function parameters.',
    )

    # * attribute: is_class
    is_class: bool = Field(
        False,
        description='Derived: kind == TypeKind.CLASS.',
    )

    # * attribute: is_func
    is_func: bool = Field(
        False,
        description='Derived: kind == TypeKind.FUNC.',
    )

    # * attribute: is_primitive
    is_primitive: bool = Field(
        False,
        description='Derived: kind in _PRIMITIVE_KINDS.',
    )

    # * attribute: is_valid_return_type
    is_valid_return_type: bool = Field(
        False,
        description='Derived: kind in _VALID_RETURN_KINDS.',
    )

    # * attribute: _VALID_RETURN_KINDS
    _VALID_RETURN_KINDS: ClassVar[FrozenSet[TypeKind]] = frozenset({
        TypeKind.UNKNOWN,
        TypeKind.NONE,
        TypeKind.BOOL,
        TypeKind.STR,
        TypeKind.INT,
        TypeKind.FLOAT,
        TypeKind.LIST,
        TypeKind.DICT,
        TypeKind.CLASS,
    })

    # * attribute: _PRIMITIVE_KINDS
    _PRIMITIVE_KINDS: ClassVar[FrozenSet[TypeKind]] = frozenset({
        TypeKind.STR,
        TypeKind.INT,
        TypeKind.FLOAT,
        TypeKind.BOOL,
        TypeKind.LIST,
        TypeKind.DICT,
        TypeKind.UNKNOWN,
        TypeKind.NONE,
    })

    # * method: _derive_classification (model validator)
    @model_validator(mode='before')
    @classmethod
    def _derive_classification(cls, data: Any) -> Any:
        '''
        Derive classification flags from the raw type kind.

        :param data: The raw input being validated.
        :type data: Any
        :return: The input, with classification flags set when it is a mapping.
        :rtype: Any
        '''

        # Leave non-mapping input for Pydantic to handle.
        if not isinstance(data, dict):
            return data

        # Copy before deriving classification flags.
        data = dict(data)

        # Resolve a known kind; leave an invalid value for field validation.
        raw_kind = data.get('kind')
        kind = None
        if raw_kind is not None:
            try:
                kind = TypeKind(raw_kind)
            except ValueError:
                kind = None

        # Set the four derived flags from the resolved kind.
        data['is_class'] = kind == TypeKind.CLASS
        data['is_func'] = kind == TypeKind.FUNC
        data['is_primitive'] = kind in cls._PRIMITIVE_KINDS
        data['is_valid_return_type'] = kind in cls._VALID_RETURN_KINDS

        # Return the canonicalized raw input.
        return data

    # * method: _rederive_classification (model validator)
    @model_validator(mode='after')
    def _rederive_classification(self) -> 'Type':
        '''
        Rederive classification flags after validation, including assignment.

        ``mode='before'`` does not run when a field is assigned, so this
        validator keeps the four flags aligned with ``kind``.

        :return: The type with classification flags aligned to its kind.
        :rtype: Type
        '''

        # Rederive the four flags without re-entering assignment validation.
        object.__setattr__(self, 'is_class', self.kind == TypeKind.CLASS)
        object.__setattr__(self, 'is_func', self.kind == TypeKind.FUNC)
        object.__setattr__(self, 'is_primitive', self.kind in self._PRIMITIVE_KINDS)
        object.__setattr__(
            self,
            'is_valid_return_type',
            self.kind in self._VALID_RETURN_KINDS,
        )

        # Return the classified type.
        return self

    # * method: type_name (property)
    @property
    def type_name(self) -> str:
        '''
        Describe this type by its class name or enum value.

        :return: The explicit class name, ``unknown`` when a class name is unset, or the kind value.
        :rtype: str
        '''

        # Return the explicit class name, or unknown when it is unset.
        if self.kind == TypeKind.CLASS:
            return self.name if self.name is not None else 'unknown'

        # Return the enum value for every other kind.
        return self.kind.value

# ** model: expression
class Expression(DomainObject):
    '''
    An expression node (value, name, operation, or call).

    Walkers query this tree in place, so later aggregates inherit the same
    structural surface instead of rebuilding it.
    '''

    # * attribute: kind
    kind: ExprKind = Field(
        ...,
        description='Expression kind.',
    )

    # * attribute: value
    value: Optional[str] = Field(
        None,
        description='Literal or comment text.',
    )

    # * attribute: name
    name: Optional[str] = Field(
        None,
        description='Name for NAME / CALL / ATTRIBUTE / KWARG.',
    )

    # * attribute: left
    left: Optional['Expression'] = Field(
        None,
        description='Left operand / callee / receiver.',
    )

    # * attribute: right
    right: Optional['Expression'] = Field(
        None,
        description='Right operand / args.',
    )

    # * attribute: lineno
    lineno: Optional[int] = Field(
        None,
        description='Source line.',
    )

    # * attribute: col
    col: Optional[int] = Field(
        None,
        description='0-based column.',
    )

    # * attribute: is_binary_op
    is_binary_op: bool = Field(
        False,
        description='Derived: kind in _BINARY_OPS.',
    )

    # * attribute: is_assignment
    is_assignment: bool = Field(
        False,
        description='Derived: kind == ASSIGN.',
    )

    # * attribute: is_name_ref
    is_name_ref: bool = Field(
        False,
        description='Derived: kind == NAME.',
    )

    # * attribute: is_self_attribute
    is_self_attribute: bool = Field(
        False,
        description='Derived: name-ref whose name starts with self.',
    )

    # * attribute: is_literal
    is_literal: bool = Field(
        False,
        description='Derived: kind in _LITERAL_KINDS.',
    )

    # * attribute: literal_type
    literal_type: Optional[str] = Field(
        None,
        description='Derived inferred type string, or None.',
    )

    # * attribute: _BINARY_OPS
    _BINARY_OPS: ClassVar[FrozenSet[ExprKind]] = frozenset({
        ExprKind.ADD,
        ExprKind.SUB,
        ExprKind.MUL,
        ExprKind.DIV,
        ExprKind.MOD,
        ExprKind.EXP,
    })

    # * attribute: _LITERAL_KINDS
    _LITERAL_KINDS: ClassVar[FrozenSet[ExprKind]] = frozenset({
        ExprKind.INT_VAL,
        ExprKind.NUM_VAL,
        ExprKind.STR_VAL,
        ExprKind.BOOL_VAL,
        ExprKind.NONE_VAL,
        ExprKind.ELLIPSIS_VAL,
    })

    # * method: _derive_classification (model validator)
    @model_validator(mode='before')
    @classmethod
    def _derive_classification(cls, data: Any) -> Any:
        '''
        Derive classification flags from the raw expression kind and name.

        :param data: The raw input being validated.
        :type data: Any
        :return: The input, with classification flags set when it is a mapping.
        :rtype: Any
        '''

        # Leave non-mapping input for Pydantic to handle.
        if not isinstance(data, dict):
            return data

        # Copy before deriving classification flags.
        data = dict(data)
        flags = cls._classification_flags(data.get('kind'), data.get('name'))
        data.update(flags)

        # Return the canonicalized raw input.
        return data

    # * method: _rederive_classification (model validator)
    @model_validator(mode='after')
    def _rederive_classification(self) -> 'Expression':
        '''
        Rederive classification flags after validation, including assignment.

        ``mode='before'`` does not run when a field is assigned, so this
        validator keeps the flags aligned with ``kind`` and ``name``.

        :return: The expression with classification flags aligned to its kind.
        :rtype: Expression
        '''

        # Rederive the flags without re-entering assignment validation.
        flags = self._classification_flags(self.kind, self.name)
        for name, value in flags.items():
            object.__setattr__(self, name, value)

        # Return the classified expression.
        return self

    # * method: _classification_flags (static)
    @staticmethod
    def _classification_flags(kind: Any, name: Any) -> Dict[str, Any]:
        '''
        Build the derived classification flags for a kind and name.

        :param kind: The raw or validated expression kind.
        :type kind: Any
        :param name: The raw or validated name.
        :type name: Any
        :return: The derived flag mapping.
        :rtype: Dict[str, Any]
        '''

        # Resolve a known kind so set membership matches enum members.
        resolved = kind
        if kind is not None and not isinstance(kind, ExprKind):
            try:
                resolved = ExprKind(kind)
            except ValueError:
                resolved = kind

        # A self attribute is a name reference whose name starts with self.
        is_name_ref = resolved == ExprKind.NAME
        is_self_attribute = bool(
            is_name_ref and name and str(name).startswith('self.')
        )

        # Return the six derived flags.
        return {
            'is_binary_op': resolved in Expression._BINARY_OPS,
            'is_assignment': resolved == ExprKind.ASSIGN,
            'is_name_ref': is_name_ref,
            'is_self_attribute': is_self_attribute,
            'is_literal': resolved in Expression._LITERAL_KINDS,
            'literal_type': {
                ExprKind.INT_VAL: 'int',
                ExprKind.NUM_VAL: 'float',
                ExprKind.STR_VAL: 'str',
                ExprKind.BOOL_VAL: 'bool',
            }.get(resolved),
        }

    # * method: children (property)
    @property
    def children(self) -> List['Expression']:
        '''
        List the child expressions in walk order.

        :return: The left child, then the right child, omitting either when absent.
        :rtype: List[Expression]
        '''

        # Append left, then right, when each is present.
        nodes = []
        if self.left is not None:
            nodes.append(self.left)
        if self.right is not None:
            nodes.append(self.right)

        # Return the child expressions.
        return nodes

    # * method: visit_role (property)
    @property
    def visit_role(self) -> str:
        '''
        Describe this node by its expression-kind value.

        :return: The kind value, or an empty string when kind is unset.
        :rtype: str
        '''

        # Return the kind value.
        return self.kind.value if self.kind else ''

    # * method: flatten_call_args
    def flatten_call_args(self) -> List['Expression']:
        '''
        Flatten a nested argument list into leaf expressions.

        :return: Leaf expressions in left-to-right order, or this expression when it is not an argument list.
        :rtype: List[Expression]
        '''

        # Concatenate both sides of an argument list.
        if self.kind == ExprKind.ARGS_LIST:
            left_args = self.left.flatten_call_args() if self.left is not None else []
            right_args = self.right.flatten_call_args() if self.right is not None else []
            return left_args + right_args

        # A non-list expression is its own leaf.
        return [self]

    # * method: encode
    def encode(self) -> str:
        '''
        Encode this expression as a structural query string.

        :return: The encoded expression, or an empty string when the kind has no encoding.
        :rtype: str
        '''

        # Encode children once; a missing child contributes an empty string.
        left = self.left.encode() if self.left is not None else ''
        right = self.right.encode() if self.right is not None else ''

        # The name-star form encodes as Exp, not as a bare name.
        if self.kind == ExprKind.NAME and self.value == '**' and self.left is not None:
            return f'Exp({left}, {right})'

        # A name reports its name, then its value.
        if self.kind == ExprKind.NAME:
            return self.name or self.value or ''

        # An attribute reports the receiver and the attribute name.
        if self.kind == ExprKind.ATTRIBUTE:
            return f'Attr({left}, {self.name})'

        # A literal reports its text.
        if self.is_literal:
            return self.value or ''

        # Binary and comparison forms share one encoding shape.
        binary_forms = {
            ExprKind.ASSIGN: 'Assign',
            ExprKind.ADD: 'Add',
            ExprKind.SUB: 'Sub',
            ExprKind.MUL: 'Mul',
            ExprKind.DIV: 'Div',
            ExprKind.MOD: 'Mod',
            ExprKind.EXP: 'Exp',
            ExprKind.FLOORDIV: 'FloorDiv',
            ExprKind.EQ: 'Eq',
            ExprKind.NEQ: 'Neq',
            ExprKind.LT: 'Lt',
            ExprKind.LTE: 'Lte',
            ExprKind.GT: 'Gt',
            ExprKind.GTE: 'Gte',
            ExprKind.AND: 'And',
            ExprKind.OR: 'Or',
            ExprKind.IS: 'Is',
            ExprKind.IS_NOT: 'IsNot',
            ExprKind.IN: 'In',
            ExprKind.NOT_IN: 'NotIn',
            ExprKind.SUBSCRIPT: 'Subscript',
            ExprKind.TERNARY: 'Ternary',
            ExprKind.COMPREHENSION: 'Comp',
        }
        if self.kind in binary_forms:
            return f'{binary_forms[self.kind]}({left}, {right})'

        # Unary forms report only the left child.
        unary_forms = {
            ExprKind.NOT: 'Not',
            ExprKind.UNARY_MINUS: 'Neg',
            ExprKind.LIST_LITERAL: 'List',
            ExprKind.DICT_LITERAL: 'Dict',
            ExprKind.SET_LITERAL: 'Set',
            ExprKind.TUPLE: 'Tuple',
            ExprKind.AWAIT: 'Await',
        }
        if self.kind in unary_forms:
            return f'{unary_forms[self.kind]}({left})'

        # Remaining kinds use a form that is not a wrapped pair.
        if self.kind == ExprKind.DICT_ENTRY:
            return f'{left}: {right}'
        if self.kind == ExprKind.SLICE:
            return f'Slice({left}:{right})'
        if self.kind == ExprKind.FOR_COMP:
            return f'for {left} in {right}'
        if self.kind == ExprKind.KWARG:
            return f'{self.name}={left}'
        if self.kind == ExprKind.STAR_EXPR:
            return f'*{left}'
        if self.kind == ExprKind.DOUBLE_STAR_EXPR:
            return f'**{left}'
        if self.kind == ExprKind.IMPORT_AS:
            return f'{left} as {right}' if right else left
        if self.kind == ExprKind.CALL:
            return f'Call({left}, {right})' if right else f'Call({left})'
        if self.kind == ExprKind.ARGS_LIST:
            return f'{left}, {right}' if left and right else left or right or ''
        if self.kind == ExprKind.COMMENT:
            return self.value or ''

        # F-strings, imports, artifacts, and unknown kinds do not encode.
        return ''

# ** model: declaration
class Declaration(DomainObject):
    '''
    A declaration (constant, class, attribute, method, or function).

    Body statements are an ordinary list so persistence chaining stays in the
    mapper layer rather than on this model.
    '''

    # * attribute: name
    name: str = Field(
        ...,
        description='Declaration name.',
    )

    # * attribute: type
    type: Optional[Type] = Field(
        None,
        description='Declaration type.',
    )

    # * attribute: metadata
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description='Untyped extra bag; artifact fields live on ArtifactDeclaration, not here.',
    )

    # * attribute: doc_string
    doc_string: Optional[str] = Field(
        None,
        description='Docstring.',
    )

    # * attribute: value
    value: Optional['Expression'] = Field(
        None,
        description='Initializer (constants / annotated assigns).',
    )

    # * attribute: code
    code: List['Statement'] = Field(
        default_factory=list,
        description='Body statements.',
    )

    # * attribute: lineno
    lineno: Optional[int] = Field(
        None,
        description='Source line.',
    )

    # * attribute: col
    col: Optional[int] = Field(
        None,
        description='0-based column.',
    )

    # * attribute: is_class
    is_class: bool = Field(
        False,
        description='Derived: type.kind == CLASS.',
    )

    # * attribute: is_func
    is_func: bool = Field(
        False,
        description='Derived: type.kind == FUNC.',
    )

    # * method: _derive_classification (model validator)
    @model_validator(mode='before')
    @classmethod
    def _derive_classification(cls, data: Any) -> Any:
        '''
        Derive class and function flags from the raw declaration type.

        :param data: The raw input being validated.
        :type data: Any
        :return: The input, with classification flags set when it is a mapping.
        :rtype: Any
        '''

        # Leave non-mapping input for Pydantic to handle.
        if not isinstance(data, dict):
            return data

        # Copy before reading the nested type kind.
        data = dict(data)
        type_val = data.get('type')
        if isinstance(type_val, dict):
            type_kind = type_val.get('kind')
        else:
            type_kind = getattr(type_val, 'kind', None)

        # Set the two derived flags from the type kind.
        data['is_class'] = type_kind == TypeKind.CLASS
        data['is_func'] = type_kind == TypeKind.FUNC

        # Return the canonicalized raw input.
        return data

    # * method: _rederive_classification (model validator)
    @model_validator(mode='after')
    def _rederive_classification(self) -> 'Declaration':
        '''
        Rederive classification flags after validation, including assignment.

        ``mode='before'`` does not run when a field is assigned, so this
        validator keeps the flags aligned with ``type``.

        :return: The declaration with classification flags aligned to its type.
        :rtype: Declaration
        '''

        # Rederive the two flags without re-entering assignment validation.
        type_kind = self.type.kind if self.type is not None else None
        object.__setattr__(self, 'is_class', type_kind == TypeKind.CLASS)
        object.__setattr__(self, 'is_func', type_kind == TypeKind.FUNC)

        # Return the classified declaration.
        return self

    # * method: inner_decl (property)
    @property
    def inner_decl(self) -> Optional['Declaration']:
        '''
        Return the first nested declaration in the body.

        :return: The first declaration statement's declaration, or None.
        :rtype: Optional[Declaration]
        '''

        # Return the first declaration statement that carries a declaration.
        for stmt in self.code:
            if stmt.is_decl and stmt.decl is not None:
                return stmt.decl

        # No nested declaration was found.
        return None

    # * method: members (property)
    @property
    def members(self) -> List['Declaration']:
        '''
        List artifact-member declarations nested in the body.

        :return: Declaration statements whose declaration is an artifact member.
        :rtype: List[Declaration]
        '''

        # Keep declaration statements marked as artifact members.
        found = []
        for stmt in self.code:
            if (
                stmt.is_decl
                and stmt.decl is not None
                and getattr(stmt.decl, 'is_artifact_member', False)
            ):
                found.append(stmt.decl)

        # Return the artifact members.
        return found

    # * method: has_method
    def has_method(self, name: str) -> bool:
        '''
        Report whether an artifact method or init member wraps a named declaration.

        :param name: The inner declaration name to find.
        :type name: str
        :return: True when a method or init member wraps that name.
        :rtype: bool
        '''

        # Match method and init members by their inner declaration name.
        for member in self.members:
            inner = member.inner_decl
            role = getattr(member, 'artifact_role', None)
            if role in ('method', 'init') and inner is not None and inner.name == name:
                return True

        # No matching method or init member was found.
        return False

    # * method: is_idempotent_delete
    def is_idempotent_delete(self) -> bool:
        '''
        Report whether this method body contains no reachable raise.

        A failing check is not a conformance finding. Callers omit
        ``idempotent`` rather than recording False.

        :return: True when no raise statement is reachable.
        :rtype: bool
        '''

        # Walk the method body, including nested control-flow and snippet bodies.
        return not any(stmt.contains_raise() for stmt in self.code)

    # * method: children (property)
    @property
    def children(self) -> List['Statement']:
        '''
        List the body statements in walk order.

        :return: A copy of the body statements.
        :rtype: List[Statement]
        '''

        # Return a copy of the body.
        return list(self.code)

    # * method: visit_role (property)
    @property
    def visit_role(self) -> Optional[str]:
        '''
        Describe this declaration by an inherited artifact role or section keyword.

        :return: The artifact role, else the section keyword, else None.
        :rtype: Optional[str]
        '''

        # Prefer an artifact role, then a section keyword. Do not invent a new classification.
        return getattr(self, 'artifact_role', None) or getattr(self, 'section_keyword', None)

    # * method: encode
    def encode(self) -> str:
        '''
        Encode this declaration as a definition query string.

        :return: ``Def(name, [params])``, or an empty string when the name is empty.
        :rtype: str
        '''

        # An empty name does not encode.
        if not self.name:
            return ''

        # Collect parameter names, excluding the receiver.
        param_names = []
        if self.type is not None and self.type.params:
            param_names = [
                param.name
                for param in self.type.params
                if param.name != 'self'
            ]

        # Join parameter names and return the definition encoding.
        joined = ', '.join(param_names)
        return f'Def({self.name}, [{joined}])'

# ** model: statement
class Statement(DomainObject):
    '''
    A statement or block inside a declaration.

    Control-flow bodies are lists of statements, not a linked next pointer.
    '''

    # * attribute: kind
    kind: StatementKind = Field(
        ...,
        description='Statement kind.',
    )

    # * attribute: lineno
    lineno: Optional[int] = Field(
        None,
        description='Source line.',
    )

    # * attribute: col
    col: Optional[int] = Field(
        None,
        description='0-based column.',
    )

    # * attribute: decl
    decl: Optional['Declaration'] = Field(
        None,
        description='Nested declaration (DECL / artifact header).',
    )

    # * attribute: init_expr
    init_expr: Optional['Expression'] = Field(
        None,
        description='Import module / for-target / with-target / assert message.',
    )

    # * attribute: expr
    expr: Optional['Expression'] = Field(
        None,
        description='Primary expression.',
    )

    # * attribute: next_expr
    next_expr: Optional['Expression'] = Field(
        None,
        description='Secondary expression.',
    )

    # * attribute: body
    body: List['Statement'] = Field(
        default_factory=list,
        description='Body.',
    )

    # * attribute: else_body
    else_body: List['Statement'] = Field(
        default_factory=list,
        description='Else / except handlers.',
    )

    # * attribute: finally_body
    finally_body: List['Statement'] = Field(
        default_factory=list,
        description='Finally body.',
    )

    # * attribute: is_artifact
    is_artifact: bool = Field(
        False,
        description='Derived: kind == ARTIFACT.',
    )

    # * attribute: is_decl
    is_decl: bool = Field(
        False,
        description='Derived: kind == DECL.',
    )

    # * attribute: is_expr
    is_expr: bool = Field(
        False,
        description='Derived: kind == EXPR.',
    )

    # * attribute: is_snippet
    is_snippet: bool = Field(
        False,
        description='Derived: kind == SNIPPET.',
    )

    # * attribute: is_return
    is_return: bool = Field(
        False,
        description='Derived: kind == RETURN.',
    )

    # * attribute: is_comment
    is_comment: bool = Field(
        False,
        description='Derived: kind == COMMENT.',
    )

    # * attribute: is_import
    is_import: bool = Field(
        False,
        description='Derived: kind == IMPORT or IMPORT_FROM.',
    )

    # * attribute: is_import_from
    is_import_from: bool = Field(
        False,
        description='Derived: kind == IMPORT_FROM.',
    )

    # * attribute: is_if_else
    is_if_else: bool = Field(
        False,
        description='Derived: kind == IF_ELSE.',
    )

    # * attribute: is_for
    is_for: bool = Field(
        False,
        description='Derived: kind == FOR.',
    )

    # * attribute: is_while
    is_while: bool = Field(
        False,
        description='Derived: kind == WHILE.',
    )

    # * attribute: is_try_except
    is_try_except: bool = Field(
        False,
        description='Derived: kind == TRY_EXCEPT.',
    )

    # * attribute: is_with
    is_with: bool = Field(
        False,
        description='Derived: kind == WITH.',
    )

    # * attribute: is_raise
    is_raise: bool = Field(
        False,
        description='Derived: kind == RAISE.',
    )

    # * attribute: is_assert
    is_assert: bool = Field(
        False,
        description='Derived: kind == ASSERT.',
    )

    # * attribute: is_pass
    is_pass: bool = Field(
        False,
        description='Derived: kind == PASS.',
    )

    # * attribute: is_continue
    is_continue: bool = Field(
        False,
        description='Derived: kind == CONTINUE.',
    )

    # * attribute: is_break
    is_break: bool = Field(
        False,
        description='Derived: kind == BREAK.',
    )

    # * attribute: is_del
    is_del: bool = Field(
        False,
        description='Derived: kind == DEL.',
    )

    # * attribute: _KIND_FLAGS
    _KIND_FLAGS: ClassVar[Dict[str, FrozenSet[StatementKind]]] = {
        'is_artifact': frozenset({StatementKind.ARTIFACT}),
        'is_decl': frozenset({StatementKind.DECL}),
        'is_expr': frozenset({StatementKind.EXPR}),
        'is_snippet': frozenset({StatementKind.SNIPPET}),
        'is_return': frozenset({StatementKind.RETURN}),
        'is_comment': frozenset({StatementKind.COMMENT}),
        'is_import': frozenset({StatementKind.IMPORT, StatementKind.IMPORT_FROM}),
        'is_import_from': frozenset({StatementKind.IMPORT_FROM}),
        'is_if_else': frozenset({StatementKind.IF_ELSE}),
        'is_for': frozenset({StatementKind.FOR}),
        'is_while': frozenset({StatementKind.WHILE}),
        'is_try_except': frozenset({StatementKind.TRY_EXCEPT}),
        'is_with': frozenset({StatementKind.WITH}),
        'is_raise': frozenset({StatementKind.RAISE}),
        'is_assert': frozenset({StatementKind.ASSERT}),
        'is_pass': frozenset({StatementKind.PASS}),
        'is_continue': frozenset({StatementKind.CONTINUE}),
        'is_break': frozenset({StatementKind.BREAK}),
        'is_del': frozenset({StatementKind.DEL}),
    }

    # * method: _derive_classification (model validator)
    @model_validator(mode='before')
    @classmethod
    def _derive_classification(cls, data: Any) -> Any:
        '''
        Derive statement-kind flags from the raw kind.

        :param data: The raw input being validated.
        :type data: Any
        :return: The input, with classification flags set when it is a mapping.
        :rtype: Any
        '''

        # Leave non-mapping input for Pydantic to handle.
        if not isinstance(data, dict):
            return data

        # Copy before deriving every kind flag.
        data = dict(data)
        data.update(cls._classification_flags(data.get('kind')))

        # Return the canonicalized raw input.
        return data

    # * method: _rederive_classification (model validator)
    @model_validator(mode='after')
    def _rederive_classification(self) -> 'Statement':
        '''
        Rederive classification flags after validation, including assignment.

        ``mode='before'`` does not run when a field is assigned, so this
        validator keeps the flags aligned with ``kind``.

        :return: The statement with classification flags aligned to its kind.
        :rtype: Statement
        '''

        # Rederive every flag without re-entering assignment validation.
        for name, value in self._classification_flags(self.kind).items():
            object.__setattr__(self, name, value)

        # Return the classified statement.
        return self

    # * method: _classification_flags (static)
    @staticmethod
    def _classification_flags(kind: Any) -> Dict[str, bool]:
        '''
        Build the derived statement-kind flags.

        :param kind: The raw or validated statement kind.
        :type kind: Any
        :return: The derived flag mapping.
        :rtype: Dict[str, bool]
        '''

        # Resolve a known kind so set membership matches enum members.
        resolved = kind
        if kind is not None and not isinstance(kind, StatementKind):
            try:
                resolved = StatementKind(kind)
            except ValueError:
                resolved = None

        # Set every flag from the kind table. PRINT and BLOCK stay flagless.
        return {
            name: resolved in kinds
            for name, kinds in Statement._KIND_FLAGS.items()
        }

    # * method: find_class
    def find_class(self) -> Optional['Declaration']:
        '''
        Find a class declaration in the body, ignoring class-typed variables.

        :return: The first body declaration whose type name equals its name, or None.
        :rtype: Optional[Declaration]
        '''

        # A class statement names the same identifier as its class type.
        for stmt in self.body:
            decl = stmt.decl if stmt.is_decl else None
            if (
                decl is not None
                and decl.is_class
                and decl.type
                and decl.name == decl.type.name
            ):
                return decl

        # No class declaration was found.
        return None

    # * method: children (property)
    @property
    def children(self) -> List[Any]:
        '''
        List nested nodes in walk order.

        :return: Present scalar children, then body, else body, and finally body.
        :rtype: List[Any]
        '''

        # Append scalar children that are present.
        nodes = []
        for node in (self.decl, self.init_expr, self.expr, self.next_expr):
            if node is not None:
                nodes.append(node)

        # Then append each body list.
        nodes.extend(self.body)
        nodes.extend(self.else_body)
        nodes.extend(self.finally_body)

        # Return the walk order.
        return nodes

    # * method: contains_raise
    def contains_raise(self) -> bool:
        '''
        Report whether this statement or a nested body contains a raise.

        :return: True when a raise is reachable from this statement.
        :rtype: bool
        '''

        # This statement is itself a raise.
        if self.is_raise:
            return True

        # Descend snippet bodies and each control-flow body.
        for name in ('body', 'else_body', 'finally_body'):
            for child in getattr(self, name) or []:
                if child.contains_raise():
                    return True

        # No raise was reachable.
        return False

    # * method: visit_role (property)
    @property
    def visit_role(self) -> str:
        '''
        Describe this node by its statement-kind value.

        :return: The kind value, or an empty string when kind is unset.
        :rtype: str
        '''

        # Return the kind value.
        return self.kind.value if self.kind else ''

    # * method: encode
    def encode(self) -> str:
        '''
        Encode this statement as a structural query string.

        :return: The encoded statement, or an empty string when the kind has no encoding.
        :rtype: str
        '''

        # Shared expression and body encodings. cond, ctx, and inner are this value.
        inner = self.expr.encode() if self.expr else ''
        body = encode_block(self.body)

        # Return, expression, and conditional forms.
        if self.is_return:
            return f'Return({inner})'
        if self.is_expr:
            return inner
        if self.is_if_else and self.else_body:
            return f'If({inner}, {body}, else={encode_block(self.else_body)})'
        if self.is_if_else:
            return f'If({inner}, {body})'

        # Loop forms.
        if self.is_for:
            target = self.init_expr.encode() if self.init_expr else ''
            iterable = self.expr.encode() if self.expr else ''
            return f'For({target}, {iterable}, {body})'
        if self.is_while:
            return f'While({inner}, {body})'

        # Try, with, raise, and assert forms.
        if self.is_try_except and self.finally_body:
            return (
                f'TryExcept(try={body}, handlers={encode_handlers(self.else_body)}, '
                f'finally={encode_block(self.finally_body)})'
            )
        if self.is_try_except:
            return f'TryExcept(try={body}, handlers={encode_handlers(self.else_body)})'
        if self.is_with and self.init_expr is not None:
            target = self.init_expr.encode()
            return f'With({inner}, {target}, {body})'
        if self.is_with:
            return f'With({inner}, {body})'
        if self.is_raise and self.expr is not None:
            return f'Raise({inner})'
        if self.is_raise:
            return 'Raise()'
        if self.is_assert and self.init_expr is not None:
            return f'Assert({inner}, {self.init_expr.encode()})'
        if self.is_assert:
            return f'Assert({inner})'

        # Simple statements and nested declarations.
        if self.is_pass:
            return 'Pass()'
        if self.is_continue:
            return 'Continue()'
        if self.is_break:
            return 'Break()'
        if self.is_del:
            return f'Del({inner})'
        if self.is_decl:
            return self.decl.encode() if self.decl else ''

        # Comments, snippets, artifacts, imports, print, and block do not encode.
        return ''

# Resolve forward references once every AST model exists.
Type.model_rebuild()
ParamList.model_rebuild()
Expression.model_rebuild()
Declaration.model_rebuild()
Statement.model_rebuild()
