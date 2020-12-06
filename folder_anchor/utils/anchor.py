import os
import typing


class Anchor:
    """
    An anchor is an inheritance structure for a folder. If a applied to a folder, the
    folder will get links to the corresponding targets.
    For example
    ```python
    a = Anchor("test_anchor")
    a["sub/inherited_file_or_folder"]="/path/to/some/file/or/folder"
    ```
    will create for our folder '/our/folder' a link_name
    '/our/folder/sub/inherited_file_or_folder' to "/path/to/some/file/or/folder".
    """

    def __init__(self, name: str):
        self.name = name
        self._links = dict()

    def __getitem__(self, item: str):
        return self._links[item]

    def __setitem__(self, key: str, value: str):
        full_path = os.path.abspath(value)
        if not os.path.exists(full_path):
            raise ValueError(f"Path {full_path} does not exist.")
        if key in self._links and self._links[key] != value:
            print(f"Warning: Overwriting entry for {key}. "
                  f"Previously '{self._links[key]}', now '{value}'")
        self._links[key] = value

    def __iter__(self) -> typing.Iterable[typing.Tuple[str, str]]:
        for k, v in self._links.items():
            yield k, v


class AnchorJson:
    def dump(self, anchor: Anchor) -> dict:
        return {
            "name": anchor.name,
            "links": {str(link): str(target) for link, target in anchor}
        }

    def load(self, data: dict):
        a = Anchor(data["name"])
        for link, target in data["links"].items():
            a[link] = target
        return a
