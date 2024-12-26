# player.py
from PyQt6.QtWidgets import (
    QWidget, QPushButton, QFileDialog, QHBoxLayout, QVBoxLayout, QLabel, QSlider
)
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput, QVideoSink
from PyQt6.QtCore import QUrl, Qt
from overlay import VideoLabel
from labels import LabelSidebar
import os

class VideoPlayer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CDL Image Labelling")
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        # media
        self.mediaPlayer = QMediaPlayer()
        self.audioOutput = QAudioOutput()
        self.mediaPlayer.setAudioOutput(self.audioOutput)

        self.videoSink = QVideoSink()
        self.mediaPlayer.setVideoOutput(self.videoSink)

        self.outputDir = ""  # output directory

        # labels
        self.currentTimeLabel = QLabel("0:00")
        self.totalTimeLabel = QLabel("0:00")

        # signals
        self.mediaPlayer.positionChanged.connect(self.updatePosition)
        self.mediaPlayer.durationChanged.connect(self.updateDuration)

        # slider
        self.positionSlider = QSlider(Qt.Orientation.Horizontal)
        self.positionSlider.sliderMoved.connect(self.mediaPlayer.setPosition)

        # sidebar
        self.labelSidebar = LabelSidebar()
        self.labelSidebar.labelList.currentItemChanged.connect(self.on_label_selected)

        # videolabel
        self.videoLabel = VideoLabel()
        self.videoSink.videoFrameChanged.connect(self.videoLabel.setVideoFrame)

        # buttons
        self.openButton = QPushButton("Open File")
        self.openButton.clicked.connect(self.open_file)

        self.playPauseButton = QPushButton("Play/Pause")
        self.playPauseButton.clicked.connect(self.toggle_play_pause)

        self.undoButton = QPushButton("Undo")
        self.undoButton.clicked.connect(self.undo_last_box)

        self.confirmButton = QPushButton("Confirm")
        self.confirmButton.clicked.connect(self.confirm_boxes)

        self.chooseDirButton = QPushButton("Choose Output Dir")
        self.chooseDirButton.clicked.connect(self.choose_output_directory)

        
        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(self.openButton)
        buttonLayout.addWidget(self.playPauseButton)
        buttonLayout.addWidget(self.undoButton)
        buttonLayout.addWidget(self.confirmButton)
        buttonLayout.addWidget(self.chooseDirButton)

        
        timeLayout = QHBoxLayout()
        timeLayout.addWidget(self.currentTimeLabel)
        timeLayout.addWidget(self.positionSlider, 1)
        timeLayout.addWidget(self.totalTimeLabel)

        
        videoLayout = QVBoxLayout()
        videoLayout.addWidget(self.videoLabel, 5)
        videoLayout.addLayout(timeLayout)
        videoLayout.addWidget(self.positionSlider)
        videoLayout.addLayout(buttonLayout)

        mainHL = QHBoxLayout()
        mainHL.addWidget(self.labelSidebar, 1)
        mainHL.addLayout(videoLayout, 4)

        self.setLayout(mainHL)

    def choose_output_directory(self):
        dirName = QFileDialog.getExistingDirectory(self, "Select Output Directory", ".")
        if dirName:
            self.outputDir = dirName
            print("Output directory set to:", self.outputDir)
            self.import_labels_from_directory(dirName)

    def import_labels_from_directory(self, rootDir):
        self.labelSidebar.labelList.clear()
        for item in os.listdir(rootDir):
            path = os.path.join(rootDir, item)
            if os.path.isdir(path):
                self.labelSidebar.labelList.addItem(item)

    def open_file(self):
        fileName, _ = QFileDialog.getOpenFileName(
            self,
            "Open Video File",
            ".",
            "Video Files (*.mp4 *.avi *.mkv *.mov *.wmv);;All Files (*)"
        )
        if fileName:
            self.mediaPlayer.setSource(QUrl.fromLocalFile(fileName))
            self.mediaPlayer.play()

    def toggle_play_pause(self):
        if self.mediaPlayer.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.mediaPlayer.pause()
            self.videoLabel.enableLabeling(True)
            current_time = self.mediaPlayer.position()
            print(f"Paused at {current_time} ms for labeling.")
        else:
            self.mediaPlayer.play()
            self.videoLabel.enableLabeling(False)

    def undo_last_box(self):
        self.videoLabel.undo_last_bounding_box()

    def confirm_boxes(self):
        label = self.labelSidebar.get_selected_label()
        self.videoLabel.confirm_bounding_boxes(self.outputDir, label)

    def on_label_selected(self):
        selectedLabel = self.labelSidebar.get_selected_label()
        self.videoLabel.setCurrentLabel(selectedLabel)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Right:
            self.scrub_video(5000)
        elif event.key() == Qt.Key.Key_Left:
            self.scrub_video(-5000)
        elif event.key() == Qt.Key.Key_Space:
            self.toggle_play_pause()
        else:
            super().keyPressEvent(event)

    def scrub_video(self, ms_offset):
        current_pos = self.mediaPlayer.position()
        duration = self.mediaPlayer.duration()
        new_pos = current_pos + ms_offset
        if new_pos < 0:
            new_pos = 0
        elif new_pos > duration:
            new_pos = duration
        self.mediaPlayer.setPosition(new_pos)

    def updatePosition(self, position_ms):
        self.currentTimeLabel.setText(self.formatTime(position_ms))
        self.positionSlider.setValue(position_ms)

    def updateDuration(self, duration_ms):
        self.totalTimeLabel.setText(self.formatTime(duration_ms))
        self.positionSlider.setRange(0, duration_ms)

    def formatTime(self, ms):
        total_seconds = ms // 1000
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        if hours > 0:
            return f"{hours}:{minutes:02}:{seconds:02}"
        else:
            return f"{minutes}:{seconds:02}"
        

    # focus window for keybindings    
    def showEvent(self, event):
        super().showEvent(event)
        self.setFocus()
