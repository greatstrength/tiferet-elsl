# Schema – Strategies and Patterns

**Project:** tiferet-elsl  
**Repository:** https://github.com/greatstrength/tiferet-elsl  
**Module:** `compiler/tests/test_schema_freeze.py`  
**Version:** 1.0.0

## Overview

`compiler/tests/test_schema_freeze.py` is the lock. `compiler/CHANGELOG.md` names the public schemas for `1.0.0`: the five CLI commands, codegen `cmpt` (and `evt_grp` for events), AST transfer `.next` chains, and the findings list. A later move of a locked name is a freeze decision. It is not a silent rename.

The test also locks surfaces the changelog does not list by name. Those are frozen too. A name the test does not assert, and the changelog does not name, is not a frozen surface.

## Ubiquitous Language

- **Frozen surface** — a name or shape `compiler/tests/test_schema_freeze.py` asserts, or a public schema `compiler/CHANGELOG.md` names.
- **Freeze decision** — a deliberate change to a frozen surface, recorded in the test and the changelog together. Updating the test to match a drive-by rename is not a freeze decision.
- **Envelope** — the codegen dict. `cmpt` is always the component envelope. `evt_grp` is the legacy event-group envelope, and only for events.
- **Transfer chain** — the persistence shape that links parameters and statements through `.next`. Runtime lists are not that shape.
- **Finding** — a dict accumulated under the `findings` data key. The freeze locks that key and the presence of `error_code` and `message`. It does not lock every other key.

## A Later Change Is a Freeze Decision

Do not rename a locked name in place and leave the test, or the changelog, describing the old name.

A freeze decision changes the surface, `compiler/tests/test_schema_freeze.py`, and `compiler/CHANGELOG.md` together. Do not edit the test only to make a drive-by rename pass. Do not leave the changelog naming a surface the test no longer locks.

The collaboration process for a freeze stays on the Tiferet skills. This guide does not restate it, and this repo does not fork it.

Retired names stay off the surface. The test locks all of these absences:

- no `compiler/pyproject.toml`
- the root `pyproject.toml` does not contain `name = "tiferet-compiler"`
- the root `pyproject.toml` does not contain `tiferet-command-parser-edu`
- `scan.event` and `compile.event` are not commands

The distribution name and the console script are different surfaces. The distribution is `tiferet-elsl`. The changelog says the console script remains `tiferet-compiler` (`compiler.cli:main`). Do not revive `tiferet-compiler` as the project name to "match" the script.

## The Package Version

The test locks `compiler.__version__ == '1.0.0'`. That attribute, in `compiler/__init__.py`, is the version surface. It is not a second project file. The changelog names the same version on the root distribution.

## The Command Surface

The test loads `compiler/assets/cli.yml` and locks the command list, in document order, to exactly:

1. `scan.module`
2. `parse.module`
3. `semantic.module`
4. `compile.module`
5. `compile.ast`

Each command's `group_key` and `key` must match the nesting that produced that id. Feature ids are `group_key.key`. Adding a sixth command, reordering these five, or restoring an `event` command fails the lock.

The test does not lock feature step order. Step order is a pipeline decision. See [pipeline.md](pipeline.md).

## The Component Choices

The test locks `-c` / `--component` on `semantic.module`, `compile.module`, and `compile.ast`. Each of those commands has exactly one such argument. It is required. Its `choices` equal this list, in this order:

`assets`, `blueprints`, `contexts`, `di`, `domain`, `events`, `interfaces`, `mappers`, `repos`, `utils`.

Reordering the choices is a freeze decision, not a style edit. A new choice is a freeze decision, not a dialect-only edit. See [dialects.md](dialects.md).

The test does not assert that scan and parse lack the flag. `compiler/assets/cli.yml` is what says those two commands do not take a component type. Do not promote that fact into a frozen assertion it is not.

## Sessions and Asset Files

The test locks the session ids in `compiler/assets/config.yml` to the set `compiler` and `compiler_cli`. Order is not locked. Adding a third session is.

It locks the `compiler_cli` const keys to the set `cli_config`, `di_config`, `feature_config`, `error_config`, and `logging_config`.

It locks the top-level `const` keys to the set `token_config`, `grammar_config`, and `production_config`.

It locks seven YAML basenames as package data under `compiler` assets, not as loose repo files only:

- `config.yml`
- `feature.yml`
- `errors.yml`
- `cli.yml`
- `tokens.yml`
- `grammars.yml`
- `productions.yml`

Existence is the lock. The order of that list is not.

## The Codegen Envelope

The changelog names `cmpt`, and `evt_grp` for events. The test locks the shape.

An events result is exactly the keys `cmpt` and `evt_grp`. `evt_grp` is not a key inside `cmpt`. A domain result has no `evt_grp`. The generator's contract matches that split: `kind='events'` dual-emits the legacy event group, and other kinds omit that key. `cmpt` never carries `evt_grp`.

Short names are the emitted keys. These long replacements stay absent: `imports`, `functions`, `events`, `component`, `event_group`.

`cmpt` keys stay within `name`, `kind`, `desc`, `impt`, and `grps`. `evt_grp` keys stay within `name`, `desc`, `impt`, `fncs`, and `evts`. A documented module emits `desc`. A bare module omits it. Do not invent `desc` for a module that has no docstring, and do not rename `impt` or `grps` to the long forms.

A serialized snippet uses `coms` and `stmt`. The test locks that pair on a snippet that has both a comment and a statement. An event dict stays within `name`, `desc`, `attributes`, `injections`, `execute`, and `methods`. The test does not require every event dict to carry every one of those keys.

## AST Transfer `.next` Chains

`.next` exists only on the persistence transfer chains. The test locks `next` on `ParamListTransferObject` and `StatementTransferObject`. `TypeTransferObject.params` is `ParamListTransferObject | None`. `DeclarationTransferObject.code` is `StatementTransferObject | None`.

Runtime lists keep their list shape and have no `.next` link. `ParamList` and `Statement` do not declare `next`. `Type.params` is `List[ParamList]`.

Do not add `.next` to the runtime models to "match" the transfer objects. Do not replace a transfer chain with a list and call it a cleanup. That is a freeze decision.

## The Findings List

The changelog names the findings list. The test locks two facts about it.

Every feature step whose `service_id` starts with `check_` and ends with `_conformance_event` uses `data_key: findings`. At least one such step exists. That collection is how the test finds the conformance steps. It is not a license to rename a conformance `service_id` off that pattern and assume the lock still sees it.

`CheckDomainConformance.execute` accumulates finding dicts. The first call seeds the list. A second call keeps that list in front, and the result is at least as long. Each item is a dict that includes `error_code` and `message`. The test does not lock other finding keys. Do not drop `error_code` or `message`, and do not replace the list with a single finding object.

The shared implementation is `ConformanceEvent.run_rule_set`, which keeps prior findings in front and does not mutate the caller's list. The test calls `CheckDomainConformance`, not every dialect event.

## What This Test Does Not Lock

Do not infer a freeze from a name that merely appears in the compiler.

The test does not lock rule-set contents, specification ids, feature step order, or service class names. Those decisions live in [dialects.md](dialects.md) and [pipeline.md](pipeline.md). Changing them is still a coordinated edit. It is not, by itself, a schema freeze.

It does not assert the console script string. The changelog still names that script, so renaming `tiferet-compiler` is a freeze decision even though the test does not read `pyproject.toml` scripts. It does not lock payload keys beyond the envelope, snippet, event-dict ceiling, and finding keys above.

## Boundaries

**Inside this domain:** the names and shapes the schema test locks, the public schemas the changelog names, and the decision that moving one of them is a freeze rather than a rename.

**Outside this domain:** phase mechanics ([pipeline.md](pipeline.md)); dialect rulebooks and gates ([dialects.md](dialects.md)); how a freeze is opened in the collaboration process, which stays on the Tiferet skills. This package has no `contexts`, `blueprints`, `di`, or `repos` of its own. The choice strings are frozen names for target dialects, not local packages.

The draft vision and distillation are not the source for this guide. Code wins.

## Related Documentation

- [pipeline.md](pipeline.md) — the five commands and which event owns which step
- [dialects.md](dialects.md) — the ten rulebooks behind the frozen component choices
- `compiler/tests/test_schema_freeze.py` — the lock
- `compiler/CHANGELOG.md` — the named public schemas for `1.0.0`
- [docs/core/code_style.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/code_style.md) — artifact comments and formatting; style law stays on the Tiferet skills
- [`.agents/skills/elsl-schema`](../../.agents/skills/elsl-schema/SKILL.md) — procedure for a change that could move a frozen surface
