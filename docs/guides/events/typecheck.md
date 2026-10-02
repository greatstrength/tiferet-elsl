# Typecheck Events

**Project:** tiferet-elsl  
**Repository:** https://github.com/greatstrength/tiferet-elsl  
**Module:** `compiler/events/typecheck.py`  
**Version:** 1.0.0

## Overview

This module is the conformance event family. One base event binds a rule set. Each subclass binds one constant and appends that constant's findings. The module does not decide which dialect runs.

**Vision:** See the `ConformanceEvent` class docstring in `compiler/events/typecheck.py`.

## Ubiquitous Language

- **Conformance event** — a `ConformanceEvent` subclass. It does not walk the AST.
- **Gate** — a `condition` on the matching step in `compiler/assets/feature.yml`. Not a branch in `execute`.
- **Finding** — a dict. Prior findings stay in front. The caller's list is not mutated.

## What this module owns

`CheckCommonConformance` is ungated. The other ten subclasses are gated by component. `execute` requires `ast` and `semantic`. It does not read `component`.

The contexts class is `CheckContextsConformance`. Its `service_id` is `check_context_conformance_event`. That mismatch is the shipped name.

## Boundaries

**Inside this domain:** which event binds which rule-set constant, and the refusal to read `component`.

**Outside this domain:** the specification lists ([utils/typecheck.md](../utils/typecheck.md)); the YAML gate ([assets.md](../assets.md)); the frozen choice strings ([tests/schema-freeze.md](../tests/schema-freeze.md)).

## Related Documentation

- `compiler/events/typecheck.py` — this module
- [utils/typecheck.md](../utils/typecheck.md) — the constants these events bind
- [assets.md](../assets.md) — the registrations and the gates
