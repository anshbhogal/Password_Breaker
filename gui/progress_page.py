import time
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QProgressBar, QFrame, QGridLayout
)
from PySide6.QtCore import Qt, Signal, QThread
from core.recovery_engine import RecoveryEngine

class RecoveryWorkerThread(QThread):
    progress_updated = Signal(dict)
    finished_signal = Signal(object)
    error_signal = Signal(str)

    def __init__(self, engine: RecoveryEngine, file_path: str, attack_type: str, config: dict, workers: int = None, session_id: int = None):
        super().__init__()
        self.engine = engine
        self.file_path = file_path
        self.attack_type = attack_type
        self.config = config
        self.workers = workers
        self.session_id = session_id

    def run(self):
        try:
            def on_progress(stats):
                self.progress_updated.emit(stats)

            if self.session_id:
                res = self.engine.resume_session(self.session_id, progress_callback=on_progress)
            else:
                res = self.engine.start_recovery(
                    file_path=self.file_path,
                    attack_type=self.attack_type,
                    config=self.config,
                    worker_count=self.workers,
                    progress_callback=on_progress
                )
            self.finished_signal.emit(res)
        except Exception as e:
            self.error_signal.emit(str(e))

class ProgressPage(QWidget):
    recovery_finished = Signal(object, dict)  # (password, stats)

    def __init__(self, engine: RecoveryEngine):
        super().__init__()
        self.engine = engine
        self.worker_thread = None
        self.last_stats = {}
        self.is_paused = False

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        self.lbl_title = QLabel("Password Recovery in Progress...")
        self.lbl_title.setStyleSheet("font-size: 22px; font-weight: bold; color: #38bdf8;")
        self.lbl_subtitle = QLabel("Engine testing candidate passwords locally across CPU cores.")
        self.lbl_subtitle.setStyleSheet("font-size: 14px; color: #94a3b8;")

        layout.addWidget(self.lbl_title)
        layout.addWidget(self.lbl_subtitle)

        # Progress Bar
        self.pbar = QProgressBar()
        self.pbar.setRange(0, 100)
        self.pbar.setValue(0)
        self.pbar.setTextVisible(True)
        self.pbar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #334155;
                border-radius: 10px;
                background-color: #0f172a;
                height: 28px;
                text-align: center;
                color: white;
                font-weight: bold;
                font-size: 13px;
            }
            QProgressBar::chunk {
                background: linear-gradient(90deg, #3b82f6, #10b981);
                border-radius: 9px;
            }
        """)
        layout.addWidget(self.pbar)

        # Live Metrics Grid
        grid_frame = QFrame()
        grid_frame.setStyleSheet("background: #1e293b; border-radius: 12px; border: 1px solid #334155; padding: 16px;")
        grid_lay = QGridLayout(grid_frame)

        self.lbl_tested = QLabel("Tested: 0")
        self.lbl_speed = QLabel("Speed: 0 cand/sec")
        self.lbl_elapsed = QLabel("Elapsed: 00:00:00")
        self.lbl_eta = QLabel("ETA: Calculating...")

        for lbl in (self.lbl_tested, self.lbl_speed, self.lbl_elapsed, self.lbl_eta):
            lbl.setStyleSheet("font-size: 15px; font-weight: 500; color: #f8fafc;")

        grid_lay.addWidget(self.lbl_tested, 0, 0)
        grid_lay.addWidget(self.lbl_speed, 0, 1)
        grid_lay.addWidget(self.lbl_elapsed, 1, 0)
        grid_lay.addWidget(self.lbl_eta, 1, 1)

        layout.addWidget(grid_frame)

        # Control Buttons
        ctrl_lay = QHBoxLayout()
        ctrl_lay.addStretch()

        self.btn_pause = QPushButton("⏸ Pause")
        self.btn_pause.setStyleSheet("""
            QPushButton {
                background-color: #f59e0b;
                color: white;
                font-weight: bold;
                padding: 10px 20px;
                border-radius: 6px;
                border: none;
            }
            QPushButton:hover { background-color: #fbbf24; }
        """)
        self.btn_pause.clicked.connect(self.toggle_pause)

        self.btn_stop = QPushButton("🛑 Stop Recovery")
        self.btn_stop.setStyleSheet("""
            QPushButton {
                background-color: #ef4444;
                color: white;
                font-weight: bold;
                padding: 10px 20px;
                border-radius: 6px;
                border: none;
            }
            QPushButton:hover { background-color: #f87171; }
        """)
        self.btn_stop.clicked.connect(self.stop_recovery)

        ctrl_lay.addWidget(self.btn_pause)
        ctrl_lay.addWidget(self.btn_stop)
        layout.addLayout(ctrl_lay)
        layout.addStretch()

    def start_recovery(self, file_path: str, attack_type: str, config: dict, workers: int = None, session_id: int = None):
        self.pbar.setValue(0)
        self.lbl_title.setText("Password Recovery in Progress...")
        self.is_paused = False
        self.btn_pause.setText("⏸ Pause")

        self.worker_thread = RecoveryWorkerThread(
            engine=self.engine,
            file_path=file_path,
            attack_type=attack_type,
            config=config,
            workers=workers,
            session_id=session_id
        )
        self.worker_thread.progress_updated.connect(self.on_progress_update)
        self.worker_thread.finished_signal.connect(self.on_finished)
        self.worker_thread.error_signal.connect(self.on_error)
        self.worker_thread.start()

    def on_progress_update(self, stats: dict):
        self.last_stats = stats
        pct = int(stats.get("progress_pct", 0))
        self.pbar.setValue(pct)
        self.lbl_tested.setText(f"Tested: {stats.get('tested_count', 0):,} / {stats.get('total_candidates', 0):,}")
        self.lbl_speed.setText(f"Speed: {stats.get('speed_cps', 0):,.0f} cand/sec")
        self.lbl_elapsed.setText(f"Elapsed: {stats.get('elapsed_formatted', '00:00:00')}")
        self.lbl_eta.setText(f"ETA: {stats.get('eta_formatted', '-')}")

    def toggle_pause(self):
        if not self.engine.active_scheduler:
            return
        if self.is_paused:
            self.engine.active_scheduler.resume()
            self.is_paused = False
            self.btn_pause.setText("⏸ Pause")
            self.lbl_title.setText("Password Recovery in Progress...")
        else:
            self.engine.active_scheduler.pause()
            self.is_paused = True
            self.btn_pause.setText("▶ Resume")
            self.lbl_title.setText("Recovery Paused")

    def stop_recovery(self):
        if self.engine.active_scheduler:
            self.engine.active_scheduler.stop()

    def on_finished(self, found_password):
        self.recovery_finished.emit(found_password, self.last_stats)

    def on_error(self, err_msg: str):
        self.lbl_title.setText("Error Encountered")
        self.lbl_subtitle.setText(f"Details: {err_msg}")
