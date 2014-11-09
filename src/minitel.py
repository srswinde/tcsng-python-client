#!/bin/python


import socket
#from angles import Angle, RA_angle, Dec_angle, Deg10, Hour_angle
import time
#from locales import tucson; T=tucson()
from exceptions import Exception
from threading import Lock, RLock


DEBUG=False

AXES = {"RA":0, "Dec": 1, "ra":0, "dec":1, "DEC":1}
telTalk = RLock()


davesPreset = {'QCLIP':0,
					'VMAX':1000000,
					'AMAX':10000,
					'JMAX':10000,
					'GN':0,
					'DMAX':0,
					'PERMAX':10000,
					'GQ':0,
					'OFFSET':0,
					'GF':0, #GP in ng
					'GDC':20,
					'VSLOPE':0,
					'VERMIN':0,#VERMIN
					'GDIFF':0,#KD
					'DSAM':0,
					'GR':8,#GR
					'GVFF':1024
							}

class telescope:
	
	
	#All methods that bind to a tcsng server request
	#will begin with req and all methods that bind to 
	#a tcsng server command will begin with com
	#After the first three letters "req" or "com" if 
	#the method name is in all caps then it is a letter 
	#for letter (underscore = whitespace)copy of the 
	#tcsng command or request
	
	def __init__(self, hostname, telid="TCSNG"):
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
		
		with self.comLock:
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
		
	
	
	def reqPECSTAT( self ):
		raw = self.request('PECSTAT')
		rawList = rawList = [ii for ii in raw.split(" ") if ii != '']
		condMap = ["OFF", "ON", "TRAINING", "WAITING" ] 
		modeMap = ["OFF", "ON", "TRAINING"]
		status = {
			"condition"	: 	condMap[int( rawList[0] ) ]	,
			"count"		:	rawList[1]  ,
			"index"		:	rawList[2]  ,
			"mode"		:	modeMap[ int( rawList[3] ) ]
		}
		
		return status
	
	def reqPECPROG( self ):
		raw = self.request('PECPROG')
		rawList = rawList = [ii for ii in raw.split(" ") if ii != '']
	
		prog = {
			"progress"	:	rawList[0],
			"correction":	rawList[1]

			}
		return prog
	
	def comPEC( self, arg ):
		out = ""
		if arg == "ON":
			out = self.command("PEC ON")
		elif arg == "OFF":
			out = self.command("PEC OFF")
		elif arg == "TRAIN":
			out = self.command("PEC TRAIN")
		else:
			out = self.command("PEC OFF")	
			
		return out
		
	
	def comPECtrain( self ):
		out = self.command("PEC TRAIN")
			
	def comPRECES( self, state="" ):
		"""Preccession state='on' turns
		it on anything else turns it off."""
		return self.command("PRECES {0}".format(state))
		

	
	def comBIAS( self, state="" ):
		"""Bias corrections, state='on' turns it on
		everything else turns it off"""
		self.command("BIAS {0}".format( state ))
		
	
	
	
	
	def comBIASRA( self, biasRA ):
		comString = "BIASRA %i" %biasRA
		return self.command( comString )
	
	def comBIASDEC( self, biasDec ):
		comString = "BIASDEC %i" %biasDec
		return self.command( comString )
	
	def comBIAS_ON( self ):
		return self.command( "BIAS ON" )
		
	def comDISABLE( self ):
		return self.command( "DISABLE" )
		
	def comENABLE( self ):
		return self.command("ENABLE")
	
	def comCANCEL( self ):
		return self.command( "CANCEL" )
	
	
	
	
	
	def reqDISABLE( self ):
		raw = self.request("DISABLE")
		lessRaw = int( raw.strip() )
		return bool( lessRaw )
	
	

	def reqSERVO( self, axis ):
		if (type(axis) == str):axis=AXES[axis]
		servoMapList = [	
							'QCLIP',#ICLIP
							'VMAX',
							'AMAX',
							'JMAX',
							'GN', #GPI
							'DMAX',
							'PERMAX',
							'GQ', #GI
							'OFFSET',
							'GF', # Type 1 servo loop gain GP
							'GDC', # DC GAIN
							'VSLOPE',
							'VERMIN', #VERMAX
							'GDIFF',
							'DSAM',
							'GR', #GROOT
							'GVFF']
							
		rawServoString = self.request("SERVO %i" %axis)
		rawServoList = rawServoString.split(' ')
		servoList = [long( ii ) for ii in rawServoList if ii != '' ]
		
		return dict( zip( servoMapList, servoList ) )
	
	
	
	def comMOVNEXT( self ):
		return self.command( "MOVNEXT" )
	
	def comSTEPRA( self, asecs ):
		comstr = "STEPRA {0}".format(asecs)
		return self.command( comstr )
		
	def comSTEPDEC( self, asecs ):
		comstr = "STEPDEC {0}".format(asecs)
		return self.command( comstr )
		
	def comSERVO( self, axis, servoDict ):
		rawComString = "SERVO {AX} {QCLIP} {VMAX} {AMAX} {JMAX} {GN} {DMAX} {PERMAX} {GQ} {OFFSET} {GF} {GDC} {VSLOPE} {VERMIN} {GDIFF} {DSAM} {GR} {GVFF}"
		
		comString = rawComString.format(AX=axis, **servoDict)
		
		self.command( comString )

	def comSAMSTART( self, axis, sampleValue, interval, size, rate ):
	
		"""This is the binding to the SAMSTART tcsng command
		the sampleValue is the type of data to be collected size
		is the total numbe of samples desired and interval is the
		how often you want the samples"""
		AXES = {"ra":0, "RA":0, "DEC":1, "Dec":1, "dec":1}
		if ( type(axis) == str ):	axis = AXES[axis]
		
		
		
		outstr = "SAMSTART {0} {1} {2} {3} {4}".format( axis, sampleValue, size, interval, rate )
		print outstr
		return self.command(outstr)
		#return self.command(outstr)
	
	def comSAMPLE( self, axis, interval, size ):
			outstr = "SAMPLE {0} {1} {2}".format( axis, interval, size )
			return self.command( outstr )
	
	def comDUMPSAM( self, axis ):
		if type(axis) == str: axis = AXES[axis]
		return self.command("DUMPSAM %i" %axis)
	
	def reqSAMDONE( self ):
		if int( self.request( "SAMDONE" ) ) == 0:
			return False
		else:
			return True
				
	def reqSAMDATA( self, start, stop):	
		"""THis is the binding to the SAMDATA command in tcsng
		The sampleValue is the variable you want to sample the start and
		stop indexes are the start has to be greater than the stop and neither
		value can be less than zero or greater than 1000"""
		
		
		data = self.request("SAMDATA %i %i" %( start, stop ) )
		return data
		
	def reqSAMDATAall( self ):
		data = []
		for a in range( 33 ):
			rawData = self.reqSAMDATA( 30*a, 30*(a+1) )
			rawData = rawData.split(' ')
			data.extend( [long( ii ) for ii in rawData if ii != '' ] )
			
		return data
	
	def reqSAMDATAsome( self, howMany ):
		data = []
		cnt = 0
		maxCnt = 30
		if howMany < 30: howMany=30
		
		while cnt < howMany-30:
			rawData = self.reqSAMDATA( cnt, cnt+maxCnt )
			rawData = rawData.split(' ')
			data.extend( [long( ii ) for ii in rawData if ii != '' ] )
			cnt+=30
			
		rawData = self.reqSAMDATA( cnt, howMany )	
		rawData = rawData.split(' ')
		data.extend( [long( ii ) for ii in rawData if ii != '' ] )
		return data
		
		#data.extend( [long( ii ) for ii in rawData if ii != '' ] )
		#return data
	
		
	
	def comSAMABORT( self ):
		return self.command("SAMABORT")

	def reqXRA(self):
		"""Binding for tcsng xra request"""
		#[COM] [NEXT] [REF] [OFF] [WOB] [DIFF] [BIAS] [GUIDE] [DRIFT]
		listMap = ["commanded",
						"next",
						"reference",
						"off",
						"wobble",
						"diff",
						"bias",
						"guide",
						"drift"]
	
		raw = self.request("XRA")
		valList = [ii for ii in raw.split() if ii != '']#remove white spaces and convert to list
		
		xra = dict( zip( listMap, valList ) )
		
		return xra
		
	def reqXDEC( self ):
		"""Binding for tcsng xra request"""
		#[COM] [NEXT] [REF] [OFF] [WOB] [DIFF] [BIAS] [GUIDE] [DRIFT]
		listMap = ["commanded",
						"next",
						"reference",
						"off",
						"wobble",
						"diff",
						"bias",
						"guide",
						"drift"]
	
		raw = self.request( "XDEC" )
		valList = [ii for ii in raw.split() if ii != '']#remove white spaces and convert to list
		
		xdec = dict( zip( listMap, valList ) )
		xdec["current"] = self.reqDEC()
		return xdec
		 
class telComError( Exception ):
	def __init__( self, message ):
		Exception.__init__( self, message)
		
		
class jt( telescope ):
	def __init__( self ):
		telescope.__init__( self, "jefftest5" )
		
if __name__ == '__main__':
	t=telescope("10.130.133.12", "MOCK")
	print t.reqALL()


	

	
	
