# -*- coding: utf-8 *-*


class mean:
	def __init__(self,maxQuantity):
		self.value = 0.0
		self.quantity = 0#number of middles values so far
		self.maxQuantity = maxQuantity # middle until this quantity is reached
		
	def get(self,new_value):
		##dependent to the size of the cluster (v = old + (new-old)/size_cluser))
		if self.quantity < self.maxQuantity:
			self.quantity += 1
		self.value += (new_value - self.value) / self.quantity

			
			

class derivate:
	
	def __init__(self):
		pass#Ableitung ... wie  mean nur, dass dazu ein weiterer wert betrachet wird



