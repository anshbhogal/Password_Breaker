import multiprocessing
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox,
    QComboBox, QFrame, QPushButton, QMessageBox
)
from PySide6.QtCore import Qt, Signal
from accelerators import get_available_accelerators

class SettingsPage(QWidget):
    settings_saved = Signal(dict)

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        title = QLabel("Engine & Parallelization Settings")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #f8fafc;")
        desc = QLabel("Configure CPU worker concurrency, acceleration hardware, and session defaults.")
        desc.setStyleSheet("font-size: 14px; color: #94a3b8;")

        layout.addWidget(title)
        layout.addWidget(desc)

        card = QFrame()
        card.setStyleSheet("background: #1e293b; border-radius: 12px; border: 1px solid #334155; padding: 20px;")
        card_lay = QVBoxLayout(card)

        # CPU Worker Settings
        cpu_row = QHBoxLayout()
        cpu_label = QLabel("CPU Worker Threads:")
        cpu_label.setStyleSheet("font-size: 15px; color: #e2e8f0;")
        
        self.spn_workers = QSpinBox()
        cpu_count = multiprocessing.cpu_count()
        self.spn_workers.setRange(1, cpu_count * 2)
        self.spn_workers.setValue(cpu_count)
        self.spn_workers.setStyleSheet("padding: 6px; background: #0f172a; color: white; border-radius: 6px;")

        cpu_row.addWidget(cpu_label)
        cpu_row.addWidget(self.spn_workers)
        card_lay.addLayout(cpu_row)

        cpu_info = QLabel(f"Detected System CPU Cores: {cpu_count}")
        cpu_info.setStyleSheet("font-size: 13px; color: #64748b; margin-bottom: 12px;")
        card_lay.addWidget(cpu_info)

        # Acceleration Hardware Settings
        acc_row = QHBoxLayout()
        acc_label = QLabel("Acceleration Engine:")
        acc_label.setStyleSheet("font-size: 15px; color: #e2e8f0;")

        self.cmb_acc = QComboBox()
        self.cmb_acc.setStyleSheet("padding: 6px; background: #0f172a; color: white; border-radius: 6px;")
        
        available = get_available_accelerators()
        for acc in available:
            self.cmb_acc.addItem(acc.name())

        acc_row.addWidget(acc_label)
        acc_row.addWidget(self.cmb_acc)
        card_lay.addLayout(acc_row)

        layout.addWidget(card)

        # Save Button
        btn_lay = QHBoxLayout()
        btn_lay.addStretch()
        self.btn_save = QPushButton("💾 Save Settings")
        self.btn_save.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6;
                color: white;
                font-weight: bold;
                font-size: 14px;
                padding: 10px 24px;
                border-radius: 6px;
                border: none;
            }
            QPushButton:hover { background-color: #60a5fa; }
        """)
        self.btn_save.clicked.connect(self.save)
        btn_lay.addWidget(self.btn_save)

        layout.addLayout(btn_lay)
        layout.addStretch()

    def save(self):
        settings = {
            "workers": self.spn_workers.value(),
            "accelerator": self.cmb_acc.currentText()
        }
        self.settings_saved.emit(settings)
        QMessageBox.information(self, "Settings Saved", "Configuration saved successfully!")
