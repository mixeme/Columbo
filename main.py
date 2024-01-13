import os.path
import shutil
import sys

import pkg.nodes
import tree

from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import QThreadPool
from PyQt5.QtWidgets import QApplication, QFileDialog, QMenu


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
                                                                   self.checked(),
                                                                   tree.OperatioType.FILE_TREE))

    def empty_dirs_action(self):
        if self.path_field.text():
            QThreadPool.globalInstance().start(tree.FileTreeWorker(self.path_field.text(),
                                                                   self.fileTreeView,
                                                                   self.checked(),
                                                                   tree.OperatioType.EMPTY_DIRS))

    def expand_action(self):
        self.fileTreeView.expandAll()

    def collapse_action(self):
        self.fileTreeView.collapseAll()

    def get_selected_nodes(self):
        return self.fileTreeView.selectedIndexes()

    def restore_action(self):
        # Get path to item
        index = self.fileTreeView.selectedIndexes()[0]
        source_file = index.model().data(index)
        index = index.parent()
        while index.isValid():
            source_file = os.path.join(index.model().data(index), source_file)
            index = index.parent()
        # Get destination
        destination_file, _ = QFileDialog.getSaveFileName(self, "Restore file", source_file, "All Files (*)")
        # Copy
        if destination_file:
            shutil.copy(source_file, destination_file)

    def filter_action(self):
        if self.path_field.text():
            worker = tree.FileTreeWorker(self.path_field.text(),
                                         self.fileTreeView,
                                         self.checked(),
                                         tree.OperatioType.FILE_TREE)
            worker.set_filter(self.filter_from_field.text(), self.filter_to_field.text())
            QThreadPool.globalInstance().start(worker)
        #pkg.nodes.filter_tree(self.fileTreeView.model(), self.filter_from_field, self.filter_to_field)

    def contextMenuEvent(self, event):
        contextMenu = QMenu(self)
        from_snapshot = contextMenu.addAction("From snapshot")
        to_snapshot = contextMenu.addAction("To snapshot")
        action = contextMenu.exec_(self.mapToGlobal(event.pos()))
        print(action)
        if action == from_snapshot:
            selected_nodes = self.get_selected_nodes()
            snapshot = selected_nodes[0].siblingAtColumn(2).data()
            self.filter_from_field.setText(snapshot)
        if action == to_snapshot:
            selected_nodes = self.get_selected_nodes()
            snapshot = selected_nodes[0].siblingAtColumn(2).data()
            self.filter_to_field.setText(snapshot)

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
