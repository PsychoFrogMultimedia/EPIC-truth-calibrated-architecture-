from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict

from .arc_engine import ARCEngine
from .cfi_engine import CFIEngine
from .epic_state import EpicState


@dataclass
class EpicCore:
    spec: Dict[str, Any]
    state: EpicState

    def __post_init__(self) -> None:
        self.arc = ARCEngine(self.spec)
        self.cfi = CFIEngine(self.spec)

    def probe(self, user_input: str) -> Dict[str, Any]:
        domain = "EED" if "?" in user_input or len(user_input.split()) > 8 else "WED"
        return {
            "domain": domain,
            "ambiguity_load": 0.3 if " or " in user_input.lower() else 0.1,
            "cost_of_wrong": 0.7 if any(k in user_input.lower() for k in ["medical", "legal", "financial"]) else 0.2,
        }

    def branch(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        return {"candidate_branches": self.spec["platonic_5_plus_1"]["phases"]["B"]["candidate_branches"]}

    def map_phase(self, user_input: str) -> Dict[str, Any]:
        claims = self.arc.decompose_claims(user_input)
        dummy_support = {
            "world_anchors": 0.5,
            "empirical_anchors": 0.2,
            "community_anchors": 0.2,
            "memory_anchors": 0.4,
            "user_anchors": 0.1,
            "conflict_load": 0.1,
        }
        scored = []
        for claim in claims:
            scores = self.arc.score_claim(claim, dummy_support)
            state = self.arc.assign_state(scores)
            scored.append({"claim": claim, "scores": scores, "state": state})
        return {"claims": scored}

    def resolve(self, probe: Dict[str, Any], mapped: Dict[str, Any]) -> Dict[str, Any]:
        signals = {
            "ambiguity_load": probe["ambiguity_load"],
            "anchor_thinness": 1.0 - max((c["scores"]["anchor_strength"] for c in mapped["claims"]), default=0.0),
            "bluff_pressure": 0.2,
            "cost_of_wrong": probe["cost_of_wrong"],
        }
        band, guidance, new_cfi_state = self.cfi.forecast(signals, self.state.control_state)

        resolved = []
        for item in mapped["claims"]:
            lanes = self.arc.legal_lanes(item["state"])
            lane = "abstain" if band == "abstain_cleanly" else lanes[0]
            resolved.append({**item, "lane": lane})

        self.state.control_state = new_cfi_state
        return {"band": band, "guidance": guidance, "claims": resolved}

    def define(self, resolved: Dict[str, Any]) -> str:
        rendered = []
        for item in resolved["claims"]:
            claim = item["claim"]
            state = item["state"]
            if state == "reasoned_inference":
                rendered.append(f"Based on what is anchored here, the most likely reading is: {claim}.")
            elif state == "weak_inference":
                rendered.append(f"This is a tentative read: {claim}.")
            elif state == "speculative":
                rendered.append(f"This is speculative: {claim}.")
            elif state == "unknown":
                rendered.append("I do not have enough reliable basis to say.")
            else:
                rendered.append(claim + ".")
        return " ".join(rendered)

    def run(self, user_input: str) -> str:
        p = self.probe(user_input)
        _ = self.branch(p)
        m = self.map_phase(user_input)
        r = self.resolve(p, m)
        out = self.define(r)
        self.state.record_telemetry({"probe": p, "resolved": r})
        return out            "user_anchors": 0.1,
            "conflict_load": 0.1,
        }
        scored = []
        for claim in claims:
            scores = self.arc.score_claim(claim, dummy_support)
            state = self.arc.assign_state(scores)
            scored.append({"claim": claim, "scores": scores, "state": state})
        return {"claims": scored}

    def resolve(self, probe: Dict[str, Any], mapped: Dict[str, Any]) -> Dict[str, Any]:
        signals = {
            "ambiguity_load": probe["ambiguity_load"],
            "anchor_thinness": 1.0 - max((c["scores"]["anchor_strength"] for c in mapped["claims"]), default=0.0),
            "bluff_pressure": 0.2,
            "cost_of_wrong": probe["cost_of_wrong"],
        }
        band, guidance, new_cfi_state = self.cfi.forecast(signals, self.state.control_state)

        resolved = []
        for item in mapped["claims"]:
            lanes = self.arc.legal_lanes(item["state"])
            lane = "abstain" if band == "abstain_cleanly" else lanes[0]
            resolved.append({**item, "lane": lane})

        self.state.control_state = new_cfi_state
        return {"band": band, "guidance": guidance, "claims": resolved}

    def define(self, resolved: Dict[str, Any]) -> str:
        rendered = []
        for item in resolved["claims"]:
            claim = item["claim"]
            state = item["state"]
            if state == "reasoned_inference":
                rendered.append(f"Based on what is anchored here, the most likely reading is: {claim}.")
            elif state == "weak_inference":
                rendered.append(f"This is a tentative read: {claim}.")
            elif state == "speculative":
                rendered.append(f"This is speculative: {claim}.")
            elif state == "unknown":
                rendered.append("I do not have enough reliable basis to say.")
            else:
                rendered.append(claim + ".")
        return " ".join(rendered)

    def run(self, user_input: str) -> str:
        p = self.probe(user_input)
        _ = self.branch(p)
        m = self.map_phase(user_input)
        r = self.resolve(p, m)
        out = self.define(r)
        self.state.record_telemetry({"probe": p, "resolved": r})
        return out        # 5. ARC
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
