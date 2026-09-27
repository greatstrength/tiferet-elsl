"""Tiferet Compiler Artifact Mapper Objects"""

# *** imports

# ** core
from typing import Optional

# ** app
from ..domain.artifact import (
    ArtifactDeclaration,
    ArtifactStatement,
    SnippetStatement,
)
from ..domain.ast import StatementKind
from .ast import (
    TypeAggregate,
    StatementAggregate,
    _as_list,
)

# *** mappers

# ** mapper: artifact_declaration_aggregate
class ArtifactDeclarationAggregate(ArtifactDeclaration):
    '''
    Mutable Tiferet artifact declaration aggregate.

    Parser actions build group headers, sections, and members through these
    factories instead of assigning domain fields ad hoc.
    '''

    # * method: new_artifact_decl (static)
    @staticmethod
    def new_artifact_decl(
        name: str,
        artifact_type: str,
        qualifier: Optional[str] = None,
        lineno: Optional[int] = None,
        col: Optional[int] = None,
    ) -> 'ArtifactDeclarationAggregate':
        '''
        Create a group or section artifact declaration.

        Tier-1 group headers use ``artifact_type='***'``. Tier-2 sections use
        values such as ``'** event'`` or ``'**'``.

        :param name: The artifact name.
        :type name: str
        :param artifact_type: The tier marker.
        :type artifact_type: str
        :param qualifier: The optional parenthetical qualifier.
        :type qualifier: Optional[str]
        :param lineno: The optional source line.
        :type lineno: Optional[int]
        :param col: The optional 0-based column.
        :type col: Optional[int]
        :return: The constructed artifact declaration.
        :rtype: ArtifactDeclarationAggregate
        '''

        # Build the header without a member role.
        return ArtifactDeclarationAggregate(
            name=name,
            type=TypeAggregate.new_artifact_type(),
            artifact_type=artifact_type,
            artifact_qualifier=qualifier,
            lineno=lineno,
            col=col,
        )

    # * method: new_member_decl (static)
    @staticmethod
    def new_member_decl(
        name: str,
        member_body: Optional[StatementAggregate] = None,
        annots: Optional[list] = None,
        qualifier: Optional[str] = None,
        lineno: Optional[int] = None,
        col: Optional[int] = None,
    ) -> 'ArtifactDeclarationAggregate':
        '''
        Create an artifact member declaration.

        ``name`` is the member role: ``'attribute'``, ``'init'``, or
        ``'method'``.

        :param name: The member role and declaration name.
        :type name: str
        :param member_body: A statement, a statement list, or None.
        :type member_body: Optional[StatementAggregate]
        :param annots: Optional structured SEE, OBSOLETE, or TODO notes.
        :type annots: Optional[list]
        :param qualifier: The optional parenthetical qualifier.
        :type qualifier: Optional[str]
        :param lineno: The optional source line.
        :type lineno: Optional[int]
        :param col: The optional 0-based column.
        :type col: Optional[int]
        :return: The constructed member declaration.
        :rtype: ArtifactDeclarationAggregate
        '''

        # Build the member header from the role name.
        aggr = ArtifactDeclarationAggregate(
            name=name,
            type=TypeAggregate.new_artifact_type(),
            artifact_type='ARTIFACT_MEMBER',
            artifact_role=name,
            artifact_qualifier=qualifier,
            annotations=annots,
            lineno=lineno,
            col=col,
        )

        # Keep the body on code, including when it is missing.
        aggr.code = _as_list(member_body)

        # Return the member declaration.
        return aggr

# ** mapper: artifact_statement_aggregate
class ArtifactStatementAggregate(ArtifactStatement):
    '''
    Mutable Tiferet artifact statement aggregate for group and section nodes.

    Parser actions wrap a section header and body through this factory instead
    of assigning domain fields ad hoc.
    '''

    # * method: new_artifact_stmt (static)
    @staticmethod
    def new_artifact_stmt(
        section_header: ArtifactDeclarationAggregate,
        section_body: Optional[StatementAggregate],
    ) -> 'ArtifactStatementAggregate':
        '''
        Create an artifact statement for a group or section.

        :param section_header: The group or section declaration.
        :type section_header: ArtifactDeclarationAggregate
        :param section_body: A statement, a statement list, or None.
        :type section_body: Optional[StatementAggregate]
        :return: The constructed artifact statement.
        :rtype: ArtifactStatementAggregate
        '''

        # Store the header and normalize the section body.
        return ArtifactStatementAggregate(
            kind=StatementKind.ARTIFACT,
            decl=section_header,
            body=_as_list(section_body),
        )

# ** mapper: snippet_statement_aggregate
class SnippetStatementAggregate(SnippetStatement):
    '''
    Mutable Tiferet snippet statement aggregate with comments kept separate from executable code.

    Leading comments stay on their own list so the body remains the executable
    statements.
    '''

    # * method: new_snippet_stmt (static)
    @staticmethod
    def new_snippet_stmt(
        comments: Optional[StatementAggregate] = None,
        code: Optional[StatementAggregate] = None,
    ) -> 'SnippetStatementAggregate':
        '''
        Create a snippet statement.

        :param comments: A comment statement, a comment list, or None.
        :type comments: Optional[StatementAggregate]
        :param code: An executable statement, a statement list, or None.
        :type code: Optional[StatementAggregate]
        :return: The constructed snippet statement.
        :rtype: SnippetStatementAggregate
        '''

        # Keep comments and executable code on separate lists.
        return SnippetStatementAggregate(
            kind=StatementKind.SNIPPET,
            comments=_as_list(comments),
            body=_as_list(code),
        )
