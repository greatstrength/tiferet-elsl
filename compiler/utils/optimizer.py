"""YAML Anchor/Alias Optimizer Utility"""

# *** imports

# ** core
from importlib import import_module
from typing import Any, Dict, List, Optional, Tuple

# ** app
from ..interfaces.optimizer import OptimizerService
from ..mappers import Rewrite
from .core import RewriteContext

# *** constants

# ** constant: optimizer_evt_grp_envelope_id
OPTIMIZER_EVT_GRP_ENVELOPE_ID = 'optimizer.evt_grp_envelope'

# ** constant: optimizer_evt_grp_envelope_applies_to
OPTIMIZER_EVT_GRP_ENVELOPE_APPLIES_TO = 'evt_grp'

# ** constant: optimizer_cmpt_envelope_id
OPTIMIZER_CMPT_ENVELOPE_ID = 'optimizer.cmpt_envelope'

# ** constant: optimizer_cmpt_envelope_applies_to
OPTIMIZER_CMPT_ENVELOPE_APPLIES_TO = 'cmpt'

# ** constant: optimizer_callable_id
OPTIMIZER_CALLABLE_ID = 'optimizer.callable'

# ** constant: optimizer_callable_applies_to
OPTIMIZER_CALLABLE_APPLIES_TO = 'callable'

# *** functions

# ** function: create_optimizer_rewrite
def create_optimizer_rewrite(flag: str) -> Rewrite:
    '''
    Load one rewrite class by flag, the way a flagged dependency is resolved.

    :param flag: The envelope flag: ``evt_grp``, ``cmpt``, or ``callable``.
    :type flag: str
    :return: The rewrite for that flag.
    :rtype: Rewrite
    '''

    # Map the flag to a module path and class name. Do not name the class object.
    dependencies = {
        OPTIMIZER_EVT_GRP_ENVELOPE_APPLIES_TO: {
            'module_path': 'compiler.utils.optimizer',
            'class_name': 'EvtGrpEnvelopeRewrite',
            'id': OPTIMIZER_EVT_GRP_ENVELOPE_ID,
            'applies_to': OPTIMIZER_EVT_GRP_ENVELOPE_APPLIES_TO,
        },
        OPTIMIZER_CMPT_ENVELOPE_APPLIES_TO: {
            'module_path': 'compiler.utils.optimizer',
            'class_name': 'CmptEnvelopeRewrite',
            'id': OPTIMIZER_CMPT_ENVELOPE_ID,
            'applies_to': OPTIMIZER_CMPT_ENVELOPE_APPLIES_TO,
        },
        OPTIMIZER_CALLABLE_APPLIES_TO: {
            'module_path': 'compiler.utils.optimizer',
            'class_name': 'CallableRewrite',
            'id': OPTIMIZER_CALLABLE_ID,
            'applies_to': OPTIMIZER_CALLABLE_APPLIES_TO,
        },
    }
    dependency = dependencies[flag]

    # Import the named class from its module path.
    rewrite_cls = getattr(
        import_module(dependency['module_path']),
        dependency['class_name'],
    )

    # Construct with that flag's singular id and applies_to constants.
    return rewrite_cls(
        id=dependency['id'],
        applies_to=dependency['applies_to'],
    )

# *** classes

# ** class: callable_rewrite
class CallableRewrite(Rewrite):
    '''
    Record one callable's params and returns lists so identical lists can share one object.

    PyYAML emits an anchor only when the same Python object appears twice, so each declared list is remembered by fingerprint rather than copied here.
    '''

    # * method: _record
    def _record(self, candidate: Dict, key: str, accumulator: Dict) -> None:
        '''
        Append one declared list location under its fingerprint.

        :param candidate: The callable dict that owns the list.
        :type candidate: Dict
        :param key: The list key, ``params`` or ``returns``.
        :type key: str
        :param accumulator: Fingerprint-to-locations collector.
        :type accumulator: Dict
        :return: None
        :rtype: None
        '''

        # A missing key is not an empty list; only declared lists are collected.
        if key not in candidate:
            return

        # Kind is part of the fingerprint so params and returns never collapse together.
        fingerprint = (key, tuple(candidate[key]))
        accumulator.setdefault(fingerprint, []).append((candidate, key))

    # * method: apply
    def apply(self, candidate: Any, context: Any) -> None:
        '''
        Record params and returns locations on the context accumulator.

        :param candidate: An execute, method, or function dict.
        :type candidate: Any
        :param context: The rewrite visit context.
        :type context: Any
        :return: None
        :rtype: None
        '''

        # Non-dicts have no lists to share.
        if not isinstance(candidate, dict):
            return None

        # Record each declared list without replacing it yet.
        self._record(candidate, 'params', context.accumulator)
        self._record(candidate, 'returns', context.accumulator)
        return None

# ** class: evt_grp_envelope_rewrite
class EvtGrpEnvelopeRewrite(Rewrite):
    '''
    Walk the legacy evt_grp envelope and collect lists from each event callable.

    Module-level functions stay on the component envelope so a dual-emitted document is not counted twice.
    '''

    # * method: apply
    def apply(self, candidate: Any, context: Any) -> None:
        '''
        Collect execute and method lists from each event.

        :param candidate: The evt_grp dict.
        :type candidate: Any
        :param context: The rewrite visit context.
        :type context: Any
        :return: None
        :rtype: None
        '''

        # The callable rewrite is resolved from the host, not constructed here.
        callable_rewrite = context.host.match_rewrite('callable')
        if callable_rewrite is None or not isinstance(candidate, dict):
            return None

        # Walk events only. Module-level fncs belong to the component envelope.
        for event in (candidate.get('evts') or {}).values():
            if not isinstance(event, dict):
                continue

            callable_rewrite(event.get('execute') or {}, context)
            for method in (event.get('methods') or {}).values():
                callable_rewrite(method, context)

        return None

# ** class: cmpt_envelope_rewrite
class CmptEnvelopeRewrite(Rewrite):
    '''
    Walk a cmpt envelope and collect lists from class-shaped payloads and functions.

    Another component kind is another payload key on this rewrite, not a change to optimize.
    '''

    # * method: _walk_class_entry
    def _walk_class_entry(self, entry: Any, callable_rewrite: Rewrite, context: Any) -> None:
        '''
        Collect the execute callable and each method on one class-shaped entry.

        :param entry: One class, event, model, mapper, interface, context, or repo dict.
        :type entry: Any
        :param callable_rewrite: The rewrite that records params and returns.
        :type callable_rewrite: Rewrite
        :param context: The rewrite visit context.
        :type context: Any
        :return: None
        :rtype: None
        '''

        # Skip a payload value that is not a class-shaped dict.
        if not isinstance(entry, dict):
            return

        # execute defaults to an empty dict when the class has no execute method.
        callable_rewrite(entry.get('execute') or {}, context)

        # Non-execute methods are keyed by name.
        for method in (entry.get('methods') or {}).values():
            callable_rewrite(method, context)

    # * method: _walk_group
    def _walk_group(self, group: Any, callable_rewrite: Rewrite, context: Any) -> None:
        '''
        Collect lists from one group's class-shaped payloads and functions.

        :param group: One item of ``cmpt.grps``.
        :type group: Any
        :param callable_rewrite: The rewrite that records params and returns.
        :type callable_rewrite: Rewrite
        :param context: The rewrite visit context.
        :type context: Any
        :return: None
        :rtype: None
        '''

        # Groups that are not dicts have no payload keys to walk.
        if not isinstance(group, dict):
            return

        # Class-shaped payloads share execute plus methods. Skip a missing or empty key.
        for key in ('evts', 'clss', 'mdls', 'mprs', 'ifcs', 'ctxs', 'repos'):
            payload = group.get(key)
            if not payload or not isinstance(payload, dict):
                continue

            for entry in payload.values():
                self._walk_class_entry(entry, callable_rewrite, context)

        # Functions are callables themselves, not class-shaped wrappers.
        functions = group.get('fncs')
        if not functions or not isinstance(functions, dict):
            return

        for function in functions.values():
            callable_rewrite(function, context)

    # * method: apply
    def apply(self, candidate: Any, context: Any) -> None:
        '''
        Collect callable lists from every group in the component envelope.

        :param candidate: The cmpt dict.
        :type candidate: Any
        :param context: The rewrite visit context.
        :type context: Any
        :return: None
        :rtype: None
        '''

        # The callable rewrite is resolved from the host, not constructed here.
        callable_rewrite = context.host.match_rewrite('callable')
        if callable_rewrite is None or not isinstance(candidate, dict):
            return None

        # Each group is independent; a missing grps list collects nothing.
        for group in candidate.get('grps', []):
            self._walk_group(group, callable_rewrite, context)

        return None

# *** utils

# ** util: yaml_anchor_optimizer
class YamlAnchorOptimizer(OptimizerService):
    '''
    Share repeated params and returns lists in a codegen dict so PyYAML can emit anchors and aliases.

    When nothing repeats, the input dict is returned unchanged and no vars key is invented.
    '''

    # * attribute: rewrites
    rewrites: List[Rewrite]

    # * init
    def __init__(self, rewrites: Optional[List[Rewrite]] = None) -> None:
        '''
        Store the rewrite set used to collect lists.

        :param rewrites: The rewrite set, or None to load one rewrite per flag.
        :type rewrites: Optional[List[Rewrite]]
        :return: None
        :rtype: None
        '''

        # Omitted rewrites load one instance per flag, evt_grp then cmpt then callable.
        self.rewrites = rewrites if rewrites is not None else [
            create_optimizer_rewrite(flag)
            for flag in (
                OPTIMIZER_EVT_GRP_ENVELOPE_APPLIES_TO,
                OPTIMIZER_CMPT_ENVELOPE_APPLIES_TO,
                OPTIMIZER_CALLABLE_APPLIES_TO,
            )
        ]

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

    # * method: collect_lists
    def collect_lists(self, codegen: Dict[str, Any]) -> Dict[Tuple, List[Tuple[Dict, str]]]:
        '''
        Collect list locations from the first rewrite whose hook is a codegen key.

        :param codegen: Codegen dict from the generator.
        :type codegen: Dict[str, Any]
        :return: Fingerprints mapped to parent and key locations.
        :rtype: Dict[Tuple, List[Tuple[Dict, str]]]
        '''

        # Start with an empty fingerprint-to-locations collector.
        collected: Dict[Tuple, List[Tuple[Dict, str]]] = {}

        # Dispatch only the first matching envelope so evt_grp precedes cmpt.
        for rewrite in self.rewrites:
            if rewrite.applies_to not in codegen:
                continue

            rewrite(
                codegen[rewrite.applies_to],
                RewriteContext(
                    host=self,
                    accumulator=collected,
                ),
            )
            break

        # Return the collector, empty when no envelope key matched.
        return collected

    # * method: optimize
    def optimize(self, codegen: Dict[str, Any]) -> Dict[str, Any]:
        '''
        Share repeated lists and expose the canonical objects under vars.

        :param codegen: Codegen dict from the generator.
        :type codegen: Dict[str, Any]
        :return: The input unchanged when nothing repeats; otherwise a dict with vars first.
        :rtype: Dict[str, Any]
        '''

        # Collect every candidate list from the preferred envelope.
        locations = self.collect_lists(codegen)

        # Replace each duplicated list with one shared object, in fingerprint order.
        vars_list = []
        for (_kind, values), entries in locations.items():
            if len(entries) < 2:
                continue

            canonical = list(values)
            vars_list.append(canonical)
            for parent, key in entries:
                parent[key] = canonical

        # Omit vars entirely when no list was shared.
        if not vars_list:
            return codegen

        # Keep the original keys after vars so the anchor table is first.
        return {'vars': vars_list, **codegen}
