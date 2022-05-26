import sys
sys.path.insert(0, "/home/jebjadchr/WeeklyGoals/Organized Code/Layer1")
from sensing import Sensors
import time
import math

class BasicMotions:

    def __init__(self, sensors):
        self.s = sensors
        self.motor = self.s.motor
        self.drift = self.s.drift
        self.mpu = self.s.mpu
        self.round_err = self.s.round_err

        self.w = 3.6
    
    def turn(self, direction):
        '''
        DIRECTIONS:
            0    - No spin
            1/-3 - Left
            2/-2 - Turn around
            3/-1 - Right
        '''
        #Setup direction and time to turn
        duration = 1
        direct = 1
        turn_vel = 0
        if(direction == 1 or direction == -3):
            self.turn_left()
        elif(direction == 3 or direction == -1):
            self.turn_right()
        elif(direction == 2 or direction == -2):
            self.turn_around()
        
    def turn_right(self):
        self.motor.set_spin(4.9)
        ang_change = 0
        start = time.time()
        delay = 0.05
        while(ang_change < ((math.pi)/4) or not bool(self.s.read_ls()[1])):
            if(ang_change + 0.75 > ((math.pi)/4)):
                self.motor.set_spin(self.w/1.5)
            elif time.time()-start > 0.1:
                self.motor.set_spin(self.w)
            ang_change -= round((delay)*(round(self.mpu.gyro[2],self.round_err)-round(self.drift,self.round_err)),self.round_err)
            time.sleep(delay)
        self.motor.setvel(0,0)
        time.sleep(0.25)
    
    def turn_left(self):
        self.motor.set_spin(-4.9)
        ang_change = 0
        start = time.time()
        delay = 0.05
        while(ang_change < ((math.pi)/4) or not bool(self.s.read_ls()[1])):
            if(ang_change + 0.75 > ((math.pi)/4)):
                self.motor.set_spin(-self.w/1.5)
            elif time.time()-start > 0.1:
                self.motor.set_spin(-self.w)
            ang_change += round((delay)*(round(self.mpu.gyro[2],self.round_err)-round(self.drift,self.round_err)),self.round_err)
            time.sleep(delay)
        self.motor.setvel(0,0)
        time.sleep(0.25)
    
    def turn_around(self):
        self.motor.set_spin(4.9)
        ang_change = 0
        start = time.time()
        delay = 0.05
        while(ang_change < ((math.pi*3)/4) or not bool(self.s.read_ls()[1])):
            if(ang_change + 0.5 > ((math.pi*3)/4)):
                self.motor.set_spin(self.w/1.5)
            elif time.time()-start > 0.1:
                self.motor.set_spin(self.w)
            ang_change -= round((delay)*(round(self.mpu.gyro[2],self.round_err)-round(self.drift,self.round_err)),self.round_err)
            time.sleep(delay)
        self.motor.setvel(0,0)
        time.sleep(0.25)
    
    def sample(self):
        to_return = [False, False, False, False]
        angles = []
        to_return[0] = bool(1 in self.s.read_ls())
        on_a_line = bool(1 in self.s.read_ls())
        ang_change = 0
        start = time.time()
        delay = 0.05
        self.motor.set_spin(-4.9)
        while(ang_change < math.pi*2-1 or not bool(1 in self.s.read_ls())):
            #PID things
            if(ang_change + 1 > math.pi*2):
                self.motor.set_spin(-self.w/1.5)
            elif time.time()-start > 0.1:
                self.motor.set_spin(-self.w)
            #Figure out what angles we see lines
            if(bool(self.s.read_ls()[1]) and not on_a_line):
                angles.append(ang_change)
                on_a_line = True
            elif(on_a_line and not bool(self.s.read_ls()[1])):
                on_a_line = False
                
            ang_change += round((delay)*(round(self.mpu.gyro[2],self.round_err)-round(self.drift,self.round_err)),self.round_err)
            time.sleep(delay)
        #stop the robot
        self.motor.setvel(0,0)
        time.sleep(0.25)
        #construct to_return
        for angle in angles:
            if 0.7 < angle and angle < 2.3:
                to_return[1] = True
            elif 2.4 < angle and angle < 3.9:
                to_return[2] = True
            elif 4.0 < angle and angle < 5.4:
                to_return[3] = True
        return(to_return)

    
    def __intersection(self):
        #get back axel over intersection
        self.motor.forward()
        time.sleep(0.275)
        #time.sleep(0.35)
        self.motor.setvel(0,0)
        time.sleep(0.25)

    def go_to_intersection(self):
        at_intersection = False
        to_return = [0,0,0]
        while(not at_intersection):
            sensors = self.s.read_ls()
            if(sensors == [0,1,0]):
                self.motor.forward()
            elif(sensors == [1,0,1]):
                self.motor.forward()
            elif(sensors == [1,1,0]):
                self.motor.veer_left()
            elif(sensors == [0,1,1]):
                self.motor.veer_right()
            elif(sensors == [1,0,0]):
                self.motor.hard_left()
            elif(sensors == [0,0,1]):
                self.motor.hard_right()              
            elif(sensors == [1,1,1]):
                #print("At intersection!")
                at_intersection = True
                to_return = self.s.read_us()
                self.__intersection()
            else:
                print("0ff the line!")
        return to_return

    def forward_until_blocked(self, distance):
        while(not self.s.read_us()[1] < distance and not self.s.read_us()[1] == 0):
            self.motor.forward()
        self.motor.setvel(0,0)

    def wall_following(self, distance):
        k = 0.01
        while True:
            state = self.s.read_us()
            desired = distance
            d = state[0]
            e = d - desired
            u = -k*e
            left = max(0.5, min(0.9, 0.7 - u))
            right = max(0.5, min(0.9, 0.7 + u))
            self.motor.set_m(left, right)

    def corners(self, distance):
        k = 0.005
        desired = distance
        while True:
            state = self.s.read_us()
            if(state[1] > desired):
                d = state[0]
                e = d - desired
                u = -k*e
                left = max(0.5, min(0.9, 0.7-0.05 - u))
                right = max(0.5, min(0.9, 0.7-0.05 + u))
                self.motor.set_m(left, right)
            else:
                self.motor.set_linear(0)
                time.sleep(1)
                self.turn_right_no_line()
        
    def turn_right_no_line(self):
        self.motor.set_spin(4.9)
        ang_change = 0
        start = time.time()
        delay = 0.05
        while(ang_change < ((math.pi)/2.5)):
            if(ang_change + 0.75 > ((math.pi)/4)):
                self.motor.set_spin(self.w/1.5)
            elif time.time()-start > 0.1:
                self.motor.set_spin(self.w)
            ang_change -= round((delay)*(round(self.mpu.gyro[2],self.round_err)-round(self.drift,self.round_err)),self.round_err)
            time.sleep(delay)
        self.motor.setvel(0,0)
        time.sleep(0.25)

    def follow_route(self, route):
        allowed = ["R","F","L","B"]
        for direction in route:
            assert(direction in allowed)
            if(direction == "R"):
                self.turn(3)
            elif(direction == "L"):
                self.turn(1)
            elif(direction == "B"):
                self.turn(2)
            #note: if direction == "F", we want to trek anyways
            self.go_to_intersection()

if __name__ == "__main__":
    sense = Sensors(5,6,7,8,23,15,18,16,13,20,19,21,26)
    bm = BasicMotions(sense)
    try:
        bm.corners(20)

    except BaseException as ex:
        print("ending due to exception: %s" % repr(ex))
        sense.stop_us()
        bm.motor.shutdown()

    sense.stop_us()
    bm.motor.shutdown()