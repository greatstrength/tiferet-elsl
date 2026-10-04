"""Compiler Provision Domain Objects"""

# *** imports

# ** core
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Literal

# ** infra
from pydantic import Field

# ** app
from tiferet.domain.core import DomainObject

# *** constants

# ** constant: provision_kind_specification
PROVISION_KIND_SPECIFICATION = 'specification'

# ** constant: provision_kind_production
PROVISION_KIND_PRODUCTION = 'production'

# ** constant: provision_kind_rewrite
PROVISION_KIND_REWRITE = 'rewrite'

# *** models

# ** model: provision
class Provision(DomainObject):
    '''
    A visit rule a walker calls by hook.

    It names the rule and the hook it handles, so a host can invoke every
    provision the same way and leave kind-specific work on the specialization.
    '''

    # * attribute: id
    id: str = Field(
        ...,
        description='The unique provision id.',
    )

    # * attribute: applies_to
    applies_to: str = Field(
        ...,
        description='The visit hook this provision handles.',
    )

    # * method: attaches_to
    def attaches_to(self, hook: str) -> bool:
        '''
        Report whether this provision applies to a visit hook.

        :param hook: The visit hook the host is entering.
        :type hook: str
        :return: True when the hook equals ``applies_to``.
        :rtype: bool
        '''

        # Match the stored visit hook exactly.
        return self.applies_to == hook

    # * method: __call__
    def __call__(self, candidate: Any, context: Any) -> Any:
        '''
        Invoke this provision on a candidate.

        :param candidate: The node being visited.
        :type candidate: Any
        :param context: The host visit context.
        :type context: Any
        :return: Never returns.
        :rtype: Any
        :raises NotImplementedError: Specializations override this method.
        '''

        # The parent provision has no kind-specific implementation.
        raise NotImplementedError

# ** model: specification
class Specification(Provision, ABC):
    '''
    A pass/fail provision that records findings instead of mutating the candidate.

    A candidate satisfies the specification when evaluation returns no findings.
    '''

    # * method: evaluate
    @abstractmethod
    def evaluate(self, candidate: Any, context: Any) -> List[Dict]:
        '''
        Evaluate the candidate and return any findings.

        :param candidate: The node being visited.
        :type candidate: Any
        :param context: The host visit context.
        :type context: Any
        :return: Finding dicts, empty when the candidate is satisfactory.
        :rtype: List[Dict]
        '''

    # * method: __call__
    def __call__(self, candidate: Any, context: Any) -> List[Dict]:
        '''
        Evaluate the candidate through the callable host contract.

        :param candidate: The node being visited.
        :type candidate: Any
        :param context: The host visit context.
        :type context: Any
        :return: The findings from ``evaluate``.
        :rtype: List[Dict]
        '''

        # Hosts and combinators call the provision; evaluation stays behind that call.
        return self.evaluate(candidate, context)

    # * method: is_satisfied_by
    def is_satisfied_by(self, candidate: Any, context: Any) -> bool:
        '''
        Report whether the candidate produces no findings.

        :param candidate: The node being visited.
        :type candidate: Any
        :param context: The host visit context.
        :type context: Any
        :return: True when evaluation returns no findings.
        :rtype: bool
        '''

        # An empty finding list is satisfaction.
        return not self.evaluate(candidate, context)

# ** model: production
class Production(Provision, ABC):
    '''
    A provision that writes into the accumulator the context supplies.

    Productions do not pass or fail. They record what the visit found.
    '''

    # * method: apply
    @abstractmethod
    def apply(self, candidate: Any, context: Any) -> None:
        '''
        Record the candidate into the context accumulator.

        :param candidate: The node being visited.
        :type candidate: Any
        :param context: The host visit context.
        :type context: Any
        :return: None
        :rtype: None
        '''

    # * method: __call__
    def __call__(self, candidate: Any, context: Any) -> None:
        '''
        Apply the production through the callable host contract.

        :param candidate: The node being visited.
        :type candidate: Any
        :param context: The host visit context.
        :type context: Any
        :return: None
        :rtype: None
        '''

        # Hosts call the provision; recording stays behind that call.
        return self.apply(candidate, context)

# ** model: rewrite
class Rewrite(Provision, ABC):
    '''
    A provision that returns a contribution the host merges, or None.

    Rewrites do not decide pass or fail. The host owns the merge.
    '''

    # * method: apply
    @abstractmethod
    def apply(self, candidate: Any, context: Any) -> Any:
        '''
        Produce a contribution for the host to merge.

        :param candidate: The node being visited.
        :type candidate: Any
        :param context: The host visit context.
        :type context: Any
        :return: The contribution, or None.
        :rtype: Any
        '''

    # * method: __call__
    def __call__(self, candidate: Any, context: Any) -> Any:
        '''
        Apply the rewrite through the callable host contract.

        :param candidate: The node being visited.
        :type candidate: Any
        :param context: The host visit context.
        :type context: Any
        :return: The contribution from ``apply``.
        :rtype: Any
        '''

        # Hosts call the provision; the contribution stays behind that call.
        return self.apply(candidate, context)

# ** model: all_of
class AllOf(Specification):
    '''
    A specification that is satisfied only when every child is satisfied.

    Findings are concatenated in child order so a host can report every failure.
    '''

    # * attribute: specs
    specs: List[Specification] = Field(
        default_factory=list,
        description='The child specifications. An omitted list is an empty conjunction.',
    )

    # * method: evaluate
    def evaluate(self, candidate: Any, context: Any) -> List[Dict]:
        '''
        Concatenate every child's findings in child order.

        :param candidate: The node being visited.
        :type candidate: Any
        :param context: The host visit context.
        :type context: Any
        :return: The concatenated findings.
        :rtype: List[Dict]
        '''

        # Call each child as an attachment, preserving child order.
        findings = []
        for spec in self.specs:
            findings.extend(spec(candidate, context))

        # Return every finding, including when the list is empty.
        return findings

# ** model: any_of
class AnyOf(Specification):
    '''
    A specification that is satisfied when any child is satisfied.

    Concatenated findings surface only when every child is unsatisfied.
    '''

    # * attribute: specs
    specs: List[Specification] = Field(
        default_factory=list,
        description='The child specifications. An omitted list is an empty disjunction.',
    )

    # * method: evaluate
    def evaluate(self, candidate: Any, context: Any) -> List[Dict]:
        '''
        Return no findings when any child is satisfied.

        :param candidate: The node being visited.
        :type candidate: Any
        :param context: The host visit context.
        :type context: Any
        :return: An empty list when any child is satisfied; otherwise concatenated findings.
        :rtype: List[Dict]
        '''

        # Call each child as an attachment before deciding satisfaction.
        results = [spec(candidate, context) for spec in self.specs]
        if any(not result for result in results):
            return []

        # Every child failed, so surface the concatenated findings.
        findings = []
        for result in results:
            findings.extend(result)
        return findings

# ** model: not
class Not(Specification):
    '''
    A specification that negates one child.

    Satisfaction of the child is itself a violation of the negation.
    '''

    # * attribute: spec
    spec: Specification = Field(
        ...,
        description='The child specification this negation wraps.',
    )

    # * method: evaluate
    def evaluate(self, candidate: Any, context: Any) -> List[Dict]:
        '''
        Violate when the child is satisfied.

        :param candidate: The node being visited.
        :type candidate: Any
        :param context: The host visit context.
        :type context: Any
        :return: One finding when the child is satisfied; otherwise an empty list.
        :rtype: List[Dict]
        '''

        # A satisfied child violates the negation.
        if not self.spec(candidate, context):
            return [{
                'error_code': f'{self.id}_VIOLATION'.upper(),
                'message': (
                    f'Candidate unexpectedly satisfied negated specification "{self.spec.id}".'
                ),
            }]

        # An unsatisfied child satisfies the negation.
        return []

# ** model: provision_registration
class ProvisionRegistration(DomainObject):
    '''
    The data needed to name one provision in a catalog.

    It describes a provision and holds no behavior, so a later seeder can
    reinject the group-dict key as ``id`` without constructing the rule.
    '''

    # * attribute: id
    id: str = Field(
        ...,
        description='The provision id, reinjected from the group-dict key at seed time.',
    )

    # * attribute: kind
    kind: Literal[
        'specification',
        'production',
        'rewrite',
    ] = Field(
        ...,
        description='The provision kind.',
    )

    # * attribute: applies_to
    applies_to: str = Field(
        ...,
        description='The visit hook the named class will be constructed with.',
    )

    # * attribute: module_path
    module_path: str = Field(
        ...,
        description='The module that defines the class.',
    )

    # * attribute: class_name
    class_name: str = Field(
        ...,
        description='The class.',
    )

    # * attribute: parameters
    parameters: Dict[str, Any] = Field(
        default_factory=dict,
        description='Constructor arguments beyond id and applies_to. Data only.',
    )
