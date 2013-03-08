# -*- coding: utf-8 *-*

import numpy
from sys import exit
#import os
from copy import deepcopy
from diaGrabber import _utils
from scipy.interpolate import griddata

class _matrix(object):

	def __init__(self, sourceClass):

		self.sourceClass = sourceClass
		self.basis_dim = self.sourceClass.basis_dim
		self.merge_dim = self.sourceClass.merge_dim
		try:
			self.nMerge = len(self.merge_dim)
		except(TypeError):
			exit("ERROR: 'merge_dim' has to be a list")
		#self.derivate_dim = derivate_dim
		self.plot_overlay = []
		try:
			self.nDim = len(self.basis_dim)
		except(TypeError):
			exit("ERROR: 'basis_dim' has to be a list")
		self.plot_overlay = []
		for i in range(len(self.merge_dim)):
			#every merge-dim has its on plot-overlay
			self.plot_overlay.append([[], [], [], [], [], [],[]])
		#plot_overlay = [(points), (lines), (broken lines), , (ellipses), (rectangles), (text), (legend)]
			#(points),(broken lines), (lines)  = [x-list,y-list]
			#(ellipses) = list[ tuple(x,y), float(width), float(height), float(angle) ) ## str(color) ]
			#(rectangles) = list[ tuple(x,y), float(width), float(height) ]
			#(text) = list[ tuple(x,y), string(text)
			#Llegend) = list[str(...),... ]

		#self.readOut_prepared = False
		sourceClass._prepareReadOut(self)

		self._build()
		#if plotClass:#start showing window
			#plotClass.show()
		#self.mergeMatrix, self.densityMatrix = sourceClass._readOut(self)
		#sourceClass._readOut(self)

		
	def _build(self):
		#empty matrix
		matrix_str = "numpy.zeros(shape=("
		for i in range(len(self.basis_dim)):
			if self.basis_dim[i].resolution <= 0:
				exit("ERROR: to build a matrix you need to set a number for %s.resolution" %self.basis_dim[i].name)
			matrix_str += "%s," %self.basis_dim[i].resolution
		matrix_str += "))"
		self.densityMatrix = []
		for i in range(self.nMerge):
			self.densityMatrix.append(eval(matrix_str))
		self.mergeMatrix = deepcopy(self.densityMatrix)
		for i in range(self.nMerge):
			self.mergeMatrix[i].fill(numpy.nan)

		self._checkMinMax(self.basis_dim, self.nDim)

		self.sortMatrix = []
		for i in range(len(self.basis_dim)):
			self.sortMatrix.append(self.basis_dim[i]._sort_range)



	def _assign(self, basis_values, merge_values):
		self._getPositionsIntensities(basis_values)
		
					#positionsIntensities = self.matrixClass._assign(self.basis_values)
		for position, intensity in self.positionsIntensities:
			tPostion = tuple(position)
			for m in range(self.nMerge):
				(replace_value, do_replace)= self.merge_dim[m]._mergeMethod._get(merge_values[m],
					self.mergeMatrix[m][tPostion],self.densityMatrix[m][tPostion],intensity)
				if do_replace:
					self.mergeMatrix[m][tPostion] = replace_value
					self.densityMatrix[m][tPostion] += intensity




	def _checkMinMax(self,basis_dim, nDim):
		##get minMax-range for all unlimited dimensions
		get_MinMax_values = []
		dims = []
		dim_names = []
		for i in range(nDim):
			if basis_dim[i]._take_all_values:
				dims.append(basis_dim[i])#.index)
				dim_names.append(basis_dim[i].name)
		if len(dims) > 0:
			print "...getting range for dims %s" %dim_names
			min_max = self.sourceClass._getMinMax(dims)
			j = 0
			for i in range(nDim):
				if basis_dim[i]._take_all_values:
					basis_dim[i]._include_from_to = min_max[j]
					basis_dim[i]._initSortRange()
					j+=1
					print "set range for %s to %s" %(basis_dim[i].name,
						basis_dim[i]._include_from_to)


	def fill(self):
		print "reading out file %s" %self.sourceClass.file_name
		self.sourceClass._readOut(False, False)
		print "done"

	def _fillInteractive(self, end_readOut):
		return self.sourceClass._readOut(True, end_readOut)
		



	def save(self, file_name, folder_name = "", save_type = "bin"):
		print "saving matrix ..."
		file_name = _utils.prepareFileSystem(file_name, folder_name)
		if save_type == "bin":
			
			for i in range(self.nMerge):
				f = "%s_%s_merge" %(file_name, self.merge_dim[i].name)
				numpy.save(f, self.mergeMatrix[i])
				print "created binary-file %s" %f

				f = "%s_%s_density" %(file_name, self.merge_dim[i].name)
				numpy.save(f, self.densityMatrix[i])
				print "created binary-file %s" %f
			f = "%s_basis" %(file_name)
			numpy.save(f, self.sortMatrix)
			print "created binary-file %s" %f

		else:
		#def txt(self):
			for i in range(self.nMerge):

				f = "%s_%s_merge" %(file_name, self.merge_dim[i].name)
				numpy.savetxt(f, self.mergeMatrix[i], fmt = "%10.5f")
				print "created txt-file %s" %f
			#f = file_name + "_sort"
			#exit("ERROR: save-txt doesnt work for sortMatrix at the moment")
			#numpy.savetxt(f, numpy.array(self.sortMatrix), fmt = "%10.5f")
			#print "created txt-file %s" %f
				f = "%s_%s_density" %(file_name, self.merge_dim[i].name)
				numpy.savetxt(f, self.densityMatrix[i], fmt = "%10.5f")
				print "created txt-file %s" %f


	def load(self, file_name, folder_name = "", load_type = "bin"):
		print "loading matrix"


		file_name = _utils.prepareFileSystem(file_name, folder_name)


		if load_type == "bin":
		#def bin(self):
			self.mergeMatrix = []
			self.sortMatrix = []
			self.densityMatrix = []
			
			for i in range(self.nMerge):
				f = "%s_%s_merge.npy" %(file_name, self.merge_dim[i].name)
				self.mergeMatrix.append(numpy.load(f))
				print "loaded binary-file %s" %f
				f = "%s_%s_density.npy" %(file_name, self.merge_dim[i].name)
				self.densityMatrix.append(numpy.load(f))
				print "loaded binary-file %s" %f
			f = f = "%s_basis.npy" %(file_name)
			self.sortMatrix = numpy.load(f)
			print "loaded binary-file %s" %f
			
		else:
			exit("ERROR: load.txt is not implemented")

		for i in range(len(self.basis_dim)):
			if self.basis_dim[i]._take_all_values:
				#define range for _include_from_to from loaded sortMatrix
				self.basis_dim[i]._include_from_to = [min(self.sortMatrix[i]),max(self.sortMatrix[i])]
				self.basis_dim[i]._take_all_values = False
				print self.basis_dim[i]._include_from_to


	def interpolate(self, method = "nearest"):
		'''interpolate NaNs in matrix; method="nearest", "linear", "cubic"'''
		print "interpolate matrix with method '%s'" %method
		#build a nD-meshgrid in which the interolation can be solved
		nDgrid = self.multiDimMeshgrid()
		#extract points from matrix
		points,merge = self.transformMatrixToPoints(nDgrid)
		#merge a dim-lists to a vector-list
			#--> X(1,2,3) Y(4,5,6) -> XY([1,4],[2,5],[3,6])
		#print points
		pointsT = zip(*points)
		#pointsT = numpy.vstack(tuple(points)).transpose()
		#do the interpolation
		print "do interpolation"
		#print pointsT
		for i in range(self.nMerge):
			#pointsT = zip(*points[i])
			#print pointsT
			self.mergeMatrix[i] = griddata(pointsT, merge[i], tuple(nDgrid), method)
		print "done"


	def transformMatrixToPoints(self, givenMultiDimMeshgrid = None):
		'''transform all not-empty parts of a  matrix to discrete points'''
		print "transform marix-indices to discrete points"
		
		if givenMultiDimMeshgrid:
			#print 111, givenMultiDimMeshgrid
			pointsi = deepcopy(givenMultiDimMeshgrid)
		else:
			pointsi = self.multiDimMeshgrid()

		#X,Y = numpy.meshgrid(sortMatrix[0],sortMatrix[1])
		for i in range(self.nDim):
			#transform to list - necassary when removing NaNs via list.pop()
			pointsi[i] = list(pointsi[i].flatten())
		points = []
		merge = []
		
		for i in range(self.nMerge):
			#points.append(deepcopy(pointsi))
			merge.append(list(deepcopy(self.mergeMatrix[i]).flatten()))
		j = 0
		
		#print i, self.nMerge, len(merge), merge[0]
		while j < len(merge[0]):
			#remove point if merge == nan
			if numpy.isnan(merge[0][j]):
				for i in range(self.nMerge):
					merge[i].pop(j)
				for k in range(self.nDim):
					#print i,k,j, len(points[i][k]), len(merge[i])
					pointsi[k].pop(j)
				j -= 1
			j += 1
		print "done"

		return pointsi, merge


	def multiDimMeshgrid(self):
		'''like numpy.meshgrid but can also produce multi-dimensional meshgrids
		takes  list of arrays, where len(list)=nDim'''
		
		print "create a multiDimMeshgrid"
		sortMatrix = list(self.sortMatrix)#if type(sortMatrix)=array an error will be produced in numpy.repeat
		sortMatrix.reverse()
		
		lenDim = []
		#nDim = len(sortMatrix)
		newShape = [self.nDim]
	
		for i in sortMatrix:
			lenDim.append(len(i))
		lenDimrev = deepcopy(lenDim)
		lenDimrev.reverse()
		newShape.extend(lenDimrev)
		
		for i in range(self.nDim):
			if i==0:
				nRepeat = 1
			else:
				nRepeat = lenDim[i-1]
				lenDim[i]*=nRepeat
			#double items
			sortMatrix[i] = sortMatrix[i].repeat(nRepeat)
	
		lenGrid = len(sortMatrix[-1])
		for i in range(self.nDim):
			#repeate blocks
			sortMatrix[i] = numpy.lib.stride_tricks.as_strided(
				sortMatrix[i], (lenGrid/len(sortMatrix[i]),)+sortMatrix[i].shape, (0,)+sortMatrix[i].strides).flatten()
			
		#reshape blocks
		sortMatrix = numpy.array(sortMatrix)#reshape need an array
		print "done"
		return list(sortMatrix.reshape(tuple(newShape)))


	def eval2dGaussianDistribution(self, dEB_types=[], which_merge_dim = 0):
		print "eval2dGaussianDistribution"
		if self.nDim != 2:
			exit("ERROR: eval2dGaussianDistribution works only for 2d-matrixes")
		min_dEB_types = [0.25,0.5,0.75]#are at least necassary to get deviation to normaldistr.
		for i in min_dEB_types:
			if i not in dEB_types:
				dEB_types.append(i)#important to the the standard deviation
			
		#from smalles to biggest diameter
		dEB_types.sort()
		dEB_types.reverse()#e.q.d_EB_75, d_EB_50, d_EB_25
		dEB_types.insert(0,0.95)
		
		w = int(which_merge_dim)
		
		peak = numpy.nanmax(self.mergeMatrix[w])
		peak_location = list(numpy.where(self.mergeMatrix[w]==peak))
		peak_location[0] = peak_location[0][0]
		peak_location[1] = peak_location[1][0]
		#print peak_location, len(sortMatrix[0]),len(sortMatrix[1])
		
		environment = 0#approximated
		dEB_limit = []
		dEB = []
		border_locations = []
		deviationTh2RealList = []
		
		for i in range(len(dEB_types)):
			dEB_limit.append((peak-environment)*dEB_types[i])
			dEB.append(numpy.nan)
			border_locations.append([])
			deviationTh2RealList.append(0)
			
		n_circle_points = 40#has to be int(multiple of 2)
		n_part_diameters = n_circle_points/2
		
		delta_radian = 2*numpy.pi / n_circle_points
		
		for d in range(len(dEB_limit)):
			radian = 0.0
			for i in range(n_circle_points):
				n = 0#at peak_location
				at_border = False
				while not at_border:
					x = peak_location[0] + int(n*numpy.cos(radian))
					y = peak_location[1] + int(n*numpy.sin(radian))
					
					
					if self.mergeMatrix[w][x][y] < dEB_limit[d]:#found border
						at_border = True
						if [x,y] not in border_locations[d]:
							border_locations[d].append([x,y])
					n += 1
				radian += delta_radian
		
		#reset the middle of the gaussiandistr. as the middle of the first (95%) polygon
		polygon = zip(*border_locations[0])
		peak_location[0] = int(sum(polygon[0])/len(polygon[0]))
		peak_location[1] = int(sum(polygon[1])/len(polygon[1]))
		peak_coord = [ self.sortMatrix[0][peak_location[0]], self.sortMatrix[1][peak_location[1]] ]


		##calc the x-y-coord of all borders in d_EB_types
		##and the distance from eBeammiddle to border
		border_coords = deepcopy(border_locations)
		distances = deepcopy(border_locations)
		print "Gausian-Diameters are..."
		for d in range(1,len(dEB_limit)):
			for i in range(len(border_locations[d])):
				border_coords[d][i] = [self.sortMatrix[0][border_locations[d][i][0]],
										self.sortMatrix[1][border_locations[d][i][1]]]
				distances[d][i] = _utils.pktAbs2(border_coords[d][i],peak_coord)

			#values for dEB_types[i]
			dEB[d] = sum(distances[d]) / len(distances[d])#mean
			if dEB_types[d] == 0.50:
				st_deviation = dEB[d]
			print "    for %s -> %s" %(dEB_types[d],dEB[d])

		
		##get max/min diameter-factor and the radian(max_diameter) for each d_EB-area
		minMax_dEB = []
		for d in range(len(dEB_limit)-1):#for each diameter
			minMax_dEB.append([None,None,None,None])#min, max, max/min, radian_of_max
			for i in range(n_part_diameters):
				# == radius + radius in opposite dir.
				part_diameter = distances[d+1][i] + distances[d+1][i+n_part_diameters]
				#print minMax_dEB, d
				if part_diameter < minMax_dEB[d][0] or minMax_dEB[d][0] == None:#min
					minMax_dEB[d][0] = part_diameter
				if part_diameter > minMax_dEB[d][1]  or minMax_dEB[d][1] == None:#max
					minMax_dEB[d][1] = part_diameter
					minMax_dEB[d][3] = delta_radian * i
			minMax_dEB[d][2] = minMax_dEB[d][1] / minMax_dEB[d][0] #max/min
		#get mean max/min-factor and mean radian_of_max
		mean_maxMin_dEB = 0
		mean_max_radian = 0
		for d in range(len(dEB_limit)-1):#for each diameter
			mean_maxMin_dEB += minMax_dEB[d][2]
			mean_max_radian += minMax_dEB[d][3]
		mean_maxMin_dEB /= (len(dEB_limit)-1)
		mean_max_radian /= (len(dEB_limit)-1)
		print "The mean factor max/min-diameter is %s" % mean_maxMin_dEB
		print "The mean radian of the max diameter is %s" % mean_max_radian

		#calc deviation to a normaldisribution defined as:
		#normal_distribution_fn = \
		corrF = 1/ (
					1/(st_deviation* ((2*numpy.pi)**0.5) ) ) * numpy.e**(-0.5 *
					( ( 0 /  st_deviation)**2 ) ) * (peak-environment)
		for d in range(1,len(dEB_limit)):
			for x in distances[d]:
				dEB_th = corrF * (
					1/(st_deviation* ((2*numpy.pi)**0.5) ) ) * numpy.e**(-0.5 *
					( ( x /  st_deviation)**2 ) ) * (peak-environment)

				deviationTh2RealList[d] += abs( (dEB_th - dEB_limit[d]) / dEB_th)#dEB_limit[d]/dEB_th#
			deviationTh2RealList[d] /= (len(distances[d])-1) #middle fo difference between theory and reality
		##middle of all deviantion-rings
		relDevianceTh2Real = sum(deviationTh2RealList) /  ( len(deviationTh2RealList))
		print "The relative deviation/variance between theoretical an real distribution is %s" %relDevianceTh2Real

		#add point middle of gaussian:
		self.plot_overlay[w][0].append(tuple(peak_coord))
		self.plot_overlay[w][6].append("Mittelpunkt")#x-,y-list

		self.plot_overlay[w][5].append("deviation= %s" %relDevianceTh2Real)
		self.plot_overlay[w][5].append("maxRad= %s" %mean_max_radian)
		self.plot_overlay[w][5].append("max/min-d-factor= %s" %mean_maxMin_dEB)
		#add rings
		for d in range(1,len(dEB_limit)):
			self.plot_overlay[w][1].append(zip(*border_coords[d]))#x-,y-list
			self.plot_overlay[w][6].append("d_EB= %s" %(dEB_types[d]) )#x-,y-list


		print "done"

	def transformDim(self, rebuild_matrix = True):
		#transform old sortMatrix
		some_dim_transformed = False
		for i in range(self.nDim):
			if self.basis_dim[i].transform:
				some_dim_transformed = True
				for j in range(len(self.sortMatrix[i])):
					self.sortMatrix[i][j] = self.basis_dim[i].transform.get(self.sortMatrix[i][j])
				self.basis_dim[i].name = self.basis_dim[i].transform.name

		##change dimension-name and -range
		#for i in range(self.nDim):
			#if self.basis_dim[i].transform:
			#transfrom range in includeFromTo
				for j in range(2):
					self.basis_dim[i]._include_from_to[j] = \
					self.basis_dim[i].transform.get(self.basis_dim[i]._include_from_to[j])
			
		##build discrete points from given matrix, and
		if rebuild_matrix and some_dim_transformed:
			points, merge = self.transformMatrixToPoints()
			for m in range(self.nMerge):
				points.reverse()
				##transform merge points
				if self.merge_dim[m].transform:
					for i in range(len(merge[m])):
						merge[m][i] = self.merge_dim[m].transform.get(merge[m][i])
					self.merge_dim[m].name = self.merge_dim[m].transform.name
				##..build new matrix from those discrete and transformed points
			self.transformPointsToMatrix(points, merge)


	def transformPointsToMatrix(self, points, merge):
		self._build()#get new merge- sort-, densityMatrix
		points = zip(*points)
		for m in range(self.nMerge):
			#points[m] = zip(*points[m])
			for i in range(len(points)):
				#print points[i]
				self._getPositionsIntensities(points[i])
				for position, intensity in self.positionsIntensities:
					tPostion = tuple(position)
					(replace_value, do_replace)= self.merge_dim[m]._mergeMethod._get(merge[m][i],
						self.mergeMatrix[m][tPostion],self.densityMatrix[m][tPostion],intensity)
					if do_replace:
						self.mergeMatrix[m][tPostion] = replace_value
						self.densityMatrix[m][tPostion] += intensity
			



class coarseMatrix(_matrix):
	
	def __init__(self, sourceClass):
		super(coarseMatrix, self).__init__(sourceClass)
		#self.basis_dim = basis_dim
		self.positionsIntensities = [[[ ],1]]#intensity in every time =1 because thers no splitting
		for i in range(self.nDim):
			self.positionsIntensities[0][0].append(0)
						
	def _getPositionsIntensities(self, basis_values):
		
		for i in range(self.nDim):
			difference_list = self.sortMatrix[i] - basis_values[i]
			difference_list = abs(difference_list)
			nearest_point = difference_list.argmin()
			self.basis_dim[i]._recent_position = nearest_point
			self.positionsIntensities[0][0][i] = nearest_point
		#return self.positionsIntensities

		#positionsIntensities = self._getPositionsIntensities(basis_values)


class fineMatrix(_matrix):
	'''
	This class isn't as fast as :class:`coarseMatrix` but can assign values
	in a more accurate way if the following condition is fullfilled:
.. note:: number of datapoints in matrix>> matrix-resolution
+---------+---------+-----------+
| 1       |  2      |  3        |
+---------+---------+-----------+
| 4       |  5      |  6        |
+---------+---------+-----------+
| 7       |  8      |  9        |
+---------+---------+-----------+
	'''
	def __init__(self, sourceClass):
		super(fineMatrix, self).__init__(sourceClass)
		#self.basis_dim = basis_dim
		self.positionsIntensities = [[[ ],1]]
		self.anzAffectedCells = 2**self.nDim
		self.affectedCellCounter =  []
		for i in range(1,self.nDim+1,1):
			self.affectedCellCounter.append((2**i/2) -1)
		
		for i in range(self.nDim):
			self.positionsIntensities[0][0].append(0)

		for i in range(self.anzAffectedCells-1):
			#1D: 2 cells
			#2D: 4 cells
			#3D: 8 cells
			self.positionsIntensities.append(deepcopy(self.positionsIntensities[0]))
			
	def _getPositionsIntensities(self, basis_values):
		
		for i in range(self.anzAffectedCells):#reset intensities (later there is a *=)
			self.positionsIntensities[i][1] = 1
		
		for i in range(self.nDim):
			difference_list = self.sortMatrix[i] - basis_values[i]
			difference_list = abs(difference_list)
			nearest_point = difference_list.argmin()
			self.basis_dim[i]._recent_position = nearest_point
			if nearest_point == 0:#is first point of array - neared point is seond point
				sec_nearest_point = 1
			elif nearest_point == difference_list.size-1:#is last point of array
				sec_nearest_point = difference_list.size-2
			else:##whose of the neigbours is closer
				if difference_list[nearest_point-1] < difference_list[nearest_point+1]:
					sec_nearest_point = nearest_point-1
				else:
					sec_nearest_point = nearest_point+1
			#sec_nearest_point get some of the intensity of the nearest point
			transfered_intensity = (difference_list[sec_nearest_point]-
				difference_list[nearest_point]) / difference_list[sec_nearest_point]
				
			n = 0
			write_point = nearest_point
			nearest_intensity = 1 - transfered_intensity
			sec_nearest_intensity = transfered_intensity
			intensity = nearest_intensity
			for j in range(self.anzAffectedCells):
				self.positionsIntensities[j][0][i] = write_point
				self.positionsIntensities[j][1] *= intensity

				if n == self.affectedCellCounter[i]:
					if write_point == nearest_point:
						write_point = sec_nearest_point
						intensity = sec_nearest_intensity
					else:
						write_point = nearest_point
						intensity = nearest_intensity
					n = -1
				n += 1
		
		#return self.positionsIntensities


