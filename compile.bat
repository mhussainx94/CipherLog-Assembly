@echo off
echo ============================================
echo   CipherLog - Compile Script
echo   32-bit MASM32 Assembly
echo ============================================
echo.

echo Step 1: Assembling cipherlog.asm...
C:\masm32\bin\ml.exe /c /coff cipherlog.asm
if errorlevel 1 goto ERROR

echo Step 2: Linking cipherlog.obj...
C:\masm32\bin\link.exe /subsystem:console /out:cipherlog.exe cipherlog.obj
if errorlevel 1 goto ERROR

echo.
echo [OK] Compiled successfully!
echo [OK] cipherlog.exe is ready!
echo.
pause
goto END

:ERROR
echo.
echo [!] Compilation failed!
echo [!] Make sure MASM32 is installed at C:\masm32
echo.
pause

:END