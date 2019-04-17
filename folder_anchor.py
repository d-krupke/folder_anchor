# !/usr/bin/python
import argparse
import errno
import json
import os

FILE_NAME = ".folder_anchor.json"


class AnchorFile:
    pass


class AutoLinkTo:
    def __init__(self, auto_link_to_data, file_data):
        self._link_data = auto_link_to_data
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
        return self._get_entry("name")

    def get_origin_path(self):
        return self._parent_data["path"]


class Anchor:
    def __init__(self, data, path):
        self._name = data["name"]
        self._path = path

    def get_name(self):
        return self._name

    def get_path(self):
        return self._path


def create_link(auto_link_to: AutoLinkTo, anchor: Anchor):
    if auto_link_to.get_subdir():
        link = os.path.join(anchor.get_path(), auto_link_to.get_subdir(),
                            auto_link_to.get_name())
    else:
        link = os.path.join(anchor.get_path(), auto_link_to.get_name())

    # The link target has to be relative to its position
    link_target = os.path.relpath(auto_link_to.get_origin_path(), os.path.dirname(link))
    create_parent_directories(link)
    ln(link_to=link_target, link_name=link)


def read_smart_link_file(path: str):
    try:
        with open(path, "r") as f:
            data = json.load(f)
            data["path"] = os.path.dirname(path)
            if "name" not in data:
                data["name"] = data["path"].split("/")[-1]
            return data
    except Exception as e:
        print("Could not read smart link", path, e)
    return None


def find_smart_link_files(base_dir="."):
    smart_link_files = []
    for root, dirs, files in os.walk(base_dir, topdown=False):
        path = os.path.join(root, FILE_NAME)
        if os.path.isfile(path):
            data = read_smart_link_file(path)
            if data:
                smart_link_files.append(data)
    return smart_link_files


def get_anchors(smart_link_files: list):
    anchor_files = dict()
    for data in smart_link_files:
        if "anchor" in data:
            for anchor_data in make_list(data["anchor"]):
                anchor = Anchor(data=anchor_data, path=data["path"])
                if anchor.get_name() in anchor_files:
                    print("Multiple anchors of the same name!", data["path"],
                          anchor.get_name())
                else:
                    anchor_files[anchor.get_name()] = anchor
    return anchor_files


def get_auto_links(smart_link_files: list):
    auto_links = []
    for data in smart_link_files:
        if "auto_link_to" in data:
            for auto_link_to_data in make_list(data["auto_link_to"]):
                alt = AutoLinkTo(auto_link_to_data=auto_link_to_data, file_data=data)
                auto_links.append(alt)
    return auto_links


def create_parent_directories(target):
    if not os.path.exists(os.path.dirname(target)):
        try:
            os.makedirs(os.path.dirname(target))
        except OSError as exc:  # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise


def ln(link_to: str, link_name: str):
    if os.path.realpath(link_to) == os.path.realpath(link_name):
        # The folder itself is at the position. No need to create link.
        return
    try:
        os.symlink(link_to, link_name)
        print(link_name, "->", link_to)
    except FileExistsError as fee:
        if os.path.realpath(os.readlink(link_name)) != os.path.realpath(link_to):
            os.unlink(link_name)
            os.symlink(link_to, link_name)
            print(link_name, "->", link_to, "(updated)")


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
        create_link(auto_link, anchors[auto_link.get_anchor_name()])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="TODO")
    parser.add_argument('--create_anchor', help="Create anchor")
    parser.add_argument('--create_smart_link', help="Create smart link")
    parser.add_argument('--subdir')
    parser.add_argument('--scan')
    args = parser.parse_args()
    if args.create_anchor:
        with open(FILE_NAME, "w") as f:
            f.write("{\"anchor\":{\"name\": \"" + args.create_anchor + "\"}}")
    if args.create_smart_link:
        with open(FILE_NAME, "w") as f:
            subdir = ""
            if args.subdir:
                subdir = ", \"subdir\":\"" + args.subdir + "\""
            f.write(
                "{\"auto_link_to\":{\"anchor\": \"" + args.create_smart_link + "\"" + subdir + "}}")
    if args.scan:
        process_files(find_smart_link_files(os.path.expanduser(args.scan)))