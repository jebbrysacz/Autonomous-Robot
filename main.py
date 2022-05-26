import sys
import pigpio
import time
import threading
import random
sys.path.insert(0, "/home/jebjadchr/WeeklyGoals/Organized Code/Layer1")
from sensing import Sensors
sys.path.insert(0, "/home/jebjadchr/WeeklyGoals/Organized Code/Layer2")
from basicmotion import BasicMotions
sys.path.insert(0, "/home/jebjadchr/WeeklyGoals/Organized Code/Layer3")
from maze import Maze
sys.path.insert(0, "/home/jebjadchr/.local/lib/python2.7/site-packages")
import networkx as nx
import pickle

class Robot():
    def __init__(self, sensors):
        self.s = sensors #sensors already holds ultrasonic thread
        self.bm = BasicMotions(self.s)
        self.m = Maze(self.bm)
        self.motor = self.m.motor

        self.pause_driving = False
        self.next_location = None
        self.done = False
        self.explore = False

        self.driving_stopflag = False
        self.driving_thread = threading.Thread(target=self.driving_loop)

    def stop_driving(self):
        self.driving_stopflag = True

    def driving_loop(self):
        self.driving_stopflag = False
        while not self.driving_stopflag:
            if self.done:
                self.stop_driving()
                self.motor.shutdown()
                self.s.stop_us()
                break
            elif self.pause_driving:
                time.sleep(0.05)
            elif self.explore:
                can_explore = self.m.explore()
                if not can_explore:
                    print("Map fully explored!")
                    self.explore = False
                    self.pause = True
            elif self.next_location != None:
                can_reach = self.m.goto(self.next_location)
                self.next_location = None
                self.pause = True
                if not can_reach:
                    print("Target not in map!")
                

    
    def user_input(self):
        command = input("Command: ")
        command = command.lower()
        if (command == 'help' or command == 'h'): #works
            print("Avalible Commands")
            print("\tPause - Pauses robot at next intersection")
            print("\tExplore - Explores map without a target")
            print("\tGoto - Drives to a target (will prompt for target coords)")
            print("\tPrint - Prints the current map. Green nodes are explored, red are unexplored")
            print("\tQuit/q - Shutsrobot down without saving")
            print("\tSave/s - Saves the current map")
            print("\tLoad - Loads map from save file")
            print("\tPosition/pos - Assign the robot a new current position")
        
        elif (command == 'pause'): #works
            print("Pausing at the next intersection")
            self.pause_driving = True
        elif (command == 'explore'): #works
            print("Exploring without a target")
            self.explore = True
            self.pause_driving = False
            self.next_location = None
        elif (command == 'goto'): #works, maybe some edge cases
            good_x = False
            good_y = False
            while not good_x:
                try:
                    target_x = input("Target longitude: ")
                    int(target_x)
                    good_x = True
                except:
                    print("Input must be an integer!")
            while not good_y:
                try:
                    target_y = input("Target latitude: ")
                    int(target_y)
                    good_y = True
                except:
                    print("Input must be an integer!")
            self.next_location = (int(target_x), int(target_y))
            self.pause_driving = False
            self.explore = False
        elif (command == 'print'): #works
            self.m.print_graph()
        elif (command == 'quit' or command == 'q'): #works
            print("Quitting...")
            self.done = True
        elif (command == 'save' or command == 's'): #works
            print("Saving the map...")
            with open('map.pickle', 'wb') as filename:
                pickle.dump(self.m.G, filename)
        elif (command == 'load'): #works
            print("Loading the map...")
            with open('map.pickle', 'rb') as filename:
                self.m.G = pickle.load(filename)
        elif (command == 'pos' or command == "position"): #works
            good_x = False
            good_y = False
            good_h = False
            while not good_x:
                try:
                    target_x = input("Set longitude: ")
                    int(target_x)
                    good_x = True
                except:
                    print("Input must be an integer!")
            while not good_y:
                try:
                    target_y = input("Set latitude: ")
                    int(target_y)
                    good_y = True
                except:
                    print("Input must be an integer!")
            while not good_h: #dont think we need to update heading_bt, could be wrong
                target_h = input("Set heading (N,E,S,W): ")
                target_h = target_h.lower()
                if(str(target_h) == "n" or str(target_h) == "0"):
                    self.m.heading = 0
                    good_h = True
                elif(str(target_h) == "e" or str(target_h) == "1"):
                    self.m.heading = 1
                    good_h = True
                elif(str(target_h) == "s" or str(target_h) == "2"):
                    self.m.heading = 2
                    good_h = True
                elif(str(target_h) == "w" or str(target_h) == "3"):
                    self.m.heading = 3
                    good_h = True
                else:
                    print("Invalid heading!")
            
            self.m.long = int(target_x)
            self.m.lat = int(target_y)
        else:
            print("Unknown command '%s'" % command)
            print("Use 'help' or 'h' to see valid commands")

#Main Loop
#=================================================================
if __name__ == "__main__":
    sense = Sensors(5,6,7,8,23,15,18,16,13,20,19,21,26)
    robot = Robot(sense)
    try:
        robot.driving_thread.start()
        while not robot.done:
            print(sense.read_us())
            #robot.user_input()
    except BaseException as ex:
        print("ending due to exception: %s" % repr(ex))
    
    robot.motor.shutdown()
    robot.driving_thread.join()
        