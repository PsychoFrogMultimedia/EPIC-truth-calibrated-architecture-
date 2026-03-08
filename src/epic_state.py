from typing import Dict, Any, List
from datetime import datetime

class EpicState:
    """Persistent state across turns (continuity field from Maintain phase)."""

    def __init__(self):
        self.turn_count: int = 0
        self.domain: str = "EED"
        self.prev_steering_band: str = "normal"
        self.forecast_history: List[Dict[str, float]] = []
        self.band_history: List[str] = []
        self.mismatch_history: List[float] = []
        self.oscillation_index: float = 0.0
        self.calibration_summary: Dict[str, Any] = {}
        self.telemetry_records: List[Dict[str, Any]] = []
        self.claim_records: Dict[str, Dict[str, Any]] = {}
        self.anchor_weights: Dict[str, float] = {}

    def update_from_maintain(self, maintain_output: Dict[str, Any]):
        self.turn_count += 1
        self.prev_steering_band = maintain_output.get("steering_band", self.prev_steering_band)
        self.forecast_history.append(maintain_output.get("forecast_scores", {}))
        self.band_history.append(maintain_output.get("steering_band", "normal"))
        self.mismatch_history.append(maintain_output.get("calibration_mismatch", 0.0))
        self.oscillation_index = maintain_output.get("oscillation_index", self.oscillation_index)
        self.calibration_summary.update(maintain_output.get("calibration_update_summary", {}))
        self.telemetry_records.append(maintain_output.get("telemetry_record", {}))
        self.claim_records.update(maintain_output.get("claim_record_revision", {}))
        self.anchor_weights.update(maintain_output.get("anchor_weight_adjustment", {}))

    def get_telemetry(self) -> Dict[str, Any]:
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "domain": self.domain,
            "task_profile": "query_processing",
            "forecast_scores": self.forecast_history[-1] if self.forecast_history else {},
            "steering_band": self.prev_steering_band,
            "claim_units": [],
            "claim_states": [],
            "route_assignments": [],
            "anchor_map_summary": self.anchor_weights,
            "contradiction_flags": [],
            "retrieval_actions": [],
            "clarification_actions": [],
            "disclosure_types": [],
            "final_lane_mix": [],
            "post_outcome_signal": 0.0,
            "calibration_update_summary": self.calibration_summary
      }
