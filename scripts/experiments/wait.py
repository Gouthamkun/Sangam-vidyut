import json
import time
while True:
    try:
        with open('outputs/experiments/phase_4f_1_rerun/checkpoints/progress.json', 'r') as f:
            d = json.load(f)
        total = d.get('validated_runs', 0) + d.get('skipped_existing_runs', 0)
        print(f"Waiting... {total}/180")
        if total >= 180:
            print('DONE')
            break
    except Exception as e:
        pass
    time.sleep(10)
