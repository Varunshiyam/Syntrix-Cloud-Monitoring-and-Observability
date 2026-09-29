import json
import sys
import re

def sanitize_key(key):
    # BigQuery columns must contain only letters, numbers, and underscores
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

def process_file(input_file, output_file):
    with open(input_file, 'r') as f:
        data = json.load(f)
        
    with open(output_file, 'w') as f:
        for row in data:
            sanitized_row = sanitize_dict(row)
            
            # For BigQuery autodetect to work well with highly variable schemas like jsonPayload,
            # it's best to stringify the variable nested structures.
            for field in ['labels', 'resource', 'jsonPayload', 'protoPayload', 'sourceLocation', 'operation']:
                if field in sanitized_row and isinstance(sanitized_row[field], dict):
                    sanitized_row[field] = json.dumps(sanitized_row[field])
                    
            f.write(json.dumps(sanitized_row) + '\n')

if __name__ == '__main__':
    process_file(sys.argv[1], sys.argv[2])
