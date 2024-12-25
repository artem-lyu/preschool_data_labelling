# player.py
from PyQt6.QtWidgets import QWidget, QPushButton, QFileDialog, QHBoxLayout, QVBoxLayout
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput, QVideoSink
from PyQt6.QtCore import QUrl, Qt
from overlay import VideoLabel
from labels import LabelSidebar

class VideoPlayer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Video Labeler with Undo/Confirm")

        # Media
        self.mediaPlayer = QMediaPlayer()
        self.audioOutput = QAudioOutput()
        self.mediaPlayer.setAudioOutput(self.audioOutput)

        self.videoSink = QVideoSink()
        self.mediaPlayer.setVideoOutput(self.videoSink)

        self.outputDir = ""  # output dir

        # label sidebar
        self.labelSidebar = LabelSidebar()

        # video label
        self.videoLabel = VideoLabel()
        self.videoSink.videoFrameChanged.connect(self.videoLabel.setVideoFrame)

        # Buttons
        self.openButton = QPushButton("Open")
        self.openButton.clicked.connect(self.open_file)

        self.playPauseButton = QPushButton("Play/Pause")
        self.playPauseButton.clicked.connect(self.toggle_play_pause)

        self.pauseButton = QPushButton("Pause/Label")
        self.pauseButton.clicked.connect(self.pause_for_labeling)

        self.undoButton = QPushButton("Undo")
        self.undoButton.clicked.connect(self.undo_last_box)

        self.confirmButton = QPushButton("Confirm")
        self.confirmButton.clicked.connect(self.confirm_boxes)

        self.chooseDirButton = QPushButton("Choose Output Dir")
        self.chooseDirButton.clicked.connect(self.choose_output_directory)


        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(self.openButton)
        buttonLayout.addWidget(self.playPauseButton)
        buttonLayout.addWidget(self.pauseButton)
        buttonLayout.addWidget(self.undoButton)
        buttonLayout.addWidget(self.confirmButton)
        buttonLayout.addWidget(self.chooseDirButton)

        mainHL = QHBoxLayout()
        mainHL.addWidget(self.labelSidebar, 1)
        videoLayout = QVBoxLayout()
        videoLayout.addWidget(self.videoLabel, 5)
        videoLayout.addLayout(buttonLayout)
        mainHL.addLayout(videoLayout, 4)

        self.setLayout(mainHL)

    def choose_output_directory(self):
        dirName = QFileDialog.getExistingDirectory(self, "Select Output Directory", ".")
        if dirName:
            self.outputDir = dirName
            print("Output directory set to:", self.outputDir)

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
        else:
            self.mediaPlayer.play()

    def pause_for_labeling(self):
        self.mediaPlayer.pause()
        current_time = self.mediaPlayer.position()
        print(f"Paused at {current_time} ms for labeling.")

    def undo_last_box(self):
        self.videoLabel.undo_last_bounding_box()

    def confirm_boxes(self):
        label = self.labelSidebar.get_selected_label()
        self.videoLabel.confirm_bounding_boxes(self.outputDir, label)
