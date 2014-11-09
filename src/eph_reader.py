#!/usr/bin/python

from angles import RA_angle, Dec_angle, Deg10
import time
import json
def format_time(raw_ut, raw_date):
	
	parsed = {
		'ss' : int(ut[-2:]),
		'mm' : int(ut[-4:-2]),
		'hh' : int(ut[:-4]),
	
		'year' 	: int(raw_date[0]),
		'month' 	: int(raw_date[1]),
		'day' 	: int(raw_date[2]),
		}
	
	
	
	
	t = time.strptime("{year} {month:02d} {day:02d} {hh:02d} {mm:02d} {ss:02d}".format(**parsed), "%Y %m %d %H %M %S")
	
	return time.mktime(t)-7*3600
data = []
with open("ephemeris_2015GA1.csv") as fp:
	for line in fp:
		if line[:4] == "2015":
			
			vals = line[:-2].split(',')

			date = vals[:3]
			ut = vals[3]
			ra = "{0}:{1}:{2}".format(*vals[4:7] )
			dec = "+{0}:{1}:{2}".format(*vals[7:10])
			offra = vals[10]
			offdec = vals[11]
			
			
			unix_epoch_time = format_time(ut, date)
			data.append({
				"time"			:	unix_epoch_time,
				"offra"			: 	offra,
				"offdec"			:	offdec,
				"pretty_time"	:	time.ctime(unix_epoch_time),
				"ra"				:	ra,
				"dec"				:	dec
				
			})
			

print json.dumps(data, indent=2)			
