import sys
import pigpio
import time

READY = 0
EXPECT_RISING = 1
EXPECT_FALLING = 2

# 13/16 -> US1 *left
# 19/20 -> US2 *forward
# 26/21 -> US3 *right

class Ultrasound:

    def __init__(self, io, echo, trig):
        self.distance = 0
        self.change = 0
        self.echo = echo
        self.trig = trig
        self.start_time = 0
        self.io = io
        self.state = READY

        io.set_mode(echo, pigpio.INPUT)
        io.set_mode(trig, pigpio.OUTPUT)

        self.rcb = self.io.callback(self.echo, pigpio.RISING_EDGE, self.rising)
        self.fcb = self.io.callback(self.echo, pigpio.FALLING_EDGE, self.falling)


    def rising(self, gpio, level, tick):
        if not self.state == EXPECT_RISING:
            return
        self.start_time = tick
        self.state = EXPECT_FALLING
        

    def falling(self, gpio, level, tick):
        if not self.state == EXPECT_FALLING:
            return
        dt = tick - self.start_time
        previous = self.distance
        self.distance = dt * (0.0343)/2
        self.change = (self.distance - previous) / dt
        self.state = READY

    def send_trig(self):
        if not self.state == READY:
            return
        self.io.write(self.trig, 1)
        time.sleep(0.00001)
        self.io.write(self.trig, 0)
        self.state = EXPECT_RISING
    
    def read(self):
        self.send_trig()

if __name__ == "__main__":
    io = pigpio.pi()
    ultrasound = Ultrasound(20, 19, io)
    try:
        while True:
            ex1 = ultrasound.rcb
            ex2 = ultrasound.fcb
            ultrasound.send_trig()
            time.sleep(0.1)
    except BaseException as ex:
        print("ending due to exception: %s" % repr(ex))
        ex1.cancel()
        ex2.cancel()



