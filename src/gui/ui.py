import os
import shutil

from PyQt5 import QtWidgets, uic, QtGui
from PyQt5.QtCore import QModelIndex, Qt
from PyQt5.QtGui import QDragEnterEvent, QDropEvent
from PyQt5.QtWidgets import QFileDialog, QMenu

import core.snapshot
from core import file, node, validator, data_model, pyqtmiscellaneous, types
from core.worker.filetree_builder import FileTreeWBuilder
from core.worker.filetree_loader import FileTreeLoader
from core.worker.filetree_deleter import FileTreeDeleter
from core.types import TreeType, OperationType
from gui import icons


class ApplicationUI(QtWidgets.QMainWindow):
    def __init__(self, project_home: str):
        # Call QtWidgets.QMainWindow constructor
        super().__init__()

        # Load GUI layout
        uic.loadUi(os.path.join(project_home, 'src/gui/history2.ui'), self)

        # Load icons
        icons.IconsLoader(project_home)

        # Set window properties
        self.setWindowTitle("Columbo - Synchronization history observer")
        self.setWindowIcon(QtGui.QIcon(os.path.join(project_home, 'resources/icons/search.png')))
        self.setAcceptDrops(True)

        # Connect signals of file tree loader
        FileTreeLoader.signals.\
            load_finished.connect(self.load_finished_action)

        # Connect signals of file tree builder
        FileTreeWBuilder.signals.\
            build_finished.connect(self.update_tree)                # Connect to slot for finishing
        FileTreeWBuilder.signals.\
            build_finished.connect(self.switch_delete_buttons)      # Switch button for delete

        # Connect signals of files cleaning
        FileTreeWBuilder.signals.\
            progress.connect(lambda x: self.statusbar.showMessage(x))
        FileTreeWBuilder.signals.\
            delete_finished.connect(self.response_clear_finished)

        # Declare fields
        self.loader = FileTreeLoader()
        self.builder = FileTreeWBuilder(self.loader)
        self.deleter = FileTreeDeleter(self.loader)

    # Group of methods for get/set value of GUI components
    # Getter and setter for history path field
    def get_history_path(self) -> str:
        """

        :return: Value of text field with history path
        """
        return self.history_path_field.text()

    def set_history_path(self, path: str) -> None:
        """

        :param path: Value of text field with history path
        """
        self.history_path_field.setText(path)
        self.history_path_changed()

    # Getter and setter for subpath path field
    def get_subpath(self) -> str:
        return self.subpath_field.text()

    def set_subpath(self, path: str) -> None:
        self.subpath_field.setText(path)

    def clear_subpath(self) -> None:
        self.subpath_field.clear()

    # Get checked source type
    def source_type(self) -> TreeType:
        if self.source_unified.isChecked():
            return TreeType.UNIFIED

        if self.source_bydate.isChecked():
            return TreeType.BY_DATE

        raise AttributeError("Unknown source type")

    # Get checked target view
    def target_view(self) -> TreeType:
        if self.target_unified.isChecked():
            return TreeType.UNIFIED

        if self.target_bydate.isChecked():
            return TreeType.BY_DATE

        raise AttributeError("Unknown target view")

    # Get view direction (source type -> target view)
    def get_view_direction(self) -> types.ViewDirection:
        return types.ViewDirection(self.source_type(), self.target_view())

    # Getter and setter for lower timestamp bound field
    def get_bounds_from(self) -> str:
        return self.bounds_from_field.text()

    def set_bounds_from(self, timestamp: str) -> None:
        self.bounds_from_field.setText(timestamp)

    # Getter and setter for lower timestamp bound field
    def get_bounds_to(self) -> str:
        return self.bounds_to_field.text()

    def set_bounds_to(self, timestamp: str) -> None:
        self.bounds_to_field.setText(timestamp)

    # Clear both bounds fields
    def clear_bounds(self) -> None:
        self.bounds_from_field.clear()
        self.bounds_to_field.clear()

    # Getter and setter for delimiter field
    def get_delimiter(self) -> str:
        return self.delimiter_field.text()

    def set_delimiter(self, delimiter: str) -> None:
        self.delimiter_field.setText(delimiter)

    # Get selection of node
    def get_selected_row(self) -> types.TreeRow:
        return self.filetree_view.selectedIndexes()

    # Set status of loader
    def set_loader_status(self):
        if self.loader.is_empty():
            self.load_label.setText("Not loaded")
        else:
            self.load_label.setText("Loaded")

    # Group of methods for button click actions
    def browse_action(self) -> None:
        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.FileMode.Directory)
        if dialog.exec():
            selected_dir = dialog.selectedFiles()[0]
            self.set_history_path(selected_dir.replace("/", os.sep))

    # Load actions
    def load_action(self):
        if len(self.get_history_path()) > 0:
            # Disable buttons
            self.load_button.setEnabled(False)
            self.build_button.setEnabled(False)

            self.loader.set_root(self.get_history_path())
            pyqtmiscellaneous.RunnableWrapper.run_async(self.loader)
            self.statusbar.showMessage("Load file tree")

    def build_action(self) -> None:
        self.tree_action(self.builder, OperationType.FULL_TREE, "Start tree building")

    # Expand and collapse actions
    def expand_action(self) -> None:
        self.filetree_view.expandAll()

    def collapse_action(self) -> None:
        self.filetree_view.collapseAll()

    # Empty directories actions
    def build_empty_dirs_action(self) -> None:
        self.tree_action(self.builder, OperationType.EMPTY_DIRS, "Start tree building")

    def delete_empty_dirs_action(self) -> None:
        self.tree_action(self.deleter, OperationType.DELETE_EMPTY_DIRS, "Start to delete empty directories")

    # Clear actions
    def clear_bounds_action(self) -> None:
        self.clear_bounds()

    def filter_clear_action(self) -> None:
        self.clear_bounds()
        self.clear_subpath()

    # Build filtered tree
    def filter_apply_action(self) -> None:
        self.tree_action(self.builder, OperationType.FILTERED_TREE, "Start tree building")

    # Delete filtered files
    def delete_snapshots_action(self) -> None:
        self.tree_action(self.deleter, OperationType.DELETE_SNAPSHOTS, "Start to delete snapshots")

    def switch_delete_buttons(self, op_type: OperationType, _) -> None:
        self.delete_empty_dirs_button.setEnabled(op_type == OperationType.EMPTY_DIRS)
        self.filter_delete_button.setEnabled(op_type == OperationType.FILTERED_TREE)

    def switch_tree_buttons(self, active: bool) -> None:
        self.load_button.setEnabled(active)
        self.build_button.setEnabled(active and (not self.loader.is_empty()))

    def create_validator(self, operation_type: OperationType):
        direction: types.ViewDirection = self.get_view_direction()
        if operation_type == OperationType.FULL_TREE:
            bounds = ("", "")
            sub_path = ""
            return validator.SnapshotValidator(direction, bounds, sub_path)
        if (operation_type == OperationType.FILTERED_TREE) or (operation_type == operation_type.DELETE_SNAPSHOTS):
            bounds = (self.get_bounds_from(), self.get_bounds_to())
            sub_path = self.get_subpath()
            return validator.SnapshotValidator(direction, bounds, sub_path)
        if (operation_type == OperationType.EMPTY_DIRS) or (operation_type == OperationType.DELETE_EMPTY_DIRS):
            _, files = self.loader.get_lists()
            return validator.EmptyDirValidator(files)
        raise ValueError("Unknown operation ")

    def tree_action(self, worker, operation: OperationType, message: str) -> None:
        if len(self.get_history_path()) > 0:
            core.snapshot.timestamp_delimiter = self.get_delimiter()

            # Set root path for loader
            self.loader.set_root(self.get_history_path())

            # Set options
            # Create & set validator
            worker.set_direction(self.get_view_direction())
            worker.set_operation(operation)
            worker.set_validator(self.create_validator(operation))

            # Run builder
            pyqtmiscellaneous.RunnableWrapper.run_async(self.builder)

            # Switch off tree buttons
            self.switch_tree_buttons(False)

            # Update status bar message
            self.statusbar.showMessage(message)

    def update_tree(self, _, model) -> None:
        self.filetree_view.setModel(model)
        self.filetree_view.header().resizeSection(0, 300)

        self.switch_tree_buttons(True)
        self.set_loader_status()

        self.statusbar.showMessage("Build is finished")

    def restore_file_action(self) -> None:
        # Get path to item
        path_parts = data_model.gather_path(self.get_selected_row()[0])
        extension = file.get_file_extension(path_parts[-1])

        # Define file extension for dialog
        if len(extension) > 0:
            dialog_extension = extension.upper() + " (*." + extension + ")"
        else:
            dialog_extension = "All Files (*)"

        # Get destination
        path = file.join_path(path_parts)
        destination_file, _ = QFileDialog.getSaveFileName(self, "Restore file", path, dialog_extension)

        # Copy
        if destination_file:
            shutil.copy(path, destination_file)

    def restore_dir_action(self) -> None:
        # Get path to item
        path_parts = data_model.gather_subnodes_path(self.get_selected_row()[0])

        # Get destination
        path = file.join_path(path_parts)
        destination_file, _ = QFileDialog.getSaveFileName(self, "Restore file", path, dialog_extension)

        # Copy
        if destination_file:
            shutil.copy(path, destination_file)


    def load_finished_action(self):
        self.switch_tree_buttons(True)
        self.set_loader_status()
        self.statusbar.showMessage("File tree is loaded")

    def path_to_selected(self):
        return file.join_path(data_model.gather_path(self.get_selected_row()[0]))

    # Set timestamp bounds
    def set_bound(self, set_function) -> None:
        selected_node = self.get_selected_row()[0]              # Get selected node
        if selected_node.siblingAtColumn(1).data() == "Folder":
            timestamp = selected_node.data()                    # Get value from its name
        else:
            timestamp = selected_node.siblingAtColumn(2).data() # Get value from its third column
        set_function(timestamp)                         # Set field text

    def response_clear_finished(self, operation: OperationType):
        if operation == OperationType.DELETE_SNAPSHOTS:
            self.statusbar.showMessage("Snapshots are cleared")
        if operation == OperationType.DELETE_EMPTY_DIRS:
            self.statusbar.showMessage("Empty directories are cleared")

        # Drop lists
        self.loader.reset()

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
        self.set_history_path(files[0])

    def contextMenuEvent(self, position) -> None:
        # Don't open context menu for no selection
        nodes = self.get_selected_row()
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
            action = context_menu.exec_(self.filetree_view.mapToGlobal(position))

            # Resolve action
            if action == openfile:
                file.open_file(self.path_to_selected())
            if action == open_folder:
                file.open_file(os.path.dirname(self.path_to_selected()))    # Open folder contains this item
            if action == from_snapshot:
                self.set_bound(self.set_bounds_from)
            if action == to_snapshot:
                self.set_bound(self.set_bounds_to)
            if action == restore:
                self.restore_action()
        else:   # If a folder is selected
            restore = context_menu.addAction("Restore")
            context_menu.addSeparator()

            from_snapshot, to_snapshot = None, None
            if self.target_view() == TreeType.BY_DATE and nodes[0].parent().data() == self.get_history_path():
                from_snapshot = context_menu.addAction("From snapshot")
                to_snapshot = context_menu.addAction("To snapshot")
                context_menu.addSeparator()

            set_as_subpath = context_menu.addAction("Set as subpath")
            context_menu.addSeparator()
            expand = context_menu.addAction("Expand recursively")

            delete = None
            if self.filter_delete_button.isEnabled():
                context_menu.addSeparator()
                delete = context_menu.addAction("Delete empty directory")

            action = context_menu.exec_(self.filetree_view.mapToGlobal(position))
            if action is None:
                return
            if action == expand:
                self.filetree_view.expandRecursively(self.get_selected_row()[0])
            if self.delete_empty_dirs_button.isEnabled() and action == delete:
                path = self.path_to_selected()
                try:
                    os.removedirs(path)
                    self.statusbar.showMessage("Delete", path)
                except OSError:
                    self.statusbar.showMessage("Failed to delete", path)
            if action == from_snapshot:
                self.set_bound(self.set_bounds_from)
            if action == to_snapshot:
                self.set_bound(self.set_bounds_to)
            if action == set_as_subpath:
                subpath: str = self.path_to_selected().removeprefix(self.get_history_path() + os.sep)
                if self.target_view() == TreeType.BY_DATE:
                    parts = file.split_path(subpath)
                    subpath = file.join_path(parts[1:])
                self.set_subpath(subpath)
            if action == restore:



    def history_path_changed(self):
        # Drop lists if path is changed
        self.loader.reset()
        self.set_loader_status()

        self.delete_empty_dirs_button.setEnabled(False)
        self.filter_delete_button.setEnabled(False)

