import json
from pathlib import Path
from typing import Dict, Any

class EpicSpecLoader:
    """Loads and validates the EPIC operational spec JSON.

    Raises:
        FileNotFoundError: If the spec file does not exist.
        ValueError: If required top-level keys are missing or version mismatch.
        json.JSONDecodeError: If the JSON is malformed (wrapped in ValueError).
    """

    EXPECTED_VERSION = "1.0.0"

    REQUIRED_TOP_KEYS = [
        "system", "domains", "platonic_5_plus_1", "cfi", "arc", "route_system",
        "disclosure", "governance", "health_monitors", "learning_and_adaptation",
        "telemetry", "evaluation", "runtime", "decision_tables", "surface_contract",
        "canonical_theorem"
    ]

    def __init__(self, spec_path: str = "docs/EPIC-v10-Operational-Spec.json"):
        self.spec_path = Path(spec_path)
        self.spec: Dict[str, Any] = self._load_and_validate()

    def _load_and_validate(self) -> Dict[str, Any]:
        if not self.spec_path.exists():
            raise FileNotFoundError(f"EPIC operational spec not found at: {self.spec_path}")

        try:
            with self.spec_path.open("r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in spec file {self.spec_path}: {e}") from e

        # Version check
        version = data.get("system", {}).get("version")
        if version != self.EXPECTED_VERSION:
            raise ValueError(
                f"Spec version mismatch: expected {self.EXPECTED_VERSION}, "
                f"got {version or 'missing'}"
            )

        # Top-level keys
        missing_keys = [k for k in self.REQUIRED_TOP_KEYS if k not in data]
        if missing_keys:
            raise ValueError(f"Missing required top-level keys: {', '.join(missing_keys)}")

        # Optional: deeper spot-checks (add more as needed)
        if "cfi" in data and "forecast_dimensions" not in data["cfi"]:
            raise ValueError("cfi section missing 'forecast_dimensions'")

        if "arc" in data and "trust_lattice" not in data["arc"]:
            raise ValueError("arc section missing 'trust_lattice'")

        return data

    @property
    def full_spec(self) -> Dict[str, Any]:
        """Returns the full loaded and validated spec."""
        return self.spec
