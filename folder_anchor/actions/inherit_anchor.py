import os

from actions.base import Action
from utils.anchor_linker import AnchorLinker
from utils.cache import Cache
from utils.global_settings import GlobalSettings


class InheritAnchorAction(Action):
    def __init__(self, folder_path: str, anchor_name: str):
        self.folder_path = os.path.abspath(folder_path)
        assert os.path.exists(self.folder_path)
        self.anchor_name = anchor_name

    def execute(self, cache: Cache, global_settings: GlobalSettings):
        with cache.get_folder_settings(self.folder_path) as folder_settings:
            folder_settings.add_anchor_inheritance(self.anchor_name)
            AnchorLinker(cache, global_settings).create_links(folder_settings.folder_path,
                                                              cache[self.anchor_name])
            cache.monitor_folder(self.folder_path)
