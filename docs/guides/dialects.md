# Dialects – Strategies and Patterns

**Project:** tiferet-elsl  
**Repository:** https://github.com/greatstrength/tiferet-elsl  
**Module:** `compiler/utils/typecheck.py`, `compiler/events/typecheck.py`  
**Version:** 1.0.0

## Overview

Conformance is one reader and ten gated rulebooks, plus the ungated `COMMON_RULE_SET`. The ten run only when `feature.yml` gates them on the requested component type. The event that owns a rulebook does not decide whether it runs.

**Vision:** See the `ConformanceEvent` docstring in `compiler/events/typecheck.py` and the `ConformanceChecker` docstring in `compiler/utils/typecheck.py`.

## Ubiquitous Language

- **Dialect** — the rulebook for one Tiferet component type. The type is a CLI choice, not a package in this repo.
- **Rule set** — a `List[Specification]` constant in `compiler/utils/typecheck.py`. Behavior varies only by which list is bound.
- **Specification** — a pass/fail attachment in `compiler/utils/core.py`. It records findings. It does not mutate the candidate.
- **Conformance event** — a `ConformanceEvent` subclass that binds one rule set and appends that set's findings. It does not walk the AST.
- **Gate** — a `condition` on a feature step in `compiler/assets/feature.yml`. The gate is configuration. It is not a branch in `execute`.
- **Finding** — a dict the checker collects. Prior findings stay in front. The caller's list is not mutated.

## One Reader, Not a Subclass

`ConformanceChecker` walks a module once and collects findings for the rule set it was given. A later dialect adds a constant list, not a subclass.

`ConformanceEvent` is the event side of that decision. Behavior varies only by `rule_set`. `run_rule_set` rebuilds scopes from the dumped symbol table, constructs one checker, and returns `(findings or []) + new_findings`. It does not walk the AST, and it does not mutate the caller's list.

Do not copy an `attaches_to` loop into an event. The checker is the reader.

## Specifications Stay in core.py

`Specification` lives in `compiler/utils/core.py`. A candidate satisfies a specification when evaluation returns no findings. The rule-set constants in `compiler/utils/typecheck.py` are the lists of those specifications.

This guide names the constants and the events that bind them. It does not transcribe the specifications. Read the constant. Do not copy it into a second home.

## COMMON_RULE_SET Is Ungated

`CheckCommonConformance` binds `COMMON_RULE_SET`. Its feature step, `check_common_conformance_event`, has no `condition`. The event is ungated. Later dialect events append to the list it starts.

The pipelines in `compiler/assets/feature.yml` always run this step before any gated dialect step, on `semantic.module`, `compile.module`, and `compile.ast`. Scan and parse do not run it.

The constant is the component-agnostic structural rulebook: import groups, section and function names, members, and expression types. The specification list stays in the constant.

## The Ten Rulebooks

Each gated constant is bound by one event. The feature step names that event's `service_id`. The `condition` is the gate. The strings below are the document text, not a paraphrase.

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

The table follows `feature.yml` step order. That order is not a schema lock. The names are the decision.

The component choice is the CLI string. Several constants and service ids use a shorter stem (`ASSET_RULE_SET`, `check_asset_conformance_event`, `MAPPER_RULE_SET`, `INTERFACE_RULE_SET`). The contexts row does not line up internally: the constant and the class are plural (`CONTEXTS_RULE_SET`, `CheckContextsConformance`), the `service_id` is singular (`check_context_conformance_event`), and the choice is `contexts`. Do not treat any of those differences as a typo.

A dialect event's docstring says it can seed or extend the findings list. In the three pipelines that include conformance, common runs first and the dialect event extends. Calling a dialect event alone can seed, because `findings` defaults to an empty list. Do not add a gate inside `execute` to force one or the other.

## Gating Is feature.yml, Not execute

Every gated event says the same thing: gating is configuration, not logic in `execute`. `execute` requires `ast` and `semantic`. It accepts prior `findings`. `component` is not read. `kwargs` are passed through and not consumed.

The gate is the step `condition` in `compiler/assets/feature.yml`. Removing a condition makes that dialect run for every component. Adding an `if component` branch in `execute` does not replace the gate, and it contradicts the event contract.

`GenerateCode` is the pipeline step that reads `component`, and it reads it as a generator kind. That is not a conformance gate. See [pipeline.md](pipeline.md).

All eleven conformance steps, including the ungated common step, write `data_key: findings`. Findings accumulate across the steps that actually run. A skipped gate does not clear the list.

## Adding a Rulebook

A new dialect is a constant list, an event that does not read `component`, and a `feature.yml` condition. It is not a `ConformanceChecker` subclass.

1. Add a `*_RULE_SET` constant in `compiler/utils/typecheck.py`. Put new specifications in `compiler/utils/core.py`, not in the event.
2. Bind that constant on a `ConformanceEvent` whose `execute` does not read `component`.
3. Register the `service_id` in `compiler/assets/config.yml` to that class. Do not guess the class from the step name.
4. Gate the step in `compiler/assets/feature.yml` with `$r.component == '<choice>'`. Anchor it once and alias it onto semantic, `compile.module`, and `compile.ast`.
5. A new component choice is a freeze decision, not a dialect-only edit. See [schema.md](schema.md).

## Boundaries

**Inside this domain:** which rule set runs for which component, and the decision that the gate is `feature.yml` rather than `execute`.

**Outside this domain:** specification bodies (`compiler/utils/core.py`); phase order and which event owns which step ([pipeline.md](pipeline.md)); the locked command and choice names ([schema.md](schema.md)); the catalogues and recognition engine (`tiferet-ly`). This package has no `contexts`, `blueprints`, `di`, or `repos` of its own. Those names are target dialects, not local packages.

The draft vision and distillation are not the source for this guide. Code wins.

## Related Documentation

- [pipeline.md](pipeline.md) — component-agnostic phases and which event owns which step
- [schema.md](schema.md) — the frozen component choices, and why a new choice is a freeze decision
- `compiler/utils/typecheck.py` — the rule-set constants and `ConformanceChecker`
- `compiler/utils/core.py` — `Specification` and the specification classes
- `compiler/events/typecheck.py` — the conformance events
- `compiler/assets/feature.yml` — the gates
- [docs/core/code_style.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/code_style.md) — artifact comments and formatting; style law stays on the Tiferet skills
- [`.agents/skills/elsl-dialects`](../../.agents/skills/elsl-dialects/SKILL.md) — procedure for changing a rule set, a specification, or a gated conformance event
