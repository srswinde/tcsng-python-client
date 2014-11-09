#!/usr/bin/python

import json
import time
from vatt import vatt; vatttel = vatt()
from threading import Timer

with open("bias.json") as fp2json: rates = json.load(fp2json)
	
	
	
def getRate():
	now = time.time()
	for ii in range(len(rates)):
		
		if ii+1 <= len(rates)-1:
			t1 = rates[ii]['time']
			t2 = rates[ii+1]['time']
			#print time.ctime(t1), time.ctime(now), time.ctime(t2)
			if t1 < now and now < t2:
				return float( rates[ii]['offra'] ), float( rates[ii]['offdec'])
	
	return (False, False)	
			

def main():
	test = True
	while test:	
		offra, offdec = getRate()
		if offra == False:
			test=False
		else:
			print "Current rate", offra, offde
			print vatttel.comSETBIAS(offra, offdec)
		
		time.sleep(2.5*60)
		
main()
