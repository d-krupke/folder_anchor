import typing
from prompt_toolkit import PromptSession
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.history import InMemoryHistory

from utils.cache import Cache


class AskForAnchor:
    def __init__(self, cache: Cache):
        self._cache = cache

    def ask(self) -> typing.Optional[str]:
        history = InMemoryHistory()
        for anchor in self._cache.anchors:
            history.append_string(anchor.name)
        session = PromptSession(
            history=history,
            auto_suggest=AutoSuggestFromHistory(),
            enable_history_search=True,
        )
        existing_anchors = [a.name for a in self._cache.anchors]
        print("[Already existing _anchors are:", ", ".join(existing_anchors), "]")
        while True:
            try:
                anchor_name = session.prompt("Enter name of anchor: ")
                return anchor_name
            except KeyboardInterrupt:
                return None
