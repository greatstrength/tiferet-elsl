# tiferet-elsl

## 1.0.1

Metadata and release hotfix. The distribution is relicensed in metadata to `BSD-3-Clause`, matching the existing `LICENSE`.

The `Private :: Do Not Upload` classifier and the proprietary license text are removed. The project gains `authors`, `readme`, and `project.urls` metadata. The release workflow publishes stable releases to PyPI through trusted publishing.

No change to the public schemas frozen in `1.0.0`.

## 1.0.0

First trunk release of `tiferet-elsl`.

The root `pyproject.toml` distribution is `tiferet-elsl` version `1.0.0`. The console script remains `tiferet-compiler` (`compiler.cli:main`).

Public schemas are frozen: CLI `scan.module`, `parse.module`, `semantic.module`, `compile.module`, and `compile.ast`; codegen `cmpt` (and `evt_grp` for events); AST transfer `.next` chains; and the findings list.
