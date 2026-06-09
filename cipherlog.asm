; ============================================================
;  PROJECT   : CipherLog - Encrypted Keylogger
;  LANGUAGE  : 32-bit MASM32 Assembly
;  PLATFORM  : Windows 11 native (no DOSBox needed!)
;  AUTHOR    : [Your Name]
;  DATE      : 2026
; ------------------------------------------------------------
;  DESCRIPTION:
;  This program combines two cybersecurity concepts:
;  1. KEYLOGGER  - Captures keyboard input from user
;  2. CAESAR CIPHER - Encrypts captured keys before saving
;
;  FEATURES:
;  1. Capture keystrokes from user
;  2. Encrypt each keystroke using Caesar Cipher (shift key)
;  3. Save encrypted log to file (encrypted_log.txt)
;  4. Decrypt log file back to original keystrokes
;  5. Lockout after 3 wrong master key attempts
;  6. Main menu to choose operation
; ============================================================

.386
.model flat, stdcall
option casemap:none

; ── Windows API includes ────────────────────────────────────
include \masm32\include\windows.inc
include \masm32\include\kernel32.inc
include \masm32\include\user32.inc
include \masm32\include\masm32.inc

includelib \masm32\lib\kernel32.lib
includelib \masm32\lib\user32.lib
includelib \masm32\lib\masm32.lib

; ── Constants ───────────────────────────────────────────────
STD_OUTPUT_HANDLE   equ -11
STD_INPUT_HANDLE    equ -10
GENERIC_WRITE       equ 40000000h
GENERIC_READ        equ 80000000h
OPEN_ALWAYS         equ 4
OPEN_EXISTING       equ 3
CREATE_ALWAYS       equ 2
FILE_ATTRIBUTE_NORMAL equ 80h

.DATA

    ; ── Strings ─────────────────────────────────────────────
    banner      db "============================================", 13, 10
                db "   CIPHERLOG - Encrypted Keylogger         ", 13, 10
                db "   32-bit MASM32 Assembly | Windows 11     ", 13, 10
                db "============================================", 13, 10, 0

    menu        db 13, 10
                db "  [ MAIN MENU ]", 13, 10
                db "  ------------------------------------", 13, 10
                db "  1. Start keylogger (captures + encrypts)", 13, 10
                db "  2. View encrypted log file", 13, 10
                db "  3. Decrypt log file", 13, 10
                db "  4. Clear log file", 13, 10
                db "  5. Exit", 13, 10
                db "  ------------------------------------", 13, 10
                db "  Your choice: ", 0

    msg_key     db 13, 10, "  Enter shift key (1-9): ", 0
    msg_confirm db 13, 10, "  Confirm shift key    : ", 0
    msg_miss    db 13, 10, "  [!] Keys do not match! Try again.", 13, 10, 0
    msg_warn1   db 13, 10, "  [!] Wrong! Attempts left: 2", 13, 10, 0
    msg_warn2   db 13, 10, "  [!] Wrong! Attempts left: 1", 13, 10, 0
    msg_locked  db 13, 10
                db "  ====================================", 13, 10
                db "  ***   SYSTEM LOCKED   ***          ", 13, 10
                db "  Too many wrong master key attempts.", 13, 10
                db "  ====================================", 13, 10, 0

    msg_start   db 13, 10
                db "  [ KEYLOGGER STARTED ]", 13, 10
                db "  Type your message below.", 13, 10
                db "  Press ENTER when done.", 13, 10
                db "  > ", 0

    msg_saved   db 13, 10, "  [OK] Encrypted log saved to: encrypted_log.txt", 13, 10, 0
    msg_cleared db 13, 10, "  [OK] Log file cleared.", 13, 10, 0
    msg_nofile  db 13, 10, "  [!] No log file found.", 13, 10, 0
    msg_dechead db 13, 10, "  [ DECRYPTED LOG ]", 13, 10
                db "  ------------------------------------", 13, 10, 0
    msg_enchead db 13, 10, "  [ ENCRYPTED LOG ]", 13, 10
                db "  ------------------------------------", 13, 10, 0
    msg_end     db 13, 10, "  ------------------------------------", 13, 10, 0
    msg_exit    db 13, 10, "  Goodbye! Stay secure.", 13, 10, 0
    msg_bad     db 13, 10, "  [!] Invalid choice!", 13, 10, 0
    msg_cont    db 13, 10, "  Press ENTER to continue...", 0
    msg_sep     db 13, 10, "  ------------------------------------", 13, 10, 0
    msg_newline db 13, 10, 0

    logfile     db "encrypted_log.txt", 0
    newline     db 13, 10, 0

    ; ── Buffers ─────────────────────────────────────────────
    input_buf   db 256 dup(0)     ; raw input from user
    enc_buf     db 256 dup(0)     ; encrypted output
    dec_buf     db 512 dup(0)     ; decrypted output
    file_buf    db 512 dup(0)     ; file read buffer
    char_buf    db 4 dup(0)       ; single char buffer

    ; ── Variables ───────────────────────────────────────────
    shift_key   dd 0              ; master shift key (numeric)
    key1        dd 0              ; first key entry for confirm
    attempts    dd 3              ; remaining attempts
    locked      dd 0              ; 0=unlocked 1=locked
    hStdOut     dd 0              ; stdout handle
    hStdIn      dd 0              ; stdin handle
    bytes_read  dd 0              ; for ReadFile
    bytes_write dd 0              ; for WriteFile
    choice      db 0              ; menu choice character

.CODE

start:
    ; ── Init handles ────────────────────────────────────────
    invoke GetStdHandle, STD_OUTPUT_HANDLE
    mov    hStdOut, eax
    invoke GetStdHandle, STD_INPUT_HANDLE
    mov    hStdIn, eax

    ; ── Print banner ────────────────────────────────────────
    invoke StdOut, addr banner

MENU_LOOP:
    ; Check lockout
    cmp    locked, 1
    je     SHOW_LOCKED

    invoke StdOut, addr menu
    invoke StdIn,  addr input_buf, 255
    mov    al, [input_buf]
    mov    choice, al

    cmp    choice, '1'
    je     DO_LOG
    cmp    choice, '2'
    je     DO_VIEW
    cmp    choice, '3'
    je     DO_DECRYPT
    cmp    choice, '4'
    je     DO_CLEAR
    cmp    choice, '5'
    je     DO_EXIT

    invoke StdOut, addr msg_bad
    jmp    MENU_LOOP

SHOW_LOCKED:
    invoke StdOut, addr msg_locked
    jmp    DO_EXIT

; ============================================================
; FEATURE 1: KEYLOGGER + ENCRYPT + SAVE
; ============================================================
DO_LOG:
    invoke StdOut, addr msg_sep
    call   GET_KEY
    cmp    eax, 0FFh
    je     MENU_LOOP
    cmp    eax, 0FEh
    je     MENU_LOOP

    ; Get user input (keystrokes)
    invoke StdOut, addr msg_start
    invoke StdIn,  addr input_buf, 255

    ; Encrypt the captured input
    call   ENCRYPT_INPUT

    ; Save encrypted text to file
    invoke CreateFile, addr logfile,
                       GENERIC_WRITE, 0, NULL,
                       OPEN_ALWAYS,
                       FILE_ATTRIBUTE_NORMAL, NULL
    cmp    eax, -1
    je     LOG_DONE

    push   eax                    ; save file handle

    ; Move to end of file to append
    invoke SetFilePointer, eax, 0, NULL, 2

    ; Write encrypted buffer to file
    mov    ecx, eax
    invoke lstrlen, addr enc_buf
    invoke WriteFile, ecx,
                      addr enc_buf, eax,
                      addr bytes_write, NULL

    ; Write newline
    invoke WriteFile, ecx,
                      addr newline, 2,
                      addr bytes_write, NULL

    pop    eax
    invoke CloseHandle, eax

LOG_DONE:
    invoke StdOut, addr msg_saved
    invoke StdOut, addr msg_cont
    invoke StdIn,  addr input_buf, 2
    jmp    MENU_LOOP

; ============================================================
; FEATURE 2: VIEW ENCRYPTED LOG
; ============================================================
DO_VIEW:
    invoke StdOut, addr msg_enchead

    ; Open file for reading
    invoke CreateFile, addr logfile,
                       GENERIC_READ, 0, NULL,
                       OPEN_EXISTING,
                       FILE_ATTRIBUTE_NORMAL, NULL
    cmp    eax, -1
    je     VIEW_NOFILE

    push   eax
    invoke ReadFile, eax, addr file_buf, 511,
                     addr bytes_read, NULL
    pop    eax
    invoke CloseHandle, eax

    ; Null terminate
    mov    ecx, bytes_read
    mov    byte ptr [file_buf + ecx], 0

    invoke StdOut, addr file_buf
    invoke StdOut, addr msg_end
    jmp    VIEW_DONE

VIEW_NOFILE:
    invoke StdOut, addr msg_nofile

VIEW_DONE:
    invoke StdOut, addr msg_cont
    invoke StdIn,  addr input_buf, 2
    jmp    MENU_LOOP

; ============================================================
; FEATURE 3: DECRYPT LOG FILE
; ============================================================
DO_DECRYPT:
    invoke StdOut, addr msg_sep
    call   GET_KEY
    cmp    eax, 0FFh
    je     MENU_LOOP
    cmp    eax, 0FEh
    je     MENU_LOOP

    invoke StdOut, addr msg_dechead

    ; Open file
    invoke CreateFile, addr logfile,
                       GENERIC_READ, 0, NULL,
                       OPEN_EXISTING,
                       FILE_ATTRIBUTE_NORMAL, NULL
    cmp    eax, -1
    je     DEC_NOFILE

    push   eax
    invoke ReadFile, eax, addr file_buf, 511,
                     addr bytes_read, NULL
    pop    eax
    invoke CloseHandle, eax

    mov    ecx, bytes_read
    mov    byte ptr [file_buf + ecx], 0

    ; Decrypt each character
    lea    esi, file_buf
    lea    edi, dec_buf
    mov    ecx, shift_key

DEC_LOOP:
    mov    al, [esi]
    cmp    al, 0
    je     DEC_DONE

    ; Decrypt uppercase
    cmp    al, 'A'
    jb     DEC_CHECK_LO
    cmp    al, 'Z'
    ja     DEC_CHECK_LO
    sub    al, 'A'
    xor    ah, ah
    mov    bl, 26
    add    al, bl
    sub    al, cl
    div    bl
    mov    al, ah
    add    al, 'A'
    jmp    DEC_STORE

DEC_CHECK_LO:
    ; Decrypt lowercase
    cmp    al, 'a'
    jb     DEC_STORE
    cmp    al, 'z'
    ja     DEC_STORE
    sub    al, 'a'
    xor    ah, ah
    mov    bl, 26
    add    al, bl
    sub    al, cl
    div    bl
    mov    al, ah
    add    al, 'a'

DEC_STORE:
    mov    [edi], al
    inc    esi
    inc    edi
    jmp    DEC_LOOP

DEC_DONE:
    mov    byte ptr [edi], 0
    invoke StdOut, addr dec_buf
    invoke StdOut, addr msg_end
    jmp    DEC_VIEW_DONE

DEC_NOFILE:
    invoke StdOut, addr msg_nofile

DEC_VIEW_DONE:
    invoke StdOut, addr msg_cont
    invoke StdIn,  addr input_buf, 2
    jmp    MENU_LOOP

; ============================================================
; FEATURE 4: CLEAR LOG FILE
; ============================================================
DO_CLEAR:
    invoke CreateFile, addr logfile,
                       GENERIC_WRITE, 0, NULL,
                       CREATE_ALWAYS,
                       FILE_ATTRIBUTE_NORMAL, NULL
    cmp    eax, -1
    je     MENU_LOOP
    invoke CloseHandle, eax
    invoke StdOut, addr msg_cleared
    invoke StdOut, addr msg_cont
    invoke StdIn,  addr input_buf, 2
    jmp    MENU_LOOP

; ============================================================
; EXIT
; ============================================================
DO_EXIT:
    invoke StdOut, addr msg_exit
    invoke ExitProcess, 0

; ============================================================
; PROC: ENCRYPT_INPUT
; Encrypts input_buf using Caesar Cipher
; Result stored in enc_buf
; ============================================================
ENCRYPT_INPUT proc
    lea    esi, input_buf
    lea    edi, enc_buf
    mov    ecx, shift_key

ENC_LOOP:
    mov    al, [esi]
    cmp    al, 0Dh           ; carriage return = end
    je     ENC_DONE
    cmp    al, 0Ah           ; line feed = end
    je     ENC_DONE
    cmp    al, 0
    je     ENC_DONE

    ; Encrypt uppercase A-Z
    cmp    al, 'A'
    jb     ENC_LO
    cmp    al, 'Z'
    ja     ENC_LO
    sub    al, 'A'
    xor    ah, ah
    add    al, cl
    mov    bl, 26
    div    bl
    mov    al, ah
    add    al, 'A'
    jmp    ENC_ST

ENC_LO:
    ; Encrypt lowercase a-z
    cmp    al, 'a'
    jb     ENC_ST
    cmp    al, 'z'
    ja     ENC_ST
    sub    al, 'a'
    xor    ah, ah
    add    al, cl
    mov    bl, 26
    div    bl
    mov    al, ah
    add    al, 'a'

ENC_ST:
    mov    [edi], al
    inc    esi
    inc    edi
    jmp    ENC_LOOP

ENC_DONE:
    mov    byte ptr [edi], 0
    ret
ENCRYPT_INPUT endp

; ============================================================
; PROC: GET_KEY
; Gets shift key twice for confirmation + lockout
; Returns EAX = 0 success, FFh locked, FEh fail
; ============================================================
GET_KEY proc
    cmp    locked, 1
    jne    GK_GO
    mov    eax, 0FFh
    ret

GK_GO:
    invoke StdOut, addr msg_key
    invoke StdIn,  addr input_buf, 4
    mov    al, [input_buf]

    cmp    al, '1'
    jb     GK_BAD
    cmp    al, '9'
    ja     GK_BAD

    xor    eax, eax
    mov    al, [input_buf]
    sub    al, '0'
    mov    key1, eax

    invoke StdOut, addr msg_confirm
    invoke StdIn,  addr input_buf, 4
    mov    al, [input_buf]

    cmp    al, '1'
    jb     GK_BAD
    cmp    al, '9'
    ja     GK_BAD

    xor    eax, eax
    mov    al, [input_buf]
    sub    al, '0'

    cmp    eax, key1
    jne    GK_MISS

    mov    shift_key, eax
    mov    eax, 0
    ret

GK_MISS:
    invoke StdOut, addr msg_miss

GK_BAD:
    dec    attempts
    cmp    attempts, 2
    je     GK_W1
    cmp    attempts, 1
    je     GK_W2
    cmp    attempts, 0
    jle    GK_LOCK
    jmp    GK_FAIL

GK_W1:
    invoke StdOut, addr msg_warn1
    jmp    GK_FAIL

GK_W2:
    invoke StdOut, addr msg_warn2
    jmp    GK_FAIL

GK_LOCK:
    mov    locked, 1
    invoke StdOut, addr msg_locked
    mov    eax, 0FFh
    ret

GK_FAIL:
    mov    eax, 0FEh
    ret
GET_KEY endp

end start
