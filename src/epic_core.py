# src/epic_core.py
from typing import Dict, Any, List
from .epic_loader import EpicSpecLoader
from .epic_state import EpicState
from .cfi_engine import CFIEngine
from .arc_engine import ARCEngine

class EpicCore:
    """Full EPIC runtime engine based on operational spec."""

    def __init__(self, spec_path: str = "docs/EPIC-v10-Operational-Spec.json"):
        self.loader = EpicSpecLoader(spec_path)
        self.spec = self.loader.full_spec
        self.state = EpicState()
        self.cfi = CFIEngine(self.spec)
        self.arc = ARCEngine(self.spec)

    def process_query(self, query: str, history: List[str] = None) -> str:
        """Run one full EPIC turn."""
        history = history or []

        # 1. Probe (simplified)
        domain = "EED" if "?" in query else "WED"

        # 2. Branch (simplified)
        candidates = self.spec['decision_tables']['lane_priority_order']

        # 3. Map (simplified)
        claims = [query]  # atomic claims

        # 4. CFI
        band, scores, new_state = self.cfi.forecast({"query": query, "history": history})
        self.state.update_from_maintain({"steering_band": band, "forecast_scores": scores})

        # 5. ARC
        anchors = {"world_anchors": 0.5, "empirical_anchors": 0.4}  # sim
        claim_states = self.arc.classify_claims(claims, anchors)

        # 6. Resolve lane
        lane = "direct_answer" if claim_states[0] in ["verified", "well_supported"] else "inference"

        # 7. Define response (simplified)
        base = f"Response to '{query}' in {lane} lane."
        if lane == "inference":
            base = "A reasoned inference: " + base

        # 8. Maintain (already updated in CFI step)

        return base
