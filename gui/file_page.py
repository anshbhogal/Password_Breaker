import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFileDialog, QFrame, QGraphicsDropShadowEffect
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QDragEnterEvent, QDropEvent
from core.detector import FileDetector

class DropZoneWidget(QFrame):
    file_dropped = Signal(str)

    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.setObjectName("DropZone")
        self.setMinimumHeight(180)
        self.setStyleSheet("""
            #DropZone {
                border: 2px dashed #3b82f6;
                border-radius: 16px;
                background-color: rgba(30, 41, 59, 0.6);
            }
            #DropZone:hover {
                border-color: #60a5fa;
                background-color: rgba(30, 41, 59, 0.9);
            }
        """)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        self.icon_label = QLabel("📄")
        self.icon_label.setStyleSheet("font-size: 48px;")
        self.icon_label.setAlignment(Qt.AlignCenter)

        self.text_label = QLabel("Drag & Drop your password-protected file here\nor click to browse files")
        self.text_label.setStyleSheet("font-size: 16px; font-weight: 500; color: #94a3b8;")
        self.text_label.setAlignment(Qt.AlignCenter)

        self.sub_label = QLabel("Supported: PDF, DOCX, XLSX, PPTX, DOC, XLS, PPT, ZIP, 7Z")
        self.sub_label.setStyleSheet("font-size: 12px; color: #64748b;")
        self.sub_label.setAlignment(Qt.AlignCenter)

        layout.addWidget(self.icon_label)
        layout.addWidget(self.text_label)
        layout.addWidget(self.sub_label)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Select Protected Document", "",
                "Supported Documents (*.pdf *.doc *.docx *.xls *.xlsx *.ppt *.pptx *.zip *.7z);;All Files (*.*)"
            )
            if file_path:
                self.file_dropped.emit(file_path)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            if file_path:
                self.file_dropped.emit(file_path)

class FilePage(QWidget):
    file_selected = Signal(str, dict)

    def __init__(self):
        super().__init__()
        self.selected_file_path = None
        self.file_info = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        # Header
        title = QLabel("Select Target Document")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #f8fafc;")
        desc = QLabel("Choose a password-protected document from your local storage to analyze encryption details.")
        desc.setStyleSheet("font-size: 14px; color: #94a3b8;")

        layout.addWidget(title)
        layout.addWidget(desc)

        # Drop Zone
        self.drop_zone = DropZoneWidget()
        self.drop_zone.file_dropped.connect(self.on_file_loaded)
        layout.addWidget(self.drop_zone)

        # File Analysis Card
        self.info_card = QFrame()
        self.info_card.setStyleSheet("""
            QFrame {
                background-color: #1e293b;
                border-radius: 12px;
                border: 1px solid #334155;
            }
        """)
        self.info_card.setVisible(False)
        info_layout = QVBoxLayout(self.info_card)
        info_layout.setContentsMargins(20, 20, 20, 20)

        card_title = QLabel("Document Analysis & Encryption Summary")
        card_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #60a5fa;")
        info_layout.addWidget(card_title)

        self.lbl_name = QLabel("File Name: -")
        self.lbl_format = QLabel("Format: -")
        self.lbl_size = QLabel("File Size: -")
        self.lbl_status = QLabel("Encryption Status: -")
        self.lbl_algo = QLabel("Encryption Algorithm: -")
        self.lbl_type = QLabel("Password Scope: -")

        for lbl in (self.lbl_name, self.lbl_format, self.lbl_size, self.lbl_status, self.lbl_algo, self.lbl_type):
            lbl.setStyleSheet("font-size: 14px; color: #e2e8f0; margin-top: 4px;")
            info_layout.addWidget(lbl)

        layout.addWidget(self.info_card)

        # Bottom Next button
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.btn_next = QPushButton("Configure Attack Strategy →")
        self.btn_next.setEnabled(False)
        self.btn_next.setStyleSheet("""
            QPushButton {
                background: linear-gradient(135deg, #3b82f6, #2563eb);
                background-color: #3b82f6;
                color: white;
                font-weight: bold;
                font-size: 14px;
                padding: 12px 24px;
                border-radius: 8px;
                border: none;
            }
            QPushButton:hover {
                background-color: #60a5fa;
            }
            QPushButton:disabled {
                background-color: #475569;
                color: #94a3b8;
            }
        """)
        self.btn_next.clicked.connect(self.on_next_clicked)
        btn_layout.addWidget(self.btn_next)
        layout.addLayout(btn_layout)
        layout.addStretch()

    def on_file_loaded(self, file_path: str):
        self.selected_file_path = file_path
        self.file_info = FileDetector.analyze(file_path)

        self.lbl_name.setText(f"File Name: {self.file_info.get('file_name')}")
        self.lbl_format.setText(f"Format: {self.file_info.get('format')}")
        self.lbl_size.setText(f"File Size: {self.file_info.get('file_size'):,} bytes")
        
        enc_str = "🔒 Password Protected" if self.file_info.get('is_encrypted') else "🔓 Unencrypted / Plain text"
        self.lbl_status.setText(f"Encryption Status: {enc_str}")
        self.lbl_algo.setText(f"Encryption Algorithm: {self.file_info.get('algorithm')}")
        self.lbl_type.setText(f"Password Scope: {self.file_info.get('password_type')}")

        self.info_card.setVisible(True)
        self.btn_next.setEnabled(True)

    def on_next_clicked(self):
        if self.selected_file_path and self.file_info:
            self.file_selected.emit(self.selected_file_path, self.file_info)
