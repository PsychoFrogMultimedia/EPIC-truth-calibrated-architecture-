# src/cfi_engine.py
from typing import Dict, Any, Tuple
import random  # for simulation - replace with real models later

class CFIEngine:
    """Implements CFI forecasting, smoothing, hysteresis, band selection from spec."""

    def __init__(self, spec: Dict[str, Any]):
        self.spec = spec['cfi']
        self.state: Dict[str, Any] = {
            "S_prev": {},
            "forecast_history": [],
            "band_history": [],
            "mismatch_history": [],
            "oscillation_index": 0.0
        }

    def forecast(self, context: Dict[str, Any]) -> Tuple[str, Dict[str, float], Dict[str, Any]]:
        """Compute multi-horizon forecast and select steering band."""
        # Simulate 10 dimensions (replace with real logic later)
        dimensions = self.spec['forecast_dimensions']
        scores = {dim: random.uniform(0.0, 1.0) for dim in dimensions}

        # Simple aggregate risk score (expand to weighted sum from spec)
        risk_score = sum(scores.values()) / len(scores)

        # Select band based on risk + hysteresis
        current_band = self._apply_hysteresis(risk_score)

        guidance = self._generate_guidance(current_band)
        new_state = self._update_state(scores, current_band)

        return current_band, scores, new_state

    def _apply_hysteresis(self, risk_score: float) -> str:
        """Apply dynamic hysteresis from spec."""
        margins = self.spec['dynamic_hysteresis']['lane_switch_margins']
        prev = self.state['band_history'][-1] if self.state['band_history'] else "normal"

        if risk_score < 0.3:
            return "normal"
        elif risk_score < 0.6:
            return "steer_light" if prev in ["normal", "steer_light"] else "cautious"
        elif risk_score < 0.8:
            return "cautious"
        elif risk_score < 0.95:
            return "retrieve_first"
        else:
            return "abstain_cleanly"

    def _generate_guidance(self, band: str) -> str:
        """Generate steering guidance text from band."""
        effects = self.spec['steering_bands'].get(band, {}).get("effects", {})
        return f"Apply {band} posture: route bias {effects.get('route_bias', 'unknown')}"

    def _update_state(self, scores: Dict[str, float], band: str) -> Dict[str, Any]:
        self.state['forecast_history'].append(scores)
        self.state['band_history'].append(band)
        # Simulate oscillation increase if band changed
        if len(self.state['band_history']) > 1 and band != self.state['band_history'][-2]:
            self.state['oscillation_index'] += 0.1
        return self.state
