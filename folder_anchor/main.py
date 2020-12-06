import os

from cli.add_link_to_anchor_prompt import AddLinkToAnchorPrompt
from cli.anchor_inheritance import AnchorInheritancePrompt
from cli.start import ask_what_to_do
from utils.cache import Cache
from utils.folder_settings import FolderSettings
from utils.global_settings import GlobalSettings

if __name__ == "__main__":
    with Cache() as cache:
        task = ask_what_to_do()
        path = os.getcwd()
        global_settings = GlobalSettings()
        if task == "inherit":
            AnchorInheritancePrompt(cache, global_settings).prompt().execute(cache,
                                                                             global_settings)
        elif task == "part_of":
            AddLinkToAnchorPrompt(cache, global_settings).prompt().execute(cache,
                                                                           global_settings)
