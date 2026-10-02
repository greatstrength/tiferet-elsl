---
name: elsl-conformance
description: >
  Use when adding or changing a gated conformance event, or the feature.yml
  condition that gates it. Phrases: "gate a conformance check", "conformance
  event", "component condition", "check_event_conformance". Not for the
  specification lists, and not for other pipeline wiring.
---

# Change a conformance event

## When to use
- Adding or changing a `ConformanceEvent` subclass.
- Changing the `feature.yml` condition that gates a conformance step.

## When not to use
- The specification lists inside a rule set — `elsl-rule-sets`.
- Pipeline wiring other than that condition — `elsl-pipeline`.
- A new component choice — `elsl-schema`.
- Code style, TRDs, RFPs, or reports — the Tiferet skills. Do not vendor them.

## Canonical source
- `compiler/events/typecheck.py`
- `compiler/assets/feature.yml`
- `compiler/assets/config.yml`

## Inputs
- The conformance event, or the component type being gated.
- `docs/collab/binding.md`. A GitHub issue. **Trunk** also needs a published TRD and a freeze id. **Prototype** needs a published RFP, and only if that strand is active.

## Catalog

`CheckCommonConformance` binds `COMMON_RULE_SET`. Its step has no `condition`. It is ungated and runs first on `semantic.module`, `compile.module`, and `compile.ast`.

| Constant | Event | `service_id` | Gate |
|---|---|---|---|
| `EVENT_RULE_SET` | `CheckEventConformance` | `check_event_conformance_event` | `$r.component == 'events'` |
| `ASSET_RULE_SET` | `CheckAssetConformance` | `check_asset_conformance_event` | `$r.component == 'assets'` |
| `DOMAIN_RULE_SET` | `CheckDomainConformance` | `check_domain_conformance_event` | `$r.component == 'domain'` |
| `MAPPER_RULE_SET` | `CheckMapperConformance` | `check_mapper_conformance_event` | `$r.component == 'mappers'` |
| `INTERFACE_RULE_SET` | `CheckInterfaceConformance` | `check_interface_conformance_event` | `$r.component == 'interfaces'` |
| `DI_RULE_SET` | `CheckDIConformance` | `check_di_conformance_event` | `$r.component == 'di'` |
| `UTILS_RULE_SET` | `CheckUtilsConformance` | `check_utils_conformance_event` | `$r.component == 'utils'` |
| `CONTEXTS_RULE_SET` | `CheckContextsConformance` | `check_context_conformance_event` | `$r.component == 'contexts'` |
| `BLUEPRINTS_RULE_SET` | `CheckBlueprintsConformance` | `check_blueprints_conformance_event` | `$r.component == 'blueprints'` |
| `REPOS_RULE_SET` | `CheckReposConformance` | `check_repos_conformance_event` | `$r.component == 'repos'` |

Shorter stems are not typos: `ASSET_RULE_SET`, `MAPPER_RULE_SET`, `INTERFACE_RULE_SET`. The contexts row does not line up internally: constant and class are plural, `service_id` is singular, choice is `contexts`.

Every conformance `service_id` is registered in `compiler/assets/config.yml` to `compiler.events.typecheck` and the class in the table.

## Example

A gated event does not read `component`. The gate is the YAML condition.

```python
# ** event: check_event_conformance
class CheckEventConformance(ConformanceEvent):
    '''
    Check the events dialect's rules and seed or extend the findings list.
    '''

    # * attribute: rule_set
    rule_set: ClassVar[List[Specification]] = EVENT_RULE_SET

    # * method: execute
    @DomainEvent.parameters_required(['ast', 'semantic'])
    def execute(self, ast: Decl, semantic: Dict[str, Any],
            findings: List[Dict] = None, **kwargs) -> List[Dict]:
        '''
        Run the events rule set and return accumulated findings.
        '''

        # Delegate to the bound rule set. Leave kwargs for middleware.
        return self.run_rule_set(ast, semantic, findings)
```

```yaml
- &event_conformance_step
  name: Check Event Conformance
  service_id: check_event_conformance_event
  data_key: findings
  condition: "$r.component == 'events'"
```

`run_rule_set` rebuilds scopes from the dumped symbol table, constructs one `ConformanceChecker`, and returns `(findings or []) + new_findings`. It does not mutate the caller's list.

## Procedure
1. Bind one `*_RULE_SET` on a `ConformanceEvent`. Do not walk the AST in the event. Do not read `component` in `execute`.
2. Register `service_id` in `compiler/assets/config.yml` to that class. Do not guess the class from the step name.
3. Gate the step in `compiler/assets/feature.yml`. Anchor it once and alias it onto semantic, `compile.module`, and `compile.ast`.
4. New specifications go in `compiler/utils/core.py` and onto the constant in `compiler/utils/typecheck.py`. Use `elsl-rule-sets` for the current lists.
5. A new component choice is `elsl-schema`.
6. **Trunk** — implement against the published TRD. Do not copy from proto.
7. **Prototype** — only if binding.md says the prototype strand is active.

## Outputs
- The event, the registration, and the `feature.yml` condition on the strand branch, in a PR to that strand. Not an issue body.

## Guardrails
- Never commit or merge unless asked.
- Never proto → trunk git.
- Never implement trunk reconstruction from a live proto branch.
- Never author a reconstruction TRD without a freeze id.
- Read `docs/collab/binding.md` in this repo for owner/repo, proto branch, and project ids.
- Do not vendor Tiferet skills into this repo.
- Do not read `component` inside `execute`. The gate is YAML.
- Do not treat a guide as the source for this catalog.
