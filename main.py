#!/usr/bin/env python3
import os
import sys

from gui.ui import HistoryUI

from PyQt5.QtWidgets import QApplication


def __get_bundle_dir() -> str:
    # Resolve project home folder
    if getattr(sys, 'frozen', False):
        # We are running in a bundle
        return sys._MEIPASS
    else:
        # We are running in a normal Python environment
        return os.path.dirname(os.path.abspath(__file__))


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


# Set the custom exception handler
sys.excepthook = except_hook

if __name__ == "__main__":
    # Create application object
    app = QApplication(sys.argv)

    history_win = HistoryUI(__get_bundle_dir())
    history_win.show()      # Show window

    sys.exit(app.exec())    # Start application
