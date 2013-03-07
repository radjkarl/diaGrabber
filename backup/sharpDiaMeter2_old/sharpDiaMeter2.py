# -*- coding: utf-8 -*-

#FOREIGN
import os
import distutils
import math
import subprocess
from distutils import dir_util
from sys import exit
import numpy
import matplotlib.pyplot as plt
from copy import deepcopy
import linecache
#from mpl_toolkits.mplot3d import Axes3D ##later for 3d stuff


#OWN
import sharpDiaMeter2Dict
from sharpDiaMeter2Dict import *
from src.utils import statusBar




def main():
	#create analyzed-folder
	if os.path.isdir("../analyzed") == False:
		os.mkdir("../analyzed")

	for i in which_class:
		#create class-folder
		optionClass = eval(i)
		if os.path.isdir("../analyzed/" + optionClass.__name__) == False:
			os.mkdir("../analyzed/" + optionClass.__name__)
		if optionClass.file_type == "bnArray":
			p = bnArray(optionClass)
		else:
			p = plainTxt(optionClass)
			p.buildMatrix()
			p.readOut()

		numpy.save("../analyzed/" + optionClass.__name__ + "/bnArray",
			p.matrix)
		numpy.savetxt("../analyzed/" + optionClass.__name__ + "/txtArray",
			p.matrix, fmt = "%10.5f")
		
		###plotting
		fig = plt.figure()
		#2D
		if p.nDim == 2:
			image = plt.imshow(p.matrix)
			image.set_interpolation('nearest')
			cBar = plt.colorbar()#colorbar(ticks=[min(data2[:,2]),max(data2[:,2])])
			#cBar.set_ticks(['Low','High'])
			cBar.set_label(optionClass.fill_matrix_with.name)
			plt.xlabel(optionClass.middle_over[0].name)
			plt.ylabel(optionClass.middle_over[1].name)

			##transform sort_values to viewable axis-values
			axis_values = getAxisValues(p,optionClass)
			plt.xticks( range(optionClass.matrix_resolution), axis_values[0])
			plt.yticks( range(optionClass.matrix_resolution), axis_values[1])

		#1D
		elif p.nDim == 1:
			plt.plot(p.matrix)
			plt.ylabel(optionClass.fill_matrix_with.name)
			plt.xlabel(optionClass.middle_over[0].name)
			axis_values = getAxisValues(p,optionClass)
			plt.xticks( range(optionClass.matrix_resolution), axis_values[0])
			#plt.yticks( range(optionClass.matrix_resolution), axis_values[1])
			
		else:
			exit(NotImplemented)

		#set bg color
		fig.patch.set_facecolor('white')
			#fig.patch.set_alpha(0.7)

		#save
		fig.savefig("../analyzed/" + optionClass.__name__ + '/figure.png',
			facecolor=fig.get_facecolor(), edgecolor='none')

	if 	optionClass.plot_to_screen:
		plt.show()



def getAxisValues(p,optionClass):
	##transform sort_values to viewable axis-values
	axis_values = []
	steps = int(optionClass.matrix_resolution/5)
	for i in range(p.nDim):
		axis_values.append([])
		n = steps
		for j in range(optionClass.matrix_resolution):
			if n == steps:
				axis_values[i].append('{0:.1g}'.format(p.matrix_sort_values[i][j]))
				n = 0
			else:
				axis_values[i].append("")
				n += 1
	return axis_values



###############################
class bnArray(object):
	def __init__(self,object):
		#object.__init__(self)
		self.oc = object
		self.matrix = numpy.load(self.oc.file_name)
		self.nDim = self.matrix.ndim


class plainTxt(object):

	def __init__(self,object):
		self.oc = object
		self.len_dat_file = len(file(self.oc.file_name, "r").readlines())
		self.nDim = len(self.oc.middle_over)
		pass

	def getMinMax(self,dims):
		#dat_file = file(self.oc.file_name, "r").readlines()
		#min_value, max_value = 1e100,-1e100
		minMax = []#deepcopy(dims)
		len_dims = len(dims)
		for i in range(len_dims):
			minMax.append([None,None])#min,max #####besser wert aus datei
		for i in range(0,self.len_dat_file,self.oc.readout_every_n_line):
			line = linecache.getline(self.oc.file_name, i+1)
		#for line in dat_file:
			for d in range(len_dims):
				#print line, dims, d
				value = eval(line[:-2].split(self.oc.categories_separation)[dims[d]])
				if minMax[d][1] == None or value > minMax[d][1]:#max
					minMax[d][1] = value
				if minMax[d][0] == None or value < minMax[d][0]:#min
					minMax[d][0] = value
					#print 4
				#print minMax[d][0],minMax[d][0] == None,value
		return minMax

	def buildMatrix(self):
		#empty matrix
		matrix_str = "numpy.zeros(shape=("
		for i in range(len(self.oc.middle_over)):
			matrix_str += "self.oc.matrix_resolution,"
		matrix_str += "))"
		self.matrix = eval(matrix_str)
		##empty matrix for number of sorted values
		self.anzValues_matrix = eval(matrix_str)
		##get minMax-range for all unlimited dimensions
		get_MinMax_values = []
		dims = []
		dim_names = []
		for i in range(len(self.oc.middle_over)):
			if self.oc.middle_over[i].take_all_values:
				dims.append(self.oc.middle_over[i].index)
				dim_names.append(self.oc.middle_over[i].name)
		if len(dims) > 0:
			print "...getting range for dims %s" %dim_names
			minMax= self.getMinMax(dims)
			for i in range(len(self.oc.middle_over)):
				if self.oc.middle_over[i].take_all_values:
					self.oc.middle_over[i].include_from_to = minMax[i]
				print "set range for %s to %s" %(self.oc.middle_over[i].name,
					self.oc.middle_over[i].include_from_to)
		#build matring for all sort-values
		matrix_sort_values_str = "numpy.array(["
		for i in range(len(self.oc.middle_over)):
			matrix_sort_values_str += """numpy.linspace(self.oc.middle_over[%s].include_from_to[0], \
			self.oc.middle_over[%s].include_from_to[1],\
			self.oc.matrix_resolution), """ %(i,i)
		matrix_sort_values_str += "])"
		self.matrix_sort_values = eval(matrix_sort_values_str)




	def readOut(self):
		#dat_file = open(self.oc.file_name, "r")
		#dat_file.close()
		values = []
		for i in range(self.nDim):
			values.append(0)
		positions0 = deepcopy(values)
		n = 0
		showBar_counter = self.len_dat_file / (self.oc.readout_every_n_line * 100)
		bar_step = 0
		for i in range(0,self.len_dat_file,self.oc.readout_every_n_line):
			line = linecache.getline(self.oc.file_name, i+1)
			file_dim = line[:-2].split(self.oc.categories_separation)
			#print file_dim
			matrix_value = eval(file_dim[self.oc.fill_matrix_with.index])
			for c in self.oc.fill_matrix_with.calc:
				c.get(matrix_value)
				print c.value, c.quantity
			
			in_range = True
			
			for dim in range(self.nDim):
				#get vlues from line
				values[dim] = eval(file_dim[self.oc.middle_over[dim].index])
				#are values in range
			 	if self.oc.middle_over[dim].include_from_to[0] > values[dim] or \
					self.oc.middle_over[dim].include_from_to[1] < values[dim]:
						in_range = False
				#calc values bounded to dim
				#print self.oc.middle_over[dim].calc, self.oc.middle_over[dim].name
				for c in self.oc.middle_over[dim].calc:
					c.get(values[dim])
					#print c.value
					
			
			if in_range:
				
				positions = assignDiscrete(self.matrix_sort_values,values,positions0,self.nDim)
				self.anzValues_matrix[positions] += 1
					##middle the basis_clustered to the new basis values
					##dependent to the size of the cluster (v = old + (new-old)/size_cluser))
				self.matrix[positions] += (matrix_value - self.matrix[positions]) /self.anzValues_matrix[positions]
			#print i, self.len_dat_file#, line
			if n == showBar_counter:
				bar_step += 1
				statusBar(bar_step,100, 20)
				n = 0
			n+= 1
		return self.matrix


def assignDiscrete(matrix_sort_values,values,positions, nDim):
	for i in range(nDim):
		difference_list = matrix_sort_values[i] - values[i]
		difference_list = abs(difference_list)
		positions[i] = numpy.where(difference_list==min(difference_list))[0][0]
	return tuple(positions)
		


#################

main()
