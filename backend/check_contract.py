from pathlib import Path
import yaml

def _find_contracts_path() -> Path:
    p = Path(__file__).resolve()
    for parent in [p.parent] + list(p.parents):
        candidate = parent / "api-contracts.yaml"
        if candidate.exists():
            return candidate
    raise FileNotFoundError("api-contracts.yaml not found")

contracts_path = _find_contracts_path()
print(f"Found contract file: {contracts_path}")

spec = yaml.safe_load(contracts_path.read_text(encoding="utf-8"))
print(f"Keywords path exists: {'/moderator/keywords' in spec['paths']}")
print(f"Logs path exists: {'/moderator/parsing-runs/{runId}/logs' in spec['paths']}")
print(f"Total paths in contract: {len(spec['paths'])}")
