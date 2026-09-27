"""Tiferet Compiler Artifact Domain Objects"""

# *** imports

# ** core
from typing import Any, List, Optional

# ** infra
from pydantic import Field, model_validator

# ** app
from .ast import Declaration, Statement

# *** models

# ** model: artifact_declaration
class ArtifactDeclaration(Declaration):
    '''
    A declaration with typed artifact tier, member role, and qualifier.

    Keyword legality per component type is a rulebook concern, not a domain invariant.
    '''

    # * attribute: artifact_type
    artifact_type: Optional[str] = Field(
        None,
        description="Tier marker: '***', '** event', 'ARTIFACT_MEMBER', etc.",
    )

    # * attribute: artifact_role
    artifact_role: Optional[str] = Field(
        None,
        description="Member role: 'attribute', 'init', 'method'.",
    )

    # * attribute: artifact_qualifier
    artifact_qualifier: Optional[str] = Field(
        None,
        description='Parenthetical qualifier (ids in constants (ids)); None if unqualified.',
    )

    # * attribute: annotations
    annotations: Optional[List[dict]] = Field(
        None,
        description='Structured SEE / OBSOLETE / TODO notes.',
    )

    # * attribute: guide_path
    guide_path: Optional[str] = Field(
        None,
        description='# >> see: target.',
    )

    # * attribute: is_artifact_member
    is_artifact_member: bool = Field(
        False,
        description="Derived: artifact_type == 'ARTIFACT_MEMBER'.",
    )

    # * attribute: section_keyword
    section_keyword: Optional[str] = Field(
        None,
        description="Derived keyword after the marker (event from ** event); None for bare *** / **.",
    )

    # * attribute: is_section
    is_section: bool = Field(
        False,
        description='Derived: section_keyword is not None.',
    )

    # * method: _derive_classification (model validator)
    @model_validator(mode='before')
    @classmethod
    def _derive_classification(cls, data: Any) -> Any:
        '''
        Derive artifact flags in addition to declaration classification.

        :param data: The raw input being validated.
        :type data: Any
        :return: The input, with artifact flags set when it is a mapping.
        :rtype: Any
        '''

        # Keep declaration classification even when this method overrides the parent validator.
        data = Declaration._derive_classification(data)

        # Leave non-mapping input for Pydantic to handle.
        if not isinstance(data, dict):
            return data

        # Copy before deriving artifact flags.
        data = dict(data)
        artifact_type = data.get('artifact_type') or ''
        parts = artifact_type.split(None, 1)
        keyword = parts[1].strip() if len(parts) > 1 and parts[1].strip() else None
        data['is_artifact_member'] = artifact_type == 'ARTIFACT_MEMBER'
        data['section_keyword'] = keyword
        data['is_section'] = keyword is not None

        # Return the canonicalized raw input.
        return data

    # * method: _rederive_classification (model validator)
    @model_validator(mode='after')
    def _rederive_classification(self) -> 'ArtifactDeclaration':
        '''
        Rederive artifact flags after validation, including assignment.

        ``mode='before'`` does not run when a field is assigned, so this
        validator keeps artifact flags aligned with ``artifact_type`` and
        declaration flags aligned with ``type``.

        :return: The declaration with classification flags rederived.
        :rtype: ArtifactDeclaration
        '''

        # Keep declaration flags aligned when this method overrides the parent validator.
        Declaration._rederive_classification(self)

        # Rederive artifact flags without re-entering assignment validation.
        artifact_type = self.artifact_type or ''
        parts = artifact_type.split(None, 1)
        keyword = parts[1].strip() if len(parts) > 1 and parts[1].strip() else None
        object.__setattr__(self, 'is_artifact_member', artifact_type == 'ARTIFACT_MEMBER')
        object.__setattr__(self, 'section_keyword', keyword)
        object.__setattr__(self, 'is_section', keyword is not None)

        # Return the classified artifact declaration.
        return self

# ** model: artifact_statement
class ArtifactStatement(Statement):
    '''
    Typed marker for group or section wrapper nodes.

    Prefer isinstance checks against this class rather than only StatementKind.ARTIFACT.
    '''

    # The marker carries no fields of its own.
    pass

# ** model: snippet_statement
class SnippetStatement(Statement):
    '''
    A snippet with leading comments kept separate from executable code.

    Comments stay on their own list so body remains the executable statements.
    '''

    # * attribute: comments
    comments: List[Statement] = Field(
        default_factory=list,
        description='Leading comment statements; executable code stays on body.',
    )
