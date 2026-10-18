# Core Domain Distillation — ElohaSL

**Status:** Draft · **Domain:** `compiler` · **Code:** `compiler/` (distribution `tiferet-elsl` 1.0.1, BSD-3-Clause, on PyPI; console script `tiferet-compiler`) · **Branch:** `main`
**Companion:** `docs/domain-vision.md`

## 1. Purpose of this document

The vision statement says what ElSL is for. This document says how the domain
works: the vocabulary, the behaviors, the rules those behaviors enforce, and
the way the pieces relate. Read it before changing the pipeline, and before
judging whether a change belongs in this package or in a neighbor.

The import package is `compiler`; the distribution name is `tiferet-elsl`.
The trunk reconstruction through `v1.0.0` is closed, and `v1.0.1` is the
current trunk release. A citation without a prefix is a file in this
repository on `main` at `c0e9bc0` (`v1.0.1`). `tiferet:` means
`greatstrength/tiferet` `main` at `dc64214`, for the import law (re-checked
at `30cec6d`: unchanged).

Earlier drafts cited a pre-reconstruction prototype as `proto:` (commit
`cf07ed5`, which is not in this repository). That prototype is not the
`v1.x-proto` branch. Every behavior those citations described now ships on
trunk, so this document cites trunk only.

All ten dialects have rule lists on trunk, each run by its own gated
conformance event, and the five pipelines are declared in
`compiler/assets/feature.yml` (v0.6.0-v0.7.0; frozen in 1.0.0). Where this document and the code disagree,
the code wins. Sections 7 and 8 record the disagreements that remain.

## 2. The core domain, restated precisely

ElSL's core domain is **verifying and distilling declared structure in
ElohaSL**.

**First principle: the compiler checks one module at a time.** Every
pipeline reads one module, or a stored model of one module, and every
finding is about that module. Package and application levels are beyond
its scope.

A Tiferet source file is not just Python. It carries markers that declare what
the file is composed of and what role each part plays. ElSL treats those
markers as structure to be checked, not as commentary. From them it builds
one structural model of the file, verifies that model against the rules for
the kind of building block the caller named, and distills the model into
organized data. That data is ElohaSL. This compiler reads the declaration
as annotated source and hands the data on. Holding it, or rendering it back
to source, is not this compiler's job.

The domain has one shape:

> **Read** → **Model** → **Verify** → **Distill**

and two axes of variation:

1. **Internal rules** — what a given kind of building block must contain, and
   how its parts must be named and shaped.
2. **Relationship rules** — which other kinds this one may depend on.

The kind is an input. It selects both rulebooks. It is not inferred from
the file. Recognizing markers, building the model, resolving names, and
serializing the result are the same job for all ten kinds. Section 8
inventories that split.

## 3. Ubiquitous language

**ElohaSL** — the declarative language of a Tiferet design. In source it is
Tiferet-structured Python: markers, grouped imports, documented intent, and
named operations. In output it is the organized data those conventions
distill to. ElSL is the short name, and the name of this compiler.

**Component type** — one of Tiferet's ten kinds of building block: `assets`,
`blueprints`, `contexts`, `di`, `domain`, `events`, `interfaces`, `mappers`,
`repos`, `utils`. Supplied by the caller. Not discovered from the file.

**Dialect** — the internal and relationship rules for one component type.
One set of markers, ten dialects.

**Rulebook** — the pair of rule sets for a dialect: what the file must
contain, and what it may depend on. The design commitment is one reader and
ten rulebooks.

**Artifact** — a declared structural unit, introduced by a marker. Three
tiers. A **group** (`# *** imports`) divides the file. A **section**
(`# ** event: ping`) names a unit inside a group, usually one class or one
function. A **member** (`# * method: execute`) is a part of a section: an
attribute, an initializer, or a method.

**Snippet** — one logical step inside a method: a leading comment plus the
statements it describes. The comment is kept separate from the code.

**Annotation** — an inline structured note — an obsolete (`# -- obsolete:`),
todo (`# ++ todo:`), or see (`# >> see:`) marker — attached to an artifact rather than discarded as a comment.

**Token** — the smallest recognized unit of source text, including the
artifact markers and annotations.

**Structural model (AST)** — the tree built from tokens. Its nodes are
declarations, statements, expressions, and types. Artifact tiers are
first-class node kinds. The code calls this tree the AST. This
document uses that name only after this definition.

**Symbol** — a named thing the file defines or imports: a class, a method, an
attribute, a parameter, an import.

**Scope** — a region that owns symbols (module, class, method), identified by
a dotted path such as `module.Ping.execute`.

**Symbol table** — the scopes and their symbols for one file.

**Resolution** — deciding, for each name the file uses, which symbol it refers
to. Names that match nothing are recorded as unresolved.

**Specification** — a rule object the walker calls. A dialect rulebook is a
list of specifications, some shared, some constructed with that dialect's
data.

**Finding** — one collected failure: an error code, a message, and a
position when the model has one. Findings accumulate. The declared pipelines
do not stop distillation because a finding exists.

**Distillation** — turning the model into organized ElohaSL data. The
code still calls this step code generation (`GenerateCode`).

**Pipeline** — an ordered list of those behaviors, declared in configuration
rather than hard-coded in a command name. Each pipeline here is a prefix of
the next, or the same tail started from a stored model.

## 4. What ElSL reads

The dialect adds a small vocabulary on top of Python. The scanner
recognizes it directly (`compiler/assets/lexer.py (6-17)`). The token rules
are declared data (`compiler/assets/tokens.yml`, with `grammars.yml`), loaded
through tiferet-ly's token and grammar repositories:

- Group, section, and member markers — the three artifact tiers.
- Annotation markers — obsolete, todo, and see (`compiler/assets/tokens.yml`).
- Docstrings, as the declared intent of a module, class, or method.
  `DocstringParser` (`compiler/utils/docstring.py:12`) normalizes them; they
  become `desc` in the distilled data, and `:param` / `:return` lines feed
  parameter and return specs.
- Ordinary line comments, which become snippet comments when they lead code.

Two conventions are where the compiler gets its leverage.

**Import grouping.** Imports are divided into `core` (standard library),
`infra` (third-party, including the `tiferet` framework itself when the file
is in a downstream repository), and `app` (this application's own component
layers, imported relatively, such as `..domain`). The common rule
rejects any other group name, and requires each of those groups to contain
only import statements (`compiler/utils/core.py (1347-1430)`,
`INVALID_IMPORT_GROUP` and `INVALID_IMPORT_CONTENT`). The
`app` group is the file's statement of what else in the system it depends
on. Relationship checking reads that group. It does not guess.

**Name concordance.** A section header names its unit in one style; the code
inside must agree. A section expects a class whose PascalCase name matches
the header's snake_case identifier (`compiler/utils/core.py:1432`).
`# ** event: get_feature` requires a class `GetFeature`. A function section
is checked the same way (`compiler/utils/core.py:1482`).

**Named operations.** Computation is recorded as a name and its operands, not
recovered later from syntax. An addition encodes as `Add(left, right)`
(`compiler/domain/ast.py:820`). A return encodes as `Return(inner)`
(`compiler/domain/ast.py:1507`). `Return(Add(a, b))` is that pairing.
The encoding lives on the structural model, so a later renderer can lower
it without this package choosing a target language.

## 5. The six behaviors

Each behavior is a bounded step. Each is a domain event, composed in
`compiler/assets/feature.yml`. Every behavior below ships on trunk.

### 5.1 Lexical scanning

*Turn source text into tokens.*

`PerformLexicalAnalysis` (`compiler/events/lexer.py:23`) reads the
file. Beyond ordinary tokenizing, the dialect keeps artifact markers and
annotations as real tokens, and injects explicit indent and dedent tokens so
block structure — including artifact nesting — is unambiguous downstream
(`TiferetLexer`, `compiler/utils/lexer.py:28`; indent and dedent handling at
`(97-120)`). `EmitScanResult`
(`compiler/events/lexer.py:92`) renders the token stream for
inspection through `ScanOutputWriter` (`compiler/utils/output.py:16`): YAML by
default, JSON when asked or when `-o` ends in `.json`.

**Agnostic on both axes.** Markers look the same in every dialect. This step
does not take a component type.

### 5.2 Syntactic parsing

*Turn tokens into one structural model.*

`PerformSyntacticAnalysis` (`compiler/events/parser.py:25`) drives a
thin adapter over `tiferet_ly.utils.parse.PlyParser`
(imports at `compiler/utils/parser.py (10-13)`; the `PlyParser` subclass at
`:372`; `TiferetParser`, the parser service, at `:435`). The model is Tiferet-aware rather than a generic Python tree
(`compiler/domain/artifact.py`, `ArtifactDeclaration`, `ArtifactStatement`,
`SnippetStatement`): groups and sections are
their own statement kind, members carry an explicit role, snippets keep
leading comments separate from code, and annotations stay on the artifact.

`EmitParseResult` (`compiler/events/parser.py:131`) serializes the
model. `LoadFromAST` (`compiler/events/codegen.py:176`) reads a stored
model back, so later stages can run without re-parsing source. The stored
model is the serialized form of the AST transfer objects
(`compiler/mappers/transfer.py`: `TypeTransferObject` :91,
`ParamListTransferObject` :160, `DeclarationTransferObject` :231,
`StatementTransferObject` :329). Parameter lists and statement sequences are
linked `.next` chains, not lists. That shape is part of the 1.0.0 frozen
schema (`compiler/tests/test_schema_freeze.py`).

A position helper in the adapter (`make_position_helpers`,
`compiler/utils/parser.py:258`) has no dialect coupling. It is not ElohaSL
domain, and is a candidate to move into tiferet-ly. The trunk code does not
mark it for that move.

**Agnostic on both axes.** Every dialect uses the same tiers, members, and
snippets. The generic parse engine is tiferet-ly's. This domain owns the
dialect vocabulary the engine is asked to recognize, and on trunk that
vocabulary is declared data: `compiler/assets/productions.yml` (grammar
productions), plus the node rewrite table and artifact block parser
(`compiler/utils/artifact.py:12`) the adapter applies.

### 5.3 Semantic analysis

*Establish what the file defines and what its references mean.*

`PerformSemanticAnalysis` (`compiler/events/semantic.py:17`) runs two
passes (`compiler/utils/semantic.py`).

The symbol-table builder (`SymbolTableBuilder`, `compiler/utils/semantic.py:417`) opens a
scope for each module, class, and method, and registers the symbols it
finds, including imports and attributes assigned through `self`. Artifact
tiers are structural, not lexical, so the builder descends through them
without creating scopes. Scopes are keyed by dotted path
(`compiler/domain/semantic.py`, `Symbol` and `Scope`).

The name resolver (`NameResolver`, `compiler/utils/semantic.py:702`) walks the model
again. For every name used, it finds the nearest scope that defines it,
walking outward from the current scope to the module, with `self.x` resolved
against the enclosing class. Each lookup is recorded as resolved or
unresolved.

**Agnostic in mechanism, on both axes.** This step does not apply a dialect
rulebook. It produces the evidence relationship checking needs: resolved
import symbols, with the modules they came from. Judging those imports is
the next behavior, and it requires the component type.

### 5.4 Conformance

*Verify that the file is a valid instance of what it claims to be.*

Component type is an input. On the semantic-bearing commands it arrives as
`-c` / `--component`, required, with the ten names as the legal choices
(`compiler/assets/cli.yml (1-2)`, `(64-82)`; locked by
`compiler/tests/test_schema_freeze.py`). The walker is one
`ConformanceChecker` (`compiler/utils/typecheck.py:431`), a
`StatementWalker`. The checker file does not branch on component type. The
rule list it is given does.

Findings are collected rather than failing on the first one
(`TypeCheckError`, `compiler/domain/typecheck.py:17`). The specifications on
trunk can record 54 distinct finding codes; the `elsl-rule-sets` skill lists
each code by specification.

The common family runs for every component type
(`COMMON_RULE_SET`, `compiler/utils/typecheck.py (41-74)`): import groups limited to
`core`, `infra`, and `app`; a named section must contain the unit it
advertises; an attribute member must be a variable declaration; a method
member must be a function. Assignments and arithmetic are checked shallowly
against declared and inferred types. That shallow check serves conformance.
It is not a general type system.

The checker does not branch on component type. All ten dialect rule lists
are constants on `compiler/utils/typecheck.py`: `EVENT_RULE_SET` (`:77`),
`DOMAIN_RULE_SET` (`:85`), `DI_RULE_SET` (`:132`), `INTERFACE_RULE_SET`
(`:166`), `MAPPER_RULE_SET` (`:196`), `UTILS_RULE_SET` (`:233`),
`REPOS_RULE_SET` (`:266`), `ASSET_RULE_SET` (`:309`), `CONTEXTS_RULE_SET`
(`:346`), and `BLUEPRINTS_RULE_SET` (`:391`). A caller passes one list.
`PermittedGroupSpecification`, `AppImportSpecification`, and
`RequiredBaseSpecification` (`compiler/utils/core.py (2000-2397)`) supply
constructor data. The dialect-specific specifications follow them
(`compiler/utils/core.py (2398-3235)`). Unique classes on the walker — event sections,
domain attributes, group-section agreement, abstract-method shape, mapper
roles, context-manager pairing, constant names, and repository CRUD methods —
are instantiated by those lists. `EVENT_RULE_SET` does not judge `app` imports.

Selecting a list by component type ships on trunk (#37, `v0.7.0`). It is one
common event plus ten dialect events (`compiler/events/typecheck.py (87-502)`,
`CheckCommonConformance` at `:88` through `CheckReposConformance` at `:467`,
on the shared `ConformanceEvent` base at `:31`), gated by
`$r.component == '...'` (`compiler/assets/feature.yml (44-93)`). Each
dialect event passes its rule-set constant; the data is constructor
arguments, not copied walker logic.

Findings reach the user only as printed lines. `semantic` prints each
finding to standard output and exits `0`. The finding list is not written
to the `-o` result, and `compile` runs the same gates but does not print or
emit their findings (`compiler/events/semantic.py (113-136)`). How findings
should be reported is open; see section 9.

**Variable on both axes.** The walker is agnostic. Which rule list runs, and
what data that list was constructed with, is the dialect. Section 7 records
what those relationship lists actually contain, including the dialect that
has none.

### 5.5 Distillation

*Turn the model into organized ElohaSL data.*

`GenerateCode` (`compiler/events/codegen.py:21`) delegates to
`TiferetGenerator.generate` (`compiler/utils/codegen.py:801`).
The walk is generic: it dispatches on artifact group name and collects
imports, functions, and ordered groups into a `cmpt` envelope keyed by the
requested component type. That envelope — name, kind, description, imports,
groups — is the component-neutral shape.

The same method still special-cases events. The default `kind` is
`'events'`. When the kind is events, a legacy `evt_grp` shape is emitted
beside `cmpt`, for an external reader of the older envelope
(`compiler/utils/codegen.py (876-886)`). The reader is an external consumer
of the older envelope; it is not in this repository. Both the `'events'`
default and the dual output were specified by TRDs #29 and #32, and the
events output is frozen in 1.0.0.

**The walk is agnostic. The output vocabulary is variable.** `cmpt` is the
ElohaSL shape. `evt_grp` is a legacy shim, not part of the language. It is
nonetheless part of the 1.0.0 frozen output for `-c events`, so removing it
needs a freeze decision (section 10, item 4).

### 5.6 Optimization and emission

*Compact the output, then write it.*

`OptimizeCode` (`compiler/events/codegen.py:70`) runs an optimizer
(`YamlAnchorOptimizer`, `compiler/utils/optimizer.py:270`) that finds repeated parameter and
return structures and replaces them with shared references, so the serialized
form can use anchors instead of repeating itself. The level is the `-O`
option: `O0` (the default) skips the optimizer, and `O1` runs it. Shared lists
are hoisted under a top-level `vars` key, present only when duplicates exist
(TRD #30). `EmitCodegenResult`
(`compiler/events/codegen.py:127`) writes the result as YAML or JSON
(`--output-format yaml|json|auto`). Format selection
and human-readable rendering live beside it
(`compiler/utils/output.py:16`, `compiler/utils/printer.py:14`).

The compacting mechanic is generic. Trunk still carries a rewrite
that walks the legacy `evt_grp` envelope
(`EvtGrpEnvelopeRewrite`, `compiler/utils/optimizer.py:137`) next to one that walks `cmpt`
(`CmptEnvelopeRewrite`, `compiler/utils/optimizer.py:174`). When both envelopes are present,
`collect_lists` applies the first matching rewrite and stops, and the events
rewrite is first (`collect_lists`, `compiler/utils/optimizer.py:321`;
dispatch at `(334-336)`). TRD #30 specifies that order.

**Agnostic in mechanic, variable in the envelope it knows how to walk.**

## 6. How the behaviors compose

Pipelines are declared, not named per component type
(`compiler/assets/feature.yml (1-4)`, #33, `v0.6.0`). Five of them exist. Each of
the first four is a prefix of the next. The fifth starts from a stored
model. Steps hand results forward by named key (`tokens`, `ast`, `semantic`,
`findings`, `codegen`).

- **scan / module** — tokens, then the scan result (`feature.yml (6-16)`).
- **parse / module** — tokens, then the structural model (`(17-28)`).
- **semantic / module** — plus the symbol table, resolution, the common
  rules, the dialect rules gated on component type, and an analysis result
  (`(29-95)`).
- **compile / module** — plus distillation, optimization, and emission
  (`(97-129)`). It runs the semantic prefix but has no analysis-result step.
- **compile / ast** — the same tail, starting from a stored model
  (`(130-151)`).

The command surface uses the same split. The command name is `module` (or
`ast`). The component type is an argument, not a command
(`compiler/assets/cli.yml`). The command surface ships as the `tiferet-compiler` console script
(`compiler.cli:main`), which boots the `compiler_cli` session. The session
config resolves relative to the installed package (#39); the catalog paths
still resolve against the working directory, a known regression with a
hotfix pending. The command
names, the ten `-c` choices, the session ids, the seven packaged YAML
basenames, the envelope keys, and the findings contract are a frozen surface (`compiler/tests/test_schema_freeze.py`,
#41, `v1.0.0`).

```mermaid
flowchart LR
  SRC([Source file]) --> LEX["Scan"]
  LEX --> PARSE["Parse"]
  PARSE --> SEM["Symbols and resolution"]
  SEM --> CHK["Conformance"]
  CHK --> GEN["Distill cmpt"]
  GEN --> OPT["Optimize"]
  OPT --> OUT([Emit])
  STORED([Stored model]) --> LOAD["Load model"]
  LOAD --> SEM
```

The diagram is `compile / module`, plus the stored-model entry. `scan` and
`parse` stop earlier. Nothing in the declared pipeline skips distillation
because findings were collected.

## 7. Relationships between component types

Verifying a file in isolation is only half the domain. The other half is
verifying its place among the ten component types.

Three facts make that checkable here and not by a generic linter:

1. The evidence is already in the model. Every dependency the file takes is
   a resolved import symbol with a recorded source module. Semantic analysis
   produces that evidence.
2. The declared group carries intent. Because imports are grouped into
   `core`, `infra`, and `app`, the checker does not guess which imports are
   internal.
3. The judgment requires the component type. The same import line is legal
   in one dialect and a violation in another.

The mechanism is `AppImportSpecification`
(`compiler/utils/core.py:2089`). A dialect passes the component types it
allows, whether same-package siblings are allowed (the default is yes), and
whether the framework-root `a` alias is allowed. The walker does not know
the sets.

There are two sources for those sets, and they do not match. Both are cited.
Neither is silently preferred.

**The framework import law**, as checked for this document, is the
architecture skill (`tiferet:.agents/skills/tiferet-code-architecture/SKILL.md (18-29)`).
The skill points at `docs/core/architecture.md`. That file is not in the
tiferet tree at `dc64214`. The skill is the law that is actually present.

- `assets` and `domain` import no framework package.
- `events` may use `assets`, `domain`, `mappers`, `utils`, and `interfaces`.
  It may not use `di`, `repos`, `contexts`, or `blueprints`.
- `mappers` may use `domain` only.
- `interfaces` may use `mappers`, and sibling interfaces. They may not import
  `domain` when the mapper layer already exposes that type.
- `di` may use `domain` and `interfaces`. It is event-free and asset-free.
- `utils` may use `interfaces`, `mappers`, and siblings.
- `repos` may use `interfaces`, `mappers`, and `utils`.
- `contexts` may use `assets`, `domain`, sibling contexts, and `events`.
  Repositories and utilities arrive by injection, not by import.
- `blueprints` may use `assets`, `contexts`, `di`, and `events` (bootstrap
  only). They reach domain types through contexts, not by importing them.

**The sets trunk enforces** are the `AppImportSpecification` arguments on
the ten rule lists (`compiler/utils/typecheck.py (77-428)`). They match the
prior-art constructor arguments that earlier drafts cited:

- `events` — no relationship specification. `EVENT_RULE_SET` contains only
  the event-section rule (`compiler/utils/typecheck.py:77`).
- `domain` — siblings, or `assets` (`:103`).
- `di` — siblings, or `domain` and `interfaces` (`:149`).
- `interfaces` — siblings, or `mappers` (`:182`).
- `mappers` — siblings, or `domain` and `events` (`(209-215)`).
- `utils` — siblings, or `interfaces` and `mappers` (`:249`).
- `repos` — siblings, or `interfaces`, `mappers`, and `utils` (`:281`).
- `assets` — siblings only; no framework-root alias (`:326`).
- `contexts` — siblings, or `assets`, `domain`, and `events`, and the
  framework-root alias (`:364`).
- `blueprints` — siblings, or `assets`, `contexts`, `di`, and `events`, and
  the framework-root alias (`:408`).

The disagreements that matter:

- **Events are unchecked.** The trunk list has no relationship rule.
  The skill's events row is not enforced.
- **Domain.** The skill forbids every framework import. The trunk
  checker allows `assets`.
- **Di.** The trunk list matches the skill: `domain` and
  `interfaces`, and no assets.
- **Mappers.** The skill allows `domain` and forbids `events`. The trunk
  checker allows both (`compiler/utils/typecheck.py (209-215)`).
- **Interfaces.** The skill's exception for importing `domain` is not a
  specification. The checker allows `mappers` and siblings, and does not
  state that exception.

A dependency that must arrive by injection rather than import is expressed
only as an absence from the allow-list. There is no separate finding for
"right dependency, wrong path."

A rulebook copied into a skill, a distillation, and constructor arguments
will drift, and a drifting rulebook produces false findings. Section 10
names one declared source as a candidate. It does not perform that work.

## 8. The agnostic core and the variable edge

The compiler lives in `compiler/`. The full pipeline is on trunk: all ten
dialect rule lists, eleven gated conformance events, and five declared
pipelines (v0.6.0-v0.7.0, frozen in 1.0.0). The last list records behavior
that trunk carries deliberately.

**Agnostic — build once, not once per component type:**

- Token recognition, including artifact markers and annotations.
- Indentation and block structure.
- The structural model: tiers, members, snippets, annotations, declarations,
  statements, expressions, types.
- Scope construction, symbol registration, and name resolution.
- Finding collection.
- The walker, and the specification objects it calls.
- Optimization mechanics, emission, and formatting.
- The generic parse engine. That one is already outside this domain, in
  tiferet-ly.

**Variable — one definition per component type:**

- The internal rulebook: which groups are expected, what each section must
  contain, which members are mandatory.
- The relationship rulebook: the permitted dependency set, and which
  dependencies must not be taken by import.
- The distilled vocabulary, to the extent a dialect needs fields the common
  envelope does not name. The envelope itself (`cmpt`, with `kind`) is the
  agnostic contract. Dialect-specific keys inside it are the variable part.

**Carried into trunk (specified by TRDs, frozen in 1.0.0); removal is proposal work:**

- `generate` defaults `kind` to `'events'`
  (`compiler/utils/codegen.py:801`, TRD #29), and `GenerateCode` defaults
  `component` to `'events'` (TRD #32). The CLI always passes `-c`, so the
  default is reached only by direct calls.
- Events dual-emit `evt_grp` beside `cmpt`
  (`compiler/utils/codegen.py (876-886)`, TRD #29). That shim is a legacy
  envelope, not ElohaSL, but it is frozen output in 1.0.0.
- When both envelopes are present, `collect_lists` walks `evt_grp` and
  stops (`compiler/utils/optimizer.py:321`, dispatch `(334-336)`, TRD #30).
- Conformance selection is eleven event classes
  (`compiler/events/typecheck.py (87-502)`) gated by ten conditions
  (`compiler/assets/feature.yml (44-93)`, TRD #37). The walker is not
  subclassed per dialect.
- The events dialect has no relationship specification
  (`compiler/utils/typecheck.py:77`). The domain list allows `assets`. The
  mapper list allows `events`. Section 7 has the lines.

## 9. Boundaries

**Inside the domain:** recognizing ElohaSL, modeling it, verifying internal
conformance, verifying relationship conformance, distilling to ElohaSL data,
and reporting findings with a location.

**Outside the domain:**

- Running components, and resolving injection at runtime — the Tiferet
  framework.
- Storing a project's design, rendering it back to source, and organizing
  projects. The distilled data is the handoff. This compiler does not name
  or depend on the tool that holds it.
- Holding a whole system in view, and orchestrating it. That is outside
  this compiler.
- The generic lex-and-parse engine — tiferet-ly. This domain supplies the
  dialect vocabulary. The dialect-free position helper is a candidate for an
  upstream move (section 10).
- General-purpose static analysis, and full type inference. Type reasoning
  here exists only to serve conformance.

## 10. Where this leads

Each item is a candidate for its own later proposal. None is opened here.
No identifier is minted.

1. **Done (v0.6.0, #33): the agnostic pipeline.** Read, model, verify, distill ships
   as one component-agnostic command surface in the `compiler` package
   (packaged in `v1.0.0`). The `'events'` default on `generate` was kept by
   TRD #29 (section 8). Whether the package is ever renamed
   `tiferet_elsl` is not decided here.
2. **Done (v0.7.0, #34-#37): the conformance step.** All ten rule lists
   exist, and eleven gated events select one by component type. No
   checker subclass was added per dialect. Collapsing the eleven events and
   ten gates into one selecting step is still a candidate.
3. **One declared relationship rulebook.** Documentation and the checker
   read the same sets. Reconcile the skill and the trunk constructor
   arguments, and add the missing events rule. Until that exists, do not
   enforce a set copied from either side alone.
4. **`cmpt` as the ElohaSL contract.** Candidate: drop the `evt_grp`
   dual-emit and the optimizer's preference for it. Trunk still emits it
   under the 1.0.0 freeze, so this needs a freeze id. An external reader
   may keep its own shim.
5. **Dialect-free parser helpers in tiferet-ly.** Candidate: move the
   position helpers (`compiler/utils/parser.py:258`), which have no dialect
   coupling, into tiferet-ly. Neither repository records that move yet. Do
   not grow them here.
