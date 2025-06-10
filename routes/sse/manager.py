import threading
import time
from collections import defaultdict
from queue import Queue, Empty
import json


class SSEManager:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance.connections = defaultdict(list)
                cls._instance.event_queue = Queue()
                cls._instance.keep_alive_interval = 15

                # Start worker thread
                threading.Thread(target=cls._instance._worker,
                                 daemon=True).start()
        return cls._instance

    def add_connection(self, channel, connection):
        self.connections[channel].append(connection)

    def remove_connection(self, channel, connection):
        if channel in self.connections \
                and connection in self.connections[channel]:
            self.connections[channel].remove(connection)

    def send_event(self, channel, event_type, data):
        self.event_queue.put((channel, event_type, data))

    def _worker(self):
        while True:
            # Process events
            try:
                while True:
                    channel, event_type, data = self.event_queue.get_nowait()
                    if channel in self.connections:
                        for connection in self.connections[channel].copy():
                            try:
                                connection.send_event(event_type, data)
                            except Exception:
                                self.remove_connection(channel, connection)
            except Empty:
                pass

            # Send keep-alive
            for channel, connections in self.connections.items():
                for connection in connections.copy():
                    try:
                        connection.send_comment("keep-alive")
                    except Exception:
                        self.remove_connection(channel, connection)

            time.sleep(self.keep_alive_interval)


class SSEConnection:
    def __init__(self):
        self.queue = Queue()

    def send_event(self, event_type, data):
        event = f"event: {event_type}\n"
        event += "data: " + json.dumps(data) + "\n\n"
        self.queue.put(event)

    def send_comment(self, comment):
        self.queue.put(f": {comment}\n\n")

    def stream(self):
        try:
            while True:
                try:
                    yield self.queue.get(timeout=30)
                except Empty:
                    yield ": keep-alive\n\n"
        except GeneratorExit:
            pass
