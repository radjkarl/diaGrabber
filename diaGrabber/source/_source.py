# -*- coding: utf-8 *-*
import sys
#import numpy as np

#import methods.merge as mergeMethods
#import methods.calc as calcMethods
#import methods.exclude as excludeMethods
#import methods.transform as transformMethods
#from methods._container import (_aliasContainer, _calcContainer,
#	_excludeContainer, _transformContainer)


#from diaGrabber import _utils

class source(object):
	'''The basis-class for all type of sources provides some general functions. And
	evaluate the 'data_type'
	data_type can be "int", "float", hex" or "fooBar" in case you don't know the type of your data.
	'''
	def __init__(self, data_type):
		self._basis_dim = []
		self._merge_dim = []
		self.value_line = [] # every readout-line is splittet and saved in this list

		self._evalDataType(data_type)
		self.nBasis = 0
		self.nMerge = 0
		self._last_file = True
		self.done_readout = False
		self._checkFileFolderName()


	def setBasis(self, basis_list):
		'''
		In diaGrabber every generated basis-dimension will added to the basis.
		Use this method to define an alternative list of basis-dimensions.
		'''
		for b in basis_list:
			if b.__class__.__name__ != "basisDimension":
				sys.exit("ERROR setBasis(basis_list) takes only basisDimension-classes")
		self._basis_dim = basis_list
		#update basisDim._basisIndex
		for i, b in enumerate(self._basis_dim):
			b._basisIndex = i


	def setMerge(self, merge_list):
		'''
		In diaGrabber every generated merge-dimension will added to the basis.
		Use this method to define an alternative list of merge-dimensions.
		'''
		for m in merge_list:
			if m.__class__.__name__ != "mergeDimension":
				sys.exit("ERROR setBasis(basis_list) takes only mergeDimension-classes")
		self._merge_dim = merge_list
		#update basisDim._basisIndex
		for i, m in enumerate(self._merge_dim):
			m._mergeIndex = i


########private############


	def _checkFileFolderName(self):
		'''
		format self.file_name and self.folder to fit further procedures
		'''
		self.file_name = self.file_name.replace(" ","")
		if self.folder != "":
			self.folder = self.folder.replace(" ","")
			if self.folder[-1] != "/":
				self.folder += "/"
		if self.file_name[0] == "/":
			self.file_name = self.file_name[1:]


	def _setDatFile(self):
		'''
		create a self.dat_file trough combining self.folder and self.file_name
		if at least one of the basisDimensnions has ._is_folder=True:
		* create a new self.dat_file=self.file_name + [basis-folders] + self.file-name
		* decide whether this dat_file is self._last_file
		'''
		final_folder = self.folder
		self._last_file = True
		for b in self._basis_dim:
			(final_folder, last_file) = b._updateFolder(final_folder)
			if not last_file:
				self._last_file = False
		self.dat_file = final_folder + self.file_name
		self.len_dat_file = None #the len of the new file is unknown
		if not self.silent_readout:
			print "\nRead from file %s" %self.dat_file


	def _evalDataType(self, data_type):
		'''
		* 'int': integer numbers
		* 'float': floating-point numbers
		* 'hex': hexadecimale numbers
		'''
		if data_type == "float":
			self.evalStr = self._floatStr
		elif data_type == "hex":
			self.evalStr = self._hexStr
		elif data_type == "int":
			self.evalStr = self._intStr
		else:
			self.evalStr = self._unknownStr


	def _floatStr(self, s):
		'''when the values of the dimension are floating-point numbers, like {0.023}'''
		return float(s)


	def _hexStr(self, s):
		'''when the values of the dimension are hexadecimal integers, like {0xff}'''
		return int(s,16)


	def _intStr(self, s):
		'''when the values of the dimension are decimal integers, like {3}'''
		return int(s,10)


	def _unknownStr(self, s):
		'''
		when we dont know the type of the values of the dimension
		we use this slow-method to transform a string to a number
		'''
		return eval(s)


	def _getBasisMergeValues(self):
		'''
		in: list of string values, like ["0.1", "1.3", "#ff"]
		process:
			* extracts all basis- and merge-values from the given list
			* transform strings to numbers
		out: bool(are all basis-values in range)
		'''
		#calc for base
		for basis in self._basis_dim:
			if not basis._is_folder:
				try:
					basis._update(
						self.evalStr(self.value_line[basis.index]))
				except (IndexError, ValueError):
					print "skipping basis... %s" %self.value_line
					return False
			if not basis._in_range:
				return False
		###get merge-values
		for merge in self._merge_dim:
			try:
				merge._update(
					self.evalStr(self.value_line[merge.index]))
			except (IndexError, ValueError):
				print "skipping merge ... %s" %self.value_line
				return False
		return True


	def _embeddBasisDim(self, new_dimension):
		self._basis_dim.append(new_dimension)
		self.value_line.append("") #this becomes a list of all value-strings of the source
		new_dimension._basisIndex = self.nBasis #let the dimension know its place
		self.nBasis += 1


	def _embeddMergeDim(self, new_dimension):
		'''analoque to _embeddBasisDim'''
		self._merge_dim.append(new_dimension)
		self.value_line.append("")
		#self.merge_values.append(0.0)
		new_dimension._mergeIndex = self.nMerge
		self.nMerge += 1


	def _prepareStandard(self):
		'''
		the standard of preparation running in all source-like-classes
		infront of the readout
		'''
		for b in self._basis_dim:
			b._clean()
		for m in self._merge_dim:
			m._clean()
		#self._resetReadOut()
		self._setDatFile()
		self.done_readout = False


	def _getMinMax(self,basis_dims):
		'''
		some targets, like matrices can only work with bounded dimensions.
		in the case, that all values of a dimension are valid this method
		looks for the maximum and minimum value of those unbounded-dimensions
		'''
		min_max = []
		for i in range(len(basis_dims)):
			min_max.append([None,None])

		self._prepareReadOut()
		while True:#for every source-file
			while True:#for every line in file
				self._getValueLine()
				self._printStatus()
				if self.done_readout:
					break
				for n,basis in enumerate(basis_dims):
					try:
						if basis._is_folder:
							value = basis._recent_value
						else:
							value = basis._update(
								self.evalStr(self.value_line[basis.index]))
						if basis._in_range:
							if min_max[n][1] == None or value > min_max[n][1]:#max
								min_max[n][1] = value
							if min_max[n][0] == None or value < min_max[n][0]:#min
								min_max[n][0] = value
					except (IndexError, ValueError):
						pass
			self._prepareReadOut()
			if self._last_file:
				break

		print "\n"
		failed_maxMin = []
		for i,dim in enumerate(basis_dims):
			if min_max[i] == [None,None]:
				failed_maxMin.append(dim.name)
		if len(failed_maxMin) > 0:
			sys.exit("ERROR: cannot define min/max for basis-dimension(s) %s"
				%(failed_maxMin) )
		self._resetReadout()
		return min_max


	def _endReadOut(self):
		pass

	def _resetStandard(self):
		for b in self._basis_dim:
			b._reset()
		self.done_readout = False
