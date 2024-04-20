# ---INFO-----------------------------------------------------------------------
"""
Mirage is a framework for making arbitrary dynamic systems in an entity based
process modified and engine orchestrated model. It is designed to be modular and
extensible, with a focus on easy adaptation to new use cases.
"""

__all__ = [
    "engines",
    "entities",
    "monitors",
    "processes",
    "frameworks",
]

__version__ = "0.1.0"


# ---DEPENDENCIES---------------------------------------------------------------
from . import engines, entities, monitors, processes, frameworks
