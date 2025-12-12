@echo off
echo ========================================
echo Silent Organizer - Dependency Installer
echo ========================================
echo.
echo Checking Python installation...
python --version
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH!
    echo Download Python from: https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)
echo.
echo Installing required Python packages...
echo.

pip install -r requirements.txt

echo.
echo ========================================
if %errorlevel% equ 0 (
    echo Installation completed successfully!
    echo.
    echo Testing tkinter (GUI library)...
    python -c "import tkinter; print('tkinter OK')" 2>nul
    if %errorlevel% neq 0 (
        echo.
        echo WARNING: tkinter is not available!
        echo.
        echo SOLUTION:
        echo 1. Reinstall Python from https://www.python.org/downloads/
        echo 2. During installation, make sure to check:
        echo    - "tcl/tk and IDLE"
        echo    - "Add Python to PATH"
        echo.
    ) else (
        echo tkinter is working correctly!
        echo.
        echo You can now run launch_control_panel.bat
    )
) else (
    echo Installation failed!
    echo.
    echo Please make sure Python is installed and added to PATH.
    echo Download Python from: https://www.python.org/downloads/
)
echo ========================================
echo.
pause
