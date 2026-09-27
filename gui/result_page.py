import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QApplication, QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt, Signal

class ResultPage(QWidget):
    restart_requested = Signal()

    def __init__(self):
        super().__init__()
        self.recovered_password = None
        self.file_path = None
        self.stats = {}

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        self.card = QFrame()
        self.card.setStyleSheet("background: #1e293b; border-radius: 12px; border: 1px solid #334155; padding: 24px;")
        card_lay = QVBoxLayout(self.card)

        self.lbl_status_icon = QLabel("🎉")
        self.lbl_status_icon.setStyleSheet("font-size: 56px;")
        self.lbl_status_icon.setAlignment(Qt.AlignCenter)

        self.lbl_status_title = QLabel("PASSWORD RECOVERED SUCCESSFULLY!")
        self.lbl_status_title.setStyleSheet("font-size: 22px; font-weight: bold; color: #10b981;")
        self.lbl_status_title.setAlignment(Qt.AlignCenter)

        self.lbl_file = QLabel("File: -")
        self.lbl_file.setStyleSheet("font-size: 15px; color: #94a3b8;")
        self.lbl_file.setAlignment(Qt.AlignCenter)

        # Password reveal box
        self.pwd_box = QFrame()
        self.pwd_box.setStyleSheet("background: #0f172a; border-radius: 8px; border: 1px solid #334155; padding: 16px;")
        pwd_lay = QHBoxLayout(self.pwd_box)

        self.lbl_pwd_text = QLabel("••••••••••••")
        self.lbl_pwd_text.setStyleSheet("font-size: 20px; font-weight: bold; font-family: monospace; color: #38bdf8;")

        self.btn_reveal = QPushButton("👁 Reveal")
        self.btn_reveal.setStyleSheet("padding: 6px 14px; background: #3b82f6; color: white; border-radius: 6px; font-weight: bold;")
        self.btn_reveal.clicked.connect(self.toggle_reveal)

        self.btn_copy = QPushButton("📋 Copy")
        self.btn_copy.setStyleSheet("padding: 6px 14px; background: #10b981; color: white; border-radius: 6px; font-weight: bold;")
        self.btn_copy.clicked.connect(self.copy_password)

        pwd_lay.addWidget(QLabel("Password:"))
        pwd_lay.addWidget(self.lbl_pwd_text, 1)
        pwd_lay.addWidget(self.btn_reveal)
        pwd_lay.addWidget(self.btn_copy)

        self.lbl_summary = QLabel("Candidates tested: 0 | Time: 00:00:00 | Speed: 0 cand/sec")
        self.lbl_summary.setStyleSheet("font-size: 14px; color: #e2e8f0;")
        self.lbl_summary.setAlignment(Qt.AlignCenter)

        card_lay.addWidget(self.lbl_status_icon)
        card_lay.addWidget(self.lbl_status_title)
        card_lay.addWidget(self.lbl_file)
        card_lay.addSpacing(10)
        card_lay.addWidget(self.pwd_box)
        card_lay.addSpacing(10)
        card_lay.addWidget(self.lbl_summary)

        layout.addWidget(self.card)

        # Action Buttons
        btn_lay = QHBoxLayout()
        self.btn_report = QPushButton("📄 Save Recovery Report")
        self.btn_report.setStyleSheet("padding: 10px 20px; background: #475569; color: white; border-radius: 6px; font-weight: bold;")
        self.btn_report.clicked.connect(self.save_report)

        self.btn_restart = QPushButton("🔄 Recover Another Document")
        self.btn_restart.setStyleSheet("padding: 10px 20px; background: #2563eb; color: white; border-radius: 6px; font-weight: bold;")
        self.btn_restart.clicked.connect(lambda: self.restart_requested.emit())

        btn_lay.addWidget(self.btn_report)
        btn_lay.addStretch()
        btn_lay.addWidget(self.btn_restart)

        layout.addLayout(btn_lay)
        layout.addStretch()
        self.is_revealed = False

    def display_result(self, file_path: str, password: str, stats: dict):
        self.file_path = file_path
        self.recovered_password = password
        self.stats = stats or {}
        self.is_revealed = False

        self.lbl_file.setText(f"Target Document: {os.path.basename(file_path)}")

        if password:
            self.lbl_status_icon.setText("🎉")
            self.lbl_status_title.setText("PASSWORD RECOVERED SUCCESSFULLY!")
            self.lbl_status_title.setStyleSheet("font-size: 22px; font-weight: bold; color: #10b981;")
            self.lbl_pwd_text.setText("••••••••••••")
            self.pwd_box.setVisible(True)
        else:
            self.lbl_status_icon.setText("❌")
            self.lbl_status_title.setText("PASSWORD NOT FOUND IN SEARCH SPACE")
            self.lbl_status_title.setStyleSheet("font-size: 22px; font-weight: bold; color: #ef4444;")
            self.pwd_box.setVisible(False)

        cnt = self.stats.get('tested_count', 0)
        el = self.stats.get('elapsed_formatted', '00:00:00')
        spd = self.stats.get('speed_cps', 0)
        self.lbl_summary.setText(f"Candidates tested: {cnt:,} | Time: {el} | Speed: {spd:,.0f} cand/sec")

    def toggle_reveal(self):
        if not self.recovered_password:
            return
        if self.is_revealed:
            self.lbl_pwd_text.setText("••••••••••••")
            self.btn_reveal.setText("👁 Reveal")
            self.is_revealed = False
        else:
            self.lbl_pwd_text.setText(self.recovered_password)
            self.btn_reveal.setText("🙈 Hide")
            self.is_revealed = True

    def copy_password(self):
        if self.recovered_password:
            QApplication.clipboard().setText(self.recovered_password)
            QMessageBox.information(self, "Copied", "Password copied to clipboard!")

    def save_report(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save Recovery Report", "recovery_report.txt", "Text Files (*.txt)")
        if path:
            with open(path, 'w', encoding='utf-8') as f:
                f.write("====================================================\n")
                f.write("      LOCAL RECOVERY SYSTEM REPORT\n")
                f.write("====================================================\n\n")
                f.write(f"Target File: {self.file_path}\n")
                f.write(f"Status     : {'SUCCESS' if self.recovered_password else 'NOT FOUND'}\n")
                if self.recovered_password:
                    f.write(f"Password   : {self.recovered_password}\n")
                f.write(f"Candidates : {self.stats.get('tested_count', 0):,}\n")
                f.write(f"Elapsed    : {self.stats.get('elapsed_formatted', '-')}\n")
                f.write(f"Speed      : {self.stats.get('speed_cps', 0):,.0f} cand/sec\n")
            QMessageBox.information(self, "Saved", f"Report saved to {path}")
