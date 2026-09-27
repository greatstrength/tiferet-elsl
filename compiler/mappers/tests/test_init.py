"""Mappers – Package Facade Tests"""

# *** imports

# ** app
import compiler.domain.ast as domain_ast
import compiler.mappers as mappers
from compiler.mappers import Decl, Expr, Stmt

# *** tests

# ** test: mappers_re_export_domain_node_types
def test_mappers_re_export_domain_node_types() -> None:
    '''
    Test that mappers re-export the domain node types.
    '''

    # Domain node types are the same objects as the domain module.
    assert mappers.Declaration is domain_ast.Declaration
    assert mappers.Statement is domain_ast.Statement
    assert mappers.Expression is domain_ast.Expression

# ** test: mappers_domain_types_are_not_aggregates
def test_mappers_domain_types_are_not_aggregates() -> None:
    '''
    Test that domain node types are distinct from their aggregates.
    '''

    # Aliases point at the aggregates, which subclass the domain types.
    assert Decl is mappers.DeclarationAggregate
    assert Expr is mappers.ExpressionAggregate
    assert Stmt is mappers.StatementAggregate
    assert mappers.Declaration is not mappers.DeclarationAggregate
    assert mappers.Statement is not mappers.StatementAggregate
    assert mappers.Expression is not mappers.ExpressionAggregate
    assert issubclass(mappers.DeclarationAggregate, domain_ast.Declaration)
    assert issubclass(mappers.StatementAggregate, domain_ast.Statement)
    assert issubclass(mappers.ExpressionAggregate, domain_ast.Expression)
