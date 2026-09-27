import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTabWidget, QLineEdit, QCheckBox, QSpinBox, QFileDialog, QFrame,
    QTextEdit, QComboBox
)
from PySide6.QtCore import Qt, Signal
from core.candidate_engine import CandidateGenerator
from gui.guided_wizard import GuidedWizardWidget

class AttackPage(QWidget):
    attack_configured = Signal(str, dict)

    def __init__(self):
        super().__init__()
        self.file_path = None
        self.file_info = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        title = QLabel("Choose & Configure Recovery Strategy")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #f8fafc;")
        desc = QLabel("Select a guided recovery wizard or an advanced attack vector for your document.")
        desc.setStyleSheet("font-size: 14px; color: #94a3b8;")

        layout.addWidget(title)
        layout.addWidget(desc)

        # Tabs for attack modes
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #334155;
                background: #1e293b;
                border-radius: 8px;
            }
            QTabBar::tab {
                background: #0f172a;
                color: #94a3b8;
                padding: 10px 18px;
                font-weight: bold;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
            }
            QTabBar::tab:selected {
                background: #1e293b;
                color: #60a5fa;
                border-bottom: 2px solid #3b82f6;
            }
        """)

        # 0. Guided Wizard Tab (matching step layout)
        self.guided_wizard = GuidedWizardWidget()
        self.guided_wizard.wizard_completed.connect(self.on_wizard_completed)
        self.tabs.addTab(self.guided_wizard, "✨ Guided Password Wizard")

        # 1. Dictionary Tab
        self.tab_dict = QWidget()
        dict_lay = QVBoxLayout(self.tab_dict)
        self.txt_wordlist = QLineEdit("resources/wordlists/default.txt")
        self.txt_wordlist.setStyleSheet("padding: 8px; background: #0f172a; color: white; border: 1px solid #334155; border-radius: 6px;")
        btn_browse_wl = QPushButton("Browse...")
        btn_browse_wl.clicked.connect(self.browse_wordlist)
        btn_browse_wl.setStyleSheet("padding: 8px 16px; background: #3b82f6; color: white; border-radius: 6px;")

        wl_row = QHBoxLayout()
        wl_row.addWidget(QLabel("Wordlist Path:"))
        wl_row.addWidget(self.txt_wordlist)
        wl_row.addWidget(btn_browse_wl)
        dict_lay.addLayout(wl_row)

        dict_lay.addWidget(QLabel("Custom Words (one per line or comma-separated):"))
        self.txt_custom = QTextEdit()
        self.txt_custom.setPlaceholderText("ansh\nAnsh\n2004\nbhogal\nikgptu")
        self.txt_custom.setStyleSheet("background: #0f172a; color: white; border: 1px solid #334155; border-radius: 6px;")
        self.txt_custom.setMaximumHeight(100)
        dict_lay.addWidget(self.txt_custom)
        dict_lay.addStretch()
        self.tabs.addTab(self.tab_dict, "Dictionary")

        # 2. Rule / Mutation Tab
        self.tab_rules = QWidget()
        rules_lay = QVBoxLayout(self.tab_rules)
        rules_lay.addWidget(QLabel("Base Words (comma-separated):"))
        self.txt_rule_base = QLineEdit("ansh, bhogal, college, 2004")
        self.txt_rule_base.setStyleSheet("padding: 8px; background: #0f172a; color: white; border: 1px solid #334155; border-radius: 6px;")
        rules_lay.addWidget(self.txt_rule_base)

        self.chk_append_digits = QCheckBox("Append Digits (0-9)")
        self.chk_append_digits.setChecked(True)
        self.chk_prepend_digits = QCheckBox("Prepend Digits (0-9)")
        self.chk_append_symbols = QCheckBox("Append Symbols (!, @, #, $, %)")
        self.chk_append_symbols.setChecked(True)
        self.chk_substitutions = QCheckBox("Common Substitutions (a->@, s->$, i->1, e->3)")
        self.chk_substitutions.setChecked(True)

        for chk in (self.chk_append_digits, self.chk_prepend_digits, self.chk_append_symbols, self.chk_substitutions):
            chk.setStyleSheet("color: #e2e8f0; font-size: 14px;")
            rules_lay.addWidget(chk)
        rules_lay.addStretch()
        self.tabs.addTab(self.tab_rules, "Rule / Mutation")

        # 3. Mask Tab
        self.tab_mask = QWidget()
        mask_lay = QVBoxLayout(self.tab_mask)
        mask_lay.addWidget(QLabel("Mask Pattern:"))
        self.txt_mask = QLineEdit("Ansh?d?d?d?d")
        self.txt_mask.setStyleSheet("padding: 8px; background: #0f172a; color: white; border: 1px solid #334155; border-radius: 6px;")
        mask_lay.addWidget(self.txt_mask)

        mask_legend = QLabel(
            "Tokens:\n"
            "?l = lowercase (a-z)   ?u = uppercase (A-Z)\n"
            "?d = digits (0-9)      ?s = special (!@#$%^&*)\n"
            "?a = printable chars   Example: Ansh?d?d?d?d"
        )
        mask_legend.setStyleSheet("color: #94a3b8; font-size: 13px; background: #0f172a; padding: 10px; border-radius: 6px;")
        mask_lay.addWidget(mask_legend)
        mask_lay.addStretch()
        self.tabs.addTab(self.tab_mask, "Mask")

        # 4. Hybrid Tab
        self.tab_hybrid = QWidget()
        hyb_lay = QVBoxLayout(self.tab_hybrid)
        hyb_lay.addWidget(QLabel("Base Words (comma-separated):"))
        self.txt_hyb_base = QLineEdit("ansh, bhogal")
        self.txt_hyb_base.setStyleSheet("padding: 8px; background: #0f172a; color: white; border: 1px solid #334155; border-radius: 6px;")
        hyb_lay.addWidget(self.txt_hyb_base)

        hyb_lay.addWidget(QLabel("Prefixes (comma-separated):"))
        self.txt_hyb_pref = QLineEdit("admin, user, test")
        self.txt_hyb_pref.setStyleSheet("padding: 8px; background: #0f172a; color: white; border: 1px solid #334155; border-radius: 6px;")
        hyb_lay.addWidget(self.txt_hyb_pref)

        hyb_lay.addWidget(QLabel("Suffixes (comma-separated):"))
        self.txt_hyb_suff = QLineEdit("123, 2004, @")
        self.txt_hyb_suff.setStyleSheet("padding: 8px; background: #0f172a; color: white; border: 1px solid #334155; border-radius: 6px;")
        hyb_lay.addWidget(self.txt_hyb_suff)
        hyb_lay.addStretch()
        self.tabs.addTab(self.tab_hybrid, "Hybrid")

        # 5. Bounded Brute Force Tab
        self.tab_bf = QWidget()
        bf_lay = QVBoxLayout(self.tab_bf)
        bf_lay.addWidget(QLabel("Charset:"))
        self.txt_bf_charset = QLineEdit("abcdefghijklmnopqrstuvwxyz0123456789")
        self.txt_bf_charset.setStyleSheet("padding: 8px; background: #0f172a; color: white; border: 1px solid #334155; border-radius: 6px;")
        bf_lay.addWidget(self.txt_bf_charset)

        len_row = QHBoxLayout()
        self.spn_min_len = QSpinBox()
        self.spn_min_len.setRange(1, 16)
        self.spn_min_len.setValue(1)
        self.spn_max_len = QSpinBox()
        self.spn_max_len.setRange(1, 16)
        self.spn_max_len.setValue(4)
        
        for spn in (self.spn_min_len, self.spn_max_len):
            spn.setStyleSheet("padding: 6px; background: #0f172a; color: white;")

        len_row.addWidget(QLabel("Min Length:"))
        len_row.addWidget(self.spn_min_len)
        len_row.addWidget(QLabel("Max Length:"))
        len_row.addWidget(self.spn_max_len)
        bf_lay.addLayout(len_row)
        bf_lay.addStretch()
        self.tabs.addTab(self.tab_bf, "Brute Force")

        layout.addWidget(self.tabs)

        # Estimation Card
        self.est_card = QFrame()
        self.est_card.setStyleSheet("background: #0f172a; border-radius: 8px; border: 1px solid #334155; padding: 12px;")
        est_lay = QVBoxLayout(self.est_card)
        self.lbl_est_candidates = QLabel("Estimated Search Space: Calculating...")
        self.lbl_est_candidates.setStyleSheet("font-size: 15px; font-weight: bold; color: #38bdf8;")
        self.lbl_est_time = QLabel("Estimated Max Time @ 10,000 cand/sec: -")
        self.lbl_est_time.setStyleSheet("font-size: 13px; color: #94a3b8;")

        est_lay.addWidget(self.lbl_est_candidates)
        est_lay.addWidget(self.lbl_est_time)
        layout.addWidget(self.est_card)

        # Action Buttons
        btn_row = QHBoxLayout()
        btn_row.addStretch()

        self.btn_start = QPushButton("🚀 Start Recovery Attack")
        self.btn_start.setStyleSheet("""
            QPushButton {
                background: linear-gradient(135deg, #10b981, #059669);
                background-color: #10b981;
                color: white;
                font-weight: bold;
                font-size: 15px;
                padding: 12px 28px;
                border-radius: 8px;
                border: none;
            }
            QPushButton:hover {
                background-color: #34d399;
            }
        """)
        self.btn_start.clicked.connect(self.on_start_clicked)
        btn_row.addWidget(self.btn_start)
        layout.addLayout(btn_row)

        self.tabs.currentChanged.connect(self.update_estimation)

    def set_file_info(self, file_path: str, file_info: dict):
        self.file_path = file_path
        self.file_info = file_info
        self.update_estimation()

    def browse_wordlist(self):
        fname, _ = QFileDialog.getOpenFileName(self, "Select Wordlist File", "", "Text Files (*.txt);;All Files (*.*)")
        if fname:
            self.txt_wordlist.setText(fname)
            self.update_estimation()

    def update_estimation(self):
        idx = self.tabs.currentIndex()
        if idx == 0:  # Guided Wizard
            self.est_card.setVisible(False)
            self.btn_start.setVisible(False)
            return

        self.est_card.setVisible(True)
        self.btn_start.setVisible(True)
        total = 0

        if idx == 1:  # Dictionary
            wl = self.txt_wordlist.text()
            custom = [w.strip() for w in self.txt_custom.toPlainText().replace(',', '\n').split('\n') if w.strip()]
            total = len(custom)
            if os.path.exists(wl):
                try:
                    with open(wl, 'r', encoding='utf-8', errors='ignore') as f:
                        total += sum(1 for line in f if line.strip())
                except Exception:
                    pass
        elif idx == 2:  # Rules
            base = [w.strip() for w in self.txt_rule_base.text().split(',') if w.strip()]
            total = len(base) * 50
        elif idx == 3:  # Mask
            mask = self.txt_mask.text()
            total = CandidateGenerator.calculate_mask_space(mask)
        elif idx == 4:  # Hybrid
            base = [w.strip() for w in self.txt_hyb_base.text().split(',') if w.strip()]
            prefs = [w.strip() for w in self.txt_hyb_pref.text().split(',') if w.strip()]
            suffs = [w.strip() for w in self.txt_hyb_suff.text().split(',') if w.strip()]
            total = max(1, len(base)) * max(1, len(prefs)) * max(1, len(suffs)) * 10
        elif idx == 5:  # Brute force
            cs = self.txt_bf_charset.text()
            min_l = self.spn_min_len.value()
            max_l = self.spn_max_len.value()
            total = CandidateGenerator.calculate_brute_force_space(len(cs), min_l, max_l)

        self.lbl_est_candidates.setText(f"Estimated Search Space: {total:,} candidates")
        sec = total / 10000.0 if total > 0 else 0
        if sec > 86400 * 365:
            self.lbl_est_time.setText("Estimated Max Time: Computationally Impractical (Huge Search Space!)")
            self.lbl_est_time.setStyleSheet("color: #ef4444; font-weight: bold;")
        else:
            mins = sec / 60.0
            self.lbl_est_time.setText(f"Estimated Time @ ~10k cand/sec: {sec:.1f}s ({mins:.1f} mins)")
            self.lbl_est_time.setStyleSheet("color: #94a3b8;")

    def on_wizard_completed(self, attack_type: str, config: dict):
        self.attack_configured.emit(attack_type, config)

    def on_start_clicked(self):
        idx = self.tabs.currentIndex()
        attack_type = "dictionary"
        config = {}

        if idx == 1:
            attack_type = "dictionary"
            custom = [w.strip() for w in self.txt_custom.toPlainText().replace(',', '\n').split('\n') if w.strip()]
            config = {
                "wordlists": [self.txt_wordlist.text()],
                "custom_words": custom
            }
        elif idx == 2:
            attack_type = "rules"
            base = [w.strip() for w in self.txt_rule_base.text().split(',') if w.strip()]
            config = {
                "base_words": base,
                "rules": {
                    "append_digits": self.chk_append_digits.isChecked(),
                    "prepend_digits": self.chk_prepend_digits.isChecked(),
                    "append_symbols_flag": self.chk_append_symbols.isChecked(),
                    "years": ["2024", "2004", "2025", "2026"]
                }
            }
        elif idx == 3:
            attack_type = "mask"
            config = {"mask": self.txt_mask.text()}
        elif idx == 4:
            attack_type = "hybrid"
            base = [w.strip() for w in self.txt_hyb_base.text().split(',') if w.strip()]
            prefs = [w.strip() for w in self.txt_hyb_pref.text().split(',') if w.strip()]
            suffs = [w.strip() for w in self.txt_hyb_suff.text().split(',') if w.strip()]
            config = {"base_words": base, "prefixes": prefs, "suffixes": suffs}
        elif idx == 5:
            attack_type = "brute_force"
            config = {
                "charset": self.txt_bf_charset.text(),
                "min_len": self.spn_min_len.value(),
                "max_len": self.spn_max_len.value()
            }

        self.attack_configured.emit(attack_type, config)
