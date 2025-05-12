#!/usr/bin/env python3

import os
import sys

from PyQt5.QtWidgets import QApplication

from gui.ui import ApplicationUI


def __get_bundle_dir() -> str:
    # Resolve project home folder
    if getattr(sys, 'frozen', False):
        # We are running in a bundle
        return sys._MEIPASS
    else:
        # We are running in a normal Python environment
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


# Set the custom exception handler
sys.excepthook = except_hook

if __name__ == "__main__":
    # Create application object
    app = QApplication(sys.argv)

    # Create window
    app_win = ApplicationUI(__get_bundle_dir())
    # Show window
    app_win.show()

    # Start application
    sys.exit(app.exec())
