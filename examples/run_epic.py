from pathlib import Path

from src.epic_loader import load_epic_spec
from src.epic_state import EpicState
from src.epic_core import EpicCore

spec = load_epic_spec(Path("docs/EPIC-v10-Operational-Spec.json"))
state = EpicState()
core = EpicCore(spec, state)

prompt = "What is the safest interpretation of this architecture under uncertainty?"
print(core.run(prompt))
