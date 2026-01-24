import os
import shutil

from PyQt5 import QtWidgets, uic, QtGui
from PyQt5.QtCore import QModelIndex, QThreadPool, Qt
from PyQt5.QtGui import QDragEnterEvent, QDropEvent
from PyQt5.QtWidgets import QFileDialog, QMenu

from core import file, node, validator, data_model, filetree_loader, pyqtmiscellaneous
from core.types import TreeType, OperationType
from core.filetree_builder import FileTreeWBuilder
from gui import icons


class ApplicationUI(QtWidgets.QMainWindow):
    def __init__(self, project_home: str):
        # Call QtWidgets.QMainWindow constructor
        super().__init__()

        # Load GUI layout
        uic.loadUi(os.path.join(project_home, 'src/gui/history2.ui'), self)

        # Set window properties
        self.setWindowTitle("Columbo - Synchronization history observer")
        self.setWindowIcon(QtGui.QIcon(os.path.join(project_home, 'resources/icons/search.png')))
        self.setAcceptDrops(True)

        # Load icons
        icons.IconsLoader(project_home)

        # Connect signals for file tree loading
        filetree_loader.FileTreeLoader.signals.load_finished.connect(self.load_finished_action())

        # Connect signals of tree building
        FileTreeWBuilder.signals.\
            build_finished.connect(self.update_tree)               # Connect to slot for finishing
        FileTreeWBuilder.signals.\
            build_finished.connect(self.switch_clear_all)          # Switch button for Clear all
        FileTreeWBuilder.signals.\
            build_finished.connect(self.switch_delete_snapshots)   # Switch buttons for snapshots

        # Connect signals of files cleaning
        FileTreeWBuilder.signals.\
            progress.connect(lambda x: self.statusbar.showMessage(x))
        FileTreeWBuilder.signals.\
            clear_finished.connect(self.response_clear_finished)
        FileTreeWBuilder.signals.\
            clear_finished.connect(self.response_clear_finished)

        # Declare fields
        self.loader = filetree_loader.FileTreeLoader()
        self.worker = FileTreeWBuilder(self.loader)

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

        # Drop lists if path is changed
        self.loader.reset()

    def get_sub_path(self) -> str:
        return self.subpath_field.text()

    def set_sub_path(self, path: str) -> None:
        self.subpath_field.setText(path)

    def source_type(self) -> TreeType:
        """

        :return: Type of the source presentation
        """
        if self.from_unified.isChecked():
            return TreeType.UNIFIED

        if self.from_bydate.isChecked():
            return TreeType.BY_DATE

    def target_view(self) -> TreeType:
        """

        :return: Type of the target presentation
        """
        if self.to_unified.isChecked():
            return TreeType.UNIFIED

        if self.to_bydate.isChecked():
            return TreeType.BY_DATE

    def transform_direction(self) -> (TreeType, TreeType):
        """

        :return: A tuple of the (source, target) tree presentation
        """
        return self.source_type(), self.target_view()

    def get_selected_nodes(self) -> list[QModelIndex]:
        return self.file_tree_view.selectedIndexes()

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

    def switch_clear_all(self, op_type: OperationType, _) -> None:
        self.clear_all_button.setEnabled(op_type == OperationType.EMPTY_DIRS)

    def switch_delete_snapshots(self, op_type: OperationType, _) -> None:
        self.delete_button.setEnabled(op_type == OperationType.FILTERED_TREE)

    def create_validator(self, operation_type: OperationType):
        if (operation_type == OperationType.FILTERED_TREE) or (operation_type == operation_type.CLEAR_SNAPSHOTS):
            bounds = [self.filter_from_field.text(), self.filter_to_field.text()]
            source_type = self.transform_direction()[0]
            sub_path = self.subpath_field.text()
        else:
            bounds = ["", ""]
            source_type = self.transform_direction()[0]
            sub_path = ""

        return validator.SnapshotValidator(bounds, source_type, sub_path)

    def setup_worker(self, operation_type: OperationType):
        # Set root path for loader
        self.loader.set_root(self.get_path())

        # Set options
        self.worker.set_options(self.transform_direction(), operation_type)

        # Create & set validator
        self.worker.set_validator(self.create_validator(operation_type))

    def build_file_tree(self, operation_type: OperationType) -> None:
        if len(self.get_path()) > 0:
            # Setup worker for job
            self.setup_worker(operation_type)

            # Start a worker in another thread
            pyqtmiscellaneous.RunnableWrapper.run_async(self.worker)
            self.statusbar.showMessage("Start tree building")

    def build_tree_action(self) -> None:
        self.build_file_tree(OperationType.FILE_TREE)

    def filter_action(self) -> None:
        self.build_file_tree(OperationType.FILTERED_TREE)

    def empty_dirs_action(self) -> None:
        self.build_file_tree(OperationType.EMPTY_DIRS)

    def update_tree(self, _, model) -> None:
        self.filetree_view.setModel(model)
        self.filetree_view.header().resizeSection(0, 300)
        self.statusbar.showMessage("Build is finished")

    def expand_action(self) -> None:
        self.file_tree_view.expandAll()

    def collapse_action(self) -> None:
        self.file_tree_view.collapseAll()

    def get_selected_path(self):
        return data_model.restore_path(self.get_path(), self.transform_direction(), self.get_selected_nodes())

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

    def clear_bounds_action(self) -> None:
        self.filter_from_field.clear()
        self.filter_to_field.clear()

    def delete_empty_dirs_action(self) -> None:
        if self.get_path():
            # Create a worker if absent
            self.worker = self.setup_worker(OperationType.CLEAR_EMPTY_DIRS)

            RunnableWrapper.run_async(self.worker)
            self.statusbar.showMessage("Start clear empty directories")

    def reset_filters_action(self) -> None:
        self.clear_bounds_action()
        self.subpath_field.clear()

    def delete_snapshots_action(self) -> None:
        if self.get_path():
            # Create a worker if absent
            self.worker = self.setup_worker(OperationType.CLEAR_SNAPSHOTS)

            RunnableWrapper.run_async(self.worker)
            self.statusbar.showMessage("Start clear snapshots")

    def filetree_load_action(self):
        if len(self.get_path()) > 0:
            self.build_button.setEnabled(False)
            self.loader.set_root(self.get_path())
            pyqtmiscellaneous.RunnableWrapper.run_async(self.loader)
            self.statusbar.showMessage("Load file tree")

    def load_finished_action(self):
        self.build_button.setEnabled(self.loader.is_empty())
        self.statusbar.showMessage("File tree is loaded")

    def response_clear_finished(self, operation: OperationType):
        if operation == OperationType.CLEAR_SNAPSHOTS:
            self.statusbar.showMessage("Snapshots are cleared")
        if operation == OperationType.CLEAR_EMPTY_DIRS:
            self.statusbar.showMessage("Empty directories are cleared")

        # Drop worker
        self.worker = None

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
        self.set_path(files[0])

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
            if self.target_view() == TreeType.BY_DATE and nodes[0].parent().data() == self.get_path():
                from_snapshot = context_menu.addAction("From snapshot")
                to_snapshot = context_menu.addAction("To snapshot")
                context_menu.addSeparator()

            if self.source_type() == TreeType.UNIFIED:
                set_as_root = context_menu.addAction("Set as root")
                context_menu.addSeparator()
            else:
                set_as_root = None
            if self.source_type() == TreeType.BY_DATE:
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
