from PyQt6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QPushButton, QInputDialog

class LabelSidebar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.labelList = QListWidget()
        self.addLabelButton = QPushButton("New Label")

        layout = QVBoxLayout()
        layout.addWidget(self.labelList)
        layout.addWidget(self.addLabelButton)
        self.setLayout(layout)

        self.addLabelButton.clicked.connect(self.handle_new_label)

    def handle_new_label(self):
        labelName, ok = QInputDialog.getText(self, "Create New Label", "Enter label:")
        if ok and labelName.strip():
            self.labelList.addItem(labelName.strip())

    def get_selected_label(self):
        item = self.labelList.currentItem()
        return item.text() if item else None
