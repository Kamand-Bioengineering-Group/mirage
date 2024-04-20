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
from ...entities import EntityV1


# ---COUNTRY--------------------------------------------------------------------
class Locus(EntityV1):
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
    susceptible: float
    infected: float
    recovered: float
    dead: float
    area: float
    quarantine_facilities: int
    general_hospitals: int
    vaccine_distribution_centers: int
    airports: tp.List[tp.Dict[str, str | int | float]] | None
    ports: tp.List[tp.Dict[str, str | int | float]] | None
    economic_zones: tp.List[tp.Dict[str, str | int | float]] | None
    tourist_zones: tp.List[tp.Dict[str, str | int | float]] | None


class Country(EntityV1):
    name: str
    gdp: float
    health_resource_stockpile: float
    sanitation_equipment_stockpile: float
    human_welfare_resource: float
    happiness_index: float
    procedure_resistance: float
    cleanliness_index: float
    disease_research_center: int
    vaccine_research_center: int
    vaccines_stock: tp.List[tp.Dict[str, str | int | float]] | None
    loci: tp.List[Locus]
