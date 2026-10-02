# Schema Freeze Test

**Project:** tiferet-elsl  
**Repository:** https://github.com/greatstrength/tiferet-elsl  
**Module:** `compiler/tests/test_schema_freeze.py`  
**Version:** 1.0.0

## Overview

This test is the lock on the public compiler surface for `1.0.0`. `compiler/CHANGELOG.md` names the same release. A later move of a locked name is a freeze decision, not a silent rename.

## Ubiquitous Language

- **Frozen surface** — a name or shape this test asserts, or a public schema the changelog names.
- **Envelope** — the codegen dict. `cmpt` is always present. `evt_grp` is present only for events.
- **Transfer chain** — the persistence shape that links parameters and statements through `.next`.

## What this test owns

It locks the package version, the distribution name, the five commands, the ten component choices, the two session ids, the const keys, the seven YAML basenames, the codegen envelope, the `.next` chains, and the findings list.

It does not lock rule-set contents, specification ids, feature step order, or service class names. Those live in the modules that own them.

## Construct

The lock is on the keys a construct emits, not on the prose around them.

```python
# ** event: get_feature
class GetFeature:
    # * method: execute
    def execute(self):
        # Load the feature.
        return feature
```

compiled with `-c events` must keep `cmpt` and `evt_grp` as siblings, the event under `evt_grp.evts`, and the snippet keys `coms` and `stmt`. Renaming any of those is a freeze decision.

## Boundaries

**Inside this domain:** the assertions in `compiler/tests/test_schema_freeze.py`.

**Outside this domain:** how a phase is wired ([assets.md](../assets.md)); how a dialect is gated ([events/typecheck.md](../events/typecheck.md)); how a freeze is opened, which stays on the Tiferet skills.

## Related Documentation

- `compiler/tests/test_schema_freeze.py` — this test
- `compiler/CHANGELOG.md` — the named public schemas for `1.0.0`
- [assets.md](../assets.md) — the YAML this test reads
