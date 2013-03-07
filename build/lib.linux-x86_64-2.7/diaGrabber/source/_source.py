# -*- coding: utf-8 *-*

class _source(object):
	def __init__(self, data_type):
		'''data_type = ["int", "float", hex"]'''
		#self.data_type = data_type
		#super(_source, self).__init__()
		
		if data_type == "float":
			self.evalStr = self._floatStr
		elif data_type == "hex":
			self.evalStr = self._hexStr
		elif data_type == "int":
			self.evalStr = self._intStr
		else:
			self.evalStr = self._unknownStr

	def _floatStr(self, s):
		#string is a hexadecimal integer
		return float(s)
		
	def _hexStr(self, s):
		#string is a hexadecimal integer
		return int(s,16)
		
	def _intStr(self, s):
		#string is a decimal integer
		return int(s,10)

	def _unknownStr(self, s):
		#datatype of string is unknown
		return eval(s)


	def _assignValues(self, file_dim):
		in_range = True
		###get merge-values
		for m in range(self.nMerge):
			try:
				(in_range, self.merge_values[m]) = self.merge_dim[m]._update(in_range,
					self.evalStr(file_dim[self.merge_dim[m].index]))
				#print self.evalStr(file_dim[self.merge_dim[m].index])
			except (IndexError, ValueError):
				print "skipping ... %s" %file_dim
				in_range = False
		if in_range: ## if merge_value is in range: get the basis values
			#calc for base
			try:
				for dim in range(self.nDim):
					(in_range, self.basis_values[dim]) = self.basis_dim[dim]._update(in_range,
						self.evalStr(file_dim[self.basis_dim[dim].index]))
			except (IndexError, ValueError):
				print "skipping ... %s" %file_dim
				in_range = False
		if in_range:
			positionsIntensities = self.matrixClass._assign(self.basis_values)
			for position, intensity in positionsIntensities:
				tPostion = tuple(position)
				for m in range(self.nMerge):
					(replace_value, do_replace)= self.merge_dim[m].merge._get(self.merge_values[m],
						self.mergeMatrix[m][tPostion],self.densityMatrix[m][tPostion],intensity)
					if do_replace:
						self.mergeMatrix[m][tPostion] = replace_value
						self.densityMatrix[m][tPostion] += intensity

	def _prepareStandard(self, matrixClass):
		self.matrixClass = matrixClass
		####is es schlau erst alle sachen von target zo kopieren???
		self.nDim = matrixClass.nDim
		self.basis_dim = matrixClass.basis_dim
		self.merge_dim = matrixClass.merge_dim
		self.nMerge = matrixClass.nMerge
		self.mergeMatrix = matrixClass.mergeMatrix
		self.sortMatrix = matrixClass.sortMatrix
		self.densityMatrix = matrixClass.densityMatrix

		self.basis_values = []
		for i in range(self.nDim):
			self.basis_values.append(0)

		self.merge_values = []
		for i in range(self.nMerge):
			self.merge_values.append(0)
			
