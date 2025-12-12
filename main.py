import os
import sys
import json
import time
import shutil
import logging
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# --- LOGGING SETUP ---
# This creates a log file in your main user folder (e.g., C:\Users\kodur\FileOrganizer.log)
LOG_FILE = os.path.join(os.path.expanduser('~'), 'FileOrganizer.log')
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    force=True
)

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller. """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# --- CONFIGURATION AND SETUP ---
CONFIG_FILE = resource_path('config.json')
HISTORY_FILE = os.path.join(os.path.expanduser('~'), 'FileOrganizer_history.json')
PROCESSED_FILES = set()
OBSERVERS = []  # Store multiple observers

def load_config():
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)

def load_history():
    if not os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'w') as f: json.dump([], f)
    with open(HISTORY_FILE, 'r') as f:
        return json.load(f)

def save_history(record):
    history = load_history()
    history.append(record)
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=2)

def get_file_type(filename, config):
    file_ext = os.path.splitext(filename)[1].lower()
    for f_type, extensions in config['file_types'].items():
        if file_ext in extensions:
            return f_type
    return 'Others'

def is_file_stable(filepath, wait_seconds=2):
    try:
        initial_size = os.path.getsize(filepath)
        time.sleep(wait_seconds)
        final_size = os.path.getsize(filepath)
        return initial_size == final_size and final_size > 0
    except (OSError, FileNotFoundError):
        return False

class DownloadHandler(FileSystemEventHandler):
    def __init__(self, config, source_folder):
        self.config = config
        self.source_folder = source_folder

    def on_created(self, event):
        if not event.is_directory: self._process_file(event.src_path)

    def on_moved(self, event):
        if not event.is_directory:
            PROCESSED_FILES.add(event.src_path)
            self._process_file(event.dest_path)

    def _process_file(self, filepath):
        try:
            if filepath in PROCESSED_FILES: return
            filename = os.path.basename(filepath)
            if filename.startswith('.') or filename.endswith(('.tmp', '.crdownload')): return
            if not os.path.exists(filepath): return
            
            logging.info(f"File event detected for: {filename}")
            PROCESSED_FILES.add(filepath)

            while not is_file_stable(filepath):
                logging.info(f"Waiting for {filename} to be fully downloaded...")
                time.sleep(2)
            logging.info(f"{filename} is now stable.")

            file_type = get_file_type(filename, self.config)
            type_folder_name = self.config['folder_paths'].get(file_type, 'Others')
            destination_folder = os.path.join(self.source_folder, type_folder_name)
            os.makedirs(destination_folder, exist_ok=True)
            destination_path = os.path.join(destination_folder, filename)

            counter = 1
            base, ext = os.path.splitext(filename)
            while os.path.exists(destination_path):
                destination_path = os.path.join(destination_folder, f"{base}_{counter}{ext}")
                counter += 1
            
            shutil.move(filepath, destination_path)
            PROCESSED_FILES.add(destination_path)
            logging.info(f"Moved '{filename}' to '{os.path.relpath(destination_path, self.source_folder)}'")
            
            history_record = {
                "file": filename, "type": file_type, "date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "destination": os.path.relpath(destination_path, self.source_folder),
                "source_folder": self.source_folder
            }
            save_history(history_record)
        except Exception as e:
            logging.error(f"Error processing {filename}: {e}", exc_info=True)

def get_folder_path(folder_config):
    """Get the full path for a monitored folder."""
    if folder_config.get('use_home_path', False):
        return os.path.join(os.path.expanduser('~'), folder_config['path'])
    else:
        return folder_config['path']

def main_logic():
    """Contains the main application logic."""
    logging.info("--- Program Start ---")
    
    config = load_config()
    logging.info("Configuration loaded.")

    # Process each monitored folder
    for folder_config in config.get('monitored_folders', []):
        if not folder_config.get('enabled', True):
            continue
            
        folder_path = get_folder_path(folder_config)
        folder_name = folder_config.get('name', folder_path)
        
        if not os.path.exists(folder_path):
            logging.warning(f"Monitored folder does not exist: {folder_path}")
            continue
            
        logging.info(f"Setting up monitoring for: {folder_name} ({folder_path})")
        
        # Scan existing files in this folder
        logging.info(f"Scanning existing files in {folder_name}...")
        temp_handler = DownloadHandler(config, folder_path)
        try:
            for filename in os.listdir(folder_path):
                filepath = os.path.join(folder_path, filename)
                if os.path.isfile(filepath):
                    temp_handler._process_file(filepath)
        except Exception as e:
            logging.error(f"Error scanning {folder_name}: {e}")
        
        # Set up monitoring for this folder
        event_handler = DownloadHandler(config, folder_path)
        observer = Observer()
        observer.schedule(event_handler, folder_path, recursive=False)
        observer.start()
        OBSERVERS.append(observer)
        logging.info(f"--- Now monitoring: {folder_name} ({folder_path}) ---")

    if not OBSERVERS:
        logging.error("No folders are being monitored! Check your configuration.")
        return

    try:
        while True:
            time.sleep(3600) # Sleep for a long time
    except KeyboardInterrupt:
        logging.info("Stopping all observers...")
        for observer in OBSERVERS:
            observer.stop()
        logging.info("All observers stopped by user.")
    
    for observer in OBSERVERS:
        observer.join()

if __name__ == "__main__":
    # This top-level try-except will catch ANY crash during startup and log it.
    try:
        main_logic()
    except Exception as e:
        logging.critical(f"A FATAL error occurred during startup: {e}", exc_info=True)
        sys.exit(1)