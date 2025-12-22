from pathlib import Path

import yaml

from app.main import app


def _find_contracts_path() -> Path:
    p = Path(__file__).resolve()
    for parent in [p.parent] + list(p.parents):
        candidate = parent / "api-contracts.yaml"
        if candidate.exists():
            return candidate
    raise FileNotFoundError("api-contracts.yaml not found starting from: " + str(p))


def test_openapi_has_no_extra_paths_vs_contract():
    """
    Contract is the only source of truth.
    Rule enforced here: implementation MUST NOT expose endpoints not present in api-contracts.yaml.
    Missing endpoints are allowed (they're simply not implemented yet).
    """
    contracts_path = _find_contracts_path()
    spec = yaml.safe_load(contracts_path.read_text(encoding="utf-8"))

    allowed = set(spec["paths"].keys())
    actual = set(app.openapi()["paths"].keys())

    extra = sorted(actual - allowed)
    assert not extra, f"Extra paths not in SSoT api-contracts.yaml: {extra}"


def test_show_missing_paths_for_dev_visibility(capsys):
    # not a gate, just prints what is not implemented yet
    contracts_path = _find_contracts_path()
    spec = yaml.safe_load(contracts_path.read_text(encoding="utf-8"))

    expected = set(spec["paths"].keys())
    actual = set(app.openapi()["paths"].keys())

    missing = sorted(expected - actual)
    print("MISSING_ENDPOINTS_COUNT=", len(missing))
    # keep it short
    print("MISSING_SAMPLE=", missing[:10])
