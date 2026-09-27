"""Domain – Artifact Domain Objects Tests"""

# *** imports

# ** app
from compiler.domain import (
    ArtifactDeclaration,
    ArtifactStatement,
    Declaration,
    SnippetStatement,
    Statement,
    StatementKind,
    Type,
    TypeKind,
)

# *** tests

# ** test: artifact_declaration_instantiation
def test_artifact_declaration_instantiation() -> None:
    '''
    Test that a group header stores its artifact fields without member or section flags.
    '''

    # A bare group marker stores the given fields.
    declaration = ArtifactDeclaration(
        name='group',
        artifact_type='***',
        artifact_role='attribute',
        artifact_qualifier='ids',
    )
    assert declaration.name == 'group'
    assert declaration.artifact_type == '***'
    assert declaration.artifact_role == 'attribute'
    assert declaration.artifact_qualifier == 'ids'

    # A bare group is neither an artifact member nor a section.
    assert declaration.is_artifact_member is False
    assert declaration.section_keyword is None

# ** test: artifact_declaration_member
def test_artifact_declaration_member() -> None:
    '''
    Test that an artifact member with a method role sets is_artifact_member.
    '''

    # A method member is an artifact member.
    declaration = ArtifactDeclaration(
        name='run',
        artifact_type='ARTIFACT_MEMBER',
        artifact_role='method',
    )
    assert declaration.artifact_type == 'ARTIFACT_MEMBER'
    assert declaration.artifact_role == 'method'
    assert declaration.is_artifact_member is True

# ** test: artifact_declaration_with_annotations
def test_artifact_declaration_with_annotations() -> None:
    '''
    Test that an annotations list persists.
    '''

    # Structured notes persist as given.
    notes = [{'kind': 'TODO', 'text': 'later'}]
    declaration = ArtifactDeclaration(name='run', annotations=notes)
    assert declaration.annotations == notes

# ** test: artifact_declaration_inherits_declaration_fields
def test_artifact_declaration_inherits_declaration_fields() -> None:
    '''
    Test that name, type, and code still work on an artifact declaration.
    '''

    # Inherited declaration fields persist, including derived class classification.
    body = Statement(kind=StatementKind.PASS)
    declaration = ArtifactDeclaration(
        name='Foo',
        type=Type(kind=TypeKind.CLASS, name='Foo'),
        code=[body],
    )
    assert declaration.name == 'Foo'
    assert declaration.type is not None
    assert declaration.type.kind == TypeKind.CLASS
    assert declaration.code == [body]
    assert declaration.is_class is True
    assert isinstance(declaration, Declaration)

# ** test: artifact_declaration_with_guide_path
def test_artifact_declaration_with_guide_path() -> None:
    '''
    Test that guide_path persists.
    '''

    # The see-target persists.
    declaration = ArtifactDeclaration(name='run', guide_path='docs/guides/domain/ast.md#run')
    assert declaration.guide_path == 'docs/guides/domain/ast.md#run'

# ** test: artifact_declaration_is_artifact_member
def test_artifact_declaration_is_artifact_member() -> None:
    '''
    Test that the derived member flag matches ARTIFACT_MEMBER and not a section marker.
    '''

    # Only the member marker sets the flag.
    member = ArtifactDeclaration(name='run', artifact_type='ARTIFACT_MEMBER')
    section = ArtifactDeclaration(name='events', artifact_type='** event')
    assert member.is_artifact_member is True
    assert section.is_artifact_member is False

# ** test: artifact_declaration_section_keyword
def test_artifact_declaration_section_keyword() -> None:
    '''
    Test section keyword derivation for an event marker and bare markers.
    '''

    # A keyword follows the marker; bare markers have none.
    assert ArtifactDeclaration(name='events', artifact_type='** event').section_keyword == 'event'
    assert ArtifactDeclaration(name='group', artifact_type='***').section_keyword is None
    assert ArtifactDeclaration(name='group', artifact_type='**').section_keyword is None

# ** test: artifact_declaration_is_section
def test_artifact_declaration_is_section() -> None:
    '''
    Test that is_section is true only when a section keyword is present.
    '''

    # A keyword makes a section; bare markers do not.
    assert ArtifactDeclaration(name='events', artifact_type='** event').is_section is True
    assert ArtifactDeclaration(name='group', artifact_type='***').is_section is False
    assert ArtifactDeclaration(name='group', artifact_type='**').is_section is False

# ** test: artifact_declaration_qualifier
def test_artifact_declaration_qualifier() -> None:
    '''
    Test that an artifact qualifier persists and defaults to None.
    '''

    # An explicit qualifier persists.
    assert ArtifactDeclaration(name='ids', artifact_qualifier='ids').artifact_qualifier == 'ids'

    # The qualifier defaults to None.
    assert ArtifactDeclaration(name='ids').artifact_qualifier is None

# ** test: artifact_declaration_classification_rederives_on_assignment
def test_artifact_declaration_classification_rederives_on_assignment() -> None:
    '''
    Test that assigning artifact_type rederives artifact classification flags.
    '''

    # Start from a section marker.
    declaration = ArtifactDeclaration(name='events', artifact_type='** event')
    assert declaration.is_section is True
    assert declaration.section_keyword == 'event'
    assert declaration.is_artifact_member is False

    # Assigning the member marker rederives the flags.
    declaration.artifact_type = 'ARTIFACT_MEMBER'
    assert declaration.is_artifact_member is True
    assert declaration.section_keyword is None
    assert declaration.is_section is False

# ** test: artifact_statement_instantiation
def test_artifact_statement_instantiation() -> None:
    '''
    Test that an artifact statement constructs with an artifact kind.
    '''

    # The marker constructs as an artifact statement.
    statement = ArtifactStatement(kind=StatementKind.ARTIFACT)
    assert statement.kind == StatementKind.ARTIFACT
    assert statement.is_artifact is True

# ** test: artifact_statement_is_statement_subtype
def test_artifact_statement_is_statement_subtype() -> None:
    '''
    Test that an artifact statement is a Statement.
    '''

    # The marker is a statement subtype.
    assert isinstance(ArtifactStatement(kind=StatementKind.ARTIFACT), Statement)

# ** test: snippet_statement_instantiation
def test_snippet_statement_instantiation() -> None:
    '''
    Test that snippet comments stay separate from the executable body.
    '''

    # Comments and body are distinct lists.
    comment = Statement(kind=StatementKind.COMMENT)
    body = Statement(kind=StatementKind.PASS)
    snippet = SnippetStatement(
        kind=StatementKind.SNIPPET,
        comments=[comment],
        body=[body],
    )
    assert snippet.comments == [comment]
    assert snippet.body == [body]
    assert comment not in snippet.body

# ** test: snippet_statement_no_comments
def test_snippet_statement_no_comments() -> None:
    '''
    Test that a snippet defaults comments to an empty list.
    '''

    # Comments default to an empty list.
    assert SnippetStatement(kind=StatementKind.SNIPPET).comments == []

# ** test: snippet_statement_is_statement_subtype
def test_snippet_statement_is_statement_subtype() -> None:
    '''
    Test that a snippet statement is a Statement.
    '''

    # The snippet is a statement subtype.
    assert isinstance(SnippetStatement(kind=StatementKind.SNIPPET), Statement)
