"""Tiferet Compiler AST Mapper Objects"""

# *** imports

# ** core
from __future__ import annotations
from typing import List, Optional

# ** app
from ..domain import ParamList, Type, TypeKind

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
