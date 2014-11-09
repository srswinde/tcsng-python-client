#!/usr/bin/python


from telescope_beta import telescope


class vatt(telescope):

	def __init__(self):
		telescope.__init__(self, "vatttel.vatt", "VATT")
		
	def reqALL(self):
		all_map = ["MOT", "RA", "DEC", "HA", "LST", "EL", "AZ", "SECZ" ]
		resp = self.request('ALL')
		resp = [val for val in resp.split(" ") if val != '']
		print resp
		return dict(zip(all_map, resp))
		
		
		
		
	
	def comSETBIAS(self, ra_asecs, dec_asecs):
	
		comStr = "SETBIAS {0} {1}".format(ra_asecs, dec_asecs)
		return self.command(comStr)


