import time
import math
import sys
import copy
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

        return self.add_edges_and_nodes(connections)
    
    def add_edges_and_nodes(self, connections):
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
        returned = self.bm.go_to_intersection()
        us_values = returned[0]
        in_tunnel = (us_values[0]<30 and us_values[2]<30)
        prev_coords = (self.long, self.lat)
        curr_coords = self.update_coords(self.long, self.lat)
        if(not self.G.has_node(curr_coords)):
            self.G.add_node(curr_coords, street = None, explored = False, blocked = (not returned[1]))
        else:
            self.G.nodes[curr_coords]["blocked"] = (not returned[1])
        if(not returned[1]):
            self.long = prev_coords[0]
            self.lat = prev_coords[1]
            self.heading = (self.heading + 2)%4
            curr_coords = prev_coords
            if(not self.G.has_node(curr_coords)):
                self.G.add_node(curr_coords, street = None, explored = False, blocked = False)
                print("This should not happen")
        if(self.G.nodes[curr_coords]['explored'] == False):
            if(in_tunnel):
                self.heading_bt = self.heading
                streets = [False, False, False, False]
                streets[self.heading] = True
                streets[(self.heading-2)%4] = True
                self.add_edges_and_nodes(streets)
            else:
                streets = self.intersection()
            self.G.nodes[curr_coords]['explored'] = True
            self.G.nodes[curr_coords]["street"] = streets
        print("us_values:", us_values)
        self.check_for_blocked_edges(us_values)
            

    def check_for_blocked_edges(self, ultrasonics):
        curr_coords = (self.long, self.lat)
        curr_heading = self.heading
        self.heading = (self.heading_bt+1)%4
        node_to_check = self.update_coords(self.long, self.lat)
        print("edge blocked:", curr_coords, (self.long, self.lat))
        print("curr_heading:", curr_heading, "pretend heading:", self.heading, "heading_bt:", self.heading_bt)
        if(self.G.has_edge((self.long, self.lat), curr_coords)):
            if(ultrasonics[0] < 30): #left
                self.G.edges[(self.long, self.lat), curr_coords]["blocked"] = True
            else:
                self.G.edges[(self.long, self.lat), curr_coords]["blocked"] = False
        self.heading = curr_heading
        self.long = curr_coords[0]
        self.lat = curr_coords[1]
        
            
        curr_coords = (self.long, self.lat)
        curr_heading = self.heading
        self.heading = (self.heading_bt)%4
        node_to_check = self.update_coords(self.long, self.lat)
        print("edge blocked:", curr_coords, (self.long, self.lat))
        print("curr_heading:", curr_heading, "pretend heading:", self.heading, "heading_bt:", self.heading_bt)
        if(self.G.has_edge((self.long, self.lat), curr_coords)):
            if(ultrasonics[1] < 30): #middle
                self.G.edges[(self.long, self.lat), curr_coords]["blocked"] = True
            else:
                self.G.edges[(self.long, self.lat), curr_coords]["blocked"] = False
        self.heading = curr_heading
        self.long = curr_coords[0]
        self.lat = curr_coords[1]
            
        
        curr_coords = (self.long, self.lat)
        curr_heading = self.heading
        self.heading = (self.heading_bt-1)%4
        node_to_check = self.update_coords(self.long, self.lat)
        print("edge blocked:", curr_coords, (self.long, self.lat))
        print("curr_heading:", curr_heading, "pretend heading:", self.heading, "heading_bt:", self.heading_bt)
        if(self.G.has_edge((self.long, self.lat), curr_coords)):
            if(ultrasonics[2] < 30): #right
                self.G.edges[(self.long, self.lat), curr_coords]["blocked"] = True
            else:
                self.G.edges[(self.long, self.lat), curr_coords]["blocked"] = False
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
        print(list(streets))
        if(streets[0]):
            if self.G.nodes[(self.long, self.lat+1)]["explored"]:
                explored.append(1)
            elif self.G.nodes[(self.long, self.lat+1)]["blocked"] or self.G.edges[(self.long, self.lat), (self.long, self.lat+1)]["blocked"]:
                explored.append(3)
            else:
                explored.append(0)
        else:
            explored.append(2)
        if(streets[1]):
            if self.G.nodes[(self.long-1, self.lat)]["explored"]:
                explored.append(1)
            elif self.G.nodes[(self.long-1, self.lat)]["blocked"] or self.G.edges[(self.long, self.lat), (self.long-1, self.lat)]["blocked"]:
                explored.append(3)
            else:
                explored.append(0)
        else:
            explored.append(2)
        if(streets[2]):
            if self.G.nodes[(self.long, self.lat-1)]["explored"]:
                explored.append(1)
            elif self.G.nodes[(self.long, self.lat-1)]["blocked"] or self.G.edges[(self.long, self.lat), (self.long, self.lat-1)]["blocked"]:
                explored.append(3)
            else:
                explored.append(0)
        else:
            explored.append(2)
        if(streets[3]):
            if self.G.nodes[(self.long+1, self.lat)]["explored"]:
                explored.append(1)
            elif self.G.nodes[(self.long+1, self.lat)]["blocked"] or self.G.edges[(self.long, self.lat), (self.long+1, self.lat)]["blocked"]:
                explored.append(3)
            else:
                explored.append(0)
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

    def follow(self, nodes):
        directions = []
        moved = False
        direction = (nodes[1][0] - nodes[0][0], nodes[1][1] - nodes[0][1])
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
        assert(moved)
        return directions

    def turn_7(self):
        direction = random.randint(0,3)
        curr_coords = (self.long,self.lat)
        explored = self.get_explored_nodes(curr_coords)
        print(explored)
        if(False not in explored):

            G_2 = self.get_G2()
            nodes = list(G_2.nodes())
            goto_node = None
            for node in nodes:
                if nx.has_path(G_2, curr_coords, node) and node != curr_coords:
                    goto_node = node
            if goto_node != None:
                self.goto(goto_node)
                self.intersection()
            else:
                print("Everything is explored")
        else:
            print((direction+self.heading_bt)%4)
            while(bool(explored[(direction+self.heading_bt)%4]) and (False in explored or explored[(direction+self.heading_bt)%4] == 2)):
                direction = random.randint(0,3)
                print((direction+self.heading_bt)%4)
            turn_amount = int((direction+(self.heading_bt-self.heading))%4)
            if turn_amount == 2:
                self.bm.turn_around()
            else:
                self.bm.turn(turn_amount)
            explored[(direction+self.heading_bt)%4] = True
            self.heading = (direction+self.heading_bt)%4
        return True
    
    def explore(self):
        if(len(self.G.nodes()) <3 or False in nx.get_node_attributes(self.G, "explored").values()):
            self.forward()
            ok = self.turn_7()
            return ok
        else:
            return False

    def goto(self, target):
        curr_coords = (self.long, self.lat)
        while(curr_coords != target):
            G_2 = copy.deepcopy(self.G)
            node_list_2 = list(G_2.nodes())
            for node in node_list_2:
                if G_2.nodes[node]["blocked"] == True:
                    touching_edges = list(G_2.edges([node]))
                    for edge in touching_edges:
                        G_2.remove_edge(*edge[:2])
                    G_2.remove_node(node)
            edge_list_2 = list(G_2.edges())
            for edge in edge_list_2:
                if(G_2.edges[edge]["blocked"] == True):
                    G_2.remove_edge(*edge[:2]) #could be a problem
            try:
                shortest_path = nx.shortest_path(G_2, curr_coords, target)
                to_turn = self.follow(shortest_path)
                self.update_heading(to_turn[0])
                self.heading_bt = self.heading
                self.bm.follow_route(to_turn[0])
                returned = self.bm.go_to_intersection()
                is_blocked = not returned[1]
                prev_coords = (self.long, self.lat)
                curr_coords = self.update_coords(self.long, self.lat)
                if(is_blocked):
                    self.G.nodes[curr_coords]["blocked"] = True
                    self.heading = (self.heading+2)%4
                    self.heading_bt = self.heading
                    curr_coords = prev_coords
                us_readings = returned[0]
                self.check_for_blocked_edges(us_readings)
            
            except:
                if target not in G_2:
                    goto_list = dict()
                    nodes = list(G_2.nodes())
                    for node in nodes:
                        if nx.has_path(G_2, curr_coords, node):
                            man_dis = abs(target[0] - node[0]) + abs(target[1]- node[1])
                            goto_list[node] = [man_dis, False]
                    while (self.is_a_false(goto_list) and curr_coords != target):
                        if(self.G.has_node(target) and self.G.nodes[target]["blocked"] == True):
                            print("Node is blocked!")
                            break
                        print(curr_coords)
                        min_dis = 10000
                        min_node = None
                        for node in goto_list.keys():
                            if min_dis > goto_list[node][0] and goto_list[node][1] == False:
                                min_dis = goto_list[node][0]
                                min_node = node
                        #print('here')
                        #print("Before the goto:", goto_list)
                        self.goto(min_node)
                        curr_coords = min_node
                        goto_list[min_node][1] = True
                        if not self.G.nodes[min_node]["explored"]:
                            streets = self.intersection()
                            self.G.nodes[curr_coords]['explored'] = True
                            self.G.nodes[curr_coords]["street"] = streets
                        #print('HERE')
                        #self.check_for_blocked_edges(us_readings)
                        G_2 = self.get_G2()
                        nodes = list(G_2.nodes())
                        for node in nodes:
                            if nx.has_path(G_2, curr_coords, node) and node not in goto_list.keys():
                                man_dis = abs(target[0] - node[0]) + abs(target[1]- node[1])
                                goto_list[node] = [man_dis, False]
                        #print("After the goto:", goto_list)
                    if(not self.is_a_false(goto_list)):
                        print("No avalible path")
                else:
                    print("No avalible path")

        #self.check_for_blocked_edges(us_readings)
        #return us_readings
        return True

    def get_G2(self):
        G_2 = copy.deepcopy(self.G)
        node_list_2 = list(G_2.nodes())
        for node in node_list_2:
            if G_2.nodes[node]["blocked"] == True:
                touching_edges = list(G_2.edges([node]))
                for edge in touching_edges:
                    G_2.remove_edge(*edge[:2])
                G_2.remove_node(node)
        edge_list_2 = list(G_2.edges())
        for edge in edge_list_2:
            if(G_2.edges[edge]["blocked"] == True):
                G_2.remove_edge(*edge[:2]) #could be a problem

        return G_2

    def is_a_false(self, goto_list):
        values = goto_list.values()
        for value in values:
            if value[1] == False:
                return True
        return False

        """ elif(len(self.G.nodes()) > 3 or False in nx.get_node_attributes(self.G, "explored").values()):
            while((len(self.G.nodes()) <3 or False in nx.get_node_attributes(self.G, "explored").values()) and (self.long, self.lat) != target):
                self.forward()
                self.turn_7() """
        """curr_coords = (self.long, self.lat)
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
        return True"""
    
    def print_g2(self):
        G_2 = copy.deepcopy(self.G)
        node_list_2 = list(G_2.nodes())
        for node in node_list_2:
            if G_2.nodes[node]["blocked"] == True:
                touching_edges = list(G_2.edges([node]))
                print(type(touching_edges))
                print("Touching:", touching_edges)
                for edge in touching_edges:
                    G_2.remove_edge(*edge[:2])
                G_2.remove_node(node)
        edge_list_2 = list(G_2.edges())
        for edge in edge_list_2:
            if(G_2.edges[edge]["blocked"] == True):
                G_2.remove_edge(*edge[:2]) #could be a problem
        self.print_graph(G_2)

    def print_graph(self, graph):
        node_list = list(graph.nodes())
        pos = {}
        color = []
        edge_colors = []
        print((self.long, self.lat), self.heading)
        print(list(graph.nodes.data()))
        for node in node_list:
            pos[node] = node
            if graph.nodes[node]["blocked"] == True:
                color.append("yellow")
            elif graph.nodes[node]["explored"] == False:
                color.append("red")
            else:
                color.append("green")
        edge_list = graph.edges()
        print(list(graph.edges.data()))
        for edge in edge_list:
            if graph.edges[edge]["blocked"] == True:
                edge_colors.append("yellow")
            else:
                edge_colors.append("green")
        print(edge_colors)
        
        nx.draw(graph, pos=pos, node_color = color, edge_color = edge_colors, with_labels = True)
        #nx.draw(graph, pos=pos, node_color = color, with_labels = True)
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