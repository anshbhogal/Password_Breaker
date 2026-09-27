from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QStackedWidget, QSpinBox, QLineEdit, QCheckBox, QFrame, QGridLayout
)
from PySide6.QtCore import Qt, Signal
from core.candidate_engine import CandidateGenerator

class StepIndicator(QFrame):
    def __init__(self, step_num: int, title: str):
        super().__init__()
        self.step_num = step_num
        self.title = title

        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(8, 8, 8, 8)
        self.layout.setSpacing(12)

        self.lbl_num = QLabel(str(step_num))
        self.lbl_num.setFixedSize(28, 28)
        self.lbl_num.setAlignment(Qt.AlignCenter)
        self.lbl_num.setStyleSheet("""
            border-radius: 14px;
            background-color: #3b82f6;
            color: white;
            font-weight: bold;
        """)

        self.lbl_title = QLabel(title)
        self.lbl_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #94a3b8;")

        self.layout.addWidget(self.lbl_num)
        self.layout.addWidget(self.lbl_title)
        self.layout.addStretch()

        self.set_active(False)

    def set_active(self, active: bool):
        if active:
            self.setStyleSheet("background-color: rgba(59, 130, 246, 0.15); border-radius: 8px;")
            self.lbl_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #60a5fa;")
            self.lbl_num.setStyleSheet("border-radius: 14px; background-color: #2563eb; color: white; font-weight: bold;")
        else:
            self.setStyleSheet("background-color: transparent;")
            self.lbl_title.setStyleSheet("font-size: 14px; font-weight: 500; color: #64748b;")
            self.lbl_num.setStyleSheet("border-radius: 14px; background-color: #334155; color: #94a3b8; font-weight: bold;")


class GuidedWizardWidget(QWidget):
    wizard_completed = Signal(str, dict)  # (attack_type, config)

    def __init__(self):
        super().__init__()

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(16)

        # Left step indicator panel
        left_panel = QFrame()
        left_panel.setFixedWidth(210)
        left_panel.setStyleSheet("background-color: #0f172a; border-radius: 12px; border: 1px solid #1e293b;")
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(12, 16, 12, 16)
        left_layout.setSpacing(10)

        self.step_indicators = [
            StepIndicator(1, "Length"),
            StepIndicator(2, "Prefix and Suffix"),
            StepIndicator(3, "Additional details"),
            StepIndicator(4, "Symbols"),
            StepIndicator(5, "Summary")
        ]

        for ind in self.step_indicators:
            left_layout.addWidget(ind)

        left_layout.addStretch()
        main_layout.addWidget(left_panel)

        # Right content area
        right_panel = QFrame()
        right_panel.setStyleSheet("background-color: #1e293b; border-radius: 12px; border: 1px solid #334155;")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(24, 24, 24, 24)

        self.step_stack = QStackedWidget()

        # Step 1: Length
        self.w_step1 = QWidget()
        s1_lay = QVBoxLayout(self.w_step1)
        s1_title = QLabel("Step 1: Password Length")
        s1_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #60a5fa;")
        s1_desc = QLabel("Specify the minimum and maximum expected length of the target password.")
        s1_desc.setStyleSheet("color: #94a3b8; font-size: 13px; margin-bottom: 16px;")
        
        len_grid = QGridLayout()
        self.spn_min = QSpinBox()
        self.spn_min.setRange(1, 32)
        self.spn_min.setValue(8)
        self.spn_max = QSpinBox()
        self.spn_max.setRange(1, 32)
        self.spn_max.setValue(8)
        
        for spn in (self.spn_min, self.spn_max):
            spn.setStyleSheet("padding: 8px; background: #0f172a; color: white; border: 1px solid #334155; border-radius: 6px;")
            spn.valueChanged.connect(self.update_summary)

        len_grid.addWidget(QLabel("Minimum Length:"), 0, 0)
        len_grid.addWidget(self.spn_min, 0, 1)
        len_grid.addWidget(QLabel("Maximum Length:"), 1, 0)
        len_grid.addWidget(self.spn_max, 1, 1)

        s1_lay.addWidget(s1_title)
        s1_lay.addWidget(s1_desc)
        s1_lay.addLayout(len_grid)
        s1_lay.addStretch()

        # Step 2: Prefix and Suffix
        self.w_step2 = QWidget()
        s2_lay = QVBoxLayout(self.w_step2)
        s2_title = QLabel("Step 2: Known Prefix & Suffix")
        s2_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #60a5fa;")
        s2_desc = QLabel("Enter any known characters at the beginning or end of the password.")
        s2_desc.setStyleSheet("color: #94a3b8; font-size: 13px; margin-bottom: 16px;")

        self.txt_prefix = QLineEdit("010")
        self.txt_prefix.setPlaceholderText("e.g. 010 or Ansh (Leave blank if unknown)")
        self.txt_suffix = QLineEdit()
        self.txt_suffix.setPlaceholderText("e.g. 2004 or ! (Leave blank if unknown)")

        for txt in (self.txt_prefix, self.txt_suffix):
            txt.setStyleSheet("padding: 8px; background: #0f172a; color: white; border: 1px solid #334155; border-radius: 6px;")
            txt.textChanged.connect(self.update_summary)

        ps_grid = QGridLayout()
        ps_grid.addWidget(QLabel("Prefix:"), 0, 0)
        ps_grid.addWidget(self.txt_prefix, 0, 1)
        ps_grid.addWidget(QLabel("Suffix:"), 1, 0)
        ps_grid.addWidget(self.txt_suffix, 1, 1)

        s2_lay.addWidget(s2_title)
        s2_lay.addWidget(s2_desc)
        s2_lay.addLayout(ps_grid)
        s2_lay.addStretch()

        # Step 3: Additional details (Lowercase, Uppercase, Numbers)
        self.w_step3 = QWidget()
        s3_lay = QVBoxLayout(self.w_step3)
        s3_title = QLabel("Step 3: Character Sets")
        s3_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #60a5fa;")
        s3_desc = QLabel("Select the types of characters included in the password.")
        s3_desc.setStyleSheet("color: #94a3b8; font-size: 13px; margin-bottom: 16px;")

        self.chk_lower = QCheckBox("Lowercase Letter (a-z)")
        self.chk_upper = QCheckBox("Uppercase Letter (A-Z)")
        self.chk_numbers = QCheckBox("Numbers (0-9)")
        self.chk_numbers.setChecked(True)

        for chk in (self.chk_lower, self.chk_upper, self.chk_numbers):
            chk.setStyleSheet("color: #f8fafc; font-size: 14px; margin-top: 6px;")
            chk.stateChanged.connect(self.update_summary)

        s3_lay.addWidget(s3_title)
        s3_lay.addWidget(s3_desc)
        s3_lay.addWidget(self.chk_lower)
        s3_lay.addWidget(self.chk_upper)
        s3_lay.addWidget(self.chk_numbers)
        s3_lay.addStretch()

        # Step 4: Symbols
        self.w_step4 = QWidget()
        s4_lay = QVBoxLayout(self.w_step4)
        s4_title = QLabel("Step 4: Special Symbols")
        s4_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #60a5fa;")
        s4_desc = QLabel("Include special symbols if applicable.")
        s4_desc.setStyleSheet("color: #94a3b8; font-size: 13px; margin-bottom: 16px;")

        self.chk_symbols = QCheckBox("Enable Special Symbols")
        self.chk_symbols.stateChanged.connect(self.update_summary)

        self.txt_custom_sym = QLineEdit("!@#$%^&*_-+")
        self.txt_custom_sym.setStyleSheet("padding: 8px; background: #0f172a; color: white; border: 1px solid #334155; border-radius: 6px;")
        self.txt_custom_sym.textChanged.connect(self.update_summary)

        s4_lay.addWidget(s4_title)
        s4_lay.addWidget(s4_desc)
        s4_lay.addWidget(self.chk_symbols)
        s4_lay.addWidget(QLabel("Allowed Symbol Set:"))
        s4_lay.addWidget(self.txt_custom_sym)
        s4_lay.addStretch()

        # Step 5: Summary (Matching exactly the UI screenshot format)
        self.w_step5 = QWidget()
        s5_lay = QVBoxLayout(self.w_step5)
        
        self.lbl_s5_prompt = QLabel("This program will use the password information you provided to attempt decryption. Please confirm that the information is correct.")
        self.lbl_s5_prompt.setStyleSheet("color: #f8fafc; font-size: 14px; margin-bottom: 20px;")
        self.lbl_s5_prompt.setWordWrap(True)

        self.lbl_sum_len = QLabel()
        self.lbl_sum_pref = QLabel()
        self.lbl_sum_suff = QLabel()
        self.lbl_sum_lower = QLabel()
        self.lbl_sum_upper = QLabel()
        self.lbl_sum_num = QLabel()
        self.lbl_sum_sym = QLabel()
        self.lbl_sum_space = QLabel()

        summary_box = QFrame()
        summary_box.setStyleSheet("background-color: #0f172a; border-radius: 8px; border: 1px solid #334155; padding: 20px;")
        box_lay = QVBoxLayout(summary_box)
        box_lay.setSpacing(12)

        for lbl in (self.lbl_sum_len, self.lbl_sum_pref, self.lbl_sum_suff, self.lbl_sum_lower, self.lbl_sum_upper, self.lbl_sum_num, self.lbl_sum_sym, self.lbl_sum_space):
            lbl.setStyleSheet("font-size: 15px; color: #f8fafc;")
            lbl.setTextFormat(Qt.RichText)
            box_lay.addWidget(lbl)

        s5_lay.addWidget(self.lbl_s5_prompt)
        s5_lay.addWidget(summary_box)

        tip_frame = QFrame()
        tip_frame.setStyleSheet("background-color: rgba(30, 41, 59, 0.5); border-radius: 8px; padding: 12px; margin-top: 16px;")
        tip_lay = QHBoxLayout(tip_frame)
        tip_lbl = QLabel("Providing accurate password information will speed up the decryption process")
        tip_lbl.setStyleSheet("color: #64748b; font-size: 13px; font-weight: 500;")
        tip_lbl.setAlignment(Qt.AlignCenter)
        tip_lay.addWidget(tip_lbl)

        s5_lay.addWidget(tip_frame)
        s5_lay.addStretch()

        self.step_stack.addWidget(self.w_step1)
        self.step_stack.addWidget(self.w_step2)
        self.step_stack.addWidget(self.w_step3)
        self.step_stack.addWidget(self.w_step4)
        self.step_stack.addWidget(self.w_step5)

        right_layout.addWidget(self.step_stack)

        # Navigation buttons
        nav_lay = QHBoxLayout()
        self.btn_back = QPushButton("← Back")
        self.btn_back.setStyleSheet("padding: 8px 18px; background: #475569; color: white; border-radius: 6px; font-weight: bold;")
        self.btn_back.clicked.connect(self.go_back)

        self.btn_next = QPushButton("Next →")
        self.btn_next.setStyleSheet("padding: 8px 18px; background: #2563eb; color: white; border-radius: 6px; font-weight: bold;")
        self.btn_next.clicked.connect(self.go_next)

        nav_lay.addWidget(self.btn_back)
        nav_lay.addStretch()
        nav_lay.addWidget(self.btn_next)
        right_layout.addLayout(nav_lay)

        main_layout.addWidget(right_panel, 1)

        self.current_step = 0
        self.update_summary()
        self.update_step_ui()

    def update_step_ui(self):
        for i, ind in enumerate(self.step_indicators):
            ind.set_active(i == self.current_step)

        self.step_stack.setCurrentIndex(self.current_step)
        self.btn_back.setEnabled(self.current_step > 0)

        if self.current_step == 4:
            self.update_summary()
            self.btn_next.setText("🚀 Confirm & Start Decryption")
            self.btn_next.setStyleSheet("padding: 10px 22px; background: #10b981; color: white; border-radius: 6px; font-weight: bold;")
        else:
            self.btn_next.setText("Next →")
            self.btn_next.setStyleSheet("padding: 8px 18px; background: #2563eb; color: white; border-radius: 6px; font-weight: bold;")

    def go_back(self):
        if self.current_step > 0:
            self.current_step -= 1
            self.update_step_ui()

    def go_next(self):
        if self.current_step < 4:
            self.current_step += 1
            self.update_step_ui()
        else:
            self.on_finish()

    def update_summary(self):
        min_l = self.spn_min.value()
        max_l = self.spn_max.value()
        pref = self.txt_prefix.text().strip()
        suff = self.txt_suffix.text().strip()

        has_lower = self.chk_lower.isChecked()
        has_upper = self.chk_upper.isChecked()
        has_num = self.chk_numbers.isChecked()
        has_sym = self.chk_symbols.isChecked()

        # Format labels matching exact reference screenshot style
        self.lbl_sum_len.setText(f"<b>Length:</b> &nbsp; {min_l}-{max_l}")
        self.lbl_sum_pref.setText(f"<b>Prefix:</b> &nbsp; {pref if pref else ''}")
        self.lbl_sum_suff.setText(f"<b>Suffix:</b> &nbsp; {suff if suff else ''}")

        lower_str = "a, b, c, d, e, f, g, h, i, j, k, l, m, n, o, p, q, r, s, t, u, v, w, x, y, z" if has_lower else ""
        upper_str = "A, B, C, D, E, F, G, H, I, J, K, L, M, N, O, P, Q, R, S, T, U, V, W, X, Y, Z" if has_upper else ""
        num_str = "0, 1, 2, 3, 4, 5, 6, 7, 8, 9" if has_num else ""
        sym_str = self.txt_custom_sym.text() if has_sym else ""

        self.lbl_sum_lower.setText(f"<b>Lowercase Letter:</b> &nbsp; {lower_str}")
        self.lbl_sum_upper.setText(f"<b>Uppercase Letter:</b> &nbsp; {upper_str}")
        self.lbl_sum_num.setText(f"<b>Numbers:</b> &nbsp; {num_str}")
        self.lbl_sum_sym.setText(f"<b>Symbols:</b> &nbsp; {sym_str}")

        # Build charset & search space
        charset = ""
        if has_lower: charset += "abcdefghijklmnopqrstuvwxyz"
        if has_upper: charset += "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        if has_num: charset += "0123456789"
        if has_sym: charset += self.txt_custom_sym.text()
        if not charset: charset = "0123456789"

        var_len_min = max(1, min_l - len(pref) - len(suff))
        var_len_max = max(1, max_l - len(pref) - len(suff))
        total = CandidateGenerator.calculate_brute_force_space(len(charset), var_len_min, var_len_max)
        self.lbl_sum_space.setText(f"<b>Estimated Candidates:</b> &nbsp; {total:,}")

    def on_finish(self):
        min_l = self.spn_min.value()
        max_l = self.spn_max.value()
        pref = self.txt_prefix.text().strip()
        suff = self.txt_suffix.text().strip()

        has_lower = self.chk_lower.isChecked()
        has_upper = self.chk_upper.isChecked()
        has_num = self.chk_numbers.isChecked()
        has_sym = self.chk_symbols.isChecked()

        charset = ""
        if has_lower: charset += "abcdefghijklmnopqrstuvwxyz"
        if has_upper: charset += "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        if has_num: charset += "0123456789"
        if has_sym: charset += self.txt_custom_sym.text()
        if not charset: charset = "0123456789"

        var_len_min = max(1, min_l - len(pref) - len(suff))
        var_len_max = max(1, max_l - len(pref) - len(suff))

        config = {
            "charset": charset,
            "min_len": var_len_min,
            "max_len": var_len_max,
            "prefixes": [pref] if pref else [],
            "suffixes": [suff] if suff else []
        }

        self.wizard_completed.emit("brute_force", config)
