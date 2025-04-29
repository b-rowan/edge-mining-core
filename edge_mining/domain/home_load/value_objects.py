"""Collection of Value Objects for the Home Consumption Analytics domain of the Edge Mining application."""

from dataclasses import dataclass, field
from typing import Dict
from datetime import datetime

from edge_mining.domain.common import Watts, Timestamp, ValueObject

@dataclass(frozen=True)
class ConsumptionForecast(ValueObject):
    # Predicted consumption for a future period
    predicted_watts: Dict[Timestamp, Watts] = field(default_factory=dict)
    generated_at: Timestamp = field(default_factory=datetime.now)