# Utils – Codegen

**Project:** tiferet-elsl  
**Repository:** https://github.com/greatstrength/tiferet-elsl  
**Module:** `compiler/utils/codegen.py`  
**Version:** 1.0.0

## Overview

This module turns a parsed module into ElohaSL. The document is a component envelope, not the source file. **Vision:** see the `TiferetGenerator` class docstring in `compiler/utils/codegen.py` for the value statement this guide distills.

## Ubiquitous Language

- **ElohaSL** — the distilled document. In this compiler that is `cmpt`, plus `evt_grp` when the requested kind is `events`.
- **Component envelope** — `cmpt`. It names the module, records the requested kind, and lists the groups that were built.
- **Named operation** — an encoded statement such as `Return(Add(a, b))`. The source syntax is not kept.
- **Snippet** — one logical step, serialized as `coms` and `stmt`.

## What the module emits

`generate` always returns `cmpt`. `kind='events'` also returns `evt_grp`. Other kinds omit that key. Empty sections are omitted rather than emitted empty.

Import rows are `{src, tgts}`. Constants stay on their group. Functions and events are dual-emitted on `evt_grp` only. `exports` is not a group. An unknown group name is treated as events.

Conformance findings are not part of this document. A finding says the source failed a rule. The envelope says what distillation recorded.

## Construct

A construct is the source marker plus the keys it emits. This method:

```python
# * method: execute
def execute(self, id: str) -> Feature:
    '''
    :param id: The feature id.
    :return: The feature.
    '''

    # Load the feature.
    return feature
```

becomes:

```yaml
execute:
  params: ['id:str:true::The feature id.']
  returns: ['Feature:The feature.']
  snpt:
    - coms: ['Load the feature.']
      stmt: ['Return(feature)']
```

`execute` has no `desc`. `self` is not a parameter. An empty section is omitted.

## Boundaries

**Inside this domain:** the envelope keys, the group entries, and the encoded statements inside snippets.
**Outside this domain:** which command produces the envelope ([cli.md](../cli.md)); which rule rejected the source ([typecheck.md](typecheck.md)); the names the schema test locks ([tests/schema-freeze.md](../tests/schema-freeze.md)).

## Related Documentation

- `compiler/utils/codegen.py` — `TiferetGenerator`
- `compiler/domain/ast.py` — `encode`
- [cli.md](../cli.md) — `compile module` and `compile ast`
- [docs/core/code_style.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/code_style.md) — artifact comments and formatting
