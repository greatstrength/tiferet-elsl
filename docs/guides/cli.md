# CLI – Compiler Console

**Project:** tiferet-elsl  
**Repository:** https://github.com/greatstrength/tiferet-elsl  
**Module:** `compiler/cli.py`  
**Version:** 1.0.0

## Overview

`tiferet-compiler` is the console script. It resolves packaged assets and boots the `compiler_cli` session. The commands themselves are declared in `compiler/assets/cli.yml`. **Vision:** see the `main` docstring in `compiler/cli.py` for the value statement this guide distills.

## Ubiquitous Language

- **Console script** — `tiferet-compiler`, entry `compiler.cli:main`.
- **Group** — the first positional token: `scan`, `parse`, `semantic`, or `compile`.
- **Command** — the second positional token. `module` for every group, plus `ast` under `compile`.
- **Component** — `-c` / `--component`. Required on semantic and both compile commands. Not accepted by scan or parse.

## Install and invoke

The package is not on PyPI. Install the `1.0.0` wheel from the GitHub release, then call the script. The working directory does not matter. Asset paths are resolved from the installed package.

```bash
pip install https://github.com/greatstrength/tiferet-elsl/releases/download/v1.0.0/tiferet_elsl-1.0.0-py3-none-any.whl
tiferet-compiler -h
tiferet-compiler scan -h
tiferet-compiler scan module -h
```

`python -m compiler` is the same entry. `compiler.py` at the repository root only calls `compiler.cli.main`.

Argparse failures exit `2`. A structured API error exits `1`.

## Commands

The shape is `tiferet-compiler <group> <command> ...`. Feature id is `group.command`.

| Invocation | Component | What it does |
|---|---|---|
| `scan module SOURCE` | no | Tokenize a source file |
| `parse module SOURCE` | no | Parse a source file |
| `semantic module SOURCE -c KIND` | required | Analyze a source file |
| `compile module SOURCE -c KIND` | required | Compile a source file |
| `compile ast SOURCE -c KIND` | required | Compile a saved JSON AST |

`KIND` is one of `assets`, `blueprints`, `contexts`, `di`, `domain`, `events`, `interfaces`, `mappers`, `repos`, `utils`.

```bash
tiferet-compiler scan module app/events/ping.py
tiferet-compiler parse module app/events/ping.py -o ping.yml
tiferet-compiler semantic module app/events/ping.py -c events
tiferet-compiler compile module app/events/ping.py -c events -O O1 -o ping.yml
tiferet-compiler compile ast ping.json -c events -o ping.yml
```

`compile ast` takes a JSON AST path, not a Python source path.

## Arguments

| Flag | Commands | Notes |
|---|---|---|
| `source_file` | all | Positional. Source path, except `compile ast`, where it is the JSON AST path |
| `-o` / `--output` | all | Path of the YAML or JSON result. Omitted, the result is printed |
| `--output-format` | all | `yaml`, `json`, or `auto`. Parse and both compile commands default to `auto` |
| `--summary-only` | `scan module` | Declared. `EmitScanResult` does not read it |
| `--include-tokens` | parse, semantic | Boolean. No value |
| `--include-ast` | `semantic module` | Boolean. No value |
| `-c` / `--component` | semantic, compile | Required. The ten choices above |
| `-O` | both compile commands | `O0` or `O1`. Default `O0`. `O0` leaves codegen unchanged. `O1` shares repeated structures |

Boolean flags are presence flags. `--include-tokens true` is not the form.

## Boundaries

**Inside this domain:** how a person invokes `tiferet-compiler`, and which arguments each command accepts.
**Outside this domain:** which event owns a step ([assets.md](assets.md)); dialect gates ([events/typecheck.md](events/typecheck.md)); the names the schema test locks ([tests/schema-freeze.md](tests/schema-freeze.md)).

## Related Documentation

- `compiler/cli.py` — the console entry
- `compiler/assets/cli.yml` — the command catalog
- [assets.md](assets.md) — the sessions and feature pipelines this script boots
- [docs/core/code_style.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/code_style.md) — artifact comments and formatting
