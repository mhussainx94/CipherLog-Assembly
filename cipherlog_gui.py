"""
CipherLog GUI — Python + 32-bit MASM32 Assembly
=================================================
Connects to cipherlog.exe compiled from cipherlog.asm
Run: python cipherlog_gui.py
"""

import tkinter as tk
from tkinter import messagebox
import subprocess
import os
import sys

# ============================================================
# CIPHER LOGIC (mirrors MASM32 Assembly exactly)
# ============================================================

def encrypt(text, shift):
    result = ""
    for ch in text:
        if 'A' <= ch <= 'Z':
            result += chr((ord(ch) - ord('A') + shift) % 26 + ord('A'))
        elif 'a' <= ch <= 'z':
            result += chr((ord(ch) - ord('a') + shift) % 26 + ord('a'))
        else:
            result += ch
    return result

def decrypt(text, shift):
    result = ""
    for ch in text:
        if 'A' <= ch <= 'Z':
            result += chr((ord(ch) - ord('A') - shift + 26) % 26 + ord('A'))
        elif 'a' <= ch <= 'z':
            result += chr((ord(ch) - ord('a') - shift + 26) % 26 + ord('a'))
        else:
            result += ch
    return result

# ============================================================
# COLORS
# ============================================================
BG     = "#0D1117"
PANEL  = "#161B22"
CARD   = "#1C2128"
GREEN  = "#00FF9C"
RED    = "#FF6B6B"
YELLOW = "#FFD93D"
ORANGE = "#FF9500"
BLUE   = "#38BDF8"
TEXT   = "#E6EDF3"
MUTED  = "#7D8590"
BORDER = "#30363D"

class CipherLogApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CipherLog — Encrypted Keylogger | MASM32 Assembly")
        self.root.geometry("950x720")
        self.root.configure(bg=BG)
        self.root.resizable(True, True)

        self.shift_var = tk.IntVar(value=3)
        self.attempts  = 0
        self.MAX_ATT   = 3
        self.locked    = False
        self.log_file  = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                       "encrypted_log.txt")
        self._build()

    def _build(self):
        # ── HEADER ──────────────────────────────────────────
        hdr = tk.Frame(self.root, bg=BG)
        hdr.pack(fill="x", padx=20, pady=(16, 0))

        tk.Label(hdr, text="CIPHERLOG",
                 bg=BG, fg=GREEN,
                 font=("Courier New", 20, "bold")).pack(side="left")
        tk.Label(hdr, text="  Encrypted Keylogger | 32-bit MASM32 Assembly",
                 bg=BG, fg=MUTED,
                 font=("Courier New", 10)).pack(side="left", pady=(6, 0))

        self.status = tk.Label(hdr, text="● READY",
                               bg=BG, fg=GREEN,
                               font=("Courier New", 10, "bold"))
        self.status.pack(side="right")

        tk.Frame(self.root, bg=BORDER, height=1).pack(fill="x", padx=20, pady=10)

        # ── SHIFT KEY ────────────────────────────────────────
        kf = tk.Frame(self.root, bg=CARD,
                      highlightthickness=1,
                      highlightbackground=BORDER)
        kf.pack(fill="x", padx=20, pady=(0, 8))

        tk.Label(kf, text="MASTER SHIFT KEY  (Caesar Cipher encryption key)",
                 bg=CARD, fg=MUTED,
                 font=("Courier New", 9, "bold")).pack(anchor="w", padx=12, pady=(8, 2))
        tk.Frame(kf, bg=BORDER, height=1).pack(fill="x", padx=12)

        kr = tk.Frame(kf, bg=CARD)
        kr.pack(fill="x", padx=12, pady=8)

        self.key_lbl = tk.Label(kr, text="3",
                                bg=CARD, fg=GREEN,
                                font=("Courier New", 28, "bold"), width=3)
        self.key_lbl.pack(side="left")

        tk.Scale(kr, from_=1, to=25,
                 orient="horizontal",
                 variable=self.shift_var,
                 bg=CARD, fg=TEXT,
                 highlightthickness=0,
                 troughcolor=BORDER,
                 activebackground=GREEN,
                 sliderrelief="flat",
                 showvalue=False,
                 length=580,
                 command=lambda v: self.key_lbl.config(text=str(v))
                 ).pack(side="left", padx=10, fill="x", expand=True)

        # ── MESSAGE INPUT ─────────────────────────────────────
        mf = tk.Frame(self.root, bg=CARD,
                      highlightthickness=1,
                      highlightbackground=BORDER)
        mf.pack(fill="x", padx=20, pady=(0, 8))

        tk.Label(mf, text="KEYSTROKE INPUT  (simulates keylogger capture)",
                 bg=CARD, fg=MUTED,
                 font=("Courier New", 9, "bold")).pack(anchor="w", padx=12, pady=(8, 2))
        tk.Frame(mf, bg=BORDER, height=1).pack(fill="x", padx=12)

        self.msg_input = tk.Text(mf, height=3,
                                 bg="#0D1117", fg=TEXT,
                                 insertbackground=GREEN,
                                 font=("Courier New", 13),
                                 bd=0, relief="flat", wrap="word",
                                 highlightthickness=1,
                                 highlightbackground=BORDER,
                                 highlightcolor=GREEN)
        self.msg_input.pack(fill="x", padx=12, pady=8)
        self.msg_input.insert("1.0", "Type your secret message here...")
        self.msg_input.bind("<FocusIn>", self._clear_placeholder)
        self.msg_input.bind("<FocusOut>", self._add_placeholder)
        self.placeholder_active = True

        # ── BUTTONS ───────────────────────────────────────────
        bf = tk.Frame(self.root, bg=BG)
        bf.pack(fill="x", padx=20, pady=(0, 8))

        buttons = [
            ("CAPTURE + ENCRYPT",  GREEN,  self._capture),
            ("VIEW ENCRYPTED LOG", YELLOW, self._view_enc),
            ("DECRYPT LOG",        BLUE,   self._view_dec),
            ("CLEAR LOG",          RED,    self._clear_log),
            ("RUN ASM IN GUI",     ORANGE, self._launch),
            ("RESET",              MUTED,  self._reset),
        ]

        for label, color, cmd in buttons:
            tk.Button(bf, text=label, command=cmd,
                      bg=CARD, fg=color,
                      font=("Courier New", 9, "bold"),
                      bd=0, relief="flat",
                      padx=10, pady=8,
                      cursor="hand2",
                      activebackground=BORDER,
                      activeforeground=color,
                      highlightthickness=1,
                      highlightbackground=color
                      ).pack(side="left", padx=(0, 6))

        self.att_lbl = tk.Label(bf,
                                text=f"Lockout: 0/{self.MAX_ATT}",
                                bg=BG, fg=MUTED,
                                font=("Courier New", 9))
        self.att_lbl.pack(side="right")

        # ── OUTPUT ────────────────────────────────────────────
        tk.Frame(self.root, bg=BORDER, height=1).pack(fill="x", padx=20, pady=(4, 0))

        of = tk.Frame(self.root, bg=BG)
        of.pack(fill="both", expand=True, padx=20, pady=(8, 16))

        tk.Label(of, text="OUTPUT  —  Assembly simulation result",
                 bg=BG, fg=MUTED,
                 font=("Courier New", 9, "bold")).pack(anchor="w")

        self.out = tk.Text(of, bg=PANEL, fg=GREEN,
                           font=("Courier New", 12),
                           bd=0, relief="flat",
                           wrap="word", state="disabled",
                           highlightthickness=1,
                           highlightbackground=BORDER)
        self.out.pack(fill="both", expand=True, pady=(4, 0))

        self._print("CipherLog — Encrypted Keylogger\n")
        self._print("32-bit MASM32 Assembly + Python GUI\n")
        self._print("=====================================\n")
        self._print("Ready. Type a message and click CAPTURE + ENCRYPT.\n", MUTED)

    # ── PLACEHOLDER HANDLERS ─────────────────────────────────
    def _clear_placeholder(self, event):
        if self.placeholder_active:
            self.msg_input.delete("1.0", "end")
            self.msg_input.config(fg=TEXT)
            self.placeholder_active = False

    def _add_placeholder(self, event):
        if not self.msg_input.get("1.0", "end").strip():
            self.msg_input.insert("1.0", "Type your secret message here...")
            self.msg_input.config(fg=MUTED)
            self.placeholder_active = True

    # ── HELPERS ──────────────────────────────────────────────
    def _print(self, text, color=GREEN):
        self.out.config(state="normal")
        tag = "c" + color.replace("#", "")
        self.out.tag_config(tag, foreground=color)
        self.out.insert("end", text, tag)
        self.out.see("end")
        self.out.config(state="disabled")

    def _clear_out(self):
        self.out.config(state="normal")
        self.out.delete("1.0", "end")
        self.out.config(state="disabled")

    def _get_msg(self):
        msg = self.msg_input.get("1.0", "end").strip()
        # ignore placeholder text
        if msg == "Type your secret message here...":
            return ""
        return msg

    def _set_status(self, text, color):
        self.status.config(text=text, fg=color)

    def _check_lock(self):
        if self.locked:
            self._clear_out()
            self._print("SYSTEM LOCKED\n", RED)
            self._print("Too many wrong attempts. Click RESET.\n", MUTED)
            return True
        return False

    # ── FEATURES ─────────────────────────────────────────────
    def _capture(self):
        if self._check_lock(): return
        msg   = self._get_msg()
        shift = self.shift_var.get()
        if not msg:
            messagebox.showwarning("Empty", "Type a message first!"); return

        folder   = os.path.dirname(os.path.abspath(__file__))
        exe_path = os.path.join(folder, "cipherlog.exe")

        self._clear_out()
        self._print("[ KEYLOGGER CAPTURED + ENCRYPTED ]\n\n", MUTED)
        self._print(f"Shift Key        : {shift}\n", YELLOW)
        self._print(f"Characters logged: {len(msg)}\n\n", YELLOW)
        self._print("Keystrokes  →  ", MUTED)
        self._print(f"{msg}\n", TEXT)

        if os.path.exists(exe_path):
            try:
                # ── Write input file for Assembly to read ──
                input_file  = os.path.join(folder, "asm_input.txt")
                output_file = os.path.join(folder, "asm_output.txt")

                # Save message + shift to input file
                with open(input_file, "w") as f:
                    f.write(f"{shift}\n{msg}\n")

                # ── Run Assembly with input/output redirected ──
                with open(input_file, "r") as fin,                      open(output_file, "w") as fout:
                    result = subprocess.run(
                        [exe_path],
                        stdin=fin,
                        stdout=fout,
                        stderr=fout,
                        timeout=10
                    )

                # ── Read Assembly output file ──
                if os.path.exists(output_file):
                    with open(output_file, "r", encoding="utf-8", errors="ignore") as f:
                        asm_out = f.read()
                    if asm_out.strip():
                        self._print("\n[ ASSEMBLY OUTPUT ]\n", ORANGE)
                        for line in asm_out.splitlines():
                            if line.strip():
                                self._print(f"  {line}\n", TEXT)

                # ── Read encrypted log saved by Assembly ──
                if os.path.exists(self.log_file):
                    with open(self.log_file, "r", encoding="utf-8", errors="ignore") as f:
                        lines = f.readlines()
                    if lines:
                        last_line = lines[-1].strip()
                        if last_line:
                            self._print("\nEncrypted   →  ", MUTED)
                            self._print(f"{last_line}\n", GREEN)
                            self._print("[OK] File saved by Assembly .exe\n", GREEN)
                            self._print("[Assembly logic — NOT Python]\n", ORANGE)
                            self._set_status("● CAPTURED BY ASM", GREEN)
                            self.attempts += 1
                            self.att_lbl.config(text=f"Lockout: {self.attempts}/{self.MAX_ATT}")
                            if self.attempts >= self.MAX_ATT:
                                self.locked = True
                                self._set_status("● LOCKED", RED)
                            return

                # If assembly did not save — fall through to Python
                raise Exception("Assembly did not save to log file")

            except Exception as e:
                self._print(f"\n[!] Assembly issue: {str(e)}\n", YELLOW)
                self._print("[Switching to Python fallback]\n", YELLOW)

        # ── Python fallback logic ──
        cipher = encrypt(msg, shift)
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(cipher + "\n")
                f.flush()
        except Exception as e:
            self._print(f"File write error: {str(e)}\n", RED)
            return

        self._print("Encrypted   →  ", MUTED)
        self._print(f"{cipher}\n", GREEN)
        self._print(f"\n[OK] Saved by Python logic\n", MUTED)

        self.attempts += 1
        self.att_lbl.config(text=f"Lockout: {self.attempts}/{self.MAX_ATT}")
        if self.attempts >= self.MAX_ATT:
            self.locked = True
            self._set_status("● LOCKED", RED)
            self._print("\n⚠ MAX ATTEMPTS — System locked!\n", RED)
            return
        self._set_status("● CAPTURED", GREEN)

    def _view_enc(self):
        self._clear_out()
        self._print("[ ENCRYPTED LOG FILE ]\n\n", MUTED)
        if not os.path.exists(self.log_file):
            self._print("No log file found. Capture something first!\n", RED)
            return
        with open(self.log_file, "r") as f:
            content = f.read()
        if not content.strip():
            self._print("Log file is empty.\n", MUTED)
            return
        self._print(content, YELLOW)
        self._print("\n[OK] This is the encrypted log.\n", MUTED)
        self._set_status("● LOG VIEWED", YELLOW)

    def _view_dec(self):
        if self._check_lock(): return
        shift    = self.shift_var.get()
        folder   = os.path.dirname(os.path.abspath(__file__))
        exe_path = os.path.join(folder, "cipherlog.exe")

        self._clear_out()
        self._print("[ DECRYPTED LOG FILE ]\n\n", MUTED)

        if not os.path.exists(self.log_file):
            self._print("No log file found. Capture something first!\n", RED)
            return

        if os.path.exists(exe_path):
            try:
                # Send input to Assembly: choice=3 (decrypt), key, confirm, exit
                asm_input = f"3\r\n{shift}\r\n{shift}\r\n\r\n5\r\n"
                result = subprocess.run(
                    [exe_path],
                    input=asm_input,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                # Parse Assembly output — find decrypted section
                output = result.stdout
                if "DECRYPTED LOG" in output:
                    lines = output.split("\n")
                    capture = False
                    for line in lines:
                        if "DECRYPTED LOG" in line:
                            capture = True
                            continue
                        if capture and "----" in line:
                            break
                        if capture and line.strip():
                            self._print(f"{line.strip()}\n", BLUE)
                    self._print("\n[OK] Decrypted by Assembly .exe\n", GREEN)
                    self._print("[Assembly logic used — NOT Python]\n", ORANGE)
                else:
                    raise Exception("No decrypted output from Assembly")

            except Exception as e:
                # Fallback to Python
                self._print(f"Assembly fallback: {str(e)}\n", YELLOW)
                with open(self.log_file, "r") as f:
                    lines = f.readlines()
                for i, line in enumerate(lines):
                    decrypted = decrypt(line.strip(), shift)
                    self._print(f"Entry {i+1}: ", MUTED)
                    self._print(f"{decrypted}\n", BLUE)
                self._print("\n[OK] Decrypted by Python fallback\n", MUTED)
        else:
            # Python fallback
            self._print("[!] cipherlog.exe not found — using Python logic\n", YELLOW)
            with open(self.log_file, "r") as f:
                lines = f.readlines()
            if not lines:
                self._print("Log file is empty.\n", MUTED)
                return
            for i, line in enumerate(lines):
                decrypted = decrypt(line.strip(), shift)
                self._print(f"Entry {i+1}: ", MUTED)
                self._print(f"{decrypted}\n", BLUE)
            self._print("\n[OK] Decryption complete.\n", GREEN)

        self._set_status("● DECRYPTED", BLUE)

    def _clear_log(self):
        if os.path.exists(self.log_file):
            open(self.log_file, "w").close()
        self._clear_out()
        self._print("Log file cleared.\n", MUTED)
        self._set_status("● CLEARED", RED)

    def _launch(self):
        """
        Runs the Assembly .exe, captures ALL output,
        and displays it live inside the Python GUI output box.
        """
        folder   = os.path.dirname(os.path.abspath(__file__))
        exe_path = os.path.join(folder, "cipherlog.exe")

        self._clear_out()
        self._print("[ ASSEMBLY .EXE OUTPUT — displayed in GUI ]\n\n", ORANGE)

        if not os.path.exists(exe_path):
            self._print("cipherlog.exe not found!\n\n", RED)
            self._print("Compile steps:\n", TEXT)
            self._print("  1. Install MASM32: http://www.masm32.com\n", MUTED)
            self._print("  2. Run compile.bat in project folder\n", MUTED)
            self._print("  3. cipherlog.exe will appear\n", MUTED)
            self._set_status("● EXE NOT FOUND", RED)
            return

        # Build interactive input for Assembly menu
        shift = self.shift_var.get()
        msg   = self._get_msg()

        if not msg:
            messagebox.showwarning("Empty", "Type a message first!")
            return

        # Input sequence for Assembly menu:
        # choice=1, shift key, confirm key, message, any key to continue, choice=5 to exit
        asm_input = f"1\r\n{shift}\r\n{shift}\r\n{msg}\r\n\r\n5\r\n"

        try:
            self._print(f"Sending to Assembly .exe:\n", MUTED)
            self._print(f"  Message  : {msg}\n", TEXT)
            self._print(f"  Shift Key: {shift}\n\n", YELLOW)
            self._print("=" * 44 + "\n", MUTED)
            self._print("  ASSEMBLY .EXE RAW OUTPUT:\n", ORANGE)
            self._print("=" * 44 + "\n\n", MUTED)

            # Run Assembly .exe and capture ALL output
            result = subprocess.run(
                [exe_path],
                input=asm_input,
                capture_output=True,
                text=True,
                timeout=30
            )

            # Display ALL Assembly output line by line in GUI
            output_lines = result.stdout.splitlines()
            for line in output_lines:
                stripped = line.strip()
                if not stripped:
                    self._print("\n", TEXT)
                    continue
                # Color code different parts of Assembly output
                if "CIPHERSHIELD" in stripped or "======" in stripped:
                    self._print(f"{line}\n", GREEN)
                elif "ENCRYPT" in stripped or "OK" in stripped:
                    self._print(f"{line}\n", GREEN)
                elif "Encrypted" in stripped:
                    self._print(f"{line}\n", YELLOW)
                elif "LOCKED" in stripped or "!" in stripped:
                    self._print(f"{line}\n", RED)
                elif "----" in stripped or "MENU" in stripped:
                    self._print(f"{line}\n", MUTED)
                else:
                    self._print(f"{line}\n", TEXT)

            # Also show stderr if any
            if result.stderr:
                self._print("\n[Assembly stderr]:\n", RED)
                self._print(result.stderr, RED)

            self._print("\n" + "=" * 44 + "\n", MUTED)
            self._print("  Assembly .exe finished.\n", ORANGE)

            # Read and show what was saved to log file
            if os.path.exists(self.log_file):
                with open(self.log_file, "r", encoding="utf-8", errors="ignore") as f:
                    lines = f.readlines()
                if lines:
                    self._print(f"\n[OK] encrypted_log.txt last entry:\n", GREEN)
                    self._print(f"  {lines[-1].strip()}\n", YELLOW)

            self._set_status("● ASM OUTPUT SHOWN", ORANGE)

        except subprocess.TimeoutExpired:
            self._print("\n[!] Assembly .exe timed out (15s)\n", RED)
            self._set_status("● TIMEOUT", RED)
        except Exception as e:
            self._print(f"\n[!] Error: {str(e)}\n", RED)
            self._set_status("● ERROR", RED)

    def _reset(self):
        self.locked   = False
        self.attempts = 0
        self.att_lbl.config(text=f"Lockout: 0/{self.MAX_ATT}")
        self.msg_input.delete("1.0", "end")
        self._clear_out()
        self._print("Reset complete. Ready!\n", MUTED)
        self._set_status("● READY", GREEN)

# ============================================================
if __name__ == "__main__":
    root = tk.Tk()
    CipherLogApp(root)
    root.mainloop()