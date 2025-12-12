#!/usr/bin/env python3
"""
Folder Manager for Silent Organizer
Easily add, remove, and manage monitored folders
"""

import os
import json
import sys
import subprocess
import threading
import time
import psutil
from tkinter import Tk, filedialog, messagebox, ttk, simpledialog
import tkinter as tk

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller. """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

CONFIG_FILE = resource_path('config.json')
STATE_FILE = resource_path('organizer_state.json')

def load_config():
    """Load configuration from JSON file."""
    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        messagebox.showerror("Error", f"Configuration file not found: {CONFIG_FILE}")
        return None
    except json.JSONDecodeError:
        messagebox.showerror("Error", "Invalid configuration file format")
        return None

def save_config(config):
    """Save configuration to JSON file."""
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
        return True
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save configuration: {e}")
        return False

def load_state():
    """Load organizer state from JSON file."""
    try:
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"is_running": False, "run_in_background": False, "pid": None}

def save_state(state):
    """Save organizer state to JSON file."""
    try:
        with open(STATE_FILE, 'w') as f:
            json.dump(state, f, indent=2)
        return True
    except Exception as e:
        print(f"Failed to save state: {e}")
        return False

def is_process_running(pid):
    """Check if a process with given PID is running."""
    if pid is None:
        return False
    try:
        process = psutil.Process(pid)
        return process.is_running() and process.status() != psutil.STATUS_ZOMBIE
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return False

class FolderManagerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Silent Organizer - Control Panel")
        self.root.geometry("800x650")
        self.root.resizable(True, True)
        
        # Set window icon and styling
        self.root.configure(bg='#f0f0f0')
        
        # Organizer process tracking
        self.organizer_process = None
        self.status_check_thread = None
        self.is_running = False
        self.run_in_background = tk.BooleanVar(value=False)
        self.state = load_state()
        
        self.config = load_config()
        if not self.config:
            self.root.destroy()
            return

        self.setup_ui()
        self.refresh_folder_list()
        self.check_organizer_status()
        
        # Load background run preference
        self.run_in_background.set(self.state.get('run_in_background', False))
    
    def setup_ui(self):
        """Setup the user interface."""
        # Create notebook for tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Main tab for folder management
        main_tab = ttk.Frame(notebook)
        notebook.add(main_tab, text="📁 Folder Management")
        
        # Settings tab
        settings_tab = ttk.Frame(notebook)
        notebook.add(settings_tab, text="⚙️ Settings")
        
        self.setup_main_tab(main_tab)
        self.setup_settings_tab(settings_tab)
    
    def setup_main_tab(self, parent):
        """Setup the main folder management tab."""
        # Title and description
        title_frame = ttk.Frame(parent)
        title_frame.pack(fill=tk.X, padx=10, pady=(10, 5))
        
        title_label = ttk.Label(title_frame, text="Silent Organizer Control Panel", 
                               font=("Arial", 16, "bold"))
        title_label.pack()
        
        desc_label = ttk.Label(title_frame, 
                              text="Select folders to automatically organize. Files will be sorted into categories.",
                              font=("Arial", 10))
        desc_label.pack(pady=(5, 0))
        
        # Quick add section
        quick_frame = ttk.LabelFrame(parent, text="Quick Add Common Folders", padding="10")
        quick_frame.pack(fill=tk.X, padx=10, pady=5)
        
        quick_buttons_frame = ttk.Frame(quick_frame)
        quick_buttons_frame.pack()
        
        ttk.Button(quick_buttons_frame, text="📥 Downloads", 
                  command=lambda: self.add_common_folder("Downloads")).pack(side=tk.LEFT, padx=5)
        ttk.Button(quick_buttons_frame, text="🖥️ Desktop", 
                  command=lambda: self.add_common_folder("Desktop")).pack(side=tk.LEFT, padx=5)
        ttk.Button(quick_buttons_frame, text="📄 Documents", 
                  command=lambda: self.add_common_folder("Documents")).pack(side=tk.LEFT, padx=5)
        ttk.Button(quick_buttons_frame, text="🎵 Music", 
                  command=lambda: self.add_common_folder("Music")).pack(side=tk.LEFT, padx=5)
        ttk.Button(quick_buttons_frame, text="🖼️ Pictures", 
                  command=lambda: self.add_common_folder("Pictures")).pack(side=tk.LEFT, padx=5)
        
        # Custom folder section
        custom_frame = ttk.LabelFrame(parent, text="Custom Folder Selection", padding="10")
        custom_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(custom_frame, text="📂 Browse and Add Custom Folder", 
                  command=self.add_folder, style="Accent.TButton").pack()
        
        # Current folders section
        folders_frame = ttk.LabelFrame(parent, text="Currently Monitored Folders", padding="10")
        folders_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Create treeview for better display
        columns = ("Status", "Name", "Path", "Type")
        try:
            self.folder_tree = ttk.Treeview(folders_frame, columns=columns, show="headings", height=10)

            # Configure columns
            self.folder_tree.heading("Status", text="☐ Click to Toggle", command=self.sort_by_status)
            self.folder_tree.heading("Name", text="Folder Name")
            self.folder_tree.heading("Path", text="Path")
            self.folder_tree.heading("Type", text="Type")

            self.folder_tree.column("Status", width=100, anchor="center")
            self.folder_tree.column("Name", width=200)
            self.folder_tree.column("Path", width=300)
            self.folder_tree.column("Type", width=100, anchor="center")

            # Bind click events for checkbox functionality
            self.folder_tree.bind("<Button-1>", self.on_tree_click)
            self.folder_tree.bind("<KeyPress-Return>", self.on_tree_keypress)
            self.folder_tree.bind("<KeyPress-space>", self.on_tree_keypress)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to create treeview: {e}")
            return

        # Scrollbars for treeview
        try:
            tree_scroll_y = ttk.Scrollbar(folders_frame, orient="vertical", command=self.folder_tree.yview)
            tree_scroll_x = ttk.Scrollbar(folders_frame, orient="horizontal", command=self.folder_tree.xview)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create scrollbars: {e}")
            return

        # Pack treeview and scrollbars
        self.folder_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        tree_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

        # Configure treeview to use scrollbars
        self.folder_tree.configure(yscrollcommand=tree_scroll_y.set, xscrollcommand=tree_scroll_x.set)
        
        # Help text
        help_label = ttk.Label(folders_frame, 
                              text="💡 Click the checkbox (☐/☑️) to enable/disable monitoring for each folder",
                              font=("Arial", 8), foreground="gray")
        help_label.pack(anchor=tk.W, pady=(5, 0))
        
        # Action buttons
        action_frame = ttk.Frame(folders_frame)
        action_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Remove the individual enable/disable buttons since it's now done via checkboxes
        ttk.Button(action_frame, text="🗑️ Remove Selected", 
                  command=self.remove_folder).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="✅ Enable All", 
                  command=self.enable_all_folders).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="❌ Disable All", 
                  command=self.disable_all_folders).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="🔄 Refresh", 
                  command=self.refresh_folder_list).pack(side=tk.RIGHT, padx=5)
        
        # Organizer control section
        control_frame = ttk.LabelFrame(parent, text="Organizer Control", padding="10")
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Status display
        status_frame = ttk.Frame(control_frame)
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(status_frame, text="Status:", font=("Arial", 10, "bold")).pack(side=tk.LEFT)
        self.status_label = ttk.Label(status_frame, text="🔴 Stopped", font=("Arial", 10))
        self.status_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Background run checkbox
        background_frame = ttk.Frame(control_frame)
        background_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.background_checkbox = ttk.Checkbutton(
            background_frame,
            text="🔄 Run in Background (continues even after closing this window)",
            variable=self.run_in_background,
            command=self.on_background_toggle
        )
        self.background_checkbox.pack(side=tk.LEFT)
        
        # Control buttons
        control_buttons_frame = ttk.Frame(control_frame)
        control_buttons_frame.pack()
        
        self.start_button = ttk.Button(control_buttons_frame, text="▶️ Start Organizer", 
                                      command=self.start_organizer)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(control_buttons_frame, text="⏹️ Stop Organizer", 
                                     command=self.stop_organizer, state="disabled")
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(control_buttons_frame, text="📋 View Logs", 
                  command=self.view_logs).pack(side=tk.LEFT, padx=5)
    
    def setup_settings_tab(self, parent):
        """Setup the settings tab."""
        settings_label = ttk.Label(parent, text="File Organization Settings", 
                                  font=("Arial", 14, "bold"))
        settings_label.pack(pady=20)
        
        # File type configuration (simplified view)
        types_frame = ttk.LabelFrame(parent, text="File Categories", padding="10")
        types_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Show current file type mappings
        if 'file_types' in self.config:
            for category, extensions in self.config['file_types'].items():
                category_frame = ttk.Frame(types_frame)
                category_frame.pack(fill=tk.X, pady=2)
                
                ttk.Label(category_frame, text=f"{category}:", 
                         font=("Arial", 10, "bold"), width=12).pack(side=tk.LEFT)
                ttk.Label(category_frame, text=", ".join(extensions)).pack(side=tk.LEFT, padx=(10, 0))
    
    def refresh_folder_list(self):
        """Refresh the folder list display."""

        try:
            # Clear existing items
            for item in self.folder_tree.get_children():
                self.folder_tree.delete(item)

            # Add folders to treeview
            for i, folder in enumerate(self.config.get('monitored_folders', [])):
                status = "☑️" if folder.get('enabled', True) else "☐"
                path = folder.get('path', '')
                name = folder.get('name', path)
                folder_type = "Home Folder" if folder.get('use_home_path', False) else "Custom Path"

                self.folder_tree.insert('', 'end', values=(status, name, path, folder_type), tags=('clickable',))

            # Configure tag for clickable items
            self.folder_tree.tag_configure('clickable', foreground='blue', font=('Arial', 9, 'bold'))

        except Exception as e:
            messagebox.showerror("Error", f"Failed to refresh folder list: {e}")
    
    def on_tree_click(self, event):
        """Handle clicks on the treeview."""
        # Get the item clicked
        item = self.folder_tree.identify_row(event.y)
        if not item:
            return
            
        # Get the column clicked
        column = self.folder_tree.identify_column(event.x)
        if column == '#1':  # Status column
            # Toggle the checkbox
            self.toggle_folder_from_tree(item)
    
    def on_tree_keypress(self, event):
        """Handle keyboard events on the treeview."""
        selection = self.folder_tree.selection()
        if selection:
            item = selection[0]
            self.toggle_folder_from_tree(item)
    
    def toggle_folder_from_tree(self, item):
        """Toggle folder status from treeview click."""
        try:
            # Get the index of the item
            all_items = self.folder_tree.get_children()
            index = all_items.index(item)
            
            # Get the folder configuration
            folder = self.config['monitored_folders'][index]
            folder['enabled'] = not folder.get('enabled', True)
            
            # Save configuration
            if save_config(self.config):
                # Update the display
                self.refresh_folder_list()
                
                # Re-select the item
                self.folder_tree.selection_set(item)
                self.folder_tree.focus(item)
                
                # Show confirmation
                status = "enabled" if folder['enabled'] else "disabled"
                messagebox.showinfo("Status Changed", f"'{folder['name']}' is now {status}!")
                
                # If organizer is running, suggest restart
                if self.is_running:
                    result = messagebox.askyesno("Restart Required", 
                                               "The organizer is currently running. Restart it to apply changes?")
                    if result:
                        self.restart_organizer()
            
        except (ValueError, IndexError) as e:
            messagebox.showerror("Error", f"Could not toggle folder status: {e}")
    
    def sort_by_status(self):
        """Sort folders by status (enabled first)."""
        if 'monitored_folders' not in self.config:
            return
            
        # Sort folders: enabled first, then disabled
        self.config['monitored_folders'].sort(key=lambda x: not x.get('enabled', True))
        
        if save_config(self.config):
            self.refresh_folder_list()
    
    def add_common_folder(self, folder_name):
        """Add a common folder (Downloads, Desktop, etc.) to monitoring."""
        # Check if folder already exists
        for folder in self.config.get('monitored_folders', []):
            if folder.get('path') == folder_name and folder.get('use_home_path', False):
                messagebox.showinfo("Info", f"{folder_name} folder is already being monitored!")
                return
        
        # Add the common folder
        new_folder = {
            "path": folder_name,
            "name": f"{folder_name} Folder",
            "enabled": True,
            "use_home_path": True
        }
        
        if 'monitored_folders' not in self.config:
            self.config['monitored_folders'] = []
        
        self.config['monitored_folders'].append(new_folder)
        
        if save_config(self.config):
            self.refresh_folder_list()
            messagebox.showinfo("Success", f"✅ {folder_name} folder added and enabled for monitoring!")
    
    def add_folder(self):
        """Add a custom folder to monitor."""
        folder_path = filedialog.askdirectory(title="Select Folder to Monitor")
        if not folder_path:
            return
        
        # Check if folder already exists
        for folder in self.config.get('monitored_folders', []):
            existing_path = folder.get('path', '')
            if folder.get('use_home_path', False):
                existing_full_path = os.path.join(os.path.expanduser('~'), existing_path)
            else:
                existing_full_path = existing_path
            
            if os.path.normpath(existing_full_path) == os.path.normpath(folder_path):
                messagebox.showinfo("Info", "This folder is already being monitored!")
                return
        
        # Ask for folder name
        name = simpledialog.askstring("Folder Name", 
                                     f"Enter a name for this folder:\n{folder_path}",
                                     initialvalue=os.path.basename(folder_path))
        if not name:
            name = os.path.basename(folder_path)
        
        # Check if it's in home directory
        home_path = os.path.expanduser('~')
        use_home_path = folder_path.startswith(home_path)
        
        if use_home_path:
            relative_path = os.path.relpath(folder_path, home_path)
        else:
            relative_path = folder_path
        
        # Add to config
        new_folder = {
            "path": relative_path if use_home_path else folder_path,
            "name": name,
            "enabled": True,
            "use_home_path": use_home_path
        }
        
        if 'monitored_folders' not in self.config:
            self.config['monitored_folders'] = []
        
        self.config['monitored_folders'].append(new_folder)
        
        if save_config(self.config):
            self.refresh_folder_list()
            messagebox.showinfo("Success", f"✅ {name} added and enabled for monitoring!")
    
    def remove_folder(self):
        selection = self.folder_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a folder to remove")
            return
        
        # Get the selected item
        item = selection[0]
        
        # Find the index of this item in the treeview
        all_items = self.folder_tree.get_children()
        try:
            index = all_items.index(item)
        except ValueError:
            messagebox.showerror("Error", "Could not find selected folder")
            return
            
        folder = self.config['monitored_folders'][index]
        
        result = messagebox.askyesno("Confirm", 
                                   f"Remove folder '{folder['name']}' from monitoring?")
        if result:
            del self.config['monitored_folders'][index]
            if save_config(self.config):
                self.refresh_folder_list()
                messagebox.showinfo("Success", "🗑️ Folder removed from monitoring")

    def toggle_folder(self, enable_state=None):
        """Toggle enable/disable status of selected folder."""
        selection = self.folder_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a folder to enable/disable")
            return
        
        # Get the selected item
        item = selection[0]
        
        # Find the index of this item in the treeview
        all_items = self.folder_tree.get_children()
        try:
            index = all_items.index(item)
        except ValueError:
            messagebox.showerror("Error", "Could not find selected folder")
            return
            
        folder = self.config['monitored_folders'][index]
        
        if enable_state is not None:
            folder['enabled'] = enable_state
        else:
            folder['enabled'] = not folder.get('enabled', True)
        
        if save_config(self.config):
            self.refresh_folder_list()
            status = "✅ enabled" if folder['enabled'] else "❌ disabled"
            messagebox.showinfo("Success", f"Folder '{folder['name']}' is now {status}!")
            
            # If organizer is running, suggest restart
            if self.is_running:
                result = messagebox.askyesno("Restart Required", 
                                           "The organizer is currently running. Restart it to apply changes?")
                if result:
                    self.restart_organizer()
    
    def enable_all_folders(self):
        """Enable all monitored folders."""
        if 'monitored_folders' not in self.config:
            return
            
        changed = False
        for folder in self.config['monitored_folders']:
            if not folder.get('enabled', True):
                folder['enabled'] = True
                changed = True
        
        if changed and save_config(self.config):
            self.refresh_folder_list()
            messagebox.showinfo("Success", "All folders have been enabled!")
            
            if self.is_running:
                result = messagebox.askyesno("Restart Required", 
                                           "The organizer is currently running. Restart it to apply changes?")
                if result:
                    self.restart_organizer()
    
    def disable_all_folders(self):
        """Disable all monitored folders."""
        if 'monitored_folders' not in self.config:
            return
            
        changed = False
        for folder in self.config['monitored_folders']:
            if folder.get('enabled', True):
                folder['enabled'] = False
                changed = True
        
        if changed and save_config(self.config):
            self.refresh_folder_list()
            messagebox.showinfo("Success", "All folders have been disabled!")
            
            if self.is_running:
                result = messagebox.askyesno("Restart Required", 
                                           "The organizer is currently running. Restart it to apply changes?")
                if result:
                    self.restart_organizer()
    
    def start_organizer(self):
        """Start the file organizer in the background."""
        if self.is_running:
            messagebox.showinfo("Info", "Organizer is already running!")
            return
        
        # Check if any folders are enabled
        enabled_folders = [f for f in self.config.get('monitored_folders', []) if f.get('enabled', True)]
        if not enabled_folders:
            messagebox.showwarning("Warning", "No folders are enabled for monitoring! Please enable at least one folder.")
            return
        
        try:
            # Start the main organizer script
            # Use DETACHED_PROCESS for true background execution on Windows
            if os.name == 'nt':
                DETACHED_PROCESS = 0x00000008
                self.organizer_process = subprocess.Popen(
                    [sys.executable, 'main.py'],
                    cwd=os.path.dirname(os.path.abspath(__file__)),
                    creationflags=subprocess.CREATE_NO_WINDOW | DETACHED_PROCESS if self.run_in_background.get() else subprocess.CREATE_NO_WINDOW,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            else:
                self.organizer_process = subprocess.Popen(
                    [sys.executable, 'main.py'],
                    cwd=os.path.dirname(os.path.abspath(__file__)),
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            
            self.is_running = True
            
            # Save state with PID
            self.state['is_running'] = True
            self.state['run_in_background'] = self.run_in_background.get()
            self.state['pid'] = self.organizer_process.pid
            save_state(self.state)
            
            self.update_ui_status()
            
            # Start status monitoring
            self.start_status_monitoring()
            
            folder_names = [f['name'] for f in enabled_folders]
            bg_msg = "\n\n⚠️ Background mode: Organizer will continue running even after closing this window." if self.run_in_background.get() else ""
            messagebox.showinfo("Success", f"🟢 Organizer started!\n\nMonitoring: {', '.join(folder_names)}{bg_msg}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start organizer: {e}")
    
    def stop_organizer(self):
        """Stop the file organizer."""
        if not self.is_running:
            messagebox.showinfo("Info", "Organizer is not running!")
            return
        
        try:
            # Try to terminate the process
            if self.organizer_process:
                self.organizer_process.terminate()
                try:
                    self.organizer_process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    self.organizer_process.kill()
            elif self.state.get('pid'):
                # Try to kill by PID if process object is not available
                try:
                    process = psutil.Process(self.state['pid'])
                    process.terminate()
                    process.wait(timeout=5)
                except (psutil.NoSuchProcess, psutil.TimeoutExpired):
                    pass
            
            self.is_running = False
            self.organizer_process = None
            
            # Update state
            self.state['is_running'] = False
            self.state['pid'] = None
            save_state(self.state)
            
            self.update_ui_status()
            
            messagebox.showinfo("Success", "🔴 Organizer stopped!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to stop organizer: {e}")
    
    def restart_organizer(self):
        """Restart the organizer to apply configuration changes."""
        if self.is_running:
            self.stop_organizer()
            time.sleep(1)
        self.start_organizer()
    
    def check_organizer_status(self):
        """Check if organizer is currently running based on saved state."""
        # Check if there's a saved PID and if that process is still running
        saved_pid = self.state.get('pid')
        if saved_pid and is_process_running(saved_pid):
            self.is_running = True
            # Try to get the process object
            try:
                self.organizer_process = psutil.Process(saved_pid)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                self.organizer_process = None
            
            # Start monitoring
            self.start_status_monitoring()
        else:
            self.is_running = False
            # Clean up stale state
            if self.state.get('is_running'):
                self.state['is_running'] = False
                self.state['pid'] = None
                save_state(self.state)
        
        self.update_ui_status()
    
    def start_status_monitoring(self):
        """Start monitoring the organizer process status."""
        def monitor():
            while self.is_running:
                # Check if process is still running
                pid = self.state.get('pid')
                if not is_process_running(pid):
                    # Process has ended
                    self.is_running = False
                    self.state['is_running'] = False
                    self.state['pid'] = None
                    save_state(self.state)
                    self.root.after(0, self.update_ui_status)
                    break
                time.sleep(2)
        
        self.status_check_thread = threading.Thread(target=monitor, daemon=True)
        self.status_check_thread.start()
    
    def on_background_toggle(self):
        """Handle background run checkbox toggle."""
        self.state['run_in_background'] = self.run_in_background.get()
        save_state(self.state)
        
        if self.is_running:
            msg = "Background mode enabled. The organizer will continue running even after you close this window."
            if not self.run_in_background.get():
                msg = "Background mode disabled. The organizer will stop when you close this window (requires restart to take effect)."
            messagebox.showinfo("Background Mode", msg)
    
    def update_ui_status(self):
        """Update the UI to reflect current organizer status."""
        if self.is_running:
            bg_indicator = " (Background)" if self.state.get('run_in_background') else ""
            self.status_label.config(text=f"🟢 Running{bg_indicator}", foreground="green")
            self.start_button.config(state="disabled")
            self.stop_button.config(state="normal")
        else:
            self.status_label.config(text="🔴 Stopped", foreground="red")
            self.start_button.config(state="normal")
            self.stop_button.config(state="disabled")
    
    def view_logs(self):
        """Open the log file to view organizer activity."""
        log_file = os.path.join(os.path.expanduser('~'), 'FileOrganizer.log')
        if os.path.exists(log_file):
            try:
                if os.name == 'nt':  # Windows
                    os.startfile(log_file)
                else:  # Linux/Mac
                    try:
                        subprocess.run(['xdg-open', log_file], check=True)
                    except (subprocess.CalledProcessError, FileNotFoundError):
                        # Fallback to basic open command
                        subprocess.run(['open', log_file])
            except Exception as e:
                messagebox.showerror("Error", f"Could not open log file: {e}")
        else:
            messagebox.showinfo("Info", "No log file found. Start the organizer to generate logs.")

def main():
    """Main function to run the folder manager."""
    root = Tk()
    
    # Try to set a better theme if available
    try:
        root.tk.call('source', 'azure.tcl')
        root.tk.call('set_theme', 'light')
    except:
        pass  # Fall back to default theme
    
    app = FolderManagerGUI(root)
    
    # Handle window closing
    def on_closing():
        if app.is_running:
            if app.run_in_background.get():
                # Background mode - just inform user
                result = messagebox.askyesno("Background Mode Active", 
                                           "The organizer is running in background mode and will continue running.\n\n"
                                           "Do you want to stop it before closing?")
                if result:
                    app.stop_organizer()
            else:
                # Normal mode - ask to stop
                result = messagebox.askyesno("Confirm Exit", 
                                           "The organizer is still running. Stop it before closing?")
                if result:
                    app.stop_organizer()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()
