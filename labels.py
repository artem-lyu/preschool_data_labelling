from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QListWidget, QPushButton,
    QInputDialog, QMenu, QMessageBox
)
from PyQt6.QtCore import Qt, QPoint, pyqtSignal

class LabelSidebar(QWidget):
    labelDeleted = pyqtSignal(str)
    def __init__(self, parent=None):
        super().__init__(parent)

        self.labelList = QListWidget()
        self.addLabelButton = QPushButton("New Label")

        layout = QVBoxLayout()
        layout.addWidget(self.labelList)
        layout.addWidget(self.addLabelButton)
        self.setLayout(layout)

        self.addLabelButton.clicked.connect(self.handle_new_label)

        self.labelList.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.labelList.customContextMenuRequested.connect(self.show_context_menu)

    def handle_new_label(self):
        labelName, ok = QInputDialog.getText(self, "Create New Label", "Enter label:")
        if ok and labelName.strip():
            self.labelList.addItem(labelName.strip())

    def get_selected_label(self):
        item = self.labelList.currentItem()
        return item.text() if item else None

    def show_context_menu(self, pos: QPoint):
        item = self.labelList.itemAt(pos)
        if not item:
            return

        menu = QMenu(self)
        deleteAction = menu.addAction("Delete Label")

        action = menu.exec(self.labelList.mapToGlobal(pos))
        if action == deleteAction:
            labelName = item.text()
            reply = QMessageBox.question(
                self,
                "Confirm Deletion",
                f"Are you sure you want to delete the label '{labelName}'?\nAll images will be removed!",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                row = self.labelList.row(item)
                self.labelList.takeItem(row)
                self.labelDeleted.emit(labelName)