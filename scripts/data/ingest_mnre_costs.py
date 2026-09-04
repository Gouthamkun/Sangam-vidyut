import os
import json
import hashlib
from datetime import date
from schemas.data.economic import BenchmarkCostRecord, ProvenanceMetadata

def compute_checksum(filepath):
    hasher = hashlib.sha256()
    with open(filepath, 'rb') as f:
        buf = f.read()
        hasher.update(buf)
    return hasher.hexdigest()

def ingest_mnre_costs():
    raw_path = "data/raw/economic/mnre_benchmark_costs/benchmark_costs_2021_22.json"
    processed_path = "data/processed/economic/mnre_benchmark_costs.json"
    metadata_path = "data/metadata/economic/mnre_benchmark_costs_meta.json"
    
    if not os.path.exists(raw_path):
        raise FileNotFoundError(f"Raw file not found: {raw_path}")
        
    with open(raw_path, 'r') as f:
        raw_data = json.load(f)
        
    dataset_id = "MNRE_BENCHMARK_2021_22"
    checksum = compute_checksum(raw_path)
    
    metadata = ProvenanceMetadata(
        dataset_id=dataset_id,
        source=raw_data["source"],
        source_url=raw_data["url"],
        access_date=date.today(),
        checksum=checksum,
        raw_filename=os.path.basename(raw_path),
        processing_script="ingest_mnre_costs.py"
    )
    
    processed_records = []
    
    # Check duplicates by creating a unique key
    seen = set()
    
    for item in raw_data["categories"]:
        key = (item["geography"], item["capacity_range"])
        if key in seen:
            raise ValueError(f"Duplicate entry found for {key}")
        seen.add(key)
        
        record = BenchmarkCostRecord(
            dataset_id=dataset_id,
            source=raw_data["source"],
            effective_date=raw_data["effective_year"],
            currency="INR",
            unit="INR/kW",
            system_category="Residential",
            benchmark_cost=item["cost_per_kw_INR"],
            capacity_range=item["capacity_range"],
            geography=item["geography"],
            source_reference=raw_data["document"]
        )
        processed_records.append(record.model_dump())
        
    # Save processed
    with open(processed_path, 'w') as f:
        json.dump(processed_records, f, indent=2)
        
    # Save metadata
    with open(metadata_path, 'w') as f:
        # date serialization handler
        json.dump(metadata.model_dump(), f, indent=2, default=str)
        
    print(f"Successfully processed {len(processed_records)} benchmark cost records.")
    return len(processed_records)

if __name__ == "__main__":
    ingest_mnre_costs()
