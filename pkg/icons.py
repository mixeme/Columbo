from PyQt5.QtGui import QIcon


class IconsLoader:
    singleton = None

    def __init__(self) -> None:
        super().__init__()
        self.folder = QIcon.fromTheme("folder", QIcon("icons/folder.png"))
        self.file = QIcon.fromTheme("text-x-generic", QIcon("icons/file.png"))
        IconsLoader.singleton = self
