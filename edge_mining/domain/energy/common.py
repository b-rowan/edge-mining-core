"""Collection of Common Objects for the Energy System Monitoring domain of the Edge Mining application."""

from dataclasses import dataclass
from enum import Enum

@dataclass(frozen=True)
class EnergySourceType(Enum):
    SOLAR = "solar"
    WIND = "wind"
    GRID = "grid"
    #IDROELECTRIC = "hydroelectric" # 😃 future use​
    OTHER = "other"