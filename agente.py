#!/usr/bin/env python
# encoding: utf8
# Artificial Intelligence, UBI 2018-19
# Modified by:Carlos Esteves nº 37491

import rospy
import numpy as np
import networkx as nx
from std_msgs.msg import String
from nav_msgs.msg import Odometry

x_ant = 0
y_ant = 0
obj_ant = ''
obj_count = []
objs = []
roomsobjs = [[] for _ in range(11)]
totobj = np.zeros((11,), dtype = int)
o_room = np.zeros((11,), dtype = int)
room = 0
room_ant = 0
met_mary = 0
mary_room = 0
G = nx.Graph()
G.add_node(1)


# ---------------------------------------------------------------
# odometry callback
def callback(data):
	global x_ant, y_ant,room,room_ant,objs,G
	x=data.pose.pose.position.x
	y=data.pose.pose.position.y
	# show coordinates only when they change
	if x != x_ant or y != y_ant:
		print " x=%.1f y=%.1f" % (x,y)
	x_ant = x
	y_ant = y
	
	# verifica se o quarto mudou
	room1 = room
	room_check()
	if(room1 != room):
		G.add_node(room)# adiciona o quarto ao grafp
		G.add_edge(room,room1)# liga dois quartos, arestas
		print "Welcome to room number %d" % room
		objs = []
		room_ant = room1

# ---------------------------------------------------------------
# object_recognition callback
def callback1(data):
	global obj_ant
	global obj_count,room,objs,roomsobjs,met_mary,totobj,mary_room,o_room
	obj = data.data
	
	room_check()
	if obj != obj_ant and data.data != "":
		print "object is %s" % data.data
		data.data = data.data.split(",")
		
		for x in range(len(data.data)):
			
			# Question2
			if(((data.data)[x]) not in objs):
				objs.append(data.data[x])
			
			# Question 1
			if(((data.data)[x]).split("_")[0] not in obj_count and ((data.data)[x]).split("_")[0] != 'person'):
				obj_count.append(((data.data)[x]).split("_")[0])
				
			# Question 9
			if(((data.data)[x]).split("_")[0] == 'person'):
				o_room[room-1] = 1
			
			# Question 7
			if(((data.data)[x]).split("_")[1] == 'mary'):
				met_mary = 1
				mary_room = room
		
				
		# Adiciona o objs ao array de quartos roomobjs	
		if objs[0] != None and objs[0] != '':
			if totobj[room-1] != 0: # se a posição do quarto não estiver a 0 faz append 
				for y in range(len(objs)):
					if(objs[y] not in roomsobjs[room-1]):
						roomsobjs[room-1].append(objs[y])
						totobj[room-1] += 1
			# Se a posição do quarto estiver a 0 faz insert
			else:
				roomsobjs.insert(room-1,objs)
				totobj[room-1] = totobj[room-1] + len(objs)
				objs =[]
	
	obj_ant = obj
		
# ---------------------------------------------------------------
# questions_keyboard callback
def callback2(data):
	global obj_count,roomsobjs,room_ant,room,met_mary,mary_room,o_room,G
	print "question is %s" % data.data
	
	if(data.data == '1'):
		print "I have recognized %d type(s) of object(s)" % len(obj_count)
	
	if(data.data == '2'):
		
		objs_aux = roomsobjs[room_ant - 1]
		print "In the room i was before there were the following objects:"
		
		for x in range(len(objs_aux)):
			print objs_aux[x]
	
	if(data.data == '6'):
		if(room == 1):
			print "I already am at the start room"
		else:
			paths = nx.all_simple_paths(G,room,1,None)
			print "I can take %d different path(s)" % len(list(paths))
		
			
	
	if(data.data == '7'):
		if(met_mary == 0):
			print "I haven't met Mary"
		else:
			Mary()
	
	if(data.data == '9'):
		for x in range(11):
			if o_room[x] == 1:
				print "Room %d is occupied" % (x+1)
				
# ---------------------------------------------------------------
def agent():
	
	rospy.init_node('agente')

	rospy.Subscriber("questions_keyboard", String, callback2)
	rospy.Subscriber("object_recognition", String, callback1)
	rospy.Subscriber("odom", Odometry, callback)

	rospy.spin()

# ---------------------------------------------------------------
# Verifica em que quarto está através das coordenadas
def room_check():
	global room,x_ant,y_ant
	
	if y_ant <= 1.5 and x_ant >= -1:
		room = 1
	if y_ant <= 6.5 and y_ant > 1.5 and x_ant >= -1:
		room = 2
	if y_ant > 6.5 and x_ant >= -1:
		room = 3
	if y_ant <= 1.5 and x_ant >=-6 and x_ant < -1:
		room = 4
	if y_ant > 1.5 and x_ant >=-6 and x_ant < -1:
		room = 5
	if y_ant <= 1.5 and x_ant >= -11 and x_ant < -6:
		room = 6
	if y_ant <= 6.5 and y_ant > 1.5 and x_ant >=-11 and x_ant < -6:
		room = 7
	if y_ant > 6.5 and x_ant >=-11 and x_ant < -6:
		room = 8
	if x_ant < -11 and y_ant <= 1.5:
		room = 9
	if x_ant < -11 and y_ant > 1.5 and y_ant<=6.5:
		room = 10
	if x_ant < -11 and y_ant > 6.5:
		room = 11
# ---------------------------------------------------------------
def Mary():
	
	global mary_room,roomsobjs
	
	objects = roomsobjs[mary_room-1]
	chair = 0 
	table = 0
	computer = 0
	book = 0
	

	for x in range(len(objects)):
		
		#print objects[x].split('_')[0]
		
		if(objects[x].split('_')[0] == 'table'):
			table = table + 1
		if(objects[x].split('_')[0] == 'chair'):
			chair = chair + 1
		if(objects[x].split('_')[0] == 'book'):
			book = book + 1	
		if(objects[x].split('_')[0] == 'computer'):
			computer = computer + 1
			
	room_type = 'generic room'		
	
	#waiting room		
	if(chair >= 1 and table == 0 and book == 0 and computer == 0):
		room_type = 'waiting room'
		
	# study room
	if(chair > 0 and table > 0 and book > 0 and computer == 0):
		room_type = 'study room'
	
	# computer lab
	if(chair > 0 and table > 0 and computer > 0):
		room_type =' computer lab'
	
	#meeting room
	if(chair > 0 and table == 1 and book == 0 and computer == 0):
		room_type = 'meeting room'
	
	
	print "Mary is in a %s" % room_type
	chair = 0 
	table = 0
	computer = 0
	
# ---------------------------------------------------------------
if __name__ == '__main__':
	agent()
