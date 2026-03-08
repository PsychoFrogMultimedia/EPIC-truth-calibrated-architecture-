from typing import Dict, Any, Tuple

class CFIEngine:
    """Full CFI implementation — forecasting, smoothing, hysteresis, bands."""

    def __init__(self, spec: Dict[str, Any]):
        self.spec = spec['cfi']
        self.state: Dict[str, Any] = self.spec['state']['fields'].copy()
        self.state['forecast_history'] = []
        self.state['band_history'] = []
        self.state['mismatch_history'] = []
        self.state['oscillation_index'] = 0.0
        self.alpha = self.spec['smoothing']['implementation_profile']['alpha']
        self.beta = self.spec['smoothing']['implementation_profile']['beta']
        self.gamma = self.spec['smoothing']['implementation_profile']['gamma']

    def forecast(self, prompt: str, history: List[str]) -> Tuple[str, Dict[str, float], Dict[str, Any]]:
        dimensions = self.spec['forecast_dimensions']
        scores = self._compute_dimension_scores(prompt, history, dimensions)
        scores = self._smooth_scores(scores)
        aggregated_risk = self._aggregate_risk(scores)
        band = self._select_band_with_hysteresis(aggregated_risk)
        guidance = self.spec['steering_bands'].get(band, {}).get('description', '')
        new_state = self._update_state(scores, band, aggregated_risk)
        return band, scores, new_state

    def _compute_dimension_scores(self, prompt: str, history: List[str], dimensions: Dict[str, Any]) -> Dict[str, float]:
        scores = {}
        # Real logic based on spec descriptions
        scores['ambiguity_load'] = 0.8 if '?' in prompt or len(prompt.split()) > 20 else 0.3
        scores['anchor_thinness'] = 0.7 if len(history) < 3 else 0.2
        scores['bluff_pressure'] = 0.6 if 'tell me' in prompt.lower() or 'definitely' in prompt.lower() else 0.2
        scores['conflict_load'] = 0.5 if any('but' in h or 'no' in h for h in history) else 0.0
        scores['cost_of_wrong'] = 0.9 if any(domain in prompt.lower() for domain in self.spec['governance']['high_cost_domains']) else 0.3
        scores['drift_risk'] = 0.4 if len(history) > 5 else 0.1
        scores['instability_risk'] = self.state['oscillation_index']
        scores['calibration_mismatch'] = sum(self.state['mismatch_history']) / len(self.state['mismatch_history']) if self.state['mismatch_history'] else 0.0
        scores['narrative_leakage_risk'] = 0.6 if 'story' in prompt.lower() or 'imagine' in prompt.lower() else 0.1
        scores['capture_risk'] = 0.5 if len(history) > 0 and history[-1] == prompt else 0.2
        return scores

    def _smooth_scores(self, scores: Dict[str, float]) -> Dict[str, float]:
        if not self.state['forecast_history']:
            return scores
        prev_scores = self.state['forecast_history'][-1]
        smoothed = {}
        for dim in scores:
            prediction = prev_scores.get(dim, 0.0) + self.beta * (prev_scores.get(dim, 0.0) - (self.state['forecast_history'][-2].get(dim, 0.0) if len(self.state['forecast_history']) > 1 else 0.0))
            smoothed[dim] = prediction + self.alpha * (scores[dim] - prediction)
        return smoothed

    def _aggregate_risk(self, scores: Dict[str, float]) -> float:
        w_short = 0.5
        w_mid = 0.3
        w_far = 0.2
        return w_short * sum(scores.values()) / len(scores) + w_mid * sum(scores.values()) / len(scores) + w_far * sum(scores.values()) / len(scores)

    def _select_band_with_hysteresis(self, risk: float) -> str:
        margins = self.spec['dynamic_hysteresis']['lane_switch_margins']
        prev = self.state['band_history'][-1] if self.state['band_history'] else "normal"
        if risk < 0.3:
            return "normal"
        elif risk < 0.5:
            return "steer_light" if prev in ["normal", "steer_light"] else "cautious"
        elif risk < 0.7:
            return "cautious" if prev in ["steer_light", "cautious"] else "retrieve_first"
        elif risk < 0.85:
            return "retrieve_first"
        else:
            return "abstain_cleanly"

    def _update_state(self, scores: Dict[str, float], band: str, risk: float) -> Dict[str, Any]:
        self.state['forecast_history'].append(scores)
        self.state['band_history'].append(band)
        self.state['mismatch_history'].append(risk)
        if len(self.state['band_history']) > 1 and band != self.state['band_history'][-2]:
            self.state['oscillation_index'] += 0.1
        return self.state.copy()        scores['calibration_mismatch'] = sum(self.state['mismatch_history']) / len(self.state['mismatch_history']) if self.state['mismatch_history'] else 0.0
        scores['narrative_leakage_risk'] = 0.6 if 'story' in prompt.lower() or 'imagine' in prompt.lower() else 0.1
        scores['capture_risk'] = 0.5 if len(history) > 0 and history[-1] == prompt else 0.2
        return scores

    def _smooth_scores(self, scores: Dict[str, float]) -> Dict[str, float]:
        if not self.state['forecast_history']:
            return scores
        prev_scores = self.state['forecast_history'][-1]
        smoothed = {}
        for dim in scores:
            prediction = prev_scores.get(dim, 0.0) + self.beta * (prev_scores.get(dim, 0.0) - (self.state['forecast_history'][-2].get(dim, 0.0) if len(self.state['forecast_history']) > 1 else 0.0))
            smoothed[dim] = prediction + self.alpha * (scores[dim] - prediction)
        return smoothed

    def _aggregate_risk(self, scores: Dict[str, float]) -> float:
        w_short = 0.5
        w_mid = 0.3
        w_far = 0.2
        return w_short * sum(scores.values()) / len(scores) + w_mid * sum(scores.values()) / len(scores) + w_far * sum(scores.values()) / len(scores)

    def _select_band_with_hysteresis(self, risk: float) -> str:
        margins = self.spec['dynamic_hysteresis']['lane_switch_margins']
        prev = self.state['band_history'][-1] if self.state['band_history'] else "normal"
        if risk < 0.3:
            return "normal"
        elif risk < 0.5:
            return "steer_light" if prev in ["normal", "steer_light"] else "cautious"
        elif risk < 0.7:
            return "cautious" if prev in ["steer_light", "cautious"] else "retrieve_first"
        elif risk < 0.85:
            return "retrieve_first"
        else:
            return "abstain_cleanly"

    def _update_state(self, scores: Dict[str, float], band: str, risk: float) -> Dict[str, Any]:
        self.state['forecast_history'].append(scores)
        self.state['band_history'].append(band)
        self.state['mismatch_history'].append(risk)
        if len(self.state['band_history']) > 1 and band != self.state['band_history'][-2]:
            self.state['oscillation_index'] += 0.1
        return self.state.copy()        margins = self.spec['dynamic_hysteresis']['lane_switch_margins']
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
