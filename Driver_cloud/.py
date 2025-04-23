import time
import threading
from database_communication import DatabaseCommunication
from greeting_server import GreetingServer

class WaitingThread(threading.Thread):
    def __init__(self, wait_time=5000):
        super().__init__()
        self.wait_time = wait_time / 1000  # Convert to seconds
        self.waiting_to_complete = True
        self.db = DatabaseCommunication()

    def run(self):
        elapsed_time = 0
        while self.waiting_to_complete:
            try:
                print(f"Waiting thread active: {elapsed_time} sec")
                time.sleep(1)
                elapsed_time += 1

                if elapsed_time >= self.wait_time:
                    self.waiting_to_complete = False
            except Exception as e:
                print("Waiting thread error:", e)

if __name__ == "__main__":
    wait_thread = WaitingThread(5000)
    wait_thread.start()