from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class ARCEngine:
    spec: Dict[str, Any]

    def decompose_claims(self, text: str) -> List[str]:
        parts = [p.strip() for p in text.split(".") if p.strip()]
        return parts

    def score_claim(self, claim: str, support: Dict[str, float]) -> Dict[str, float]:
        base = (
            support.get("world_anchors", 0.0) * 0.35
            + support.get("empirical_anchors", 0.0) * 0.35
            + support.get("community_anchors", 0.0) * 0.15
            + support.get("memory_anchors", 0.0) * 0.10
            + support.get("user_anchors", 0.0) * 0.05
        )
        specificity_burden = min(len(claim.split()) / 40.0, 1.0)
        return {
            "anchor_strength": max(0.0, min(1.0, base)),
            "specificity_burden": specificity_burden,
            "conflict_load": support.get("conflict_load", 0.0),
        }

    def assign_state(self, scores: Dict[str, float]) -> str:
        strength = scores["anchor_strength"]
        if strength >= 0.85:
            return "verified"
        if strength >= 0.70:
            return "well_supported"
        if strength >= 0.50:
            return "reasoned_inference"
        if strength >= 0.30:
            return "weak_inference"
        if strength >= 0.15:
            return "speculative"
        return "unknown"

    def legal_lanes(self, state: str) -> List[str]:
        lanes = self.spec["route_system"]["response_lanes"]
        return [name for name, lane in lanes.items() if state in lane["allowed_states"]]            elif score >= 0.1:
                states.append("speculative")
            else:
                states.append("unknown")
        return states
