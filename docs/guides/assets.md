# Assets – Strategies and Patterns

**Project:** tiferet-elsl  
**Repository:** https://github.com/greatstrength/tiferet-elsl  
**Module:** `compiler/assets/`  
**Version:** 1.0.0

## Overview

`compiler/assets/` is the packaged catalog the compiler boots from. The pipeline is not a Python package of its own. It is three YAML artifacts in this package, plus the lexer token module.

**Vision:** See the comments at the top of `compiler/assets/feature.yml`, `compiler/assets/cli.yml`, and `compiler/assets/config.yml`.

## Ubiquitous Language

- **Phase** — a feature in `feature.yml`. Phases are component-agnostic.
- **Command** — a CLI feature id `group_key.key` in `cli.yml`.
- **Session** — `compiler` or `compiler_cli` in `config.yml`.
- **Registration** — a `services` entry. `module_path` and `class_name` name the class. The step name does not.

## The three YAML artifacts

`feature.yml` declares the five phases and anchors shared steps at first use. `cli.yml` declares the matching commands. `config.yml` registers every `service_id` and names the two sessions.

Scan and parse do not take a component type. Semantic and both compile commands require `-c` / `--component`. The console script boots `compiler_cli`. It does not implement a phase.

Catalogue repositories are `tiferet-ly` classes. The lexer and parser adapters are `compiler.utils`. The events do not open the YAML files. The repositories do.

## Construct

A phase is a YAML feature, not a Python class. This step is the construct that turns a parsed events file into ElohaSL:

```yaml
- name: Generate Code
  service_id: generate_code_event
  data_key: codegen
  params:
    codegen_service: codegen_service
```

The registration that owns it is:

```yaml
generate_code_event:
  module_path: compiler.events.codegen
  class_name: GenerateCode
```

The source it consumes still has markers such as `# *** events` and `# ** event: get_feature`. The component type arrives as request data. It is not part of the step name.

## Boundaries

**Inside this domain:** the packaged YAML, the session ids, and the service registrations.

**Outside this domain:** event bodies (`compiler/events/`); rule-set constants (`compiler/utils/typecheck.py`); the names the schema test locks (`compiler/tests/test_schema_freeze.py`). This package has no `contexts`, `blueprints`, `di`, or `repos` of its own.

## Related Documentation

- [events/typecheck.md](events/typecheck.md) — the conformance events these registrations point at
- [utils/typecheck.md](utils/typecheck.md) — the rule sets those events bind
- [tests/schema-freeze.md](tests/schema-freeze.md) — the names this package must not rename in place
