import sys

import tree

from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import QThreadPool
from PyQt5.QtWidgets import QApplication, QFileDialog


class history_ui(QtWidgets.QMainWindow):
    def __init__(self):
        # Load GUI layout
        super().__init__()
        uic.loadUi('gui/history.ui', self)

    def browse_action(self):
        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.FileMode.Directory)
        if dialog.exec():
            selected_dir = dialog.selectedFiles()[0]
            self.path_field.setText(selected_dir)
            QThreadPool.globalInstance().start(tree.FileTreeWorker(selected_dir, self.fileTreeView))


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


# Set the custom exception handler
sys.excepthook = except_hook

if __name__ == "__main__":
    # Create application object
    app = QApplication(sys.argv)

    history_win = history_ui()
    history_win.show()  # Show window

    sys.exit(app.exec())          # Start application

