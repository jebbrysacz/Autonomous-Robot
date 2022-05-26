import time
import math
import sys
sys.path.insert(0, "/home/jebjadchr/WeeklyGoals/Organized Code/Layer2")
from basicmotion import BasicMotions
import matplotlib.pyplot as plt
import random
sys.path.insert(0, "/home/jebjadchr/WeeklyGoals/Organized Code/Layer1")
from sensing import Sensors
sys.path.insert(0, "/home/jebjadchr/.local/lib/python2.7/site-packages")
import networkx as nx

class Maze:
    def __init__(self, basicmotion):
        self.bm = basicmotion
        self.motor = self.bm.motor
        self.long = 0 
        self.lat = -1
        self.heading = 0
        self.heading_bt = 0
        self.directions = []
        self.G = nx.Graph()



    def update_coords(self, prev_long, prev_lat):
        if(self.heading == 0):
            self.lat = prev_lat + 1
            self.long = prev_long
        elif(self.heading == 2):
            self.lat = prev_lat - 1
            self.long = prev_long
        elif(self.heading == 1):
            self.long = prev_long - 1
            self.lat = prev_lat
        elif(self.heading == 3):
            self.long = prev_long + 1
            self.lat = prev_lat
        #self.G.add_node
        return(self.long, self.lat)
    
    def intersection(self):
        self.heading_bt = self.heading
        self.heading = self.heading % 4 #this better not cause issues
        connections = [False, False, False, False] #N,W,S,E
        sample = self.bm.sample()
        
        connections[self.heading] = sample[0]
        connections[(self.heading-1)%4] = sample[-1]
        connections[(self.heading-2)%4] = sample[-2]
        connections[(self.heading-3)%4] = sample[-3]
        
        self.heading=(self.heading+sample.index(True))%4
        if(connections[0]):
            if(not self.G.has_node((self.long, self.lat+1))):
                self.G.add_node((self.long, self.lat+1), street=None, explored = False, blocked = False)
            if(not self.G.has_edge((self.long, self.lat), (self.long, self.lat+1))):
                self.G.add_edge((self.long, self.lat), (self.long, self.lat+1), weight=1, blocked = False)
        if(connections[1]):
            if(not self.G.has_node((self.long-1, self.lat))):
                self.G.add_node((self.long-1, self.lat), street=None, explored = False, blocked = False)
            if(not self.G.has_edge((self.long, self.lat), (self.long-1, self.lat))):
                self.G.add_edge((self.long, self.lat), (self.long-1, self.lat), weight=1, blocked = False)
        if(connections[2]):
            if(not self.G.has_node((self.long, self.lat-1))):
                self.G.add_node((self.long, self.lat-1), street=None, explored = False, blocked = False)
            if(not self.G.has_edge((self.long, self.lat), (self.long, self.lat-1))):
                self.G.add_edge((self.long, self.lat), (self.long, self.lat-1), weight=1, blocked = False)
        if(connections[3]):
            if(not self.G.has_node((self.long+1, self.lat))):
                self.G.add_node((self.long+1, self.lat), street=None, explored = False, blocked = False)
            if(not self.G.has_edge((self.long, self.lat), (self.long+1, self.lat))):
                self.G.add_edge((self.long, self.lat), (self.long+1, self.lat), weight=1, blocked = False)
        return connections

        '''    
        def forward(self):
            self.bm.go_to_intersection()
            prev_coords = (self.long, self.lat)
            curr_coords = self.update_coords(self.long, self.lat)
            if(not self.G.has_node(curr_coords)):
                self.G.add_node(curr_coords, street = None, explored = False)
            if(self.G.nodes[curr_coords]['explored'] == False):
                streets = self.intersection()
                self.G.nodes[curr_coords]['explored'] = True
                self.G.nodes[curr_coords]["street"] = streets
        '''    
            
    def forward(self):
        us_values = self.bm.go_to_intersection()
        prev_coords = (self.long, self.lat)
        curr_coords = self.update_coords(self.long, self.lat)

        if(not self.G.has_node(curr_coords)):
            self.G.add_node(curr_coords, street = None, explored = False, blocked = False)
        if(self.G.nodes[curr_coords]['explored'] == False):
            streets = self.intersection()
            self.G.nodes[curr_coords]['explored'] = True
            self.G.nodes[curr_coords]["street"] = streets
        self.check_for_blocked_edges(us_values)
            

    def check_for_blocked_edges(self, ultrasonics):
        ultrasonics
        if(ultrasonics[0] < 25): #left
            curr_coords = (self.long, self.lat)
            curr_heading = self.heading
            self.heading = (self.heading-1)%4
            node_to_check = self.update_coords(self.long, self.lat)
            if(self.G.has_edge((self.long, self.lat), curr_coords)):
                self.G.edge((self.long, self.lat), curr_coords)["blocked"] = True
            else:
                self.G.edge((self.long, self.lat), curr_coords)["blocked"] = False
            self.heading = curr_heading
            self.long = curr_coords[0]
            self.lat = curr_coords[1]

        if(ultrasonics[1] < 25): #middle
            curr_coords = (self.long, self.lat)
            curr_heading = self.heading
            self.heading = (self.heading)%4
            node_to_check = self.update_coords(self.long, self.lat)
            if(self.G.has_edge((self.long, self.lat), curr_coords)):
                self.G.edge((self.long, self.lat), curr_coords)["blocked"] = True
            else:
                self.G.edge((self.long, self.lat), curr_coords)["blocked"] = False
            self.heading = curr_heading
            self.long = curr_coords[0]
            self.lat = curr_coords[1]
            
        if(ultrasonics[2] < 25): #right
            curr_coords = (self.long, self.lat)
            curr_heading = self.heading
            self.heading = (self.heading+1)%4
            node_to_check = self.update_coords(self.long, self.lat)
            if(self.G.has_edge((self.long, self.lat), curr_coords)):
                self.G.edge((self.long, self.lat), curr_coords)["blocked"] = True
            else:
                self.G.edge((self.long, self.lat), curr_coords)["blocked"] = False
            self.heading = curr_heading
            self.long = curr_coords[0]
            self.lat = curr_coords[1]


    def random_turn(self):
        direction = random.randint(0,3)
        curr_coords = (self.long,self.lat)
        while(self.G.nodes[curr_coords]['street'][(direction+self.heading_bt)%4] == False):
            direction = random.randint(0,3)
        if (direction == 0 or direction == 2):
            self.directions.append(direction)
        else:
            self.directions.append((direction+2)%4)
        self.bm.turn(int((direction+(self.heading_bt-self.heading))%4))
        self.heading = (direction+self.heading_bt)%4

    def get_explored_nodes(self, curr_coords):
        explored = []
        streets = self.G.nodes[curr_coords]["street"]
        if(streets[0]):
            explored.append(self.G.nodes[(self.long, self.lat+1)]["explored"])
        else:
            explored.append(2)
        if(streets[1]):
            explored.append(self.G.nodes[(self.long-1, self.lat)]["explored"])
        else:
            explored.append(2)
        if(streets[2]):
            explored.append(self.G.nodes[(self.long, self.lat-1)]["explored"])
        else:
            explored.append(2)
        if(streets[3]):
            explored.append(self.G.nodes[(self.long+1, self.lat)]["explored"])
        else:
            explored.append(2)
        return explored 
        
    def random_turn_6(self):
        direction = random.randint(0,3)
        curr_coords = (self.long,self.lat)
        explored = self.get_explored_nodes(curr_coords)    
        while(bool(explored[(direction+self.heading_bt)%4]) and (False in explored or explored[(direction+self.heading_bt)%4] == 2)):
            direction = random.randint(0,3)
        turn_amount = int((direction+(self.heading_bt-self.heading))%4)
        if turn_amount == 2:
            self.bm.turn_around()
        else:
            self.bm.turn(turn_amount)
        explored[(direction+self.heading_bt)%4] = True
        self.heading = (direction+self.heading_bt)%4

    def update_heading(self, turn):
        if turn == "L":
            self.heading += 1
        if turn == "B":
            self.heading += 2
        if turn == "R":
            self.heading += 3
        self.heading = self.heading % 4

    def follow(self, list):
        directions = []
        previous = list[0]
        for i in list:
            moved = False
            direction = (i[0] - previous[0], i[1] - previous[1])
            previous = (i[0], i[1])
            if direction == (0, -1):
                moved = True
                if self.heading == 0:
                    directions.append("B")
                elif self.heading == 1:
                    directions.append("L")
                elif self.heading == 2:
                    directions.append("F")
                elif self.heading == 3:
                    directions.append("R")
            elif direction == (0, 1):
                moved = True
                if self.heading == 0:
                    directions.append("F")
                elif self.heading == 1:
                    directions.append("R")
                elif self.heading == 2:
                    directions.append("B")
                elif self.heading == 3:
                    directions.append("L")
            elif direction == (-1, 0):
                moved = True
                if self.heading == 0:
                    directions.append("L")
                elif self.heading == 1:
                    directions.append("F")
                elif self.heading == 2:
                    directions.append("R")
                elif self.heading == 3:
                    directions.append("B")
            elif direction == (1, 0):
                moved = True
                if self.heading == 0:
                    directions.append("R")
                elif self.heading == 1:
                    directions.append("B")
                elif self.heading == 2:
                    directions.append("L")
                elif self.heading == 3:
                    directions.append("F")
            if moved:
                self.update_heading(directions[-1])
                self.update_coords(self.long, self.lat)
                
        return directions

    def turn_7(self):
        direction = random.randint(0,3)
        curr_coords = (self.long,self.lat)
        explored = self.get_explored_nodes(curr_coords)
        if(not False in explored):
            if(False in nx.get_node_attributes(self.G, "explored").values()):
                node_list = list(self.G.nodes())
                node_num = 0
                while(self.G.nodes[node_list[node_num]]["explored"]):
                    node_num += 1
                shortest_path = nx.shortest_path(self.G, curr_coords, node_list[node_num])
                route = self.follow(shortest_path)
                self.bm.follow_route(route)
                curr_coords = (self.long,self.lat)
                streets = self.intersection()
                self.G.nodes[curr_coords]['explored'] = True
                self.G.nodes[curr_coords]["street"] = streets
        else:
            while(bool(explored[(direction+self.heading_bt)%4]) and (False in explored or explored[(direction+self.heading_bt)%4] == 2)):
                direction = random.randint(0,3)
            turn_amount = int((direction+(self.heading_bt-self.heading))%4)
            if turn_amount == 2:
                self.bm.turn_around()
            else:
                self.bm.turn(turn_amount)
            explored[(direction+self.heading_bt)%4] = True
            self.heading = (direction+self.heading_bt)%4
    
    def explore(self):
        if(len(self.G.nodes()) <3 or False in nx.get_node_attributes(self.G, "explored").values()):
            self.forward()
            self.turn_7()
            return True
        else:
            return False
    
    def goto(self, target):
        curr_coords = (self.long,self.lat)
        if(target in list(self.G.nodes())):
            shortest_path = nx.shortest_path(self.G, curr_coords, target)
            route = self.follow(shortest_path)
            self.bm.follow_route(route)
        elif(len(self.G.nodes()) > 3 or False in nx.get_node_attributes(self.G, "explored").values()):

            #GOTO NEAREST UNEXPLORED NODE

            while(False in nx.get_node_attributes(self.G, "explored").values() and (self.long, self.lat) != target):
                node_list = list(self.G.nodes())
                unexplored_list = []
                for node in node_list:
                    if not self.G.nodes[node]["explored"]:
                        unexplored_list.append(node)
                min_distance = 1000000 #big number
                if unexplored_list == []:
                    return False
                for i in range(0, len(unexplored_list)):
                    distance = abs(target[0]-unexplored_list[i][0]) + abs(target[1]-unexplored_list[i][1])
                    if min_distance > distance:
                        min_distance = distance
                        next_stop = unexplored_list[i]
                self.goto(next_stop)

        """ elif(len(self.G.nodes()) > 3 or False in nx.get_node_attributes(self.G, "explored").values()):
            while((len(self.G.nodes()) <3 or False in nx.get_node_attributes(self.G, "explored").values()) and (self.long, self.lat) != target):
                self.forward()
                self.turn_7() """
        curr_coords = (self.long, self.lat)
        if(target != (self.long, self.lat)):
            return False
        elif(self.G.nodes[target]['explored'] == False):
            curr_coords = (self.long, self.lat)
            streets = self.intersection()
            self.G.nodes[curr_coords]['explored'] = True
            self.G.nodes[curr_coords]["street"] = streets
        elif(self.G.nodes[curr_coords]["street"][self.heading] == False):
                self.bm.turn_left()
                self.heading = self.G.nodes[curr_coords]["street"].index(True)
        return True

    def print_graph(self):
        node_list = list(self.G.nodes())
        pos = {}
        color = []
        for node in node_list:
            pos[node] = node
            if self.G.nodes[node]["explored"] == False:
                color.append("red")
            else:
                color.append("green")
        nx.draw(self.G, pos=pos, node_color = color, with_labels = True)
        plt.show()

if __name__ == "__main__":
    sense = Sensors(5,6,7,8,23,15,18,16,13,20,19,21,26)
    bm = BasicMotions(sense)
    maze = Maze(bm)
    try:
        while(len(maze.G.nodes())<3 or False in nx.get_node_attributes(maze.G, "explored").values()):
            maze.forward()
            maze.turn_7()
        node_list = list(maze.G.nodes())
        pos = {}
        color = []
        for node in node_list:
            pos[node] = node
            if maze.G.nodes[node]["explored"] == False:
                color.append("red")
            else:
                color.append("green")
        maze.motor.shutdown()
        nx.draw(maze.G, pos=pos, node_color = color)
        plt.show()
    except BaseException as ex:
        print("ending due to exception: %s" % repr(ex))

    sense.stop_us()
    bm.motor.shutdown()
