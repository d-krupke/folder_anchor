from actions.base import Action
from utils.cache import Cache
from utils.global_settings import GlobalSettings


class RebuildCacheAction(Action):
    def execute(self, cache: Cache, global_settings: GlobalSettings):
        raise NotImplementedError()
