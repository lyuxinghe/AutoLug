from dataclasses import dataclass
from simple_pid import PID
from control.motor import Motor
from control.encoder import Encoder
from control.controller import Controller
from control.tof import TOF
from tracking.tracker import Tracker
from util.parameters import *
import Jetson.GPIO as GPIO
import time
import threading
from multiprocessing import Manager, Process, Value, Array
from ctypes import c_char_p
from smbus2 import SMBus
from flask import Flask, request
import json
import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

import matplotlib.pyplot as plt

### GLOBALS ###
desired_speed = Value('f', 0.0)
deviation_angle = Value('f', 0.0)
max_speed = Value('f', 0.5)
l_speed = Value('f', 0.0)
r_speed = Value('f', 0.0)
l_pwm = Value('i', 0)
r_pwm = Value('i', 0)
distance = Value('f', 0.0)
stop_flag = False
manager = Manager()
frame_base64 = manager.Value(c_char_p, "")
bbox = Array('f', [0, 0, 0, 0])
track_status = Value('i', 0)
mode = Value('i', 0)

l_speed_list = []
r_speed_list = []
### ENDS ###

MODE_MANUAL = 0
MODE_AUTO = 1

app = Flask(__name__)

@app.route('/api/stats', methods=['GET'])
def get_stats():
    return json.dumps({'l_speed': l_speed.value,
                        'r_speed': r_speed.value,
                        'l_pwm': l_pwm.value,
                        'r_pwm': r_pwm.value,
                        'distance': distance.value,
                        'track_status': track_status.value,
                       })

@app.route('/api/controls', methods=['POST'])
def set_controls():
    data = request.json
    desired_speed.value = data['desired_speed']
    deviation_angle.value = data['deviation_angle']
    mode.value = 0
    return 'OK'

@app.route('/api/max_speed', methods=['POST'])
def set_max_speed():
    data = request.json
    max_speed.value = data['max_speed']
    return 'OK'

@app.route('/api/bbox', methods=['POST'])
def set_bbox():
    data = request.json['bbox']
    for i in range(4):
        bbox[i] = data[i]
    track_status.value = 2
    return 'OK'

@app.route('/api/camera', methods=['GET'])
def get_camera():
    mode.value = 1
    return json.dumps({'image': frame_base64.value}) 

def keyboard_thread():
    global stop_flag
    while True:
        key = input()
        if key == 'q':
            stop_flag = True
            break
        elif key.startswith('a'):
            deviation_angle.value = float(key[1:])
            print(f"deviation angle: {deviation_angle}")
        elif key.startswith('s'):
            desired_speed.value = float(key[1:])
            print(f"desired speed: {desired_speed}")

def update_speed_i2c(bus, speed_left, speed_right):
    try:
        bus.write_byte(I2C_ADDR, speed_left)
        bus.write_byte(I2C_ADDR, speed_right)
        return bus.read_byte(I2C_ADDR), bus.read_byte(I2C_ADDR)
    except:
        print("I2C read error")
        return 0, 0

def controller_loop(controller, i2c_bus):
    l_speedv, r_speedv, l_pwmv, r_pwmv, distancev = controller.update(deviation_angle.value, desired_speed.value)
    l_speed.value = l_speedv
    r_speed.value = r_speedv
    l_pwm.value = l_pwmv
    r_pwm.value = r_pwmv
    distance.value = distancev
    #print(f"angle: {deviation_angle.value}, speed: {desired_speed.value}, status: {track_status.value}")
    update_speed_i2c(i2c_bus, l_pwmv, r_pwmv)

    #Plotting
    l_speed_list.append(l_speedv)
    r_speed_list.append(r_speedv)

def main():
    global frame_base64
    GPIO.setmode(GPIO.BOARD)
    motor_left = Motor(1)
    motor_right = Motor(2)

    encoder_left = Encoder(1, ENC1)
    encoder_right = Encoder(2, ENC2)

    tof = TOF(1, TOF_IN, TOF_OUT)

    controller = Controller(motor_left, motor_right, encoder_left, encoder_right, tof, safety_distance=0.4)

    tracker = Tracker(bbox, frame_base64, track_status, max_speed, camera=0)

    # set speed according to bounding box [m/s]
    motor_left.set_speed(0)
    motor_right.set_speed(0)

    bus = SMBus(1)
    threading.Thread(target=keyboard_thread).start()
    server = Process(target=app.run, args=('0.0.0.0', 6969))
    server.start()

    while True:
        if mode.value == MODE_AUTO and track_status.value == 1:
            deviation_angle.value = tracker.get_deviation_angle()
            desired_speed.value = tracker.get_desired_speed()
        
        if mode.value == MODE_AUTO and track_status.value == 0:
            #deviation_angle.value = 80
            #desired_speed.value = max_speed.value
            deviation_angle.value = 0
            desired_speed.value = 0
            
        controller_loop(controller, bus)
        frame_base64.value = tracker.get_frame_base64()
        if stop_flag:
            break
        time.sleep(0.05)
    
    print("Cleaning up...")
    update_speed_i2c(bus, 0, 0)
    encoder_left.stop()
    encoder_right.stop()
    tof.stop()
    tracker.stop()
    bus.close()
    server.terminate()
    GPIO.cleanup()
    
    plt.plot(l_speed_list, label='left motor measured speed')
    plt.plot(r_speed_list, label='right motor measured speed')
    plt.xlabel('iteration')
    plt.ylabel('speed [m/s]')
    plt.title('Measured Motor Speed')
    plt.legend()
    plt.savefig('motor_speed.png')


if __name__ == '__main__':
    main()