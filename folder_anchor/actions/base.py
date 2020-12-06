from abc import ABC, abstractmethod

from utils.cache import Cache
from utils.global_settings import GlobalSettings


class Action(ABC):
    @abstractmethod
    def execute(self, cache: Cache, global_settings: GlobalSettings):
        pass
