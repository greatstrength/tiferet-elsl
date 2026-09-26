"""Tiferet Compiler Code Generation Domain Objects"""

# *** imports

# ** core
from typing import Any, Dict, List, Optional

# ** infra
from pydantic import Field

# ** app
from tiferet.domain.core import DomainObject

# *** models

# ** model: import_entry
class ImportEntry(DomainObject):
    '''
    One import line in a component envelope: the module path and the symbols
    taken from it, so distillation can record imports without walking source.
    '''

    # * attribute: src
    src: str = Field(
        ...,
        description='Module path (e.g. `tiferet.events`).',
    )

    # * attribute: tgts
    tgts: List[str] = Field(
        default_factory=list,
        description='Imported symbol names.',
    )

# ** model: snippet_data
class SnippetData(DomainObject):
    '''
    A body fragment of leading comments and encoded statements, kept under
    domain field names so later emission can rename keys without this model.
    '''

    # * attribute: comments
    comments: List[str] = Field(
        default_factory=list,
        description='Leading comment lines (hash stripped, trimmed).',
    )

    # * attribute: statements
    statements: List[str] = Field(
        default_factory=list,
        description='Encoded executable statements.',
    )

# ** model: constant_data
class ConstantData(DomainObject):
    '''
    The encoded initializer for one named constant inside a group payload.
    '''

    # * attribute: value
    value: str = Field(
        ...,
        description='Encoded initializer expression.',
    )

# ** model: callable_data
class CallableData(DomainObject):
    '''
    The shared shape of a module function, a non-execute method, or `execute`:
    docstring, decorators, colon-delimited specs, and body snippets.
    '''

    # * attribute: desc
    desc: Optional[str] = Field(
        default=None,
        description='Stripped docstring summary (functions; omitted on methods when unused).',
    )

    # * attribute: deco
    deco: List[str] = Field(
        default_factory=list,
        description='Encoded decorator expressions.',
    )

    # * attribute: params
    params: List[str] = Field(
        default_factory=list,
        description='Specs `name:type:required:default:desc` (`self` omitted; `required` is `true`/`false`).',
    )

    # * attribute: returns
    returns: List[str] = Field(
        default_factory=list,
        description='Specs `type:` or `type:description`.',
    )

    # * attribute: snpt
    snpt: List[SnippetData] = Field(
        default_factory=list,
        description='Body snippets.',
    )

    # * attribute: idempotent
    idempotent: Optional[bool] = Field(
        default=None,
        description='Set `True` only on a repos `delete` method that passes the no-raise heuristic; omit otherwise.',
    )

# ** model: collaborator_data
class CollaboratorData(DomainObject):
    '''
    A context constructor collaborator, named by parameter and by a sibling
    type imported from the same package.
    '''

    # * attribute: name
    name: str = Field(
        ...,
        description='Constructor parameter name.',
    )

    # * attribute: type
    type: str = Field(
        ...,
        description='Type name matching a same-package sibling import.',
    )

# ** model: event_data
class EventData(DomainObject):
    '''
    A class-shaped payload reused for events, classes, models, mappers,
    interfaces, contexts, and repos — not the component envelope root.
    '''

    # * attribute: name
    name: str = Field(
        ...,
        description='Class name.',
    )

    # * attribute: desc
    desc: Optional[str] = Field(
        default=None,
        description='Stripped class docstring.',
    )

    # * attribute: attributes
    attributes: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Attribute members as `{<name>: <type_name>}` or `{<name>: {'type': <type_name>, 'init': <encoded>}}`.",
    )

    # * attribute: injections
    injections: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Constructor injection entries `{<spec>: {'assign': [{'target': <name>, 'value': <name>}]}}`.",
    )

    # * attribute: execute
    execute: Optional[CallableData] = Field(
        default=None,
        description='`execute` method; `None`/empty for non-event classes.',
    )

    # * attribute: methods
    methods: Dict[str, CallableData] = Field(
        default_factory=dict,
        description='Non-execute methods keyed by name.',
    )

    # * attribute: base
    base: Optional[str] = Field(
        default=None,
        description='Resolved first base (classes, interfaces, contexts).',
    )

    # * attribute: maps
    maps: Optional[str] = Field(
        default=None,
        description='Mapper wrapped domain type (first base).',
    )

    # * attribute: kind
    kind: Optional[str] = Field(
        default=None,
        description="Mapper kind: `'aggregate'` or `'transfer_object'`.",
    )

    # * attribute: implements
    implements: Optional[str] = Field(
        default=None,
        description='Repo fulfilled interface (base name).',
    )

    # * attribute: collaborators
    collaborators: List[CollaboratorData] = Field(
        default_factory=list,
        description='Context sibling-typed constructor params.',
    )

# ** model: group_entry
class GroupEntry(DomainObject):
    '''
    One ordered item in a component envelope's groups. Qualified groups may
    repeat `name`; source order is the document order, not a map key.
    '''

    # * attribute: name
    name: str = Field(
        ...,
        description='Group name.',
    )

    # * attribute: qual
    qual: Optional[str] = Field(
        default=None,
        description='Group qualifier (omit when `None`), e.g. constants `(ids)`.',
    )

    # * attribute: csts
    csts: Dict[str, ConstantData] = Field(
        default_factory=dict,
        description='Constants keyed by name.',
    )

    # * attribute: fncs
    fncs: Dict[str, CallableData] = Field(
        default_factory=dict,
        description='Functions keyed by name (`functions`, `blueprints`).',
    )

    # * attribute: clss
    clss: Dict[str, EventData] = Field(
        default_factory=dict,
        description='Classes keyed by name (`classes`, `utils`).',
    )

    # * attribute: mdls
    mdls: Dict[str, EventData] = Field(
        default_factory=dict,
        description='Models keyed by name.',
    )

    # * attribute: mprs
    mprs: Dict[str, EventData] = Field(
        default_factory=dict,
        description='Mappers keyed by name.',
    )

    # * attribute: ifcs
    ifcs: Dict[str, EventData] = Field(
        default_factory=dict,
        description='Interfaces keyed by name.',
    )

    # * attribute: ctxs
    ctxs: Dict[str, EventData] = Field(
        default_factory=dict,
        description='Contexts keyed by name.',
    )

    # * attribute: repos
    repos: Dict[str, EventData] = Field(
        default_factory=dict,
        description='Repositories keyed by name.',
    )

    # * attribute: evts
    evts: Dict[str, EventData] = Field(
        default_factory=dict,
        description='Events keyed by name, and any unmatched group.',
    )

# ** model: component_envelope
class ComponentEnvelope(DomainObject):
    '''
    The distillation document for every component type, rooted under `cmpt`
    and organized by ordered groups rather than an event-only document.
    '''

    # * attribute: name
    name: str = Field(
        ...,
        description='Module name.',
    )

    # * attribute: kind
    kind: str = Field(
        ...,
        description='Component type: `assets`, `blueprints`, `contexts`, `di`, `domain`, `events`, `interfaces`, `mappers`, `repos`, `utils`.',
    )

    # * attribute: desc
    desc: Optional[str] = Field(
        default=None,
        description='Module docstring summary.',
    )

    # * attribute: impt
    impt: Dict[str, List[ImportEntry]] = Field(
        default_factory=dict,
        description='Import categories `core`, `infra`, `app`.',
    )

    # * attribute: grps
    grps: List[GroupEntry] = Field(
        default_factory=list,
        description='Ordered groups.',
    )
