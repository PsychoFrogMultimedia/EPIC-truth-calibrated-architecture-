from typing import Dict, Any, List


class ARCEngine:
    """Full ARC implementation — claim decomposition, lattice scoring, and state assignment."""

    def __init__(self, spec: Dict[str, Any]):
        self.spec = spec["arc"]

    def decompose_claims(self, prompt: str) -> List[str]:
        """Lightweight claim decomposition. Replace with parser-based segmentation later."""
        normalized = (
            prompt.replace("?", ".")
            .replace("!", ".")
            .replace("\n", ". ")
        )
        claims = [part.strip() for part in normalized.split(".") if part.strip()]
        return claims if claims else [prompt.strip()]

    def score_anchors(self, anchors: Dict[str, float]) -> float:
        """
        Score anchor support using trust lattice weights and penalties.

        Assumes `anchors` contains runtime anchor strengths in [0,1].
        """
        rules = self.spec["trust_lattice"]["rules"]
        classes = self.spec["trust_lattice"]["anchor_classes"]

        weighted_sum = 0.0
        total_possible_weight = 0.0

        for cls_name, cls_cfg in classes.items():
            runtime_strength = anchors.get(cls_name, 0.0)
            static_weight = cls_cfg["default_weight"]

            weighted_sum += runtime_strength * static_weight
            total_possible_weight += static_weight

        base_score = weighted_sum / total_possible_weight if total_possible_weight > 0 else 0.0

        distinct_classes = len([cls for cls, value in anchors.items() if value > 0.0])

        diversity_bonus_cfg = rules["diversity_bonus"]
        diversity_bonus = min(
            distinct_classes * diversity_bonus_cfg["bonus_per_distinct_anchor_class"],
            diversity_bonus_cfg["max_bonus"],
        )

        single_source_penalty = 0.0
        if rules["single_source_dampener"]["enabled"] and distinct_classes == 1:
            single_source_penalty = rules["single_source_dampener"]["decay_factor"]

        unsupported_penalty = 0.0
        if rules["unsupported_specificity_penalty"]["enabled"] and base_score < 0.5:
            unsupported_penalty = rules["unsupported_specificity_penalty"]["penalty"]

        # Stub staleness penalty until freshness is tracked per anchor
        staleness_penalty = 0.05

        score = base_score + diversity_bonus - single_source_penalty - unsupported_penalty - staleness_penalty
        return self._clamp(score)

    def assign_states(self, claims: List[str], anchor_scores: List[float]) -> List[str]:
        """Assign epistemic states from anchor scores."""
        states: List[str] = []

        for score in anchor_scores:
            if score >= 0.90:
                states.append("verified")
            elif score >= 0.70:
                states.append("well_supported")
            elif score >= 0.50:
                states.append("reasoned_inference")
            elif score >= 0.30:
                states.append("weak_inference")
            elif score >= 0.10:
                states.append("speculative")
            else:
                states.append("unknown")

        return states

    @staticmethod
    def _clamp(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
        return max(lo, min(hi, value))        if strength >= 0.30:
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
