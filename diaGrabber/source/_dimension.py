# -*- coding: utf-8 *-*
import sys, os
import numpy as np

import methods.merge as mergeMethods
import methods.transform as transformMethods
from methods._container import (_aliasContainer, _calcContainer,
	_excludeContainer, _transformContainer)

from diaGrabber import _utils


class dimension(object):
	'''
	The basis-class of merge- and basisDimension. Provides everything
	that is identically for both of them.
	'''
	def __init__(self, source):

		self.source = source
		#helpers
		self._plotOnlyRecentPosition = False#only needed for basis-dim
		self._calc_is_value = False
		self._update_sort_range = True
		self._is_counter = False # take value from source by default
		self._in_range = True

		#get instances
		self._calc = _calcContainer()
		self._exclude = _excludeContainer()
		self._transform = _transformContainer()


	def calc(self):
		'''call-method for instance of :class:`diaGrabber.source.methods._container._calcContainer`'''
		return self._calc

	def exclude(self):
		'''call-method for instance of :class:`diaGrabber.source.methods._container._excludeContainer`'''
		return self._exclude

	def transform(self):
		'''call-method for instance of :class:`diaGrabber.source.methods._container._transformContainer`'''
		return self._transform

	def _evalPrefix(self,factor):
		if type(factor) == str:
			#get factor for given prefix
			prefixes = {"p":1e-12, "n":1e-9,"µ":1e-6,
				"m":1e-3,"c":1e-2, "d":1e-1, "k":1e3,"M":1e6,"G":1e9, "T":1e12}
			if factor not in prefixes:
				raise KeyError("prefix %s of Dimension %s is not valid. Valid types are: %s"
					%(factor, self.name, prefixes.keys()) )
			else:
				factor = prefixes[factor]
		else:
			factor = float(factor)
		self.prefix = factor
		self._transform.append(transformMethods.linear(
			factor=factor,offset=0,unit=self.unit), adhoc=True)
		

	def setCalcResultToValue(self, calc_index):
		"""set every value of the dimension to the result of one
		entry in dimension.getCalc()"""
		self._calc_is_value = True
		self._calc_is_value_index = int(calc_index)
		if self._calc_is_value_index >= len(self._calc._list):
			sys.exit("ERROR: 'calc_index' has to be <len(dimension.getCalc())")

	def setCounter(self, **kwargs):
		'''Use this method to generate a dimension as a linear counter.

		Optional kwargs ("keyword arguments") are:

		==================     ========  ==========   ==========================
		Keyword	               Type      Default      Description
		==================     ========  ==========   ==========================
		*start*                float     **0**        the fist value of the counter
		*delta*	               float     **1**        the difference which is
		                                              add to the last couter-value
		*update*               bool      **True**     **True**: continue counting
		                                              **False**: create a fixed
		                                              counter-list from start
		                                              to start + (delta*resolution)
		==================     ========  ==========   ==========================
		'''
		self._is_counter = True
		self._counter_step = 0
		#standard
		self._recent_value = 0
		self._start_value = 0
		self._delta = 1
		#individual
		for key in kwargs:
			if key == "update":
				self._update_sort_range = bool(kwargs[key])
			elif key == "start":
				self._recent_value = float(kwargs[key])
				self._start_value = float(kwargs[key])

			elif key == "delta":
				self._delta = float(kwargs[key])

	def _cleanStandard(self):
		self._calc._clean()


	def _transformDim(self):
		for n,i in enumerate(self._transform._list):
			if self._transform.adhoc[n]:
				self._recent_value = i.get(self._recent_value)

	def _processDim(self):
		'''	call the _get-method of all classes in .calc() and .exclude()'''

		#calc values bounded to dim
		for c in self._calc._list:
			c._get(self._recent_value)
		for c in self._exclude._list:
			if c._get():
				self._in_range = False
				continue#return False#not in range
		if self._calc_is_value:
			self._recent_value = self._calc[self._calc_is_value_index]
		#return True

	def _updateCounter(self):
		'''build the next value of the (linear) counter-dimension like: y=mx+n'''
		self._recent_value += self._delta
		#for fixed_Couters: go to start value if at the end
		if not self._update_sort_range:
			self._counter_step += 1
			if self._counter_step == self.resolution:
				self._recent_value = self._start_value
				self._counter_step = 0

class basisDimension(dimension):
	"""
	basisDimensions determine the shape and size of the target. Therefore its values are
	strictly bounded to a range of discrete points.
	
	see :py:func:`setArgs` fo all possible arguments.
	"""
	def __init__(self, source, **kwargs):
		super(basisDimension,self).__init__(source)

		#standard
		self.name = None
		self.index = None
		self.resolution = None
		self.unit = None
		self.prefix = ""

		self._includeAll()

		#helpers
		self._take_all_values = True
		self._include_chronic = False
		self._include_range = [None, None]
		self._recent_position = 0 #will be updated by target-class
		self._plot_range = slice(None,None,None)
		self._update_sort_range = True
		self._is_folder = False
		self._str_folder_values = None

		#indivídual
		self.setArgs(**kwargs)
		_utils.checkRequiredArgs({
			"name":self.name,
			"index":self.index,
			"resolution":self.resolution,
			"unit":self.unit})

		if self._is_folder:
			self._getFolderValues()


	def setArgs(self, **kwargs):
		'''
		**Required kwargs** ("keyword arguments") are:

		==================     ===========  ===============  ============================
		Keyword	               Type         Example          Description
		==================     ===========  ===============  ============================
		*name*                 str          "one"            the name of the basisDimension
		*unit*                 str          "m/s"            the unit of the basisDimension
		*index*                int          0                the position in the source-file
		                                                     '0' will be the first one
		                       str          "folder"         all sourcefiles are in *folders*
		                                                     each name of a folder represents
		                                                     a value of this basisDimension
		                                                     The folder is located between
		                                                     the source-folder (if given) and
		                                                     source-file.
		                                                     It is possible to use multible
		                                                     basisDimensions with
		                                                     index='folder'. In this case the
		                                                     order of those dimensions
		                                                     represents the order in th
		                                                     filesystem.
		                                    "counter"        see :py:meth:`setCounter`
		                                                     (with update=True)
		                                    "fixedCounter"   see :py:meth:`setCounter`
		                                                     (with update=False)
		*resolution*           int          50               the number of different
		                                                     positions stored in the range
		                                                     of all values of the
		                                                     basisDimension
		==================     ===========  ===============  ============================

		**Optional kwargs** ("keyword arguments") are:

		==================     ===========  =======          ============================
		Keyword	               Type         Default          Description
		==================     ===========  =======          ============================
		*prefix*               float/str    1                the prefix of the
		                                                     unit. can be a float
		                                                     or a string like 'm' for milli
		                                                     see :py:func:`_evalPrefix` for all
		                                                     possibilities
		*include*              list/str     "all"            in opposite to mergeDimensions
		                                                     every basisDimension is strictly
		                                                     bounded. That means every basis
		                                                     has a range in which its values
		                                                     can vary. Typing **'all'**
		                                                     indicates diaGrabber to look
		                                                     for the min. and max. values
		                                                     in the source(s) and set the
		                                                     range as [min,max]
		                                                     typing **[x,y]** would bound
		                                                     the basis-values between x,y
		                                                     all values bigger and lower than
		                                                     those would be excluded
		                                                     typing **chronic** bounds the
		                                                     basis not to the size but to the
		                                                     ammound of values. this means
		                                                     that in this case every last n
		                                                     values would be stored, where
		                                                     n is the value of 'resolution'
		==================     ===========  =======          ============================
		'''
		prefix = None
		for key in kwargs:
			if key == "name":
				self.name = str(kwargs[key])
			elif key == "prefix":
				prefix = kwargs[key]
			elif key == "unit":
				self.unit = str(kwargs[key])
			elif key == "index":
				if type(kwargs[key]) != int:
					if kwargs[key] == "runningCounter" or kwargs[key] == "counter":
						self.setCounter(update=True)
						self.index = 0
					elif kwargs[key] == "fixedCounter":
						self.setCounter(update=False)
						self.index = 0
					elif kwargs[key] == "folder":
						self._is_folder = True
						self.index = 0
					else:
						sys.exit("ERROR: index has to be an iteger or 'runningCounter' or 'fixedCounter'")
				else:
					self.index = int(kwargs[key])
			elif key == "resolution":
				self.resolution = int(kwargs[key])
			elif key == "include":
				pass
			else:
				raise KeyError("keyword '%s' not known" %key)

		#after main loop to ensure that unit is set
		if prefix != None:
			self._evalPrefix(prefix)

		for key in kwargs:
			#in extra cycle to ensure that resolution is set
			if key == "include":
				if kwargs[key] == "all" or kwargs[key] == "" or kwargs[key] == None:
					self._includeAll()
				elif kwargs[key] == "chronic":
					self._includeChronic()
				elif type(kwargs[key]) == list:
					self._includeRange(kwargs[key], True)
				else:
					sys.exit("ERROR include invalide")


	def setPlotOnlyRecentPosition(self, TrueOrFalse):
		'''Set this if you only want to plot the last readout basis-value.'''
		self._plotOnlyRecentPosition = bool(TrueOrFalse)


	def setPlotRange(self, start=None, stop=None, step=None):
		'''Define the visible range of the plotted values.
		
		:param start: defines the fist position in the range of all basis-values. {0} would be the first position.
		:type start: int
		:param start: defines the last position in the range of all basis-values. {RESOLUTION} would be the last position.
		:type start: int
		:param step: defines the number of basis-values to jump over for plotting. {1} would plot every value of this dimension. {10} would plot every 10st value.
		:type start: int
		type {None} if you don't want to define one entry.
		'''
		if start != None:
			start = int(start)
		if stop != None:
			stop = int(stop)
		if step != None:
			step = int(step)
			if step < 1:
				sys.exit("ERROR [setPlotRange]: 'step' has to be >= 1")
		
		self._plot_range = slice(start,stop,step)

#########private############

	def _clean(self):
		if self._is_counter:
			self._recent_value = self._start_value
		self._cleanStandard()


	def _includeAll(self):
		'''Include all values and sort in a range from min to max values
		dissolved by the resolution
		!!!: not all sources can define the min and max values '''
		self._take_all_values = True


	def _getFolderValues(self):
		self._str_folder_values = os.listdir(self.source.folder)
		i = 0
		while i < len(self._str_folder_values):
			#clean from every entry in main-folder that is not a folder itself
			if not os.path.isdir(self.source.folder + self._str_folder_values[i]):
				self._str_folder_values.pop(i)
				i -= 1
			i += 1
		if len(self._str_folder_values) == 0:
			sys.exit("ERROR: no folders in for basisDimension %s in folder %s"
				%self.name, self.source.folder)


	def _updateFolder(self, folder_structure):
		if self._is_folder:
			folder_name = self._str_folder_values[self.index]
			self._update(self.source.evalStr(folder_name))
			if self.index == len(self._str_folder_values)-1:
				last_file = True
			else:
				last_file = False
				self.index += 1
			return 	folder_structure + folder_name + "/", last_file
		return folder_structure, True


	def _reset(self):
		if self._is_folder:
			self.index = 0


	def _includeRange(self,range_list, transformRange=False):
		'''include only values from x to y'''
		if len(range_list) == 2:
			self._include_range = [min(range_list),max(range_list)]
		else:
			sys.exit("ERROR: include hast to be a list of len==2")
		self._take_all_values = False

		if transformRange:
			print "set range for %s(%s%s) to %s" %(
				self.name, self.prefix, self.unit, self._include_range)
			for n,i in enumerate(self._transform._list):
				#transform sort_range
				if self._transform.adhoc[n]:
					self._include_range[0] = i.get(self._include_range[0])
					self._include_range[1] = i.get(self._include_range[1])
					self.unit = i.unit
			print "... thats in (%s) %s" %(self.unit, self._include_range)
		elif self.prefix != "":
			start = self._include_range[0] / self.prefix
			stop = self._include_range[1] / self.prefix
			print "set range for %s(%s%s) to [%s,%s]" %(self.name, self.prefix, self.unit, start,stop)
			print "... thats in (%s) %s" %(self.unit, self._include_range)
		else:
			print "set range for %s(%s) to %s" %(self.name, self.unit, self._include_range)
		if self._include_range[0] == self._include_range[1]:
			print "WARNING: boundaries of range are equal!"
		self._initSortRange()


	def _getIncludeRange(self):
		return self._include_range


	def _includeChronic(self):
		'''Only take the last [dimension.resolution]-values
		override when read more than that'''
		self._take_all_values = False
		self._include_chronic = True
		#set the first include_range ... this has to be updated
		self._include_range = [0,self.resolution-1]
		self._chronic_step = 0
		self._initSortRange()


	def _updateChronic(self):
		'''updates the sort-range for a chronic-dimension'''
		self._chronic_step += 1
		if self._chronic_step >= self.resolution:
			self._chronic_step = 0
		if self._update_sort_range:
			self._sort_range[self._chronic_step] = self._recent_value
	
			if self._is_counter:
				#the smallest/biggest value in the chronic is the value
				#infront of the recent one
				#this is correct because a counter increases/decreases monotone
				try:
					self._include_range[0] = self._sort_range[self._chronic_step+1]
				# except the revent value ist the last value in range
				#- than its the first one
				except IndexError:
					self._include_range[0] = self._sort_range[0]
				self._include_range[1] = self._recent_value
			else:
				self._include_range[0] = min(self._sort_range)
				self._include_range[1] = max(self._sort_range)


	def _initSortRange(self):
		'''builds the (first) sort-range as a numpy.linspace(from,to,step)'''
		self._sort_range = np.linspace(self._include_range[0],self._include_range[1],
			self.resolution)


	def _update(self, source_value):
		'''main update-procedure which runs ever time a new value is readout from the source.'''
		self._in_range = True
		if self._is_counter:
			self._updateCounter()
		else:
			self._recent_value = source_value
		self._transformDim()

		if self._include_chronic:
			self._updateChronic()
		elif self._take_all_values:
			#update self._include_range with max in min values of the dim
			if self._recent_value < self._include_range[0] or self._include_range[0] == None:
				self._include_range[0] = self._recent_value
			if self._recent_value > self._include_range[1] or self._include_range[1] == None:
				self._include_range[1] = self._recent_value
		else:
			#check whether in range
			if self._include_range[0] > self._recent_value or \
					self._include_range[1] < self._recent_value:
				self._in_range = False
		if self._in_range:
			self._processDim()

		if self._in_range:
			if self._plotOnlyRecentPosition:
				self._plot_range = slice(self._recent_position,self._recent_position+1,1)

		return self._recent_value


class mergeDimension(dimension):
	"""
	Values of mergeDimensions where directly written into the matrices of the target.
	That's why it's values were not bounded. If merge-values are store in postitions
	of the mergeMatrix which are not empty, its values have to be merged
	(that gives the name of the dimension). Have a look at :mod:`diaGrabber.source.methods.merge` to see all methods
	of merging values together.
	
	see :py:func:`setArgs` fo all possible arguments.
	"""
	def __init__(self, source, **kwargs):

		super(mergeDimension,self).__init__(source)

		#standard
		self.name = None
		self.index = None
		self.resolution = None
		self.unit = None
		self.prefix = None
		self._mergeMethod = mergeMethods.last()
		
		#individual
		self.setArgs(**kwargs)
		_utils.checkRequiredArgs({
			"name":self.name,
			"index":self.index,
			"unit":self.unit
			})

		self._alias = _aliasContainer(self)

	#def setArgs(self, **kwargs):
	#	'''may overridden by some source-class'''
	#	return self._setBasisArgs(**kwargs)

	def setArgs(self, **kwargs):
		'''
		**Required kwargs** ("keyword arguments") are:

		==================     ===========  ==============   ============================
		Keyword	               Type         Example          Description
		==================     ===========  ==============   ============================
		*name*                 str          "one"            the name of the basisDimension
		*unit*                 str          "m/s"            the unit of the basisDimension
		*index*                int          0                the position in the source-file
		                                                     '0' will be the first one
		                       str          "counter"        see :py:meth:`setCounter`
		                                                     (with update=True)
		                                    "fixedCounter"   see :py:meth:`setCounter`
		                                                     (with update=False)
		==================     ===========  ==============   ============================

		**Optional kwargs** ("keyword arguments") are:

		==================     ===========  =============    ============================
		Keyword	               Type         Default          Description
		==================     ===========  =============    ============================
		*prefix*               float/str    1                the prefix of the
		                                                     unit. can be a float
		                                                     or a string like 'm' for milli
		                                                     see :py:func:`_evalPrefix` for all
		                                                     possibilities
		*merge*                instance     merge.last()     see                          :mod:`diaGrabber.source.methods.merge` for all possible options
		==================     ===========  =============    ============================
		'''
		prefix = None
		for key in kwargs:
			if key == "name":
				self.name = str(kwargs[key])
			elif key == "unit":
				self.unit = str(kwargs[key])
			elif key == "prefix":
				prefix = kwargs[key]
			elif key == "index":
				if type(kwargs[key]) != int:
					if kwargs[key] == "runningCounter" or kwargs[key] == "counter":
						self.setCounter(update=True)
						self.index = 0
					elif index == "fixedCounter":
						self.setCounter(update=False)
						self.index = 0
					else:
						sys.exit("ERROR: index has to be an iteger or 'runningCounter' or 'fixedCounter'")
				else:
					self.index = int(kwargs[key])
			elif key == "merge":
				_utils.checkModuleInstance(kwargs[key], mergeMethods)
				self._mergeMethod = kwargs[key]
			else:
				raise KeyError("keyword '%s' not known" %key)
		#after main loop to ensure that unit is set
		if prefix != None:
			self._evalPrefix(prefix)

	#caller functions
	def alias(self):
		'''
		With this method you can bound the success of taking a new merge-value
		on the success of other mergeDimensions.
		Example::
			
			one = mergeDimension(... merge=merge.max() )
			two = mergeDimension( ... )
			two.alias.append(one)
			
		In this case only merge-values of the dimension 'two' were taken if those
		values of 'one' were also taken.
		
		See all possible methods of alias() in:
		:class:`diaGrabber.source.methods._container._aliasContainer`
		'''
		return self._alias

	def _update(self, source_value):
		'''main update-procedure which runs ever time a new value is readout
		from the source.'''
		self._in_range = True
		if self._is_counter:
			self._updateCounter()
		else:
			self._recent_value = source_value
		self._transformDim()
		self._processDim()
		return self._recent_value

	def _clean(self):
		self._cleanStandard()


