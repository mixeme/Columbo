import os
import shutil

from PyQt5 import QtWidgets, uic, QtGui
from PyQt5.QtCore import QModelIndex, QThreadPool, Qt
from PyQt5.QtGui import QDragEnterEvent, QDropEvent
from PyQt5.QtWidgets import QFileDialog, QMenu

from core import file, node, validator
from core.types import TreeType, OperationType
from core.worker import FileTreeWorker
from gui import icons


class ApplicationUI(QtWidgets.QMainWindow):
    def __init__(self, project_home: str):
        # Call QtWidgets.QMainWindow constructor
        super().__init__()

        # Load GUI layout
        uic.loadUi(os.path.join(project_home, 'src/gui/history.ui'), self)

        # Set window properties
        self.setWindowTitle("Columbo - Synchronization history observer")
        self.setWindowIcon(QtGui.QIcon(os.path.join(project_home, 'resources/icons/search.png')))
        self.setAcceptDrops(True)

        # Load icons
        icons.IconsLoader(project_home)

        # Connect signals of tree building
        FileTreeWorker.signals.\
            build_finished.connect(self.update_tree)               # Connect to slot for finishing
        FileTreeWorker.signals.\
            build_finished.connect(self.switch_clear_all)          # Switch button for Clear all
        FileTreeWorker.signals.\
            build_finished.connect(self.switch_delete_snapshots)   # Switch buttons for snapshots

        # Connect signals of files cleaning
        FileTreeWorker.signals.\
            progress.connect(lambda x: self.statusbar.showMessage(x))
        FileTreeWorker.signals.\
            clear_finished.connect(lambda: self.statusbar.showMessage("Snapshots are cleared"))
        FileTreeWorker.signals.\
            clear_finished.connect(lambda: self.statusbar.showMessage("Empty directories are cleared"))

    def get_path(self) -> str:
        """

        :return: Value of text field with history path
        """
        return self.path_field.text()

    def set_path(self, path: str) -> None:
        """

        :param path: Value of text field with history path
        """
        self.path_field.setText(path)

    def get_sub_path(self) -> str:
        return self.subpath_field.text()

    def set_sub_path(self, path: str) -> None:
        self.subpath_field.setText(path)

    def from_checked(self) -> TreeType:
        """

        :return: Type of the source presentation
        """
        if self.from_unified.isChecked():
            return TreeType.UNIFIED

        if self.from_bydate.isChecked():
            return TreeType.BY_DATE

    def to_checked(self) -> TreeType:
        """

        :return: Type of the target presentation
        """
        if self.to_unified.isChecked():
            return TreeType.UNIFIED

        if self.to_bydate.isChecked():
            return TreeType.BY_DATE

    def checked(self) -> (TreeType, TreeType):
        """

        :return: A tuple of the (source, target) tree presentation
        """
        return self.from_checked(), self.to_checked()

    def get_selected_nodes(self) -> list[QModelIndex]:
        return self.file_tree_view.selectedIndexes()

    def get_selected_path(self) -> (str, str):
        selected_nodes = self.get_selected_nodes()
        index = selected_nodes[0]               # Get the selected index
        snapshot = selected_nodes[2].data()     # Get snapshot name
        selected_item = index.data()            # Get data of the selected index
        selected_path = selected_item           # Prepare selected path

        # Go up for a versioned file
        if (self.from_checked() == TreeType.BY_DATE) \
                and (self.to_checked() == TreeType.UNIFIED)\
                and (not node.is_folder_row(selected_nodes)):
            index = index.parent()

        index = index.parent()                          # Get its parent
        while index.isValid():                          # Combine a path to the selected item
            parent_item = index.data()                  # Get parent name

            # If we reach the root
            if parent_item == self.get_path():
                # Add snapshot to the path for By date -> Unified
                if (self.from_checked() == TreeType.BY_DATE) and (self.to_checked() == TreeType.UNIFIED) \
                        and (not node.is_folder_row(selected_nodes)):
                    parent_item = os.path.join(parent_item, snapshot)

                # Remove snapshot from the path for Unified -> By date
                if (self.from_checked() == TreeType.UNIFIED) and (self.to_checked() == TreeType.BY_DATE):
                    selected_path = selected_path[selected_path.find(os.sep)+1:]

            selected_path = os.path.join(parent_item, selected_path)
            index = index.parent()

        return selected_path, selected_item

    def browse_action(self) -> None:
        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.FileMode.Directory)
        if dialog.exec():
            selected_dir = dialog.selectedFiles()[0]
            self.set_path(selected_dir.replace("/", os.sep))

    def set_from_snapshot(self):
        selected_node = self.get_selected_nodes()[0]            # Get selected node

        if selected_node.siblingAtColumn(1).data() == "Folder":
            snapshot = selected_node.data()                     # Get value from its name
        else:
            snapshot = selected_node.siblingAtColumn(2).data()  # Get value from its third column

        self.filter_from_field.setText(snapshot)                # Set field text

    def set_to_snapshot(self):
        selected_node = self.get_selected_nodes()[0]            # Get selected node

        if selected_node.siblingAtColumn(1).data() == "Folder":
            snapshot = selected_node.data()                     # Get value from its name
        else:
            snapshot = selected_node.siblingAtColumn(2).data()  # Get value from its third column

        self.filter_to_field.setText(snapshot)                  # Set field text

    def update_tree(self, _, model) -> None:
        self.file_tree_view.setModel(model)
        self.file_tree_view.header().resizeSection(0, 300)
        self.statusbar.showMessage("Build is finished")

    def switch_clear_all(self, op_type: OperationType, _) -> None:
        self.clear_all_button.setEnabled(op_type == OperationType.EMPTY_DIRS)

    def switch_delete_snapshots(self, op_type: OperationType, _) -> None:
        self.delete_button.setEnabled(op_type == OperationType.FILTERED_TREE)

    def create_validator(self, operation_type: OperationType):
        if (operation_type == OperationType.FILTERED_TREE) or (operation_type == operation_type.CLEAR_SNAPSHOTS):
            bounds = [self.filter_from_field.text(), self.filter_to_field.text()]
            source_type = self.checked()[0]
            sub_path = self.subpath_field.text()
        else:
            bounds = [None, None]
            source_type = self.checked()[0]
            sub_path = ""

        return validator.SnapshotValidator(bounds, source_type, sub_path)

    def create_worker(self, operation_type: OperationType):
        # Create worker
        worker = FileTreeWorker(self.path_field.text(), self.checked(), operation_type)

        # Create & set validator
        worker.validator = self.create_validator(operation_type)

        return worker

    def build_file_tree(self, operation_type: OperationType) -> None:
        if len(self.path_field.text()) > 0:
            # Create worker
            worker = self.create_worker(operation_type)

            # Start a worker in another thread
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
        extension = file.get_file_extension(selected_item)

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
            worker = self.create_worker(OperationType.CLEAR_EMPTY_DIRS)
            QThreadPool.globalInstance().start(worker)
            self.statusbar.showMessage("Start clear empty directories")

    def delete_snapshots_action(self) -> None:
        if self.path_field.text():
            worker = self.create_worker(OperationType.CLEAR_SNAPSHOTS)
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
        if not node.is_folder_row(nodes):    # If a file is selected
            # Create context menu
            openfile = context_menu.addAction("Open")
            restore = context_menu.addAction("Restore")
            context_menu.addSeparator()
            from_snapshot = context_menu.addAction("From snapshot")
            to_snapshot = context_menu.addAction("To snapshot")
            context_menu.addSeparator()
            open_folder = context_menu.addAction("Open in folder")
            action = context_menu.exec_(self.file_tree_view.mapToGlobal(position))

            # Resolve action
            if action == openfile:
                file.open_file(self.get_selected_path()[0])
            if action == restore:
                self.restore_action()
            if action == from_snapshot:
                self.set_from_snapshot()
            if action == to_snapshot:
                self.set_to_snapshot()
            if action == open_folder:
                file_path = self.get_selected_path()[0]     # Get path of the selected item
                file.open_file(os.path.dirname(file_path))       # Open folder contains this item
        else:   # If a folder is selected
            from_snapshot, to_snapshot = None, None
            if self.to_checked() == TreeType.BY_DATE and nodes[0].parent().data() == self.path_field.text():
                from_snapshot = context_menu.addAction("From snapshot")
                to_snapshot = context_menu.addAction("To snapshot")
                context_menu.addSeparator()

            if self.from_checked() == TreeType.UNIFIED:
                set_as_root = context_menu.addAction("Set as root")
                context_menu.addSeparator()
            else:
                set_as_root = None
            if self.from_checked() == TreeType.BY_DATE:
                set_as_sub_path = context_menu.addAction("Set as sub-path")
                context_menu.addSeparator()
            else:
                set_as_sub_path = None

            expand = context_menu.addAction("Expand recursively")

            delete = None
            if self.clear_all_button.isEnabled():
                context_menu.addSeparator()
                delete = context_menu.addAction("Delete empty directory")

            action = context_menu.exec_(self.file_tree_view.mapToGlobal(position))
            if action is None:
                return
            if action == expand:
                self.file_tree_view.expandRecursively(self.get_selected_nodes()[0])
            if self.clear_all_button.isEnabled() and action == delete:
                selected_path, _ = self.get_selected_path()
                try:
                    os.removedirs(selected_path)
                    self.statusbar.showMessage("Delete", selected_path)
                except OSError:
                    self.statusbar.showMessage("Failed to delete", selected_path)
            if action == from_snapshot:
                self.set_from_snapshot()
            if action == to_snapshot:
                self.set_to_snapshot()
            if action == set_as_root:
                self.set_path(self.get_selected_path()[0])
            if action == set_as_sub_path:
                sub_path: str = self.get_selected_path()[0].removeprefix(self.get_path() + os.sep)
                self.set_sub_path(sub_path)
