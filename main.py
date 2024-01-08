import sys

import tree

from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import QThreadPool
from PyQt5.QtWidgets import QApplication, QFileDialog


class HistoryUI(QtWidgets.QMainWindow):
    def __init__(self):
        # Load GUI layout
        super().__init__()
        uic.loadUi('gui/history.ui', self)

    def from_checked(self):
        if self.from_unified.isChecked():
            return tree.TreeType.UNIFIED

        if self.from_bydate.isChecked():
            return tree.TreeType.BYDATE

    def to_checked(self):
        if self.to_unified.isChecked():
            return tree.TreeType.UNIFIED

        if self.to_bydate.isChecked():
            return tree.TreeType.BYDATE

    def checked(self):
        return self.from_checked(), self.to_checked()

    def browse_action(self):
        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.FileMode.Directory)
        if dialog.exec():
            selected_dir = dialog.selectedFiles()[0]
            self.path_field.setText(selected_dir)

    def scan_action(self):
        if self.path_field.text():
            QThreadPool.globalInstance().start(tree.FileTreeWorker(self.path_field.text(),
                                                                   self.fileTreeView,
                                                                   self.checked()))

    def expand_action(self):
        self.fileTreeView.expandAll()

    def collapse_action(self):
        self.fileTreeView.collapseAll()


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


# Set the custom exception handler
sys.excepthook = except_hook

if __name__ == "__main__":
    # Create application object
    app = QApplication(sys.argv)

    history_win = HistoryUI()
    history_win.show()      # Show window

    sys.exit(app.exec())    # Start application
