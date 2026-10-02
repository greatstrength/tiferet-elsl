# Pipeline – Strategies and Patterns

**Project:** tiferet-elsl  
**Repository:** https://github.com/greatstrength/tiferet-elsl  
**Module:** `compiler/`  
**Version:** 1.0.0

## Overview

The compiler runs five component-agnostic phases. A phase is a feature in `compiler/assets/feature.yml`. The component type is request data, not part of the command name. Scan and parse never take a component. Semantic analysis and both compile commands require one.

The console script `tiferet-compiler` (`compiler.cli:main`) boots the `compiler_cli` session and dispatches those features. It does not implement a phase of its own.

## Ubiquitous Language

- **Phase** — a feature pipeline in `compiler/assets/feature.yml`. Phases are component-agnostic.
- **Command** — a CLI feature id `group_key.key` declared in `compiler/assets/cli.yml`. The five ids are `scan.module`, `parse.module`, `semantic.module`, `compile.module`, and `compile.ast`.
- **Component type** — the requested Tiferet module kind, passed as request data via `-c` / `--component`. It is not a command name.
- **Step** — one feature step. Its `service_id` names the event that owns the work. The class is the registration in `compiler/assets/config.yml`, not a guess from the step name.
- **Anchor** — a YAML alias defined at first use (`&tokenize_step` and the rest). Later phases reuse the step. They do not redeclare it.
- **Catalogue** — the token, grammar, and production rules listed by `tiferet-ly` repositories. This package does not host those rules.
- **Finding** — a conformance dict accumulated under the `findings` data key. Which dialect runs is a separate decision. See [dialects.md](dialects.md).

## Phases Stay Component-Agnostic

`compiler/assets/feature.yml` and `compiler/assets/cli.yml` open with the same decision: phases are component-agnostic, and the component type arrives as request data.

Do not add `scan.event`, `compile.event`, or any other component-named command. Those event commands are retired. The locked command list is in [schema.md](schema.md).

Scan and parse do not declare `-c` / `--component`. `semantic.module`, `compile.module`, and `compile.ast` require it. The choices, in the order `cli.yml` declares them, are `assets`, `blueprints`, `contexts`, `di`, `domain`, `events`, `interfaces`, `mappers`, `repos`, and `utils`.

Two sessions exist in `compiler/assets/config.yml`. `compiler` is the compiler session. `compiler_cli` is the CLI session. `compiler.cli:main` boots `compiler_cli`, and that session is the one that adds `cli_config`.

## The Five Commands

Each command is one feature. Shared steps are anchors, not copies.

- **`scan.module`** tokenizes a source file. It does not take a component type. Steps: Tokenize, Emit Scan Result.
- **`parse.module`** parses a source file. It does not take a component type. Steps: Tokenize, Parse, Emit Parse Result.
- **`semantic.module`** analyzes a source file. Dialect checks are gated on the requested component type. Steps: Tokenize, Parse, Build Symbols, Check Common Conformance, the ten gated dialect checks, Emit Semantic Result.
- **`compile.module`** compiles a source file. It runs the semantic prefix, then Generate Code, Optimize Code, and Emit Codegen Result. It does not emit a semantic result.
- **`compile.ast`** compiles a saved JSON AST. It does not tokenize or parse. Steps: Load From AST, then Build Symbols through Emit Codegen Result. Its `source_file` argument is the JSON AST path, not a Python source path.

`compile.module` and `compile.ast` take `-O`. The CLI description is the decision: `O0` leaves codegen unchanged, and `O1` shares repeated structures. That flag is request data for `OptimizeCode`. It does not select a dialect.

`scan.module` declares `--summary-only`. `EmitScanResult` does not read it, and the scan payload does not carry a summary flag. A declared flag is not phase behavior until an event consumes it.

## Which Event Owns Which Step

The owner is the class registered for the step's `service_id` in `compiler/assets/config.yml`.

| Step | `service_id` | Class |
|---|---|---|
| Tokenize | `perform_lexical_analysis_event` | `PerformLexicalAnalysis` (`compiler.events.lexer`) |
| Emit Scan Result | `emit_scan_result_event` | `EmitScanResult` (`compiler.events.lexer`) |
| Parse | `perform_syntactic_analysis_event` | `PerformSyntacticAnalysis` (`compiler.events.parser`) |
| Emit Parse Result | `emit_parse_result_event` | `EmitParseResult` (`compiler.events.parser`) |
| Build Symbols | `perform_semantic_analysis_event` | `PerformSemanticAnalysis` (`compiler.events.semantic`) |
| Check Common Conformance | `check_common_conformance_event` | `CheckCommonConformance` (`compiler.events.typecheck`) |
| Check Event Conformance | `check_event_conformance_event` | `CheckEventConformance` (`compiler.events.typecheck`) |
| Check Asset Conformance | `check_asset_conformance_event` | `CheckAssetConformance` (`compiler.events.typecheck`) |
| Check Domain Conformance | `check_domain_conformance_event` | `CheckDomainConformance` (`compiler.events.typecheck`) |
| Check Mapper Conformance | `check_mapper_conformance_event` | `CheckMapperConformance` (`compiler.events.typecheck`) |
| Check Interface Conformance | `check_interface_conformance_event` | `CheckInterfaceConformance` (`compiler.events.typecheck`) |
| Check DI Conformance | `check_di_conformance_event` | `CheckDIConformance` (`compiler.events.typecheck`) |
| Check Utils Conformance | `check_utils_conformance_event` | `CheckUtilsConformance` (`compiler.events.typecheck`) |
| Check Context Conformance | `check_context_conformance_event` | `CheckContextsConformance` (`compiler.events.typecheck`) |
| Check Blueprints Conformance | `check_blueprints_conformance_event` | `CheckBlueprintsConformance` (`compiler.events.typecheck`) |
| Check Repos Conformance | `check_repos_conformance_event` | `CheckReposConformance` (`compiler.events.typecheck`) |
| Emit Semantic Result | `emit_semantic_result_event` | `EmitSemanticResult` (`compiler.events.semantic`) |
| Generate Code | `generate_code_event` | `GenerateCode` (`compiler.events.codegen`) |
| Optimize Code | `optimize_code_event` | `OptimizeCode` (`compiler.events.codegen`) |
| Emit Codegen Result | `emit_codegen_result_event` | `EmitCodegenResult` (`compiler.events.codegen`) |
| Load From AST | `load_from_ast_event` | `LoadFromAST` (`compiler.events.codegen`) |

The context row is the naming exception. The step and `service_id` say `context`. The class is `CheckContextsConformance`. Do not treat that as a typo. Gating and rule-set binding are in [dialects.md](dialects.md).

Data keys, where the feature declares one: Tokenize writes `tokens`. Parse and Load From AST write `ast`. Build Symbols writes `semantic`. Every conformance step writes `findings`. Generate Code and Optimize Code write `codegen`. Emit steps declare no `data_key`. They record the result.

`GenerateCode` is the step that reads `component`. It passes that string to the generator as `kind`. A missing `component` on a direct call defaults to `events`. The CLI still requires the flag on semantic and both compile commands, so that default is not a command default. Conformance events do not read `component`. `OptimizeCode` reads `O`, not `component`. A missing or empty `O` is `O0`.

`LoadFromAST` accepts a parse-result payload or a bare AST dict. It maps the transfer object. It does not parse source.

## Shared Steps Are Anchored Once

`feature.yml` anchors a step at first use and aliases it after that. Tokenize is anchored on scan and reused by parse, semantic, and `compile.module`. Parse is anchored on parse and reused by semantic and `compile.module`. Build Symbols, the conformance steps, and the three codegen steps are anchored on semantic or `compile.module` and reused by `compile.ast`.

`compile.ast` does not alias Tokenize or Parse. Editing `&tokenize_step` changes every phase that aliases it, including scan. Editing a dialect step changes semantic, `compile.module`, and `compile.ast` together.

CLI arguments follow the same rule. `&component_arg` is defined once, required, and aliased onto semantic and both compile commands. Do not give those commands different choice lists.

## The tiferet-ly Boundary

`tiferet-ly` owns the catalogues and the recognition engine. This package adapts them. It does not host token rules, grammar YAML, productions, or indent tracking.

`compiler/assets/config.yml` registers the three catalogue services on `tiferet-ly` repositories, not on compiler classes:

- `token_service` → `tiferet_ly.repos.token.TokenConfigRepository`
- `grammar_service` → `tiferet_ly.repos.grammar.GrammarConfigRepository`
- `production_service` → `tiferet_ly.repos.production.ProductionConfigRepository`

The lexer and parser adapters are local:

- `lexer_service` → `compiler.utils.lexer.TiferetLexer`
- `parser_service` → `compiler.utils.parser.TiferetParser`

`PerformLexicalAnalysis` reads the source file and lists the injected catalogues. It does not open `tokens.yml` or `grammars.yml`, and it does not own token rules, grammar YAML, or indent layout. `TiferetLexer` adapts a caller-supplied catalogue into token aggregates without hosting rules. Indent tracking stays in `tiferet-ly`.

`PerformSyntacticAnalysis` lists the injected catalogues and delegates recognition to the parser. It does not open grammar, token, or production YAML, and it does not type-check the result. `TiferetParser` adapts a recognized token stream into a module AST without hosting productions. It hosts no `p_*` productions. `PlyParser` in `compiler/utils/parser.py` extends the published `tiferet-ly` parser with dialect node mutations.

Semantic analysis, conformance, and codegen do not cross that boundary. `PerformSemanticAnalysis` builds a symbol table and resolves names. It does not own scope construction, and it does not print findings. `GenerateCode` delegates to `compiler.utils.codegen.TiferetGenerator`. It does not walk the AST. `OptimizeCode` delegates to `compiler.utils.optimizer.YamlAnchorOptimizer` at `O1` and above, and returns the dict unchanged at `O0`. `LoadFromAST` loads JSON through `tiferet.utils.Json`.

The catalogue paths in `config.yml` `const` — `token_config`, `grammar_config`, `production_config` — point at packaged YAML under `compiler/assets/`. The events do not open those files. The repositories do.

## When a Phase Changes

Change the feature step, the event that owns it, and the service registration together. A shared anchor is one edit, not one edit per phase.

A new public command, or a new component choice, is a freeze decision. See [schema.md](schema.md). A new dialect check is a rulebook plus a `feature.yml` condition, not a branch inside `execute`. See [dialects.md](dialects.md).

Do not put phase logic in `compiler/cli.py`. That module rewrites packaged asset paths and boots `compiler_cli`.

## Boundaries

**Inside this domain:** phase order, which command takes a component type, which event owns which step, and the seam where recognition leaves this package for `tiferet-ly`.

**Outside this domain:** the ten rulebooks and the `feature.yml` gates ([dialects.md](dialects.md)); the names the schema test locks ([schema.md](schema.md)); token, grammar, and production rule bodies (`tiferet-ly`); Tiferet feature execution, which this package configures and does not implement. This package has no `contexts`, `blueprints`, `di`, or `repos` of its own. Those names are target dialects, not local packages.

The draft vision and distillation are not the source for this guide. Code wins.

## Related Documentation

- [dialects.md](dialects.md) — one reader, ten rulebooks, and why `execute` does not read `component`
- [schema.md](schema.md) — the frozen command, choice, session, and envelope names
- [docs/core/code_style.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/code_style.md) — artifact comments and formatting; style law stays on the Tiferet skills
- [`.agents/skills/elsl-pipeline`](../../.agents/skills/elsl-pipeline/SKILL.md) — procedure for changing a phase, a feature step, a CLI command, or a pipeline event
