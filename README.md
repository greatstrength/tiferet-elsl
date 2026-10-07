# tiferet-elsl

`tiferet-elsl` is the Tiferet-based compiler for ElohaSL. This repository is the compiler, not the language.

It checks Tiferet-structured Python and hands the result on as data. It does not run applications. It does not store a project's design.

The import package is `compiler`. The distribution is `tiferet-elsl` `1.0.1`. The console script is `tiferet-compiler` (`compiler.cli:main`).

## Install

Install `1.0.1` from PyPI. Requires Python >= 3.10.

```bash
pip install tiferet-elsl
```

Each release also attaches its wheel and sdist on GitHub:

https://github.com/greatstrength/tiferet-elsl/releases/tag/v1.0.1

```bash
pip install https://github.com/greatstrength/tiferet-elsl/releases/download/v1.0.1/tiferet_elsl-1.0.1-py3-none-any.whl
```

The same release also publishes `tiferet_elsl-1.0.1.tar.gz`.

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

## License

`tiferet-elsl` is released under the [BSD 3-Clause License](LICENSE). Copyright (c) 2025-2026, Great Strength Systems LLC.

Redistributions of the source or of a built distribution must retain the copyright notice, the license conditions, and the disclaimer. The name of the copyright holder and the names of its contributors may not be used to endorse or promote products derived from this software without specific prior written permission.

This license covers `tiferet-elsl` only. It does not extend to any other Great Strength Systems product.

## Read next

- [CLI guide](docs/guides/cli.md) — how to run `tiferet-compiler`
- [AGENTS.md](AGENTS.md) — orientation for working in this repository
- [Domain vision](docs/domain-vision.md)
- [Core domain distillation](docs/core-domain-distillation.md)
