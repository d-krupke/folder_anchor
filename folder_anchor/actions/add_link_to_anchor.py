import os

from actions.base import Action
from utils.anchor_linker import AnchorLinker
from utils.cache import Cache
from utils.global_settings import GlobalSettings


class AddLinkToAnchorAction(Action):
    def __init__(self, anchor_name, link_name, link_target):
        self.anchor_name = anchor_name
        if not os.path.isabs(link_target):
            link_target = os.path.abspath(link_target)
        assert os.path.exists(link_target)
        self.link_name = link_name
        self.link_target = link_target

    def execute(self, cache: Cache, global_settings: GlobalSettings):
        anchor = cache[self.anchor_name]
        with cache.get_folder_settings(os.getcwd()) as folder_settings:
            folder_settings.make_part_of_anchor(anchor_name=self.anchor_name,
                                                link_name=self.link_name,
                                                link_target=self.link_target)
            cache.update(folder_settings)
            linker = AnchorLinker(cache=cache, settings=global_settings)
            for path in cache.get_folders_inheriting_anchor(self.anchor_name):
                linker.create_links(path, anchor)
