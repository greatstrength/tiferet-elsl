# AGENTS.md — tiferet-elsl (v1.0.0)

Orientation index for this repository. It is not a copy of the Tiferet framework guide, and it does not restate the compiler. Where a document and the code disagree, the code wins.

## Project overview

**tiferet-elsl** is the Tiferet-based compiler for ElohaSL. It is not the language. It does not run applications, and it does not store a project's design.

- **Repository:** https://github.com/greatstrength/tiferet-elsl
- **Trunk:** `main`
- **Python:** >= 3.10
- **Distribution:** `tiferet-elsl` `1.0.0` (`Private :: Do Not Upload`; not on PyPI)
- **Import package:** `compiler` (`compiler.__version__` is `1.0.0`)
- **Console script:** `tiferet-compiler` (`compiler.cli:main`)
- **Release:** https://github.com/greatstrength/tiferet-elsl/releases/tag/v1.0.0
- **Sessions:** `compiler` and `compiler_cli`. The console script boots `compiler_cli`.
- **Phone book:** [docs/collab/binding.md](docs/collab/binding.md)

`v1.x-proto` is still not cut. The trunk reconstruction through `v1.0.0` is closed. Do not invent a prototype branch, and do not import `tiferet_elsl`.

## Package map

```
compiler/
├── assets/        # Packaged YAML and the lexer token module
├── domain/        # Compiler nouns
├── events/        # Pipeline and conformance events
├── interfaces/    # Service contracts this compiler defines
├── mappers/       # Aggregates and transfer objects
├── utils/         # Adapters, specifications, and dialect rule sets
├── tests/         # Schema freeze
└── cli.py         # Console entry
```

`compiler.py` at the repository root calls `compiler.cli.main`. It is not a second package.

This package has no `contexts`, `blueprints`, `di`, or `repos` of its own. Those names are component choices the compiler checks in other code. Paths under `compiler/utils/tests/fixtures/` are test inputs, not packages. Do not add a Tiferet layer package here to match the framework tree.

The generic parse engine is `tiferet-ly`. This package does not absorb it. The boundary is in `elsl-pipeline` and in [docs/guides/assets.md](docs/guides/assets.md).

## Pipelines

Five pipelines, declared in `compiler/assets/feature.yml` and exposed by `compiler/assets/cli.yml`:

- `scan.module`
- `parse.module`
- `semantic.module`
- `compile.module`
- `compile.ast`

Scan and parse do not take a component type. `semantic.module`, `compile.module`, and `compile.ast` require `-c` / `--component`. The ten choices are `assets`, `blueprints`, `contexts`, `di`, `domain`, `events`, `interfaces`, `mappers`, `repos`, and `utils`.

Before changing a phase, a feature step, a CLI command, or an event that is a pipeline step, use `elsl-pipeline`. The skill carries the step catalog.

## Where law lives

Code style, TRDs, RFPs, and Collaboration Reports stay on the Tiferet skills. Do not vendor `tiferet-code-*` or any collaboration skill into this repository. Do not fork `docs/collab/` or `docs/core/`.

Use the installed Tiferet skills. If a skill is not installed, read the framework copy under https://github.com/greatstrength/tiferet/blob/main/. Start at [AGENTS.md](https://github.com/greatstrength/tiferet/blob/main/AGENTS.md) and [CONTRIBUTING.md](https://github.com/greatstrength/tiferet/blob/main/CONTRIBUTING.md).

- Read `tiferet-code-style` at the start of every implementation session.
- Read `tiferet-code-architecture` before a change that spans more than one package.
- Then read the component skill for the `compiler/` package you are editing: `assets`, `domain`, `events`, `interfaces`, `mappers`, `utils`, or tests.
- Repo-local facts — owner, strands, project ids, milestone shapes — are only in [docs/collab/binding.md](docs/collab/binding.md).

Four local skills, `elsl-` prefix, live under `.agents/skills/`. Each carries its own catalog. A guide is for a human reader of a module. It is not the source an agent follows.

- `elsl-pipeline` — a phase, a feature step, a CLI command, or a pipeline-step event.
- `elsl-conformance` — a conformance event, or the `feature.yml` condition that gates it.
- `elsl-rule-sets` — a specification on a `*_RULE_SET` constant.
- `elsl-schema` — any change that could move a frozen surface.

Dialect files, not a transcription of the rulebooks:

- Rule-set constants live in `compiler/utils/typecheck.py`.
- Specifications live in `compiler/utils/core.py`.
- Gated conformance events live in `compiler/events/typecheck.py`.
- The gate is `compiler/assets/feature.yml`, not `execute`. `execute` does not read `component`.

## Frozen surfaces

Frozen surfaces are whatever `compiler/tests/test_schema_freeze.py` locks, plus the names in `compiler/CHANGELOG.md`. Do not invent a surface, and do not rename one in a drive-by edit. A schema change is a freeze decision. Use `elsl-schema`. The human page for that test is [docs/guides/tests/schema-freeze.md](docs/guides/tests/schema-freeze.md).

## Guides

Guides correspond to a package, a module, or a test. They are not the agent catalog.

- [docs/guides/assets.md](docs/guides/assets.md) — `compiler/assets/`
- [docs/guides/events/typecheck.md](docs/guides/events/typecheck.md) — `compiler/events/typecheck.py`
- [docs/guides/utils/typecheck.md](docs/guides/utils/typecheck.md) — `compiler/utils/typecheck.py`
- [docs/guides/tests/schema-freeze.md](docs/guides/tests/schema-freeze.md) — `compiler/tests/test_schema_freeze.py`

## Testing

```bash
source .venv/bin/activate && python -m pytest compiler -q
```

Tests live under `compiler/`, including `compiler/tests/test_schema_freeze.py`. There is no repository-root `tests/` tree.

Before an implementation session, scan open annotations in this package. The scan root is `compiler/`, not `tiferet/`:

```bash
grep -rn "# ++\|# --" compiler/
```

## Stale documents

[docs/domain-vision.md](docs/domain-vision.md) and [docs/core-domain-distillation.md](docs/core-domain-distillation.md) are Draft. They still cite `tiferet_elsl/` and `proto:`. The import package is `compiler`. Do not treat those citations as the implementation map. A rewrite of either draft is its own docs change, not a side effect of compiler work.

## Contributing

Follow the Tiferet collaboration process. This file does not replace it. Read [docs/collab/binding.md](docs/collab/binding.md), then the matching Tiferet skill. A docs or skills change needs no TRD. Do not commit or merge unless asked.
