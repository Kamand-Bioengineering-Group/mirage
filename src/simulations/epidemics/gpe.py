# ---INFO-----------------------------------------------------------------------
"""
Module for geo-political entities.
"""

__all__ = [
    "Country",
    "Locus",
]


# ---DEPENDENCIES---------------------------------------------------------------
import typing as tp
import pydantic as pyd


# ---COUNTRY--------------------------------------------------------------------
class Locus(pyd.BaseModel):
    name: str
    lat: float
    lon: float
    susceptible: int
    infected: int
    recovered: int
    area: int
    airports: tp.List[tp.Dict[str, str | int]] | None
    ports: tp.List[tp.Dict[str, str | int]] | None
    economic_zones: tp.List[tp.Dict[str, str | int]] | None
    tourist_zones: tp.List[tp.Dict[str, str | int]] | None

class Country(pyd.BaseModel):
    name: str
    B: float
    C: float
    E: float
    A: float
    Ds: float
    Di: float
    Dr: float
    gdp: float
    health_resource_stockpile: float
    sanitation_equipment_stockpile: float
    human_welfare_resource: float
    happiness_index: float
    general_hospitals: int
    procedure_resistance: float
    cleanliness_index: float
    base_death_rate: float
    vaccine_components: tp.List[dict]
    loci: tp.List[Locus]

