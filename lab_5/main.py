import sys
import os

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QFileDialog, QMessageBox
)
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtCore import Qt, QUrl

from dataset_iterator import FileIterator

class AudioPlayer(QMainWindow):
    def __init__(self, initial_songs: list = None):
        super().__init__()
        self.songs = initial_songs if initial_songs else []
        self.song_iterator = None
        self.current_track = None
        self.player = QMediaPlayer()
        self.init_ui()

    def init_ui(self):
        self.setGeometry(100, 100, 800, 600)
        self.setWindowTitle("My Music Player")
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowMaximizeButtonHint)
        self.setStyleSheet("""
        QMainWindow {
            background-image: url(background.jpg);
            background-position: center;
            background-repeat: no-repeat;
        }
        QLabel { color: #f0f0f0; background: rgba(0,0,0,0.6); }
        QPushButton {
            background-color: #8B4513;
            color: white;
            border: 2px solid #A0522D;
            border-radius: 15px;
            padding: 10px 20px;
            font-weight: bold;
            font-size: 14px;
        }
        QPushButton:hover {
            background-color: rgba(255, 255, 255, 0.3);
        }
        """)
        main_layout = QVBoxLayout()

        # Кнопки загрузки
        buttons_load_layout = QHBoxLayout()
        self.btn_load_csv = QPushButton("📄 Загрузить из CSV")
        self.btn_load_csv.clicked.connect(self.load_csv)
        buttons_load_layout.addWidget(self.btn_load_csv)

        self.btn_add_folder = QPushButton("📁 Добавить треки из папки")
        self.btn_add_folder.clicked.connect(self.add_folder)
        buttons_load_layout.addWidget(self.btn_add_folder)

        main_layout.addLayout(buttons_load_layout)
        main_layout.addStretch()

        # Информация о треке
        self.track_name_label = QLabel("Название трека: --")
        self.track_name_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.track_name_label)

        self.track_duration_label = QLabel("Длительность: --")
        self.track_duration_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.track_duration_label)

        # Кнопки управления
        buttons_layout = QHBoxLayout()
        self.btn_prev = QPushButton("⏮ Назад")
        self.btn_play = QPushButton("▶ Воспроизведение")
        self.btn_next = QPushButton("⏭ Вперед")

        buttons_layout.addWidget(self.btn_prev)
        buttons_layout.addWidget(self.btn_play)
        buttons_layout.addWidget(self.btn_next)
        main_layout.addLayout(buttons_layout)

        self.track_count_label = QLabel("Треки: 0/0")
        self.track_count_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.track_count_label)

        main_layout.addStretch()
        central_widget.setLayout(main_layout)

        # Подключение сигналов
        self.btn_play.clicked.connect(self.play_track)
        self.btn_next.clicked.connect(self.next_track)
        self.btn_prev.clicked.connect(self.prev_track)
        self.player.mediaStatusChanged.connect(self.on_media_status_changed)
        self.player.durationChanged.connect(self.on_duration_changed)

        self.update_buttons_state()

    def load_csv(self):
        csv_path, _ = QFileDialog.getOpenFileName(self, "Выберите CSV файл", "", "CSV Files (*.csv)")
        if csv_path:
            self.song_iterator = FileIterator(csv_path)

            if len(self.song_iterator.file_list) > 0:
                self.next_track()
            else:
                QMessageBox.warning(self, "Пустой датасет", "В CSV нет MP3 файлов!")
            self.update_buttons_state()
            QMessageBox.information(self, "Загрузка", f"Найдено {len(self.song_iterator.file_list)} трек(ов)")

    def add_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Выберите папку с треками")
        if folder_path:
            self.song_iterator = FileIterator(folder_path)
            if len(self.song_iterator.file_list) > 0:
                self.next_track()
            else:
                QMessageBox.warning(self, "Пустая папка", "В папке нет MP3 файлов!")
            self.update_buttons_state()
            QMessageBox.information(self, "Загрузка", f"Найдено {len(self.song_iterator.file_list)} трек(ов)")

    def update_buttons_state(self):
        has_songs = self.song_iterator is not None and len(self.song_iterator.file_list) > 0
        self.btn_play.setEnabled(has_songs and self.current_track is not None)
        self.btn_next.setEnabled(has_songs)
        self.btn_prev.setEnabled(has_songs)

    def update_track_info(self):
        if self.current_track:
            track_name = os.path.basename(self.current_track)
            self.track_name_label.setText(f"Название трека: {track_name}")
            self.player.setMedia(QMediaContent(QUrl.fromLocalFile(self.current_track)))

            current_pos = self.song_iterator.index
            total = len(self.song_iterator.file_list)
            self.track_count_label.setText(f"Треки: {current_pos}/{total}")

    def next_track(self):
        try:
            self.current_track = next(self.song_iterator)
        except StopIteration:
            self.song_iterator.index = 0
            try:
                self.current_track = next(self.song_iterator)
            except StopIteration:
                self.current_track = None
                self.track_name_label.setText("Название трека: --")
                return

        self.update_track_info()
        self.player.play()
        self.play_b_change()

    def prev_track(self):
        if self.song_iterator:
            self.current_track = self.song_iterator.prev()
            self.update_track_info()
            self.player.play()
            self.play_b_change()

    def play_track(self):
        if self.player.state() == QMediaPlayer.PlayingState:
            self.player.pause()
            self.play_b_change()
        else:
            self.player.play()
            self.play_b_change()

    def play_b_change(self):
        if self.player.state() != QMediaPlayer.PlayingState:
            self.btn_play.setText("▶ Воспроизведение")
        else:
            self.btn_play.setText("⏸ Пауза")

    def on_media_status_changed(self, status):
        if status == QMediaPlayer.EndOfMedia:
            self.next_track()

    def on_duration_changed(self, duration_ms):
        if duration_ms > 0:
            seconds = duration_ms // 1000
            minutes = seconds // 60
            seconds = seconds % 60
            self.track_duration_label.setText(f"Длительность: {minutes}:{seconds:02d}")

def main():
    app = QApplication(sys.argv)
    window = AudioPlayer()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
