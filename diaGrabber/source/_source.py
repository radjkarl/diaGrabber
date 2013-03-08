# -*- coding: utf-8 *-*
import sys
import numpy as np
#from diaGrabber.methods.merge import mean
import diaGrabber.methods.merge as mergeMethods
import inspect

#from diaGrabber import _utils

class source(object):
	'''This basis-class for all type of source provides som general functions. And
	evaluate the 'data_type' '''
	def __init__(self, data_type):
		'''data_type = ["int", "float", hex"]'''
		self.basis_dim = []
		self.merge_dim = []
		#self.data_type = data_type
		#super(_source, self).__init__()
		self._evalDataType(data_type)
		
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

	def setBasis(self, basis_list):
		for b in basis_list:
			if b.__class__.__name__ != "basisDimension":
				sys.exit("ERROR setBasis(basis_list) takes only basisDimension-classes")
		self.basis_dim = basis_list
		
	def setMerge(self, merge_list):
		for m in merge_list:
			if b.__class__.__name__ != "mergeDimension":
				sys.exit("ERROR setBasis(basis_list) takes only mergeDimension-classes")
		self.merge_dim = merge_list
	
		
###########################
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


	def _getBasisMergeValues(self, file_dim):
		in_range = True
		###get merge-values
		for m in range(self.nMerge):
			try:
				(in_range, self.merge_values[m]) = self.merge_dim[m]._update(in_range,
					self.evalStr(file_dim[self.merge_dim[m].index]))
				#print self.evalStr(file_dim[self.merge_dim[m].index])
			except (IndexError, ValueError):
				print "skipping merge ... %s" %file_dim
				return False
		#calc for base
		for dim in range(self.nDim):
			try:
				(in_range, self.basis_values[dim]) = self.basis_dim[dim]._update(in_range,
					self.evalStr(file_dim[self.basis_dim[dim].index]))
			except (IndexError, ValueError):
				print "skipping basis... %s" %file_dim
				return False
		return in_range





	def _prepareStandard(self, matrixClass):
		self.matrixClass = matrixClass
		self.nDim = len(self.basis_dim)#matrixClass.nDim
		self.nMerge = len(self.merge_dim)#matrixClass.nMerge

		self.basis_values = []
		for i in range(self.nDim):
			self.basis_values.append(0)

		self.merge_values = []
		for i in range(self.nMerge):
			self.merge_values.append(0)
			

#	def __iter__(self):
		#necassary do do iterations like for x in self
#		return self

	def _getMinMax(self,basis_dims):
		min_max = []
		for i in range(len(basis_dims)):
			min_max.append([None,None])

		while True:
			try:
				file_dim = self._getFileDim()
			except StopIteration:
				break
			self._printStatus()

			in_range = True
			for n,dim in enumerate(basis_dims):
				#print file_dim
				try:
					(in_range, value) = dim._update(in_range,
						self.evalStr(file_dim[dim.index]))
	
					#print value
					if min_max[n][1] == None or value > min_max[n][1]:#max
						min_max[n][1] = value
					if min_max[n][0] == None or value < min_max[n][0]:#min
						min_max[n][0] = value
				except (IndexError, ValueError):
					pass
					#value = None
		#print min_max
		failed_maxMin = []
		for i,dim in enumerate(basis_dims):
			if min_max[i] == [None,None]:
				failed_maxMin.append(dim.name)
		if len(failed_maxMin) > 0:
			sys.exit("ERROR: cannot define min/max for basis-dimension(s) %s"
				%(failed_maxMin) )
		
		self._resetReadOut()
		return min_max




	def _readOut(self, readout_one_line, end_readOut):
		while True:#self.step_in_readOut_range < self.len_readOut_range:
			#i = self.readOut_range[self.step_in_readOut_range]
			try:

				if end_readOut:
					self._endReadOut()
					break
					
				file_dim = self._getFileDim()
				in_range = self._getBasisMergeValues(file_dim)
				if in_range:
					self.matrixClass._assign(self.basis_values, self.merge_values)
							
				self._printStatus()
				
				#self.step_in_readOut_range += 1
				if readout_one_line:
					return False


				
			except StopIteration:
				break

			except KeyboardInterrupt:
				self._endReadOut()
				break
				
		print ""
		self._resetReadOut()

		return True # means i'm done with readout



#######################################
class dimension(object):
	def __init__(self,name, index):
		self.name = str(name)
		self.index = int(index)
		self.calc = []
		self.exclude = []
		self.transform = False#can be loaded up with some methods.transform....
		self._plotOnlyRecentPosition = False#only needed for basis-dim
		self._calc_is_value = False


	def setCalcToValue(self, calc_index):
		"""set every value of the dimension to the result of one
		entry in dimension.calc"""
		self._calc_is_value = True
		self._calc_is_value_index = int(calc_index)
		if self._calc_is_value_index >= len(self.calc):
			sys.exit("ERROR: 'calc_index' has to be <len(dimension.calc)")



###############################


	def _processDim(self):

		#calc values bounded to dim
		for c in self.calc:
			c._get(self._recent_value)
		for c in self.exclude:
			if c._get():
				return False#not in range
				#in_range = False
		
		if self._calc_is_value:
			self._recent_value = self.calc[self._calc_is_value_index]
		return True



class basisDimension(dimension):
	"""basisDimensionText"""
	def __init__(self, name, index, resolution, includeMethod):
		super(basisDimension,self).__init__(name, index)

		self._is_counter = False # take value from source by default
		self._take_all_values = True
		self._include_chronic = False
		self._include_from_to = [None, None]
		self._recent_position = 0 #will be updated by target-class
		self._plot_range = slice(None,None,None)
		self.resolution = int(resolution)

		self.evalIncludeMethod(includeMethod)

	def evalIncludeMethod(self, includeMethod):
		'''
		* 'all': include all values of the dimension
		* [START,STOP]: include all values from START to STOP
		* 'chronic': include the last n=resolution values
		'''
		
		if includeMethod == "all" or includeMethod == "":
			self.includeAll()
		elif type(includeMethod) == list:
			if len(includeMethod) == 2:
				self.includeFromTo(includeMethod)
			else:
				sys.exit("ERROR: includeMethod hast to be a list of len==2")
		elif includeMethod == "chronic":
			self.includeChronic()
		else:
			sys.exit("ERROR includeMethod invalide")

	def setPlotOnlyRecentPosition(self, TrueOrFalse):
		self._plotOnlyRecentPosition = bool(TrueOrFalse)

	def setCounter(self, start = 0, delta = 1):
		self._is_counter = True
		self.index = 0 #to prevent error when reading out values from sources
		#self._recent_number = int(0)
		self._recent_value = start#-delta
		self._delta = delta
	
	def setPlotRange(self, start, stop, step):
		"""type 'None' if you don't want to define the input"""
		self._plot_range = slice(start,stop,step)

#########private############

	def _updateCounter(self):
		self._recent_value += self._delta


	def includeAll(self):
		'''Include all values and sort in a range from min to max values
		dissolved by the resolution
		!!!: not all sources can define the min and max values '''
		self._take_all_values = True
		#sys.exit("ERROR include all not implemended")
		###########get min max from source ##############
		#!!!!!!!!!!!!!!!!!!!!!!!!!!!
		#self._initSortRange()

	
	def includeFromTo(self,from_to_list):
		self._include_from_to = from_to_list
		self._take_all_values = False
		self._initSortRange()

	def includeChronic(self):
		'''Only take the last [dimension.resolution] values
		override when read more than that'''
		self._take_all_values = False
		self._include_chronic = True
		#set the first include_from_to ... this has to be updated
		self._include_from_to = [-self.resolution+1,self.resolution-1]
		self._chronic_step = 0
		self._initSortRange()

	def _updateChronic(self):
		self._chronic_step += 1
		if self._chronic_step >= self.resolution:
			self._chronic_step = 0
		self._sort_range[self._chronic_step] = self._recent_value
		#the smallest value in the chronic is the value infront of the recent one
		try:
			self._include_from_to[0] = self._sort_range[self._chronic_step+1]
		# except the revent value ist the last value in range - than its the first one
		except IndexError:
			self._include_from_to[0] = self._sort_range[0]
		self._include_from_to[1] = self._recent_value

	def _initSortRange(self):
		self._sort_range = np.linspace(self._include_from_to[0],self._include_from_to[1],
			self.resolution)


	def _update(self, in_range, source_value):

		if self._is_counter:
			self._updateCounter()
		else:
			self._recent_value = source_value

		if self._include_chronic:
			self._updateChronic()
		elif self._take_all_values:
			#update self._include_from_to with max in min values of the dim
			if source_value < self._include_from_to[0] or self._include_from_to[0] == None:
				self._include_from_to[0] = source_value
			if source_value > self._include_from_to[1] or self._include_from_to[1] == None:
				self._include_from_to[1] = source_value
		else:
			#check whether in range
			if self._include_from_to[0] > self._recent_value or \
					self._include_from_to[1] < self._recent_value:
				in_range = False

		if in_range:
			in_range = self._processDim()

		if in_range:
			if self._plotOnlyRecentPosition:
				self._plot_range = slice(self._recent_position,self._recent_position+1,1)

		return in_range, self._recent_value


class mergeDimension(dimension):
	"""mergeDimensionText"""
	def __init__(self,name, index, mergeMethod):
		super(mergeDimension,self).__init__(name, index)
		if mergeMethod == "" or mergeMethod == None:
			mergeMethod = mergeMethods.mean()
		#else:
		#	print type(mergeMethod)
		else:
			#check whether mergeMethod is a instande of one class in diagrabber-methods.merge
			all_merge_classes = tuple(x[1] for x in inspect.getmembers(mergeMethods,inspect.isclass))
			instance_of_some_class_in_merge_module = False
			for m in all_merge_classes:
				if isinstance(mergeMethod, m):
					instance_of_some_class_in_merge_module = True
			if not instance_of_some_class_in_merge_module:
				sys.exit("ERROR: mergeMethod %s of mergeDimension %s has to be a instance of classes in the module %s" %(mergeMethod, self.name, mergeMethods))

		self._mergeMethod = mergeMethod
		

	def setMergeMethod(self, mergeMethod):
		'''defines an alternative merge-method from :class:`diaGrabber.methods.merge`'''
		self._mergeMethod = mergeMethod


	def _update(self, in_range, source_value):
		self._recent_value = source_value
		
		#if in_range:
		in_range = self._processDim()


		return in_range, self._recent_value
