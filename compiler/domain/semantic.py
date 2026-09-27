"""Tiferet Compiler Semantic Analysis Domain Objects"""

# *** imports

# ** core
from typing import Dict, List, Literal, Optional

# ** infra
from pydantic import Field

# ** app
from tiferet.domain.core import DomainObject

# *** constants

# ** constant: symbol_kind_module
SYMBOL_KIND_MODULE = 'module'

# ** constant: symbol_kind_import
SYMBOL_KIND_IMPORT = 'import'

# ** constant: symbol_kind_class_def
SYMBOL_KIND_CLASS_DEF = 'class_def'

# ** constant: symbol_kind_method
SYMBOL_KIND_METHOD = 'method'

# ** constant: symbol_kind_attribute
SYMBOL_KIND_ATTRIBUTE = 'attribute'

# ** constant: symbol_kind_parameter
SYMBOL_KIND_PARAMETER = 'parameter'

# ** constant: symbol_kind_variable
SYMBOL_KIND_VARIABLE = 'variable'

# *** models

# ** model: symbol
class Symbol(DomainObject):
    '''
    A named entity in the symbol table (import, class, method, attribute, parameter, or variable).

    It records what a file defines and where that definition lives, so later
    resolution can look a name up without walking the source again.
    '''

    # * attribute: name
    name: str = Field(
        ...,
        description='Symbol name.',
    )

    # * attribute: kind
    kind: Literal[
        'module',
        'import',
        'class_def',
        'method',
        'attribute',
        'parameter',
        'variable',
    ] = Field(
        ...,
        description='What the symbol represents.',
    )

    # * attribute: type_annotation
    type_annotation: Optional[str] = Field(
        None,
        description='Lightweight type hint string; recorded, not checked here.',
    )

    # * attribute: scope_path
    scope_path: str = Field(
        ...,
        description='Fully qualified defining scope (e.g. `module`, `module.Ping.execute`).',
    )

    # * attribute: source_module
    source_module: Optional[str] = Field(
        None,
        description='For imports: module path (e.g. `.settings`, `typing`).',
    )

# ** model: scope
class Scope(DomainObject):
    '''
    A lexical scope (module, class, or method) identified by a dotted path.

    It groups the symbols defined at that path. Artifact groups, sections,
    members, and snippets are not scopes, and this model does not create them.
    '''

    # * attribute: name
    name: str = Field(
        ...,
        description='Scope segment (`module`, `Ping`, `execute`).',
    )

    # * attribute: kind
    kind: Literal[
        'module',
        'import',
        'class_def',
        'method',
        'attribute',
        'parameter',
        'variable',
    ] = Field(
        ...,
        description='Scope kind (`module`, `class_def`, or `method`).',
    )

    # * attribute: path
    path: str = Field(
        ...,
        description='Fully qualified path (e.g. `module.Ping.execute`).',
    )

    # * attribute: symbols
    symbols: Dict[str, Symbol] = Field(
        default_factory=dict,
        description='Name to `Symbol`.',
    )

    # * attribute: children
    children: Dict[str, str] = Field(
        default_factory=dict,
        description='Name to child scope path.',
    )

    # * attribute: parent_path
    parent_path: Optional[str] = Field(
        None,
        description='Parent scope path; `None` for module.',
    )

# ** model: resolved_name
class ResolvedName(DomainObject):
    '''
    A name reference that resolved to a defining scope.

    It keeps both where the name was used and where it was defined, so later
    checks can cite the binding without searching again.
    '''

    # * attribute: name
    name: str = Field(
        ...,
        description='Name that resolved.',
    )

    # * attribute: scope_path
    scope_path: str = Field(
        ...,
        description='Scope where the reference was encountered.',
    )

    # * attribute: resolved_to
    resolved_to: str = Field(
        ...,
        description='Scope path of the definition.',
    )

# ** model: unresolved_name
class UnresolvedName(DomainObject):
    '''
    A name reference that did not resolve to a definition.

    Failed lookups stay on the result so conformance can report them instead
    of stopping at the first miss.
    '''

    # * attribute: name
    name: str = Field(
        ...,
        description='Name that did not resolve.',
    )

    # * attribute: scope_path
    scope_path: str = Field(
        ...,
        description='Scope where the reference was encountered.',
    )

# ** model: resolution_result
class ResolutionResult(DomainObject):
    '''
    The collected outcome of looking names up against the symbol table.

    Successful and failed lookups stay together so a caller can inspect both
    without a second pass.
    '''

    # * attribute: resolved
    resolved: List[ResolvedName] = Field(
        default_factory=list,
        description='Successful lookups.',
    )

    # * attribute: unresolved
    unresolved: List[UnresolvedName] = Field(
        default_factory=list,
        description='Failed lookups.',
    )
