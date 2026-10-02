---
name: elsl-language
description: >
  Use when reading, explaining, or changing an ElohaSL construct. Phrases:
  "ElohaSL", "ElSL", "what does this marker emit", "event section", "snippet",
  "cmpt", "evt_grp", "named operation". Not for wiring a pipeline step unless
  the question is what the construct becomes.
---

# Read an ElohaSL construct

## When to use
- Explaining what a source marker, member, or statement becomes in the compiled document.
- Changing the generator for one of those constructs.

## When not to use
- Wiring a phase — `elsl-pipeline`.
- Adding a specification — `elsl-rule-sets`. A rule judges the source construct. It does not appear in the document.
- Renaming a frozen key — `elsl-schema`.

## Canonical source
- `compiler/utils/tests/test_codegen.py` — the pairs below are taken from those locks.
- `compiler/utils/codegen.py` — `TiferetGenerator.generate`.
- `compiler/domain/ast.py` — `encode`.

## Inputs
- The source construct, or the emitted key being read.
- `docs/collab/binding.md` when the work will edit the generator.

## How to read a construct

ElohaSL here is the compiled document, not the Python source. A construct is a source marker plus the keys it emits. A missing key means the construct was absent or empty. It does not mean an empty list.

`compile` with `-c events` emits `cmpt` and `evt_grp`. Any other `-c` emits `cmpt` only. `cmpt` never contains `evt_grp`.

## Module

```python
"""Feature events."""
```

emits `cmpt.desc` and, for events, `evt_grp.desc`, both `Feature events.` The quotes are stripped. No docstring means `desc` is absent.

An empty module is still `{'name': 'feature', 'kind': 'events'}`. `kind` is the requested component, not something discovered from the file.

## Import group

```python
# *** imports

# ** core
from typing import Any, Dict

# ** app
from ..domain import Feature
```

emits `cmpt.impt`, not a group entry:

```yaml
core:
  - {src: typing, tgts: [Any, Dict]}
app:
  - {src: ..domain, tgts: [Feature]}
```

Two symbols from one module collapse into one row. First-seen module order is kept. The categories are the section names `core`, `infra`, and `app`.

## Event section

```python
# *** events

# ** event: get_feature
class GetFeature:
    '''Retrieve a feature by identifier.'''
```

The section name is the key. The class name is the payload name.

```yaml
evt_grp:
  evts:
    get_feature:
      name: GetFeature
      desc: Retrieve a feature by identifier.
```

`cmpt.grps` also gets an events group. A class with no base has no `base` key. Do not invent one.

`# *** exports` is skipped. It is not emitted as an event group.

## Members

```python
# * attribute: feature_id
feature_id: str = 'missing'

# * init
def __init__(self, feature_service: FeatureService):
    '''
    :param feature_service: The feature service.
    '''

# * method: execute
def execute(self, id: str) -> Feature:
    '''
    :param id: The feature id.
    :return: The feature.
    '''

    # Load the feature.
    return feature
```

emits, on that event payload:

```yaml
attributes:
  - feature_id: {type: str, init: missing}
injections:
  - feature_service:FeatureService:true::The feature service.:
      assign: [{target: feature_service, value: feature_service}]
execute:
  params: ['id:str:true::The feature id.']
  returns: ['Feature:The feature.']
  snpt:
    - coms: ['Load the feature.']
      stmt: ['Return(feature)']
```

`execute` has no `desc`, even when the method docstring has a summary. `self` is not a parameter. A method whose inner name is not `execute` goes in `methods`, keyed by that name.

Parameter spec is `name:type:required:default:desc`. An injection spec leaves the default slot empty: `name:type:required::desc`.

## Function and blueprint

```python
# *** functions

# ** function: build_app
def build_app(name: str) -> App:
    '''Build the application.'''
```

emits `cmpt.grps[].fncs.build_app`, and `evt_grp.fncs.build_app` when kind is events. It does not appear under `evts`.

A blueprint uses the same callable shape. Only the group name changes:

```python
# *** blueprints

# ** blueprint: build_app
def build_app(name: str) -> App:
    ...
```

emits `grps[].name == blueprints` and `fncs.build_app.params == ['name:str:true::']`, `returns == ['App:']`.

## Constant

```python
# *** constants

# ** constant: feature_not_found_id (ids)
FEATURE_NOT_FOUND_ID = 'FEATURE_NOT_FOUND'
```

emits a constants group. The key is the assignment target, not the section name.

```yaml
grps:
  - name: constants
    qual: ids
    csts:
      FEATURE_NOT_FOUND_ID: {value: FEATURE_NOT_FOUND}
```

Constants are not copied to the envelope root.

## Named operation

A snippet comment becomes `coms`. The statement becomes `stmt` through `encode`, not through a pretty-printer.

| Source | `stmt` |
|---|---|
| `return feature` | `Return(feature)` |
| `return a + b` | `Return(Add(a, b))` |
| `self.name` | `Attr(self, name)` |
| `verify(...)` | `Call(verify, ...)` |

`encode` returns an empty string when a kind has no encoding. Comments, artifact headers, imports, and f-strings do not become statements.

## Conformance

A finding is not a construct in this document. `# *** imports` may fail `INVALID_IMPORT_GROUP` and still be the construct that, when it passes, becomes `impt`. Do not put the error code on `cmpt`.

## Procedure
1. Name the source construct first: group, section, member, or statement.
2. Read the emitted keys for that construct above. Then confirm against `compiler/utils/tests/test_codegen.py` if the edit touches the generator.
3. Treat a missing key as omitted.
4. **Trunk** — renaming an emitted key is `elsl-schema` before it is a generator edit.
5. **Prototype** — only if binding.md says that strand is active.

## Outputs
- An explanation of one construct, or a generator change on the strand branch, in a PR. Not an issue body.

## Guardrails
- Never commit or merge unless asked.
- Never proto → trunk git.
- Never implement trunk reconstruction from a live proto branch.
- Never author a reconstruction TRD without a freeze id.
- Read `docs/collab/binding.md` in this repo for owner/repo, proto branch, and project ids.
- Do not vendor Tiferet skills into this repo.
- Do not describe a construct by its envelope key alone. Show the source marker that produces it.
- Do not treat a guide as the source for these pairs.
