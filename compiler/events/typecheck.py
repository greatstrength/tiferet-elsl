"""Conformance Checking Domain Events"""

# *** imports

# ** core
from typing import Any, ClassVar, Dict, List

# ** app
from ..mappers import Decl
from ..mappers.semantic import ScopeAggregate
from ..utils.typecheck import ConformanceChecker
from .settings import DomainEvent, a

# *** events

# ** event: conformance_event
class ConformanceEvent(DomainEvent):
    '''
    Run one conformance rule set so findings can collect across a pipeline of events.

    Behavior varies only by ``selector``. The event does not walk the AST itself
    and does not build the cache.
    '''

    # * attribute: selector
    selector: ClassVar[str] = ''

    # * method: build_scopes (static)
    @staticmethod
    def build_scopes(semantic: Dict[str, Any]) -> Dict[str, ScopeAggregate]:
        '''
        Reconstruct live scopes from a dumped semantic result.

        :param semantic: The semantic result, including the dumped symbol table.
        :type semantic: Dict[str, Any]
        :return: Path-to-scope aggregates for the checker.
        :rtype: Dict[str, ScopeAggregate]
        '''

        # Read the dumped scopes. A missing table is an empty registry.
        symbol_table = semantic.get('symbol_table', {})
        raw_scopes = symbol_table.get('scopes', {})

        # Reconstruct live scopes. Do not walk the AST.
        return {
            path: ScopeAggregate(**scope_data)
            for path, scope_data in raw_scopes.items()
        }

    # * method: run_rule_set
    def run_rule_set(self, ast: Decl, semantic: Dict[str, Any],
            cache: Any, provision_prefix: tuple,
            findings: List[Dict] = None) -> List[Dict]:
        '''
        Run this event's selector and append its findings.

        :param ast: The module declaration to check.
        :type ast: Decl
        :param semantic: The semantic result, including the dumped symbol table.
        :type semantic: Dict[str, Any]
        :param cache: The merged provision cache. This event does not build one.
        :type cache: Any
        :param provision_prefix: The namespace prefix the caller passes.
        :type provision_prefix: tuple
        :param findings: Prior findings to prepend. None is an empty list.
        :type findings: List[Dict]
        :return: Prior findings followed by this selector's findings.
        :rtype: List[Dict]
        '''

        # One checker, bound to this event's selector. Do not copy an attaches_to loop.
        scopes = self.build_scopes(semantic)
        checker = ConformanceChecker(
            scopes,
            cache,
            self.selector,
            provision_prefix,
        )
        new_findings = checker.check(ast)

        # Append new findings. Do not mutate the caller's list.
        return (findings or []) + new_findings

# ** event: check_common_conformance
class CheckCommonConformance(ConformanceEvent):
    '''
    Check component-agnostic structural rules and seed the findings list.

    This event is ungated. Later dialect events append to the list it starts.
    '''

    # * attribute: selector
    selector: ClassVar[str] = 'common.'

    # * method: execute
    @DomainEvent.parameters_required(['ast', 'semantic', 'cache', 'provision_prefix'])
    def execute(self,
            ast: Decl,
            semantic: Dict[str, Any],
            cache: Any,
            provision_prefix: tuple,
            findings: List[Dict] = None,
            **kwargs,
        ) -> List[Dict]:
        '''
        Run the common rule set and return accumulated findings.

        :param ast: The module declaration to check.
        :type ast: Decl
        :param semantic: The semantic result, including the dumped symbol table.
        :type semantic: Dict[str, Any]
        :param cache: The merged provision cache. This event does not build one.
        :type cache: Any
        :param provision_prefix: The namespace prefix the caller passes.
        :type provision_prefix: tuple
        :param findings: Prior findings to prepend. None is an empty list.
        :type findings: List[Dict]
        :param kwargs: Middleware keyword arguments, such as logging, caching, and timing. Passed through and not consumed. ``component`` is not read.
        :type kwargs: dict
        :return: Prior findings followed by common findings.
        :rtype: List[Dict]
        '''

        # Delegate to the bound selector. Leave kwargs for middleware.
        return self.run_rule_set(ast, semantic, cache, provision_prefix, findings)

# ** event: check_event_conformance
class CheckEventConformance(ConformanceEvent):
    '''
    Check the events dialect's rules and seed or extend the findings list.

    The event is gated on the requested component type so it runs only for that
    module kind. Gating is configuration, not logic in ``execute``.
    '''

    # * attribute: selector
    selector: ClassVar[str] = 'event.'

    # * method: execute
    @DomainEvent.parameters_required(['ast', 'semantic', 'cache', 'provision_prefix'])
    def execute(self,
            ast: Decl,
            semantic: Dict[str, Any],
            cache: Any,
            provision_prefix: tuple,
            findings: List[Dict] = None,
            **kwargs,
        ) -> List[Dict]:
        '''
        Run the events rule set and return accumulated findings.

        :param ast: The module declaration to check.
        :type ast: Decl
        :param semantic: The semantic result, including the dumped symbol table.
        :type semantic: Dict[str, Any]
        :param cache: The merged provision cache. This event does not build one.
        :type cache: Any
        :param provision_prefix: The namespace prefix the caller passes.
        :type provision_prefix: tuple
        :param findings: Prior findings to prepend. None is an empty list.
        :type findings: List[Dict]
        :param kwargs: Middleware keyword arguments, such as logging, caching, and timing. Passed through and not consumed. ``component`` is not read.
        :type kwargs: dict
        :return: Prior findings followed by events findings.
        :rtype: List[Dict]
        '''

        # Delegate to the bound selector. Leave kwargs for middleware.
        return self.run_rule_set(ast, semantic, cache, provision_prefix, findings)

# ** event: check_asset_conformance
class CheckAssetConformance(ConformanceEvent):
    '''
    Check the assets dialect's rules and seed or extend the findings list.

    The event is gated on the requested component type so it runs only for that
    module kind. Gating is configuration, not logic in ``execute``.
    '''

    # * attribute: selector
    selector: ClassVar[str] = 'asset.'

    # * method: execute
    @DomainEvent.parameters_required(['ast', 'semantic', 'cache', 'provision_prefix'])
    def execute(self,
            ast: Decl,
            semantic: Dict[str, Any],
            cache: Any,
            provision_prefix: tuple,
            findings: List[Dict] = None,
            **kwargs,
        ) -> List[Dict]:
        '''
        Run the assets rule set and return accumulated findings.

        :param ast: The module declaration to check.
        :type ast: Decl
        :param semantic: The semantic result, including the dumped symbol table.
        :type semantic: Dict[str, Any]
        :param cache: The merged provision cache. This event does not build one.
        :type cache: Any
        :param provision_prefix: The namespace prefix the caller passes.
        :type provision_prefix: tuple
        :param findings: Prior findings to prepend. None is an empty list.
        :type findings: List[Dict]
        :param kwargs: Middleware keyword arguments, such as logging, caching, and timing. Passed through and not consumed. ``component`` is not read.
        :type kwargs: dict
        :return: Prior findings followed by assets findings.
        :rtype: List[Dict]
        '''

        # Delegate to the bound selector. Leave kwargs for middleware.
        return self.run_rule_set(ast, semantic, cache, provision_prefix, findings)

# ** event: check_domain_conformance
class CheckDomainConformance(ConformanceEvent):
    '''
    Check the domain dialect's rules and seed or extend the findings list.

    The event is gated on the requested component type so it runs only for that
    module kind. Gating is configuration, not logic in ``execute``.
    '''

    # * attribute: selector
    selector: ClassVar[str] = 'domain.'

    # * method: execute
    @DomainEvent.parameters_required(['ast', 'semantic', 'cache', 'provision_prefix'])
    def execute(self,
            ast: Decl,
            semantic: Dict[str, Any],
            cache: Any,
            provision_prefix: tuple,
            findings: List[Dict] = None,
            **kwargs,
        ) -> List[Dict]:
        '''
        Run the domain rule set and return accumulated findings.

        :param ast: The module declaration to check.
        :type ast: Decl
        :param semantic: The semantic result, including the dumped symbol table.
        :type semantic: Dict[str, Any]
        :param cache: The merged provision cache. This event does not build one.
        :type cache: Any
        :param provision_prefix: The namespace prefix the caller passes.
        :type provision_prefix: tuple
        :param findings: Prior findings to prepend. None is an empty list.
        :type findings: List[Dict]
        :param kwargs: Middleware keyword arguments, such as logging, caching, and timing. Passed through and not consumed. ``component`` is not read.
        :type kwargs: dict
        :return: Prior findings followed by domain findings.
        :rtype: List[Dict]
        '''

        # Delegate to the bound selector. Leave kwargs for middleware.
        return self.run_rule_set(ast, semantic, cache, provision_prefix, findings)

# ** event: check_mapper_conformance
class CheckMapperConformance(ConformanceEvent):
    '''
    Check the mappers dialect's rules and seed or extend the findings list.

    The event is gated on the requested component type so it runs only for that
    module kind. Gating is configuration, not logic in ``execute``.
    '''

    # * attribute: selector
    selector: ClassVar[str] = 'mapper.'

    # * method: execute
    @DomainEvent.parameters_required(['ast', 'semantic', 'cache', 'provision_prefix'])
    def execute(self,
            ast: Decl,
            semantic: Dict[str, Any],
            cache: Any,
            provision_prefix: tuple,
            findings: List[Dict] = None,
            **kwargs,
        ) -> List[Dict]:
        '''
        Run the mappers rule set and return accumulated findings.

        :param ast: The module declaration to check.
        :type ast: Decl
        :param semantic: The semantic result, including the dumped symbol table.
        :type semantic: Dict[str, Any]
        :param cache: The merged provision cache. This event does not build one.
        :type cache: Any
        :param provision_prefix: The namespace prefix the caller passes.
        :type provision_prefix: tuple
        :param findings: Prior findings to prepend. None is an empty list.
        :type findings: List[Dict]
        :param kwargs: Middleware keyword arguments, such as logging, caching, and timing. Passed through and not consumed. ``component`` is not read.
        :type kwargs: dict
        :return: Prior findings followed by mappers findings.
        :rtype: List[Dict]
        '''

        # Delegate to the bound selector. Leave kwargs for middleware.
        return self.run_rule_set(ast, semantic, cache, provision_prefix, findings)

# ** event: check_interface_conformance
class CheckInterfaceConformance(ConformanceEvent):
    '''
    Check the interfaces dialect's rules and seed or extend the findings list.

    The event is gated on the requested component type so it runs only for that
    module kind. Gating is configuration, not logic in ``execute``.
    '''

    # * attribute: selector
    selector: ClassVar[str] = 'interface.'

    # * method: execute
    @DomainEvent.parameters_required(['ast', 'semantic', 'cache', 'provision_prefix'])
    def execute(self,
            ast: Decl,
            semantic: Dict[str, Any],
            cache: Any,
            provision_prefix: tuple,
            findings: List[Dict] = None,
            **kwargs,
        ) -> List[Dict]:
        '''
        Run the interfaces rule set and return accumulated findings.

        :param ast: The module declaration to check.
        :type ast: Decl
        :param semantic: The semantic result, including the dumped symbol table.
        :type semantic: Dict[str, Any]
        :param cache: The merged provision cache. This event does not build one.
        :type cache: Any
        :param provision_prefix: The namespace prefix the caller passes.
        :type provision_prefix: tuple
        :param findings: Prior findings to prepend. None is an empty list.
        :type findings: List[Dict]
        :param kwargs: Middleware keyword arguments, such as logging, caching, and timing. Passed through and not consumed. ``component`` is not read.
        :type kwargs: dict
        :return: Prior findings followed by interfaces findings.
        :rtype: List[Dict]
        '''

        # Delegate to the bound selector. Leave kwargs for middleware.
        return self.run_rule_set(ast, semantic, cache, provision_prefix, findings)

# ** event: check_di_conformance
class CheckDIConformance(ConformanceEvent):
    '''
    Check the di dialect's rules and seed or extend the findings list.

    The event is gated on the requested component type so it runs only for that
    module kind. Gating is configuration, not logic in ``execute``.
    '''

    # * attribute: selector
    selector: ClassVar[str] = 'di.'

    # * method: execute
    @DomainEvent.parameters_required(['ast', 'semantic', 'cache', 'provision_prefix'])
    def execute(self,
            ast: Decl,
            semantic: Dict[str, Any],
            cache: Any,
            provision_prefix: tuple,
            findings: List[Dict] = None,
            **kwargs,
        ) -> List[Dict]:
        '''
        Run the di rule set and return accumulated findings.

        :param ast: The module declaration to check.
        :type ast: Decl
        :param semantic: The semantic result, including the dumped symbol table.
        :type semantic: Dict[str, Any]
        :param cache: The merged provision cache. This event does not build one.
        :type cache: Any
        :param provision_prefix: The namespace prefix the caller passes.
        :type provision_prefix: tuple
        :param findings: Prior findings to prepend. None is an empty list.
        :type findings: List[Dict]
        :param kwargs: Middleware keyword arguments, such as logging, caching, and timing. Passed through and not consumed. ``component`` is not read.
        :type kwargs: dict
        :return: Prior findings followed by di findings.
        :rtype: List[Dict]
        '''

        # Delegate to the bound selector. Leave kwargs for middleware.
        return self.run_rule_set(ast, semantic, cache, provision_prefix, findings)

# ** event: check_utils_conformance
class CheckUtilsConformance(ConformanceEvent):
    '''
    Check the utils dialect's rules and seed or extend the findings list.

    The event is gated on the requested component type so it runs only for that
    module kind. Gating is configuration, not logic in ``execute``.
    '''

    # * attribute: selector
    selector: ClassVar[str] = 'utils.'

    # * method: execute
    @DomainEvent.parameters_required(['ast', 'semantic', 'cache', 'provision_prefix'])
    def execute(self,
            ast: Decl,
            semantic: Dict[str, Any],
            cache: Any,
            provision_prefix: tuple,
            findings: List[Dict] = None,
            **kwargs,
        ) -> List[Dict]:
        '''
        Run the utils rule set and return accumulated findings.

        :param ast: The module declaration to check.
        :type ast: Decl
        :param semantic: The semantic result, including the dumped symbol table.
        :type semantic: Dict[str, Any]
        :param cache: The merged provision cache. This event does not build one.
        :type cache: Any
        :param provision_prefix: The namespace prefix the caller passes.
        :type provision_prefix: tuple
        :param findings: Prior findings to prepend. None is an empty list.
        :type findings: List[Dict]
        :param kwargs: Middleware keyword arguments, such as logging, caching, and timing. Passed through and not consumed. ``component`` is not read.
        :type kwargs: dict
        :return: Prior findings followed by utils findings.
        :rtype: List[Dict]
        '''

        # Delegate to the bound selector. Leave kwargs for middleware.
        return self.run_rule_set(ast, semantic, cache, provision_prefix, findings)

# ** event: check_contexts_conformance
class CheckContextsConformance(ConformanceEvent):
    '''
    Check the contexts dialect's rules and seed or extend the findings list.

    The event is gated on the requested component type so it runs only for that
    module kind. Gating is configuration, not logic in ``execute``.
    '''

    # * attribute: selector
    selector: ClassVar[str] = 'contexts.'

    # * method: execute
    @DomainEvent.parameters_required(['ast', 'semantic', 'cache', 'provision_prefix'])
    def execute(self,
            ast: Decl,
            semantic: Dict[str, Any],
            cache: Any,
            provision_prefix: tuple,
            findings: List[Dict] = None,
            **kwargs,
        ) -> List[Dict]:
        '''
        Run the contexts rule set and return accumulated findings.

        :param ast: The module declaration to check.
        :type ast: Decl
        :param semantic: The semantic result, including the dumped symbol table.
        :type semantic: Dict[str, Any]
        :param cache: The merged provision cache. This event does not build one.
        :type cache: Any
        :param provision_prefix: The namespace prefix the caller passes.
        :type provision_prefix: tuple
        :param findings: Prior findings to prepend. None is an empty list.
        :type findings: List[Dict]
        :param kwargs: Middleware keyword arguments, such as logging, caching, and timing. Passed through and not consumed. ``component`` is not read.
        :type kwargs: dict
        :return: Prior findings followed by contexts findings.
        :rtype: List[Dict]
        '''

        # Delegate to the bound selector. Leave kwargs for middleware.
        return self.run_rule_set(ast, semantic, cache, provision_prefix, findings)

# ** event: check_blueprints_conformance
class CheckBlueprintsConformance(ConformanceEvent):
    '''
    Check the blueprints dialect's rules and seed or extend the findings list.

    The event is gated on the requested component type so it runs only for that
    module kind. Gating is configuration, not logic in ``execute``.
    '''

    # * attribute: selector
    selector: ClassVar[str] = 'blueprints.'

    # * method: execute
    @DomainEvent.parameters_required(['ast', 'semantic', 'cache', 'provision_prefix'])
    def execute(self,
            ast: Decl,
            semantic: Dict[str, Any],
            cache: Any,
            provision_prefix: tuple,
            findings: List[Dict] = None,
            **kwargs,
        ) -> List[Dict]:
        '''
        Run the blueprints rule set and return accumulated findings.

        :param ast: The module declaration to check.
        :type ast: Decl
        :param semantic: The semantic result, including the dumped symbol table.
        :type semantic: Dict[str, Any]
        :param cache: The merged provision cache. This event does not build one.
        :type cache: Any
        :param provision_prefix: The namespace prefix the caller passes.
        :type provision_prefix: tuple
        :param findings: Prior findings to prepend. None is an empty list.
        :type findings: List[Dict]
        :param kwargs: Middleware keyword arguments, such as logging, caching, and timing. Passed through and not consumed. ``component`` is not read.
        :type kwargs: dict
        :return: Prior findings followed by blueprints findings.
        :rtype: List[Dict]
        '''

        # Delegate to the bound selector. Leave kwargs for middleware.
        return self.run_rule_set(ast, semantic, cache, provision_prefix, findings)

# ** event: check_repos_conformance
class CheckReposConformance(ConformanceEvent):
    '''
    Check the repos dialect's rules and seed or extend the findings list.

    The event is gated on the requested component type so it runs only for that
    module kind. Gating is configuration, not logic in ``execute``.
    '''

    # * attribute: selector
    selector: ClassVar[str] = 'repos.'

    # * method: execute
    @DomainEvent.parameters_required(['ast', 'semantic', 'cache', 'provision_prefix'])
    def execute(self,
            ast: Decl,
            semantic: Dict[str, Any],
            cache: Any,
            provision_prefix: tuple,
            findings: List[Dict] = None,
            **kwargs,
        ) -> List[Dict]:
        '''
        Run the repos rule set and return accumulated findings.

        :param ast: The module declaration to check.
        :type ast: Decl
        :param semantic: The semantic result, including the dumped symbol table.
        :type semantic: Dict[str, Any]
        :param cache: The merged provision cache. This event does not build one.
        :type cache: Any
        :param provision_prefix: The namespace prefix the caller passes.
        :type provision_prefix: tuple
        :param findings: Prior findings to prepend. None is an empty list.
        :type findings: List[Dict]
        :param kwargs: Middleware keyword arguments, such as logging, caching, and timing. Passed through and not consumed. ``component`` is not read.
        :type kwargs: dict
        :return: Prior findings followed by repos findings.
        :rtype: List[Dict]
        '''

        # Delegate to the bound selector. Leave kwargs for middleware.
        return self.run_rule_set(ast, semantic, cache, provision_prefix, findings)
