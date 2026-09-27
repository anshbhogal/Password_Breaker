from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QStackedWidget,
    QPushButton, QLabel, QFrame
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QFont
from core.recovery_engine import RecoveryEngine
from gui.file_page import FilePage
from gui.attack_page import AttackPage
from gui.progress_page import ProgressPage
from gui.result_page import ResultPage
from gui.settings_page import SettingsPage

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Local Document Password Recovery System")
        self.resize(1000, 680)
        self.setMinimumSize(900, 600)

        self.engine = RecoveryEngine()
        self.current_file_path = None
        self.current_file_info = None

        # Dark theme stylesheet
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0f172a;
            }
            QWidget {
                color: #f8fafc;
                font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
            }
        """)

        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Sidebar navigation panel
        sidebar = QFrame()
        sidebar.setFixedWidth(220)
        sidebar.setStyleSheet("background-color: #020617; border-right: 1px solid #1e293b;")
        sb_layout = QVBoxLayout(sidebar)
        sb_layout.setContentsMargins(16, 24, 16, 24)
        sb_layout.setSpacing(12)

        logo_label = QLabel("🛡️ DocPass")
        logo_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #3b82f6; margin-bottom: 20px;")
        sb_layout.addWidget(logo_label)

        self.btn_nav_file = self.create_nav_button("1. Select Document")
        self.btn_nav_attack = self.create_nav_button("2. Choose Attack")
        self.btn_nav_progress = self.create_nav_button("3. Recovery Progress")
        self.btn_nav_result = self.create_nav_button("4. Password Result")
        self.btn_nav_settings = self.create_nav_button("⚙ Settings")

        for btn in (self.btn_nav_file, self.btn_nav_attack, self.btn_nav_progress, self.btn_nav_result, self.btn_nav_settings):
            sb_layout.addWidget(btn)

        sb_layout.addStretch()

        footer_lbl = QLabel("100% Local & Offline\nAuthorized Use Only")
        footer_lbl.setStyleSheet("font-size: 11px; color: #64748b;")
        sb_layout.addWidget(footer_lbl)

        main_layout.addWidget(sidebar)

        # Main content stacked widget
        self.stack = QStackedWidget()
        self.file_page = FilePage()
        self.attack_page = AttackPage()
        self.progress_page = ProgressPage(self.engine)
        self.result_page = ResultPage()
        self.settings_page = SettingsPage()

        self.stack.addWidget(self.file_page)
        self.stack.addWidget(self.attack_page)
        self.stack.addWidget(self.progress_page)
        self.stack.addWidget(self.result_page)
        self.stack.addWidget(self.settings_page)

        main_layout.addWidget(self.stack, 1)
        self.setCentralWidget(main_widget)

        # Signal connections
        self.file_page.file_selected.connect(self.on_file_selected)
        self.attack_page.attack_configured.connect(self.on_attack_configured)
        self.progress_page.recovery_finished.connect(self.on_recovery_finished)
        self.result_page.restart_requested.connect(self.on_restart)

        self.btn_nav_file.clicked.connect(lambda: self.switch_page(0))
        self.btn_nav_attack.clicked.connect(lambda: self.switch_page(1))
        self.btn_nav_progress.clicked.connect(lambda: self.switch_page(2))
        self.btn_nav_result.clicked.connect(lambda: self.switch_page(3))
        self.btn_nav_settings.clicked.connect(lambda: self.switch_page(4))

        self.switch_page(0)

    def create_nav_button(self, text: str) -> QPushButton:
        btn = QPushButton(text)
        btn.setCheckable(True)
        btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #94a3b8;
                font-weight: bold;
                font-size: 13px;
                text-align: left;
                padding: 10px 14px;
                border-radius: 8px;
                border: none;
            }
            QPushButton:hover {
                background-color: #1e293b;
                color: #f8fafc;
            }
            QPushButton:checked {
                background-color: #1e293b;
                color: #3b82f6;
                border-left: 3px solid #3b82f6;
            }
        """)
        return btn

    def switch_page(self, index: int):
        self.stack.setCurrentIndex(index)
        btns = [self.btn_nav_file, self.btn_nav_attack, self.btn_nav_progress, self.btn_nav_result, self.btn_nav_settings]
        for i, b in enumerate(btns):
            b.setChecked(i == index)

    def on_file_selected(self, file_path: str, file_info: dict):
        self.current_file_path = file_path
        self.current_file_info = file_info
        self.attack_page.set_file_info(file_path, file_info)
        self.switch_page(1)

    def on_attack_configured(self, attack_type: str, config: dict):
        self.switch_page(2)
        workers = self.settings_page.spn_workers.value()
        self.progress_page.start_recovery(
            file_path=self.current_file_path,
            attack_type=attack_type,
            config=config,
            workers=workers
        )

    def on_recovery_finished(self, found_password, stats: dict):
        self.result_page.display_result(self.current_file_path, found_password, stats)
        self.switch_page(3)

    def on_restart(self):
        self.switch_page(0)
