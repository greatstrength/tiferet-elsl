"""Tiferet Compiler AST Mapper Objects"""

# *** imports

# ** core
from __future__ import annotations
from typing import List, Optional

# ** app
from ..domain import (
    TypeKind,
    ExprKind,
    StatementKind,
    Type,
    ParamList,
    Declaration,
    Expression,
    Statement,
)

# *** functions

# ** function: as_list
def _as_list(value: Optional[object]) -> List:
    '''
    Normalize a missing value, list, or scalar into a runtime list.

    :param value: A list, a single item, or None.
    :type value: Optional[object]
    :return: An empty list, the original list, or a one-item list.
    :rtype: List
    '''

    # Missing values become an empty list.
    if value is None:
        return []

    # An existing list is returned unchanged.
    if isinstance(value, list):
        return value

    # Any other value is wrapped as a single item.
    return [value]

# *** mappers

# ** mapper: type_aggregate
class TypeAggregate(Type):
    '''
    Aggregate representing a type in the Tiferet AST, such as a class or method type.

    Parser actions build types through these factories instead of assigning
    domain fields ad hoc.
    '''

    # * method: set_return_type
    def set_return_type(self, return_type: TypeAggregate) -> None:
        '''
        Set the return type, nesting when one is already present.

        :param return_type: The return type to assign or nest.
        :type return_type: TypeAggregate
        '''

        # Nest on the existing return type when one is already set.
        if self.return_type is not None:
            self.return_type.set_return_type(return_type)
            return

        # Otherwise assign the return type directly.
        self.return_type = return_type

    # * method: set_subtype
    def set_subtype(self, subtype: TypeAggregate) -> None:
        '''
        Set the subtype, nesting when one is already present.

        :param subtype: The subtype to assign or nest.
        :type subtype: TypeAggregate
        '''

        # Nest on the existing subtype when one is already set.
        if self.subtype is not None:
            self.subtype.set_subtype(subtype)
            return

        # Otherwise assign the subtype directly.
        self.subtype = subtype

    # * method: new (static)
    @staticmethod
    def new(
        kind: TypeKind,
        subtype: Optional[TypeAggregate] = None,
        params: Optional[ParamList] = None,
    ) -> TypeAggregate:
        '''
        Create a type of the given kind.

        Does not set ``name`` or ``return_type``.

        :param kind: The type kind.
        :type kind: TypeKind
        :param subtype: The optional nested type.
        :type subtype: Optional[TypeAggregate]
        :param params: A parameter, a parameter list, or None.
        :type params: Optional[ParamList]
        :return: The constructed type aggregate.
        :rtype: TypeAggregate
        '''

        # Build the type without name or return type.
        return TypeAggregate(
            kind=kind,
            subtype=subtype,
            params=_as_list(params),
        )

    # * method: new_null_type (static)
    @staticmethod
    def new_null_type() -> TypeAggregate:
        '''
        Create a none type.

        :return: A type whose kind is none.
        :rtype: TypeAggregate
        '''

        # Build a none type.
        return TypeAggregate(kind=TypeKind.NONE)

    # * method: new_unknown_type (static)
    @staticmethod
    def new_unknown_type() -> TypeAggregate:
        '''
        Create an unknown type.

        :return: A type whose kind is unknown.
        :rtype: TypeAggregate
        '''

        # Build an unknown type.
        return TypeAggregate(kind=TypeKind.UNKNOWN)

    # * method: new_func_type (static)
    @staticmethod
    def new_func_type(
        params: Optional[ParamList] = None,
        return_type: Optional[TypeAggregate] = None,
    ) -> TypeAggregate:
        '''
        Create a function type.

        :param params: A parameter, a parameter list, or None.
        :type params: Optional[ParamList]
        :param return_type: The optional return type.
        :type return_type: Optional[TypeAggregate]
        :return: A function type aggregate.
        :rtype: TypeAggregate
        '''

        # Build a function type with normalized parameters.
        return TypeAggregate(
            kind=TypeKind.FUNC,
            params=_as_list(params),
            return_type=return_type,
        )

    # * method: new_artifact_type (static)
    @staticmethod
    def new_artifact_type() -> TypeAggregate:
        '''
        Create an artifact type.

        :return: A type whose kind is artifact.
        :rtype: TypeAggregate
        '''

        # Build an artifact type.
        return TypeAggregate(kind=TypeKind.ARTIFACT)

    # * method: new_class_type (static)
    @staticmethod
    def new_class_type(
        name: Optional[str] = None,
        subclasses: Optional[TypeAggregate] = None,
    ) -> TypeAggregate:
        '''
        Create a class type.

        :param name: The optional class name.
        :type name: Optional[str]
        :param subclasses: The optional subclass chain, stored as subtype.
        :type subclasses: Optional[TypeAggregate]
        :return: A class type aggregate.
        :rtype: TypeAggregate
        '''

        # Store the subclass chain on subtype.
        return TypeAggregate(
            kind=TypeKind.CLASS,
            name=name,
            subtype=subclasses,
        )

# ** mapper: param_list_aggregate
class ParamListAggregate(ParamList):
    '''
    Aggregate representing a parameter in the Tiferet AST, used for method or function declarations.

    Parser actions build parameters through these factories instead of assigning
    domain fields ad hoc.
    '''

    # * method: set_type
    def set_type(self, type: TypeAggregate) -> None:
        '''
        Set the parameter type.

        :param type: The parameter type.
        :type type: TypeAggregate
        '''

        # Assign the parameter type.
        self.type = type

    # * method: set_default
    def set_default(self, default: Optional['ExpressionAggregate']) -> None:
        '''
        Set the default value and mark the parameter optional.

        :param default: The default expression node.
        :type default: Optional[ExpressionAggregate]
        '''

        # Store the default and clear requiredness.
        self.default = default
        self.required = False

    # * method: new (static)
    @staticmethod
    def new(
        name: str,
        type: Optional[TypeAggregate] = None,
        required: bool = True,
        default: Optional['ExpressionAggregate'] = None,
    ) -> ParamListAggregate:
        '''
        Create a parameter.

        The factory default for ``required`` is True, unlike the domain field.

        :param name: The parameter name.
        :type name: str
        :param type: The optional parameter type.
        :type type: Optional[TypeAggregate]
        :param required: Whether the parameter is required.
        :type required: bool
        :param default: The optional default expression node.
        :type default: Optional[ExpressionAggregate]
        :return: The constructed parameter aggregate.
        :rtype: ParamListAggregate
        '''

        # Build the parameter from the factory arguments.
        return ParamListAggregate(
            name=name,
            type=type,
            required=required,
            default=default,
        )

    # * method: new_args_param (static)
    @staticmethod
    def new_args_param(name: str = 'args') -> ParamListAggregate:
        '''
        Create a variadic positional parameter.

        :param name: The parameter name.
        :type name: str
        :return: A parameter typed as a list of unknown.
        :rtype: ParamListAggregate
        '''

        # Type the parameter as a list of unknown.
        return ParamListAggregate(
            name=name,
            type=TypeAggregate.new(
                kind=TypeKind.LIST,
                subtype=TypeAggregate.new_unknown_type(),
            ),
        )

    # * method: new_kwargs_param (static)
    @staticmethod
    def new_kwargs_param(name: str = 'kwargs') -> ParamListAggregate:
        '''
        Create a variadic keyword parameter.

        :param name: The parameter name.
        :type name: str
        :return: A parameter typed as a dict of unknown.
        :rtype: ParamListAggregate
        '''

        # Type the parameter as a dict of unknown.
        return ParamListAggregate(
            name=name,
            type=TypeAggregate.new(
                kind=TypeKind.DICT,
                subtype=TypeAggregate.new_unknown_type(),
            ),
        )

# ** mapper: expression_aggregate
class ExpressionAggregate(Expression):
    '''
    Aggregate representing an expression in the Tiferet AST, such as a name, call, or operator.

    Parser actions build expressions through these factories instead of assigning
    domain fields ad hoc.
    '''

    # * method: set_left
    def set_left(self, left: 'ExpressionAggregate') -> None:
        '''
        Set the left child, nesting when one is already present.

        :param left: The left expression to assign or nest.
        :type left: ExpressionAggregate
        '''

        # Nest on the existing left child when one is already set.
        if self.left is not None:
            self.left.set_left(left)
            return

        # Otherwise assign the left child directly.
        self.left = left

    # * method: set_right
    def set_right(self, right: 'ExpressionAggregate') -> None:
        '''
        Set the right child, nesting when one is already present.

        :param right: The right expression to assign or nest.
        :type right: ExpressionAggregate
        '''

        # Nest on the existing right child when one is already set.
        if self.right is not None:
            self.right.set_right(right)
            return

        # Otherwise assign the right child directly.
        self.right = right

    # * method: new_name_expr (static)
    @staticmethod
    def new_name_expr(
        name: Optional[str],
        left: Optional['ExpressionAggregate'] = None,
        right: Optional['ExpressionAggregate'] = None,
        lineno: Optional[int] = None,
        col: Optional[int] = None,
    ) -> 'ExpressionAggregate':
        '''
        Create a name expression.

        :param name: The name.
        :type name: Optional[str]
        :param left: The optional left child.
        :type left: Optional[ExpressionAggregate]
        :param right: The optional right child.
        :type right: Optional[ExpressionAggregate]
        :param lineno: The optional source line.
        :type lineno: Optional[int]
        :param col: The optional 0-based column.
        :type col: Optional[int]
        :return: The constructed name expression.
        :rtype: ExpressionAggregate
        '''

        # Build a name expression from the supplied children and span.
        return ExpressionAggregate(
            kind=ExprKind.NAME,
            name=name,
            left=left,
            right=right,
            lineno=lineno,
            col=col,
        )

    # * method: new_name_or_literal_expr (static)
    @staticmethod
    def new_name_or_literal_expr(
        value: object,
        lineno: Optional[int] = None,
        col: Optional[int] = None,
    ) -> 'ExpressionAggregate':
        '''
        Create a bool, string, number, or name expression from a raw value.

        :param value: The raw value to classify.
        :type value: object
        :param lineno: The optional source line.
        :type lineno: Optional[int]
        :param col: The optional 0-based column.
        :type col: Optional[int]
        :return: The constructed expression.
        :rtype: ExpressionAggregate
        '''

        # Boolean and other strings are literal values.
        if isinstance(value, str):
            kind = ExprKind.BOOL_VAL if value in ('True', 'False') else ExprKind.STR_VAL
            return ExpressionAggregate(
                kind=kind,
                value=value,
                lineno=lineno,
                col=col,
            )

        # Integers and floats are numeric literals. Booleans are not integers here.
        if type(value) in (int, float):
            return ExpressionAggregate(
                kind=ExprKind.NUM_VAL,
                value=str(value),
                lineno=lineno,
                col=col,
            )

        # Anything else is a name expression.
        return ExpressionAggregate.new_name_expr(
            name=str(value),
            lineno=lineno,
            col=col,
        )

    # * method: new_args_list_expr (static)
    @staticmethod
    def new_args_list_expr(
        args_list: Optional['ExpressionAggregate'],
        arg: Optional['ExpressionAggregate'] = None,
    ) -> 'ExpressionAggregate':
        '''
        Create an argument-list expression.

        :param args_list: The existing argument list.
        :type args_list: Optional[ExpressionAggregate]
        :param arg: The optional next argument.
        :type arg: Optional[ExpressionAggregate]
        :return: The constructed argument-list expression.
        :rtype: ExpressionAggregate
        '''

        # Chain the next argument on the right.
        return ExpressionAggregate(
            kind=ExprKind.ARGS_LIST,
            left=args_list,
            right=arg,
        )

    # * method: new_import_expr_as (static)
    @staticmethod
    def new_import_expr_as(
        impt_expr: Optional['ExpressionAggregate'],
        alias: str,
    ) -> 'ExpressionAggregate':
        '''
        Create an import-as expression.

        :param impt_expr: The imported expression.
        :type impt_expr: Optional[ExpressionAggregate]
        :param alias: The alias name.
        :type alias: str
        :return: The constructed import-as expression.
        :rtype: ExpressionAggregate
        '''

        # Store the alias as a name expression on the right.
        return ExpressionAggregate(
            kind=ExprKind.IMPORT_AS,
            left=impt_expr,
            right=ExpressionAggregate.new_name_expr(alias),
        )

    # * method: new_import_expr_multi (static)
    @staticmethod
    def new_import_expr_multi(
        existing_expr: Optional['ExpressionAggregate'],
        new_name: str,
    ) -> 'ExpressionAggregate':
        '''
        Create a multi-import expression.

        :param existing_expr: The existing import expression.
        :type existing_expr: Optional[ExpressionAggregate]
        :param new_name: The next imported name.
        :type new_name: str
        :return: The constructed multi-import expression.
        :rtype: ExpressionAggregate
        '''

        # Append the next name on the right.
        return ExpressionAggregate(
            kind=ExprKind.IMPORT_MULTI,
            left=existing_expr,
            right=ExpressionAggregate.new_name_expr(new_name),
        )

    # * method: new_call_expr (static)
    @staticmethod
    def new_call_expr(
        caller: Optional['ExpressionAggregate'],
        arguments: Optional['ExpressionAggregate'] = None,
        lineno: Optional[int] = None,
        col: Optional[int] = None,
    ) -> 'ExpressionAggregate':
        '''
        Create a call expression.

        :param caller: The callee expression.
        :type caller: Optional[ExpressionAggregate]
        :param arguments: The optional argument expression.
        :type arguments: Optional[ExpressionAggregate]
        :param lineno: The optional source line.
        :type lineno: Optional[int]
        :param col: The optional 0-based column.
        :type col: Optional[int]
        :return: The constructed call expression.
        :rtype: ExpressionAggregate
        '''

        # Store the callee on the left and the arguments on the right.
        return ExpressionAggregate(
            kind=ExprKind.CALL,
            left=caller,
            right=arguments,
            lineno=lineno,
            col=col,
        )

    # * method: new_attribute_expr (static)
    @staticmethod
    def new_attribute_expr(
        receiver: Optional['ExpressionAggregate'],
        attr: str,
        lineno: Optional[int] = None,
        col: Optional[int] = None,
    ) -> 'ExpressionAggregate':
        '''
        Create an attribute expression.

        :param receiver: The receiver expression.
        :type receiver: Optional[ExpressionAggregate]
        :param attr: The attribute name.
        :type attr: str
        :param lineno: The optional source line.
        :type lineno: Optional[int]
        :param col: The optional 0-based column.
        :type col: Optional[int]
        :return: The constructed attribute expression.
        :rtype: ExpressionAggregate
        '''

        # Keep the receiver on the left and the attribute as the name.
        return ExpressionAggregate(
            kind=ExprKind.ATTRIBUTE,
            name=attr,
            left=receiver,
            lineno=lineno,
            col=col,
        )

    # * method: new_assign_expr (static)
    @staticmethod
    def new_assign_expr(
        target: Optional['ExpressionAggregate'],
        value: Optional['ExpressionAggregate'],
        lineno: Optional[int] = None,
        col: Optional[int] = None,
    ) -> 'ExpressionAggregate':
        '''
        Create an assignment expression.

        :param target: The assignment target.
        :type target: Optional[ExpressionAggregate]
        :param value: The assigned value.
        :type value: Optional[ExpressionAggregate]
        :param lineno: The optional source line.
        :type lineno: Optional[int]
        :param col: The optional 0-based column.
        :type col: Optional[int]
        :return: The constructed assignment expression.
        :rtype: ExpressionAggregate
        '''

        # Store the target on the left and the value on the right.
        return ExpressionAggregate(
            kind=ExprKind.ASSIGN,
            left=target,
            right=value,
            lineno=lineno,
            col=col,
        )

    # * method: new_operator_expr (static)
    @staticmethod
    def new_operator_expr(
        operator: str,
        left: Optional['ExpressionAggregate'],
        right: Optional['ExpressionAggregate'],
        lineno: Optional[int] = None,
        col: Optional[int] = None,
    ) -> 'ExpressionAggregate':
        '''
        Create an operator expression.

        Unknown operators become name expressions. The operator string is
        always stored as ``value``.

        :param operator: The operator text.
        :type operator: str
        :param left: The left operand.
        :type left: Optional[ExpressionAggregate]
        :param right: The right operand.
        :type right: Optional[ExpressionAggregate]
        :param lineno: The optional source line.
        :type lineno: Optional[int]
        :param col: The optional 0-based column.
        :type col: Optional[int]
        :return: The constructed operator expression.
        :rtype: ExpressionAggregate
        '''

        # Map a known operator to its kind. Anything else is a name.
        kinds = {
            '+': ExprKind.ADD,
            '-': ExprKind.SUB,
            '*': ExprKind.MUL,
            '/': ExprKind.DIV,
            '%': ExprKind.MOD,
            '**': ExprKind.EXP,
            '//': ExprKind.FLOORDIV,
            '==': ExprKind.EQ,
            '!=': ExprKind.NEQ,
            '<': ExprKind.LT,
            '<=': ExprKind.LTE,
            '>': ExprKind.GT,
            '>=': ExprKind.GTE,
            'and': ExprKind.AND,
            'or': ExprKind.OR,
            'is': ExprKind.IS,
            'is not': ExprKind.IS_NOT,
            'in': ExprKind.IN,
            'not in': ExprKind.NOT_IN,
        }

        # Store the operator text even when the kind falls back to name.
        return ExpressionAggregate(
            kind=kinds.get(operator, ExprKind.NAME),
            value=operator,
            left=left,
            right=right,
            lineno=lineno,
            col=col,
        )

    # * method: new_none_expr (static)
    @staticmethod
    def new_none_expr(
        lineno: Optional[int] = None,
        col: Optional[int] = None,
    ) -> 'ExpressionAggregate':
        '''
        Create a none literal.

        :param lineno: The optional source line.
        :type lineno: Optional[int]
        :param col: The optional 0-based column.
        :type col: Optional[int]
        :return: The constructed none expression.
        :rtype: ExpressionAggregate
        '''

        # Build a none literal.
        return ExpressionAggregate(
            kind=ExprKind.NONE_VAL,
            value='None',
            lineno=lineno,
            col=col,
        )

    # * method: new_ellipsis_expr (static)
    @staticmethod
    def new_ellipsis_expr(
        lineno: Optional[int] = None,
        col: Optional[int] = None,
    ) -> 'ExpressionAggregate':
        '''
        Create an ellipsis literal.

        :param lineno: The optional source line.
        :type lineno: Optional[int]
        :param col: The optional 0-based column.
        :type col: Optional[int]
        :return: The constructed ellipsis expression.
        :rtype: ExpressionAggregate
        '''

        # Build an ellipsis literal.
        return ExpressionAggregate(
            kind=ExprKind.ELLIPSIS_VAL,
            value='...',
            lineno=lineno,
            col=col,
        )

    # * method: new_not_expr (static)
    @staticmethod
    def new_not_expr(
        operand: Optional['ExpressionAggregate'],
        lineno: Optional[int] = None,
        col: Optional[int] = None,
    ) -> 'ExpressionAggregate':
        '''
        Create a not expression.

        :param operand: The negated expression.
        :type operand: Optional[ExpressionAggregate]
        :param lineno: The optional source line.
        :type lineno: Optional[int]
        :param col: The optional 0-based column.
        :type col: Optional[int]
        :return: The constructed not expression.
        :rtype: ExpressionAggregate
        '''

        # Store the operand on the left.
        return ExpressionAggregate(
            kind=ExprKind.NOT,
            left=operand,
            lineno=lineno,
            col=col,
        )

    # * method: new_unary_minus_expr (static)
    @staticmethod
    def new_unary_minus_expr(
        operand: Optional['ExpressionAggregate'],
        lineno: Optional[int] = None,
        col: Optional[int] = None,
    ) -> 'ExpressionAggregate':
        '''
        Create a unary-minus expression.

        :param operand: The negated expression.
        :type operand: Optional[ExpressionAggregate]
        :param lineno: The optional source line.
        :type lineno: Optional[int]
        :param col: The optional 0-based column.
        :type col: Optional[int]
        :return: The constructed unary-minus expression.
        :rtype: ExpressionAggregate
        '''

        # Store the operand on the left.
        return ExpressionAggregate(
            kind=ExprKind.UNARY_MINUS,
            left=operand,
            lineno=lineno,
            col=col,
        )

    # * method: new_list_literal_expr (static)
    @staticmethod
    def new_list_literal_expr(
        elements: Optional['ExpressionAggregate'] = None,
        lineno: Optional[int] = None,
        col: Optional[int] = None,
    ) -> 'ExpressionAggregate':
        '''
        Create a list literal.

        :param elements: The optional element expression.
        :type elements: Optional[ExpressionAggregate]
        :param lineno: The optional source line.
        :type lineno: Optional[int]
        :param col: The optional 0-based column.
        :type col: Optional[int]
        :return: The constructed list literal.
        :rtype: ExpressionAggregate
        '''

        # Store the elements on the left.
        return ExpressionAggregate(
            kind=ExprKind.LIST_LITERAL,
            left=elements,
            lineno=lineno,
            col=col,
        )

    # * method: new_dict_literal_expr (static)
    @staticmethod
    def new_dict_literal_expr(
        entries: Optional['ExpressionAggregate'] = None,
        lineno: Optional[int] = None,
        col: Optional[int] = None,
    ) -> 'ExpressionAggregate':
        '''
        Create a dict literal.

        :param entries: The optional entry expression.
        :type entries: Optional[ExpressionAggregate]
        :param lineno: The optional source line.
        :type lineno: Optional[int]
        :param col: The optional 0-based column.
        :type col: Optional[int]
        :return: The constructed dict literal.
        :rtype: ExpressionAggregate
        '''

        # Store the entries on the left.
        return ExpressionAggregate(
            kind=ExprKind.DICT_LITERAL,
            left=entries,
            lineno=lineno,
            col=col,
        )

    # * method: new_dict_entry_expr (static)
    @staticmethod
    def new_dict_entry_expr(
        key: Optional['ExpressionAggregate'],
        value: Optional['ExpressionAggregate'],
    ) -> 'ExpressionAggregate':
        '''
        Create a dict entry.

        :param key: The entry key.
        :type key: Optional[ExpressionAggregate]
        :param value: The entry value.
        :type value: Optional[ExpressionAggregate]
        :return: The constructed dict entry.
        :rtype: ExpressionAggregate
        '''

        # Store the key on the left and the value on the right.
        return ExpressionAggregate(
            kind=ExprKind.DICT_ENTRY,
            left=key,
            right=value,
        )

    # * method: new_set_literal_expr (static)
    @staticmethod
    def new_set_literal_expr(
        elements: Optional['ExpressionAggregate'] = None,
        lineno: Optional[int] = None,
        col: Optional[int] = None,
    ) -> 'ExpressionAggregate':
        '''
        Create a set literal.

        :param elements: The optional element expression.
        :type elements: Optional[ExpressionAggregate]
        :param lineno: The optional source line.
        :type lineno: Optional[int]
        :param col: The optional 0-based column.
        :type col: Optional[int]
        :return: The constructed set literal.
        :rtype: ExpressionAggregate
        '''

        # Store the elements on the left.
        return ExpressionAggregate(
            kind=ExprKind.SET_LITERAL,
            left=elements,
            lineno=lineno,
            col=col,
        )

    # * method: new_tuple_expr (static)
    @staticmethod
    def new_tuple_expr(
        elements: Optional['ExpressionAggregate'] = None,
        lineno: Optional[int] = None,
        col: Optional[int] = None,
    ) -> 'ExpressionAggregate':
        '''
        Create a tuple expression.

        :param elements: The optional element expression.
        :type elements: Optional[ExpressionAggregate]
        :param lineno: The optional source line.
        :type lineno: Optional[int]
        :param col: The optional 0-based column.
        :type col: Optional[int]
        :return: The constructed tuple expression.
        :rtype: ExpressionAggregate
        '''

        # Store the elements on the left.
        return ExpressionAggregate(
            kind=ExprKind.TUPLE,
            left=elements,
            lineno=lineno,
            col=col,
        )

    # * method: new_subscript_expr (static)
    @staticmethod
    def new_subscript_expr(
        target: Optional['ExpressionAggregate'],
        index: Optional['ExpressionAggregate'],
        lineno: Optional[int] = None,
        col: Optional[int] = None,
    ) -> 'ExpressionAggregate':
        '''
        Create a subscript expression.

        :param target: The subscripted expression.
        :type target: Optional[ExpressionAggregate]
        :param index: The index expression.
        :type index: Optional[ExpressionAggregate]
        :param lineno: The optional source line.
        :type lineno: Optional[int]
        :param col: The optional 0-based column.
        :type col: Optional[int]
        :return: The constructed subscript expression.
        :rtype: ExpressionAggregate
        '''

        # Store the target on the left and the index on the right.
        return ExpressionAggregate(
            kind=ExprKind.SUBSCRIPT,
            left=target,
            right=index,
            lineno=lineno,
            col=col,
        )

    # * method: new_slice_expr (static)
    @staticmethod
    def new_slice_expr(
        start: Optional['ExpressionAggregate'] = None,
        stop: Optional['ExpressionAggregate'] = None,
        lineno: Optional[int] = None,
        col: Optional[int] = None,
    ) -> 'ExpressionAggregate':
        '''
        Create a slice expression.

        :param start: The optional start expression.
        :type start: Optional[ExpressionAggregate]
        :param stop: The optional stop expression.
        :type stop: Optional[ExpressionAggregate]
        :param lineno: The optional source line.
        :type lineno: Optional[int]
        :param col: The optional 0-based column.
        :type col: Optional[int]
        :return: The constructed slice expression.
        :rtype: ExpressionAggregate
        '''

        # Store the bounds on the left and right.
        return ExpressionAggregate(
            kind=ExprKind.SLICE,
            left=start,
            right=stop,
            lineno=lineno,
            col=col,
        )

    # * method: new_ternary_expr (static)
    @staticmethod
    def new_ternary_expr(
        true_val: Optional['ExpressionAggregate'],
        condition: Optional['ExpressionAggregate'],
        false_val: Optional['ExpressionAggregate'],
        lineno: Optional[int] = None,
        col: Optional[int] = None,
    ) -> 'ExpressionAggregate':
        '''
        Create a ternary expression.

        ``condition`` is accepted and not stored. There is no third child field.

        :param true_val: The true-branch expression.
        :type true_val: Optional[ExpressionAggregate]
        :param condition: The condition, accepted and not stored.
        :type condition: Optional[ExpressionAggregate]
        :param false_val: The false-branch expression.
        :type false_val: Optional[ExpressionAggregate]
        :param lineno: The optional source line.
        :type lineno: Optional[int]
        :param col: The optional 0-based column.
        :type col: Optional[int]
        :return: The constructed ternary expression.
        :rtype: ExpressionAggregate
        '''

        # Accept the condition without storing it.
        _ = condition

        # Store only the true and false branches.
        return ExpressionAggregate(
            kind=ExprKind.TERNARY,
            left=true_val,
            right=false_val,
            lineno=lineno,
            col=col,
        )

    # * method: new_comprehension_expr (static)
    @staticmethod
    def new_comprehension_expr(
        output: Optional['ExpressionAggregate'],
        iterators: Optional['ExpressionAggregate'],
        lineno: Optional[int] = None,
        col: Optional[int] = None,
    ) -> 'ExpressionAggregate':
        '''
        Create a comprehension expression.

        :param output: The output expression.
        :type output: Optional[ExpressionAggregate]
        :param iterators: The iterator expression.
        :type iterators: Optional[ExpressionAggregate]
        :param lineno: The optional source line.
        :type lineno: Optional[int]
        :param col: The optional 0-based column.
        :type col: Optional[int]
        :return: The constructed comprehension expression.
        :rtype: ExpressionAggregate
        '''

        # Store the output on the left and the iterators on the right.
        return ExpressionAggregate(
            kind=ExprKind.COMPREHENSION,
            left=output,
            right=iterators,
            lineno=lineno,
            col=col,
        )

    # * method: new_for_comp_expr (static)
    @staticmethod
    def new_for_comp_expr(
        target: Optional['ExpressionAggregate'],
        iterable: Optional['ExpressionAggregate'],
        condition: Optional['ExpressionAggregate'] = None,
    ) -> 'ExpressionAggregate':
        '''
        Create a for-comprehension clause.

        ``condition`` is accepted and not stored.

        :param target: The loop target.
        :type target: Optional[ExpressionAggregate]
        :param iterable: The iterable expression.
        :type iterable: Optional[ExpressionAggregate]
        :param condition: The optional condition, accepted and not stored.
        :type condition: Optional[ExpressionAggregate]
        :return: The constructed for-comprehension clause.
        :rtype: ExpressionAggregate
        '''

        # Accept the condition without storing it.
        _ = condition

        # Store the target on the left and the iterable on the right.
        return ExpressionAggregate(
            kind=ExprKind.FOR_COMP,
            left=target,
            right=iterable,
        )

    # * method: new_await_expr (static)
    @staticmethod
    def new_await_expr(
        operand: Optional['ExpressionAggregate'],
        lineno: Optional[int] = None,
        col: Optional[int] = None,
    ) -> 'ExpressionAggregate':
        '''
        Create an await expression.

        :param operand: The awaited expression.
        :type operand: Optional[ExpressionAggregate]
        :param lineno: The optional source line.
        :type lineno: Optional[int]
        :param col: The optional 0-based column.
        :type col: Optional[int]
        :return: The constructed await expression.
        :rtype: ExpressionAggregate
        '''

        # Store the operand on the left.
        return ExpressionAggregate(
            kind=ExprKind.AWAIT,
            left=operand,
            lineno=lineno,
            col=col,
        )

    # * method: new_kwarg_expr (static)
    @staticmethod
    def new_kwarg_expr(
        name: str,
        value: Optional['ExpressionAggregate'],
    ) -> 'ExpressionAggregate':
        '''
        Create a keyword-argument expression.

        :param name: The keyword name.
        :type name: str
        :param value: The keyword value.
        :type value: Optional[ExpressionAggregate]
        :return: The constructed keyword-argument expression.
        :rtype: ExpressionAggregate
        '''

        # Store the name and the value on the left.
        return ExpressionAggregate(
            kind=ExprKind.KWARG,
            name=name,
            left=value,
        )

    # * method: new_star_expr (static)
    @staticmethod
    def new_star_expr(
        operand: Optional['ExpressionAggregate'],
    ) -> 'ExpressionAggregate':
        '''
        Create a star expression.

        :param operand: The starred expression.
        :type operand: Optional[ExpressionAggregate]
        :return: The constructed star expression.
        :rtype: ExpressionAggregate
        '''

        # Store the operand on the left.
        return ExpressionAggregate(
            kind=ExprKind.STAR_EXPR,
            left=operand,
        )

    # * method: new_double_star_expr (static)
    @staticmethod
    def new_double_star_expr(
        operand: Optional['ExpressionAggregate'],
    ) -> 'ExpressionAggregate':
        '''
        Create a double-star expression.

        :param operand: The double-starred expression.
        :type operand: Optional[ExpressionAggregate]
        :return: The constructed double-star expression.
        :rtype: ExpressionAggregate
        '''

        # Store the operand on the left.
        return ExpressionAggregate(
            kind=ExprKind.DOUBLE_STAR_EXPR,
            left=operand,
        )

    # * method: new_comment_expr (static)
    @staticmethod
    def new_comment_expr(
        comment_text: str,
        lineno: Optional[int] = None,
        col: Optional[int] = None,
    ) -> 'ExpressionAggregate':
        '''
        Create a comment expression.

        :param comment_text: The comment text.
        :type comment_text: str
        :param lineno: The optional source line.
        :type lineno: Optional[int]
        :param col: The optional 0-based column.
        :type col: Optional[int]
        :return: The constructed comment expression.
        :rtype: ExpressionAggregate
        '''

        # Store the comment text as the value.
        return ExpressionAggregate(
            kind=ExprKind.COMMENT,
            value=comment_text,
            lineno=lineno,
            col=col,
        )

    # * method: collect_import_names (static)
    @staticmethod
    def collect_import_names(
        expr: Optional['ExpressionAggregate'],
    ) -> List[str]:
        '''
        Collect imported names from a name, multi-import, or import-as expression.

        :param expr: The import expression, or None.
        :type expr: Optional[ExpressionAggregate]
        :return: The imported names, or an empty list.
        :rtype: List[str]
        '''

        # A missing expression contributes no names.
        if not expr:
            return []

        # A name contributes itself when it is set.
        if expr.kind == ExprKind.NAME:
            return [expr.name] if expr.name else []

        # A multi-import flattens both children.
        if expr.kind == ExprKind.IMPORT_MULTI:
            return (
                ExpressionAggregate.collect_import_names(expr.left)
                + ExpressionAggregate.collect_import_names(expr.right)
            )

        # An import-as contributes only the alias.
        if expr.kind == ExprKind.IMPORT_AS:
            if expr.right and expr.right.name:
                return [expr.right.name]
            return []

        # Every other kind contributes no names.
        return []

# ** mapper: declaration_aggregate
class DeclarationAggregate(Declaration):
    '''
    Aggregate representing a declaration in the Tiferet AST, such as a class or method declaration.

    Parser actions build declarations through these factories instead of assigning
    domain fields ad hoc.
    '''

    # * method: set_name
    def set_name(self, name: str) -> None:
        '''
        Set the declaration name.

        :param name: The declaration name.
        :type name: str
        '''

        # Assign the declaration name.
        self.name = name

    # * method: set_doc_string
    def set_doc_string(self, doc_string: Optional[str]) -> None:
        '''
        Set the declaration docstring.

        :param doc_string: The docstring text.
        :type doc_string: Optional[str]
        '''

        # Assign the docstring.
        self.doc_string = doc_string

    # * method: new_module_decl (static)
    @staticmethod
    def new_module_decl(
        name: str,
        code: Optional[object] = None,
        doc_string: Optional[str] = None,
    ) -> 'DeclarationAggregate':
        '''
        Create a module declaration.

        :param name: The module name.
        :type name: str
        :param code: A statement, a statement list, or None.
        :type code: Optional[object]
        :param doc_string: The optional docstring.
        :type doc_string: Optional[str]
        :return: The constructed module declaration.
        :rtype: DeclarationAggregate
        '''

        # Normalize the module body to a list.
        return DeclarationAggregate(
            name=name,
            doc_string=doc_string,
            code=_as_list(code),
        )

    # * method: new_func_decl (static)
    @staticmethod
    def new_func_decl(
        name: str,
        type: Optional[TypeAggregate] = None,
        doc_string: Optional[str] = None,
        body: Optional[object] = None,
        lineno: Optional[int] = None,
        col: Optional[int] = None,
    ) -> 'DeclarationAggregate':
        '''
        Create a function declaration.

        :param name: The function name.
        :type name: str
        :param type: The optional function type.
        :type type: Optional[TypeAggregate]
        :param doc_string: The optional docstring.
        :type doc_string: Optional[str]
        :param body: A statement, a statement list, or None.
        :type body: Optional[object]
        :param lineno: The optional source line.
        :type lineno: Optional[int]
        :param col: The optional 0-based column.
        :type col: Optional[int]
        :return: The constructed function declaration.
        :rtype: DeclarationAggregate
        '''

        # Normalize the function body to a list.
        return DeclarationAggregate(
            name=name,
            type=type,
            doc_string=doc_string,
            code=_as_list(body),
            lineno=lineno,
            col=col,
        )

    # * method: new_class_decl (static)
    @staticmethod
    def new_class_decl(
        name: str,
        subclasses: Optional[TypeAggregate],
        doc_string: Optional[str],
        members: Optional[object],
        lineno: Optional[int] = None,
        col: Optional[int] = None,
    ) -> 'DeclarationAggregate':
        '''
        Create a class declaration.

        :param name: The class name.
        :type name: str
        :param subclasses: The optional subclass chain.
        :type subclasses: Optional[TypeAggregate]
        :param doc_string: The optional docstring.
        :type doc_string: Optional[str]
        :param members: A member, a member list, or None.
        :type members: Optional[object]
        :param lineno: The optional source line.
        :type lineno: Optional[int]
        :param col: The optional 0-based column.
        :type col: Optional[int]
        :return: The constructed class declaration.
        :rtype: DeclarationAggregate
        '''

        # Wrap the class name and subclass chain in a class type.
        return DeclarationAggregate(
            name=name,
            type=TypeAggregate.new_class_type(
                name=name,
                subclasses=subclasses,
            ),
            doc_string=doc_string,
            code=_as_list(members),
            lineno=lineno,
            col=col,
        )

    # * method: new_attr_decl (static)
    @staticmethod
    def new_attr_decl(
        name: str,
        types: Optional[TypeAggregate] = None,
        value: Optional[ExpressionAggregate] = None,
        lineno: Optional[int] = None,
        col: Optional[int] = None,
    ) -> 'DeclarationAggregate':
        '''
        Create an attribute declaration.

        :param name: The attribute name.
        :type name: str
        :param types: The optional attribute type.
        :type types: Optional[TypeAggregate]
        :param value: The optional initializer.
        :type value: Optional[ExpressionAggregate]
        :param lineno: The optional source line.
        :type lineno: Optional[int]
        :param col: The optional 0-based column.
        :type col: Optional[int]
        :return: The constructed attribute declaration.
        :rtype: DeclarationAggregate
        '''

        # Construct from the name and span, then assign optional fields.
        agg = DeclarationAggregate(
            name=name,
            lineno=lineno,
            col=col,
        )
        if types:
            agg.type = types
        if value:
            agg.value = value
        return agg

# ** mapper: statement_aggregate
class StatementAggregate(Statement):
    '''
    Aggregate representing a statement in the Tiferet AST, such as an if-else or for statement.

    Parser actions build statements through these factories instead of assigning
    domain fields ad hoc.
    '''

    # * method: new_import_stmt (static)
    @staticmethod
    def new_import_stmt(
        import_expr: Optional[ExpressionAggregate],
        lineno: Optional[int] = None,
        col: Optional[int] = None,
    ) -> 'StatementAggregate':
        '''
        Create an import statement.

        :param import_expr: The import expression.
        :type import_expr: Optional[ExpressionAggregate]
        :param lineno: The optional source line.
        :type lineno: Optional[int]
        :param col: The optional 0-based column.
        :type col: Optional[int]
        :return: The constructed import statement.
        :rtype: StatementAggregate
        '''

        # Store the import expression as the primary expression.
        return StatementAggregate(
            kind=StatementKind.IMPORT,
            expr=import_expr,
            lineno=lineno,
            col=col,
        )

    # * method: new_import_stmt_from (static)
    @staticmethod
    def new_import_stmt_from(
        from_expr: Optional[ExpressionAggregate],
        import_expr: Optional[ExpressionAggregate],
        lineno: Optional[int] = None,
        col: Optional[int] = None,
    ) -> 'StatementAggregate':
        '''
        Create an import-from statement.

        :param from_expr: The module expression.
        :type from_expr: Optional[ExpressionAggregate]
        :param import_expr: The imported-name expression.
        :type import_expr: Optional[ExpressionAggregate]
        :param lineno: The optional source line.
        :type lineno: Optional[int]
        :param col: The optional 0-based column.
        :type col: Optional[int]
        :return: The constructed import-from statement.
        :rtype: StatementAggregate
        '''

        # Store the module and the imported names.
        return StatementAggregate(
            kind=StatementKind.IMPORT_FROM,
            init_expr=from_expr,
            expr=import_expr,
            lineno=lineno,
            col=col,
        )

    # * method: new_decl_stmt (static)
    @staticmethod
    def new_decl_stmt(decl: DeclarationAggregate) -> 'StatementAggregate':
        '''
        Create a declaration statement.

        :param decl: The nested declaration.
        :type decl: DeclarationAggregate
        :return: The constructed declaration statement.
        :rtype: StatementAggregate
        '''

        # Store the nested declaration.
        return StatementAggregate(
            kind=StatementKind.DECL,
            decl=decl,
        )

    # * method: new_expr_stmt (static)
    @staticmethod
    def new_expr_stmt(
        expr: Optional[ExpressionAggregate],
        lineno: Optional[int] = None,
        col: Optional[int] = None,
    ) -> 'StatementAggregate':
        '''
        Create an expression statement.

        :param expr: The expression.
        :type expr: Optional[ExpressionAggregate]
        :param lineno: The optional source line.
        :type lineno: Optional[int]
        :param col: The optional 0-based column.
        :type col: Optional[int]
        :return: The constructed expression statement.
        :rtype: StatementAggregate
        '''

        # Store the expression as the primary expression.
        return StatementAggregate(
            kind=StatementKind.EXPR,
            expr=expr,
            lineno=lineno,
            col=col,
        )

    # * method: new_comment_stmt (static)
    @staticmethod
    def new_comment_stmt(
        comment: Optional[ExpressionAggregate],
        lineno: Optional[int] = None,
        col: Optional[int] = None,
    ) -> 'StatementAggregate':
        '''
        Create a comment statement.

        :param comment: The comment expression.
        :type comment: Optional[ExpressionAggregate]
        :param lineno: The optional source line.
        :type lineno: Optional[int]
        :param col: The optional 0-based column.
        :type col: Optional[int]
        :return: The constructed comment statement.
        :rtype: StatementAggregate
        '''

        # Store the comment as the primary expression.
        return StatementAggregate(
            kind=StatementKind.COMMENT,
            expr=comment,
            lineno=lineno,
            col=col,
        )

    # * method: new_if_stmt (static)
    @staticmethod
    def new_if_stmt(
        condition: Optional[ExpressionAggregate],
        body: Optional[object],
        else_body: Optional[object] = None,
        lineno: Optional[int] = None,
        col: Optional[int] = None,
    ) -> 'StatementAggregate':
        '''
        Create an if-else statement.

        :param condition: The condition expression.
        :type condition: Optional[ExpressionAggregate]
        :param body: A statement, a statement list, or None.
        :type body: Optional[object]
        :param else_body: A statement, a statement list, or None.
        :type else_body: Optional[object]
        :param lineno: The optional source line.
        :type lineno: Optional[int]
        :param col: The optional 0-based column.
        :type col: Optional[int]
        :return: The constructed if-else statement.
        :rtype: StatementAggregate
        '''

        # Normalize both bodies to lists.
        return StatementAggregate(
            kind=StatementKind.IF_ELSE,
            expr=condition,
            body=_as_list(body),
            else_body=_as_list(else_body),
            lineno=lineno,
            col=col,
        )

    # * method: new_for_stmt (static)
    @staticmethod
    def new_for_stmt(
        target: Optional[ExpressionAggregate],
        iterable: Optional[ExpressionAggregate],
        body: Optional[object],
        else_body: Optional[object] = None,
        lineno: Optional[int] = None,
        col: Optional[int] = None,
    ) -> 'StatementAggregate':
        '''
        Create a for statement.

        :param target: The loop target.
        :type target: Optional[ExpressionAggregate]
        :param iterable: The iterable expression.
        :type iterable: Optional[ExpressionAggregate]
        :param body: A statement, a statement list, or None.
        :type body: Optional[object]
        :param else_body: A statement, a statement list, or None.
        :type else_body: Optional[object]
        :param lineno: The optional source line.
        :type lineno: Optional[int]
        :param col: The optional 0-based column.
        :type col: Optional[int]
        :return: The constructed for statement.
        :rtype: StatementAggregate
        '''

        # Normalize both bodies to lists.
        return StatementAggregate(
            kind=StatementKind.FOR,
            init_expr=target,
            expr=iterable,
            body=_as_list(body),
            else_body=_as_list(else_body),
            lineno=lineno,
            col=col,
        )

    # * method: new_while_stmt (static)
    @staticmethod
    def new_while_stmt(
        condition: Optional[ExpressionAggregate],
        body: Optional[object],
        lineno: Optional[int] = None,
        col: Optional[int] = None,
    ) -> 'StatementAggregate':
        '''
        Create a while statement.

        :param condition: The condition expression.
        :type condition: Optional[ExpressionAggregate]
        :param body: A statement, a statement list, or None.
        :type body: Optional[object]
        :param lineno: The optional source line.
        :type lineno: Optional[int]
        :param col: The optional 0-based column.
        :type col: Optional[int]
        :return: The constructed while statement.
        :rtype: StatementAggregate
        '''

        # Normalize the body to a list.
        return StatementAggregate(
            kind=StatementKind.WHILE,
            expr=condition,
            body=_as_list(body),
            lineno=lineno,
            col=col,
        )

    # * method: new_try_stmt (static)
    @staticmethod
    def new_try_stmt(
        body: Optional[object],
        except_body: Optional[object] = None,
        finally_body: Optional[object] = None,
        except_expr: Optional[ExpressionAggregate] = None,
        lineno: Optional[int] = None,
        col: Optional[int] = None,
    ) -> 'StatementAggregate':
        '''
        Create a try-except statement.

        :param body: A statement, a statement list, or None.
        :type body: Optional[object]
        :param except_body: A handler, a handler list, or None.
        :type except_body: Optional[object]
        :param finally_body: A statement, a statement list, or None.
        :type finally_body: Optional[object]
        :param except_expr: The optional exception expression.
        :type except_expr: Optional[ExpressionAggregate]
        :param lineno: The optional source line.
        :type lineno: Optional[int]
        :param col: The optional 0-based column.
        :type col: Optional[int]
        :return: The constructed try-except statement.
        :rtype: StatementAggregate
        '''

        # Store the finally body; do not drop it.
        return StatementAggregate(
            kind=StatementKind.TRY_EXCEPT,
            expr=except_expr,
            body=_as_list(body),
            else_body=_as_list(except_body),
            finally_body=_as_list(finally_body),
            next_expr=None,
            lineno=lineno,
            col=col,
        )

    # * method: new_with_stmt (static)
    @staticmethod
    def new_with_stmt(
        context_expr: Optional[ExpressionAggregate],
        target: Optional[ExpressionAggregate],
        body: Optional[object],
        lineno: Optional[int] = None,
        col: Optional[int] = None,
    ) -> 'StatementAggregate':
        '''
        Create a with statement.

        :param context_expr: The context expression.
        :type context_expr: Optional[ExpressionAggregate]
        :param target: The optional target expression.
        :type target: Optional[ExpressionAggregate]
        :param body: A statement, a statement list, or None.
        :type body: Optional[object]
        :param lineno: The optional source line.
        :type lineno: Optional[int]
        :param col: The optional 0-based column.
        :type col: Optional[int]
        :return: The constructed with statement.
        :rtype: StatementAggregate
        '''

        # Normalize the body to a list.
        return StatementAggregate(
            kind=StatementKind.WITH,
            expr=context_expr,
            init_expr=target,
            body=_as_list(body),
            lineno=lineno,
            col=col,
        )

    # * method: new_raise_stmt (static)
    @staticmethod
    def new_raise_stmt(
        expr: Optional[ExpressionAggregate] = None,
        lineno: Optional[int] = None,
        col: Optional[int] = None,
    ) -> 'StatementAggregate':
        '''
        Create a raise statement.

        :param expr: The optional exception expression.
        :type expr: Optional[ExpressionAggregate]
        :param lineno: The optional source line.
        :type lineno: Optional[int]
        :param col: The optional 0-based column.
        :type col: Optional[int]
        :return: The constructed raise statement.
        :rtype: StatementAggregate
        '''

        # Store the optional exception expression.
        return StatementAggregate(
            kind=StatementKind.RAISE,
            expr=expr,
            lineno=lineno,
            col=col,
        )

    # * method: new_assert_stmt (static)
    @staticmethod
    def new_assert_stmt(
        expr: Optional[ExpressionAggregate],
        msg: Optional[ExpressionAggregate] = None,
        lineno: Optional[int] = None,
        col: Optional[int] = None,
    ) -> 'StatementAggregate':
        '''
        Create an assert statement.

        :param expr: The asserted expression.
        :type expr: Optional[ExpressionAggregate]
        :param msg: The optional message expression.
        :type msg: Optional[ExpressionAggregate]
        :param lineno: The optional source line.
        :type lineno: Optional[int]
        :param col: The optional 0-based column.
        :type col: Optional[int]
        :return: The constructed assert statement.
        :rtype: StatementAggregate
        '''

        # Store the assertion and the optional message.
        return StatementAggregate(
            kind=StatementKind.ASSERT,
            expr=expr,
            init_expr=msg,
            lineno=lineno,
            col=col,
        )

    # * method: new_pass_stmt (static)
    @staticmethod
    def new_pass_stmt(
        lineno: Optional[int] = None,
        col: Optional[int] = None,
    ) -> 'StatementAggregate':
        '''
        Create a pass statement.

        :param lineno: The optional source line.
        :type lineno: Optional[int]
        :param col: The optional 0-based column.
        :type col: Optional[int]
        :return: The constructed pass statement.
        :rtype: StatementAggregate
        '''

        # Build a pass statement at the given span.
        return StatementAggregate(
            kind=StatementKind.PASS,
            lineno=lineno,
            col=col,
        )

    # * method: new_continue_stmt (static)
    @staticmethod
    def new_continue_stmt(
        lineno: Optional[int] = None,
        col: Optional[int] = None,
    ) -> 'StatementAggregate':
        '''
        Create a continue statement.

        :param lineno: The optional source line.
        :type lineno: Optional[int]
        :param col: The optional 0-based column.
        :type col: Optional[int]
        :return: The constructed continue statement.
        :rtype: StatementAggregate
        '''

        # Build a continue statement at the given span.
        return StatementAggregate(
            kind=StatementKind.CONTINUE,
            lineno=lineno,
            col=col,
        )

    # * method: new_break_stmt (static)
    @staticmethod
    def new_break_stmt(
        lineno: Optional[int] = None,
        col: Optional[int] = None,
    ) -> 'StatementAggregate':
        '''
        Create a break statement.

        :param lineno: The optional source line.
        :type lineno: Optional[int]
        :param col: The optional 0-based column.
        :type col: Optional[int]
        :return: The constructed break statement.
        :rtype: StatementAggregate
        '''

        # Build a break statement at the given span.
        return StatementAggregate(
            kind=StatementKind.BREAK,
            lineno=lineno,
            col=col,
        )

    # * method: new_del_stmt (static)
    @staticmethod
    def new_del_stmt(
        expr: Optional[ExpressionAggregate],
        lineno: Optional[int] = None,
        col: Optional[int] = None,
    ) -> 'StatementAggregate':
        '''
        Create a del statement.

        :param expr: The deleted expression.
        :type expr: Optional[ExpressionAggregate]
        :param lineno: The optional source line.
        :type lineno: Optional[int]
        :param col: The optional 0-based column.
        :type col: Optional[int]
        :return: The constructed del statement.
        :rtype: StatementAggregate
        '''

        # Store the deleted expression.
        return StatementAggregate(
            kind=StatementKind.DEL,
            expr=expr,
            lineno=lineno,
            col=col,
        )

    # * method: new_return_stmt (static)
    @staticmethod
    def new_return_stmt(
        return_expr: Optional[ExpressionAggregate] = None,
        lineno: Optional[int] = None,
        col: Optional[int] = None,
    ) -> 'StatementAggregate':
        '''
        Create a return statement.

        :param return_expr: The optional return expression.
        :type return_expr: Optional[ExpressionAggregate]
        :param lineno: The optional source line.
        :type lineno: Optional[int]
        :param col: The optional 0-based column.
        :type col: Optional[int]
        :return: The constructed return statement.
        :rtype: StatementAggregate
        '''

        # Store the optional return expression.
        return StatementAggregate(
            kind=StatementKind.RETURN,
            expr=return_expr,
            lineno=lineno,
            col=col,
        )
