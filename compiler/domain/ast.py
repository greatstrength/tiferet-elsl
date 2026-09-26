"""Tiferet Compiler AST Domain Objects"""

# *** imports

# ** core
from enum import Enum
from typing import Any, ClassVar, FrozenSet, List, Optional

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
    # ++ todo: greatstrength/tiferet-elsl#4 replaces this annotation with Optional[Expression]
    default: Optional[Any] = Field(
        None,
        description='Default value node.',
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

# Resolve ParamList's forward reference to Type once both models exist.
ParamList.model_rebuild()
