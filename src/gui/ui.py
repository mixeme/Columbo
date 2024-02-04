import os
import shutil
import subprocess

from PyQt5 import QtWidgets, uic, QtGui
from PyQt5.QtCore import QModelIndex, QThreadPool, Qt
from PyQt5.QtGui import QDragEnterEvent, QDropEvent
from PyQt5.QtWidgets import QFileDialog, QMenu

from core import file
from core.tree import FileTreeWorker
from core.types import TreeType, OperationType
from core.workers import ClearSnapshotWorker, ClearEmptyDirsWorker
from gui import icons


class HistoryUI(QtWidgets.QMainWindow):
    def __init__(self, project_home: str):
        # Load GUI layout
        super().__init__()

        # Load GUI layout
        uic.loadUi(os.path.join(project_home, 'src/gui/history.ui'), self)

        # Set window properties
        self.setWindowTitle("Columbo - Synchronization history observer")
        self.setWindowIcon(QtGui.QIcon(os.path.join(project_home, 'icons/search.png')))
        self.setAcceptDrops(True)

        # Load icons
        icons.IconsLoader(project_home)

        # Connect signals
        FileTreeWorker.signals.finished.connect(self.update_tree)               # Connect to slot for finishing
        FileTreeWorker.signals.finished.connect(self.switch_clear_all)          # Switch Clear all button
        FileTreeWorker.signals.finished.connect(self.switch_delete_snapshots)   # Switch Clear all button

        ClearSnapshotWorker.signals.finished.connect(lambda: self.statusbar.showMessage("Snapshots are cleared"))
        ClearEmptyDirsWorker.signals.finished.connect(lambda: self.statusbar.showMessage("Empty directories are cleared"))

    def from_checked(self) -> TreeType:
        if self.from_unified.isChecked():
            return TreeType.UNIFIED

        if self.from_bydate.isChecked():
            return TreeType.BY_DATE

    def to_checked(self) -> TreeType:
        if self.to_unified.isChecked():
            return TreeType.UNIFIED

        if self.to_bydate.isChecked():
            return TreeType.BY_DATE

    def checked(self) -> (TreeType, TreeType):
        return self.from_checked(), self.to_checked()

    def get_selected_nodes(self) -> list[QModelIndex]:
        return self.file_tree_view.selectedIndexes()

    def get_selected_path(self) -> (str, str):
        index = self.file_tree_view.selectedIndexes()[0]  # Get the selected index
        snapshot = index.siblingAtColumn(2).data()      # Get snapshot
        selected_item = index.data()                    # Get item for the selected index
        selected_path = selected_item                   # Prepare selected path

        # Go up for a versioned file
        if (self.from_checked() == TreeType.BY_DATE) and (self.to_checked() == TreeType.UNIFIED):
            index = index.parent()

        index = index.parent()                          # Get its parent
        while index.isValid():                          # Combine a path to the selected item
            parent_item = index.data()                  # Get parent name

            # If we reach the root
            if parent_item == self.path_field.text():
                # Add snapshot to the path for By date -> Unified
                if (self.from_checked() == TreeType.BY_DATE) and (self.to_checked() == TreeType.UNIFIED):
                    parent_item = os.path.join(parent_item, snapshot)

                # Remove snapshot from the path for Unified -> By date
                if (self.from_checked() == TreeType.UNIFIED) and (self.to_checked() == TreeType.BY_DATE):
                    selected_path = selected_path[selected_path.find(os.sep)+1:]

            selected_path = os.path.join(parent_item, selected_path)
            index = index.parent()
        return selected_path, selected_item

    def _open_file(self):
        file = self.get_selected_path()[0]
        try:
            os.startfile(file)
        except AttributeError:
            subprocess.call(['open', file])

    def browse_action(self) -> None:
        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.FileMode.Directory)
        if dialog.exec():
            selected_dir = dialog.selectedFiles()[0]
            self.path_field.setText(selected_dir.replace("/", os.sep))

    def update_tree(self, _, model) -> None:
        self.file_tree_view.setModel(model)
        self.file_tree_view.header().resizeSection(0, 300)
        self.statusbar.showMessage("Build is finished")

    def switch_clear_all(self, op_type: OperationType, _) -> None:
        self.clear_all_button.setEnabled(op_type == OperationType.EMPTY_DIRS)

    def switch_delete_snapshots(self, op_type: OperationType, _) -> None:
        self.delete_button.setEnabled(op_type == OperationType.FILTERED_TREE)

    def build_file_tree(self, op_type: OperationType) -> None:
        if self.path_field.text():
            worker = FileTreeWorker(self.path_field.text(),
                                    self.checked(),
                                    op_type)

            # Switch filter
            if op_type == OperationType.FILTERED_TREE:
                tester = file.SnapshotTester([self.filter_from_field.text(), self.filter_to_field.text()],
                                             self.checked()[0])
                worker.set_filter(tester)

            # Start worker in another thread
            QThreadPool.globalInstance().start(worker)
            self.statusbar.showMessage("Start tree building")

    def scan_action(self) -> None:
        self.build_file_tree(OperationType.FILE_TREE)

    def filter_action(self) -> None:
        self.build_file_tree(OperationType.FILTERED_TREE)

    def empty_dirs_action(self) -> None:
        self.build_file_tree(OperationType.EMPTY_DIRS)

    def expand_action(self) -> None:
        self.file_tree_view.expandAll()

    def collapse_action(self) -> None:
        self.file_tree_view.collapseAll()

    def restore_action(self) -> None:
        # Get path to item
        selected_path, selected_item = self.get_selected_path()
        extension = file.get_extension(selected_item)

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
            bounds = [self.filter_from_field.text(), self.filter_to_field.text()]
            tester = file.SnapshotTester(bounds, self.checked()[0])
            worker = ClearSnapshotWorker(self.path_field.text(), tester)
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

    def contextMenuEvent(self, position) -> None:
        # Don't open context menu for no selection
        nodes = self.get_selected_nodes()
        if len(nodes) == 0:
            return

        context_menu = QMenu()
        if nodes[0].siblingAtColumn(1).data() != "Folder":
            openfile = context_menu.addAction("Open")
            restore = context_menu.addAction("Restore")
            context_menu.addSeparator()
            from_snapshot = context_menu.addAction("From snapshot")
            to_snapshot = context_menu.addAction("To snapshot")
            action = context_menu.exec_(self.file_tree_view.mapToGlobal(position))

            if action == openfile:
                self._open_file()
            if action == restore:
                self.restore_action()
            if action == from_snapshot:
                selected_nodes = self.get_selected_nodes()
                snapshot = selected_nodes[0].siblingAtColumn(2).data()
                self.filter_from_field.setText(snapshot)
            if action == to_snapshot:
                selected_nodes = self.get_selected_nodes()
                snapshot = selected_nodes[0].siblingAtColumn(2).data()
                self.filter_to_field.setText(snapshot)
        else:
            expand = context_menu.addAction("Expand recursively")

            delete = None
            if self.clear_all_button.isEnabled():
                context_menu.addSeparator()
                delete = context_menu.addAction("Delete empty directory")

            action = context_menu.exec_(self.file_tree_view.mapToGlobal(position))
            if action == expand:
                self.file_tree_view.expandRecursively(self.get_selected_nodes()[0])
            if self.clear_all_button.isEnabled() and action == delete:
                selected_path, _ = self.get_selected_path()
                try:
                    os.removedirs(selected_path)
                    self.statusbar.showMessage("Delete", selected_path)
                except OSError:
                    self.statusbar.showMessage("Failed to delete", selected_path)
