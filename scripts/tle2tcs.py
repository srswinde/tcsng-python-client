#!/bin/python3
from telescope import kuiper
import sys
import time

usage = """Send TLE data from a file to TCSng.
        usage: python tle2tcs.py <filename>
        like:  python tle2tcs.py  iss.tle
"""

if len( sys.argv ) != 2:
    print(usage)
    sys.exit(1)


with open(sys.argv[1]) as tlefd:
    tle = tlefd.read()

outtle = []
test_list = tle.split('\n')
if len(test_list) == 2:
    outtle.append(test_list[0])
    outtle.append(test_list[1])
else:
    outtle.append(test_list[1])
    outtle.append(test_list[2])



tel=kuiper()
tel.comTLE(test_list)
for a in range(10):
    print("Satellite Horizontal Coordinates: {} {}" .format(*tle.reqGETSATELAZ()) )
    time.sleep(1.0)



