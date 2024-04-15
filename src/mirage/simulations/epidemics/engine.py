# ---INFO-----------------------------------------------------------------------
"""
State of the simulation engine.
"""

__all__ = [
    "EpidemicFireflyState",
]


# ---DEPENDENCIES---------------------------------------------------------------
import pydantic as pyd


# ---ENGINESTATE----------------------------------------------------------------
class EpidemicFireflyState(pyd.BaseModel):
    """
    State of Firefly engine.
    """

    ...
