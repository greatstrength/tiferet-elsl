"""Mappers – AST Transfer Object Tests"""

# *** imports

# ** core
import pytest

# ** app
from .. import (
    ArtifactDecl,
    ArtifactStmt,
    Decl,
    Expr,
    ParamList,
    SnippetStmt,
    Stmt,
    Type,
)
from ..transfer import DeclarationTransferObject

# *** fixtures

# ** fixture: sample_module
@pytest.fixture
def sample_module() -> Decl:
    '''
    Build a list-based module AST for transfer round-trips.

    :return: A module whose execute parameters and bodies are Python lists.
    :rtype: Decl
    '''

    # A required self parameter and a variadic kwargs parameter.
    self_param = ParamList.new(
        'self',
        type=Type.new_unknown_type(),
    )
    kwargs = ParamList.new_kwargs_param()

    # The execute body is a snippet: a comment, then a string return.
    snippet = SnippetStmt.new_snippet_stmt(
        comments=Stmt.new_comment_stmt(Expr.new_comment_expr('return pong')),
        code=Stmt.new_return_stmt(Expr.new_name_or_literal_expr("'pong'")),
    )
    execute = Decl.new_func_decl(
        'execute',
        type=Type.new_func_type(
            params=[self_param, kwargs],
            return_type=Type.new(kind='str'),
        ),
        body=snippet,
    )

    # Wrap execute as a method member of class Ping.
    method_member = ArtifactDecl.new_member_decl(
        'method',
        member_body=Stmt.new_decl_stmt(execute),
    )
    ping = Decl.new_class_decl(
        name='Ping',
        subclasses=Type.new_class_type(name='DomainEvent'),
        doc_string='A minimal event.',
        members=[Stmt.new_decl_stmt(method_member)],
    )

    # Section '** event' inside group '*** events', then the module.
    section = ArtifactStmt.new_artifact_stmt(
        ArtifactDecl.new_artifact_decl('event', '** event'),
        Stmt.new_decl_stmt(ping),
    )
    events = ArtifactStmt.new_artifact_stmt(
        ArtifactDecl.new_artifact_decl('events', '***'),
        section,
    )
    return Decl.new_module_decl(name='m', code=[events])

# *** tests

# ** test: round_trip_lossless
def test_round_trip_lossless(sample_module: Decl) -> None:
    '''
    Test that a serialized module maps back to the same aggregate dump.

    :param sample_module: The list-based module AST.
    :type sample_module: Decl
    '''

    # Serialize, revalidate, and map back to aggregates.
    primitive = DeclarationTransferObject.from_model(sample_module).to_primitive()
    restored = DeclarationTransferObject.model_validate(primitive).map()

    # The restored dump matches the original, excluding missing values.
    assert restored.model_dump(exclude_none=True) == sample_module.model_dump(
        exclude_none=True,
    )

# ** test: params_serialize_as_next_chain
def test_params_serialize_as_next_chain(sample_module: Decl) -> None:
    '''
    Test that function parameters persist as a ``.next`` chain, not a list.

    :param sample_module: The list-based module AST.
    :type sample_module: Decl
    '''

    # Serialize the module and drill to the execute function type.
    primitive = DeclarationTransferObject.from_model(sample_module).to_primitive()
    execute = (
        primitive['code']['body']['body']['decl']['code']['decl']['code']['decl']
    )
    params = execute['type']['params']

    # The head is self, linked to kwargs. It is not a JSON list.
    assert isinstance(params, dict)
    assert not isinstance(params, list)
    assert params['name'] == 'self'
    assert params['next']['name'] == 'kwargs'

# ** test: map_restores_python_lists
def test_map_restores_python_lists(sample_module: Decl) -> None:
    '''
    Test that mapping restores statement lists and the method member role.

    :param sample_module: The list-based module AST.
    :type sample_module: Decl
    '''

    # Serialize, revalidate, and map back to aggregates.
    primitive = DeclarationTransferObject.from_model(sample_module).to_primitive()
    restored = DeclarationTransferObject.model_validate(primitive).map()

    # The module body is a list, and the class method role survives.
    assert isinstance(restored.code, list)
    ping = restored.code[0].body[0].body[0].decl
    assert ping.members[0].artifact_role == 'method'
