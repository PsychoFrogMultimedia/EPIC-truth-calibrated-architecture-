from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class EpicState:
    control_state: Dict[str, Any] = field(default_factory=dict)
    forecast_history: List[Dict[str, Any]] = field(default_factory=list)
    lane_history: List[str] = field(default_factory=list)
    mismatch_history: List[Dict[str, Any]] = field(default_factory=list)
    anchored_claims: List[Dict[str, Any]] = field(default_factory=list)
    telemetry: List[Dict[str, Any]] = field(default_factory=list)

    def record_forecast(self, item: Dict[str, Any]) -> None:
        self.forecast_history.append(item)

    def record_lane(self, lane: str) -> None:
        self.lane_history.append(lane)

    def record_telemetry(self, item: Dict[str, Any]) -> None:
        self.telemetry.append(item)
