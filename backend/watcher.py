# backend/watcher.py
import time
import json
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from backend.metadata_extractor import extract_metadata_from_directory
from backend.ollama_tagger import suggest_for_metadata
import os

WATCH_DIR = os.environ.get("WATCH_DIRECTORY")
TAGGED_FILE_PATH = os.environ.get('TAGGED_OUTPUT_FILE')
METADATA_FILE_PATH = os.environ.get('RAW_METADATA_FILE_PATH')

class AudioHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory and not event.src_path.startswith('.'):
            print(f"New file: {event.src_path}")
            metadata = extract_metadata_from_directory(WATCH_DIR)
            with open("sound_metadata.json", "w") as f:
                json.dump(metadata, f, indent=2)
            suggest_for_metadata(METADATA_FILE_PATH, TAGGED_FILE_PATH)

def start_watcher():
    observer = Observer()
    observer.schedule(AudioHandler(), path=WATCH_DIR, recursive=True)
    observer.start()
    print(f"Watching {WATCH_DIR}...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
