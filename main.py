# main.py
import sys
from PyQt6.QtWidgets import QApplication
from player import VideoPlayer

if __name__ == "__main__":
    app = QApplication(sys.argv)
    player = VideoPlayer()
    player.resize(1200, 800)
    player.show()
    sys.exit(app.exec())
