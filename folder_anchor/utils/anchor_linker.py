import os
import typing

from utils.anchor import Anchor
from utils.cache import Cache
from utils.global_settings import GlobalSettings


class LinkCreator:
    def __init__(self, cache: Cache, dry: bool = False, verbose: bool = False):
        self.cache = cache
        self.dry = dry
        self.verbose = verbose

    def __call__(self, link_path, link_target):
        if self.dry:
            print(f"Would create link_name {link_path}->{link_target}.")
            return
        self.cache.add_created_link(link=link_path, target=link_target)
        if os.path.exists(link_path):
            if self.verbose:
                print(f"Unlinked {link_path}")
            os.unlink(link_path)
        os.symlink(link_target, link_path)
        if self.verbose:
            print(f"Created link_name {link_path}->{link_target}.")


class AnchorLinker:
    """
    Creates the links for the _anchors.
    """

    def __init__(self, cache: Cache, settings: GlobalSettings, dry: bool = False):
        """
        :param settings: Settings are currently not used but there are some things that
                            might be decided by settings.
        """
        self._settings = settings
        self._dry = dry
        self._link_creator = LinkCreator(cache, dry=dry)

    def _create_parent_directories_for_link(self, link_path):
        """
        Creates the folder structure for the link_name if it does not exist yet.
        :param link_path:
        :return:
        """
        folder_path = os.path.dirname(link_path)
        if os.path.exists(folder_path):
            if os.path.isfile(folder_path):
                raise FileExistsError()
        os.makedirs(folder_path, exist_ok=True)

    def _create_link(self, link_path, link_target):
        link_folder = os.path.dirname(link_path)
        if not os.path.exists(os.path.join(link_folder, link_target)):
            raise FileNotFoundError()
        if os.path.exists(link_path):
            if not os.path.islink(link_path):
                # If there is already a file where we want to create a link_name, something
                # is bad. We can overwrite links but we don't want to replace real files
                # by links as this could lead to data loss.
                raise FileExistsError()
            old_target = os.path.realpath(os.readlink(link_path))
            if old_target != os.path.realpath(link_target):
                self._link_creator(link_path=link_path, link_target=link_target)
        else:
            self._link_creator(link_path=link_path, link_target=link_target)

    def create_links(self, path: str, anchor: Anchor,
                     protect: typing.List[Anchor] = None) -> typing.List[str]:
        """
        Creates the links of an anchor for a path.
        :param path: The path which should get the links of the anchor.
        :param anchor: The anchor that should be applied to the path.
        :param protect: A list with _anchors whose links are not overwritten.
                        Possibly needed in multi-inheritance problems.
        :return: A list with all the created links.
        """
        created_links = []
        protect = protect if protect else []
        for link, link_target in anchor:
            print(link, link_target)
            if any((link in a for a in protect)):
                continue
            link_path = os.path.join(path, link)
            link_folder = os.path.dirname(link_path)
            link_target = os.path.relpath(link_target, start=link_folder)
            try:
                self._create_parent_directories_for_link(link_path)
                self._create_link(link_path, link_target)
                created_links.append(link_path)
            except FileExistsError as fee:
                print(
                    f"Warning: Could not create [{anchor.name}]{link}->{link_target} for {path}. File exists.")
            except FileNotFoundError as fnfe:
                print(
                    f"Warning: Did not create [{anchor.name}]{link}->{link_target} for {path}. Target does not exist.")
        return created_links
