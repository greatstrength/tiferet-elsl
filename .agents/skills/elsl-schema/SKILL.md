---
name: elsl-schema
description: >
  Use when a change could move a frozen surface: the five commands, the ten
  component choices, session ids, the seven YAML basenames, codegen cmpt /
  evt_grp, AST transfer .next chains, or the findings list. Phrases:
  "schema freeze", "rename a command", "change a session id", "frozen
  surface", "YAML basename", "findings list". Not for an internal rename
  the schema test does not lock.
---

# Change a frozen compiler surface

## When to use

- A change that could move a frozen surface: the five commands, the ten component choices, session ids (`compiler`, `compiler_cli`), the seven YAML basenames, codegen `cmpt` / `evt_grp`, AST transfer `.next` chains, or the findings list.
- Any other name `compiler/tests/test_schema_freeze.py` locks.

## When not to use

- An internal rename that test does not lock.
- Pipeline step wiring that leaves the frozen names in place — `elsl-pipeline`.
- Dialect rule text — `elsl-dialects`.
- Code style, TRDs, RFPs, or reports — the Tiferet skills. Do not vendor them. Authoring the freeze TRD is `tiferet-author-trd`, not this skill.

## Canonical source

- `docs/guides/schema.md`
- `compiler/tests/test_schema_freeze.py`
- Do not invent surfaces. The test is the lock. Do not duplicate its assertions here.

## Inputs

- The surface the change would move, confirmed against the test.
- `docs/collab/binding.md`.
- A freeze decision. **Trunk** needs a freeze id and a published TRD before the edit. Do not start from a drive-by.

## Procedure

1. Read `docs/guides/schema.md` and `compiler/tests/test_schema_freeze.py`. If the test does not lock the name, stop. This skill does not apply.
2. Treat the change as a freeze decision, not a drive-by edit. Names in `compiler/CHANGELOG.md` are the same surfaces, not a second list.
3. **Trunk** — do not edit the surface without a freeze id and a published TRD. Do not implement from a live proto branch.
4. **Prototype** — only if binding.md says the prototype strand is active. Do not promote the change onto trunk. Do not cut the proto branch from this skill.
5. Update the test in the same change as the surface. Do not silently rename.

## Outputs

- The freeze decision first, on the GitHub issue via the Tiferet TRD skill. Do not author that TRD here.
- Then the surface change and the schema test, on the strand branch, in a PR. Not a silent rename. Not an issue comment from this skill.

## Guardrails

- Never commit or merge unless asked.
- Never proto → trunk git.
- Never implement trunk reconstruction from a live proto branch.
- Never author a reconstruction TRD without a freeze id.
- Read `docs/collab/binding.md` in this repo for owner/repo, proto branch, and project ids.
- Do not vendor Tiferet skills into this repo.
- A schema change is a freeze decision, not a drive-by edit.
- Do not invent a frozen surface. Do not add a name the schema test does not lock.
