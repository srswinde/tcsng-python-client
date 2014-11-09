#!/usr/bin/python


from scottSock import scottSock
import re
from HTMLParser import HTMLParser
import time
import json
import sys
from vatt import vatt; vatttel = vatt()


class MyHTMLParser(HTMLParser):
	def __init__(self):
		HTMLParser.__init__(self)
		self.ephs_list = []
		
		

	def handle_data(self, data):
		#if data.lstrip().startswith("2015"):
		dlist = data.split('\n')
		for d in dlist:
			if d.startswith("2015") and d.endswith("/ "):
				
				vals = [val for val in d.split(" ") if val != ""]

				ut = vals[3]
				date = vals[:3]

				unix_time_epoch = self.format_time(ut, date)
				self.ephs_list.append(
				{
					"time"		:	unix_time_epoch,
					"ctime"		:	time.ctime(unix_time_epoch),
					"biasra"		:	float(vals[15]),
					"biasdec"	:	float(vals[16]),
					"mag"			:	vals[14],
					"ra"			:	"{0}:{1}:{2}".format(*vals[4:7]),
					"dec"			:	"{0}:{1}:{2}".format(*vals[7:10])
					
				})

	def mapvals( self, vals ):
		pass
		
		
	def format_time(self,raw_ut, raw_date):
	
		parsed = {
		'ss' : int(raw_ut[-2:]),
		'mm' : int(raw_ut[-4:-2]),
		'hh' : int(raw_ut[:-4]),
	
		'year' 	: int(raw_date[0]),
		'month' 	: int(raw_date[1]),
		'day' 	: int(raw_date[2]),
		}
		
		t = time.strptime("{year} {month:02d} {day:02d} {hh:02d} {mm:02d} {ss:02d}".format(**parsed), "%Y %m %d %H %M %S")
	
		return time.mktime(t)-7*3600

def getCurrentRate(rates):
	now = time.time()+30#30 seconds in the future
	for ii in range(len(rates)):
		
		if ii+1 <= len(rates)-1:
			t1 = rates[ii]['time']
			t2 = rates[ii+1]['time']
			#print time.ctime(t1), time.ctime(now), time.ctime(t2)
			if t1 < now and now < t2:
				return rates[ii]

	return False
		
def getRates(obj):
	mpc_url = "www.minorplanetcenter.net"


	with open("mpc_http4.dat") as fp: outdata=fp.read()


	conn = scottSock(mpc_url, 80)

	html_data = conn.converse( outdata.format(NAME=obj.replace(" ","+"), COUNT=150 ) )
	parser = MyHTMLParser()



	parser.feed(html_data)
	

	
	return parser.ephs_list
	
	

def main(obj):
	
	
	print "Getting ephemeris from MPC for ", obj
	rates = getRates(obj)
	
	print "We have the ephemeris. Saving to file"
	with open("{0}.json".format(obj), 'w') as fp: fp.write(json.dumps(rates, indent=4, sort_keys=True)) 
	print "Saved as", "{0}.json".format(obj)
	
	print "Press enter when you want to load them in the telescope"
	
	raw_input()
	test = True
	
	while test:
		
		rate = getCurrentRate(rates)
		
		print "Current Ephemeris from MPC for ", obj, "is:"
		print json.dumps(rate, indent=4, sort_keys=True)
		vatttel.comSETBIAS(rate["biasra"], rate["biasdec"])
		time.sleep(60)
		
main(sys.argv[1])
	
	
	
	
	
	

