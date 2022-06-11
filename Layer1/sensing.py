# imports:
import pigpio
import sys
import time
import math
from motor import Motor
import threading
from ultrasound import Ultrasound
import random
import board
import adafruit_mpu6050

# Class:
class Sensors:

    def __init__(self, m1_la, m1_lb, m2_la, m2_lb, left_ls, middle_ls, right_ls, echo_l, trig_l, echo_m, trig_m, echo_r, trig_r):

        self.io = pigpio.pi()

        self.pickedup = False

        self.motor = Motor(self.io, m1_la, m1_lb, m2_la, m2_lb)
        
        self.line_l = left_ls
        self.line_m = middle_ls
        self.line_r = right_ls

        self.curr_lines = [0,0,0]
        self.prev_lines = [0,0,0]

        self.us_l = Ultrasound(self.io, echo_l, trig_l)
        self.us_m = Ultrasound(self.io, echo_m, trig_m)
        self.us_r = Ultrasound(self.io, echo_r, trig_r)
        self.stopflag = False
        self.t1 = threading.Thread(target=self.run_continual_us, args=(self.us_l,))
        self.t2 = threading.Thread(target=self.run_continual_us, args=(self.us_m,))
        self.t3 = threading.Thread(target=self.run_continual_us, args=(self.us_r,))
        self.t5 = threading.Thread(target=self.picked_up)
        
        self.round_err = 3
        self.i2c = board.I2C()  # uses board.SCL and board.SDA
        self.mpu = adafruit_mpu6050.MPU6050(self.i2c)
        self.drift = self.calc_drift()
        self.t4 = threading.Thread(target=self.run_gyro, args=(self.mpu,))
    
    def calc_drift(self):
        total = 0
        loops = 100
        time.sleep(1)
        for i in range(0,loops):
            driftt = self.mpu.gyro[2]
            total += driftt
        drift = round(total/loops, self.round_err)
        print("Avg drift:", drift)
        return round(total/loops, self.round_err)

    def stop_continual_us(self):
        self.stopflag = True

    def run_continual_us(self, us):
        self.stopflag = False
        while(not self.stopflag):
            us.send_trig()
            time.sleep(0.2 + 0.1 * random.random())
    
    def picked_up(self):
        while not self.stopflag:
            #print(self.us_l.distance, self.us_m.distance, self.us_r.distance)
            if(self.read_ls_no_update() == [1,1,1] and
                self.us_m.distance < 5):
                print("picked up!")
                self.pickedup = True
            else:
                self.pickedup = False
            time.sleep(0.5)

    def start_us(self):
        self.t1.start()
        self.t2.start()
        self.t3.start()
        self.t5.start()
        time.sleep(2)
    
    def stop_us(self):
        self.stop_continual_us()
        self.t1.join()
        self.t2.join()
        self.t3.join()
        self.t5.join()
    
    def read_ls(self):
        self.prev_lines = self.curr_lines
        self.curr_lines = [self.io.read(self.line_l), self.io.read(self.line_m), self.io.read(self.line_r)]
        return self.curr_lines
    
    def read_ls_no_update(self):
        return [self.io.read(self.line_l), self.io.read(self.line_m), self.io.read(self.line_r)]

    def read_us(self):
        return [self.us_l.distance, self.us_m.distance, self.us_r.distance]
    
    def run_gyro(self):
        return 0

if __name__ == "__main__":
    sense = Sensors(5,6,7,8,23,15,18,16,13,20,19,21,26)
    try:
        while True:
            print("Line Sensors:", sense.read_ls())
            print("Ultrasonic Sensors:", sense.read_us())
            time.sleep(1)

    except BaseException as ex:
        print("ending due to exception: %s" % repr(ex))
        sense.stop_us()

    