import os

from prompt_toolkit import prompt
from prompt_toolkit.completion import PathCompleter
from prompt_toolkit.validation import Validator, ValidationError


class PathValidator(Validator):
    def __init__(self, root: str):
        self.root = root

    def validate(self, document):
        path = document.text
        abs_path = path if os.path.isabs(path) else os.path.join(self.root, path)
        if not os.path.exists(abs_path):
            raise ValidationError(message=f"{abs_path} is not valid path.")


class AskForLocalPath:
    def __init__(self, root=None, prompt_text=None):
        self.root = root if root else os.getcwd()
        self.prompt_text = prompt_text if prompt_text else "Enter path (autocomplete with tab):"
        self._validator = PathValidator(self.root)

    def ask(self):
        path = prompt(self.prompt_text, completer=PathCompleter(),
                      validator=self._validator)
        return path
