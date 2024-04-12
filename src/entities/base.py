# ---INFO-----------------------------------------------------------------------
"""
Base classes for entities.
"""	

# TODO: Implement the EntityV1 class if required.

__all__ = [
    "EntityV1",
]


# ---DEPENDENCIES---------------------------------------------------------------
import pydantic as pyd


# ---ENTITYV1-------------------------------------------------------------------
class EntityV1(pyd.BaseModel):
    """
    Base class for V1 type entities. This is just a placeholder, EntityV1 should
    be a subclass of pyd.BaseModel.
    """
    ...