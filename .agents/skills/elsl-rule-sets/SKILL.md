---
name: elsl-rule-sets
description: >
  Use when adding or changing a specification on a compiler rule set. Phrases:
  "add a dialect rule", "rule set", "COMMON_RULE_SET", "specification id",
  "permitted group". Not for the feature.yml gate or the conformance event class.
---

# Change a rule-set constant

## When to use
- Adding, removing, or reordering a specification on a `*_RULE_SET` constant.
- Changing the arguments a listed specification is constructed with.

## When not to use
- The event class or the `feature.yml` condition — `elsl-conformance`.
- Pipeline wiring — `elsl-pipeline`.
- A frozen command, choice, or envelope name — `elsl-schema`.
- Code style, TRDs, RFPs, or reports — the Tiferet skills. Do not vendor them.

## Canonical source
- `compiler/utils/typecheck.py`
- `compiler/utils/core.py`
- The lists below are the operator copy of the constants. If the module and this skill disagree, the module on the branch wins, and this skill is updated in the same change.

## Inputs
- The rule set and the specification id being changed.
- `docs/collab/binding.md`. A GitHub issue. **Trunk** also needs a published TRD and a freeze id. **Prototype** needs a published RFP, and only if that strand is active.

## Catalog

A later dialect adds a constant list, not a `ConformanceChecker` subclass. New specification classes go in `compiler/utils/core.py`.

`COMMON_RULE_SET` is ungated:

- `ImportGroupSpecification` `common.import_group` `artifact_header`
- `SectionClassNameSpecification` `common.section_class_name` `artifact_header`
- `FunctionSectionNameSpecification` `common.function_section_name` `artifact_header`
- `AttributeMemberSpecification` `common.attribute_member` `member`
- `MethodMemberSpecification` `common.method_member` `member`
- `AssignmentTypeSpecification` `common.assignment_type` `expression`
- `BinaryOpTypeSpecification` `common.binary_op_expression` `expression`
- `ReturnBinaryOpTypeSpecification` `common.binary_op_return` `return`

`EVENT_RULE_SET`: `EventSectionSpecification` `event.section` `artifact_header`.

`DOMAIN_RULE_SET`:

- `PermittedGroupSpecification` `domain.permitted_group` — `imports`, `constants`, `functions`, `classes`, `models`, `exports`. Error `DISALLOWED_DOMAIN_GROUP`.
- `AppImportSpecification` `domain.app_import` — allowed `assets`. Error `INVALID_DOMAIN_APP_IMPORT`.
- `GroupSectionAgreementSpecification` `domain.group_section_agreement`
- `RequiredBaseSpecification` `domain.model_base_class` — section keyword `model`, error `MODEL_MISSING_DOMAIN_OBJECT_BASE`, must extend `DomainObject`.
- `DomainAttributeSpecification` `domain.attribute` `member`

`DI_RULE_SET`:

- `PermittedGroupSpecification` `di.permitted_group` — `imports`, `constants`, `functions`, `classes`, `exports`. Error `DISALLOWED_DI_GROUP`.
- `AppImportSpecification` `di.app_import` — allowed `domain`, `interfaces`. Error `INVALID_DI_APP_IMPORT`.
- `DIAbstractMethodSpecification` `di.abstract_method`

`INTERFACE_RULE_SET`:

- `PermittedGroupSpecification` `interface.permitted_group` — `imports`, `classes`, `interfaces`, `exports`. Error `DISALLOWED_INTERFACE_GROUP`.
- `AppImportSpecification` `interface.app_import` — allowed `mappers`. Error `INVALID_INTERFACE_APP_IMPORT`.
- `InterfaceAbstractMethodSpecification` `interface.abstract_method`

`MAPPER_RULE_SET`:

- `PermittedGroupSpecification` `mapper.permitted_group` — `imports`, `constants`, `mappers`, `exports`. Error `DISALLOWED_MAPPER_GROUP`.
- `AppImportSpecification` `mapper.app_import` — allowed `domain`, `events`. Error `INVALID_MAPPER_APP_IMPORT`.
- `GroupSectionAgreementSpecification` `mapper.group_section_agreement`
- `MapperRolesAttributeSpecification` `mapper.roles_attribute` `member`

`UTILS_RULE_SET`:

- `PermittedGroupSpecification` `utils.permitted_group` — `imports`, `constants`, `utils`, `exports`. Error `DISALLOWED_UTILS_GROUP`.
- `AppImportSpecification` `utils.app_import` — allowed `interfaces`, `mappers`. Error `INVALID_UTILS_APP_IMPORT`.
- `ContextManagerPairingSpecification` `utils.context_manager_pairing`

`REPOS_RULE_SET`:

- `PermittedGroupSpecification` `repos.permitted_group` — `imports`, `repos`, `exports`. Error `DISALLOWED_REPOS_GROUP`.
- `AppImportSpecification` `repos.app_import` — allowed `interfaces`, `mappers`, `utils`. Error `INVALID_REPOS_APP_IMPORT`.
- `RequiredBaseSpecification` `repos.base_class` — section keyword `repo`, error `REPO_MISSING_BASE`.
- `ReposCrudMethodSpecification` `repos.crud_method`

`ASSET_RULE_SET`:

- `PermittedGroupSpecification` `asset.permitted_group` — `imports`, `constants`, `functions`, `classes`, `exports`. Error `DISALLOWED_ASSET_GROUP`.
- `AppImportSpecification` `asset.import_sibling` — `allowed_components` empty, `allow_siblings=True`, `allow_framework_root_alias=False`. Error `INVALID_ASSET_APP_IMPORT`.
- `GroupSectionAgreementSpecification` `asset.group_section_agreement`
- `ConstantSectionNameSpecification` `asset.constant_section_name`

`CONTEXTS_RULE_SET`:

- `PermittedGroupSpecification` `contexts.permitted_group` — `imports`, `contexts`, `exports`, `classes`, `constants`, `functions`. Error `DISALLOWED_CONTEXTS_GROUP`.
- `AppImportSpecification` `contexts.app_import` — allowed `assets`, `domain`, `events`. Siblings and the framework-root alias are allowed. Error `INVALID_CONTEXTS_APP_IMPORT`.
- `RequiredBaseSpecification` `contexts.base_class` — section keyword `context`, required base `BaseContext`, predicate `declares_bound_domain_type`. Error `CONTEXT_MISSING_BASE_CONTEXT`.

`BLUEPRINTS_RULE_SET`:

- `PermittedGroupSpecification` `blueprints.permitted_group` — `imports`, `constants`, `functions`, `blueprints`, `exports`. Error `DISALLOWED_BLUEPRINTS_GROUP`.
- `AppImportSpecification` `blueprints.app_import` — allowed `assets`, `contexts`, `di`, `events`. Siblings and the framework-root alias are allowed. Error `INVALID_BLUEPRINTS_APP_IMPORT`.
- `GroupSectionAgreementSpecification` `blueprints.group_section_agreement`

Unless a row says otherwise, `applies_to` is `artifact_header`.

## Relation to ElohaSL

A specification judges a source construct. It does not emit a group. The constructs line up with the envelope as follows:

- `ImportGroupSpecification` and `AppImportSpecification` judge the import group that becomes `impt` rows `{src, tgts}`.
- `SectionClassNameSpecification` and `FunctionSectionNameSpecification` judge the header whose PascalCase or snake_case name becomes a class, function, or event key.
- `AttributeMemberSpecification` and `MethodMemberSpecification` judge the members that become `attributes` and `methods`.
- `AssignmentTypeSpecification` and the binary-op specifications judge the operations that `encode` later writes into `stmt`, such as `Add` and `Assign`.
- A dialect `PermittedGroupSpecification` judges which `# ***` groups that component may contain. Those names are the generator's group hooks, plus `events` for an unknown name. `exports` is a legal source group and is skipped at emission.

Do not add an envelope key to make a rule pass. Change the source, or change the specification. The emission catalog is `elsl-language`.

## Procedure
1. Edit the constant in `compiler/utils/typecheck.py`. Do not copy the list into the event.
2. If the specification class does not exist, add it in `compiler/utils/core.py`. A specification records findings. It does not mutate the candidate.
3. If the constant is new, bind it with `elsl-conformance`. Do not add the gate in this skill's change unless that skill's procedure is the one you are following.
4. **Trunk** — implement against the published TRD. Do not copy from proto.
5. **Prototype** — only if binding.md says the prototype strand is active.

## Outputs
- The constant change, and any new specification class, on the strand branch, in a PR to that strand. Not an issue body.

## Guardrails
- Never commit or merge unless asked.
- Never proto → trunk git.
- Never implement trunk reconstruction from a live proto branch.
- Never author a reconstruction TRD without a freeze id.
- Read `docs/collab/binding.md` in this repo for owner/repo, proto branch, and project ids.
- Do not vendor Tiferet skills into this repo.
- Do not subclass `ConformanceChecker` to add a dialect.
- Do not treat a guide as the source for this catalog.
