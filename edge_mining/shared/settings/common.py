"""Collection of Common Objects for the Settings shared domain of the Edge Mining application."""

from enum import StrEnum

class PersistenceAdapter(StrEnum):
    IN_MEMORY = "in_memory"
    SQLITE = "sqlite"

class EnergyMonitorAdapter(StrEnum):
    DUMMY = "dummy"
    HOME_ASSISTANT = "home_assistant"

class MinerControllerAdapter(StrEnum):
    DUMMY = "dummy"

class ForecastProviderAdapter(StrEnum):
    DUMMY = "dummy"
    HOME_ASSISTANT = "home_assistant"

class HomeForecastProviderAdapter(StrEnum):
    DUMMY = "dummy"

class NotificationAdapter(StrEnum):
    DUMMY = "dummy"
    TELEGRAM = "telegram"

class PerformaceTrackerAdapter(StrEnum):
    DUMMY = "dummy"

class ExternalServiceAdapter(StrEnum):
    HOME_ASSISTANT = "home_assistant"