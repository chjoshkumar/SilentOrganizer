# Silent Organizer

Automatically organize files in your folders by type. Monitors folders in real-time and sorts files into categories (Pictures, Documents, Videos, Music, Archives, Others).

## Features

✅ **Multiple Folder Monitoring** - Monitor any number of folders simultaneously
✅ **Background Run Mode** - Keeps running even after closing the control panel
✅ **Easy Management** - Simple checkbox interface to enable/disable folders
✅ **Auto-Organization** - Files sorted automatically by type
✅ **Persistent State** - Remembers running status across sessions

## Quick Start

### First Time Setup
1. **Install dependencies**: Double-click `install_dependencies.bat`
2. **Open control panel**: Double-click `launch_control_panel.bat`
3. **Add folders**: Click quick buttons (Downloads, Desktop, etc.) or browse for custom folders
4. **Enable background mode** (optional): Check "🔄 Run in Background"
5. **Start**: Click "▶️ Start Organizer"

### Installing on Another PC
1. Copy the entire folder to new PC
2. Run `install_dependencies.bat`
3. Run `launch_control_panel.bat` and configure folders

📖 **Detailed guides available in `docs/` folder**

## File Organization

Files are automatically sorted into:
- **Pictures** - .jpg, .png, .gif, etc.
- **Videos** - .mp4, .avi, .mkv, etc.
- **Documents** - .pdf, .docx, .txt, etc.
- **Music** - .mp3, .wav, .flac, etc.
- **Archives** - .zip, .rar, .7z, etc.
- **Others** - Everything else

## Requirements

- Python 3.7 or higher
- Dependencies: `watchdog`, `psutil` (auto-installed by `install_dependencies.bat`)

## Troubleshooting

- **tkinter/GUI errors**: Reinstall Python with "tcl/tk and IDLE" option checked
- **Module not found**: Run `install_dependencies.bat`
- **Organizer stops immediately**: Check `C:\Users\YourName\FileOrganizer.log`
- **Old PC folders showing**: Edit `config.json` to remove them

📖 **Full troubleshooting guide:** `docs/TROUBLESHOOTING.md`

## Documentation

- 📖 `docs/SETUP_NEW_PC.md` - Installing on another PC
- 📖 `docs/QUICK_START.txt` - Quick reference guide
- 📖 `docs/CHANGELOG.md` - Version history and changes

## Files

**Essential:**
- `launch_control_panel.bat` - Start here
- `install_dependencies.bat` - Install required packages
- `prepare_for_new_pc.bat` - Clean before copying to new PC

**Auto-generated:**
- `config.json` - Your settings
- `organizer_state.json` - Running status
- `history.json` - File movement history
