"""Validation schemas for optimization policies."""

import uuid
from datetime import datetime
from typing import List, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, field_serializer, field_validator, model_validator

from edge_mining.adapters.infrastructure.rule_engine.common import OperatorType
from edge_mining.domain.common import EntityId
from edge_mining.domain.policy.aggregate_roots import OptimizationPolicy
from edge_mining.domain.policy.entities import AutomationRule
from edge_mining.domain.policy.exceptions import PolicyError


class RuleConditionSchema(BaseModel):
    """Single condition within a rule."""

    field: str = Field(..., description="Field path in DecisionalContext (dot notation)")
    operator: OperatorType = Field(..., description="Comparison operator")
    value: Union[int, float, str, bool, List[Union[int, float, str]]] = Field(
        ..., description="Value to compare against"
    )

    @field_validator("field")
    @classmethod
    def validate_field_path(cls, v):
        """Validate that field path is not empty and contains valid characters."""
        if not v or not isinstance(v, str):
            raise ValueError("Field path must be a non-empty string")

        # Basic validation - could be enhanced with actual field path checking
        allowed_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._")
        if not all(c in allowed_chars for c in v):
            raise ValueError("Field path contains invalid characters")

        return v

    @field_validator("operator", mode="before")
    @classmethod
    def validate_operator(cls, v: Union[str, OperatorType]) -> OperatorType:
        """Validate operator type."""
        if isinstance(v, str):
            try:
                return OperatorType(v.lower())
            except KeyError as e:
                raise ValueError(f"Invalid operator: {v}. Must be one of {list(OperatorType)}") from e
        elif isinstance(v, OperatorType):
            return v
        else:
            raise ValueError("Operator must be a string or an OperatorType enum value")

    @field_serializer("operator")
    def serialize_operator(self, operator: OperatorType) -> str:
        """Serialize operator as string value."""
        return operator.value

    def to_model(self) -> dict:
        """Convert schema to dict for domain model."""
        return self.model_dump()


class LogicalGroupSchema(BaseModel):
    """Logical grouping of conditions (AND/OR)."""

    all_of: Optional[List[Union[RuleConditionSchema, "LogicalGroupSchema"]]] = Field(
        None, description="All conditions must be true (AND logic)"
    )
    any_of: Optional[List[Union[RuleConditionSchema, "LogicalGroupSchema"]]] = Field(
        None, description="At least one condition must be true (OR logic)"
    )
    not_: Optional[Union[RuleConditionSchema, "LogicalGroupSchema"]] = Field(
        None, description="Negation of the condition/group"
    )

    @field_validator("all_of", "any_of")
    @classmethod
    def validate_logical_groups(cls, v: Optional[List]):
        """Ensure at least one logical operator is specified."""
        if v is None:
            return v
        if not isinstance(v, List) or len(v) == 0:
            raise ValueError("Logical group must be a non-empty list")
        return v

    def to_model(self) -> dict:
        """Convert schema to dict for domain model."""
        return self.model_dump(exclude_none=True, exclude_unset=True)


class AutomationRuleSchema(BaseModel):
    """Schema for a single automation rule."""

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique identifier for the rule (auto-generated if not provided)",
    )
    name: str = Field(..., description="Unique name for the rule")
    description: Optional[str] = Field(None, description="Human-readable description")
    conditions: Union[LogicalGroupSchema, RuleConditionSchema] = Field(
        ..., description="Conditions that must be met for the rule to trigger"
    )
    priority: int = Field(
        default=0,
        description="Rule priority (higher numbers = higher priority)",
    )
    enabled: bool = Field(default=True, description="Whether the rule is active")

    @field_validator("id")
    @classmethod
    def validate_id(cls, v: str) -> str:
        """Validate rule ID."""
        if not v or not isinstance(v, str) or len(v.strip()) == 0:
            return str(uuid.uuid4())
        return v.strip()

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate rule name."""
        if not v or not isinstance(v, str) or len(v.strip()) == 0:
            raise ValueError("Rule name must be a non-empty string")
        return v.strip()

    @field_validator("conditions")
    def validate_conditions(
        cls, v: Union[LogicalGroupSchema, RuleConditionSchema]
    ) -> Union[LogicalGroupSchema, RuleConditionSchema]:
        """Ensure exactly one logical operator is specified."""
        if isinstance(v, LogicalGroupSchema):
            operators = [v.all_of, v.any_of, v.not_]
            non_none_count = sum(1 for op in operators if op is not None)
            if non_none_count != 1:
                raise ValueError("Exactly one logical operator (all_of, any_of, not_) must be specified")
        return v

    @field_serializer("id")
    def serialize_id(self, rule_id: str) -> str:
        """Serialize rule ID as string."""
        return str(rule_id)

    @field_serializer("conditions")
    def serialize_conditions(self, conditions: Union[LogicalGroupSchema, RuleConditionSchema]) -> dict:
        """Serialize conditions."""
        if isinstance(conditions, LogicalGroupSchema):
            return conditions.model_dump(exclude_none=True, exclude_unset=True)
        else:
            return conditions.model_dump()

    def to_model(self) -> AutomationRule:
        """Convert schema to AutomationRule domain entity."""
        # Convert conditions to dict for domain model
        conditions_dict = {}
        if isinstance(self.conditions, (LogicalGroupSchema, RuleConditionSchema)):
            conditions_dict = self.conditions.to_model()

        return AutomationRule(
            id=EntityId(uuid.UUID(self.id)),
            name=self.name,
            description=self.description or "",
            priority=self.priority,
            enabled=self.enabled,
            conditions=conditions_dict,
        )

    @classmethod
    def from_model(cls, rule: AutomationRule) -> "AutomationRuleSchema":
        """Convert domain model to schema."""
        return cls(
            id=str(rule.id),
            name=rule.name,
            description=rule.description,
            conditions=convert_conditions_to_schema(rule.conditions),
            priority=rule.priority,
            enabled=rule.enabled,
        )

    model_config = ConfigDict(from_attributes=True)


class MetadataSchema(BaseModel):
    """Schema for optional metadata."""

    author: Optional[str] = Field(None, description="Author of the policy")
    version: Optional[int] = Field(None, description="Version of the policy schema")
    created: Optional[str] = Field(None, description="Creation date")
    last_modified: Optional[str] = Field(None, description="Last modified date")


class OptimizationPolicySchema(BaseModel):
    """Schema for an optimization policy."""

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique identifier for the policy (auto-generated if not provided)",
    )
    name: str = Field(..., description="Policy name")
    description: Optional[str] = Field(None, description="Policy description")

    # Rules embedded directly in the policy file
    start_rules: List[AutomationRuleSchema] = Field(default_factory=list, description="Rules for starting mining")
    stop_rules: List[AutomationRuleSchema] = Field(default_factory=list, description="Rules for stopping mining")

    # Metadata
    metadata: Optional[MetadataSchema] = Field(
        default_factory=lambda: MetadataSchema(
            author="Edge Mining User",
            version=1,
            created=datetime.now().strftime("%Y-%m-%d"),
            last_modified=datetime.now().strftime("%Y-%m-%d"),
        )
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate policy name."""
        if not v or not isinstance(v, str) or len(v.strip()) == 0:
            raise ValueError("Policy name must be a non-empty string")
        return v.strip()

    @field_validator("id")
    @classmethod
    def validate_id(cls, v: str) -> str:
        """Validate policy ID."""
        if not v or not isinstance(v, str) or len(v.strip()) == 0:
            return str(uuid.uuid4())
        return v.strip()

    @field_serializer("id")
    def serialize_id(self, policy_id: str) -> str:
        """Serialize policy ID as string."""
        return str(policy_id)

    @field_validator("start_rules", "stop_rules")
    @classmethod
    def validate_rule_ids_unique(cls, v: List[AutomationRuleSchema]) -> List[AutomationRuleSchema]:
        """Ensure rule ids are unique within each rule type."""
        if not v:
            return v
        ids = [rule.id for rule in v]
        if len(ids) != len(set(ids)):
            duplicates = [id for id in ids if ids.count(id) > 1]
            raise ValueError(f"Duplicate rule id found: {duplicates}")
        return v

    @model_validator(mode="after")
    def validate_overall_rule_ids(self) -> "OptimizationPolicySchema":
        """Ensure rule ids are unique across all rules in the policy."""
        all_rule_ids = []
        all_rule_ids.extend([rule.id for rule in self.start_rules])
        all_rule_ids.extend([rule.id for rule in self.stop_rules])

        if len(all_rule_ids) != len(set(all_rule_ids)):
            duplicates = [id for id in all_rule_ids if all_rule_ids.count(id) > 1]
            raise ValueError(f"Duplicate rule ids found across start and stop rules: {duplicates}")

        return self

    def to_model(self) -> OptimizationPolicy:
        """Convert schema to OptimizationPolicy domain aggregate root."""
        return OptimizationPolicy(
            id=EntityId(uuid.UUID(self.id)),
            name=self.name,
            description=self.description,
            start_rules=[rule.to_model() for rule in self.start_rules],
            stop_rules=[rule.to_model() for rule in self.stop_rules],
        )

    @classmethod
    def from_model(
        cls, policy: OptimizationPolicy, metadata: Optional[MetadataSchema] = None
    ) -> "OptimizationPolicySchema":
        """Create schema from OptimizationPolicy domain aggregate root."""
        start_rules: List[AutomationRuleSchema] = [AutomationRuleSchema.from_model(rule) for rule in policy.start_rules]
        stop_rules: List[AutomationRuleSchema] = [AutomationRuleSchema.from_model(rule) for rule in policy.stop_rules]

        return cls(
            id=str(policy.id),
            name=policy.name,
            description=policy.description,
            start_rules=start_rules,
            stop_rules=stop_rules,
            metadata=metadata
            or MetadataSchema(
                author="Edge Mining User",
                version=1,
                created=datetime.now().strftime("%Y-%m-%d"),
                last_modified=datetime.now().strftime("%Y-%m-%d"),
            ),
        )

    model_config = ConfigDict(from_attributes=True)


class OptimizationPolicyCreateSchema(BaseModel):
    """Schema for creating a new optimization policy."""

    name: str = Field(..., description="Policy name")
    description: Optional[str] = Field(None, description="Policy description")
    start_rules: List[AutomationRuleSchema] = Field(default_factory=list, description="Rules for starting mining")
    stop_rules: List[AutomationRuleSchema] = Field(default_factory=list, description="Rules for stopping mining")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate policy name."""
        if not v or not isinstance(v, str) or len(v.strip()) == 0:
            raise ValueError("Policy name must be a non-empty string")
        return v.strip()

    def to_model(self) -> OptimizationPolicy:
        """Convert schema to OptimizationPolicy domain aggregate root."""
        return OptimizationPolicy(
            id=EntityId(uuid.uuid4()),
            name=self.name,
            description=self.description,
            start_rules=[rule.to_model() for rule in self.start_rules],
            stop_rules=[rule.to_model() for rule in self.stop_rules],
        )


class OptimizationPolicyUpdateSchema(BaseModel):
    """Schema for updating an existing optimization policy."""

    name: Optional[str] = Field(None, description="Policy name")
    description: Optional[str] = Field(None, description="Policy description")
    start_rules: Optional[List[AutomationRuleSchema]] = Field(None, description="Rules for starting mining")
    stop_rules: Optional[List[AutomationRuleSchema]] = Field(None, description="Rules for stopping mining")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        """Validate policy name."""
        if v is not None:
            if not isinstance(v, str) or len(v.strip()) == 0:
                raise ValueError("Policy name must be a non-empty string")
            return v.strip()
        return v


class AutomationRuleCreateSchema(BaseModel):
    """Schema for creating a new automation rule."""

    name: str = Field(..., description="Unique name for the rule")
    description: Optional[str] = Field(None, description="Human-readable description")
    conditions: Union[LogicalGroupSchema, RuleConditionSchema] = Field(
        ..., description="Conditions that must be met for the rule to trigger"
    )
    priority: int = Field(
        default=0,
        description="Rule priority (higher numbers = higher priority)",
    )
    enabled: bool = Field(default=True, description="Whether the rule is active")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate rule name."""
        if not v or not isinstance(v, str) or len(v.strip()) == 0:
            raise ValueError("Rule name must be a non-empty string")
        return v.strip()

    def to_model(self) -> AutomationRule:
        """Convert create schema to AutomationRule domain entity."""
        # Convert conditions to dict for domain model
        conditions_dict = {}
        if isinstance(self.conditions, (LogicalGroupSchema, RuleConditionSchema)):
            conditions_dict = self.conditions.to_model()

        return AutomationRule(
            id=EntityId(uuid.uuid4()),  # Generate new ID for create
            name=self.name,
            description=self.description or "",
            priority=self.priority,
            enabled=self.enabled,
            conditions=conditions_dict,
        )


class AutomationRuleUpdateSchema(BaseModel):
    """Schema for updating an existing automation rule."""

    name: Optional[str] = Field(None, description="Unique name for the rule")
    description: Optional[str] = Field(None, description="Human-readable description")
    conditions: Optional[Union[LogicalGroupSchema, RuleConditionSchema]] = Field(
        None, description="Conditions that must be met for the rule to trigger"
    )
    priority: Optional[int] = Field(
        None,
        description="Rule priority (higher numbers = higher priority)",
    )
    enabled: Optional[bool] = Field(None, description="Whether the rule is active")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        """Validate rule name."""
        if v is not None:
            if not isinstance(v, str) or len(v.strip()) == 0:
                raise ValueError("Rule name must be a non-empty string")
            return v.strip()
        return v


# Helper methods for converting from domain models to schemas
def convert_conditions_to_schema(conditions: dict) -> Union[LogicalGroupSchema, RuleConditionSchema]:
    """Recursively convert conditions dict to appropriate schema."""
    # Check if conditions are a logical group or a single rule condition
    if isinstance(conditions, dict):
        conditions_dict_keys = set(conditions.keys())
        logical_group_keys = set(LogicalGroupSchema.model_fields.keys())
        rule_condition_keys = set(RuleConditionSchema.model_fields.keys())

        # Check if any key from conditions matches LogicalGroupSchema keys
        if conditions_dict_keys.intersection(logical_group_keys):
            # It's a logical group - create instance with only the matching fields
            logical_group_data = {k: v for k, v in conditions.items() if k in logical_group_keys and v is not None}
            return LogicalGroupSchema(**logical_group_data)
        elif conditions_dict_keys.intersection(rule_condition_keys):
            # It's a single rule condition - create instance with only the matching fields
            rule_condition_data = {k: v for k, v in conditions.items() if k in rule_condition_keys}
            return RuleConditionSchema(**rule_condition_data)
        else:
            # It's an unknown format, raise an error
            raise PolicyError(f"Invalid conditions format: {conditions}")
    else:
        # If conditions is not a dict, raise an error
        raise PolicyError(f"Expected conditions to be a dict, got {type(conditions)}")


# Update forward references
LogicalGroupSchema.model_rebuild()
