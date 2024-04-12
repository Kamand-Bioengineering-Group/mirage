# ---INFO-----------------------------------------------------------------------
"""
Module for simulating epidemics.
"""	

__all__ = [
    "engine",
    "gpe",
]


# ---DEPENDENCIES---------------------------------------------------------------
from . import engine, gpe
from typing import List, Dict, Union
from pydantic import BaseModel
import yaml
import pydantic