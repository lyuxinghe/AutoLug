import Jetson.GPIO as GPIO
import threading
import time

from util.parameters import DISTANCE_PER_PULSE

class TOF():
    def __init__(self, id, input_pin, output_pin):
        self.id = id
        self.input_pin = input_pin
        self.output_pin = output_pin
        self.period = 0.05
        self.stop_flag = False
        self.send_time = None
        self.distance = 0

        GPIO.setup(self.input_pin, GPIO.IN)
        GPIO.setup(self.output_pin, GPIO.OUT)

        self.thread = threading.Thread(target=self.sample_loop)
        self.thread.start()
    
    def sample_loop(self):
        while not self.stop_flag:
            self.distance = self.find_distance()
            time.sleep(self.period)

    def find_distance(self):
        # set Trigger to HIGH
        GPIO.output(self.output_pin, True)
    
        # set Trigger after 0.01ms to LOW
        time.sleep(0.00001)
        GPIO.output(self.output_pin, False)

        sense_time = time.time()
    
        StartTime = time.time()
        StopTime = time.time()
    
        # save StartTime
        while GPIO.input(self.input_pin) == 0 and time.time() - sense_time < 0.1:
            StartTime = time.time()
    
        # save time of arrival
        while GPIO.input(self.input_pin) == 1 and time.time() - sense_time < 0.1:
            StopTime = time.time()
    
        # time difference between start and arrival
        TimeElapsed = StopTime - StartTime
        # multiply with the sonic speed (34300 cm/s)
        # and divide by 2, because there and back
        distance = (TimeElapsed * 343) / 2
    
        return distance
    
    def get_distance(self):
        return self.distance
    
    def stop(self):
        self.stop_flag = True
        self.thread.join()
    
