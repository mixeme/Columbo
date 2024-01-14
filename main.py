import os.path
import shutil
import sys

import pkg.file
import tree

from PyQt5 import QtWidgets, QtGui, uic
from PyQt5.QtCore import QThreadPool
from PyQt5.QtWidgets import QApplication, QFileDialog, QMenu


class HistoryUI(QtWidgets.QMainWindow):
    def __init__(self):
        # Load GUI layout
        super().__init__()
        uic.loadUi('gui/history.ui', self)
        self.setWindowTitle("Columbo - Synchronization history observer")
        self.setWindowIcon(QtGui.QIcon('icons/search.png'))

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

    def update_tree(self, model) -> None:
        self.fileTreeView.setModel(model)
        self.fileTreeView.header().resizeSection(0, 400)
        self.statusbar.showMessage("Build is finished")

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
            self.clear_all_button.setEnabled(True)

    def expand_action(self):
        self.fileTreeView.expandAll()

    def collapse_action(self):
        self.fileTreeView.collapseAll()

    def get_selected_nodes(self):
        return self.fileTreeView.selectedIndexes()

    def get_selected_path(self):
        index = self.fileTreeView.selectedIndexes()[0]  # Get the selected index
        selected_item = index.model().data(index)       # Get item for the selected index
        selected_path = selected_item
        index = index.parent()                          # Get its parent
        while index.isValid():                          # Combine a path to the the selected item
            selected_path = os.path.join(index.model().data(index), selected_path)
            index = index.parent()
        return selected_path, selected_item

    def restore_action(self):
        # Get path to item
        index = self.fileTreeView.selectedIndexes()[0]
        source_file = index.model().data(index)
        extension = pkg.file.get_extension(source_file)
        index = index.parent()
        while index.isValid():
            source_file = os.path.join(index.model().data(index), source_file)
            index = index.parent()

        if extension:
            extension_dialog = "(*." + extension + ")"
        else:
            extension_dialog = "All Files (*)"

        # Get destination
        destination_file, _ = QFileDialog.getSaveFileName(self, "Restore file", source_file, extension_dialog)
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

    def clear_action(self):
        self.filter_from_field.clear()
        self.filter_to_field.clear()

    def clear_all_action(self):
        if self.path_field.text():
            pkg.file.clear_empty_dirs(self.path_field.text())

    def delete_snapshots_action(self):
        if self.path_field.text():
            from_snapshot = self.filter_from_field.text()
            to_snapshot = self.filter_to_field.text()

            if self.checked()[0] == tree.TreeType.UNIFIED:
                snapshot_fun = lambda root, file: pkg.file.get_snapshot(file)
            if self.checked()[0] == tree.TreeType.BYDATE:
                snapshot_fun = lambda root, file: root.split(os.sep)[1]

            def test_fun(root: str, file: str) -> bool:
                snapshot = snapshot_fun(root, file)
                return (from_snapshot <= snapshot) and (snapshot <= to_snapshot)

            pkg.file.clear_snapshots(self.path_field.text(), test_fun)

    def contextMenuEvent(self, event):
        context_menu = QMenu(self)
        from_snapshot = context_menu.addAction("From snapshot")
        to_snapshot = context_menu.addAction("To snapshot")
        context_menu.addSeparator()
        expand = context_menu.addAction("Expand recursively")
        context_menu.addSeparator()
        delete = context_menu.addAction("Delete empty directory")
        action = context_menu.exec_(self.mapToGlobal(event.pos()))
        if action == from_snapshot:
            selected_nodes = self.get_selected_nodes()
            snapshot = selected_nodes[0].siblingAtColumn(2).data()
            self.filter_from_field.setText(snapshot)
        if action == to_snapshot:
            selected_nodes = self.get_selected_nodes()
            snapshot = selected_nodes[0].siblingAtColumn(2).data()
            self.filter_to_field.setText(snapshot)
        if action == expand:
            self.fileTreeView.expandRecursively(self.get_selected_nodes()[0])
        if action == delete:
            selected_path, _ = self.get_selected_path()
            try:
                os.removedirs(selected_path)
                print("Delete", selected_path)
            except OSError:
                print("Failed to delete", selected_path)
                pass


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
