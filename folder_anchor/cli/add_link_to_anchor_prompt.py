import os

from prompt_toolkit import prompt

from actions import AddLinkToAnchorAction
from cli.ask_for_anchor import AskForAnchor
from cli.ask_for_local_path import AskForLocalPath
from utils.cache import Cache
from utils.global_settings import GlobalSettings


class AddLinkToAnchorPrompt:
    def __init__(self, cache: Cache, global_settings: GlobalSettings):
        self._cache = cache
        self._global_settings = global_settings

    def prompt(self):
        anchor_name = AskForAnchor(self._cache).ask()
        print("What do you want to link?",
              "This file or folder will be linked to the anchor.",
              "If you enter nothing or '.', the current folder will be used.")
        link_target = AskForLocalPath().ask()
        print("How do you want to name this link?")
        link_name = link_target if link_target else os.getcwd().split("/")[-1]
        link_name = prompt("Enter link name (can contain folders):",
                           placeholder=link_name)
        return AddLinkToAnchorAction(anchor_name=anchor_name, link_name=link_name,
                              link_target=link_target)
