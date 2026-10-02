---
name: elsl-pipeline
description: >
  Use when changing a compiler phase, a feature step, a CLI command, or an
  event that is a pipeline step. Phrases: "add a pipeline step", "change a
  phase", "wire a CLI command", "edit scan.module", "parse.module",
  "semantic.module", "compile.module", "compile.ast". Not for dialect rule
  text or a frozen-surface rename.
---

# Change a compiler pipeline step

## When to use

- Changing a phase, a feature step, a CLI command, or an event that is a pipeline step.
- Wiring or reordering `scan.module`, `parse.module`, `semantic.module`, `compile.module`, or `compile.ast`.

## When not to use

- Dialect rule text, a specification, or a gated conformance check — `elsl-dialects`. The `feature.yml` condition that gates a conformance step belongs there.
- A frozen-surface rename — `elsl-schema`.
- Code style, TRDs, RFPs, or reports — the Tiferet skills. Do not vendor them.

## Canonical source

- `docs/guides/pipeline.md`
- Do not duplicate the step list here. Point, then add only the operator steps.
- The `tiferet-ly` boundary is in that guide. Do not restate it.

## Inputs

- The phase, command, or event being changed.
- `docs/collab/binding.md` for strand, owner/repo, and proto branch.
- A GitHub issue. **Trunk** reconstruction also needs a published TRD and a freeze id. **Prototype** work needs a published RFP, and only if binding.md says that strand is active.

## Procedure

1. Read `docs/guides/pipeline.md`. Do not copy its step list into the change.
2. Read `compiler/assets/feature.yml` and `compiler/assets/cli.yml`.
3. Follow the step `service_id` to the event. The map is `compiler/assets/config.yml` (`services` → `module_path` / `class_name`). Edit that event.
4. Scan and parse do not take a component type. `semantic.module`, `compile.module`, and `compile.ast` require `-c` / `--component`.
5. **Trunk** — implement against the published TRD. Do not copy from proto.
6. **Prototype** — only if binding.md says the prototype strand is active. Implement against the published RFP on the proto branch named there. Do not cut that branch from this skill.

## Outputs

- The phase, command, and event change on the strand branch, in a PR to that strand. Not an issue body.

## Guardrails

- Never commit or merge unless asked.
- Never proto → trunk git.
- Never implement trunk reconstruction from a live proto branch.
- Never author a reconstruction TRD without a freeze id.
- Read `docs/collab/binding.md` in this repo for owner/repo, proto branch, and project ids.
- Do not vendor Tiferet skills into this repo.
- Do not copy the YAML step list into this skill or into a comment.
- This package has no contexts, blueprints, di, or repos. Do not add them to wire a step.
