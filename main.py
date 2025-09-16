# pinterest_batch_poster/main.py

import sys
import os
import json
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
    QPushButton, QLabel, QFileDialog, QComboBox, QMessageBox, QFrame
)
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QFont, QIcon
from config import load_settings, save_settings
from pinterest_api import get_boards



class CustomTitleBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(40)
        self.setStyleSheet("background-color: #2d2d2d;")

        layout = QHBoxLayout()
        layout.setContentsMargins(10, 0, 0, 0)

        self.title = QLabel("📌 Pinterest Batch Poster")
        self.title.setStyleSheet("color: white; font-size: 14px;")
        layout.addWidget(self.title)
        layout.addStretch()

        # Minimize
        self.min_btn = QPushButton("🗕")
        self.min_btn.clicked.connect(parent.showMinimized)
        layout.addWidget(self.min_btn)

        # Maximize/Restore
        self.max_btn = QPushButton("⬜")
        self.max_btn.clicked.connect(lambda: parent.showNormal() if parent.isMaximized() else parent.showMaximized())
        layout.addWidget(self.max_btn)

        # Close
        self.close_btn = QPushButton("❌")
        self.close_btn.clicked.connect(parent.close)
        layout.addWidget(self.close_btn)

        for btn in (self.min_btn, self.max_btn, self.close_btn):
            btn.setFixedSize(30, 30)
            btn.setStyleSheet("""
                QPushButton {
                    color: white;
                    background-color: transparent;
                    border: none;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #444;
                }
            """)

        self.setLayout(layout)


class PinterestPosterUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setStyleSheet("background-color: #1e1e1e; color: white; font-family: 'Segoe UI';")

        self.old_pos = None
        self.setMinimumSize(600, 400)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)

        self.title_bar = CustomTitleBar(self)
        main_layout.addWidget(self.title_bar)

        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(15)

        self.pinterest_api_input = self.create_input_field("Pinterest API Key", content_layout)
        self.nvidia_api_input = self.create_input_field("NVIDIA API Key", content_layout)

        # Folder
        folder_layout = QHBoxLayout()
        self.folder_path = QLineEdit()
        self.folder_path.setReadOnly(True)
        self.folder_path.setStyleSheet("background-color: #2a2a2a; padding: 5px; border: 1px solid #555;")
        folder_btn = QPushButton("📂 Обзор")
        folder_btn.clicked.connect(self.select_folder)
        folder_btn.setStyleSheet(self.button_style())
        folder_layout.addWidget(self.folder_path)
        folder_layout.addWidget(folder_btn)
        content_layout.addWidget(QLabel("Папка с изображениями:"))
        content_layout.addLayout(folder_layout)

        # Boards
        content_layout.addWidget(QLabel("Выбор доски:"))
        self.board_dropdown = QComboBox()
        self.board_dropdown.setStyleSheet("background-color: #2a2a2a; padding: 5px; border: 1px solid #555;")
        self.board_dropdown.addItems(["Выберите...", "Board1", "Board2"])  # TODO: подключить API
        content_layout.addWidget(self.board_dropdown)

        # Save
        save_btn = QPushButton("💾 Сохранить настройки")
        save_btn.clicked.connect(self.save_settings)
        save_btn.setStyleSheet(self.button_style())
        content_layout.addWidget(save_btn)

        main_layout.addLayout(content_layout)
        self.setLayout(main_layout)

        self.load_settings_on_start()

    def create_input_field(self, label_text, layout):
        layout.addWidget(QLabel(label_text))
        input_field = QLineEdit()
        input_field.setStyleSheet("background-color: #2a2a2a; padding: 5px; border: 1px solid #555;")
        layout.addWidget(input_field)
        return input_field

    def button_style(self):
        return """
            QPushButton {
                background-color: #3a3a3a;
                color: white;
                padding: 6px 12px;
                border: 1px solid #555;
            }
            QPushButton:hover {
                background-color: #505050;
            }
        """

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Выберите папку")
        if folder:
            self.folder_path.setText(folder)

    def save_settings(self):
        settings = {
            "pinterest_api_key": self.pinterest_api_input.text(),
            "nvidia_api_key": self.nvidia_api_input.text(),
            "image_folder": self.folder_path.text(),
            "selected_board": self.board_dropdown.currentText()
        }
        save_settings(settings)
        QMessageBox.information(self, "Успешно", "Настройки сохранены!")

    def load_settings_on_start(self):
        settings = load_settings()
        if settings:
            self.pinterest_api_input.setText(settings.get("pinterest_api_key", ""))
            self.nvidia_api_input.setText(settings.get("nvidia_api_key", ""))
            self.folder_path.setText(settings.get("image_folder", ""))

            pinterest_key = settings.get("pinterest_api_key", "")
            if pinterest_key:
                boards = get_boards(pinterest_key)
                if boards:
                    self.board_dropdown.clear()
                    self.board_dropdown.addItems(boards)
                    saved_board = settings.get("selected_board", "")
                    if saved_board in boards:
                        self.board_dropdown.setCurrentText(saved_board)
                else:
                    self.board_dropdown.clear()
                    self.board_dropdown.addItem("⚠️ Не удалось загрузить доски")

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.old_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if self.old_pos:
            delta = event.globalPosition().toPoint() - self.old_pos
            self.move(self.pos() + delta)
            self.old_pos = event.globalPosition().toPoint()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PinterestPosterUI()
    window.show()
    sys.exit(app.exec())
