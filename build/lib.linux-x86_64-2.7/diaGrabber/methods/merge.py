# -*- coding: utf-8 *-*
from numpy import isnan as _isnan

class mean:
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
	def _get(self, new_value,old_value,anz_values,intensity):
		if _isnan(old_value):
			return new_value, True
		else:
			new_value = old_value + intensity * new_value
			return new_value, True

	
