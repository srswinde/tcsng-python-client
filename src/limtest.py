#!/usr/bin/python


from telescope_beta import telescope
from threading import *
from angles import Angle, Hour_angle, Dec_angle, Deg10
tel = telescope("10.130.133.12", "MOCK")


for hour in range( -6,6,1 ):
	ra = tel.reqRA() + Hour_angle([hour,0,0])
	for decint in range(-90,0, 5 ):
		dec = Dec_angle( Deg10( decint ) )
		print ra.Format('hours'), dec, tel.reqVERIFY(ra, dec)
		
