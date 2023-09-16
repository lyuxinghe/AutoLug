from simple_pid import PID
from control.motor import Motor
from control.encoder import Encoder
from control.controller import Controller
from util.parameters import *
import Jetson.GPIO as GPIO
import time
import sys
import threading
from smbus2 import SMBus

desired_speed = 1.0
deviation_angle = 45.0
stop_flag = False

def update_speed_i2c(bus, speed_left, speed_right):
    bus.write_byte(I2C_ADDR, speed_left)
    bus.write_byte(I2C_ADDR, speed_right)
    return bus.read_byte(I2C_ADDR), bus.read_byte(I2C_ADDR)

def keyboard_thread():
    global stop_flag
    while True:
        key = input()
        if key == 'q':
            stop_flag = True
            break
        elif key.startswith('a'):
            deviation_angle = float(key[1:])
            print(f"deviation angle: {deviation_angle}")
        elif key.startswith('s'):
            desired_speed = float(key[1:])
            print(f"desired speed: {desired_speed}")

def main():

    GPIO.setmode(GPIO.BOARD)
    motor_left = Motor(1)
    motor_right = Motor(2)

    encoder_left = Encoder(1, ENC1)
    encoder_right = Encoder(2, ENC2)

    # set speed according to bounding box [m/s]
    motor_left.set_speed(0.5)
    motor_right.set_speed(0.5)
    bus = SMBus(1)
    threading.Thread(target=keyboard_thread).start()
    while True:
        l_speed_obs = encoder_left.get_speed()
        r_speed_obs = encoder_right.get_speed()
        print(f"left speed: {l_speed_obs}, right speed: {r_speed_obs}")
        l_pwm = motor_left.update(l_speed_obs)
        r_pwm = motor_right.update(r_speed_obs)
        update_speed_i2c(bus, l_pwm, r_pwm)
        if stop_flag:
            break
        time.sleep(0.05)
    
    print("Cleaning up...")
    update_speed_i2c(bus, 0, 0)
    encoder_left.stop()
    encoder_right.stop()
    bus.close()
    GPIO.cleanup()
    return

        

if __name__ == '__main__':
    main()