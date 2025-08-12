"""Bootstrap operations"""

import os

from edge_mining.domain.energy.ports import (
    EnergySourceRepository,
    EnergyMonitorRepository,
)
from edge_mining.domain.miner.ports import MinerRepository
from edge_mining.domain.forecast.ports import ForecastProviderRepository
from edge_mining.domain.home_load.ports import (
    HomeForecastProviderPort,
    HomeLoadsProfileRepository,
    HomeForecastProviderRepository,
)

from edge_mining.domain.notification.ports import NotifierRepository
from edge_mining.domain.policy.ports import OptimizationPolicyRepository
from edge_mining.domain.performance.ports import (
    MiningPerformanceTrackerRepository
)
from edge_mining.domain.optimization_unit.ports import EnergyOptimizationUnitRepository

from edge_mining.adapters.infrastructure.persistence.sqlite import BaseSqliteRepository

from edge_mining.adapters.domain.energy.repositories import (
    InMemoryEnergyMonitorRepository,
    InMemoryEnergySourceRepository,
    SqliteEnergyMonitorRepository,
    SqliteEnergySourceRepository,
)
from edge_mining.adapters.domain.miner.repositories import (
    InMemoryMinerRepository,
    InMemoryMinerControllerRepository,
    SqliteMinerRepository,
    SqliteMinerControllerRepository,
)
from edge_mining.adapters.domain.forecast.repositories import (
    InMemoryForecastProviderRepository,
    SqliteForecastProviderRepository,
)
from edge_mining.adapters.domain.home_load.repositories import (
    InMemoryHomeLoadsProfileRepository,
    SqliteHomeLoadsProfileRepository,
    InMemoryHomeForecastProviderRepository,
    SqliteHomeForecastProviderRepository,
)
from edge_mining.adapters.domain.notification.repositories import (
    InMemoryNotifierRepository,
    SqliteNotifierRepository,
)
from edge_mining.adapters.domain.optimization_unit.repositories import (
    InMemoryOptimizationUnitRepository,
    SqliteOptimizationUnitRepository,
)
from edge_mining.adapters.domain.policy.repositories import (
    InMemoryOptimizationPolicyRepository,
    SqliteOptimizationPolicyRepository,
    YamlOptimizationPolicyRepository,
)
from edge_mining.adapters.domain.performance.repositories import (
    InMemoryMiningPerformanceTrackerRepository,
    SqliteMiningPerformanceTrackerRepository,
)
from edge_mining.adapters.domain.user.repositories import (
    InMemorySettingsRepository,
    SqliteSettingsRepository,
)
from edge_mining.adapters.infrastructure.external_services.repositories import (
    InMemoryExternalServiceRepository,
    SqliteExternalServiceRepository,
)

from edge_mining.application.interfaces import SunFactoryInterface
from edge_mining.adapters.infrastructure.sun.factories import AstralSunFactory

from edge_mining.shared.settings.common import PersistenceAdapter

from edge_mining.shared.logging.port import LoggerPort
from edge_mining.shared.settings.settings import AppSettings
from edge_mining.shared.settings.ports import SettingsRepository
from edge_mining.shared.external_services.ports import ExternalServiceRepository
from edge_mining.shared.infrastructure import PersistenceSettings, Services

from edge_mining.application.services.miner_action_service import MinerActionService
from edge_mining.application.services.configuration_service import ConfigurationService
from edge_mining.application.services.optimization_service import OptimizationService
from edge_mining.application.services.adapter_service import AdapterService


def configure_persistence(
    logger: LoggerPort, settings: AppSettings
) -> PersistenceSettings:
    """
    Configures the persistence layer based on the settings.
    """
    logger.debug("Configuring persistence...")

    persistence_adapter: PersistenceAdapter = PersistenceAdapter(
        settings.persistence_adapter
    )
    policies_persistence_adapter: PersistenceAdapter = PersistenceAdapter(
        settings.policies_persistence_adapter
    )

    # Initialize SQLite DB base repository if needed
    if PersistenceAdapter.SQLITE in [persistence_adapter, policies_persistence_adapter]:
        db_path = settings.sqlite_db_file
        db_dir = os.path.dirname(db_path)
        if db_dir and not os.path.exists(db_dir):
            logger.debug(f"Creating database directory: {db_dir}")
            os.makedirs(db_dir, exist_ok=True)

        logger.debug(f"Using SQLite persistence adapter (DB: {db_path}).")
        sqlite_db: BaseSqliteRepository = BaseSqliteRepository(
            db_path=db_path, logger=logger
        )

    # Initialize repositories based on the selected persistence adapter
    if persistence_adapter == PersistenceAdapter.IN_MEMORY:
        # Pre-populate in-memory repos with some test data (used for debug or development)
        energy_source_repo: EnergySourceRepository = InMemoryEnergySourceRepository()
        energy_monitor_repo: EnergyMonitorRepository = InMemoryEnergyMonitorRepository()
        miner_repo: MinerRepository = InMemoryMinerRepository()
        miner_controller_repo: InMemoryMinerControllerRepository = (
            InMemoryMinerControllerRepository()
        )
        forecast_provider_repo: ForecastProviderRepository = (
            InMemoryForecastProviderRepository()
        )
        notifier_repo: NotifierRepository = InMemoryNotifierRepository()
        mining_performance_tracker_repo: MiningPerformanceTrackerRepository = (
            InMemoryMiningPerformanceTrackerRepository()
        )
        settings_repo: SettingsRepository = InMemorySettingsRepository()
        home_profile_repo: HomeLoadsProfileRepository = (
            InMemoryHomeLoadsProfileRepository()
        )
        home_forecast_provider_repo: HomeForecastProviderPort = (
            InMemoryHomeForecastProviderRepository()
        )
        optimization_unit_repo: EnergyOptimizationUnitRepository = (
            InMemoryOptimizationUnitRepository()
        )
        external_service_repo: ExternalServiceRepository = (
            InMemoryExternalServiceRepository()
        )

        logger.debug("Using InMemory persistence adapters.")
    elif persistence_adapter == PersistenceAdapter.SQLITE:
        # Instantiate all SQLite repositories passing the DB base
        energy_source_repo: EnergySourceRepository = SqliteEnergySourceRepository(
            db=sqlite_db
        )
        energy_monitor_repo: EnergyMonitorRepository = SqliteEnergyMonitorRepository(
            db=sqlite_db
        )
        miner_repo: MinerRepository = SqliteMinerRepository(db=sqlite_db)
        miner_controller_repo: SqliteMinerControllerRepository = (
            SqliteMinerControllerRepository(db=sqlite_db)
        )
        forecast_provider_repo: ForecastProviderRepository = (
            SqliteForecastProviderRepository(db=sqlite_db)
        )
        notifier_repo: NotifierRepository = SqliteNotifierRepository(db=sqlite_db)
        mining_performance_tracker_repo: MiningPerformanceTrackerRepository = (
            SqliteMiningPerformanceTrackerRepository(db=sqlite_db)
        )
        settings_repo: SettingsRepository = SqliteSettingsRepository(db=sqlite_db)
        home_profile_repo: HomeLoadsProfileRepository = (
            SqliteHomeLoadsProfileRepository(db=sqlite_db)
        )
        home_forecast_provider_repo: HomeForecastProviderRepository = (
            SqliteHomeForecastProviderRepository(db=sqlite_db)
        )
        optimization_unit_repo: EnergyOptimizationUnitRepository = (
            SqliteOptimizationUnitRepository(db=sqlite_db)
        )
        external_service_repo: ExternalServiceRepository = (
            SqliteExternalServiceRepository(db=sqlite_db)
        )

        # user_repo: UserRepository = SqliteUserRepository(
        #   db_path=db_path, logger=logger
        # ) # If implemented
    else:
        raise ValueError(
            f"Unsupported persistence_adapter: {settings.persistence_adapter}"
        )

    # Initialize specific policies repositories based on the selected persistence adapter
    if policies_persistence_adapter == PersistenceAdapter.IN_MEMORY:
        policy_repo: OptimizationPolicyRepository = InMemoryOptimizationPolicyRepository()
        logger.debug("Using InMemory policies persistence adapter.")
    elif policies_persistence_adapter == PersistenceAdapter.SQLITE:
        policy_repo: OptimizationPolicyRepository = SqliteOptimizationPolicyRepository(
            db=sqlite_db
        )
        logger.debug("Using SQLite policies persistence adapter.")
    elif policies_persistence_adapter == PersistenceAdapter.YAML:
        policy_repo: OptimizationPolicyRepository = YamlOptimizationPolicyRepository(
            policies_directory=settings.yaml_policies_dir,
            logger=logger
        )
        logger.debug("Using YAML policies persistence adapter.")

    persistence_settings: PersistenceSettings = PersistenceSettings(
        energy_source_repo=energy_source_repo,
        energy_monitor_repo=energy_monitor_repo,
        miner_repo=miner_repo,
        miner_controller_repo=miner_controller_repo,
        forecast_provider_repo=forecast_provider_repo,
        home_profile_repo=home_profile_repo,
        home_forecast_provider_repo=home_forecast_provider_repo,
        notifier_repo=notifier_repo,
        optimization_unit_repo=optimization_unit_repo,
        policy_repo=policy_repo,
        mining_performance_tracker_repo=mining_performance_tracker_repo,
        external_service_repo=external_service_repo,
        settings_repo=settings_repo,
    )

    return persistence_settings


def configure_dependencies(logger: LoggerPort, settings: AppSettings) -> Services:
    """
    Performs Dependency Injection - Creates instances of adapters and services.
    Returns the main application services.
    """

    logger.debug("Configuring dependencies...")

    # --- Factories ---
    sun_factory: SunFactoryInterface = AstralSunFactory(
        latitude=settings.latitude,
        longitude=settings.longitude,
        timezone=settings.timezone
    )

    # --- Persistence ---
    persistence_settings: PersistenceSettings = configure_persistence(logger, settings)

    logger.debug("Instantiating application services...")

    adapter_service = AdapterService(
        energy_monitor_repo=persistence_settings.energy_monitor_repo,
        miner_controller_repo=persistence_settings.miner_controller_repo,
        notifier_repo=persistence_settings.notifier_repo,
        forecast_provider_repo=persistence_settings.forecast_provider_repo,
        home_forecast_provider_repo=persistence_settings.home_forecast_provider_repo,
        mining_performance_tracker_repo=persistence_settings.mining_performance_tracker_repo,
        external_service_repo=persistence_settings.external_service_repo,
        logger=logger,
    )

    optimization_service = OptimizationService(
        optimization_unit_repo=persistence_settings.optimization_unit_repo,
        energy_source_repo=persistence_settings.energy_source_repo,
        policy_repo=persistence_settings.policy_repo,
        miner_repo=persistence_settings.miner_repo,
        adapter_service=adapter_service,
        sun_factory=sun_factory,
        logger=logger,
    )

    miner_action_service = MinerActionService(
        adapter_service=adapter_service,
        miner_repo=persistence_settings.miner_repo,
        logger=logger,
    )

    config_service = ConfigurationService(
        persistence_settings=persistence_settings, logger=logger
    )

    services = Services(
        adapter_service=adapter_service,
        optimization_service=optimization_service,
        miner_action_service=miner_action_service,
        configuration_service=config_service,
    )

    logger.debug("Dependency configuration complete.")
    return services
