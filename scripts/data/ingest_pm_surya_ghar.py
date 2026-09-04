import os
import json
import hashlib
from datetime import date
from schemas.data.economic import SubsidyRecord, SubsidySlab, ProvenanceMetadata

def compute_checksum(filepath):
    hasher = hashlib.sha256()
    with open(filepath, 'rb') as f:
        buf = f.read()
        hasher.update(buf)
    return hasher.hexdigest()

def ingest_pm_surya_ghar():
    raw_path = "data/raw/economic/pm_surya_ghar/official_guidelines_2024.json"
    processed_path = "data/processed/economic/pm_surya_ghar.json"
    metadata_path = "data/metadata/economic/pm_surya_ghar_meta.json"
    
    if not os.path.exists(raw_path):
        raise FileNotFoundError(f"Raw file not found: {raw_path}")
        
    with open(raw_path, 'r') as f:
        raw_data = json.load(f)
        
    dataset_id = "PM_SURYA_GHAR_2024"
    checksum = compute_checksum(raw_path)
    
    metadata = ProvenanceMetadata(
        dataset_id=dataset_id,
        source=raw_data["source"],
        source_url=raw_data["url"],
        access_date=date.today(),
        checksum=checksum,
        raw_filename=os.path.basename(raw_path),
        processing_script="ingest_pm_surya_ghar.py"
    )
    
    slabs = []
    seen = set()
    for slab in raw_data["subsidy_structure"]:
        if slab["capacity_band"] in seen:
            raise ValueError(f"Duplicate subsidy band found: {slab['capacity_band']}")
        seen.add(slab["capacity_band"])
        
        # Check contradictory logic (e.g. max_subsidy shouldn't be negative)
        if slab["max_subsidy_for_band"] < 0:
            raise ValueError("Contradictory data: negative maximum subsidy")
            
        slabs.append(SubsidySlab(
            capacity_band=slab["capacity_band"],
            subsidy_amount=slab["subsidy_per_kw"],
            max_subsidy=slab["max_subsidy_for_band"]
        ))
        
    record = SubsidyRecord(
        dataset_id=dataset_id,
        policy_id="PM_SURYA_GHAR_V1",
        policy_name=raw_data["scheme"],
        start_date=raw_data["launch_date"],
        geography="National",
        eligibility=raw_data["eligibility"],
        slabs=slabs,
        maximum_subsidy=raw_data["overall_max_subsidy"],
        implementation_notes=raw_data["notes"],
        source_reference=raw_data["url"]
    )
    
    # Save processed
    with open(processed_path, 'w') as f:
        json.dump([record.model_dump()], f, indent=2)
        
    # Save metadata
    with open(metadata_path, 'w') as f:
        json.dump(metadata.model_dump(), f, indent=2, default=str)
        
    print(f"Successfully processed PM Surya Ghar policy with {len(slabs)} slabs.")
    return 1

if __name__ == "__main__":
    ingest_pm_surya_ghar()
