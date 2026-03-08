from typing import Dict, Any, List
from .epic_loader import EpicSpecLoader
from .epic_state import EpicState
from .cfi_engine import CFIEngine
from .arc_engine import ARCEngine

class EpicCore:
    """Full EPIC runtime engine — loads spec, executes all phases."""

    def __init__(self, spec_path: str = "docs/EPIC-v10-Operational-Spec.json"):
        self.loader = EpicSpecLoader(spec_path)
        self.spec = self.loader.full_spec
        self.state = EpicState()
        self.cfi = CFIEngine(self.spec)
        self.arc = ARCEngine(self.spec)

    def process_query(self, query: str, history: List[str] = None) -> str:
        """Execute one complete EPIC turn using the spec-defined flow."""
        history = history or []

        telemetry = self.state.get_telemetry()
        telemetry['task_profile'] = "query_processing"

        # 1. Probe
        domain = self._probe_domain(query)
        self.state.domain = domain

        # 2. Branch
        candidates = self.spec['decision_tables']['lane_priority_order']

        # 3. Map
        claims = self.arc.decompose_claims(query)

        # 4. CFI
        band, scores, new_cfi_state = self.cfi.forecast(query, history)

        # 5. ARC
        anchors = self._get_anchors()  # Expand to real retrieval
        anchor_score = self.arc.score_anchors(anchors)
        claim_states = self.arc.assign_states(claims, [anchor_score] * len(claims))

        # 6. Resolve lane
        lane = self._resolve_lane(band, claim_states)

        # 7. Define response with disclosure
        base_response = "This is a governed response to your query: " + query
        disclosed = self._apply_disclosure(lane, base_response)

        # 8. Maintain
        maintain_output = {
            "steering_band": band,
            "forecast_scores": scores,
            "calibration_mismatch": 0.0,  # Real value from outcome comparison
            "oscillation_index": self.state.oscillation_index,
            "telemetry_record": telemetry,
            "claim_record_revision": {"query": claim_states},
            "anchor_weight_adjustment": anchors,
            "calibration_update_summary": {}
        }
        self.state.update_from_maintain(maintain_output)

        return disclosed

    def _probe_domain(self, query: str) -> str:
        """Probe phase: classify domain from spec rules."""
        rules = self.spec['governance']['domain_assignment']['rules']
        query_lower = query.lower()
        if 'self' in query_lower or 'i am' in query_lower or 'my identity' in query_lower:
            return "SED"
        elif '?' in query or 'what is' in query_lower or 'how' in query_lower or 'fact' in query_lower:
            return "EED"
        else:
            return "WED"

    def _get_anchors(self) -> Dict[str, float]:
        """Simulate anchor weights (expand to real retrieval/RAG later)."""
        classes = self.spec['arc']['trust_lattice']['anchor_classes']
        return {cls: classes[cls]['default_weight'] for cls in classes}

    def _resolve_lane(self, band: str, claim_states: List[str]) -> str:
        """Resolve lane using coupling laws from spec."""
        rules = self.spec['route_system']['coupling_law']['rules']
        if band in ["retrieve_first", "clarify_first", "abstain_cleanly"]:
            return band

        if all(s in ["verified", "well_supported"] for s in claim_states):
            return "direct_answer"
        elif any(s == "reasoned_inference" for s in claim_states):
            return "inference"
        elif any(s == "weak_inference" for s in claim_states):
            return "weak_inference"
        elif any(s == "speculative" for s in claim_states):
            return "speculative"
        else:
            return "abstain"

    def _apply_disclosure(self, lane: str, base: str) -> str:
        """Apply disclosure from spec rules."""
        rules = self.spec['disclosure']['rules']
        if lane == "direct_answer":
            return base
        rule = rules.get(lane, rules.get("weak_inference"))
        if rule['required_marker']:
            marker = rule['approved_forms'][0]
            return marker + " " + base
        return base        anchor_score = self.arc.score_anchors(anchors)
        claim_states = self.arc.assign_states(claims, [anchor_score] * len(claims))

        # 6. Resolve lane
        lane = self._resolve_lane(band, claim_states)

        # 7. Define response with disclosure
        base_response = "This is a governed response to your query: " + query
        disclosed = self._apply_disclosure(lane, base_response)

        # 8. Maintain
        maintain_output = {
            "steering_band": band,
            "forecast_scores": scores,
            "calibration_mismatch": 0.0,  # Real value would come from outcome
            "oscillation_index": self.state.oscillation_index,
            "telemetry_record": telemetry,
            "claim_record_revision": {"query": claim_states},
            "anchor_weight_adjustment": anchors,
            "calibration_update_summary": {}
        }
        self.state.update_from_maintain(maintain_output)

        return disclosed

    def _probe_domain(self, query: str) -> str:
        rules = self.spec['governance']['domain_assignment']['rules']
        if 'self' in query.lower() or 'I am' in query:
            return "SED"
        elif '?' in query or 'what is' in query.lower() or 'how' in query.lower():
            return "EED"
        else:
            return "WED"

    def _simulate_anchors(self) -> Dict[str, float]:
        classes = self.spec['arc']['trust_lattice']['anchor_classes']
        return {cls: classes[cls]['default_weight'] for cls in classes}

    def _resolve_lane(self, band: str, claim_states: List[str]) -> str:
        rules = self.spec['route_system']['coupling_law']['rules']
        if band in ["retrieve_first", "clarify_first", "abstain_cleanly"]:
            return band
        if all(s in ["verified", "well_supported"] for s in claim_states):
            return "direct_answer"
        elif any(s == "reasoned_inference" for s in claim_states):
            return "inference"
        elif any(s == "weak_inference" for s in claim_states):
            return "weak_inference"
        else:
            return "speculative"

    def _apply_disclosure(self, lane: str, base: str) -> str:
        rules = self.spec['disclosure']['rules']
        if lane == "direct_answer":
            return base
        rule = rules.get(lane, rules.get("weak_inference"))
        if rule['required_marker']:
            marker = rule['approved_forms'][0]
            return marker + " " + base
        return base        anchor_score = self.arc.score_anchors(anchors)
        claim_states = self.arc.assign_states(claims, [anchor_score] * len(claims))

        # 6. Resolve lane
        lane = self._resolve_lane(band, claim_states)

        # 7. Define response with disclosure
        base_response = "This is a governed response to your query: " + query
        disclosed = self._apply_disclosure(lane, base_response)

        # 8. Maintain
        maintain_output = {
            "steering_band": band,
            "forecast_scores": scores,
            "calibration_mismatch": 0.0,  # Real value would come from outcome
            "oscillation_index": self.state.oscillation_index,
            "telemetry_record": telemetry,
            "claim_record_revision": {"query": claim_states},
            "anchor_weight_adjustment": anchors,
            "calibration_update_summary": {}
        }
        self.state.update_from_maintain(maintain_output)

        return disclosed

    def _probe_domain(self, query: str) -> str:
        rules = self.spec['governance']['domain_assignment']['rules']
        if 'self' in query.lower() or 'I am' in query:
            return "SED"
        elif '?' in query or 'what is' in query.lower() or 'how' in query.lower():
            return "EED"
        else:
            return "WED"

    def _simulate_anchors(self) -> Dict[str, float]:
        classes = self.spec['arc']['trust_lattice']['anchor_classes']
        return {cls: classes[cls]['default_weight'] for cls in classes}

    def _resolve_lane(self, band: str, claim_states: List[str]) -> str:
        rules = self.spec['route_system']['coupling_law']['rules']
        if band in ["retrieve_first", "clarify_first", "abstain_cleanly"]:
            return band
        if all(s in ["verified", "well_supported"] for s in claim_states):
            return "direct_answer"
        elif any(s == "reasoned_inference" for s in claim_states):
            return "inference"
        elif any(s == "weak_inference" for s in claim_states):
            return "weak_inference"
        else:
            return "speculative"

    def _apply_disclosure(self, lane: str, base: str) -> str:
        rules = self.spec['disclosure']['rules']
        if lane == "direct_answer":
            return base
        rule = rules.get(lane, rules.get("weak_inference"))
        if rule['required_marker']:
            marker = rule['approved_forms'][0]
            return marker + " " + base
        return base        claim_states = self.arc.classify_claims(claims, anchors)

        # 6. Resolve lane
        lane = "direct_answer" if claim_states[0] in ["verified", "well_supported"] else "inference"

        # 7. Define response (simplified)
        base = f"Response to '{query}' in {lane} lane."
        if lane == "inference":
            base = "A reasoned inference: " + base

        # 8. Maintain (already updated in CFI step)

        return base
