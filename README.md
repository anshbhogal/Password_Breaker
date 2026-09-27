# Local Document Password Recovery System

A high-performance, 100% offline and secure local document password recovery desktop application built with Python 3.12, PySide6, and Multiprocessing. Inspired by commercial password recovery workflows, this software provides local recovery for authorized document password recovery.

## Features

- **100% Local & Offline Security**: No cloud uploads, no password logging, no telemetry.
- **Multiple Recovery Strategies**:
  1. Dictionary Attack (streaming wordlists + custom candidate entry)
  2. Rule / Mutation Attack (casing, substitutions, digit/symbol appending, year combinations)
  3. Mask Attack (`?l`, `?u`, `?d`, `?s`, `?a`)
  4. Pattern-Based Attack
  5. Combined / Hybrid Attack (prefix + base words + suffix + year + symbol)
  6. Bounded Brute-Force Attack
- **Supported File Formats**:
  - **PDF** (`.pdf`) - User/Open encryption password
  - **Microsoft Word** (`.doc`, `.docx`)
  - **Microsoft Excel** (`.xls`, `.xlsx`)
  - **Microsoft PowerPoint** (`.ppt`, `.pptx`)
  - **ZIP Archives** (`.zip`) - PKWARE & AES-128/256
  - **7z Archives** (`.7z`) - AES-256
- **Crash Recovery & Checkpointing**: SQLite-backed session persistence (`recovery.db`).
- **CPU Parallelization**: Auto-detects system cores with worker pool concurrency.
- **Modern PySide6 GUI**: Clean dark-themed graphical interface with real-time statistics (candidates/sec, elapsed time, progress %).
- **CLI Mode**: Full command-line interface support.

---

## Installation & Setup

### Prerequisites
- Python 3.12+

### 1. Create Virtual Environment

**Windows:**
```bash
python -m venv .venv
.venv\Scripts\activate
```

**Linux/macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

---

## Usage Guide

### Launching Graphical User Interface (GUI)
```bash
python app.py
```

### Launching Command Line Interface (CLI)

#### 1. Analyze Document Encryption
```bash
python cli.py analyze document.pdf
```

#### 2. Start Dictionary Recovery Attack
```bash
python cli.py recover --file document.pdf --mode dictionary --wordlist resources/wordlists/default.txt
```

#### 3. Start Mask Recovery Attack
```bash
python cli.py recover --file document.pdf --mode mask --mask "Ansh?d?d?d?d"
```

#### 4. Resume Interrupted Session
```bash
python cli.py resume SESSION_ID
```

---

## Running Automated Tests

Run the full test suite using `pytest`:
```bash
python -m pytest -v
```

---

## Legal & Ethical Disclaimer

This software is designed exclusively for genuine, authorized document recovery and security testing. You are strictly required to use this software ONLY on files and systems you legally own or have explicit written authorization from the owner to audit.

- **No Illegal Use**: Any unauthorized attempt to breach passwords or access files without consent is illegal and strictly prohibited.
- **Zero Author Liability**: The copyright owner, authors, and contributors assume **no liability** and shall not be held responsible for any misuse, unauthorized access, data loss, or illegal activities conducted with this software.

---

## License

Proprietary License - See [LICENSE](LICENSE) for details. Modification, derivation, and redistribution are strictly prohibited without express written permission.
