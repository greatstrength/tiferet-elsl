"""Mappers – Artifact Aggregate Tests"""

# *** imports

# ** app
from ...domain.ast import StatementKind, TypeKind
from ..artifact import (
    ArtifactDeclarationAggregate,
    ArtifactStatementAggregate,
    SnippetStatementAggregate,
)
from ..ast import DeclarationAggregate, StatementAggregate

# *** tests

# ** test: new_artifact_decl_group
def test_new_artifact_decl_group() -> None:
    '''
    Test that a group header stores the tier marker and is not a member.
    '''

    # A tier-1 header uses the bare group marker.
    declaration = ArtifactDeclarationAggregate.new_artifact_decl('imports', '***')

    # The header is an artifact type without a member role.
    assert declaration.name == 'imports'
    assert declaration.artifact_type == '***'
    assert declaration.artifact_role is None
    assert declaration.type.kind == TypeKind.ARTIFACT
    assert not declaration.is_artifact_member

# ** test: new_artifact_decl_section
def test_new_artifact_decl_section() -> None:
    '''
    Test that a section header stores its marker and is not a member.
    '''

    # A tier-2 header carries the section marker.
    declaration = ArtifactDeclarationAggregate.new_artifact_decl('ping', '** event')

    # The section marker does not make a member.
    assert declaration.artifact_type == '** event'
    assert not declaration.is_artifact_member

# ** test: new_member_decl
def test_new_member_decl() -> None:
    '''
    Test that a member declaration stores the member marker and role.
    '''

    # The name is both the declaration name and the member role.
    declaration = ArtifactDeclarationAggregate.new_member_decl('attribute')

    # The member marker and role are derived from that name.
    assert declaration.name == 'attribute'
    assert declaration.artifact_type == 'ARTIFACT_MEMBER'
    assert declaration.artifact_role == 'attribute'
    assert declaration.is_artifact_member

# ** test: new_member_decl_with_body
def test_new_member_decl_with_body() -> None:
    '''
    Test that a member body is stored as the first code statement.
    '''

    # Attach one statement as the member body.
    body = StatementAggregate.new_expr_stmt(expr=None)
    declaration = ArtifactDeclarationAggregate.new_member_decl(
        'method',
        member_body=body,
    )

    # The body is the first code item.
    assert declaration.code[0] is body

# ** test: new_member_decl_with_annotations
def test_new_member_decl_with_annotations() -> None:
    '''
    Test that member annotations persist.
    '''

    # Structured notes are stored on the member.
    notes = [{'kind': 'TODO', 'text': 'later'}]
    declaration = ArtifactDeclarationAggregate.new_member_decl(
        'attribute',
        annots=notes,
    )

    # The notes persist as given.
    assert declaration.annotations == notes

# ** test: new_member_decl_with_guide_path
def test_new_member_decl_with_guide_path() -> None:
    '''
    Test that a guide path and SEE annotation assigned after construction persist.
    '''

    # Assign the see-target and a SEE note after the factory returns.
    declaration = ArtifactDeclarationAggregate.new_member_decl('method')
    see = {'kind': 'SEE', 'text': 'docs/guides/mappers.md#method'}
    declaration.guide_path = 'docs/guides/mappers.md#method'
    declaration.annotations = [see]

    # Both assignments persist.
    assert declaration.guide_path == 'docs/guides/mappers.md#method'
    assert declaration.annotations == [see]

# ** test: is_artifact_member_false
def test_is_artifact_member_false() -> None:
    '''
    Test that a group header is not an artifact member.
    '''

    # A group header is not a member.
    declaration = ArtifactDeclarationAggregate.new_artifact_decl('imports', '***')
    assert declaration.is_artifact_member is False

# ** test: is_artifact_member_true
def test_is_artifact_member_true() -> None:
    '''
    Test that an init member is an artifact member.
    '''

    # An init role is a member.
    declaration = ArtifactDeclarationAggregate.new_member_decl('init')
    assert declaration.is_artifact_member is True

# ** test: members_single
def test_members_single() -> None:
    '''
    Test that Declaration.members yields the one artifact member in code.
    '''

    # Nest the member in a declaration statement.
    member = ArtifactDeclarationAggregate.new_member_decl('attribute')
    parent = ArtifactDeclarationAggregate.new_artifact_decl('models', '** model')
    parent.code = [StatementAggregate.new_decl_stmt(member)]

    # The body yields that one member.
    assert parent.members == [member]

# ** test: members_chain
def test_members_chain() -> None:
    '''
    Test that Declaration.members yields attribute, init, and method in order.
    '''

    # Nest three members in body order.
    attribute = ArtifactDeclarationAggregate.new_member_decl('attribute')
    init = ArtifactDeclarationAggregate.new_member_decl('init')
    method = ArtifactDeclarationAggregate.new_member_decl('method')
    parent = ArtifactDeclarationAggregate.new_artifact_decl('models', '** model')
    parent.code = [
        StatementAggregate.new_decl_stmt(attribute),
        StatementAggregate.new_decl_stmt(init),
        StatementAggregate.new_decl_stmt(method),
    ]

    # Members follow the body order.
    assert parent.members == [attribute, init, method]

# ** test: members_excludes_non_member
def test_members_excludes_non_member() -> None:
    '''
    Test that a plain declaration in code is omitted from members.
    '''

    # A plain declaration sits beside one member.
    plain = DeclarationAggregate.new_module_decl('plain')
    member = ArtifactDeclarationAggregate.new_member_decl('method')
    parent = ArtifactDeclarationAggregate.new_artifact_decl('models', '** model')
    parent.code = [
        StatementAggregate.new_decl_stmt(plain),
        StatementAggregate.new_decl_stmt(member),
    ]

    # Only the artifact member is yielded.
    assert parent.members == [member]

# ** test: section_keyword_event
def test_section_keyword_event() -> None:
    '''
    Test that an event section marker yields the event keyword.
    '''

    # The keyword follows the section marker.
    declaration = ArtifactDeclarationAggregate.new_artifact_decl('ping', '** event')
    assert declaration.section_keyword == 'event'

# ** test: section_keyword_model
def test_section_keyword_model() -> None:
    '''
    Test that a model section marker yields the model keyword.
    '''

    # The keyword follows the section marker.
    declaration = ArtifactDeclarationAggregate.new_artifact_decl('error', '** model')
    assert declaration.section_keyword == 'model'

# ** test: section_keyword_group_header
def test_section_keyword_group_header() -> None:
    '''
    Test that a group header has no section keyword.
    '''

    # A bare group marker has no keyword.
    declaration = ArtifactDeclarationAggregate.new_artifact_decl('imports', '***')
    assert declaration.section_keyword is None

# ** test: section_keyword_import_section
def test_section_keyword_import_section() -> None:
    '''
    Test that a bare section marker has no section keyword.
    '''

    # A bare tier-2 marker has no keyword.
    declaration = ArtifactDeclarationAggregate.new_artifact_decl('imports', '**')
    assert declaration.section_keyword is None

# ** test: section_keyword_member
def test_section_keyword_member() -> None:
    '''
    Test that a member has no section keyword.
    '''

    # A member marker has no keyword.
    declaration = ArtifactDeclarationAggregate.new_member_decl('attribute')
    assert declaration.section_keyword is None

# ** test: is_section_true
def test_is_section_true() -> None:
    '''
    Test that each legal section keyword yields a section.
    '''

    # Each keyword after the marker is a section.
    keywords = (
        'event',
        'model',
        'context',
        'repo',
        'mapper',
        'util',
        'interface',
        'contract',
        'command',
    )
    for keyword in keywords:
        declaration = ArtifactDeclarationAggregate.new_artifact_decl(
            keyword,
            f'** {keyword}',
        )
        assert declaration.is_section is True

# ** test: is_section_false_group
def test_is_section_false_group() -> None:
    '''
    Test that a group header is not a section.
    '''

    # A group header is not a section.
    declaration = ArtifactDeclarationAggregate.new_artifact_decl('imports', '***')
    assert declaration.is_section is False

# ** test: is_section_false_member
def test_is_section_false_member() -> None:
    '''
    Test that a member is not a section.
    '''

    # A member is not a section.
    declaration = ArtifactDeclarationAggregate.new_member_decl('method')
    assert declaration.is_section is False

# ** test: new_artifact_stmt
def test_new_artifact_stmt() -> None:
    '''
    Test that an artifact statement stores the header and body.
    '''

    # Wrap a header and one body statement.
    header = ArtifactDeclarationAggregate.new_artifact_decl('imports', '***')
    body = StatementAggregate.new_expr_stmt(expr=None)
    statement = ArtifactStatementAggregate.new_artifact_stmt(header, body)

    # The statement kind, header, and body are the given values.
    assert statement.kind == StatementKind.ARTIFACT
    assert statement.decl is header
    assert statement.body[0] is body

# ** test: new_snippet_stmt_with_comments
def test_new_snippet_stmt_with_comments() -> None:
    '''
    Test that snippet comments and code stay on distinct lists.
    '''

    # Keep one comment and one executable statement separate.
    comment = StatementAggregate.new_comment_stmt(comment=None)
    code = StatementAggregate.new_expr_stmt(expr=None)
    snippet = SnippetStatementAggregate.new_snippet_stmt(
        comments=comment,
        code=code,
    )

    # The two lists hold different statements.
    assert snippet.comments[0] is comment
    assert snippet.body[0] is code
    assert snippet.comments[0] is not snippet.body[0]

# ** test: new_snippet_stmt_code_only
def test_new_snippet_stmt_code_only() -> None:
    '''
    Test that omitted snippet comments become an empty list.
    '''

    # Omit comments and keep one executable statement.
    code = StatementAggregate.new_expr_stmt(expr=None)
    snippet = SnippetStatementAggregate.new_snippet_stmt(code=code)

    # Comments default to an empty list.
    assert snippet.comments == []
