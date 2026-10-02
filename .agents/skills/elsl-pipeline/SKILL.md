---
name: elsl-pipeline
description: >
  Use when changing a compiler phase, a feature step, a CLI command, or an
  event that is a pipeline step. Phrases: "add a pipeline step", "change a
  phase", "wire a CLI command", "edit scan.module", "parse.module",
  "semantic.module", "compile.module", "compile.ast". Not for dialect rule
  text or a frozen-surface rename.
---

# Change a compiler pipeline step

## When to use
- Changing a phase, a feature step, a CLI command, or an event that is a pipeline step.
- Wiring or reordering `scan.module`, `parse.module`, `semantic.module`, `compile.module`, or `compile.ast`.

## When not to use
- A rule set, a specification, or a gated conformance event — `elsl-conformance` and `elsl-rule-sets`.
- A frozen-surface rename — `elsl-schema`.
- Code style, TRDs, RFPs, or reports — the Tiferet skills. Do not vendor them.

## Canonical source
- `compiler/assets/feature.yml`
- `compiler/assets/cli.yml`
- `compiler/assets/config.yml`
- The catalog below is the operator copy. If a YAML edit and this skill disagree, the YAML on the branch wins, and this skill is updated in the same change.

## Inputs
- The phase, command, or event being changed.
- `docs/collab/binding.md` for strand, owner/repo, and proto branch.
- A GitHub issue. **Trunk** reconstruction also needs a published TRD and a freeze id. **Prototype** work needs a published RFP, and only if binding.md says that strand is active.

## Catalog

Five commands. Feature id is `group_key.key`.

| Command | Component flag | Steps, in order |
|---|---|---|
| `scan.module` | none | Tokenize, Emit Scan Result |
| `parse.module` | none | Tokenize, Parse, Emit Parse Result |
| `semantic.module` | required | Tokenize, Parse, Build Symbols, Check Common Conformance, the ten gated dialect checks, Emit Semantic Result |
| `compile.module` | required | the semantic prefix through the dialect checks, then Generate Code, Optimize Code, Emit Codegen Result. No Emit Semantic Result |
| `compile.ast` | required | Load From AST, then Build Symbols through Emit Codegen Result. No Tokenize, no Parse |

`-c` / `--component` choices, in `cli.yml` order: `assets`, `blueprints`, `contexts`, `di`, `domain`, `events`, `interfaces`, `mappers`, `repos`, `utils`.

`compile.module` and `compile.ast` take `-O`. `O0` leaves codegen unchanged. `O1` shares repeated structures. A missing or empty `O` is `O0`.

Sessions in `config.yml`: `compiler` and `compiler_cli`. `compiler.cli:main` boots `compiler_cli`.

Shared steps are YAML anchors, defined once. `&tokenize_step` is defined on scan. Editing it changes every phase that aliases it.

| Step | `service_id` | Class | Module | `data_key` |
|---|---|---|---|---|
| Tokenize | `perform_lexical_analysis_event` | `PerformLexicalAnalysis` | `compiler.events.lexer` | `tokens` |
| Emit Scan Result | `emit_scan_result_event` | `EmitScanResult` | `compiler.events.lexer` | none |
| Parse | `perform_syntactic_analysis_event` | `PerformSyntacticAnalysis` | `compiler.events.parser` | `ast` |
| Emit Parse Result | `emit_parse_result_event` | `EmitParseResult` | `compiler.events.parser` | none |
| Build Symbols | `perform_semantic_analysis_event` | `PerformSemanticAnalysis` | `compiler.events.semantic` | `semantic` |
| Check Common Conformance | `check_common_conformance_event` | `CheckCommonConformance` | `compiler.events.typecheck` | `findings` |
| Check Event Conformance | `check_event_conformance_event` | `CheckEventConformance` | `compiler.events.typecheck` | `findings` |
| Check Asset Conformance | `check_asset_conformance_event` | `CheckAssetConformance` | `compiler.events.typecheck` | `findings` |
| Check Domain Conformance | `check_domain_conformance_event` | `CheckDomainConformance` | `compiler.events.typecheck` | `findings` |
| Check Mapper Conformance | `check_mapper_conformance_event` | `CheckMapperConformance` | `compiler.events.typecheck` | `findings` |
| Check Interface Conformance | `check_interface_conformance_event` | `CheckInterfaceConformance` | `compiler.events.typecheck` | `findings` |
| Check DI Conformance | `check_di_conformance_event` | `CheckDIConformance` | `compiler.events.typecheck` | `findings` |
| Check Utils Conformance | `check_utils_conformance_event` | `CheckUtilsConformance` | `compiler.events.typecheck` | `findings` |
| Check Context Conformance | `check_context_conformance_event` | `CheckContextsConformance` | `compiler.events.typecheck` | `findings` |
| Check Blueprints Conformance | `check_blueprints_conformance_event` | `CheckBlueprintsConformance` | `compiler.events.typecheck` | `findings` |
| Check Repos Conformance | `check_repos_conformance_event` | `CheckReposConformance` | `compiler.events.typecheck` | `findings` |
| Emit Semantic Result | `emit_semantic_result_event` | `EmitSemanticResult` | `compiler.events.semantic` | none |
| Generate Code | `generate_code_event` | `GenerateCode` | `compiler.events.codegen` | `codegen` |
| Optimize Code | `optimize_code_event` | `OptimizeCode` | `compiler.events.codegen` | `codegen` |
| Emit Codegen Result | `emit_codegen_result_event` | `EmitCodegenResult` | `compiler.events.codegen` | none |
| Load From AST | `load_from_ast_event` | `LoadFromAST` | `compiler.events.codegen` | `ast` |

The context row is not a typo. The step and `service_id` say `context`. The class is `CheckContextsConformance`.

`GenerateCode` reads `component` and passes it to the generator as `kind`. A missing `component` on a direct call defaults to `events`. The CLI still requires the flag on semantic and both compile commands. Conformance events do not read `component`.

Catalogue services are `tiferet-ly`, not compiler classes:

- `token_service` → `tiferet_ly.repos.token.TokenConfigRepository`
- `grammar_service` → `tiferet_ly.repos.grammar.GrammarConfigRepository`
- `production_service` → `tiferet_ly.repos.production.ProductionConfigRepository`
- `lexer_service` → `compiler.utils.lexer.TiferetLexer`
- `parser_service` → `compiler.utils.parser.TiferetParser`
- `codegen_service` → `compiler.utils.codegen.TiferetGenerator`
- `optimizer_service` → `compiler.utils.optimizer.YamlAnchorOptimizer`

`PerformLexicalAnalysis` does not open `tokens.yml` or `grammars.yml`. `PerformSyntacticAnalysis` does not open grammar, token, or production YAML. `TiferetParser` hosts no `p_*` productions.

## Relation to ElohaSL

`compile.module` and `compile.ast` are the commands that emit the language. Scan, parse, and semantic do not. The component flag becomes `cmpt.kind`. It is not a command name.

`GenerateCode` is the step that asks `TiferetGenerator` for the envelope. `OptimizeCode` may share repeated structures at `O1`. It does not rename keys. Read `elsl-language` before changing what those steps emit. This skill owns the wiring, not the document shape.

## Procedure
1. Use the catalog above. Then open the YAML you are editing and match it.
2. Change the feature step, the registered class, and the event together. A shared anchor is one edit.
3. Do not add `scan.event` or `compile.event`. Do not put phase logic in `compiler/cli.py`.
4. A new public command or a new component choice is `elsl-schema`, not a pipeline-only edit.
5. **Trunk** — implement against the published TRD. Do not copy from proto.
6. **Prototype** — only if binding.md says the prototype strand is active. Do not cut that branch from this skill.

## Outputs
- The phase, command, and event change on the strand branch, in a PR to that strand. Not an issue body.

## Guardrails
- Never commit or merge unless asked.
- Never proto → trunk git.
- Never implement trunk reconstruction from a live proto branch.
- Never author a reconstruction TRD without a freeze id.
- Read `docs/collab/binding.md` in this repo for owner/repo, proto branch, and project ids.
- Do not vendor Tiferet skills into this repo.
- Do not treat a guide as the source for this catalog.
- This package has no contexts, blueprints, di, or repos. Do not add them to wire a step.
