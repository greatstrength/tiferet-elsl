---
name: elsl-language
description: >
  Use when reading, explaining, or changing ElohaSL output. Phrases: "ElohaSL",
  "ElSL", "cmpt", "evt_grp", "what does compile emit", "codegen envelope",
  "named operation", "snippet". Not for wiring a pipeline step or editing a
  conformance rule unless the question is what the distilled document means.
---

# Read ElohaSL from codegen

## When to use
- Explaining what `compile.module` or `compile.ast` emits.
- Reading a `cmpt` or `evt_grp` document.
- Changing a generator key, a snippet, or an encoded statement.

## When not to use
- Wiring a phase or a CLI flag — `elsl-pipeline`.
- Adding a specification or a gate — `elsl-rule-sets` and `elsl-conformance`. Those check source. They do not appear in the envelope.
- Renaming a frozen key — `elsl-schema`.

## Canonical source
- `compiler/utils/codegen.py` — `TiferetGenerator.generate`
- `compiler/mappers/codegen.py` — import, snippet, and event serialization
- `compiler/domain/ast.py` — `Expression.encode` and `Statement.encode`

## Inputs
- A compiled document, or the construct being explained.
- `docs/collab/binding.md` when the work will edit the generator.

## The document

ElohaSL, in this compiler's output, is the component envelope. It is not the source file and not the findings list.

`generate` always returns `cmpt`. `kind='events'` also returns `evt_grp`. Other kinds omit `evt_grp`. `cmpt` never contains `evt_grp`.

`cmpt` keys, only when built:

- `name` — module name, or `unknown`
- `kind` — the requested component type. A direct `generate` call defaults to `events`. The CLI passes `-c`.
- `desc` — stripped module docstring. Omitted when empty.
- `impt` — import categories. Each row is `{src, tgts}`. Same-module imports collapse. First-seen module order is kept.
- `grps` — ordered group entries. `exports` is skipped. An unknown group name dispatches as events.

`evt_grp` repeats `name`, `desc`, and `impt`, then adds `fncs` and `evts` when those maps were built. Functions and events are dual-emitted only on that legacy key. They are not copied onto `cmpt` except as group entries inside `grps`.

Short names are the language. These long replacements are absent: `imports`, `functions`, `events`, `component`, `event_group`.

## Groups

Known group hooks: `imports`, `functions`, `constants`, `classes`, `models`, `mappers`, `interfaces`, `utils`, `contexts`, `blueprints`, `repos`. Anything else, including `events`, uses the event rewrite.

| Source group | Envelope |
|---|---|
| `imports` | `cmpt.impt` only. No group entry |
| `functions` | group `functions` with `fncs`, and `evt_grp.fncs` when kind is events |
| `blueprints` | group `blueprints` with the same callable shape as functions |
| `constants` | group `constants` with `csts`. Not dual-emitted at the root |
| `classes` | group of class payloads. A base is recorded. An absent base is omitted |
| `models` | class shape only. No `base`, `maps`, `kind`, or `implements` |
| `mappers` | `maps` from the first base, `kind` from the second base name |
| `interfaces` | same base rule as classes |
| `contexts` | `base`, plus `collaborators` when an init parameter type is a sibling import |
| `repos` | `implements` from the first base. `idempotent` only when delete raises nothing |
| `events` | group of event payloads, and `evt_grp.evts` when kind is events |

A group entry is `{name}` plus `qual` when the header has a parenthetical qualifier. Empty containers are omitted.

## Members

A class or event payload includes `name`, then only the filled sections: `desc`, `attributes`, `injections`, `execute`, `methods`.

- Attribute without an initializer: `{name: type_name}`.
- Attribute with an initializer: `{name: {type, init}}`. `init` is `Expression.encode()`.
- Injection spec: `name:type:required::desc`. The default slot is empty. The value is `{assign: [{target, value}]}`, and the value is the parameter name.
- `execute` has no description key. Optional sections are `deco`, `params`, `returns`, `snpt`.
- A method whose inner name is `execute` is the execute payload. Other methods go in `methods`, keyed by name.
- Parameter spec: `name:type:required:default:desc`. `self` is skipped.
- Return spec: `type:desc`, or `type:` when the docstring has no return description.

## Snippets and named operations

A snippet is one logical step. Serialization renames the domain fields: comments become `coms`, encoded statements become `stmt`. An empty snippet is omitted.

Statements inside `stmt` are `Statement.encode()`, not source text. Expressions inside those strings are `Expression.encode()`.

```text
Return(Add(a, b))
Attr(self, name)
Call(verify, expression=feature is not None)
If(cond, body)
```

`encode` returns `''` when a kind has no encoding. Comments, artifact headers, and imports do not encode as statements. F-strings do not encode.

## Conformance is not the document

Conformance findings are a separate list. A finding does not become a key on `cmpt`. The gate that chose the dialect is also absent. What conformance checks is the source shape this language later records: import groups, section names, members, and the encoded operations inside snippets.

If a finding and an envelope disagree, the envelope is what distillation emitted. The finding is what the rulebook rejected. Do not merge them.

## Procedure
1. Read `cmpt` first. Read `evt_grp` only when `kind` is `events`.
2. Treat a missing key as omitted, not as an empty list.
3. Decode `stmt` with the encode names above. Do not pretty-print it back to Python and call that the language.
4. **Trunk** — a key rename is `elsl-schema` before it is a generator edit.
5. **Prototype** — only if binding.md says that strand is active.

## Outputs
- An explanation of the document, or a generator change on the strand branch, in a PR. Not an issue body.

## Guardrails
- Never commit or merge unless asked.
- Never proto → trunk git.
- Never implement trunk reconstruction from a live proto branch.
- Never author a reconstruction TRD without a freeze id.
- Read `docs/collab/binding.md` in this repo for owner/repo, proto branch, and project ids.
- Do not vendor Tiferet skills into this repo.
- Do not invent a long key for a short one.
- Do not treat a guide as the source for this catalog.
