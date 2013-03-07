# -*- coding: utf-8 *-*
#class _transform(object):
	
def __init__(self):
	pass
	

class fx(object):
	def __init__(self,fx_str, name):
		'''e.g. fn_str = 3x/2'''
		self.fn_str = fx_str
		self.name = name

		#_dimension.__init__(self)
		
	def get(self,x):
		return eval(self.fn_str)



class interpolationTable(object):
	def __init__(self,source_l, name):
		self.source_l = source_l
		self.name = name
		self._get

		#_dimension.__init__(self)

	def get(self,time):
		"""
	conform to the openFoam-class of the same name
	print an linear-interpolated value to a given time[float]
	source_l = [ [time1,value1], ... , [timeN,valueN] ]
	"""
		if time <= self.source_l[0][0]:#fist given time
			return self.source_l[0][1]#first given value
		elif time >= self.source_l[-1][0]:#last given time
			return self.source_l[-1][1]#last given value
		else:
			for i in range(1,len(self.source_l),1):##for all values exept fist and last one
				if time == self.source_l[i][0]:#time-i
					return self.source_l[i][1]#value of time-i
				elif time < self.source_l[i][0]:#time-i
					##do a linear interpolation betwen this an the last value
					delta_time1 = self.source_l[i][0]-self.source_l[i-1][0]
					delta_time2 = time-self.source_l[i-1][0]
					delta_value = self.source_l[i][1]-self.source_l[i-1][1]
					return self.source_l[i-1][1] + delta_value * (delta_time2 / delta_time1 )


