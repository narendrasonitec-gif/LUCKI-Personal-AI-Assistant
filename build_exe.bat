@echo off
setlocal
cd /d "%~dp0"

echo =========================================
echo       LUCKI AI - WINDOWS EXE BUILDER
echo =========================================
echo.
echo This builds the app on this Windows PC.
echo Python is required only on the build PC.
echo.

where python >nul 2>nul
if errorlevel 1 (
  echo Python was not found. Install Python 3.11 or 3.12 and try again.
  pause
  exit /b 1
)

python -m pip install --upgrade pip
if errorlevel 1 goto :failed

python -m pip install -r requirements.txt
if errorlevel 1 goto :failed

python -m pip install pyinstaller
if errorlevel 1 goto :failed

if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

python -m PyInstaller --noconfirm --clean lucki.spec
if errorlevel 1 goto :failed

echo.
echo BUILD COMPLETE!
echo EXE: dist\Lucki\Lucki.exe
echo Copy the whole dist\Lucki folder to another PC, not only the EXE.
echo Keep your private .env file beside Lucki.exe for cloud AI.
pause
exit /b 0

:failed
echo.
echo BUILD FAILED. Read the error above and check BUILD_AND_INSTALL.md.
pause
exit /b 1
