# Compiler changelog

## 1.0.0

First trunk release of `tiferet-compiler`.

The root `pyproject.toml` distribution is `tiferet-compiler` version `1.0.0`. The console script is `tiferet-compiler` (`compiler.cli:main`).

Public schemas are frozen: CLI `scan.module`, `parse.module`, `semantic.module`, `compile.module`, and `compile.ast`; codegen `cmpt` (and `evt_grp` for events); AST transfer `.next` chains; and the findings list.
