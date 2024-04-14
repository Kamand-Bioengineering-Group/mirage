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
    B: float
    C: float
    E: float
    A: float
    Ds: float
    Di: float
    Dr: float
    lat: float
    lon: float
    name: str
    susceptible: int
    infected: int
    recovered: int
    area: int
    quarantine_facilities: int
    general_hospitals: int
    airports: tp.List[tp.Dict[str, str | int]] | None
    ports: tp.List[tp.Dict[str, str | int]] | None
    economic_zones: tp.List[tp.Dict[str, str | int]] | None
    tourist_zones: tp.List[tp.Dict[str, str | int]] | None

class Country(pyd.BaseModel):
    name: str
    gdp: int
    health_resource_stockpile: float
    sanitation_equipment_stockpile: float
    human_welfare_resource: float
    happiness_index: float
    procedure_resistance: float
    cleanliness_index: int
    disease_research_center: int
    vaccine_reseach_center: int
    base_birth_rate: float
    vaccine_center_details: tp.Dict[str, int]
    loci: tp.List[Locus]