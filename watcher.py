import time
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ChangeHandler(FileSystemEventHandler):
    def __init__(self, script):
        self.script = script
        self.process = None

    def on_modified(self, event):
        if event.src_path.endswith(self.script):
            if self.process:
                self.process.terminate()
            self.process = subprocess.Popen(["python", self.script])

if __name__ == "__main__":
    script_to_watch = "main.py"
    event_handler = ChangeHandler(script_to_watch)
    observer = Observer()
    observer.schedule(event_handler, path=".", recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
