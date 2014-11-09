#!/bin/python


import socket
import time
from exceptions import Exception
from threading import Lock, RLock
DEBUG = False

class ngDevice:
	
	
	#All methods that bind to a tcsng server request
	#will begin with req and all methods that bind to 
	#a tcsng server command will begin with com
	#After the first three letters "req" or "com" if 
	#the method name is in all caps then it is a letter 
	#for letter (underscore = whitespace)copy of the 
	#tcsng command or request
	
	def __init__(self, hostname, port, obsid, sysid):
		try:
			self.ipaddr = socket.gethostbyname(hostname)
			self.hostname = hostname
			
			
			
		except socket.error:
			raise telComError("Cannot Find Telescope Host {0}.".format(hostname) )
		
		self.port = port
		self.info = {
				"OBSID"	: obsid	,
				"SYSID"	: sysid	,
			}
			
		self.comLock = Lock()

			
		
	def request( self, reqStr, timeout=.25, refNum=123, retry=True ):
				
		"""This is the main TCSng request method all
		server requests must come through here."""
		outString = "{OBSID} {SYSID} {REFNUM} REQUEST {REQSTR}\n".format(REFNUM=refNum, REQSTR=reqStr, **self.info)
		
		with self.comLock:
			HOST = socket.gethostbyname(self.hostname)
			PORT= 5750
			s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.settimeout( timeout )
			try:
				s.connect((self.ipaddr, self.port))
				s.send( outString )
				recvstr = s.recv(4096)
				s.close()
				
				if DEBUG:
					print outString
				return recvstr
				
			except socket.error:
				msg = "Cannot communicate with telescope {0}".format(self.hostname)
				raise Exception(msg)
				time.sleep(1.0)
		
	def command( self, comStr, timeout=0.25, refNum=123 ):
		"""This is the main TCSng command method. All TCS
			server commands must come through here."""
	
		outString = "{OBSID} {SYSID} {REFNUM} COMMAND {COMSTR}\n".format( REFNUM=refNum, COMSTR=comStr, **self.info )

		s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.settimeout( timeout )
		s.connect((self.ipaddr, self.port))
		s.send( outString )
		test = True
		recvstr = ""
		while True:
			data = s.recv(1024)
			if not data: break
			recvstr+=data
		s.close()
		if DEBUG:
			print outString
		return recvstr
		



class flatfield( ngDevice ):
	def __init__( self, hostname, port ):
		ngDevice.__init__( self, hostname, port, obsid="VATT", sysid="FLAT")
	
	def comSETCOLOR( self, color, intensity, refNum=123 ):
		reqStr = "SETCOLOR {0} {1}".format(color, intensity)
		return self.command( reqStr, refNum=refNum )
	
	def comBURN( self, color, intensity, refNum=123 ):
		reqStr = "BURN {0} {1}".format( color, intensity )
		

	
if __name__ == "__main__":
	f=flatfield( "jefftest3", 8080 )
	while 1:
		for a in range(100):
			print a, [f.comSETCOLOR( "AMBER", a )]

		
		for a in range(100, -1, -1):
			print a, [f.comSETCOLOR( "AMBER", a )]

	
	
	
	
