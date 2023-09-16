import Jetson.GPIO as GPIO
import threading
import time

from util.parameters import DISTANCE_PER_PULSE

class Encoder():
    def __init__(self, id, pin):
        self.id = id
        self.pin = pin
        self.steps = 0
        self.prev_steps = 0
        self.period = 0.05
        self.stop_flag = False

        self.thread = threading.Thread(target=self.sample_loop)
        self.thread.start()

        GPIO.setup(self.pin, GPIO.IN)
        GPIO.add_event_detect(self.pin, GPIO.RISING, callback=self.handler)
    
    def handler(self, channel):
        self.steps += 1
    
    def sample_loop(self):
        while True:
            self.speed = (self.steps - self.prev_steps) * DISTANCE_PER_PULSE / self.period
            self.prev_steps = self.steps
            if self.stop_flag:
                return
            time.sleep(self.period)
    
    def stop(self):
        self.stop_flag = True
        self.thread.join()

    def get_speed(self):
        # 16 pulses per revolution
        return self.speed

