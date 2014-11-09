#!/bin/python


import socket
from astro.angles import Angle, RA_angle, Dec_angle, Deg10, Hour_angle
import time
from astro.locales import tucson; T=tucson()
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
		
	def string2RAAngle( self, rawAngle ):
		"""This method is used if there is no
			character to seperate the hours minutes
			and seconds in the string ie 084000.0
			instead of 08:40:00.0 the later format 
			can be handled directly by RA_angle class"""
			
		rawAngle = rawAngle.strip()
		HH = int( rawAngle[0:2] )
		MM = int( rawAngle[2:4] )
		SS = float( rawAngle[4:] )
		return RA_angle( [HH, MM, SS] )
	
	def string2DecAngle( self, rawAngle ):
		"""This method is used if there is no
			character to seperate the Degrees arcminutes
			and arcseconds in the string ie +320000.0
			instead of +32:00:00.0 the latter format 
			can be handled directly by Dec_angle class"""
			
		rawAngle = rawAngle.strip()
		Deg = int( rawAngle[0:3] )
		arcmin = int( rawAngle[3:5] )
		arcsec = float( rawAngle[5:] )
	
		return Dec_angle([Deg, arcmin, arcsec])
	
	def reqFOCUS( self ):
		return self.request( "FOCUS" )
		
	def reqFOCSPEED( self ):
		return self.request( "FOCSPEED" )
	
	def reqEL(self):
		rawEl = self.request("EL")
		return Deg10(float(rawEl))
		
	def reqAZ(self):
		rawAz = self.request( "AZ" )
		return Deg10( float( rawAz ) )
	
	def reqRA(self):
		"""Binding for tcsng request RA"""
		raw = self.request("RA")
		return self.string2RAAngle(raw)
	
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
		
	def reqDOME( self ):
		"""[DEL] [MOD] [INIT] [TELAZ] [AZ] [HOME]"""
		names = ["delta", "mode", "init", "telaz", "az", "home"]
		domeDict = {}
		rawStr = self.request("DOME")
		rawList = [ii for ii in rawStr.split(" ") if ii != '']
        
		for num in range( len( rawList ) ):
			domeDict[names[num]] = rawList[num]

		return domeDict

	def reqDomeAz( self ):
		return self.reqDOME()['az']

	def reqALL( self ):
		"""returns dictions of "ALL" request i.e.
			[MOT] [RA] [DEC] [HA] [UT] [ALT] [AZ] [SECZ] [Epoch]"""
		allDict = {}
		names = ["motion", "ra", "dec", "ha", "ut", "alt", "az", "secz", "epoch"]
		rawStr = self.request("ALL")
		rawList = [ii for ii in rawStr.split(" ") if ii != '']
		
		for num in range( len(rawList) ):
			allDict[names[num]] = rawList[num]
			
		return allDict
	
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
		xra["current"] = str(self.reqRA())
		return xra
			
	def reqDEC( self ):
		"""Binding for tcsng request DEC"""
		raw = self.request( "DEC" )
		return self.string2DecAngle( raw )
		
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
		xdec["current"] = str(self.reqDEC())
		return xdec
	
	def reqMOTION( self ):
		bits = int(self.request('MOTION').split(' ')[-2])
		motion = {'ra':bool(bits&2**0), 'dec':bool(bits&2**1), 'focus':bool(bits&2**2), 'dome':bool(bits&2**3)}
		return motion
	
	def reqST( self ):
		raw = self.request('ST').split(' ')[-2]
		return RA_angle(raw)
	
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
		
	def comPROPMO( self, state="" ):
		"""Proper Motions state='ON' turns
		it on anything else turns it off."""
		return self.command("PROPMO {0}".format( state ) )
		
	def comTRACK( self, state="" ):
		"""Tracking state='ON' turns it on
		anything else turns it off"""
		self.command( "TRACK {0}".format( state ) )
		
	def comREFRAC( self, state="" ):
		"""Refraction state='on' turns it on
		anything else turns it off."""
		self.command( "REFRAC {0}".format(state) )
		
	
	
	
	def comNUTAT( self, state="" ):
		"""Nutation correction, state ='on' 
		turns it on anything else turns it off"""
		self.command( "NUTAT {0}".format( state ) )
	
	def comFLEX( self, state="" ):
		"""Flexure corrections, state='on'
		turns it on everything else turns it off"""
		self.command( "FLEX {0}".format(state) )
	def comABERRATE( self, state="" ):
		"""Abberation corrections, state='on' turns
		it on everything else turns it off"""
		self.command( "ABERRATE {0}".format( state ) )
	
	def comPARALLAX( self, state="" ):
		"""Parrallax corrections, state='ON' turns it on
		everything else turns it off"""
		self.command( "PARALLAX {0}".format( state ) )
	
	def comBIAS( self, state="" ):
		"""Bias corrections, state='on' turns it on
		everything else turns it off"""
		self.command("BIAS {0}".format( state ))
		
	def reqCORRECTIONS( self ):
		
		"""MPNARFp+tob
		M=Proper Motion
		P=Precession
		N=Nutation
		A=Aberration
		R=Refraction
		F=Flexure
		p=Parallax
		+=pointing model used...  can change to a,b,c,d?
		t=Sidereal
		o=Object
		b=Bias	"""
		corr = ["Proper_Motion", "Precession", "Nutation", "Aberration", "Refraction", "Flexure", "Parallax", "Model", "Tracking", "Object", "Bias" ]
		corrDict = {}
		corrStr = self.request("CORRECTIONS").strip()
		
		index=0
		for char in corrStr:
			
			if char != "_":
				corrDict[corr[index]] = True
			else:
				
				corrDict[corr[index]] = False
			
			index+=1
				
		corrDict["Model"] = corrStr[7]
		
		return corrDict
	
	def comFOCUP( self ):
		"""Focus paddle up"""
		return self.command("FOCUP")
	
	def comFOCDN( self ):
		"""Focus Paddle Down"""
		return self.command( "FOCDN" )
		
	def comFOCSTOP( self ):
		"""Focus Paddle Stop"""
		self.command( "FOCSTOP" )
	
	def comFOCSPEED( self, speed=""):
		"""Sets focus speed to fast or slow
		if speed=FAST speed will be fast 
		any other value speed will be slow"""
		self.command("FOCSPEED {0}".format(speed))
		
	
	def comPAD( self, DIR, rate ):
		"""Telescope Paddle command"""
		return self.command("PAD {0} {1}".format(DIR, rate))
	
	def comPADDLE( self, state="" ):
		"""Paddle enable/disable"""
		return self.command("PADDLE {0}".format(state) )
	
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
	
	def comELAZ( self, el, az ):
		return self.command("ELAZ {el}, az".format(el.deg10, az.deg10))
	
	
	
	def reqDISABLE( self ):
		raw = self.request("DISABLE")
		lessRaw = int( raw.strip() )
		return bool( lessRaw )
	
	def reqVERIFY( self, ra, dec ):
		outStr = "VERIFY {ra} {dec}".format( ra=ra.Format("hours"), dec=dec.Format( "degarc180" ) )
		
		return  int( self.request( outStr )  ) 

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
							'GF', # Type 1 servo loop gain
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
	
	def comMOVSTOW( self ):
		return self.command("MOVSTOW")
	
	def comDECLARE( self, next_or_com):
		comstr = "DECLARE {ARG}".format( ARG=next_or_com )
		return self.command( comstr )
	
	def comInitNext( self ):
		return self.comDECLARE( "INITNEXT" )
		
	def comInitCom( self ):
		return self.comDECLARE( "INITCOM" )
	
	def comNEXTPOS( self, ra, dec, epoch, rapm, decpm ):
		comstr = "NEXTPOS {ra} {dec} {epoch} {rapm} {decpm}".format(ra=ra.Format("hours"), dec=dec.Format("degarc180"), epoch=float( epoch ), decpm=float( decpm ), rapm=float( rapm ))
		return self.command( comstr )
	
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

	def comDomeAutoOn( self ):
		return self.command("DOME AUTO ON")

	def reqTIME( self ):
		return self.request("TIME")

	def reqST( self ):
		return self.request("ST")
		 
class telComError( Exception ):
	def __init__( self, message ):
		Exception.__init__( self, message)
		
		
class jt( telescope ):
	def __init__( self ):
		telescope.__init__( self, "jefftest5" )

class legacyTel(  ):
	def __init__(ip, port=5750):
		pass
	
if __name__ == '__main__':
	t=telescope("10.130.133.12", "MOCK")
	print t.reqALL()


	

	
	
