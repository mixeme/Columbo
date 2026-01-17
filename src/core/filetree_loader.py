from core import file


class FileTreeLoader:
    def __init__(self, path: str) -> None:
        self.path = path
        self.dirs = []
        self.files = []

    def reset(self) -> None:
        self.dirs = []
        self.files = []

    def load(self) -> None:
        self.dirs, self.files = file.list_dir(self.path)


