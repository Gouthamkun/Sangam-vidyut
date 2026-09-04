from pydantic import BaseModel, Field, ConfigDict
from typing import List, Dict, Optional

class TargetSpec(BaseModel):
    target_name: str = "PM_Surya_Ghar_State_Penetration"
    numerator_metric: str = "residential_installations"
    numerator_reference_date: str = "27.07.2024" # 2024, not 2026
    denominator_metric: str = "domestic_consumers"
    denominator_reference_date: str = "31.03.2024"
    geography: str = "State/UT"
    programme_scope: str = "PM Surya Ghar (Phase-II extension)"

class PreprocessingSpec(BaseModel):
    version: str = "1.0"
    log_transform_mpce: bool = True
    mpce_clip_lower: float = 1.0
    categorical_encoding: str = "one-hot"
    
class CalibrationConfig(BaseModel):
    seed: int = 42
    features: List[str] = ["derived_mpce", "household_size", "sector", "dwelling_type", "electricity_access", "free_electricity"]
    weight_column: str = "survey_weight"
    objective: str = "binomial_nll"
    state_effects: str = "none"
    validation_strategy: str = "loso" # Leave-one-state-out
    
class SerializedModelArtifact(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    model_version: str = "1.0"
    target: TargetSpec
    preprocessing: PreprocessingSpec
    coefficients: Dict[str, float]
    intercept: float
    feature_order: List[str]
    calibration_seed: int
    training_states: List[str]
