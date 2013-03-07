# -*- coding: utf-8 *-*
'''Includes all classes for calculations for off-the-reel-taken-values of a source-class'''

class mean:
	'''calc. the mean of the last n values'''
	def __init__(self,n):
		self.value = 0.0
		self.quantity = 0#number of middles values so far
		self.maxQuantity = n # middle until this quantity is reached
		
	def _get(self,new_value):
		##dependent to the size of the cluster (v = old + (new-old)/size_cluser))
		if self.quantity < self.maxQuantity:
			self.quantity += 1
		self.value += (new_value - self.value) / self.quantity


class delta:
	'''calc. the mean-difference of the last n values'''
	def __init__(self,n):
		self.last_value = 0.0
		self.value = 0.0#last delta
		self.quantity = 0.0#number of middles values so far
		self.maxQuantity = float(n) # middle until this quantity is reached
		
	def _get(self,new_value):
		##dependent to the size of the cluster (v = old + (new-old)/size_cluser))
		delta = new_value-self.last_value
		self.last_value = new_value
		if self.quantity < self.maxQuantity:
			self.quantity += 1
		self.value += (delta - self.value) / self.quantity

class divideCalcClasses:
	'''divide the last calulated values of two given calc-classes
		use it like this:
		dim1 = myFile.dimension(...)
		dim1.calc.append(calc.delta(10))
		
		dim2 = myFile.dimension(...)
		dim2.calc.append(calc.delta(10))
		#<<<
		dim2.calc.append(dim1.calc[0], dim2.calc[0])
		#>>>
		#In this case the derivate d(dim1)/d(dim2) middled for the last 10
		#valued will be calculated
		This procedure will only work if both dimensions are in merge or basis.
		'''
	def __init__(self, upperCalcClass, lowerCalcClass):
		self.upperCalcClass = upperCalcClass
		self.lowerCalcClass = lowerCalcClass

	def _get(self,new_value):
		#print self.upperCalcClass.value , self.lowerCalcClass.value
		try:
			self.value = self.upperCalcClass.value / self.lowerCalcClass.value
		except ZeroDivisionError:
			self.value = self.upperCalcClass.value / 1e-20
		#print self.value


			
			

#class derivate:
	#
	#def __init__(self,dimension,max_sum_delta):
		#pass#Ableitung ... wie  mean nur, dass dazu ein weiterer wert betrachet wird

	#def get(v1,v2):
		#
	#
	#return
