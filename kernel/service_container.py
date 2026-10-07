from kernel.services.cache import CacheService
from kernel.services.logger import LoggerService
from kernel.services.config_reader import ConfigReader
from kernel.services.translator import TranslatorService
from kernel.database import DatabaseService  # ← only this, remove kernel.services.database


class ServiceContainer:
    def __init__(self):
        self.config = ConfigReader()
        self.logger = LoggerService()
        self.db = DatabaseService()        
        self.cache = CacheService()
        self.translator = TranslatorService()



    def init_db(self, config: dict) -> None:
        """Call after config is loaded."""
        self.db.setup(config)


    async def init(self):
        self.config.load()
        self.logger.setup()
        await self.db.connect()
        await self.cache.connect()
        self.logger.info("All services initialized")

    async def dispose(self):
        await self.db.disconnect()
        await self.cache.disconnect()
        self.logger.info("All services disposed")
