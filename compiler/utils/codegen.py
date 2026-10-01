"""Tiferet Code Generator Utility"""

# *** imports

# ** core
from typing import Any, Dict, FrozenSet, List, Optional

# ** app
from ..mappers import Declaration, Statement, Expression, ParamList
from ..interfaces.codegen import CodegenService
from ..mappers.ast import ExpressionAggregate
from ..mappers.codegen import (
    EventAccumulator,
    ImportEntryCollector,
    SnippetAccumulator,
)
from .core import (
    Rewrite,
    RewriteContext,
    collect_member_decorators,
    get_return_type_name,
    get_type_name,
)
from .docstring import DocstringParser

# *** functions

# ** function: is_idempotent_delete
def _is_idempotent_delete(inner: Declaration) -> bool:
    '''
    Report whether a method body contains no reachable raise.

    A failing check is not a conformance finding. Callers omit ``idempotent``
    rather than recording False.

    :param inner: The method declaration whose body is walked.
    :type inner: Declaration
    :return: True when no raise statement is reachable.
    :rtype: bool
    '''

    # Walk the method body, including nested control-flow and snippet bodies.
    return not _contains_raise(inner.code)

# ** function: contains_raise
def _contains_raise(stmts: Optional[List[Statement]]) -> bool:
    '''
    Report whether a statement list can reach a raise.

    :param stmts: The statements to walk, or None.
    :type stmts: Optional[List[Statement]]
    :return: True when a raise is reachable.
    :rtype: bool
    '''

    # A missing list has no raise to find.
    for current in stmts or []:
        if getattr(current, 'is_raise', False):
            return True

        # Descend snippet bodies and each control-flow body.
        for name in ('body', 'else_body', 'finally_body'):
            if _contains_raise(getattr(current, name, None)):
                return True

    # No raise was reachable.
    return False

# *** classes

# ** class: imports_group_rewrite
class ImportsGroupRewrite(Rewrite):
    '''
    Turn an imports group into collapsed import categories.

    The host owns the merge. This rewrite only contributes ``impt``.
    '''

    # * method: apply
    def apply(self, candidate: Statement, context: RewriteContext) -> Optional[Dict[str, Any]]:
        '''
        Build import categories from the group body.

        :param candidate: The imports group statement.
        :type candidate: Statement
        :param context: The rewrite visit context.
        :type context: RewriteContext
        :return: ``{'impt': ...}`` when imports exist, else None.
        :rtype: Optional[Dict[str, Any]]
        '''

        # A missing body contributes nothing.
        if not getattr(candidate, 'body', None):
            return None

        # Omit the key when no category collected a symbol.
        impt = context.host.build_imports(candidate.body)
        if not impt:
            return None

        # Return the category map for the host to merge.
        return {'impt': impt}

# ** class: functions_group_rewrite
class FunctionsGroupRewrite(Rewrite):
    '''
    Turn a functions group into free-function payloads.

    The same payloads feed the group entry and the legacy function map.
    '''

    # * method: apply
    def apply(self, candidate: Statement, context: RewriteContext) -> Optional[Dict[str, Any]]:
        '''
        Build function payloads and a functions group entry.

        :param candidate: The functions group statement.
        :type candidate: Statement
        :param context: The rewrite visit context.
        :type context: RewriteContext
        :return: Function payloads and a group entry, or None.
        :rtype: Optional[Dict[str, Any]]
        '''

        # A missing body contributes nothing.
        if not getattr(candidate, 'body', None):
            return None

        # An empty function map is absence, not an empty group.
        fncs = context.host.build_functions(candidate.body)
        if not fncs:
            return None

        # Share the payload with the group entry and the legacy map.
        return {
            'fncs': fncs,
            'grp_entry': context.host.build_group_entry(
                'functions',
                qualifier=context.qualifier,
                fncs=fncs,
            ),
        }

# ** class: blueprints_group_rewrite
class BlueprintsGroupRewrite(Rewrite):
    '''
    Turn a blueprints group into the same callable shape as functions.

    Blueprint sections reuse the free-function builder. Only the group name changes.
    '''

    # * method: apply
    def apply(self, candidate: Statement, context: RewriteContext) -> Optional[Dict[str, Any]]:
        '''
        Build blueprint callables and a blueprints group entry.

        :param candidate: The blueprints group statement.
        :type candidate: Statement
        :param context: The rewrite visit context.
        :type context: RewriteContext
        :return: Callable payloads and a group entry, or None.
        :rtype: Optional[Dict[str, Any]]
        '''

        # A missing body contributes nothing.
        if not getattr(candidate, 'body', None):
            return None

        # Blueprint sections are function sections with a different group name.
        fncs = context.host.build_functions(candidate.body)
        if not fncs:
            return None

        # Keep the callable key. The group name is blueprints.
        return {
            'fncs': fncs,
            'grp_entry': context.host.build_group_entry(
                'blueprints',
                qualifier=context.qualifier,
                fncs=fncs,
            ),
        }

# ** class: constants_group_rewrite
class ConstantsGroupRewrite(Rewrite):
    '''
    Turn a constants group into encoded initializers.

    Constants stay on the group entry. They are not dual-emitted at the envelope root.
    '''

    # * method: apply
    def apply(self, candidate: Statement, context: RewriteContext) -> Optional[Dict[str, Any]]:
        '''
        Build a constants group entry.

        :param candidate: The constants group statement.
        :type candidate: Statement
        :param context: The rewrite visit context.
        :type context: RewriteContext
        :return: A group entry, or None when no constants were built.
        :rtype: Optional[Dict[str, Any]]
        '''

        # A missing body contributes nothing.
        if not getattr(candidate, 'body', None):
            return None

        # An empty constant map is not a group.
        csts = context.host.build_constants(candidate.body)
        if not csts:
            return None

        # Constants live only on the group entry.
        return {
            'grp_entry': context.host.build_group_entry(
                'constants',
                qualifier=context.qualifier,
                csts=csts,
            ),
        }

# ** class: classes_group_rewrite
class ClassesGroupRewrite(Rewrite):
    '''
    Turn a classes group into class payloads keyed by class name.

    A missing base stays omitted rather than recorded as an empty key.
    '''

    # * method: apply
    def apply(self, candidate: Statement, context: RewriteContext) -> Optional[Dict[str, Any]]:
        '''
        Build a classes group entry.

        :param candidate: The classes group statement.
        :type candidate: Statement
        :param context: The rewrite visit context.
        :type context: RewriteContext
        :return: A group entry, or None when no classes were built.
        :rtype: Optional[Dict[str, Any]]
        '''

        # A missing body contributes nothing.
        if not getattr(candidate, 'body', None):
            return None

        # Key classes by class name, not by the section name.
        clss = context.host.build_classes(candidate.body)
        if not clss:
            return None

        # Return the group entry for the host to append.
        return {
            'grp_entry': context.host.build_group_entry(
                'classes',
                qualifier=context.qualifier,
                clss=clss,
            ),
        }

# ** class: utils_group_rewrite
class UtilsGroupRewrite(Rewrite):
    '''
    Turn a utils group into class payloads under the utils name.

    Utility classes reuse the class builder, including the optional base.
    '''

    # * method: apply
    def apply(self, candidate: Statement, context: RewriteContext) -> Optional[Dict[str, Any]]:
        '''
        Build a utils group entry.

        :param candidate: The utils group statement.
        :type candidate: Statement
        :param context: The rewrite visit context.
        :type context: RewriteContext
        :return: A group entry, or None when no classes were built.
        :rtype: Optional[Dict[str, Any]]
        '''

        # A missing body contributes nothing.
        if not getattr(candidate, 'body', None):
            return None

        # Utils are class-shaped. The group name stays utils.
        clss = context.host.build_classes(candidate.body)
        if not clss:
            return None

        # Return the group entry for the host to append.
        return {
            'grp_entry': context.host.build_group_entry(
                'utils',
                qualifier=context.qualifier,
                clss=clss,
            ),
        }

# ** class: models_group_rewrite
class ModelsGroupRewrite(Rewrite):
    '''
    Turn a models group into class payloads without extra envelope keys.

    Models keep the shared class shape and add nothing of their own.
    '''

    # * method: apply
    def apply(self, candidate: Statement, context: RewriteContext) -> Optional[Dict[str, Any]]:
        '''
        Build a models group entry.

        :param candidate: The models group statement.
        :type candidate: Statement
        :param context: The rewrite visit context.
        :type context: RewriteContext
        :return: A group entry, or None when no models were built.
        :rtype: Optional[Dict[str, Any]]
        '''

        # A missing body contributes nothing.
        if not getattr(candidate, 'body', None):
            return None

        # Models add no base, maps, or kind of their own.
        mdls = context.host.build_models(candidate.body)
        if not mdls:
            return None

        # Return the group entry for the host to append.
        return {
            'grp_entry': context.host.build_group_entry(
                'models',
                qualifier=context.qualifier,
                mdls=mdls,
            ),
        }

# ** class: mappers_group_rewrite
class MappersGroupRewrite(Rewrite):
    '''
    Turn a mappers group into mapper payloads with maps and kind.

    The first base is the wrapped type. The second base selects aggregate or transfer object.
    '''

    # * method: apply
    def apply(self, candidate: Statement, context: RewriteContext) -> Optional[Dict[str, Any]]:
        '''
        Build a mappers group entry.

        :param candidate: The mappers group statement.
        :type candidate: Statement
        :param context: The rewrite visit context.
        :type context: RewriteContext
        :return: A group entry, or None when no mappers were built.
        :rtype: Optional[Dict[str, Any]]
        '''

        # A missing body contributes nothing.
        if not getattr(candidate, 'body', None):
            return None

        # Mapper extras are applied by the host, not this rewrite.
        mprs = context.host.build_mappers(candidate.body)
        if not mprs:
            return None

        # Return the group entry for the host to append.
        return {
            'grp_entry': context.host.build_group_entry(
                'mappers',
                qualifier=context.qualifier,
                mprs=mprs,
            ),
        }

# ** class: interfaces_group_rewrite
class InterfacesGroupRewrite(Rewrite):
    '''
    Turn an interfaces group into interface payloads with an optional base.

    A class with no base does not receive a base key.
    '''

    # * method: apply
    def apply(self, candidate: Statement, context: RewriteContext) -> Optional[Dict[str, Any]]:
        '''
        Build an interfaces group entry.

        :param candidate: The interfaces group statement.
        :type candidate: Statement
        :param context: The rewrite visit context.
        :type context: RewriteContext
        :return: A group entry, or None when no interfaces were built.
        :rtype: Optional[Dict[str, Any]]
        '''

        # A missing body contributes nothing.
        if not getattr(candidate, 'body', None):
            return None

        # Interfaces share the class base rule.
        ifcs = context.host.build_interfaces(candidate.body)
        if not ifcs:
            return None

        # Return the group entry for the host to append.
        return {
            'grp_entry': context.host.build_group_entry(
                'interfaces',
                qualifier=context.qualifier,
                ifcs=ifcs,
            ),
        }

# ** class: contexts_group_rewrite
class ContextsGroupRewrite(Rewrite):
    '''
    Turn a contexts group into context payloads with base and collaborators.

    Collaborators are sibling-typed constructor parameters, omitted when none match.
    '''

    # * method: apply
    def apply(self, candidate: Statement, context: RewriteContext) -> Optional[Dict[str, Any]]:
        '''
        Build a contexts group entry.

        :param candidate: The contexts group statement.
        :type candidate: Statement
        :param context: The rewrite visit context.
        :type context: RewriteContext
        :return: A group entry, or None when no contexts were built.
        :rtype: Optional[Dict[str, Any]]
        '''

        # A missing body contributes nothing.
        if not getattr(candidate, 'body', None):
            return None

        # Context extras are applied by the host.
        ctxs = context.host.build_contexts(candidate.body)
        if not ctxs:
            return None

        # Return the group entry for the host to append.
        return {
            'grp_entry': context.host.build_group_entry(
                'contexts',
                qualifier=context.qualifier,
                ctxs=ctxs,
            ),
        }

# ** class: repos_group_rewrite
class ReposGroupRewrite(Rewrite):
    '''
    Turn a repos group into repository payloads with an implemented interface.

    A delete method that raises nothing is marked idempotent. A raise omits the key.
    '''

    # * method: apply
    def apply(self, candidate: Statement, context: RewriteContext) -> Optional[Dict[str, Any]]:
        '''
        Build a repos group entry.

        :param candidate: The repos group statement.
        :type candidate: Statement
        :param context: The rewrite visit context.
        :type context: RewriteContext
        :return: A group entry, or None when no repos were built.
        :rtype: Optional[Dict[str, Any]]
        '''

        # A missing body contributes nothing.
        if not getattr(candidate, 'body', None):
            return None

        # Repo extras, including idempotent delete, are applied by the host.
        repos = context.host.build_repos(candidate.body)
        if not repos:
            return None

        # Return the group entry for the host to append.
        return {
            'grp_entry': context.host.build_group_entry(
                'repos',
                qualifier=context.qualifier,
                repos=repos,
            ),
        }

# ** class: event_group_rewrite
class EventGroupRewrite(Rewrite):
    '''
    Turn an events group, or any unknown group, into event payloads.

    The group entry keeps the group's own name. Events are keyed by section name.
    '''

    # * method: apply
    def apply(self, candidate: Statement, context: RewriteContext) -> Optional[Dict[str, Any]]:
        '''
        Build event payloads and a group entry named for the group.

        :param candidate: The event or unknown group statement.
        :type candidate: Statement
        :param context: The rewrite visit context.
        :type context: RewriteContext
        :return: Event payloads and a group entry, or None.
        :rtype: Optional[Dict[str, Any]]
        '''

        # A missing body or header contributes nothing.
        if not getattr(candidate, 'body', None) or candidate.decl is None:
            return None

        # Unknown groups keep their declared name when dispatched as events.
        evts = context.host.build_events(candidate.body)
        if not evts:
            return None

        # Share the payload with the group entry and the legacy event map.
        return {
            'evts': evts,
            'grp_entry': context.host.build_group_entry(
                candidate.decl.name,
                qualifier=context.qualifier,
                evts=evts,
            ),
        }

# ** class: attribute_member_rewrite
class AttributeMemberRewrite(Rewrite):
    '''
    Record one attribute member on the event accumulator.

    The host reads the inner declaration. This rewrite does not merge a dict.
    '''

    # * method: apply
    def apply(self, candidate: Declaration, context: RewriteContext) -> None:
        '''
        Add the attribute to the event being rewritten.

        :param candidate: The attribute member declaration.
        :type candidate: Declaration
        :param context: The rewrite visit context.
        :type context: RewriteContext
        :return: None
        :rtype: None
        '''

        # The host mutates the accumulator. There is no contribution to merge.
        context.host.build_attribute(candidate, context.event)
        return None

# ** class: init_member_rewrite
class InitMemberRewrite(Rewrite):
    '''
    Record constructor injections from an init member.

    ``self`` is skipped. Each remaining parameter becomes one injection spec.
    '''

    # * method: apply
    def apply(self, candidate: Declaration, context: RewriteContext) -> None:
        '''
        Add injections to the event being rewritten.

        :param candidate: The init member declaration.
        :type candidate: Declaration
        :param context: The rewrite visit context.
        :type context: RewriteContext
        :return: None
        :rtype: None
        '''

        # The host mutates the accumulator. There is no contribution to merge.
        context.host.build_injections(candidate, context.event)
        return None

# ** class: execute_member_rewrite
class ExecuteMemberRewrite(Rewrite):
    '''
    Record an execute payload without a summary description.

    Execute summaries are out of scope. Decorators, params, returns, and snippets are not.
    '''

    # * method: apply
    def apply(self, candidate: Declaration, context: RewriteContext) -> None:
        '''
        Set the execute payload on the event being rewritten.

        :param candidate: The execute member declaration.
        :type candidate: Declaration
        :param context: The rewrite visit context.
        :type context: RewriteContext
        :return: None
        :rtype: None
        '''

        # The host mutates the accumulator and does not copy a desc key.
        context.host.build_execute(candidate, context.event)
        return None

# ** class: method_member_rewrite
class MethodMemberRewrite(Rewrite):
    '''
    Record a non-execute method on the event accumulator.

    A parenthetical qualifier is copied onto the payload. A method summary is not.
    '''

    # * method: apply
    def apply(self, candidate: Declaration, context: RewriteContext) -> None:
        '''
        Add a method payload when the inner declaration builds one.

        :param candidate: The method member declaration.
        :type candidate: Declaration
        :param context: The rewrite visit context.
        :type context: RewriteContext
        :return: None
        :rtype: None
        '''

        # An empty callable is absence, not a method entry.
        method = context.host.build_method(candidate)
        if not method:
            return None

        # Copy a member qualifier when the header declared one.
        if getattr(candidate, 'artifact_qualifier', None):
            method['qualifier'] = candidate.artifact_qualifier

        # Key the method by the inner declaration name.
        inner = candidate.inner_decl
        if inner is not None and inner.name:
            context.event.add_method(inner.name, method)
        return None

# *** constants

# ** constant: known_group_hooks
KNOWN_GROUP_HOOKS: FrozenSet[str] = frozenset({
    'imports',
    'functions',
    'constants',
    'classes',
    'models',
    'mappers',
    'interfaces',
    'utils',
    'contexts',
    'blueprints',
    'repos',
})

# ** constant: generator_rewrite_set
GENERATOR_REWRITE_SET: List[Rewrite] = [
    ImportsGroupRewrite(
        id='generator.imports_group',
        applies_to='imports',
    ),
    FunctionsGroupRewrite(
        id='generator.functions_group',
        applies_to='functions',
    ),
    BlueprintsGroupRewrite(
        id='generator.blueprints_group',
        applies_to='blueprints',
    ),
    ConstantsGroupRewrite(
        id='generator.constants_group',
        applies_to='constants',
    ),
    ClassesGroupRewrite(
        id='generator.classes_group',
        applies_to='classes',
    ),
    ModelsGroupRewrite(
        id='generator.models_group',
        applies_to='models',
    ),
    MappersGroupRewrite(
        id='generator.mappers_group',
        applies_to='mappers',
    ),
    InterfacesGroupRewrite(
        id='generator.interfaces_group',
        applies_to='interfaces',
    ),
    UtilsGroupRewrite(
        id='generator.utils_group',
        applies_to='utils',
    ),
    ContextsGroupRewrite(
        id='generator.contexts_group',
        applies_to='contexts',
    ),
    ReposGroupRewrite(
        id='generator.repos_group',
        applies_to='repos',
    ),
    EventGroupRewrite(
        id='generator.events_group',
        applies_to='events',
    ),
    AttributeMemberRewrite(
        id='generator.attribute_member',
        applies_to='attribute',
    ),
    InitMemberRewrite(
        id='generator.init_member',
        applies_to='init',
    ),
    ExecuteMemberRewrite(
        id='generator.execute_member',
        applies_to='execute',
    ),
    MethodMemberRewrite(
        id='generator.method_member',
        applies_to='method',
    ),
]

# *** utils

# ** util: tiferet_generator
class TiferetGenerator(CodegenService):
    '''
    Turn a parsed module into a component envelope so distillation can record structure without keeping the source.

    Kind 3 rewrites dispatch groups and members. This host builds imports, constants, classes, functions, and events, and dual-emits a legacy event group only when the requested kind is events.
    '''

    # * attribute: rewrites
    rewrites: List[Rewrite]

    # * attribute: _sibling_import_names
    _sibling_import_names: FrozenSet[str]

    # * init
    def __init__(self, rewrites: Optional[List[Rewrite]] = None) -> None:
        '''
        Store the rewrite set used to dispatch groups and members.

        Zero-arg construction uses ``GENERATOR_REWRITE_SET`` so dependency injection can build the generator without arguments.

        :param rewrites: The rewrite set, or None for the default set.
        :type rewrites: Optional[List[Rewrite]]
        :return: None
        :rtype: None
        '''

        # An omitted set is the published dispatch order.
        self.rewrites = GENERATOR_REWRITE_SET if rewrites is None else rewrites

        # Sibling names are filled when a module is generated.
        self._sibling_import_names = frozenset()

    # * method: match_rewrite
    def match_rewrite(self, hook: str) -> Optional[Rewrite]:
        '''
        Return the first rewrite attached to a visit hook.

        :param hook: The visit hook to match.
        :type hook: str
        :return: The first matching rewrite, or None.
        :rtype: Optional[Rewrite]
        '''

        # Preserve rewrite-set order and return on the first hook match.
        for rewrite in self.rewrites:
            if rewrite.attaches_to(hook):
                return rewrite

        # No rewrite handles this hook.
        return None

    # * method: resolve_group_hook
    def resolve_group_hook(self, group_name: str) -> str:
        '''
        Map a group name to the hook that dispatches it.

        Unknown names dispatch as events. ``exports`` is skipped before this is called.

        :param group_name: The artifact group name.
        :type group_name: str
        :return: The group name when it is known, otherwise ``events``.
        :rtype: str
        '''

        # Known groups keep their own hook. Everything else is an event group.
        if group_name in KNOWN_GROUP_HOOKS:
            return group_name
        return 'events'

    # * method: resolve_member_hook
    def resolve_member_hook(self, member_decl: Declaration) -> Optional[str]:
        '''
        Map a member declaration to an attribute, init, execute, or method hook.

        :param member_decl: The artifact member declaration.
        :type member_decl: Declaration
        :return: The member hook, or None when the member is not dispatched.
        :rtype: Optional[str]
        '''

        # Prefer the typed role, then the declaration name.
        role = getattr(member_decl, 'artifact_role', None) or member_decl.name
        if role in ('attribute', 'init'):
            return role

        # A method with a body is execute only when the inner name is execute.
        if role == 'method' and member_decl.code:
            inner = member_decl.inner_decl
            if inner is not None and inner.name == 'execute':
                return 'execute'
            return 'method'

        # Other roles are not member rewrites.
        return None

    # * method: generate
    def generate(self, ast: Any, kind: str = 'events') -> Dict[str, Any]:
        '''
        Generate a component envelope from a parsed module.

        ``kind='events'`` also dual-emits a legacy ``evt_grp``. Other kinds omit that key. ``cmpt`` never carries ``evt_grp``.

        :param ast: Module-level declaration aggregate from parsing.
        :type ast: Any
        :param kind: Requested component type. Defaults to ``events``.
        :type kind: str
        :return: The component envelope, and a legacy event group when kind is events.
        :rtype: Dict[str, Any]
        '''

        # A missing module name is still a named envelope.
        module_name = ast.name or 'unknown'

        # Strip the module docstring. An empty summary is omitted later.
        description = DocstringParser.strip(ast.doc_string) if ast.doc_string else ''

        # Sibling names must be known before context collaborators are built.
        self._sibling_import_names = self.collect_sibling_import_names(ast.code)

        # The envelope always carries the requested component type.
        cmpt = {
            'name': module_name,
            'kind': kind,
        }
        if description:
            cmpt['desc'] = description

        # Groups contribute imports, functions, events, and ordered group entries.
        impt = {}
        fncs = {}
        evts = {}
        grps = []
        for current in ast.code or []:
            if not getattr(current, 'is_artifact', False) or current.decl is None:
                continue

            # Exports are not a generated group.
            group_name = current.decl.name
            if group_name == 'exports':
                continue

            # Unknown groups dispatch as events. A missing rewrite is skipped.
            hook = self.resolve_group_hook(group_name)
            rewrite = self.match_rewrite(hook)
            if rewrite is None:
                continue

            # Invoke the rewrite as a callable. The host owns the merge.
            outcome = rewrite(
                current,
                RewriteContext(
                    host=self,
                    qualifier=current.decl.artifact_qualifier,
                ),
            ) or {}
            self._merge_imports(impt, outcome.get('impt'))
            fncs.update(outcome.get('fncs') or {})
            evts.update(outcome.get('evts') or {})
            if outcome.get('grp_entry'):
                grps.append(outcome['grp_entry'])

        # Attach only the envelope keys that were built.
        if impt:
            cmpt['impt'] = impt
        if grps:
            cmpt['grps'] = grps

        # The component envelope is the distillation document.
        result = {'cmpt': cmpt}

        # Dual-emit the legacy event group only for the events kind.
        if kind == 'events':
            evt_grp = {'name': module_name}
            if description:
                evt_grp['desc'] = description
            if impt:
                evt_grp['impt'] = impt
            if fncs:
                evt_grp['fncs'] = fncs
            if evts:
                evt_grp['evts'] = evts
            result['evt_grp'] = evt_grp

        # Return the envelope. Other kinds have no evt_grp key.
        return result

    # * method: collect_sibling_import_names
    def collect_sibling_import_names(self, code: Optional[List[Statement]]) -> FrozenSet[str]:
        '''
        Collect symbol names imported from a same-package sibling module.

        A sibling path starts with ``.`` and not ``..``.

        :param code: The module statements.
        :type code: Optional[List[Statement]]
        :return: Imported sibling symbol names.
        :rtype: FrozenSet[str]
        '''

        # Only the imports group contributes sibling names.
        names = []
        for current in code or []:
            if not getattr(current, 'is_artifact', False) or current.decl is None:
                continue
            if current.decl.name != 'imports':
                continue

            # Walk category sections for relative import-from statements.
            self._collect_sibling_names(current.body, names)

        # Return a set so collaborator checks are membership tests.
        return frozenset(names)

    # * method: build_group_entry
    def build_group_entry(self, name: str,
            qualifier: Optional[str] = None, **payload) -> Dict[str, Any]:
        '''
        Build one ordered group entry.

        :param name: The group name.
        :type name: str
        :param qualifier: The optional parenthetical qualifier.
        :type qualifier: Optional[str]
        :param payload: Group payload keys such as ``fncs`` or ``evts``.
        :type payload: dict
        :return: The group entry.
        :rtype: Dict[str, Any]
        '''

        # Name is the only required key.
        entry = {'name': name}

        # Omit an empty qualifier rather than recording it.
        if qualifier:
            entry['qual'] = qualifier

        # Payload keys follow name and qual.
        entry.update(payload)
        return entry

    # * method: build_constants
    def build_constants(self, body: List[Statement]) -> Dict[str, Dict[str, str]]:
        '''
        Encode each constant section's assignment targets.

        :param body: The constants group body.
        :type body: List[Statement]
        :return: Constant names mapped to ``{'value': encoded}``.
        :rtype: Dict[str, Dict[str, str]]
        '''

        # Walk constant sections. Other sections in the group are ignored.
        csts = {}
        for section in body or []:
            if not self._is_section(section, 'constant'):
                continue

            # Key by the assignment target, not the section name.
            for stmt in section.body or []:
                assigned = self._constant_assignment(stmt)
                if assigned is None:
                    continue
                name, encoded = assigned
                csts[name] = {'value': encoded}

        # Return the constant map, empty when none were assigned.
        return csts

    # * method: build_imports
    def build_imports(self, body: List[Statement]) -> Dict[str, List[Dict[str, Any]]]:
        '''
        Collapse import-from statements under each category section.

        :param body: The imports group body.
        :type body: List[Statement]
        :return: Category names mapped to ``{src, tgts}`` rows.
        :rtype: Dict[str, List[Dict[str, Any]]]
        '''

        # Category names are the section names, in source order.
        impt = {}
        for section in body or []:
            if not getattr(section, 'is_artifact', False) or section.decl is None:
                continue

            # Omit a category that collected no import-from symbols.
            entries = self.collect_import_entries(section.body)
            if entries:
                impt[section.decl.name] = entries

        # Return the category map.
        return impt

    # * method: collect_import_entries
    def collect_import_entries(self, stmts: Optional[List[Statement]]) -> List[Dict[str, Any]]:
        '''
        Collapse import-from statements into first-seen module rows.

        :param stmts: The statements to scan.
        :type stmts: Optional[List[Statement]]
        :return: Ordered ``{src, tgts}`` rows.
        :rtype: List[Dict[str, Any]]
        '''

        # The collector keeps first-seen module order.
        collector = ImportEntryCollector()
        for stmt in stmts or []:
            if not getattr(stmt, 'is_import_from', False):
                continue

            # The module path is the import-from target. Symbols come from the import expression.
            module_path = ''
            if stmt.init_expr is not None and stmt.init_expr.name:
                module_path = stmt.init_expr.name
            for symbol in ExpressionAggregate.collect_import_names(stmt.expr):
                collector.add(module_path, symbol)

        # Return the collapsed rows.
        return collector.to_list()

    # * method: build_functions
    def build_functions(self, body: List[Statement]) -> Dict[str, Dict[str, Any]]:
        '''
        Build each function or blueprint section into a callable payload.

        :param body: The functions or blueprints group body.
        :type body: List[Statement]
        :return: Function names mapped to callable payloads.
        :rtype: Dict[str, Dict[str, Any]]
        '''

        # Only function and blueprint sections contribute callables.
        fncs = {}
        for section in body or []:
            if not getattr(section, 'is_artifact', False) or section.decl is None:
                continue
            artifact_type = (getattr(section.decl, 'artifact_type', '') or '').strip()
            if artifact_type not in ('** function', '** blueprint'):
                continue

            # Decorators precede the inner function declaration.
            func_decl, decorators = self._function_from_section(section)
            built = self.build_function(func_decl, decorators)
            if built and func_decl is not None and func_decl.name:
                fncs[func_decl.name] = built

        # Return the function map.
        return fncs

    # * method: build_function
    def build_function(self, func_decl: Optional[Declaration],
            decorators: Optional[List[str]] = None) -> Optional[Dict[str, Any]]:
        '''
        Build one function payload, with the stripped docstring first.

        :param func_decl: The function declaration.
        :type func_decl: Optional[Declaration]
        :param decorators: Encoded decorators that precede the declaration.
        :type decorators: Optional[List[str]]
        :return: The function payload, or None when the declaration is missing.
        :rtype: Optional[Dict[str, Any]]
        '''

        # A missing declaration is not a function.
        if func_decl is None:
            return None

        # Description comes first, then decorators, then callable keys.
        payload = {}
        description = DocstringParser.strip(func_decl.doc_string) if func_decl.doc_string else ''
        if description:
            payload['desc'] = description
        if decorators:
            payload['deco'] = list(decorators)

        # Callable keys follow. They do not carry a function summary.
        payload.update(self.build_callable(func_decl) or {})
        return payload or None

    # * method: build_events
    def build_events(self, body: List[Statement]) -> Dict[str, Dict[str, Any]]:
        '''
        Build each event section, keyed by the section name.

        :param body: The events group body.
        :type body: List[Statement]
        :return: Section names mapped to event payloads.
        :rtype: Dict[str, Dict[str, Any]]
        '''

        # The section name is the event key, even when it differs from the class name.
        evts = {}
        for section in body or []:
            if not getattr(section, 'is_artifact', False) or section.decl is None:
                continue
            payload = self.extract_event_from_body(section)
            if payload:
                evts[section.decl.name] = payload

        # Return the event map.
        return evts

    # * method: extract_event_from_body
    def extract_event_from_body(self, section: Statement) -> Optional[Dict[str, Any]]:
        '''
        Find the class in a section and build its shared payload.

        :param section: The section statement.
        :type section: Statement
        :return: The serialized class payload, or None when no class is present.
        :rtype: Optional[Dict[str, Any]]
        '''

        # A section without a class declaration contributes nothing.
        class_decl = section.find_class() if section is not None else None
        if class_decl is None:
            return None

        # Strip the class docstring. An empty summary becomes None on the accumulator.
        doc_string = DocstringParser.strip(class_decl.doc_string) if class_decl.doc_string else ''
        return self.build_event(class_decl, doc_string)

    # * method: build_event
    def build_event(self, class_decl: Declaration,
            doc_string: str) -> Dict[str, Any]:
        '''
        Accumulate one class and serialize the filled sections.

        :param class_decl: The class declaration.
        :type class_decl: Declaration
        :param doc_string: The stripped class docstring.
        :type doc_string: str
        :return: The serialized class payload.
        :rtype: Dict[str, Any]
        '''

        # Name is required. An empty description is omitted by serialization.
        event = EventAccumulator(
            name=class_decl.name,
            desc=doc_string or None,
        )

        # Members mutate the accumulator through their own rewrites.
        for member in class_decl.members:
            self.dispatch_member(member, event)

        # Return only the filled sections.
        return event.to_dict()

    # * method: dispatch_member
    def dispatch_member(self, member_decl: Declaration,
            event: EventAccumulator) -> None:
        '''
        Invoke the member rewrite for one class member.

        :param member_decl: The artifact member declaration.
        :type member_decl: Declaration
        :param event: The accumulator the rewrite mutates.
        :type event: EventAccumulator
        :return: None
        :rtype: None
        '''

        # A member without a hook is not an attribute, init, execute, or method.
        hook = self.resolve_member_hook(member_decl)
        if hook is None:
            return

        # Invoke the matching rewrite as a callable.
        rewrite = self.match_rewrite(hook)
        if rewrite is None:
            return
        rewrite(
            member_decl,
            RewriteContext(
                host=self,
                event=event,
            ),
        )

    # * method: build_attribute
    def build_attribute(self, member_decl: Declaration,
            event: EventAccumulator) -> None:
        '''
        Add one attribute from the member's inner declaration.

        :param member_decl: The attribute member declaration.
        :type member_decl: Declaration
        :param event: The accumulator to update.
        :type event: EventAccumulator
        :return: None
        :rtype: None
        '''

        # The inner declaration carries the name, type, and initializer.
        inner = member_decl.inner_decl
        if inner is None or not inner.name:
            return

        # Encode an initializer only when one is present.
        init = inner.value.encode() if inner.value is not None else None
        event.add_attribute(
            inner.name,
            get_type_name(inner.type),
            init=init,
        )

    # * method: build_injections
    def build_injections(self, member_decl: Declaration,
            event: EventAccumulator) -> None:
        '''
        Add constructor injections for every parameter except ``self``.

        :param member_decl: The init member declaration.
        :type member_decl: Declaration
        :param event: The accumulator to update.
        :type event: EventAccumulator
        :return: None
        :rtype: None
        '''

        # Parameters live on the inner function type.
        inner = member_decl.inner_decl
        if inner is None or inner.type is None:
            return

        # Descriptions come from the init docstring, not from the parameter node.
        descriptions = DocstringParser.parse_param_descriptions(inner.doc_string or '')
        for param in inner.type.params or []:
            if param.name == 'self':
                continue

            # The spec leaves the default slot empty. The value assigns the name to itself.
            event.add_injection(
                self._injection_spec(param, descriptions),
                {
                    'assign': [{
                        'target': param.name,
                        'value': param.name,
                    }],
                },
            )

    # * method: build_execute
    def build_execute(self, member_decl: Declaration,
            event: EventAccumulator) -> None:
        '''
        Assemble an execute payload without a description key.

        :param member_decl: The execute member declaration.
        :type member_decl: Declaration
        :param event: The accumulator to update.
        :type event: EventAccumulator
        :return: None
        :rtype: None
        '''

        # Optional sections are omitted when empty. desc is never set.
        data = {}
        decorators = self.collect_decorators(member_decl)
        if decorators:
            data['deco'] = decorators

        # Params, returns, and snippets come from the inner function.
        inner = member_decl.inner_decl
        if inner is not None:
            params = self.build_params(inner)
            if params:
                data['params'] = params
            returns = self.build_returns(inner)
            if returns:
                data['returns'] = returns
            snippets = self.build_snippets(inner.code)
            if snippets:
                data['snpt'] = snippets

        # Store the payload. An empty dict is omitted by serialization.
        event.set_execute(data)

    # * method: build_method
    def build_method(self, member_decl: Declaration) -> Optional[Dict[str, Any]]:
        '''
        Build a non-execute method payload without a description.

        :param member_decl: The method member declaration.
        :type member_decl: Declaration
        :return: The callable payload, or None when the inner declaration is missing.
        :rtype: Optional[Dict[str, Any]]
        '''

        # The member wrapper supplies decorators. The inner declaration supplies the callable.
        return self.build_callable(member_decl.inner_decl, member_decl)

    # * method: build_callable
    def build_callable(self, func_decl: Optional[Declaration],
            member_decl: Optional[Declaration] = None) -> Optional[Dict[str, Any]]:
        '''
        Build the shared callable shape for a function or method.

        :param func_decl: The function or method declaration.
        :type func_decl: Optional[Declaration]
        :param member_decl: The optional member wrapper that carries decorators.
        :type member_decl: Optional[Declaration]
        :return: The callable payload, or None when the declaration is missing.
        :rtype: Optional[Dict[str, Any]]
        '''

        # A missing declaration is not a callable.
        if func_decl is None:
            return None

        # Decorators come from the member wrapper, not from a function section.
        payload = {}
        if member_decl is not None:
            decorators = self.collect_decorators(member_decl)
            if decorators:
                payload['deco'] = decorators

        # Include only the callable sections that were built.
        params = self.build_params(func_decl)
        if params:
            payload['params'] = params
        returns = self.build_returns(func_decl)
        if returns:
            payload['returns'] = returns
        snippets = self.build_snippets(func_decl.code)
        if snippets:
            payload['snpt'] = snippets

        # Return the filled sections, or None when the callable is empty.
        return payload or None

    # * method: collect_decorators
    def collect_decorators(self, member_decl: Optional[Declaration]) -> List[str]:
        '''
        Collect encoded decorators that precede a member's inner declaration.

        :param member_decl: The member declaration, or None.
        :type member_decl: Optional[Declaration]
        :return: Encoded decorator expressions.
        :rtype: List[str]
        '''

        # A missing wrapper has no decorators.
        if member_decl is None:
            return []

        # Delegate to the shared member-decorator walk.
        return collect_member_decorators(member_decl)

    # * method: build_params
    def build_params(self, func_decl: Optional[Declaration]) -> List[str]:
        '''
        Build compact parameter specs, skipping ``self``.

        :param func_decl: The function or method declaration.
        :type func_decl: Optional[Declaration]
        :return: Specs ``name:type:required:default:desc``.
        :rtype: List[str]
        '''

        # A missing type has no parameters.
        if func_decl is None or func_decl.type is None:
            return []

        # Descriptions come from the callable docstring.
        descriptions = DocstringParser.parse_param_descriptions(func_decl.doc_string or '')
        specs = []
        for current in func_decl.type.params or []:
            if current.name == 'self':
                continue
            specs.append(self._param_spec(current, descriptions))

        # Return the specs, empty when only self was declared.
        return specs

    # * method: build_returns
    def build_returns(self, func_decl: Optional[Declaration]) -> List[str]:
        '''
        Build return specs from the return type and docstring descriptions.

        :param func_decl: The function or method declaration.
        :type func_decl: Optional[Declaration]
        :return: Specs ``type:desc``, or ``type:`` when no description was parsed.
        :rtype: List[str]
        '''

        # A missing declaration has no return spec.
        if func_decl is None:
            return []

        # One spec per description. Otherwise emit the type with an empty description.
        type_name = get_return_type_name(func_decl.type)
        descriptions = DocstringParser.parse_return_descriptions(func_decl.doc_string or '')
        if descriptions:
            return [f'{type_name}:{desc}' for desc in descriptions]
        return [f'{type_name}:']

    # * method: build_snippets
    def build_snippets(self, code: Optional[List[Statement]]) -> List[Dict[str, Any]]:
        '''
        Build a snippet dict for each snippet statement in a body.

        :param code: The callable body.
        :type code: Optional[List[Statement]]
        :return: Serialized snippets, omitting empty ones.
        :rtype: List[Dict[str, Any]]
        '''

        # Only snippet statements contribute. Empty snippets are omitted.
        snippets = []
        for current in code or []:
            if not getattr(current, 'is_snippet', False):
                continue
            snippet = self.build_snippet(current)
            if snippet:
                snippets.append(snippet)

        # Return the serialized snippets.
        return snippets

    # * method: build_snippet
    def build_snippet(self, snippet_stmt: Statement) -> Optional[Dict[str, Any]]:
        '''
        Accumulate one snippet's comments and encoded statements.

        :param snippet_stmt: The snippet statement.
        :type snippet_stmt: Statement
        :return: The snippet dict, or None when it is empty.
        :rtype: Optional[Dict[str, Any]]
        '''

        # Comments and statements stay on the accumulator until serialization.
        accumulator = SnippetAccumulator()
        for comment in getattr(snippet_stmt, 'comments', None) or []:
            if not getattr(comment, 'is_comment', False):
                continue
            text = self._comment_text(comment)
            if text:
                accumulator.add_comment(text)

        # Encode each executable statement. Blank encodings are dropped by the accumulator.
        for current in snippet_stmt.body or []:
            accumulator.add_statement(current.encode())

        # An empty snippet is absence.
        return accumulator.to_dict()

    # * method: build_classes
    def build_classes(self, body: List[Statement]) -> Dict[str, Dict[str, Any]]:
        '''
        Build class payloads and set ``base`` when a first base is present.

        :param body: The classes or utils group body.
        :type body: List[Statement]
        :return: Class names mapped to payloads.
        :rtype: Dict[str, Dict[str, Any]]
        '''

        # Classes and utils share the optional base key.
        return self._class_payloads(body, self._set_base)

    # * method: build_interfaces
    def build_interfaces(self, body: List[Statement]) -> Dict[str, Dict[str, Any]]:
        '''
        Build interface payloads and set ``base`` when a first base is present.

        :param body: The interfaces group body.
        :type body: List[Statement]
        :return: Class names mapped to payloads.
        :rtype: Dict[str, Dict[str, Any]]
        '''

        # Interfaces use the same base rule as classes.
        return self._class_payloads(body, self._set_base)

    # * method: build_mappers
    def build_mappers(self, body: List[Statement]) -> Dict[str, Dict[str, Any]]:
        '''
        Build mapper payloads with ``maps`` and a mapper kind.

        :param body: The mappers group body.
        :type body: List[Statement]
        :return: Class names mapped to payloads.
        :rtype: Dict[str, Dict[str, Any]]
        '''

        # maps is the first base. kind comes from the second base name.
        return self._class_payloads(body, self._set_mapper_keys)

    # * method: build_contexts
    def build_contexts(self, body: List[Statement]) -> Dict[str, Dict[str, Any]]:
        '''
        Build context payloads with ``base`` and sibling collaborators.

        :param body: The contexts group body.
        :type body: List[Statement]
        :return: Class names mapped to payloads.
        :rtype: Dict[str, Dict[str, Any]]
        '''

        # Collaborators are added only when the init signature names a sibling type.
        return self._class_payloads(body, self._set_context_keys)

    # * method: build_repos
    def build_repos(self, body: List[Statement]) -> Dict[str, Dict[str, Any]]:
        '''
        Build repository payloads with ``implements`` and an idempotent delete.

        :param body: The repos group body.
        :type body: List[Statement]
        :return: Class names mapped to payloads.
        :rtype: Dict[str, Dict[str, Any]]
        '''

        # implements is the first base. idempotent is set only when delete raises nothing.
        return self._class_payloads(body, self._set_repo_keys)

    # * method: build_models
    def build_models(self, body: List[Statement]) -> Dict[str, Dict[str, Any]]:
        '''
        Build model payloads with no keys beyond the shared class shape.

        :param body: The models group body.
        :type body: List[Statement]
        :return: Class names mapped to payloads.
        :rtype: Dict[str, Dict[str, Any]]
        '''

        # Models do not receive base, maps, kind, or implements.
        return self._class_payloads(body, self._keep_class_payload)

    # * method: build_collaborators
    def build_collaborators(self, class_decl: Declaration) -> List[Dict[str, str]]:
        '''
        Collect init parameters whose type is a same-package sibling import.

        :param class_decl: The class declaration.
        :type class_decl: Declaration
        :return: Collaborator dicts with ``name`` and ``type``.
        :rtype: List[Dict[str, str]]
        '''

        # Only init members contribute constructor collaborators.
        collaborators = []
        for member in class_decl.members:
            role = getattr(member, 'artifact_role', None) or member.name
            if role != 'init':
                continue
            inner = member.inner_decl
            if inner is None or inner.type is None:
                continue

            # Skip self. A type must match a sibling import symbol.
            for param in inner.type.params or []:
                if param.name == 'self':
                    continue
                type_name = get_type_name(param.type)
                if type_name in self._sibling_import_names:
                    collaborators.append({
                        'name': param.name,
                        'type': type_name,
                    })

        # Return the matching parameters, empty when none are siblings.
        return collaborators

    # * method: merge_imports
    def _merge_imports(self, impt: Dict[str, List[Dict[str, Any]]],
            extra: Optional[Dict[str, List[Dict[str, Any]]]]) -> None:
        '''
        Extend import categories with another category map.

        :param impt: The accumulated import map.
        :type impt: Dict[str, List[Dict[str, Any]]]
        :param extra: The map to merge, or None.
        :type extra: Optional[Dict[str, List[Dict[str, Any]]]]
        :return: None
        :rtype: None
        '''

        # Later groups append to a category that was already seen.
        for category, entries in (extra or {}).items():
            impt.setdefault(category, []).extend(entries)

    # * method: collect_sibling_names
    def _collect_sibling_names(self, stmts: Optional[List[Statement]],
            names: List[str]) -> None:
        '''
        Append sibling import symbols from import-from statements.

        :param stmts: The statements to walk.
        :type stmts: Optional[List[Statement]]
        :param names: The symbol list to extend.
        :type names: List[str]
        :return: None
        :rtype: None
        '''

        # Descend artifact sections so category wrappers are not a boundary.
        for stmt in stmts or []:
            if getattr(stmt, 'is_import_from', False):
                module_path = ''
                if stmt.init_expr is not None and stmt.init_expr.name:
                    module_path = stmt.init_expr.name
                if module_path.startswith('.') and not module_path.startswith('..'):
                    names.extend(ExpressionAggregate.collect_import_names(stmt.expr))
            if getattr(stmt, 'is_artifact', False):
                self._collect_sibling_names(stmt.body, names)

    # * method: is_section
    def _is_section(self, section: Statement, keyword: str) -> bool:
        '''
        Report whether a statement is an artifact section of a given keyword.

        :param section: The candidate statement.
        :type section: Statement
        :param keyword: The section keyword, such as ``constant``.
        :type keyword: str
        :return: True when the section keyword matches.
        :rtype: bool
        '''

        # Non-artifact statements and bare headers have no keyword.
        if not getattr(section, 'is_artifact', False) or section.decl is None:
            return False
        return getattr(section.decl, 'section_keyword', None) == keyword

    # * method: constant_assignment
    def _constant_assignment(self, stmt: Statement) -> Optional[tuple]:
        '''
        Read an assignment target name and its encoded initializer.

        :param stmt: A constant-section statement.
        :type stmt: Statement
        :return: The name and encoded value, or None.
        :rtype: Optional[tuple]
        '''

        # Parser constants are attribute declarations with an initializer.
        if getattr(stmt, 'is_decl', False) and stmt.decl is not None and stmt.decl.value is not None:
            if not stmt.decl.name:
                return None
            return stmt.decl.name, stmt.decl.value.encode()

        # An assignment expression is the same target and value.
        if (
            getattr(stmt, 'is_expr', False)
            and stmt.expr is not None
            and stmt.expr.is_assignment
            and stmt.expr.left is not None
            and stmt.expr.left.name
        ):
            encoded = stmt.expr.right.encode() if stmt.expr.right is not None else ''
            return stmt.expr.left.name, encoded

        # Anything else is not a constant assignment.
        return None

    # * method: function_from_section
    def _function_from_section(self, section: Statement) -> tuple:
        '''
        Find a section's inner function and the decorators that precede it.

        :param section: The function or blueprint section.
        :type section: Statement
        :return: The function declaration and encoded decorators.
        :rtype: tuple
        '''

        # Stop at the first function declaration. Earlier expressions are decorators.
        decorators = []
        for stmt in section.body or []:
            if getattr(stmt, 'is_decl', False) and stmt.decl is not None and stmt.decl.is_func:
                return stmt.decl, decorators
            if not getattr(stmt, 'is_expr', False) or stmt.expr is None:
                continue
            encoded = stmt.expr.encode()
            if encoded:
                decorators.append(encoded)

        # A section without a function declaration contributes neither.
        return None, decorators

    # * method: class_payloads
    def _class_payloads(self, body: List[Statement], annotate) -> Dict[str, Dict[str, Any]]:
        '''
        Build class payloads and let the caller patch extra keys.

        :param body: The group body.
        :type body: List[Statement]
        :param annotate: Callable that patches one class declaration and payload.
        :type annotate: Callable
        :return: Class names mapped to payloads.
        :rtype: Dict[str, Dict[str, Any]]
        '''

        # Key by the class name. The section name is not the map key.
        entries = {}
        for section in body or []:
            if not getattr(section, 'is_artifact', False):
                continue
            class_decl = section.find_class()
            payload = self.extract_event_from_body(section)
            if not payload or class_decl is None:
                continue

            # Patch extras after the shared payload exists.
            annotate(class_decl, payload)
            entries[payload['name']] = payload

        # Return the class map.
        return entries

    # * method: keep_class_payload
    def _keep_class_payload(self, class_decl: Declaration,
            payload: Dict[str, Any]) -> None:
        '''
        Leave a shared class payload unchanged.

        :param class_decl: The class declaration.
        :type class_decl: Declaration
        :param payload: The serialized payload.
        :type payload: Dict[str, Any]
        :return: None
        :rtype: None
        '''

        # Models add no extra keys.
        del class_decl, payload

    # * method: set_base
    def _set_base(self, class_decl: Declaration, payload: Dict[str, Any]) -> None:
        '''
        Set ``base`` from the first base name when one is present.

        :param class_decl: The class declaration.
        :type class_decl: Declaration
        :param payload: The serialized payload.
        :type payload: Dict[str, Any]
        :return: None
        :rtype: None
        '''

        # A class with no base does not receive the key.
        base = self._base_name(class_decl, 0)
        if base:
            payload['base'] = base

    # * method: set_mapper_keys
    def _set_mapper_keys(self, class_decl: Declaration,
            payload: Dict[str, Any]) -> None:
        '''
        Set ``maps`` and mapper ``kind`` from the base chain.

        :param class_decl: The class declaration.
        :type class_decl: Declaration
        :param payload: The serialized payload.
        :type payload: Dict[str, Any]
        :return: None
        :rtype: None
        '''

        # The first base is the wrapped domain type.
        maps = self._base_name(class_decl, 0)
        if maps:
            payload['maps'] = maps

        # The second base selects the mapper kind. Other names omit kind.
        second = self._base_name(class_decl, 1)
        if second == 'Aggregate':
            payload['kind'] = 'aggregate'
        elif second == 'TransferObject':
            payload['kind'] = 'transfer_object'

    # * method: set_context_keys
    def _set_context_keys(self, class_decl: Declaration,
            payload: Dict[str, Any]) -> None:
        '''
        Set ``base`` and sibling collaborators on a context payload.

        :param class_decl: The class declaration.
        :type class_decl: Declaration
        :param payload: The serialized payload.
        :type payload: Dict[str, Any]
        :return: None
        :rtype: None
        '''

        # Contexts use the class base rule, then optional collaborators.
        self._set_base(class_decl, payload)
        collaborators = self.build_collaborators(class_decl)
        if collaborators:
            payload['collaborators'] = collaborators

    # * method: set_repo_keys
    def _set_repo_keys(self, class_decl: Declaration,
            payload: Dict[str, Any]) -> None:
        '''
        Set ``implements`` and mark an idempotent delete method.

        :param class_decl: The class declaration.
        :type class_decl: Declaration
        :param payload: The serialized payload.
        :type payload: Dict[str, Any]
        :return: None
        :rtype: None
        '''

        # implements is the first base name.
        implements = self._base_name(class_decl, 0)
        if implements:
            payload['implements'] = implements

        # Set idempotent only when delete exists and raises nothing.
        for member in class_decl.members:
            inner = member.inner_decl
            if inner is None or inner.name != 'delete':
                continue
            if not _is_idempotent_delete(inner):
                continue
            methods = payload.get('methods') or {}
            if 'delete' in methods:
                methods['delete']['idempotent'] = True

    # * method: base_name
    def _base_name(self, class_decl: Declaration, index: int) -> Optional[str]:
        '''
        Read a base-class name by chain index.

        :param class_decl: The class declaration.
        :type class_decl: Declaration
        :param index: Zero for the first base, one for the second.
        :type index: int
        :return: The base name, or None.
        :rtype: Optional[str]
        '''

        # The subclass chain starts at the class type's subtype.
        current = class_decl.type.subtype if class_decl.type is not None else None
        depth = 0
        while current is not None and depth < index:
            current = current.subtype
            depth += 1

        # A missing link or an unnamed type is not a base name.
        if current is None or not current.name:
            return None
        return current.name

    # * method: injection_spec
    def _injection_spec(self, param: ParamList,
            descriptions: Dict[str, str]) -> str:
        '''
        Format one injection spec with an empty default slot.

        :param param: The constructor parameter.
        :type param: ParamList
        :param descriptions: Parameter names mapped to docstring descriptions.
        :type descriptions: Dict[str, str]
        :return: ``name:type:required::desc``.
        :rtype: str
        '''

        # required is the literal true or false. The default slot stays empty.
        required = 'true' if param.required else 'false'
        desc = descriptions.get(param.name, '')
        return f'{param.name}:{get_type_name(param.type)}:{required}::{desc}'

    # * method: param_spec
    def _param_spec(self, param: ParamList, descriptions: Dict[str, str]) -> str:
        '''
        Format one parameter spec, including an encoded default.

        :param param: The parameter.
        :type param: ParamList
        :param descriptions: Parameter names mapped to docstring descriptions.
        :type descriptions: Dict[str, str]
        :return: ``name:type:required:default:desc``.
        :rtype: str
        '''

        # A missing default encodes as an empty slot, not the word None.
        default = param.default.encode() if param.default is not None else ''
        required = 'true' if param.required else 'false'
        desc = descriptions.get(param.name, '')
        return f'{param.name}:{get_type_name(param.type)}:{required}:{default}:{desc}'

    # * method: comment_text
    def _comment_text(self, comment: Statement) -> str:
        '''
        Strip a comment marker and trim the remaining text.

        :param comment: The comment statement.
        :type comment: Statement
        :return: The trimmed comment text.
        :rtype: str
        '''

        # Comment text lives on the expression value.
        raw = ''
        if comment.expr is not None and comment.expr.value:
            raw = comment.expr.value

        # Remove one leading hash marker, then trim.
        text = raw.strip()
        if text.startswith('#'):
            text = text[1:]
        return text.strip()
