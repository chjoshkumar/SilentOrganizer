# Troubleshooting Guide

## Common Issues and Solutions

### ❌ Error: "Can't invoke 'wm' command" or tkinter errors

**Problem:** The GUI library (tkinter) is not installed or not working.

**Solution:**
1. **Reinstall Python** from https://www.python.org/downloads/
2. During installation, make sure to check these options:
   - ✅ **"tcl/tk and IDLE"** (this installs tkinter)
   - ✅ **"Add Python to PATH"**
3. After reinstalling, run `install_dependencies.bat` again

**Quick Test:**
Open Command Prompt and type:
```
python -c "import tkinter; print('tkinter OK')"
```
If you see "tkinter OK", it's working. If you see an error, reinstall Python.

---

### ❌ Error: "Module not found: watchdog" or "Module not found: psutil"

**Problem:** Required packages are not installed.

**Solution:**
1. Run `install_dependencies.bat`
2. Or manually: `pip install -r requirements.txt`

---

### ❌ Error: "Python is not recognized"

**Problem:** Python is not installed or not in PATH.

**Solution:**
1. Install Python from https://www.python.org/downloads/
2. During installation, check **"Add Python to PATH"**
3. Restart your computer
4. Run `install_dependencies.bat`

---

### ❌ Organizer stops immediately after starting

**Problem:** The main.py script is crashing.

**Solution:**
1. Check the log file: `C:\Users\YourName\FileOrganizer.log`
2. Common causes:
   - Missing dependencies → Run `install_dependencies.bat`
   - Folder paths don't exist → Remove old folders from config.json
   - Permission issues → Run as Administrator

---

### ❌ Old PC folders showing up

**Problem:** config.json has folder paths from the old PC.

**Solution:**
1. Open `config.json`
2. Delete the old folder entries
3. Or delete `config.json` entirely (it will be recreated)
4. Open control panel and add new folders

---

### ❌ Files not being organized

**Problem:** Organizer is running but files aren't moving.

**Solution:**
1. Check if folders are enabled (☑️) in the control panel
2. Check the log file for errors: `C:\Users\YourName\FileOrganizer.log`
3. Make sure you have write permissions to the folders
4. Verify the organizer is actually running (check status in control panel)

---

### ❌ "Permission denied" errors

**Problem:** The application doesn't have permission to move files.

**Solution:**
1. Run `launch_control_panel.bat` as Administrator (right-click → Run as administrator)
2. Make sure you have write access to the monitored folders
3. Check if files are locked by another program

---

### ❌ Background mode not working

**Problem:** Organizer stops when closing the control panel.

**Solution:**
1. Make sure the "🔄 Run in Background" checkbox is checked **before** starting
2. If already running, stop it, check the box, then start again
3. Check `organizer_state.json` - it should show `"run_in_background": true`

---

## Testing Your Installation

### Test 1: Python Installation
```
python --version
```
Should show: Python 3.7 or higher

### Test 2: tkinter (GUI)
```
python -c "import tkinter; print('tkinter OK')"
```
Should show: tkinter OK

### Test 3: Dependencies
```
python -c "import watchdog; import psutil; print('All packages OK')"
```
Should show: All packages OK

### Test 4: Control Panel
```
python folder_manager.py
```
Should open the control panel window

---

## Getting Help

If none of these solutions work:

1. Check the log file: `C:\Users\YourName\FileOrganizer.log`
2. Make sure all requirements are met:
   - Python 3.7+ installed
   - tkinter included with Python
   - Dependencies installed (`pip install -r requirements.txt`)
3. Try running from Command Prompt to see error messages:
   ```
   cd "path\to\Silent Organizer"
   python folder_manager.py
   ```

---

## System Requirements

- **Operating System:** Windows 7 or higher
- **Python:** 3.7 or higher (with tkinter)
- **Dependencies:** watchdog, psutil (auto-installed)
- **Disk Space:** ~50 MB
- **Permissions:** Write access to monitored folders
