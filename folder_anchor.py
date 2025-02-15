# !/usr/bin/python3
import argparse
import json
import os

FILE_NAME = ".folder_anchor.json"
DRY_RUN = False

class AnchorFile:
    pass


class MakePartOfAnchorRequest:
    def __init__(self, make_part_of_data, file_data):
        self._link_data = make_part_of_data
        self._parent_data = file_data

    def _get_entry(self, entry):
        if entry in self._link_data:
            return self._link_data[entry]
        if entry in self._parent_data:
            return self._parent_data[entry]
        return None

    def get_anchor_name(self):
        if "anchor" in self._link_data:
            return self._link_data["anchor"]
        return None

    def get_subdir(self):
        return self._get_entry("subdir")

    def get_name(self):
        if "name" in self._link_data:
            return self._link_data["name"]
        if "file" in self._link_data:
            return os.path.basename(self._link_data["file"])
        if "name" in self._parent_data:
            return self._parent_data["name"]
        return None

    def get_origin_path(self):
        path = self._parent_data["path"]
        if "file" in self._link_data:
            path = os.path.join(path, self._link_data["file"])
        return path


class Anchor:
    def __init__(self, data, path):
        self._name = data["name"]
        self._path = path

    def get_name(self):
        return self._name

    def get_path(self):
        return self._path


def create_link(make_part_of: MakePartOfAnchorRequest, anchor: Anchor):
    if make_part_of.get_subdir():
        link = os.path.join(anchor.get_path(), make_part_of.get_subdir(),
                            make_part_of.get_name())
    else:
        link = os.path.join(anchor.get_path(), make_part_of.get_name())

    # The link target has to be relative to its position
    link_target = os.path.relpath(make_part_of.get_origin_path(), os.path.dirname(link))
    create_parent_directories(link)
    ln(link_to=link_target, link_name=link)


def parse_json(path: str):
    try:
        with open(path, "r") as f:
            data = json.load(f)
            return data
    except Exception as e:
        print("Could not parse", path, e)
    return None


def parse_folder_anchor_file(path: str):
    data = parse_json(path)
    if data:
        data["path"] = os.path.dirname(path)
        if "name" not in data:
            data["name"] = data["path"].split("/")[-1]
    return data


def find_folder_anchor_files(base_dir="."):
    folder_anchor_files = []
    for root, dirs, files in os.walk(base_dir, topdown=False):
        path = os.path.join(root, FILE_NAME)
        if os.path.isfile(path):
            data = parse_folder_anchor_file(path)
            if data:
                folder_anchor_files.append(data)
    return folder_anchor_files


def get_anchors(smart_link_files: list):
    anchor_files = dict()
    for data in smart_link_files:
        if "anchor" in data:
            for anchor_data in make_list(data["anchor"]):
                anchor = Anchor(data=anchor_data, path=data["path"])
                if anchor.get_name() not in anchor_files:
                    anchor_files[anchor.get_name()] = []
                anchor_files[anchor.get_name()].append(anchor)
    return anchor_files


def get_auto_links(make_part_of_files: list):
    auto_links = []
    for data in make_part_of_files:
        if "make_part_of" in data:
            for make_part_of_data in make_list(data["make_part_of"]):
                alt = MakePartOfAnchorRequest(make_part_of_data=make_part_of_data,
                                              file_data=data)
                auto_links.append(alt)
    return auto_links


def create_parent_directories(target):
    if not os.path.exists(os.path.dirname(target)):
        os.makedirs(os.path.dirname(target))


def update_ln(link_to: str, link_name: str):
    if not os.path.islink(link_name):
        print("Tried to create to create link", link_name, "->", link_to,
              "but there exists already a file/folder with the same name")
        return
    path_of_old_link = os.path.realpath(os.readlink(link_name))
    if path_of_old_link != os.path.realpath(link_to):
        if os.path.exists(path_of_old_link):
            print("Tried to link", link_name, "->", link_to,
                  "but it already points to", path_of_old_link)
            return
        if not DRY_RUN:
            os.unlink(link_name)
            os.symlink(link_to, link_name)
        print("Updated:", link_name, "->", link_to)


def ln(link_to: str, link_name: str):
    full_link_destination = os.path.join(os.path.dirname(link_name), link_to )
    if not os.path.exists(full_link_destination):
        print("Tried to create broken link", link_name, "->", link_to)
        return
    if os.path.realpath(full_link_destination) == os.path.realpath(link_name):
        # The folder itself is at the position. No need to create link.
        return
    try:
        if not DRY_RUN:
            os.symlink(link_to, link_name)
        print("Created:", link_name, "->", link_to)
    except FileExistsError as fee:
        update_ln(link_to, link_name)


def make_list(l):
    if isinstance(l, list):
        return l
    return [l]


def process_files(folder_anchor_datas):
    anchors = get_anchors(folder_anchor_datas)
    auto_links = get_auto_links(folder_anchor_datas)
    for auto_link in auto_links:
        if auto_link.get_anchor_name() not in anchors:
            print("Could not find anchor", auto_link.get_anchor_name(), "for",
                  auto_link.get_origin_path())
            continue
        for anchor in anchors[auto_link.get_anchor_name()]:
            create_link(auto_link, anchor)


def print_anchors(path: str):
    anchors = get_anchors(find_folder_anchor_files(path))
    for anchor, data in anchors.items():
        print(anchor, ":", end="\t")
        for d in data:
            print(d.get_path(), end=" ")
        print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="folder_anchor is a tool for automatically"
                    "creating symbolic links based on local"
                    "json configuration files. See "
                    "https://github.com/d-krupke/folder_anchor for more.")
    parser.add_argument('-a', '--anchor', metavar="ANCHOR_NAME", dest="anchor",
                        help="Create anchor")
    parser.add_argument('-p', '--make_part_of', metavar="ANCHOR_NAME",
                        dest="make_part_of",
                        help="Make this folder a part of an anchor folder by creating"
                             " a symbolic link in it")
    parser.add_argument('--subdir', metavar="./PATH", dest="subdir",
                        help="Creates a subdir at the corresponding anchor")
    parser.add_argument('--name', help='Name of the link (if different from folder name)')
    parser.add_argument('--file', metavar="./FILE", dest="file",
                        help="Don't link to the folder but this file "
                             "(file can also be another folder).")
    parser.add_argument('-s', '--scan', dest="scan", metavar="PATH",
                        help="Scans the directory and adds missing symbolic links.")
    parser.add_argument('-l', '--list_anchors', dest="list_anchors", metavar="PATH",
                        help="Lists all anchors")
    parser.add_argument('--dry', action="store_true", help="Dry run. Print changes but don't make them.")
    args = parser.parse_args()

    if args.dry:
        DRY_RUN = True

    if args.anchor or args.make_part_of:
        data = parse_json(FILE_NAME) if os.path.exists(FILE_NAME) else None
        if not data:
            data = dict()

        if args.anchor:
            if "anchor" in data:
                data["anchor"] = make_list(data["anchor"])
            else:
                data["anchor"] = []
            data["anchor"].append({"name": args.anchor})
        if args.make_part_of:
            if "make_part_of" in data:
                data["make_part_of"] = make_list(data["make_part_of"])
            else:
                data["make_part_of"] = []
            make_part_of = {"anchor": args.make_part_of}
            if args.subdir:
                make_part_of["subdir"] = args.subdir
            if args.name:
                make_part_of["name"] = args.name
            if args.file:
                make_part_of["file"] = args.file
            data["make_part_of"].append(make_part_of)

        with open(FILE_NAME, "w") as f:
            f.write(json.dumps(data))

    if args.list_anchors:
        print_anchors(args.list_anchors)

    if args.scan:
        process_files(find_folder_anchor_files(os.path.expanduser(args.scan)))
