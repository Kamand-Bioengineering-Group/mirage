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
    Base class for V1 type entities. This class provides a staging mechanism to
    store the changes made to the entity before syncing. Also, it registers the
    entities given in arbitrary nested structures through fields and syncs them
    all at once through a cascade of `sync` calls.

    Explanation:
    ------------
    - `__setattr__`:
        - If the attribute is a model field, it is stored in the `_stage`.
        - Otherwise, it is set as a regular attribute.
    - `_scan_entities`:
        - Recursively scans the given structure for entities.

    Attributes:
    -----------
    - `_stage`:
        - A dictionary to store the staged attributes.
    - `_regen`:
        - A list to store the registered entities.

    Methods:
    --------
    - `_scan_entities`:
        - Recursively scans the structure for entities.
    - `_register_entities`:
        - Registers the entities found in the fields of the entity.
    - `sync`:
        - Syncs the staged attributes.
        - Syncs the registered entities.
        - Clears the `_stage`.
    """
    def __init__(self, **data):
        super().__init__(**data)
        self._stage = {}
        self._regen = []
        self._register_entities()

    def __setattr__(self, name, value):
        if self.model_fields.get(name):
            self._stage[name] = value
        else:
            super().__setattr__(name, value)

    def _scan_entities(self, structure):
        if isinstance(structure, EntityV1):
            yield structure
        if isinstance(structure, dict):
            for value in structure.values():
                yield from self._scan_entities(value)
        elif isinstance(structure, (list, tuple)):
            for item in structure:
                yield from self._scan_entities(item)

    def _register_entities(self):
        self._regen.extend(
            entity
            for field, structure in self.__dict__.items()
            if field not in ("_stage", "_regen")
            for entity in self._scan_entities(structure)
        )

    def sync(self):
        for key, value in self._stage.items():
            super().__setattr__(key, value)
        for ren in self._regen:
            ren.sync()
        self._stage.clear()
