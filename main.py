import os.path
import shutil
import sys

import pkg.file
import tree
from pkg.workers import ClearEmptyDirsWorker, ClearSnapshotWorker
from tree import OperatioType, TreeType

from PyQt5 import QtWidgets, QtGui, uic
from PyQt5.QtCore import QThreadPool, Qt, QModelIndex
from PyQt5.QtGui import QDropEvent, QDragEnterEvent
from PyQt5.QtWidgets import QApplication, QFileDialog, QMenu


class HistoryUI(QtWidgets.QMainWindow):
    def __init__(self):
        # Load GUI layout
        super().__init__()
        uic.loadUi('gui/history.ui', self)      # Load GUI layout

        self.setWindowTitle("Columbo - Synchronization history observer")
        self.setWindowIcon(QtGui.QIcon('icons/search.png'))

        self.setAcceptDrops(True)

        tree.FileTreeWorker.signals.finished.connect(self.update_tree)  # Connect to slot for finishing
        tree.FileTreeWorker.signals.finished.connect(self.switch_clear_all) # Switch Clear all button

        ClearSnapshotWorker.signals.finished.connect(lambda: self.statusbar.showMessage("Snapshots are cleared"))
        ClearEmptyDirsWorker.signals.finished.connect(lambda: self.statusbar.showMessage("Empty directories are cleared"))

    def from_checked(self) -> TreeType:
        if self.from_unified.isChecked():
            return TreeType.UNIFIED

        if self.from_bydate.isChecked():
            return TreeType.BYDATE

    def to_checked(self) -> TreeType:
        if self.to_unified.isChecked():
            return TreeType.UNIFIED

        if self.to_bydate.isChecked():
            return TreeType.BYDATE

    def checked(self) -> (TreeType, TreeType):
        return self.from_checked(), self.to_checked()

    def get_selected_nodes(self) -> list[QModelIndex]:
        return self.fileTreeView.selectedIndexes()

    def get_selected_path(self) -> (str, str):
        index = self.fileTreeView.selectedIndexes()[0]  # Get the selected index
        snapshot = index.siblingAtColumn(2).data()      # Get snapshot
        selected_item = index.data()                    # Get item for the selected index
        selected_path = selected_item                   # Prepare selected path

        # Go up for a versioned file
        if (self.from_checked() == TreeType.BYDATE) and (self.to_checked() == TreeType.UNIFIED):
            index = index.parent()

        index = index.parent()                          # Get its parent
        while index.isValid():                          # Combine a path to the selected item
            parent_item = index.data()                  # Get parent name

            # If we reach the root
            if parent_item == self.path_field.text():
                # Add snapshot to the path for By date -> Unified
                if (self.from_checked() == TreeType.BYDATE) and (self.to_checked() == TreeType.UNIFIED):
                    parent_item = os.path.join(parent_item, snapshot)

                # Remove snapshot from the path for Unified -> By date
                if (self.from_checked() == TreeType.UNIFIED) and (self.to_checked() == TreeType.BYDATE):
                    selected_path = selected_path[selected_path.find(os.sep)+1:]

            selected_path = os.path.join(parent_item, selected_path)
            index = index.parent()
        return selected_path, selected_item

    def browse_action(self) -> None:
        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.FileMode.Directory)
        if dialog.exec():
            selected_dir = dialog.selectedFiles()[0]
            self.path_field.setText(selected_dir)

    def update_tree(self, _, model) -> None:
        self.fileTreeView.setModel(model)
        self.fileTreeView.header().resizeSection(0, 400)
        self.statusbar.showMessage("Build is finished")

    def switch_clear_all(self, op_type: OperatioType, _) -> None:
        self.clear_all_button.setEnabled(op_type == OperatioType.EMPTY_DIRS)

    def build_file_tree(self, op_type: OperatioType) -> None:
        if self.path_field.text():
            worker = tree.FileTreeWorker(self.path_field.text(),
                                         self.checked(),
                                         op_type)

            # Switch filter
            if op_type == OperatioType.FILTERED_TREE:
                worker.set_filter(self.filter_from_field.text(), self.filter_to_field.text())

            # Start worker in another thread
            QThreadPool.globalInstance().start(worker)
            self.statusbar.showMessage("Start tree building")

    def scan_action(self) -> None:
        self.build_file_tree(OperatioType.FILE_TREE)

    def filter_action(self) -> None:
        self.build_file_tree(OperatioType.FILTERED_TREE)

    def empty_dirs_action(self) -> None:
        self.build_file_tree(OperatioType.EMPTY_DIRS)

    def expand_action(self) -> None:
        self.fileTreeView.expandAll()

    def collapse_action(self) -> None:
        self.fileTreeView.collapseAll()

    def restore_action(self) -> None:
        # Get path to item
        selected_path, selected_item = self.get_selected_path()
        extension = pkg.file.get_extension(selected_item)

        # Define file extension for dialog
        if extension:
            dialog_extension = extension.upper() + " (*." + extension + ")"
        else:
            dialog_extension = "All Files (*)"

        # Get destination
        destination_file, _ = QFileDialog.getSaveFileName(self, "Restore file", selected_path, dialog_extension)

        # Copy
        if destination_file:
            shutil.copy(selected_path, destination_file)

    def clear_action(self) -> None:
        self.filter_from_field.clear()
        self.filter_to_field.clear()

    def clear_all_action(self) -> None:
        if self.path_field.text():
            worker = ClearEmptyDirsWorker(self.path_field.text())
            worker.signals.progress.connect(lambda x: print(x))
            QThreadPool.globalInstance().start(worker)
            self.statusbar.showMessage("Start clear empty directories")

    def delete_snapshots_action(self) -> None:
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

            worker = ClearSnapshotWorker(self.path_field.text(), test_fun)
            worker.signals.progress.connect(lambda x: print(x))
            QThreadPool.globalInstance().start(worker)
            self.statusbar.showMessage("Start clear snapshots")

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event) -> None:
        if event.mimeData().hasUrls():
            event.setDropAction(Qt.MoveAction)
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent) -> None:
        files = [url.toLocalFile() for url in event.mimeData().urls()]
        self.path_field.setText(files[0])

    def contextMenuEvent(self, event) -> None:
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
                self.statusbar.showMessage("Delete", selected_path)
            except OSError:
                self.statusbar.showMessage("Failed to delete", selected_path)


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
