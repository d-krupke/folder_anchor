import os
import typing
import json

from utils.anchor import AnchorJson, Anchor
from utils.folder_settings import FolderSettings


class Cache:
    def __init__(self, path=os.path.expanduser("~/.folder_anchor.cache.json")):
        self.path = path
        self._anchors = dict()
        self.monitored_folders = []
        self._cached_folder_settings = dict()
        self.links = dict()
        try:
            with open(path, 'r') as f:
                data = json.load(f)
                self._read_anchors_from_data(data)
                self.monitored_folders = data.get("monitored_folders", [])
        except FileNotFoundError:
            pass
        except json.decoder.JSONDecodeError as je:
            print("The cache file has been corrupted:",path)

    def _read_anchors_from_data(self, data):
        j = AnchorJson()
        for anchor_data in data["anchors"]:
            a = j.load(anchor_data)
            self._anchors[a.name] = a

    def __getitem__(self, item) -> Anchor:
        return self._anchors.setdefault(item, Anchor(item))

    def add_created_link(self, link, target):
        self.links[link] = target

    @property
    def anchors(self):
        for name, anchor in self._anchors.items():
            yield anchor

    def get_folders_inheriting_anchor(self, anchor_name) -> typing.Iterable[str]:
        """
        Returns the paths of the folders that are inheriting the anchor.
        :param anchor_name:
        :return:
        """
        for f in self.monitored_folders:
            fs = self.get_folder_settings(f)
            if anchor_name in fs.anchor_inheritances:
                yield f

    def add_anchor(self, anchor: Anchor):
        self._anchors[anchor.name] = anchor

    def monitor_folder(self, path: str):
        """
        Add the folder to the monitored folders that can quickly be rescanned.
        :param path: The path of the folder to be observed.
        :return:
        """
        path = os.path.normpath(path)
        assert os.path.exists(path), "Folders to be monitored, should exist."
        if path not in self.monitored_folders:
            self.monitored_folders.append(path)

    def update(self, folder_settings: FolderSettings):
        for por in folder_settings.part_of_relationships:
            self[por.anchor_name][por.link_name] = por.link_target

    def get_folder_settings(self, path: str):
        path = os.path.normpath(path)
        try:
            return self._cached_folder_settings[path]
        except KeyError as ke:
            fs = FolderSettings(path)
            self.monitor_folder(path)
            return self._cached_folder_settings.setdefault(path, fs)

    def write(self):
        data = dict()
        j = AnchorJson()
        data["anchors"] = [j.dump(a) for a in self._anchors.values()]
        data["anchor_inheritances"] = {name: list(self.get_folders_inheriting_anchor(name)) for
                                       name in self._anchors.keys()}
        data["monitored_folders"] = self.monitored_folders
        with open(self.path, "w") as f:
            json.dump(data, f)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.write()
