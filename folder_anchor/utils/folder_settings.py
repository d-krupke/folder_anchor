import json
import os

import typing

from version import __version__


class PartOfRelationship:
    def __init__(self, anchor_name, link_name, target):
        self.anchor_name = anchor_name
        self.link_name = link_name
        assert os.path.isabs(target)
        self.link_target = target
        if not os.path.exists(self.link_target):
            raise FileNotFoundError(self.link_target)

    def to_dict(self, root=None):
        link_target = os.path.relpath(self.link_target,
                                      start=root) if root else self.link_target
        return {"anchor": self.anchor_name, "link_name": self.link_name,
                "link_target": link_target}


class FolderSettings:
    """
    Saves the settings of a specific folder.
    """

    def __init__(self, folder_path, data=None):
        folder_path = os.path.abspath(folder_path)
        self.folder_path = folder_path
        if not os.path.exists(folder_path):
            raise FileNotFoundError(folder_path)
        self.anchor_inheritances = []
        self.part_of_relationships: typing.List[PartOfRelationship] = []
        self._json_path = os.path.join(folder_path, ".folder_anchor.json")
        if data is None:
            if os.path.exists(self._json_path):
                with open(self._json_path, 'r') as f:
                    data = json.load(f)
            else:
                data = {"part_of": [], "inherits": []}
        for d in data["part_of"]:
            self.part_of_relationships.append(
                PartOfRelationship(d["anchor"], d["link_name"],
                                   os.path.join(folder_path, d["link_target"])))
        self.anchor_inheritances = data["inherits"]

    def add_anchor_inheritance(self, anchor_name):
        if anchor_name not in self.anchor_inheritances:
            self.anchor_inheritances.append(anchor_name)

    def remove_anchor_inheritance(self, anchor_name):
        self.anchor_inheritances.remove(anchor_name)

    def _deduce_link_name_from_target(self, link_target):
        if os.path.normpath(link_target) == os.path.normpath(self.folder_path):
            return os.path.normpath(self.folder_path).split("/")[-1]
        else:
            return os.path.relpath(link_target, start=self.folder_path)

    def make_part_of_anchor(self, anchor_name, link_name=None, link_target=None):
        """
        :param anchor_name:
        :param link_name: anchor/link_name -> link_target. If none, the whole folder will be used.
        :param link_target: anchor/link_target -> source. If none, the source will be used. If the
                        source is the whole folder, the folder name is used.
        :return: None
        """
        link_target = link_target if link_target and link_target else self.folder_path
        link_target = os.path.abspath(
            os.path.relpath(link_target, start=self.folder_path))
        if not link_name:
            link_name = self._deduce_link_name_from_target(link_target)
        self.part_of_relationships.append(
            PartOfRelationship(anchor_name, link_name=link_name, target=link_target))

    def to_dict(self):
        data = {
            "part_of": [p.to_dict(self.folder_path) for p in self.part_of_relationships],
            "inherits": self.anchor_inheritances,
            "version": __version__}
        return data

    def write(self):
        with open(self._json_path, 'w') as f:
            json.dump(self.to_dict(), f)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.write()
