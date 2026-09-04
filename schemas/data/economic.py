from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from datetime import date

class ProvenanceMetadata(BaseModel):
    dataset_id: str
    source: str
    source_url: str
    access_date: date
    checksum: str
    raw_filename: str
    processing_script: str

class BenchmarkCostRecord(BaseModel):
    dataset_id: str
    source: str
    effective_date: str
    currency: str = "INR"
    unit: str = "INR/kW"
    system_category: str = "Residential"
    benchmark_cost: float = Field(..., ge=0)
    capacity_range: str
    geography: str
    source_reference: str

    @field_validator("currency")
    @classmethod
    def check_currency(cls, v):
        if v != "INR":
            raise ValueError("Currency must be INR")
        return v

class SubsidySlab(BaseModel):
    capacity_band: str
    subsidy_amount: float = Field(..., ge=0)
    max_subsidy: float = Field(..., ge=0)
    
class SubsidyRecord(BaseModel):
    dataset_id: str
    policy_id: str
    policy_name: str
    start_date: str
    end_date: Optional[str] = None
    geography: str = "National"
    eligibility: str
    slabs: List[SubsidySlab]
    maximum_subsidy: float = Field(..., ge=0)
    implementation_notes: str
    source_reference: str

    @field_validator("slabs")
    @classmethod
    def check_slabs(cls, v):
        if not v:
            raise ValueError("At least one subsidy slab is required")
        return v
