import sys
import yaml

def validate_openapi_contract(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        contract = yaml.safe_load(f)
    
    paths = contract.get('paths', {})
    errors = []
    
    for path in paths.keys():
        if not path.startswith('/'):
            errors.append(f"Path does not start with '/': {path}")
    
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        sys.exit(1)
    
    print(f"OK: All {len(paths)} paths start with '/'")
    sys.exit(0)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python validate_openapi_contract.py <contract.yaml>", file=sys.stderr)
        sys.exit(2)
    validate_openapi_contract(sys.argv[1])