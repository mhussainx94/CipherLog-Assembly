# 🔐 CipherLog — Caesar Cipher Encrypted Keylogger

![Assembly](https://img.shields.io/badge/Assembly-MASM32-blue)
![Python](https://img.shields.io/badge/Python-3.x-green)
![Platform](https://img.shields.io/badge/Platform-Windows%2011-lightgrey)
![License](https://img.shields.io/badge/License-Educational-orange)

> A 32-bit MASM32 Assembly project that combines a **Keylogger** and **Caesar Cipher Encryption** — demonstrating core Assembly language concepts including register operations, memory management, subroutines, loops, conditional jumps, and Windows API calls.

---

## 📌 Table of Contents

- [Project Overview](#project-overview)
- [Project Purpose](#project-purpose)
- [Features](#features)
- [Project Structure](#project-structure)
- [Assembly Concepts Used](#assembly-concepts-used)
- [How It Works](#how-it-works)
- [Requirements](#requirements)
- [How to Run](#how-to-run)
- [How to Compile](#how-to-compile)
- [Screenshots](#screenshots)
- [Team](#team)

---

## 📖 Project Overview

**CipherLog** is a 32-bit Assembly language project built using **MASM32** that runs natively on **Windows 11** — no emulator or virtual machine required.

The project has two layers:

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Core Logic | 32-bit MASM32 Assembly | Encryption, decryption, file I/O |
| Presentation | Python tkinter GUI | Visual interface for demonstration |

The Python GUI connects to the compiled Assembly executable using Python's `subprocess` module — so all encryption and decryption logic comes from Assembly.

---

## 🎯 Project Purpose

This project was built to demonstrate the following Assembly language concepts in a practical real-world application:

1. **Register operations** — using EAX, EBX, ECX, EDX, ESI, EDI
2. **Arithmetic instructions** — ADD, SUB, DIV for Caesar Cipher math
3. **Conditional jumps** — JE, JNE, JB, JA, JLE for decision making
4. **Loop structures** — JMP based loops for processing each character
5. **Subroutines** — PROC, CALL, RET for modular code
6. **Memory buffers** — .DATA section variables and buffers
7. **Stack operations** — PUSH, POP for saving register state
8. **Windows API calls** — StdIn, StdOut, CreateFile, WriteFile, ReadFile

---

## ✨ Features

### Assembly (.exe) Features
| Feature | Description |
|---------|-------------|
| 🔑 Main Menu | Choose operation using keyboard input |
| ⬆ Encrypt | Capture keystrokes and encrypt with Caesar Cipher |
| ⬇ Decrypt | Decrypt log file back to original text |
| 📄 View Log | View encrypted log file contents |
| 🗑 Clear Log | Clear the encrypted log file |
| 🔒 Lockout | System locks after 3 wrong key attempts |

### Python GUI Features
| Feature | Description |
|---------|-------------|
| 🎨 Dark theme | Cybersecurity themed dark GUI |
| ⬆ Capture + Encrypt | Sends input to Assembly, shows result |
| 📄 View Encrypted Log | Reads and displays encrypted_log.txt |
| ⬇ Decrypt Log | Decrypts using Assembly logic |
| 🗑 Clear Log | Empties the log file |
| ▶ Run ASM in GUI | Launches Assembly and shows output in GUI |
| 🔄 Reset | Clears lockout and resets everything |

---

## 📁 Project Structure

```
CipherLog-Assembly/
│
├── cipherlog.asm           ← Main 32-bit MASM32 Assembly source code
├── cipherlog.exe           ← Compiled Assembly executable (Windows 11)
├── cipherlog.obj           ← Object file (generated during compile)
├── cipherlog_gui.py        ← Python tkinter GUI
├── compile.bat             ← One-click compile script
├── encrypted_log.txt       ← Auto-created when program runs
└── README.md               ← This file
```

---

## 🔧 Assembly Concepts Used

### 1. Registers
```asm
MOV  AL, [SI]       ; load character from memory into AL
MOV  CL, shift_key  ; shift key stored in CL register
MOV  ESI, input_buf ; ESI points to input buffer
MOV  EDI, enc_buf   ; EDI points to encrypted buffer
```

### 2. Caesar Cipher — Encryption Logic
```asm
; Encrypt uppercase letter A-Z
SUB  AL, 'A'        ; convert to 0-25
ADD  AL, CL         ; apply shift key from CL register
MOV  AH, 0
MOV  BL, 26
DIV  BL             ; divide by 26 — AH = remainder (mod 26)
MOV  AL, AH         ; AL = encrypted position (0-25)
ADD  AL, 'A'        ; convert back to ASCII letter
```

### 3. Caesar Cipher — Decryption Logic
```asm
; Decrypt uppercase letter A-Z
SUB  AL, 'A'        ; convert to 0-25
MOV  BL, 26
ADD  AL, BL         ; add 26 to prevent negative result
SUB  AL, CL         ; subtract shift key
DIV  BL             ; mod 26 wrap around
MOV  AL, AH
ADD  AL, 'A'        ; convert back to ASCII
```

### 4. Subroutines (PROC)
```asm
ENCRYPT_INPUT proc  ; encrypts input_buf → enc_buf
    ...
ENCRYPT_INPUT endp

GET_KEY proc        ; gets shift key with confirmation + lockout
    ...
GET_KEY endp
```

### 5. Windows API Calls
```asm
invoke StdIn,  addr input_buf, 255     ; capture keyboard input
invoke StdOut, addr enc_buf            ; print to screen
invoke CreateFile, addr logfile, ...   ; create/open file
invoke WriteFile, handle, addr data,.. ; write to file
invoke ReadFile,  handle, addr buf,..  ; read from file
```

### 6. Lockout Protection Logic
```asm
DEC  attempts          ; decrement attempt counter
CMP  attempts, 0       ; check if zero
JLE  GK_LOCK           ; jump to lock if zero or below
MOV  locked, 1         ; set locked flag
```

---

## ⚙️ How It Works

### Step 1 — User types a message
The Assembly program captures keyboard input using `StdIn` Windows API into `input_buf` memory buffer.

### Step 2 — Caesar Cipher encrypts
Each letter is processed character by character:
```
Plain text  : H  e  l  l  o
Shift key   : 3  3  3  3  3
Encrypted   : K  h  o  o  r
```
Formula: `encrypted = (character - 'A' + shift) mod 26 + 'A'`

### Step 3 — Save to file
Encrypted text is saved to `encrypted_log.txt` using `CreateFile` and `WriteFile` Assembly API calls.

### Step 4 — Decrypt
Enter the same shift key — Assembly reverses the operation:
```
Cipher text : K  h  o  o  r
Shift key   : 3  3  3  3  3
Decrypted   : H  e  l  l  o
```
Formula: `decrypted = (character - 'A' - shift + 26) mod 26 + 'A'`

### Step 5 — Lockout Protection
If user enters wrong shift key 3 times:
```
Attempt 1 wrong → Warning: 2 attempts left
Attempt 2 wrong → Warning: 1 attempt left
Attempt 3 wrong → SYSTEM LOCKED
```

---

## 💻 Requirements

### For Assembly (.exe)
| Requirement | Details |
|-------------|---------|
| OS | Windows 10 / Windows 11 (64-bit) |
| MASM32 | Install from http://www.masm32.com |
| Architecture | 32-bit (runs on 64-bit Windows) |

### For Python GUI
| Requirement | Details |
|-------------|---------|
| Python | Version 3.x |
| tkinter | Built into Python (no install needed) |
| subprocess | Built into Python (no install needed) |

---

## ▶️ How to Run

### Option 1 — Run Assembly directly
Open PowerShell in project folder:
```bash
.\cipherlog.exe
```
Follow the on-screen menu.

### Option 2 — Run Python GUI (recommended for presentation)
```bash
python cipherlog_gui.py
```
Or simply **double click** `cipherlog_gui.py`

### Option 3 — Run GUI and connect to Assembly
1. Run `python cipherlog_gui.py`
2. Type your message in the input box
3. Set shift key using the slider
4. Click **CAPTURE + ENCRYPT** — Assembly encrypts and saves
5. Click **VIEW ENCRYPTED LOG** — see encrypted file
6. Click **DECRYPT LOG** — recover original message

---

## 🔨 How to Compile

### Step 1 — Install MASM32
Download from: **http://www.masm32.com/download.htm**
Install to: `C:\masm32`

### Step 2 — Compile using batch file
Double click `compile.bat` — it runs automatically!

### Step 3 — Or compile manually
Open Command Prompt in project folder:
```bash
C:\masm32\bin\ml.exe /c /coff cipherlog.asm
C:\masm32\bin\link.exe /subsystem:console /out:cipherlog.exe cipherlog.obj
```

### Step 4 — Verify
```
✅ cipherlog.exe created successfully
✅ File size should be 10-50 KB
```

---

## 🖥️ How Python Connects to Assembly

```
Python GUI
    │
    │  subprocess.run([cipherlog.exe], input=asm_input)
    ↓
cipherlog.exe (32-bit Assembly)
    │
    │  Encrypts using Caesar Cipher
    │  Saves to encrypted_log.txt
    ↓
Python reads encrypted_log.txt
    │
    │  Displays result in GUI output box
    ↓
User sees Assembly output in Python GUI
```

Python sends input to Assembly using:
```python
result = subprocess.run(
    ["cipherlog.exe"],
    input=asm_input,
    capture_output=True,
    text=True
)
```

---


---

## 📚 Key Assembly Instructions Reference

| Instruction | Purpose in Project |
|-------------|-------------------|
| `MOV` | Move data between registers and memory |
| `ADD` | Add shift key to character for encryption |
| `SUB` | Subtract for decryption and ASCII conversion |
| `DIV` | Divide by 26 for mod wrap-around |
| `CMP` | Compare values for decision making |
| `JE` | Jump if Equal — exact match check |
| `JB` | Jump if Below — range check |
| `JA` | Jump if Above — range check |
| `JLE` | Jump if Less or Equal — lockout check |
| `JMP` | Unconditional jump — loop back |
| `CALL` | Call subroutine |
| `RET` | Return from subroutine |
| `PUSH/POP` | Save and restore register values |
| `INC/DEC` | Increment/decrement counters |
| `invoke` | Call Windows API functions |

---

## ⚠️ Disclaimer

> This project is built for **educational purposes only** as part of an Assembly Language course. The keylogger component demonstrates how keyboard input is captured at the Assembly level — it is not designed for malicious use.

---

*Built with ❤️ using 32-bit MASM32 Assembly Language*
