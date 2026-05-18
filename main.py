import threading
import cv2
import time
from vision_engine import VisionEngine
from controller import MouseController

class HandControllerApp:
    def __init__(self):
        self.vision_engine = VisionEngine()
        self.controller = MouseController()
        self.latest_hands = []
        self.running = True
        self.lock = threading.Lock()

    def vision_loop(self):
        while self.running:
            frame, hands = self.vision_engine.process_frame()
            if frame is None:
                continue

            with self.lock:
                self.latest_hands = hands

            cv2.imshow("Hand Tracking Feedback", frame)
            
            # Fail-safe exit key
            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.running = False
                break

    def control_loop(self):
        while self.running:
            hands = []
            with self.lock:
                hands = self.latest_hands
            
            if hands:
                for hand, label in hands:
                    self.controller.process_gestures(hand, label)
            
            # Run roughly at 60 FPS
            time.sleep(1/60)

    def run(self):
        print("Starting Hand Controller... Press 'q' to quit.")
        vision_thread = threading.Thread(target=self.vision_loop)
        control_thread = threading.Thread(target=self.control_loop)

        vision_thread.start()
        control_thread.start()

        vision_thread.join()
        control_thread.join()

        self.vision_engine.release()
        print("Application closed gracefully.")

if __name__ == "__main__":
    app = HandControllerApp()
    app.run()
