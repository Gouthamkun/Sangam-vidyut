from pydantic import BaseModel, Field, model_validator
from typing import Literal

class SimulationConfig(BaseModel):
    n_agents: int = Field(default=500, description="Total number of households (N).", ge=1)
    timesteps: int = Field(default=12, description="Number of simulation steps (quarters).", ge=1)
    timestep_duration_months: int = Field(default=3, description="Months per timestep.", ge=1)
    seed: int = Field(default=42, description="Random seed for reproducibility.")
    baseline_provider: Literal["legacy", "empirical"] = Field(default="legacy", description="Source of the base probability (p_base)")

class SIRConfig(BaseModel):
    recovery_duration_quarters: int = Field(default=2, description="Duration in quarters an adopter actively influences others.", ge=0)
    beta: float = Field(default=0.1, description="Probability of infection (adoption) per contact.", ge=0.0, le=1.0)

class NetworkConfig(BaseModel):
    topology: Literal["watts_strogatz", "barabasi_albert"] = Field(default="watts_strogatz")
    ws_k: int = Field(default=4, description="Each node is connected to k nearest neighbors in ring topology.", ge=2)
    ws_p: float = Field(default=0.1, description="Probability of rewiring each edge.", ge=0.0, le=1.0)
    ba_m: int = Field(default=2, description="Number of edges to attach from a new node to existing nodes.", ge=1)

class GovernmentConfig(BaseModel):
    initial_budget: float = Field(default=1000000.0, description="Total finite policy budget.", ge=0.0)
    target_adoption_rate: float = Field(default=0.5, description="Target proportion of households to adopt.", ge=0.0, le=1.0)
    base_subsidy: float = Field(default=1000.0, description="Initial subsidy amount.", ge=0.0)
    dynamic_subsidy: bool = Field(default=True, description="Whether subsidy adjusts dynamically based on adoption targets.")

class IndustryConfig(BaseModel):
    base_price: float = Field(default=5000.0, description="Initial cost of a solar panel installation.", ge=0.0)
    price_adjustment_rate: float = Field(default=0.05, description="Rate at which price adjusts based on demand.", ge=0.0, le=1.0)
    dynamic_pricing: bool = Field(default=True, description="Whether panel price adjusts dynamically based on demand.")

class EnvironmentConfig(BaseModel):
    kw_per_panel: float = Field(default=5.0, description="Estimated capacity in kW per installation.", ge=0.0)
    co2_per_kw: float = Field(default=0.7, description="Estimated CO2 reduction in tons per kW.", ge=0.0)

class BehaviorPolicyConfig(BaseModel):
    name: str = Field(default="legacy_defaults")
    lower_threshold: float = Field(default=0.3, ge=0.0, le=1.0)
    upper_threshold: float = Field(default=0.7, ge=0.0, le=1.0)

class CognitiveConfig(BaseModel):
    policy: BehaviorPolicyConfig = Field(default_factory=BehaviorPolicyConfig)
    
    # Keep flat thresholds for backward compatibility, mapped to policy defaults if not overridden
    lower_threshold: float = Field(default=0.3, description="Below this score, clearly reject.", ge=0.0, le=1.0)
    upper_threshold: float = Field(default=0.7, description="Above this score, clearly adopt.", ge=0.0, le=1.0)
    
    @model_validator(mode='after')
    def sync_policy_thresholds(self):
        # Explicit policy overrides flat fields if a specific policy is named
        if self.policy.name == "cognitive_accessible_candidate_v1":
            self.policy.lower_threshold = 0.05
            self.policy.upper_threshold = 0.20
            self.lower_threshold = 0.05
            self.upper_threshold = 0.20
        else:
            # Sync flat fields into policy for consistency
            self.policy.lower_threshold = self.lower_threshold
            self.policy.upper_threshold = self.upper_threshold

        if self.lower_threshold > self.upper_threshold:
            raise ValueError("lower_threshold must be <= upper_threshold")
        return self

class LLMConfig(BaseModel):
    enabled: bool = Field(default=True, description="Whether LLM routing is enabled")
    provider: Literal["mock", "langgraph"] = Field(default="mock", description="The LLM provider to use")
    model: str = Field(default="gpt-4o-mini", description="The underlying LLM model identifier")
    temperature: float = Field(default=0.1, description="Temperature for LLM generation")
    fallback_enabled: bool = Field(default=True, description="Whether to use mathematical fallback if LLM fails")
    cache_enabled: bool = Field(default=True, description="Whether to cache LLM decisions for identical contexts")
    prompt_version: str = Field(default="v1", description="Version of the prompt to use")
    request_timeout: int = Field(default=10, description="Timeout for LLM API calls in seconds")

class ExperimentConfig(BaseModel):
    simulation: SimulationConfig = SimulationConfig()
    sir: SIRConfig = SIRConfig()
    network: NetworkConfig = NetworkConfig()
    government: GovernmentConfig = GovernmentConfig()
    industry: IndustryConfig = IndustryConfig()
    environment: EnvironmentConfig = EnvironmentConfig()
    cognitive: CognitiveConfig = CognitiveConfig()
    llm: LLMConfig = LLMConfig()

    @classmethod
    def load_from_yaml(cls, path: str):
        import yaml
        with open(path, 'r') as f:
            data = yaml.safe_load(f)
        return cls(**data)
