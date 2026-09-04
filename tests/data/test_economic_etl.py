import os
import pytest
import json
from schemas.data.economic import BenchmarkCostRecord, SubsidyRecord
from scripts.data.ingest_mnre_costs import ingest_mnre_costs
from scripts.data.ingest_pm_surya_ghar import ingest_pm_surya_ghar

def test_mnre_costs_etl():
    records = ingest_mnre_costs()
    assert records == 5
    
    # Verify processed data
    with open("data/processed/economic/mnre_benchmark_costs.json", "r") as f:
        data = json.load(f)
    
    assert len(data) == 5
    for item in data:
        # Schema validation
        record = BenchmarkCostRecord(**item)
        assert record.currency == "INR"
        assert record.benchmark_cost > 0
        assert record.dataset_id == "MNRE_BENCHMARK_2021_22"

def test_pm_surya_ghar_etl():
    records = ingest_pm_surya_ghar()
    assert records == 1
    
    with open("data/processed/economic/pm_surya_ghar.json", "r") as f:
        data = json.load(f)
        
    assert len(data) == 1
    record = SubsidyRecord(**data[0])
    assert record.policy_name == "PM Surya Ghar: Muft Bijli Yojana"
    assert len(record.slabs) == 3
    assert record.maximum_subsidy == 78000
    
    # Check date validation (will raise error if format is bad in pydantic natively if used, 
    # but here we just assert it exists and is a string)
    assert record.start_date == "2024-02-15"

def test_schema_validations():
    with pytest.raises(ValueError):
        # Invalid currency
        BenchmarkCostRecord(
            dataset_id="test",
            source="test",
            effective_date="2021",
            currency="USD", # Invalid
            benchmark_cost=1000,
            capacity_range="1kW",
            geography="National",
            source_reference="test"
        )
        
    with pytest.raises(ValueError):
        # Negative cost
        BenchmarkCostRecord(
            dataset_id="test",
            source="test",
            effective_date="2021",
            benchmark_cost=-1000, # Invalid
            capacity_range="1kW",
            geography="National",
            source_reference="test"
        )
