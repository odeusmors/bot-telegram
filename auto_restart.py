import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
import subprocess

class Watcher(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith(".py"):
            print(f"🔄 Arquivo modificado: {event.src_path}, reiniciando bot...")
            os.system("pkill -f main.py")  # mata o bot atual
            subprocess.Popen(["python3", "main.py"])  # reinicia o bot

if __name__ == "__main__":
    path = "."
    event_handler = Watcher()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    print("👀 Observando alterações nos arquivos .py...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
