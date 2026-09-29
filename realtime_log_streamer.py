import json
import subprocess
import time
import re
import sys
from datetime import datetime, timedelta

PROJECT_ID = "project-4e3f1563-833a-4721-bf7"
DATASET = "syntrix_logs"
TABLE = "raw_logs"

def sanitize_key(key):
    return re.sub(r'[^a-zA-Z0-9_]', '_', key)

def sanitize_dict(d):
    if not isinstance(d, dict):
        return d
    new_dict = {}
    for k, v in d.items():
        new_k = sanitize_key(k)
        if isinstance(v, dict):
            new_dict[new_k] = sanitize_dict(v)
        elif isinstance(v, list):
            new_dict[new_k] = [sanitize_dict(i) if isinstance(i, dict) else i for i in v]
        else:
            new_dict[new_k] = v
    return new_dict

def main():
    last_timestamp = (datetime.utcnow() - timedelta(minutes=60)).isoformat() + "Z"
    print(f"Starting log streaming from {last_timestamp}", flush=True)
    
    while True:
        try:
            query = f'resource.type=("cloud_run_revision" OR "gce_instance" OR "k8s_container") AND timestamp>="{last_timestamp}"'
            cmd = ['gcloud', 'logging', 'read', query, '--project', PROJECT_ID, '--format=json', '--limit=2000']
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"Error reading logs: {result.stderr}", flush=True)
                time.sleep(10)
                continue
                
            if not result.stdout.strip():
                time.sleep(10)
                continue
                
            logs = json.loads(result.stdout)
            if not logs:
                time.sleep(10)
                continue
                
            latest_ts = last_timestamp
            processed_lines = []
            
            for row in reversed(logs):
                if row['timestamp'] > latest_ts:
                    latest_ts = row['timestamp']
                    
                sanitized_row = sanitize_dict(row)
                for field in ['labels', 'resource', 'jsonPayload', 'protoPayload', 'sourceLocation', 'operation']:
                    if field in sanitized_row and isinstance(sanitized_row[field], dict):
                        sanitized_row[field] = json.dumps(sanitized_row[field])
                
                processed_lines.append(json.dumps(sanitized_row))
                
            if processed_lines:
                with open('/tmp/stream_batch.ndjson', 'w') as f:
                    f.write('\n'.join(processed_lines) + '\n')
                    
                bq_cmd = [
                    'bq', 'load', 
                    '--source_format=NEWLINE_DELIMITED_JSON', 
                    '--schema_update_option=ALLOW_FIELD_ADDITION', 
                    '--ignore_unknown_values',
                    f'{PROJECT_ID}:{DATASET}.{TABLE}', 
                    '/tmp/stream_batch.ndjson'
                ]
                bq_result = subprocess.run(bq_cmd, capture_output=True, text=True)
                
                if bq_result.returncode == 0:
                    print(f"Appended {len(processed_lines)} rows up to {latest_ts}", flush=True)
                    last_timestamp = latest_ts[:-1] + "1Z" 
                else:
                    print(f"Error loading to BQ: {bq_result.stderr}\nSTDOUT: {bq_result.stdout}", flush=True)
                    
        except Exception as e:
            print(f"Exception: {e}", flush=True)
            
        time.sleep(10)

if __name__ == '__main__':
    main()
