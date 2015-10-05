import socket

class telescope:
	
	
	#All methods that bind to a tcsng server request
	#will begin with req and all methods that bind to 
	#a tcsng server command will begin with com
	#After the first three letters "req" or "com" if 
	#the method name is in all caps then it is a letter 
	#for letter (underscore = whitespace)copy of the 
	#tcsng command or request
	
	def __init__(self, hostname, telid, port ):
		try:
			self.ipaddr = socket.gethostbyname(hostname)
			self.hostname = hostname
			self.telid=telid
		except socket.error:
			raise telComError("Cannot Find Telescope Host {0}.".format(hostname) )
		
		self.comLock = Lock()
		#Make sure we can talk to this telescope
		if not self.request( 'EL' ):
			raise socket.error
			
		
	def request( self, reqstr, timeout=0.1, retry=True):
				
		"""This is the main TCSng request method all 
		server requests must come through here."""
		

		HOST = socket.gethostbyname(self.hostname)
		PORT= 5750
		s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.settimeout( timeout )
		try:
			s.connect((HOST, PORT))
			s.send("%s TCS 1 REQUEST %s" %(self.telid, reqstr.upper()) )
			recvstr = s.recv(4096)
			s.close()
			if DEBUG:
				print "%s TCS 1 REQUEST %s" %(self.telid, reqstr.upper())
			return recvstr[len(self.telid)+6:-1]
		except socket.error:
			msg = "Cannot communicate with telescope {0}".format(self.hostname)
			raise telComError(msg)
			time.sleep(1.0)
		
	def command( self, reqstr, timeout=0.5 ):
		"""This is the main TCSng command method. All TCS
			server commands must come through here."""
	
		HOST = socket.gethostbyname(self.hostname)
		PORT= 5750
		s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((HOST, PORT))
		s.send("%s TCS 123 COMMAND %s" %( self.telid, reqstr.upper() ) )
		recvstr = s.recv( 4096 ) 
		s.settimeout( timeout )
		s.close()
		if DEBUG:
			print "%s TCS 123 COMMAND %s" %( self.telid, reqstr.upper() )
		return recvstr
		
		
		
	def reqALL( self ):
		"""returns dictions of "ALL" request i.e.
			[MOT] [RA] [DEC] [HA] [LST] [ALT] [AZ] [SECZ] [Epoch]"""
		allDict = {}
		names = ["motion", "ra", "dec", "ha", "lst", "alt", "az", "secz", "epoch"]
		rawStr = self.request("ALL")
		rawList = [ii for ii in rawStr.split(" ") if ii != '']
		
		
	def reqXALL( self ):
		"""returns dictions of "XALL" request i.e.
			[FOC] [DOME] [IIS] [PA] [UTD] [JD]"""
		xallDict = {}
		names = ["focus", "dome", "iis", "pa", "utd", "jd"]
		rawStr = self.request("XALL")
		rawList = [ii for ii in rawStr.split(" ") if ii != '']
		
		for num in range( len( rawList ) ):
			xallDict[names[num]] = rawList[num]

		return xallDict
		
	def azcam_all( self ):
		azcamall = {}
		
		vals = ['ha', 'iis', 'utd', 'ut', 'focus', 'epoch', 'motion', 'lst', 'pa', 'ra', 'jd', 'alt', 'az', 'dec', 'dome', 'secz']
		azcamall.update( reqALL() )
		azcamall.update( reqXALL() )
		for key in vals:
			if key not in azcamall.keys():
				print key
		
		
		
		
		
		
		
		
		
		
