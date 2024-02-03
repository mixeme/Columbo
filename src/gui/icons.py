from os import path

from PyQt5.QtGui import QIcon


class IconsLoader:
    singleton = None

    def __init__(self, project_home) -> None:
        super().__init__()
        self.folder = QIcon.fromTheme("folder", QIcon(path.join(project_home, "icons/folder.png")))
        self.file = QIcon.fromTheme("text-x-generic", QIcon(path.join(project_home, "icons/file.png")))
        IconsLoader.singleton = self
