# -*- coding: utf-8 *-*
'''Includes all classes for criteria to exclude
off-the-reel-taken-values of a source-class
private methods _get will return True if the value fullfills the criteria and
falas if it fails.'''

class calcSmallerCalc:
	'''
	exclude value if result of dimension.calc[dim1]
	is smaller than dimension.calc[dim2]
	'''
	def __init__(self,dim1,dim2):
		self.dim1 = int(dim1)
		self.dim2 = int(dim2)
		
	def _get(self,dimension):
		##dependent to the size of the cluster (v = old + (new-old)/size_cluser))
		#print dimension.calc[self.dim1].value ,  dimension.calc[self.dim2].value
		if dimension.calc[self.dim1].value <  dimension.calc[self.dim2].value:
			return True
		else:
			return False


class calcSmallerValue:
	'''
	exclude value if result of a calc.xx-class
	is smaller than the given value
	'''
	def __init__(self,calcClass,value):
		self.dim = calcClass
		self.value = float(value)
		
	def _get(self):
		##dependent to the size of the cluster (v = old + (new-old)/size_cluser))
		#print dimension.calc[self.dim1].value ,  dimension.calc[self.dim2].value
		if self.dim.value <  self.value:
			return True
		else:
			return False


class calcBiggerValue:
	'''
	exclude value if result of a calc.xx-class
	is bigger than the given value
	'''
	def __init__(self,calcClass,value):
		self.dim = calcClass
		self.value = float(value)
		
	def _get(self):
		##dependent to the size of the cluster (v = old + (new-old)/size_cluser))
		#print dimension.calc[self.dim1].value ,  dimension.calc[self.dim2].value
		if self.dim.value >  self.value:
			return True
		else:
			return False


class valueBiggerValue:
	'''
	exclude value if the last value from given dimInstance
	is bigger than the given value
	'''

	def __init__(self,dimInstance,value):
		self.dimInstance = dimInstance
		self.value = float(value)

	def _get(self):
		##dependent to the size of the cluster (v = old + (new-old)/size_cluser))
		#print dimension.calc[self.dim1].value ,  dimension.calc[self.dim2].value
		if self.dimInstance._recent_value >  self.value:
			return True
		else:
			return False


class valueSmallerValue:
	'''
	exclude value if the last value from given dimInstance
	is bigger than the given value
	'''

	def __init__(self,dimInstance,value):
		self.value = float(value)
		self.dimInstance = dimInstance

	def _get(self):
		##dependent to the size of the cluster (v = old + (new-old)/size_cluser))
		#print dimension.calc[self.dim1].value ,  dimension.calc[self.dim2].value
		if self.dimInstance._recent_value <  self.value:
			return True
		else:
			return False


class absValueBiggerValue:
	'''
	exclude value if the last abs(value) from given
	dimInstance is bigger than the given value
	'''

	def __init__(self,dimInstance,value):
		self.value = float(value)
		self.dimInstance = dimInstance
		
	def _get(self):
		##dependent to the size of the cluster (v = old + (new-old)/size_cluser))
		#print dimension.calc[self.dim1].value ,  dimension.calc[self.dim2].value
		if abs(self.dimInstance._recent_value) >  self.value:
			return True
		else:
			return False
