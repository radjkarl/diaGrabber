# -*- coding: utf-8 *-*
#from diaGrabber.methods.merge import mean
import numpy as np
from diaGrabber.methods.merge import mean
import sys

class _dimension(object):
	def __init__(self,name, index):
		self.name = name
		self.index = index
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



class basisDimension(_dimension):
	"""basisDimensionText"""
	def __init__(self, name, index, resolution, includeMethod):
		super(basisDimension,self).__init__(name, index)

		self._is_counter = False # take value from source by default
		self._take_all_values = True
		self._include_chronic = False
		self._include_from_to = [None, None]
		self._recent_position = 0 #will be updated by target-class
		self._plot_range = slice(None,None,None)

		if includeMethod == "all" or includeMethod == "":
			self.includeAll(resolution)
		elif type(includeMethod) == list:
			if len(includeMethod) == 2:
				self.includeFromTo(includeMethod[0],includeMethod[1], resolution)
			else:
				sys.exit("ERROR: includeMethod hast to be a list of len==2")
		elif includeMethod == "chronic":
			self.includeChronic(resolution)
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


	def includeAll(self, resolution):
		'''Include all values and sort in a range from min to max values
		dissolved by the resolution
		!!!: not all sources can define the min and max values '''
		self._take_all_values = True
		self.resolution = int(resolution)
		sys.exit("ERROR include all not implemended")
		###########get min max from source ##############
		#!!!!!!!!!!!!!!!!!!!!!!!!!!!
		self._initSortRange()

	
	def includeFromTo(self,from_value,to_value, resolution):
		self._include_from_to = [from_value,to_value]
		self._take_all_values = False
		self.resolution = int(resolution)
		self._initSortRange()

	def includeChronic(self, resolution):
		'''Only take the last [dimension.resolution] values
		override when read more than that'''
		self._take_all_values = False
		self._include_chronic = True
		self.resolution = int(resolution)
		#set the first include_from_to ... this has to be updated
		self._include_from_to = [-self.resolution+1,self.resolution-1]
		self._chronic_step = 0
		self._initSortRange()

	def _updateChronic(self, ):
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


class mergeDimension(_dimension):
	"""mergeDimensionText"""
	def __init__(self,name, index, mergeMethod):
		super(mergeDimension,self).__init__(name, index)
		if mergeMethod == "":
			mergeMethod = mean()
		self._mergeMethod = mergeMethod
		

	def setMergeMethod(self, mergeMethod):
		self._mergeMethod = mergeMethod


	def _update(self, in_range, source_value):
		self._recent_value = source_value
		
		#if in_range:
		in_range = self._processDim()


		return in_range, self._recent_value
