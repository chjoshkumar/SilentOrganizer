# Setup Guide - Installing Silent Organizer on a New PC

## Quick Setup (3 Steps)

### Step 1: Copy the Folder
Copy the entire "Silent Organizer" folder to your new PC (any location is fine)

### Step 2: Install Dependencies
Double-click `install_dependencies.bat` to automatically install required Python packages

### Step 3: Configure and Run
Double-click `launch_control_panel.bat` to open the control panel and add your folders

---

## Detailed Instructions

### Prerequisites
- **Python 3.7 or higher** must be installed on the new PC
- To check: Open Command Prompt and type `python --version`
- If not installed, download from: https://www.python.org/downloads/

### Installation Steps

1. **Copy the entire folder** to the new PC
   - You can place it anywhere (Desktop, Documents, C:\, etc.)

2. **Install required packages**
   - Option A: Double-click `install_dependencies.bat`
   - Option B: Open Command Prompt in this folder and run:
     ```
     pip install -r requirements.txt
     ```

3. **Configure folders**
   - Double-click `launch_control_panel.bat`
   - Add folders you want to monitor (Downloads, Desktop, etc.)
   - The old PC's folders (like E:/testing) will NOT work on the new PC
   - You'll need to add new folders specific to the new PC

4. **Start organizing**
   - Check "Run in Background" if you want it to run continuously
   - Click "Start Organizer"
   - Close the control panel (organizer keeps running in background mode)

---

## Important Notes

### ⚠️ What Gets Transferred
✅ **Will work on new PC:**
- Application code and logic
- File organization rules (Pictures, Documents, etc.)
- File type configurations (.jpg, .pdf, etc.)

❌ **Will NOT work on new PC:**
- Folder paths from old PC (like `E:/testing`, `F:/downloads`)
- Running organizer status
- Process IDs

### 🔧 What to Clean Up
After copying to the new PC, you should:
1. Delete or update `config.json` to remove old PC folder paths
2. Delete `organizer_state.json` (it will be recreated)
3. Delete `history.json` if you don't want old file movement history

### 📝 Fresh Start (Recommended)
For a clean installation on the new PC:
1. Copy only these files:
   - `main.py`
   - `folder_manager.py`
   - `requirements.txt`
   - `launch_control_panel.bat`
   - `install_dependencies.bat`
   - `prepare_for_new_pc.bat`
   - `README.md`

2. Run `install_dependencies.bat`
3. Run `launch_control_panel.bat` and configure your folders
   (config.json will be auto-created)

---

## Troubleshooting

### "Module not found" error
- Run `install_dependencies.bat` or `pip install -r requirements.txt`

### Folders from old PC showing up
- Open `config.json` and remove old folder paths
- Or delete `config.json` and let the app create a fresh one

### Organizer not starting
- Check the log file: `C:\Users\YourName\FileOrganizer.log`
- Make sure Python is installed and in PATH
- Reinstall dependencies: `pip install -r requirements.txt`

### Permission errors
- Run as Administrator if needed
- Make sure you have write access to the folders you're monitoring

---

## Quick Reference

### Files You Need
- ✅ `main.py` - Core organizer logic
- ✅ `folder_manager.py` - Control panel GUI
- ✅ `requirements.txt` - Python dependencies
- ✅ `launch_control_panel.bat` - Quick launcher
- ✅ `install_dependencies.bat` - Dependency installer

### Files You Can Delete (Optional)
- ❌ `config.json` - Will be recreated with your new folders
- ❌ `organizer_state.json` - Will be recreated
- ❌ `history.json` - Old file movement history
- ❌ `FileOrganizer.log` - Old logs

### Generated Files (Created Automatically)
- `config.json` - Your folder and file type settings
- `organizer_state.json` - Running status and background mode
- `C:\Users\YourName\FileOrganizer.log` - Activity log
- `C:\Users\YourName\FileOrganizer_history.json` - File movement history
