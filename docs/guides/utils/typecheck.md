# Typecheck Utilities

**Project:** tiferet-elsl  
**Repository:** https://github.com/greatstrength/tiferet-elsl  
**Module:** `compiler/utils/typecheck.py`  
**Version:** 1.0.0

## Overview

This module is the rulebook catalog and the one reader. `ConformanceChecker` walks a module once for whatever list it was given. A dialect is a constant, not a subclass.

**Vision:** See the `ConformanceChecker` class docstring in `compiler/utils/typecheck.py`.

## Ubiquitous Language

- **Rule set** — a `List[Specification]` constant in this module.
- **Specification** — a class in `compiler/utils/core.py`. It records findings. It does not mutate the candidate.
- **Common rule set** — `COMMON_RULE_SET`. Ungated. The other ten constants are gated by the event module, not here.

## What this module owns

The constants name the specifications, their ids, and the arguments those specifications are constructed with. `COMMON_RULE_SET` is the component-agnostic list. Each other constant is one component type.

Specification classes stay in `compiler/utils/core.py`. This module imports them and lists them.

## Boundaries

**Inside this domain:** the eleven constants and `ConformanceChecker`.

**Outside this domain:** specification bodies (`compiler/utils/core.py`); which event binds which constant ([events/typecheck.md](../events/typecheck.md)); the YAML gate ([assets.md](../assets.md)).

## Related Documentation

- `compiler/utils/typecheck.py` — this module
- `compiler/utils/core.py` — `Specification` and the specification classes
- [events/typecheck.md](../events/typecheck.md) — the events that bind these constants
