# imports:
import pigpio
import sys
import time
import math

RANGE = 254
FREQUENCY = 1000

# Class:
class Motor:

    def __init__(self, io, m1_la, m1_lb, m2_la, m2_lb):
        self.io = io
        self.m1_la = m1_la
        self.m1_lb = m1_lb
        self.m2_la = m2_la
        self.m2_lb = m2_lb

        self.v = 30
        self.w = 3.6
        
        pins = [self.m1_la, self.m1_lb, self.m2_la, self.m2_lb]
        self.io = pigpio.pi()
        if not self.io.connected:
            print("Unable to connect to pigpio daemon!")
            sys.exit(0)
        for i in pins:
            self.io.set_mode(i, pigpio.OUTPUT)
        for i in pins:
            self.io.set_PWM_range(i, RANGE)
        for i in pins:
            self.io.set_PWM_frequency(i, FREQUENCY)
        for i in pins:
            self.io.set_PWM_dutycycle(i, 0)
        
    def set_PWM_frequency(self, frequency):
        self.io.set_PWM_frequency(self.m1_la, frequency)
        self.io.set_PWM_frequency(self.m1_lb, frequency)
        self.io.set_PWM_frequency(self.m2_la, frequency)
        self.io.set_PWM_frequency(self.m2_lb, frequency)
        
    def set_PWM_range(self, pwm_range):
        self.io.set_PWM_range(self.m1_la, pwm_range)
        self.io.set_PWM_range(self.m1_lb, pwm_range)
        self.io.set_PWM_range(self.m2_la, pwm_range)
        self.io.set_PWM_range(self.m2_lb, pwm_range)

    def shutdown(self):
        print("Turning off...")
        self.io.set_PWM_dutycycle(self.m1_la, 0)
        self.io.set_PWM_dutycycle(self.m1_lb, 0)
        self.io.set_PWM_dutycycle(self.m2_la, 0)
        self.io.set_PWM_dutycycle(self.m2_lb, 0)
        self.io.stop()

    def set_m(self, leftdutycycle, rightdutycycle):
        if(-1 < leftdutycycle and leftdutycycle < 1 and -1 < rightdutycycle and rightdutycycle < 1):
                if(leftdutycycle < 0):
                    self.io.set_PWM_dutycycle(self.m1_lb, -leftdutycycle * RANGE)
                    self.io.set_PWM_dutycycle(self.m1_la, 0)
                if(leftdutycycle > 0):
                    self.io.set_PWM_dutycycle(self.m1_la, leftdutycycle * RANGE)
                    self.io.set_PWM_dutycycle(self.m1_lb, 0)
                if(rightdutycycle < 0):    
                    self.io.set_PWM_dutycycle(self.m2_la, -rightdutycycle * RANGE)
                    self.io.set_PWM_dutycycle(self.m2_lb, 0) 
                if(rightdutycycle > 0):
                    self.io.set_PWM_dutycycle(self.m2_lb, rightdutycycle * RANGE) 
                    self.io.set_PWM_dutycycle(self.m2_la, 0)
                if(rightdutycycle == 0):
                    self.io.set_PWM_dutycycle(self.m2_lb, 0)
                    self.io.set_PWM_dutycycle(self.m2_la, 0)
                if(leftdutycycle == 0):
                    self.io.set_PWM_dutycycle(self.m1_lb, 0)
                    self.io.set_PWM_dutycycle(self.m1_la, 0)
        else:
            print("duty cycle inputs must be between -1 and 1.")
            
    def set_linear(self, speed):
        if(speed <= (57.123 - 12.161) and speed >= 0):
            dutycycle = ((speed + 12.161)/57.123)
            self.set_m(dutycycle, dutycycle)
        if(speed >= -(57.123 - 12.161) and speed < 0):
            dutycycle = ((speed - 12.161)/57.123)
            self.set_m(dutycycle, dutycycle)
    
    def set_spin(self, omega):
        if(omega <= 5.7559 and omega >=0):
            dutycycle = math.pow(2.71828,((omega - 5.5)/5.2327))
            self.set_m(-dutycycle, dutycycle)
        elif(omega < 0 and omega>=-5.7559):
            dutycycle = math.pow(2.71828,(((-1*omega) - 5.5)/5.2327))
            self.set_m(dutycycle, -dutycycle)
        else:
            print("too fast!")
        
    def setvel(self, angular, linear):
        if(angular == 0):
            vl = linear
            vr = linear
        else:
            radius = linear/angular
            vl = angular*(radius+(13.5/2))
            vr = angular*(radius-(13.5/2))
        
        leftdutycycle = ((vl + 12.161)/57.123)
        rightdutycycle = ((vr + 12.161)/57.123)
                
        self.set_m(rightdutycycle,leftdutycycle)

    def forward(self):
        self.setvel(0,self.v)

    def veer_left(self):
        self.setvel(-1*self.w*0.5, self.v*5/7)
    
    def veer_right(self):
        self.setvel(self.w*0.5, self.v*5/7)

    def hard_left(self):
        self.setvel(-1*self.w*0.7, self.v*5/7)
    
    def hard_right(self):
        self.setvel(1*self.w*0.7, self.v*5/7)



        
        
            
