# -*- coding: utf-8 *-*
#from copy import deepcopy
import linecache, sys

from diaGrabber import _utils
from _dimension import _dimension
from _source import _source


class plainText(_source):
	def __init__(self, folder, file_name, dim_seperator, data_type = "unknown"):
		super(plainText,self).__init__(data_type)
		self.folder = folder
		self.file_name = file_name
		self.dat_file = self.folder + self.file_name
		self.dim_seperator = dim_seperator
		self.readout_every_n_line = 1
		#self.dimension = _dimension.dimension
		
		try:
			self.len_dat_file = len(file(self.dat_file, "r").readlines())
		except IOError:#found no readable file called self._output_file
			print "ERROR: does your output_file exist?"
			sys.exit()

	class dimension(_dimension):
		'''...test'''
		def __init__(self, name, index=0):
			'''index = [collumn in your stream-output] e.g. 2'''
			try:
				self.index = int(index)
			except TypeError:
				self.index = 0
			super(plainText.dimension, self).__init__(name, self.index)
			
			
	def _prepareReadOut(self, matrixClass):
		#matrixClass.nDim
		self._prepareStandard(matrixClass)
		
		self.n = 0
		self.sum_bar = 100
		self.showBar_counter = self.len_dat_file / (self.readout_every_n_line * self.sum_bar)
		if self.showBar_counter == 0:
			self.showBar_counter = 1
		self.bar_step = 0
		self.bar_step_delta = int(self.sum_bar / self.len_dat_file)
		if self.bar_step_delta == 0:
			self.bar_step_delta = 1
		else:
			self.sum_bar = self.bar_step_delta*self.len_dat_file

		self.readOut_range = range(0,self.len_dat_file,self.readout_every_n_line)
		self.len_readOut_range = len(self.readOut_range)
		self.step_in_readOut_range = 0
	
	def _readOut(self, readout_one_line, end_readOut):
		while self.step_in_readOut_range < self.len_readOut_range:
			i = self.readOut_range[self.step_in_readOut_range]
			
			
		#for i in readOut_range:
			line = linecache.getline(self.dat_file, i+1)
			file_dim = line[:-2].split(self.dim_seperator)
			
			self._assignValues(file_dim)
			
						
			if self.n == self.showBar_counter:
				self.bar_step += self.bar_step_delta
				_utils.statusBar(self.bar_step,self.sum_bar, 20)
				self.n = 0
			self.n+= 1
			
			self.step_in_readOut_range += 1
			if readout_one_line:
				return False
			if end_readOut:
				return True

		return True # means i'm done with readout


	

	
	
	def _getMinMax(self,dims):
		min_max = []
		len_dims = len(dims)
		for i in range(len_dims):
			min_max.append([None,None])
		for i in range(0,self.len_dat_file,self.readout_every_n_line):
			line = linecache.getline(self.dat_file, i+1)
			for d in range(len_dims):
				value = eval(line[:-2].split(self.dim_seperator)[dims[d]])
				if min_max[d][1] == None or value > min_max[d][1]:#max
					min_max[d][1] = value
				if min_max[d][0] == None or value < min_max[d][0]:#min
					min_max[d][0] = value
		return min_max
	

	

