# -*- coding: utf-8 *-*
'''
This module includes all methods to merge values from
type :class:`diaGrabber.source._dimension.mergeDimension`.
"Merge" means in this case to handle an incoming  new value at a place in
the target where other values exists allready.
Depending on the chosen target-class :mod:`diaGrabber.target` its also
possible that incomming values have an intensity < 1 because the orig.
values were splitted.
'''

from numpy import isnan as _isnan

class last:
	'''Take every last incomming value. Do not merge with old values.
	This is the standard-procedure.'''

	def _get(self, new_value,old_value,anz_values,intensity):
		return new_value, True


class mean:
	'''Caluculate and take the mean of all incomming values.'''
	def _get(self,new_value,old_value,anz_values,intensity):
		if _isnan(old_value):
			return new_value, True
		else:
			##middle the basis_clustered to the new basis values
			##dependent to the size of the cluster (v = old + (new-old)/size_cluser))
			value = old_value + intensity * ( (new_value - old_value) / (anz_values+1) )
			#value in matrix, is_new_value
			return value,True
	
class max:
	'''Take only the maximum of all incomming values.'''

	def _get(self, new_value,old_value,anz_values,intensity):
		if _isnan(old_value):
			return new_value, True
		else:
			new_value = old_value + intensity * (new_value - old_value)
			if new_value > old_value:
				return new_value, True
			else:
				return old_value, False

class min:
	'''Take only the minimum of all incomming values.'''


	def _get(self, new_value,old_value,anz_values,intensity):
		if _isnan(old_value):
			return new_value, True
		else:
			new_value = old_value + intensity * (new_value - old_value)
			if new_value < old_value:
				return new_value, True
			else:
				return old_value, False
	
class sum:
	'''Caluculate and take the sum of all incomming values.'''

	def _get(self, new_value,old_value,anz_values,intensity):
		if _isnan(old_value):
			return new_value, True
		else:
			new_value = old_value + intensity * new_value
			return new_value, True

