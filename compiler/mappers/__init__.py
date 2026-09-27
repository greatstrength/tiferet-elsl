"""Compiler Mappers Exports"""

# *** exports

# ** app
from .lexer import TokenAggregate, TokenAggregate as Tok
from .ast import (
    TypeAggregate,
    TypeAggregate as Type,
    ParamListAggregate,
    ParamListAggregate as ParamList,
    DeclarationAggregate,
    DeclarationAggregate as Decl,
    ExpressionAggregate,
    ExpressionAggregate as Expr,
    StatementAggregate,
    StatementAggregate as Stmt,
)
from ..domain.ast import (
    Declaration,
    Statement,
    Expression,
    ExprKind,
    Type as TypeModel,
    ParamList as ParamListModel,
)
from .artifact import (
    ArtifactDeclarationAggregate,
    ArtifactDeclarationAggregate as ArtifactDecl,
    ArtifactStatementAggregate,
    ArtifactStatementAggregate as ArtifactStmt,
    SnippetStatementAggregate,
    SnippetStatementAggregate as SnippetStmt,
)
from ..domain.artifact import ArtifactDeclaration
from .semantic import ScopeAggregate, ScopeAggregate as SymbolScope
from ..domain.semantic import (
    SYMBOL_KIND_ATTRIBUTE,
    SYMBOL_KIND_CLASS_DEF,
    SYMBOL_KIND_IMPORT,
    SYMBOL_KIND_METHOD,
    SYMBOL_KIND_MODULE,
    SYMBOL_KIND_PARAMETER,
    SYMBOL_KIND_VARIABLE,
)
