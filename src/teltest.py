#!/usr/bin/python


from telescope_beta import telescope
from threading import *
tel = telescope("10.130.133.12", "MOCK")
global prob
prob = False

def thread1():
	global prob
	try:
		for a in range(1000):
			print tel.reqRA()
			if prob: 
				print "PROBLEM"
				return
	except Exception as e:
		
		prob = True
		print "PROBLEM 1", type(e), e.args
	
def thread2():
	global prob
	try:
		for a in range(1000):
			print tel.reqDEC()
			if prob: 
				print "PROBLEM"
				return
	except(Exception):
		
		prob = True
		print "PROBLEM 2"
		
def thread3():
	global prob
	try:
		for a in range(1000):
			print tel.reqXDEC()
			if prob: 
				print "PROBLEM"
				return
	except(Exception):
		
		prob = True
		print "PROBLEM 3"

def thread4():
	global prob
	try:
		for a in range(1000):
			print tel.reqXRA()
			if prob: 
				print "PROBLEM"
				return
	except(Exception):
		
		prob = True
		print "PROBLEM 4"
		
def thread5():
	
	try:
		for a in range(1000):
			print tel.reqXALL()
			if prob: 
				print "PROBLEM"
				return
	except(Exception):
		
		prob = True
		print "PROBLEM 5"
		
def main():
	
	task1 = Thread(target=thread1)
	task2 = Thread(target=thread2)
	task3 = Thread(target=thread3)
	task4 = Thread(target=thread4)
	task5 = Thread(target=thread5)
	
	
	task1.start()
	task2.start()
	task3.start()
	task4.start()
	task5.start()
	
	
	
main()
