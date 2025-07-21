"""Collection of Common Objects for the Mining Performace Analysis domain of the Edge Mining application."""

from typing import NewType

from edge_mining.domain.common import AdapterType

# Using Satoshi as the unit for rewards
Satoshi = NewType("Satoshi", int)

class MiningPerformanceTrackerAdapter(AdapterType):
    """Types of mining performace tracker adapter."""
    DUMMY = "dummy"
