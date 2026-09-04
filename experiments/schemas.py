from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Literal, Dict, Any

class ExperimentConfig(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    experiment_id: str
    model_type: Literal["STATIC_BASELINE", "SIR_ONLY", "DETERMINISTIC_ABM", "FULL_COGNITIVE_ABM"]
    seed: int
    n_agents: int = 500
    timesteps: int = 12
    topology: str = "watts_strogatz"
    
class ExperimentResult(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    experiment_id: str
    model_type: str
    seed: int
    population: int
    # Provenance and Traceability
    provider: Optional[str] = None
    model_identifier: Optional[str] = None
    prompt_version: Optional[str] = None
    model_configuration: Optional[dict] = None
    cache_scope: Optional[str] = "seed"
    
    # Core Metrics
    timesteps: int
    final_adoption: int
    final_adoption_rate: float
    cumulative_adoptions: List[int]
    tipping_point: Optional[int]
    tipping_point_reached: bool
    peak_new_adoption_rate: float
    time_to_25_percent: Optional[int]
    time_to_50_percent: Optional[int]
    total_llm_calls: Optional[int]
    total_cache_hits: Optional[int]
    total_llm_failures: Optional[int]
    cumulative_co2_displaced: Optional[float]

class AblationConfig(BaseModel):
    disable_sir: bool = False
    disable_network: bool = False
    disable_dynamic_subsidy: bool = False
    disable_dynamic_pricing: bool = False
    disable_llm: bool = False
    force_mock_llm: bool = False

class MultiSeedExperimentConfig(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    experiment_name: str
    model_type: Literal["STATIC_BASELINE", "SIR_ONLY", "DETERMINISTIC_ABM", "FULL_COGNITIVE_ABM"]
    seeds: List[int]
    n_agents: int = 500
    timesteps: int = 12
    topology: str = "watts_strogatz"
    
    # Overrides for specific parameters to support parameter sweeps
    parameters: Dict[str, Any] = Field(default_factory=dict)
    
    ablation: AblationConfig = Field(default_factory=AblationConfig)

class AggregatedResult(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    experiment_name: str
    model_type: str
    num_seeds: int
    
    # Provenance
    provider: Optional[str] = None
    model_identifier: Optional[str] = None
    prompt_version: Optional[str] = None
    cache_scope: Optional[str] = "seed"
    
    mean_final_adoption_rate: float
    std_final_adoption_rate: float
    min_final_adoption_rate: float
    max_final_adoption_rate: float
    mean_tipping_point: Optional[float]
    fraction_tipping_point_reached: float
    mean_peak_new_adoption_rate: float
    mean_time_to_25_percent: Optional[float]
    mean_time_to_50_percent: Optional[float]
    mean_llm_calls: float
    mean_cache_hit_rate: float
