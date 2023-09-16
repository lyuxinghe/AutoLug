from simple_pid import PID
import Jetson.GPIO as GPIO
from util.parameters import *
from util.helper import clamp

class Motor():
    def __init__(self, id):
        self.id = id
        self.target_speed = 0
        self.current_speed = 0
        self.pid = PID(800, 100, 1.00, setpoint=0)
    
    def set_speed(self, speed):
        self.target_speed = speed
        self.pid.setpoint = speed
    
    def update(self, current_speed):
        self.current_speed = current_speed
        output = self.pid(current_speed)
        return int(clamp(output, 0, 255))


