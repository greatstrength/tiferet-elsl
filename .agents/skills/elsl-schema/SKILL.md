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
- A change that could move a name in the catalog below.
- Any other name `compiler/tests/test_schema_freeze.py` asserts.

## When not to use
- An internal rename that test does not lock. Rule-set contents, specification ids, feature step order, and service class names are not this skill.
- Pipeline step wiring that leaves the frozen names in place — `elsl-pipeline`.
- Dialect rule text — `elsl-rule-sets`.
- Code style, TRDs, RFPs, or reports — the Tiferet skills. Do not vendor them. Authoring the freeze TRD is `tiferet-author-trd`, not this skill.

## Canonical source
- `compiler/tests/test_schema_freeze.py`
- `compiler/CHANGELOG.md`
- The catalog below is the operator copy of that test. If the test and this skill disagree, the test on the branch wins, and this skill is updated in the same change.

## Inputs
- The surface the change would move, confirmed against the catalog.
- `docs/collab/binding.md`.
- A freeze decision. **Trunk** needs a freeze id and a published TRD before the edit.

## Catalog

`compiler.__version__` is `1.0.0`. The root distribution name is `tiferet-elsl`. There is no `compiler/pyproject.toml`. The root file does not contain `name = "tiferet-compiler"` or `tiferet-command-parser-edu`. The console script remains `tiferet-compiler` (`compiler.cli:main`). The changelog names that script. The test does not read `[project.scripts]`. Renaming the script is still a freeze decision.

Commands, in document order, and no others:

1. `scan.module`
2. `parse.module`
3. `semantic.module`
4. `compile.module`
5. `compile.ast`

`scan.event` and `compile.event` are absent. Each command's `group_key` and `key` match the nesting. The test does not lock feature step order. It also does not assert that scan and parse lack `-c`.

`-c` / `--component` is required, exactly once, on `semantic.module`, `compile.module`, and `compile.ast`. Choices, in this order: `assets`, `blueprints`, `contexts`, `di`, `domain`, `events`, `interfaces`, `mappers`, `repos`, `utils`. Reordering is a freeze decision.

Sessions are the set `compiler`, `compiler_cli`. Order is not locked. `compiler_cli` const keys are the set `cli_config`, `di_config`, `feature_config`, `error_config`, `logging_config`. Top-level `const` keys are the set `token_config`, `grammar_config`, `production_config`.

Seven packaged YAML basenames must exist: `config.yml`, `feature.yml`, `errors.yml`, `cli.yml`, `tokens.yml`, `grammars.yml`, `productions.yml`. Existence is the lock. Order is not.

Codegen: an events result is exactly `cmpt` and `evt_grp`. `evt_grp` is not inside `cmpt`. A domain result has no `evt_grp`. `cmpt` keys stay within `name`, `kind`, `desc`, `impt`, `grps`. `evt_grp` keys stay within `name`, `desc`, `impt`, `fncs`, `evts`. Absent long names: `imports`, `functions`, `events`, `component`, `event_group`. A documented module emits `desc`. A bare module omits it. A snippet with both a comment and a statement uses `coms` and `stmt`. An event dict stays within `name`, `desc`, `attributes`, `injections`, `execute`, `methods`.

`.next` is on `ParamListTransferObject` and `StatementTransferObject` only. `TypeTransferObject.params` is `ParamListTransferObject | None`. `DeclarationTransferObject.code` is `StatementTransferObject | None`. Runtime `ParamList` and `Statement` do not declare `next`. `Type.params` is `List[ParamList]`.

Findings: every `service_id` that starts with `check_` and ends with `_conformance_event` uses `data_key: findings`. `CheckDomainConformance.execute` returns dicts that include `error_code` and `message`. Prior findings stay in front. The test does not lock other finding keys, and it does not call every dialect event.

## Relation to ElohaSL

A frozen name is a construct's emitted key, not a local variable. This source:

```python
# ** event: get_feature
class GetFeature:
    # * method: execute
    def execute(self):
        # Load the feature.
        return feature
```

compiled with `-c events` must keep `cmpt` and `evt_grp` as siblings, `evt_grp.evts.get_feature`, and `snpt` entries that use `coms` and `stmt`. `.next` is the persistence chain for parameters and statements. It is not a key inside `cmpt`. The findings list is the conformance result. It is not ElohaSL.

A rename of `impt`, `grps`, `fncs`, `evts`, `coms`, or `stmt` is a freeze decision when the schema test locks that name. Read `elsl-language` for what the key means before proposing the rename.

## Procedure
1. If the catalog does not lock the name, stop. This skill does not apply.
2. Treat the change as a freeze decision. Do not rename in place and leave the test describing the old name.
3. **Trunk** — do not edit the surface without a freeze id and a published TRD. Do not implement from a live proto branch.
4. **Prototype** — only if binding.md says the prototype strand is active. Do not promote the change onto trunk.
5. Update `compiler/tests/test_schema_freeze.py` and `compiler/CHANGELOG.md` in the same change as the surface. Then update this catalog.

## Outputs
- The freeze decision first, on the GitHub issue via the Tiferet TRD skill. Do not author that TRD here.
- Then the surface change, the schema test, and this skill's catalog, on the strand branch, in a PR.

## Guardrails
- Never commit or merge unless asked.
- Never proto → trunk git.
- Never implement trunk reconstruction from a live proto branch.
- Never author a reconstruction TRD without a freeze id.
- Read `docs/collab/binding.md` in this repo for owner/repo, proto branch, and project ids.
- Do not vendor Tiferet skills into this repo.
- A schema change is a freeze decision, not a drive-by edit.
- Do not invent a frozen surface.
- Do not treat a guide as the source for this catalog.
