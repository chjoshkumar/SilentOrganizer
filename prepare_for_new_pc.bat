@echo off
echo ========================================
echo Preparing Silent Organizer for New PC
echo ========================================
echo.
echo This will clean up PC-specific files to prepare
echo for copying to a new computer.
echo.
echo The following files will be DELETED:
echo   - config.json (folder paths from this PC)
echo   - organizer_state.json (running status)
echo   - history.json (file movement history)
echo.
set /p confirm="Are you sure you want to continue? (Y/N): "

if /i "%confirm%" neq "Y" (
    echo.
    echo Operation cancelled.
    pause
    exit /b
)

echo.
echo Cleaning up PC-specific files...

if exist "config.json" (
    del "config.json"
    echo   ✓ Deleted config.json
)

if exist "organizer_state.json" (
    del "organizer_state.json"
    echo   ✓ Deleted organizer_state.json
)

if exist "history.json" (
    del "history.json"
    echo   ✓ Deleted history.json
)

echo.
echo ========================================
echo Preparation complete!
echo.
echo You can now copy this folder to the new PC.
echo.
echo On the new PC:
echo   1. Run install_dependencies.bat
echo   2. Run launch_control_panel.bat
echo   3. Add your folders and start organizing
echo ========================================
echo.
pause
