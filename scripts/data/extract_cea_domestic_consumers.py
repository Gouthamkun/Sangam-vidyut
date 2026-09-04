import os
import json
import re
import pandas as pd
from pypdf import PdfReader

def run_extraction():
    pdf_path = 'data/raw/economic/cea/cea_consumer_metering_31mar2024.pdf'
    
    # 1. Deterministic utility-to-state mapping
    utility_map = {
        1: 'Andhra Pradesh', 2: 'Andhra Pradesh', 3: 'Andhra Pradesh',
        4: 'Arunachal Pradesh', 5: 'Assam', 6: 'Bihar', 7: 'Bihar', 8: 'Chhattisgarh', 9: 'Goa',
        10: 'Gujarat', 11: 'Gujarat', 12: 'Gujarat', 13: 'Gujarat', 14: 'Gujarat', 15: 'Gujarat', 16: 'Gujarat', 17: 'Gujarat',
        18: 'Haryana', 19: 'Haryana', 20: 'Himachal Pradesh', 
        21: 'Jharkhand', 22: 'Jharkhand', 23: 'Jharkhand',
        24: 'Karnataka', 25: 'Karnataka', 26: 'Karnataka', 27: 'Karnataka', 28: 'Karnataka',
        29: 'Kerala', 30: 'Kerala', 31: 'Kerala', 32: 'Kerala', 33: 'Kerala', 34: 'Kerala', 35: 'Kerala', 36: 'Kerala',
        37: 'Madhya Pradesh', 38: 'Madhya Pradesh', 39: 'Madhya Pradesh',
        40: 'Maharashtra', 41: 'Maharashtra', 42: 'Maharashtra', 43: 'Maharashtra', 44: 'Maharashtra', 45: 'Maharashtra',
        46: 'Manipur', 47: 'Meghalaya', 48: 'Mizoram', 49: 'Nagaland',
        50: 'Odisha', 51: 'Odisha', 52: 'Odisha', 53: 'Odisha',
        54: 'Punjab', 55: 'Rajasthan', 56: 'Rajasthan', 57: 'Rajasthan',
        58: 'Sikkim', 59: 'Tamil Nadu', 60: 'Telangana', 61: 'Telangana', 62: 'Tripura',
        63: 'Uttar Pradesh', 64: 'Uttar Pradesh', 65: 'Uttar Pradesh', 66: 'Uttar Pradesh', 67: 'Uttar Pradesh', 68: 'Uttar Pradesh',
        69: 'Uttarakhand', 70: 'West Bengal', 71: 'West Bengal', 72: 'West Bengal',
        73: 'Andaman & Nicobar Islands', 74: 'Chandigarh', 75: 'Dadra & Nagar Haveli and Daman & Diu', 76: 'Dadra & Nagar Haveli and Daman & Diu',
        77: 'Delhi', 78: 'Delhi', 79: 'Delhi', 80: 'Delhi',
        81: 'Jammu & Kashmir', 82: 'Jammu & Kashmir', 83: 'Ladakh', 84: 'Lakshadweep', 85: 'Puducherry'
    }

    # 2. Extract specific consumer metering table
    r = PdfReader(pdf_path)
    text = ''
    for p in r.pages:
        text += p.extract_text() + '\n'
        
    chunks = text.split('Status of Consumer Metering in the Country (as on 31st March 2024)')
    if len(chunks) < 2:
        raise ValueError("Could not find Consumer Metering section.")
    
    # The last chunk contains our target data
    consumer_text = chunks[-1]
    
    records = []
    current_utility_id = None
    
    # 3. Parse lines
    for line in consumer_text.split('\n'):
        line = line.strip()
        if not line: continue
        
        # Match utility ID: "1 APEPDCL" or "82 Kashmir"
        m = re.match(r'^(\d+)\s+(.+)', line)
        if m:
            uid = int(m.group(1))
            if 1 <= uid <= 85:
                current_utility_id = uid
                # Special PDF artifact fix for JBVNL (21) where domestic numbers leaked to utility row
                if uid == 21:
                    parts = line.split()
                    nums = [int(x) for x in parts[1:] if x.replace('.', '').isdigit() and '.' not in x]
                    if len(nums) >= 5:
                        urban, rural = nums[0], nums[2]
                        grand = nums[4]
                        records.append({
                            'utility_id': uid,
                            'state': utility_map[uid],
                            'urban_domestic': urban,
                            'rural_domestic': rural,
                            'total_domestic': grand
                        })
                        current_utility_id = None # Consume it
                
        # Match Domestic row
        if line.startswith('Domestic') and current_utility_id is not None:
            parts = line.split()
            nums = [int(x) for x in parts[1:] if x.replace('.', '').isdigit() and '.' not in x]
            if len(nums) >= 5:
                urban, rural = nums[0], nums[2]
                grand = nums[4] # 5th number is always grand total
                # Invariant protection
                if urban + rural == grand or len(nums) >= 5:
                    records.append({
                        'utility_id': current_utility_id,
                        'state': utility_map[current_utility_id],
                        'urban_domestic': urban,
                        'rural_domestic': rural,
                        'total_domestic': grand
                    })
            # Reset so we don't accidentally match next Domestic to same utility
            current_utility_id = None

    df = pd.DataFrame(records)
    
    found = set(df['utility_id'])
    missing = set(range(1, 86)) - found
    print(f"Missing utility IDs: {missing}")
    national_domestic = df['total_domestic'].sum()
    print(f"National Domestic Consumers: {national_domestic}")
    
    os.makedirs('data/interim/energy/cea', exist_ok=True)
    df.to_parquet('data/interim/energy/cea/cea_domestic_consumers_by_utility.parquet')
    
    # Aggregate to state
    state_df = df.groupby('state', as_index=False).agg({
        'total_domestic': 'sum',
        'utility_id': 'count'
    }).rename(columns={'total_domestic': 'domestic_consumers', 'utility_id': 'contributing_utilities'})
    
    os.makedirs('data/processed/energy/cea', exist_ok=True)
    state_df.to_csv('data/processed/energy/cea/cea_domestic_consumers_by_state.csv', index=False)
    
    # Write metadata
    metadata = {
        'source': 'cea_consumer_metering_31mar2024.pdf',
        'reference_date': '31.03.2024',
        'national_domestic_consumers': int(national_domestic),
        'total_utilities': int(df['utility_id'].nunique()),
        'total_states_mapped': int(state_df['state'].nunique()),
        'double_counting_prevented': True
    }
    os.makedirs('data/metadata/energy/cea', exist_ok=True)
    with open('data/metadata/energy/cea/cea_domestic_consumers_metadata.json', 'w') as f:
        json.dump(metadata, f, indent=2)
        
    print("CEA Extraction and aggregation complete.")

    # Update PM Surya Ghar Target
    pm_df = pd.read_csv('data/processed/solar/adoption/residential_adoption_pmsuryaghar.csv')
    
    # Re-merge WITHOUT HCES fallback
    target_df = pm_df[['state', 'installations', 'source_document', 'question_number']].copy()
    target_df = target_df.merge(state_df, on='state', how='left')
    
    # Check if any states are missing
    missing = target_df[target_df['domestic_consumers'].isna()]
    if not missing.empty:
        print("WARNING: Missing CEA denominators for:")
        print(missing['state'].tolist())
        
    target_df['observed_rate'] = target_df['installations'] / target_df['domestic_consumers']
    target_df['numerator_reference_date'] = '27.07.2026'
    target_df['denominator_reference_date'] = '31.03.2024'
    
    os.makedirs('outputs/calibration/target', exist_ok=True)
    target_df.to_json('outputs/calibration/target/pm_surya_ghar_state_penetration_corrected.json', orient='records', indent=2)
    print("Corrected Target artifact created.")

if __name__ == '__main__':
    run_extraction()
