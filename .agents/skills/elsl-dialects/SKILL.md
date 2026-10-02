---
name: elsl-dialects
description: >
  Use when adding or changing a rule set, a specification, or a gated
  conformance event. Phrases: "add a dialect rule", "new specification",
  "gate a conformance check", "component rule set", "conformance event".
  Not for pipeline wiring except the feature.yml condition.
---

# Change a dialect rule set

## When to use

- Adding or changing a rule set, a specification, or a gated conformance event.
- Changing the `feature.yml` condition that gates a conformance step.

## When not to use

- Pipeline wiring other than that condition — `elsl-pipeline`.
- A frozen-surface rename — `elsl-schema`.
- Code style, TRDs, RFPs, or reports — the Tiferet skills. Do not vendor them.

## Canonical source

- `docs/guides/dialects.md`
- Do not transcribe specifications or rule-set constants here. Point, then add only the operator steps.

## Inputs

- The rule set, specification, or conformance event being changed.
- The component type, if the rule is gated. The common rule set is ungated.
- `docs/collab/binding.md`. A GitHub issue. **Trunk** also needs a published TRD and a freeze id. **Prototype** needs a published RFP, and only if that strand is active.

## Procedure

1. Read `docs/guides/dialects.md`. The guide names the constants and their events. Do not copy that list here.
2. Rule-set constants live in `compiler/utils/typecheck.py`. Specifications live in `compiler/utils/core.py`. Gated conformance events live in `compiler/events/typecheck.py`. Edit the artifact the change needs.
3. Put the gate in `compiler/assets/feature.yml` as a step `condition`. `execute` does not read `component`.
4. Do not rewire phases, commands, or other steps.
5. **Trunk** — implement against the published TRD. Do not copy from proto.
6. **Prototype** — only if binding.md says the prototype strand is active. Implement against the published RFP on the proto branch named there. Do not cut that branch from this skill.

## Outputs

- The rule, specification, or event change on the strand branch, in a PR to that strand. The gate, if any, is the `feature.yml` condition in that same change. Not an issue body.

## Guardrails

- Never commit or merge unless asked.
- Never proto → trunk git.
- Never implement trunk reconstruction from a live proto branch.
- Never author a reconstruction TRD without a freeze id.
- Read `docs/collab/binding.md` in this repo for owner/repo, proto branch, and project ids.
- Do not vendor Tiferet skills into this repo.
- Do not read `component` inside `execute`. The gate is YAML.
