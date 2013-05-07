# -*- coding: utf-8 *-*
from diaGrabber import _utils
import calc as calcMethods
import exclude as excludeMethods
import transform as transformMethods



class _aliasContainer:
	'''
	The container-class of :func:`diaGrabber.source._dimension.mergeDimension.alias`.
	'''
	def __init__(self, parent):
		self._parent = parent.__class__
		self._list = []
	
	def append(self, mergeDimensionInstance):
		'''Add a new alias-condition to the container.
		need a instance of :class:`diaGrabber.source._dimension.mergeDimension` for this.'''
		_utils.checkClassInstance(mergeDimensionInstance,self._parent)
		self._list.append(mergeDimensionInstance)

	def set(self, mergeDimensionInstance, index=None):
		'''add or change the alias-contition on a known position in the alias-container'''
		if index==None:
			self.append(mergeDimensionInstance)
		else:
			_utils.checkClassInstance(mergeDimensionInstance,self._parent)
			self._list[int(index)] = mergeDimensionInstance


class _calcContainer:
	'''
	The container-class for all methods in :mod:`diaGrabber.source.methods.calc`.
	'''
	def __init__(self):
		self._list = []

	def append(self, calcMethodInstance):
		'''add a new calc-procedure to the container, need a instance of :mod:`diaGrabber.source.methods.calc` for this.'''
		_utils.checkModuleInstance(calcMethodInstance,calcMethods)
		self._list.append(calcMethodInstance)

	def get(self, index=None):
		'''return all calc-instances of one (at a given index) stored in the container '''
		if index==None:
			#return every entry as list
			return self._list
		else:
			return self._list[int(index)]

	def set(self, calcMethodInstance, index=None):
		'''ad or change the calc-instance at a given index'''
		if index==None:
			self.appendCalcMethod(calcMethodInstance)
		else:
			_utils.checkModuleInstance(calcMethodInstance,calcMethods)
			self._list[int(index)] = calcMethodInstance

	def available(self):
		'''return all available classes in methods.calc'''
		return _utils.getAvailableClassesInModule(calcMethods)

	def _clean(self):
		for l in self._list:
			l._clean()


class _excludeContainer:
	'''
	assign one or more excludeMethod-classes of from :mod:`diaGrabber.methods.exclude`
	Using this option you can exclude values from a dimension because of its development
	when readed out.
	'''
	def __init__(self):
		self._list = []

	def append(self, excludeMethodInstance):
		'''add a new exclude-condition to the container. need a instance of :mod:`diaGrabber.source.methods.exclude` for this.'''
		_utils.checkModuleInstance(excludeMethodInstance,excludeMethods)
		self._list.append(excludeMethodInstance)

	def get(index=None):
		'''return all or one (at a given index) exclude-condition of the container'''
		if index==None:
			return self._list
		else:
			return self._list[int(index)]

	def available(self):
		'''return all available classes in methods.exlude'''
		return _utils.getAvailableClassesInModule(excludeMethods)

	def set(self, excludeMethodInstance, index=None):
		'''add or change an exclude-instance in the container'''
		if index==None:
			self.appendExcludeMethod(excludeMethodInstance)
		else:
			_utils.checkModuleInstance(excludeMethodInstance,excludeMethods)
			self._list[int(index)] = excludeMethodInstance

class _transformContainer:
	'''
	assign one or more transformMethod-classes of from :mod:`diaGrabber.methods.transform`
	using this option you can trnsform all basis-values after readout with the command::
		target.transformDim()
	'''
	def __init__(self):
		self._list= []
		self.adhoc = []

	def append(self, transformMethodInstance, adhoc=False):
		'''
		*adhoc*: transform each value right in the readout
		else the talues can be transformed via :func:`diaGrabber.target._matrixMethods.matrixMethods.transformDim`
		'''
		_utils.checkModuleInstance(transformMethodInstance,transformMethods)
		self.adhoc.append(bool(adhoc))
		self._list.append(transformMethodInstance)

	def get(self):
		return self._list

	def available(self):
		'''return all available classes in methods.transform'''
		return _utils.getAvailableClassesInModule(transformMethods)

	def _clean(self):
		for l in self._list:
			l._clean()
