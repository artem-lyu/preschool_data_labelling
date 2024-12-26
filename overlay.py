from PyQt6.QtWidgets import QLabel
from PyQt6.QtGui import QPainter, QPixmap, QPen, QColor
from PyQt6.QtCore import Qt, QRect, QPoint

import os, uuid

class VideoLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setScaledContents(True)

        self.currentFrame = QPixmap()
        self.boundingBoxes = []
        self.isDrawing = False
        self.startPoint = QPoint()
        self.endPoint = QPoint()
        self.currentLabel = ""
        self.labelingEnabled = False


    def enableLabeling(self, enabled: bool):
        self.labelingEnabled = enabled

    def setCurrentLabel(self, label: str):
        self.currentLabel = label or ""

    def setVideoFrame(self, frame):
        if not frame.isValid():
            return
        image = frame.toImage()
        if not image.isNull():
            self.currentFrame = QPixmap.fromImage(image)
            self.update()

    def mousePressEvent(self, event):
        if not self.labelingEnabled:
            return

        if event.button() == Qt.MouseButton.LeftButton:
            self.isDrawing = True
            self.startPoint = event.pos()
            self.endPoint = event.pos()
            self.update()

    def mouseMoveEvent(self, event):
        if self.isDrawing:
            self.endPoint = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.isDrawing = False
            rect = QRect(self.startPoint, self.endPoint).normalized()
            if not rect.isNull():
                self.boundingBoxes.append((rect, self.currentLabel))
            self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)

    
        if not self.currentFrame.isNull():
            painter.drawPixmap(0, 0, self.width(), self.height(), self.currentFrame)

        pen = QPen(QColor(255, 0, 0), 3)  # red bounding box
        painter.setPen(pen)

        for (rect, label) in self.boundingBoxes:
            painter.drawRect(rect)

            # label text
            painter.setPen(QColor(255, 0, 0)) 
            painter.drawText(
                rect.x() + 2,
                rect.y() + 16,
                label
            )

            painter.setPen(pen)

        if self.isDrawing:
            painter.setPen(QColor(255, 0, 0))
            liveRect = QRect(self.startPoint, self.endPoint).normalized()
            painter.drawRect(liveRect)

        painter.end()

    def undo_last_bounding_box(self):
        if self.boundingBoxes:
            self.boundingBoxes.pop()
            self.update()

    def confirm_bounding_boxes(self, outputDir, selectedLabel):
        if not selectedLabel:
            print("No label selected!")
            return
        if not outputDir:
            print("No output directory set!")
            return
        if self.currentFrame.isNull():
            print("No current frame to save from!")
            return

        scale_x = self.currentFrame.width() / self.width()
        scale_y = self.currentFrame.height() / self.height()

        for rect in self.boundingBoxes:
            x = int(rect.x() * scale_x)
            y = int(rect.y() * scale_y)
            w = int(rect.width() * scale_x)
            h = int(rect.height() * scale_y)
            rImg = QRect(x, y, w, h)
            cropped = self.currentFrame.copy(rImg)

            labelPath = os.path.join(outputDir, selectedLabel)
            os.makedirs(labelPath, exist_ok=True)
            filename = f"{uuid.uuid4().hex}.png"
            fullPath = os.path.join(labelPath, filename)
            cropped.save(fullPath)
            print("Saved:", fullPath)

        # clear bounding boxes
        self.boundingBoxes.clear()
        self.update()
