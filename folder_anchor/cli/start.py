from prompt_toolkit.shortcuts import radiolist_dialog


def ask_what_to_do():
    result = radiolist_dialog(
        values=[
            ("inherit",
             "Inherit anchor (_links of this anchor will be added to this folder)."),
            ("part_of",
             "Make file or folder part of anchor (folders that inherit the anchor will have _links to this file/folder)."),
            ("edit", "Edit data of this folder."),
            ("delete", "Clear anchor data."),
            ("scan", "Scan folders and refresh cache.")
        ],
        title="Folder Anchor",
        text="Please choose an option:",
    ).run()
    return result
