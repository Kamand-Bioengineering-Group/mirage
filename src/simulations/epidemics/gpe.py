# ---INFO-----------------------------------------------------------------------
"""
Module for geo-political entities.
"""

__all__ = [
    "Country",
    "Locus",
]


# ---DEPENDENCIES---------------------------------------------------------------
from typing import List, Dict, Union
from pydantic import BaseModel

class Locus(BaseModel):
    name: str
    lat: float
    lon: float
    susceptible: int
    infected: int
    recovered: int
    area: int
    airports: List[Dict[str, Union[str, int]]]
    ports: List[Dict[str, Union[int, str]]]
    economic_zones: List[Dict[str, int]]
    tourist_zones: List[Dict[str, int]]

class Country(BaseModel):
    name: str
    B: float
    C: float
    E: float
    A: float
    Ds: float
    Di: float
    Dr: float
    gdp: int
    health_resource_stockpile: float
    sanitation_equipment_stockpile: int
    human_welfare_resource: float
    happiness_index: float
    general_hospitals: int
    procedure_resistance: float
    cleanliness_index: float
    base_death_rate: float
    vaccine_components: List[Dict[str, Union[str, int, float]]]
    loci: List[Locus]

