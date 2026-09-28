"""Tiferet Compiler AST Transfer Objects"""

# *** imports

# ** core
from typing import List, Optional

# ** infra
from tiferet.mappers import TransferObject

# ** app
from ..domain.ast import (
    Expression,
    ParamList,
    Statement,
    StatementKind,
    Type,
)
from ..domain.artifact import (
    ArtifactDeclaration,
    SnippetStatement,
)
from .ast import (
    DeclarationAggregate,
    ParamListAggregate,
    StatementAggregate,
    TypeAggregate,
)
from .artifact import (
    ArtifactDeclarationAggregate,
    ArtifactStatementAggregate,
    SnippetStatementAggregate,
)

# *** functions

# ** function: chain_from_models
def _chain_from_models(
    transfer_cls: type,
    models: List,
) -> Optional[TransferObject]:
    '''
    Link domain models into a ``.next`` chain of transfer objects.

    :param transfer_cls: The transfer class to build for each model.
    :type transfer_cls: type
    :param models: The runtime list, or None.
    :type models: List
    :return: The chain head, or None when the list is empty.
    :rtype: Optional[TransferObject]
    '''

    # Walk the list, linking each node to the previous one.
    head = None
    prev = None
    for model in models or []:
        node = transfer_cls.from_model(model)
        if prev is None:
            head = node
        else:
            prev.next = node
        prev = node

    # Return the head, or None when nothing was linked.
    return head

# ** function: chain_to_models
def _chain_to_models(head: Optional[TransferObject]) -> List:
    '''
    Walk a ``.next`` chain back into a runtime list.

    :param head: The chain head, or None.
    :type head: Optional[TransferObject]
    :return: Mapped models, or an empty list when the head is missing.
    :rtype: List
    '''

    # Append each mapped node until the chain ends.
    models = []
    node = head
    while node is not None:
        models.append(node.map())
        node = node.next

    # Return the restored list.
    return models

# *** mappers

# ** mapper: type_transfer_object
class TypeTransferObject(Type, TransferObject):
    '''
    Transfer object for AST Type nodes.

    Persistence stores function parameters as a ``.next`` chain while runtime
    types keep them in a list.
    '''

    # * attribute: subtype
    subtype: Optional['TypeTransferObject'] = None

    # * attribute: return_type
    return_type: Optional['TypeTransferObject'] = None

    # * attribute: params
    params: Optional['ParamListTransferObject'] = None

    # * method: from_model (classmethod)
    @classmethod
    def from_model(cls, model: Type, **overrides) -> 'TypeTransferObject':
        '''
        Create a type transfer object from a type model.

        :param model: The type domain object or aggregate.
        :type model: Type
        :param overrides: Additional field overrides.
        :type overrides: dict
        :return: The constructed type transfer object.
        :rtype: TypeTransferObject
        '''

        # Copy scalar fields and convert nested types and the parameter list.
        data = dict(
            kind=model.kind,
            name=model.name,
            subtype=cls.from_model(model.subtype) if model.subtype else None,
            return_type=cls.from_model(model.return_type) if model.return_type else None,
            params=_chain_from_models(ParamListTransferObject, model.params),
        )
        data.update(overrides)

        # Construct the transfer object.
        return cls(**data)

    # * method: map
    def map(self, **overrides) -> TypeAggregate:
        '''
        Map this type transfer object to a type aggregate.

        :param overrides: Additional field overrides.
        :type overrides: dict
        :return: The mapped type aggregate.
        :rtype: TypeAggregate
        '''

        # Restore nested types and the parameter list.
        data = dict(
            kind=self.kind,
            name=self.name,
            subtype=self.subtype.map() if self.subtype else None,
            return_type=self.return_type.map() if self.return_type else None,
            params=_chain_to_models(self.params),
        )
        data.update(overrides)

        # Construct the runtime aggregate.
        return TypeAggregate(**data)

# ** mapper: param_list_transfer_object
class ParamListTransferObject(ParamList, TransferObject):
    '''
    Transfer object for AST parameter nodes.

    Parameters persist as a ``.next`` chain. The chain builder sets ``.next``;
    this class does not.
    '''

    # * attribute: type
    type: Optional[TypeTransferObject] = None

    # * attribute: default
    default: Optional[Expression] = None

    # * attribute: next
    next: Optional['ParamListTransferObject'] = None

    # * method: from_model (classmethod)
    @classmethod
    def from_model(
        cls,
        model: ParamList,
        **overrides,
    ) -> 'ParamListTransferObject':
        '''
        Create a parameter transfer object from a parameter model.

        :param model: The parameter domain object or aggregate.
        :type model: ParamList
        :param overrides: Additional field overrides.
        :type overrides: dict
        :return: The constructed parameter transfer object.
        :rtype: ParamListTransferObject
        '''

        # Copy the parameter fields. The chain builder sets ``.next``.
        data = dict(
            name=model.name,
            required=model.required,
            default=model.default,
            type=TypeTransferObject.from_model(model.type) if model.type else None,
        )
        data.update(overrides)

        # Construct the transfer object.
        return cls(**data)

    # * method: map
    def map(self, **overrides) -> ParamListAggregate:
        '''
        Map this parameter transfer object to a parameter aggregate.

        :param overrides: Additional field overrides.
        :type overrides: dict
        :return: The mapped parameter aggregate.
        :rtype: ParamListAggregate
        '''

        # Restore the parameter without the persistence link.
        data = dict(
            name=self.name,
            type=self.type.map() if self.type else None,
            required=self.required,
            default=self.default,
        )
        data.update(overrides)

        # Construct the runtime aggregate.
        return ParamListAggregate(**data)

# ** mapper: declaration_transfer_object
class DeclarationTransferObject(ArtifactDeclaration, TransferObject):
    '''
    Transfer object for AST declaration nodes.

    Extends the artifact declaration so artifact fields survive persistence.
    Body statements persist as a ``.next`` chain.
    '''

    # * attribute: type
    type: Optional[TypeTransferObject] = None

    # * attribute: value
    value: Optional[Expression] = None

    # * attribute: code
    code: Optional['StatementTransferObject'] = None

    # * method: from_model (classmethod)
    @classmethod
    def from_model(
        cls,
        model: ArtifactDeclaration,
        **overrides,
    ) -> 'DeclarationTransferObject':
        '''
        Create a declaration transfer object from a declaration model.

        :param model: The declaration domain object or aggregate.
        :type model: ArtifactDeclaration
        :param overrides: Additional field overrides.
        :type overrides: dict
        :return: The constructed declaration transfer object.
        :rtype: DeclarationTransferObject
        '''

        # Copy declaration fields and convert the type and body chain.
        data = dict(
            name=model.name,
            doc_string=model.doc_string,
            value=model.value,
            lineno=model.lineno,
            col=model.col,
            type=TypeTransferObject.from_model(model.type) if model.type else None,
            metadata=getattr(model, 'metadata', {}) or {},
            code=_chain_from_models(StatementTransferObject, model.code),
            artifact_type=getattr(model, 'artifact_type', None),
            artifact_role=getattr(model, 'artifact_role', None),
            artifact_qualifier=getattr(model, 'artifact_qualifier', None),
            annotations=getattr(model, 'annotations', None),
            guide_path=getattr(model, 'guide_path', None),
        )
        data.update(overrides)

        # Construct the transfer object.
        return cls(**data)

    # * method: map
    def map(self, **overrides) -> DeclarationAggregate:
        '''
        Map this declaration transfer object to a declaration aggregate.

        Artifact fields select the artifact aggregate. Otherwise the plain
        declaration aggregate is returned.

        :param overrides: Additional field overrides.
        :type overrides: dict
        :return: The mapped declaration aggregate.
        :rtype: DeclarationAggregate
        '''

        # Restore fields shared by plain and artifact declarations.
        common = dict(
            name=self.name,
            type=self.type.map() if self.type else None,
            metadata=self.metadata,
            doc_string=self.doc_string,
            value=self.value,
            code=_chain_to_models(self.code),
            lineno=self.lineno,
            col=self.col,
        )
        common.update(overrides)

        # Keep artifact fields only when this node is an artifact declaration.
        if self.artifact_type is not None or self.artifact_role is not None:
            return ArtifactDeclarationAggregate(
                artifact_type=self.artifact_type,
                artifact_role=self.artifact_role,
                artifact_qualifier=self.artifact_qualifier,
                annotations=self.annotations,
                guide_path=self.guide_path,
                **common,
            )

        # Return the plain declaration aggregate.
        return DeclarationAggregate(**common)

# ** mapper: statement_transfer_object
class StatementTransferObject(SnippetStatement, TransferObject):
    '''
    Transfer object for AST statement nodes.

    Extends the snippet statement so leading comments persist. Bodies and the
    statement sequence itself persist as ``.next`` chains.
    '''

    # * attribute: decl
    decl: Optional[DeclarationTransferObject] = None

    # * attribute: body
    body: Optional['StatementTransferObject'] = None

    # * attribute: else_body
    else_body: Optional['StatementTransferObject'] = None

    # * attribute: finally_body
    finally_body: Optional['StatementTransferObject'] = None

    # * attribute: comments
    comments: Optional['StatementTransferObject'] = None

    # * attribute: next
    next: Optional['StatementTransferObject'] = None

    # * method: from_model (classmethod)
    @classmethod
    def from_model(
        cls,
        model: Statement,
        **overrides,
    ) -> 'StatementTransferObject':
        '''
        Create a statement transfer object from a statement model.

        :param model: The statement domain object or aggregate.
        :type model: Statement
        :param overrides: Additional field overrides.
        :type overrides: dict
        :return: The constructed statement transfer object.
        :rtype: StatementTransferObject
        '''

        # Copy statement fields and convert nested chains.
        data = dict(
            kind=model.kind,
            lineno=model.lineno,
            col=model.col,
            init_expr=model.init_expr,
            expr=model.expr,
            next_expr=model.next_expr,
            decl=DeclarationTransferObject.from_model(model.decl) if model.decl else None,
            body=_chain_from_models(cls, model.body),
            else_body=_chain_from_models(cls, model.else_body),
            finally_body=_chain_from_models(
                cls,
                getattr(model, 'finally_body', []),
            ),
            comments=_chain_from_models(
                cls,
                getattr(model, 'comments', []),
            ),
        )
        data.update(overrides)

        # Construct the transfer object. The chain builder sets ``.next``.
        return cls(**data)

    # * method: map
    def map(self, **overrides) -> StatementAggregate:
        '''
        Map this statement transfer object to a statement aggregate.

        Snippet and artifact kinds select their aggregates. Every other kind
        maps to the plain statement aggregate.

        :param overrides: Additional field overrides.
        :type overrides: dict
        :return: The mapped statement aggregate.
        :rtype: StatementAggregate
        '''

        # Restore fields shared by every statement kind.
        common = dict(
            kind=self.kind,
            lineno=self.lineno,
            col=self.col,
            decl=self.decl.map() if self.decl else None,
            init_expr=self.init_expr,
            expr=self.expr,
            next_expr=self.next_expr,
            body=_chain_to_models(self.body),
            else_body=_chain_to_models(self.else_body),
            finally_body=_chain_to_models(self.finally_body),
        )
        common.update(overrides)

        # Keep comments only on snippet statements.
        if self.kind == StatementKind.SNIPPET:
            return SnippetStatementAggregate(
                comments=_chain_to_models(self.comments),
                **common,
            )

        # Artifact statements use the artifact aggregate.
        if self.kind == StatementKind.ARTIFACT:
            return ArtifactStatementAggregate(**common)

        # Return the plain statement aggregate.
        return StatementAggregate(**common)

# *** model rebuilds

# Resolve forward references once every transfer object exists.
TypeTransferObject.model_rebuild()
ParamListTransferObject.model_rebuild()
DeclarationTransferObject.model_rebuild()
StatementTransferObject.model_rebuild()
