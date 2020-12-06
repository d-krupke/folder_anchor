import os

from prompt_toolkit import PromptSession
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.history import InMemoryHistory

from actions.inherit_anchor import InheritAnchorAction
from cli.ask_for_anchor import AskForAnchor
from utils.cache import Cache
from utils.global_settings import GlobalSettings


class AnchorInheritancePrompt:
    """
    Guides through the inheritance of an anchor.
    """

    def __init__(self, cache: Cache, global_settings: GlobalSettings):
        self._cache = cache
        self._global_settings = global_settings

    def prompt(self):
        anchor_name = AskForAnchor(self._cache).ask()
        return InheritAnchorAction(anchor_name=anchor_name,
                                   folder_path=os.getcwd())
