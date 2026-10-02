# tiferet-elsl

`tiferet-elsl` is the Tiferet-based compiler for ElohaSL. This repository is the compiler, not the language.

It checks Tiferet-structured Python and hands the result on as data. It does not run applications. It does not store a project's design.

The import package is `compiler`. The distribution is `tiferet-elsl` `1.0.0`. The console script is `tiferet-compiler` (`compiler.cli:main`).

## Install

This package is not published to PyPI (`Private :: Do Not Upload`). Install `1.0.0` from the GitHub release:

https://github.com/greatstrength/tiferet-elsl/releases/tag/v1.0.0

```bash
pip install https://github.com/greatstrength/tiferet-elsl/releases/download/v1.0.0/tiferet_elsl-1.0.0-py3-none-any.whl
```

The same release also publishes `tiferet_elsl-1.0.0.tar.gz`. Requires Python >= 3.10.

## Commands

`tiferet-compiler` exposes five commands:

- `scan.module`
- `parse.module`
- `semantic.module`
- `compile.module`
- `compile.ast`

## Tests

```bash
source .venv/bin/activate && python -m pytest compiler -q
```

## Read next

- [AGENTS.md](AGENTS.md) — orientation for working in this repository
- [Domain vision](docs/domain-vision.md)
- [Core domain distillation](docs/core-domain-distillation.md)
