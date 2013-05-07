# -*- coding: utf-8 *-*
'''
The transform-module include classes to transform values and units.
'''

class fx(object):
	'''
	Get y-values from given f(x)-functions.
	
	:param source_l: some function  e.q. **"3x/2"**
	:type source_l: string
	:param name: name of the y-dimension
	:type name: string
	'''
	def __init__(self,fx_str, unit):
		self.fn_str = str(fx_str)
		self.unit = str(unit)

	def get(self,x):
		'''
		transform 'x' through evaluation of the given fn-string.
		Note that this is the slowest method of transformation.
		'''
		return eval(self.fn_str)


class linear(object):
	'''
	Get y-values from given f(x)-functions.
	
	:param source_l: some function  e.q. **"3x/2"**
	:type source_l: string
	:param name: name of the y-dimension
	:type name: string
	'''
	def __init__(self,factor, offset, unit):
		self.factor = float(factor)
		self.offset = float(offset)
		self.unit = str(unit)

	def get(self,x):
		'''
		return y = factor * x + offset
		'''
		return self.factor*x + self.offset


class interpolationTable(object):
	'''Get y-values from given (also unsorted) point(x,y) values.
	Do a linear interpolation between given points and extrapolate with the first and last y-value. This class in analoque the the openFOAM-class of the same name.
	
	:param source_l: list of discrete foat-point values e.q.::

		[[0,1],
		[2,3],
		[10,2]]

	:type source_l: list
	:param name: name of the y-dimension
	:type name: string
	'''
	def __init__(self,source_l, unit):
		self.source_l = list(source_l)
		self.source_l.sort()
		self.unit = str(unit)

	def get(self,x):
		"""
		return a linear interpolated value between given
		points. Return the last/fist given values for all 'x' aboth/beneath the border
		"""
		if x <= self.source_l[0][0]:#fist given time
			return self.source_l[0][1]#first given value
		elif x >= self.source_l[-1][0]:#last given time
			return self.source_l[-1][1]#last given value
		else:
			for i in range(1,len(self.source_l),1):##for all values exept fist and last one
				if x == self.source_l[i][0]:#time-i
					return self.source_l[i][1]#value of time-i
				elif x < self.source_l[i][0]:#time-i
					##do a linear interpolation betwen this an the last value
					delta_x1 = float(self.source_l[i][0]-self.source_l[i-1][0])
					delta_x2 = x-self.source_l[i-1][0]
					delta_value = self.source_l[i][1]-self.source_l[i-1][1]
					return self.source_l[i-1][1] + delta_value * (delta_x2 / delta_x1 )


