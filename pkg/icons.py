from os import path
import sys

from PyQt5.QtGui import QIcon


class IconsLoader:
    singleton = None

    def __init__(self) -> None:
        super().__init__()

        # Resolve project home folder
        if getattr(sys, 'frozen', False):
            # we are running in a bundle
            bundle_dir = sys._MEIPASS
        else:
            # we are running in a normal Python environment
            bundle_dir = path.dirname(path.dirname(path.abspath(__file__)))

        self.folder = QIcon.fromTheme("folder", QIcon(path.join(bundle_dir, "icons/folder.png")))
        self.file = QIcon.fromTheme("text-x-generic", QIcon(path.join(bundle_dir, "icons/file.png")))
        IconsLoader.singleton = self
