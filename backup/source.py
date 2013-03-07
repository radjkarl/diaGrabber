# -*- coding: utf-8 *-*
import _dimension

class plainText(object):
	def __init__(self, file_name, dim_seperator):
		self.name = file_name
		self.dim_seperator = dim_seperator
		self.readout_every_n_line = 1


	
	
	class dim(object):
		'''choose dimensions of your file'''
		
		def __init__(self):
			self.index = 0
		interpolationTable = _dimension.interpolationTable
		function = _dimension.function
		identically = _dimension.identically

	def _readOut():#wird nur durch das programm aufgerufen
		pass
