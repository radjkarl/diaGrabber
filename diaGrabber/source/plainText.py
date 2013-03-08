# -*- coding: utf-8 *-*
#from copy import deepcopy
import linecache, sys

from diaGrabber import _utils
import _source


class plainText(_source.source):
	def __init__(self, folder, file_name, dim_seperator, data_type = "unknown"):
		super(plainText,self).__init__(data_type)
		self.folder = folder
		if self.folder != "" and self.folder[-1] != "/":
			self.folder += "/"
		self.file_name = file_name
		self.dat_file = self.folder + self.file_name
		self.dim_seperator = dim_seperator
		self.readout_every_n_line = 1
		#self.dimension = _dimension.dimension
		self.n_line = 0

		try:
			self.len_dat_file = len(file(self.dat_file, "r").readlines())
		except IOError:#found no readable file called self._output_file
			print "ERROR: does your output_file exist?"
			sys.exit()


	def basisDimension(self, name, index, resolution, includeMethod=""):
		'''
		:class:`diaGrabber.source._dimension.basisDimension` \n
		needs:
		'''	
		new_dimension  = _source.basisDimension(name, index, resolution, includeMethod)
		self.basis_dim.append(new_dimension)
		return new_dimension




	def mergeDimension(self, name, index, mergeMethod=""):
		'''
		:class:`diaGrabber.source._dimension.mergeDimension` \n
		needs: "
		'''	
		new_dimension  = _source.mergeDimension(name, index, mergeMethod)
		self.merge_dim.append(new_dimension)
		return new_dimension



	def _prepareReadOut(self, matrixClass):
		self._prepareStandard(matrixClass)
		self._initPrintStatus()

	def _initPrintStatus(self):
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



	def _getFileDim(self):
		if self.n_line < self.len_dat_file:
			self.n_line += self.readout_every_n_line
			#self.A, self.B = self.B, self.A + self.B
			line = linecache.getline(self.dat_file, self.n_line+1)
			#self.file_dim = line[:-2].split(self.dim_seperator)
			return line[:-2].split(self.dim_seperator)
		else:
			raise StopIteration

	def _printStatus(self):
		if self.n == self.showBar_counter:
			self.bar_step += self.bar_step_delta
			_utils.statusBar(self.bar_step,self.sum_bar, 20)
			self.n = 0
		self.n+= 1

	def _resetReadOut(self):
		self.n_line = 0
		self._initPrintStatus()

	def _endReadOut(self):
		pass

if __name__ == "__main__":
########test
	folder = "/home/bedrich/Dokumente/HiWi/Strahlvermessung/"
	
	file_name = "test.txt"#"
	seperator = " "
	data_type = "float"
	f = plainText(folder, file_name, seperator, data_type)
	f.readout_every_n_line = 10
	
	#for x in f:
	#	print x
	#f.n_line = 0
	while True:
		try:
			print f.next()
		except StopIteration:
			break
