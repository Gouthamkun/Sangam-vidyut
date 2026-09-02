import json
import glob
import sys

try:
    results = []
    for p in glob.glob('outputs/experiments/exp2_economic_nonlinearity_sweep_*/aggregated/aggregated.json'):
        with open(p, 'r') as f:
            data = json.load(f)
            # Find the subsidy from the config metadata
            meta_path = p.replace('aggregated\\aggregated.json', 'metadata\\config.json').replace('aggregated/aggregated.json', 'metadata/config.json')
            with open(meta_path, 'r') as fm:
                meta = json.load(fm)
                data['subsidy'] = meta['parameters']['subsidy']
            results.append(data)
            
    results.sort(key=lambda x: x['subsidy'])
    
    with open('outputs/experiments/exp2_economic_nonlinearity/summary.json', 'w') as f:
        json.dump(results, f, indent=2)
        
    print("Summary written successfully.")
except Exception as e:
    print(f"Error: {e}")
