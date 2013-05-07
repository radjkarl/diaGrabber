# -*- coding: utf-8 *-*
import numpy as np
import bottleneck as bn
from sys import exit
from copy import deepcopy
from scipy.interpolate import griddata
#own modules
from diaGrabber import _utils
from diaGrabber.source._dimension import mergeDimension, basisDimension


class matrixMethods(object):
	'''
	This class includes a list of methods inherited (and hence callable)
	by all matrix-like targets.
	'''
	
	def __init__(self):
		pass

	def autoZoom(self, **kwargs):
		'''
		**Required kwargs** ("keyword arguments") are:

		==================     ===============  =============    ================
		Keyword	               Type             Example          Description
		==================     ===============  =============    ================
		*mergeName*            str              myMergeName      the name of the merge-dim to do the method on
		*value*                float/string     *max*            The merge-value to zoom in. Type 'min' or 'max' to use the equivalent extrem-value in the matrix
		*scale*                string           *'relative'*
		                                        **OR**
		                                        *'absolute'*
		*level*                float            0.3              The relative zoom-level
		                                                         0.3 means +-30% around the zoom-point
		==================     ===============  =============    ================

		**Optional kwargs** ("keyword arguments") are:

		==================     =================  ============    ================
		Keyword	               Type               Default         Description
		==================     =================  ============    ================
		*basisNames*           list(basisNames)   [{all}]         Which basisDimensions get a new scale.
		*operator*             string             "=="            The zoom-point is defined as the first point in matrix where a value in "==" (equal), ">" (bigger) etc. than the given *value*
		==================     =================  ============    ================
		'''

		#standard
		mergeDim = None
		value=None
		scale=None
		level=None
		operator = "=="
		basisDim = range(self.nBasis)
		#individual
		for key in kwargs:
			if key == "mergeName":
				if kwargs[key] not in self.mergeNames:
					raise KeyError("ERROR: mergeName %s not known" %m)
				mergeDim =  self.mergeNames.index(kwargs[key])
			elif key == "value":
				if type(kwargs[key]) == str:
					if kwargs[key] != "max" and kwargs[key] != "min":
						exit("ERROR: 'value' can only be 'max', 'min' or a float")
					value = kwargs[key]
				else:
					value = str(kwargs[key])
			elif key == "scale":
				if kwargs[key] != "absolute" and kwargs[key] != "relative":
					exit("ERROR: 'scale' in method 'autoZoom' has to be 'absolute' or 'relative'")
				scale = str(kwargs[key])
			elif key == "level":
				level = abs(float(kwargs[key]))
			elif key == "operator":
				operator = str(kwargs[key])
			elif key == "basisNames":
				basisDim = list(kwargs[key])
				for n,b in enumerate(basisDim):
					if b not in self.basisNames:
						exit("ERROR: the given basisDimension %s does not belong to those from target" %b)
					basisDim[n] = self.basisNames.index(b)
			else:
				raise KeyError("keyword '%s' not known" %key)

		_utils.checkRequiredArgs({
				"mergeName":mergeDim,
				"value":value,
				"scale":scale,
				"level":level})

		#which mergeMatrix is involved?
		m=self.mergeMatrix[mergeDim]
		#prepare value
		if value=="max":
			value = bn.nanmax(m)
		elif value=="min":
			value = bn.nanmin(m)

		if np.isnan(value):
			raise ValueError("cannot autoZoom to nan")
		#get position in matrix
		#try:
		positions=np.argwhere(eval(str(value) + operator + "m"))[0]
		print "\n... do autoZoom for basisDimensions at a mergeValue of %s" %value
		for n,p in enumerate(positions):
			if n in basisDim:
				#get basis-values at those positions
				zoompoint = self.basisMatrix[n][p]
				#calc. the new range
				if scale == "relative":
					basis_range = self._basis_dim[n]._include_range[1]-self._basis_dim[n]._include_range[0]

					zoomrange=[zoompoint-abs(basis_range*level),zoompoint+abs(basis_range*level)]
					ampl = zoomrange[1]-zoomrange[0]
				elif scale == "absolute":
					zoomrange=[zoompoint-level,zoompoint+level]
				#define a new include_range-range for that basisDim
				print "%s --> %s (offset: %s, amplitude: %s)" %(self._basis_dim[n].name,zoomrange, zoompoint, ampl)
				self._basis_dim[n]._includeRange(zoomrange)
			else:
				print "ignored %s for autozoom" %self._basis_dim[n].name

	def copyMerge(self, presentMergeName, newMergeName):
		'''
		copy an existent mergeDim, including its merge- and densityMatrix.
		Return the copied mergeDim
		'''
		#found_merge = False
		for n,merge in enumerate(self._merge_dim):
			if merge.name == presentMergeName:
				new_merge = deepcopy(merge)
				new_merge.name = str(newMergeName)
				self._merge_dim.append( new_merge )
				self.nMerge += 1
				self.mergeMatrix.append( deepcopy(self.mergeMatrix[n]) )
				self.densityMatrix.append( deepcopy(self.densityMatrix[n]) )
				self.mergeNames.append(str(newMergeName))

				#found_merge = True
				return new_merge
		#if not found_merge:
		raise AttributeError("presentMergeName '%s' does not exist" %presentMergeName)



	def interpolateFast(self, **kwargs):
		'''
		interpolate NaNs (empty points) in matrix using
		`scipy.interpolate.griddata <http://docs.scipy.org/doc/scipy/reference/generated/scipy.interpolate.griddata.html>`_.
		
		**Optional kwargs** ("keyword arguments") are:

		==================     ===============  =========    ================
		Keyword	               Type             Default      Description
		==================     ===============  =========    ================
		*mergeName*            list(mergeDim)   [{all}]      one or more merge-dims to do the method on
		*method*               str              'nearest'    {"nearest", "linear", "cubic"}
		==================     ===============  =========    ================
		'''
		#standard
		method = 'nearest'
		mergeNames = deepcopy(self.mergeNames)

		#individual
		for key in kwargs:
			if key == "mergeName":
				if type(kwargs[key]) != list and type(kwargs[key]) != tuple:
					kwargs[key] = [ kwargs[key] ]
				for m in kwargs[key]:
					if m not in self.mergeNames:
						raise KeyError("ERROR: mergeName '%s' not known" %m)
					mergeNames.append(m)
			elif key == "method":
				if kwargs[key] not in ["nearest", "linear", "cubic"]:
					raise KeyError("ERROR: method '%s' not known" %kwargs[key])
				else:
					method = kwargs[key]
			else:
				raise KeyError("keyword '%s' not known" %key)

		if method == "cubic" and self.nBasis > 2:
			method = "linear"
			print "method='cubic' works only for one and two basisDimensions"
		print "--> interpolate matrix with method '%s'" %method
		#build a nD-meshgrid in which the interolation can be solved
		nDgrid = self._multiDimMeshgrid()
		#do the interpolation
		print "do interpolation"
		for i in mergeNames:
			merge_index = self.mergeNames.index(i)
					#extract points from matrix
			points,merge = self.transformMatrixToPoints(nDgrid, merge_index)
			#merge a dim-lists to a vector-list
			#--> X(1,2,3) Y(4,5,6) -> XY([1,4],[2,5],[3,6])
			pointsT = zip(*points)
			try:
				self.mergeMatrix[merge_index] = griddata(pointsT, np.array(merge),
					tuple(nDgrid), method)
			except ValueError, exInstance:
				print "WARNING: interpolation of mergeMatrix %s FAILED because of:" %self._merge_dim[i].name
				print "    ValueError:",exInstance.args
				print "    continue with original values"
		print "done"




	def interpolateFine(self, **kwargs):
		'''
		interpolate NaNs (empty points) in matrix.
		In contrast to  :py:func:`interpolateFast` this function is comparatively slow.
		Therefore it can take a some minutes to finish interpolation on mergeMatrices that have reslutions > 30 in each basisDimension.
		However this function enables you to:
			
			* blurring between points (*focusExponent*). Thus it is possible to get smooth intersections between heavy scattered values.
			* extrapolate
			* limit the maximum interpolation/extrapolation distance (related to the unit of the chosen basisDimension)
			* weight distances in each basisDimension
		
		**Optional kwargs** ("keyword arguments") are:

		==================     ===============  =========    ================
		Keyword	               Type             Default      Description
		==================     ===============  =========    ================
		*mergeName*            list(mergeDim)   [{all}]      one or more merge-dims to do the method on
		*focusExponent*        float            10           blurring between points (sharpness will increase with increasing focusExponent)
		*evalPointDensity*     bool             True         weights the moments: 'moment = pointDensity*moment'
		*maxDistance*          dict             {None}       {basisName:maxDistance,..}
		*distanceFactor*       dict             {1}          {basisName:factor,..}
		==================     ===============  =========    ================
		
		.. math::
			moment = 1/distance^{focusExponent}
		
		'''
		#standard
		mergeNames = deepcopy(self.mergeNames)
		focus_exponent = 5
		eval_pointDesity = True
		max_interpolate_distance_dict = {}
		basis_distance_factor_dict = {}
		basis_distance_factor = []
		max_interpolate_distance =[]
		for b in self._basis_dim:
			max_interpolate_distance_dict[b.name] = None
			basis_distance_factor_dict[b.name] = 1
			max_interpolate_distance.append(None)
			basis_distance_factor.append(1)

		#individual
		for key in kwargs:
			if key == "mergeName":
				mergeNames = []
				if type(kwargs[key]) != list and type(kwargs[key]) != tuple:
					kwargs[key] = [ kwargs[key] ]
				for m in kwargs[key]:
					if m not in self.mergeNames:
						raise KeyError("ERROR: mergeName '%s' not known" %m)
					mergeNames.append(m)
			elif key == "method":
				if kwargs[key] not in ["nearest", "linear", "cubic"]:
					raise KeyError("ERROR: method '%s' not known" %kwargs[key])
				else:
					method = kwargs[key]
			elif key == "focusExponent":
					focus_exponent = float(abs(kwargs[key]))
			elif key == "evalPointDensity":
				eval_pointDesity = bool(kwargs[key])
			elif key == "maxDistance":
				for i in dict(kwargs[key]):
					if i not in max_interpolate_distance_dict.keys():
						raise KeyError("basisName '%s' in maxDistance not known" %i)
					max_interpolate_distance_dict[i] = kwargs[key][i]
			elif key == "distanceFactor":
				for i in dict(kwargs[key]):
					if i not in basis_distance_factor_dict.keys():
						raise KeyError("basisName '%s' in distanceFactor not known" %i)
					basis_distance_factor_dict[i] = kwargs[key][i]
			else:
				raise KeyError("keyword '%s' not known" %key)

		max_moment = 1 / ( 0.5 **focus_exponent )
		momentMatrix = deepcopy(self.mergeMatrix[0])

		#generate list from dict sorted via indices
		for i in basis_distance_factor_dict:
			for n,b in enumerate(self._basis_dim):
				if b.name == i:
					basis_distance_factor[n] = basis_distance_factor_dict[i]
		for i in max_interpolate_distance_dict:
			for n,b in enumerate(self._basis_dim):
				if b.name == i:
					max_interpolate_distance[n] = max_interpolate_distance_dict[i]
		#normalize distances
		sumB = float(sum(basis_distance_factor))
		for n in range(len(basis_distance_factor)):
			basis_distance_factor[n] /= sumB
		
		#prepare regarded-array-slice
		n_regarded_cells = []
		regarded_cell_range = []
		abs_max_interpolation_dist = 0
		pos_corr = []
		for n,b in enumerate(self._basis_dim):
			basis_distance_factor.append(1)
			if max_interpolate_distance[n] != None:
				cell_len = (b._include_range[1]-b._include_range[0]) / b.resolution
				nCells = int(max_interpolate_distance[n] /cell_len)
				if nCells == 0:
					nCells = 1
				n_regarded_cells.append(nCells)
				abs_max_interpolation_dist += nCells

			else:
				n_regarded_cells.append(1)#dummy
			regarded_cell_range.append(0)
			pos_corr.append(0)
		abs_max_interpolation_dist **= 0.5
		print abs_max_interpolation_dist
		try:
			for m in mergeNames:
				merge_index = self.mergeNames.index(m)
				print "--> interpolate matrix %s" %m
				mergeM = self.mergeMatrix[merge_index]
				new_mergeM = deepcopy(mergeM)
				densityM = self.densityMatrix[merge_index]
				status_counter = 0
				next_status = int(mergeM.size/100)
				
				#len_matrix = len(mergeM)
				for nPoi, poi in enumerate(np.ndindex( mergeM.shape ) ):
					for n,b in enumerate(self._basis_dim):
						# only work with a part of the matrix depending on the size
						# of the regarded cell range
						if max_interpolate_distance[n] != None:
							start = poi[n] - n_regarded_cells[n]
							if start < 0:
								start= 0
							stop = poi[n] + n_regarded_cells[n]
							if stop > b.resolution-1:
								stop= b.resolution-1
							regarded_cell_range[n] = slice(start, stop)
							pos_corr[n] = start
						else:
							regarded_cell_range[n] = slice(None,None)
					t_regarded_cell_range = tuple(regarded_cell_range)
					sliced_moment_matrix = momentMatrix[t_regarded_cell_range]
					for mergePosition,mergeValue in np.ndenumerate(
							mergeM[t_regarded_cell_range]):
						#empty merge-positions have no moment
						if np.isnan(mergeValue):
							sliced_moment_matrix[mergePosition] = 0
						else:
							#calc distance of each mergePoint to each mergePoint
							distance = 0
							for k in range(self.nBasis):
								distance += (abs(poi[k] -
								(mergePosition[k] + pos_corr[k]) )*
									basis_distance_factor[k]) **2
							distance = distance**0.5
							if distance == 0:
								#above point of interest
								sliced_moment_matrix[mergePosition] = max_moment
							elif (max_interpolate_distance[n] != None and
									distance > abs_max_interpolation_dist):
								#no moments if to far away from existant points
								sliced_moment_matrix[mergePosition] = np.nan
							else:
								#calc moments
								sliced_moment_matrix[mergePosition] = 1 / (
									distance **focus_exponent )
					if eval_pointDesity:
						#multiply moment with number of points
						sliced_moment_matrix *= densityM[t_regarded_cell_range]
					##normalize moments that sum(moments)=1
					nansum = bn.nansum(sliced_moment_matrix)
					if nansum != 0:
						sliced_moment_matrix /= nansum
					##mergeMatrix[point]=sum(moments*matrix)
						new_mergeM[poi] = bn.nansum(
							mergeM[t_regarded_cell_range] * sliced_moment_matrix )
					status_counter += 1
					if status_counter == next_status:
						#print status
						_utils.statusBar(nPoi+1, mergeM.size)
						status_counter = 0
				self.mergeMatrix[merge_index] = new_mergeM
		except KeyboardInterrupt:
			print "...interrupted"
		print "done"


	def transformDim(self, **kwargs):
		'''
		==================     ===============  =========    ================
		Keyword	               Type             Default      Description
		==================     ===============  =========    ================
		*mergeName*            list(mergeDim)   [{all}]      one or more merge-dims to do the method on
		*rebuildMatrix*        bool             False        'True' does:
		                                                     :py:func:`transformMatrixToPoints`
		                                                     :py:func:`_buildMatrices`
		                                                     :py:func:`fill`
		==================     ===============  =========    ================
		'''

		mergeNames = deepcopy(self.mergeNames)
		rebuild_matrix = True
		#individual
		for key in kwargs:
			if key == "mergeName":
				mergeNames = []
				if type(kwargs[key]) != list and type(kwargs[key]) != tuple:
					kwargs[key] = [ kwargs[key] ]
				for m in kwargs[key]:
					if m not in self.mergeNames:
						raise KeyError("ERROR: mergeName '%s' not known" %m)
					mergeNames.append(m)
			elif key == "rebuildMatrix":
				rebuild_matrix = bool(kwargs[key])


		#transform old basisMatrix
		some_dim_transformed = False
		for i in range(self.nBasis):
			#rewrite basisMatrix
			for n,k in enumerate(self._basis_dim[i]._transform._list):
				if not self._basis_dim[i]._transform.adhoc[n]:
					some_dim_transformed = True
					#than: values were not transformed in readout
					for j in range(len(self.basisMatrix[i])):
						self.basisMatrix[i][j] =k.get(self.basisMatrix[i][j])
					##change dimension-unit and -range
					self._basis_dim[i].unit = k.unit
					new_range = [None,None]
					for j in range(2):
						new_range[j] = \
							k.get(self._basis_dim[i]._getIncludeRange()[j])
				#init new range
					self._basis_dim[i]._includeRange(new_range)
	
		if not some_dim_transformed:
			print "WARNING: no transform-Method defined in basisDimension"
		
		##build discrete points from given matrix, and
		if rebuild_matrix and some_dim_transformed:
			for m in mergeNames:
				merge_index = self.mergeNames.index(m)
				points, merge = self.transformMatrixToPoints()
				points.reverse()
			#for m in range(self.nMerge):

				##transform merge points
				for t in self._merge_dim[merge_index]._transform._list:
					for i in range(len(merge)):
						merge[i] = t.get(merge[i])
						self._merge_dim[merge_index].name = t.name
				##..build new matrix from those discrete and transformed points
				self.transformPointsToMatrix(points, merge,mergeIndex)


	def transformPointsToMatrix(self, points, merge, mergeIndex=0):
		'''
		Counter piece of :py:func:`transformMatrixToPoints`
		'''
		self._buildMatrices()#get new merge- sort-, densityMatrix
		#print self.basisMatrix[0]
		points = zip(*points)
		#for m in range(self.nMerge):
		for i,self._basis_dim[i]._recent_value in enumerate(points):
			if i==5000000:
				exit()
			self._getPositionsIntensities(self)
			for position, intensity in self.positionsIntensities:
				tPostion = tuple(position)
				(replace_value, do_replace)= self._merge_dim[mergeIndex]._mergeMethod._get(
					merge[i],self.mergeMatrix[mergeIndex][tPostion],
					self.densityMatrix[mergeIndex][tPostion],intensity)
				if do_replace:
					self.mergeMatrix[mergeIndex][tPostion] = replace_value
					self.densityMatrix[mergeIndex][tPostion] += intensity



	def transformMatrixToPoints(self, givenMultiDimMeshgrid = None, mergeIndex=0):
		'''
		transform all not-empty parts of a  matrix to discrete points
		
		:return: list(list(basis-values)), list(merge-values)
		'''
		print "transform marix-indices of merge %s to discrete points" %self._merge_dim[mergeIndex].name
		
		if givenMultiDimMeshgrid:
			pointsi = deepcopy(givenMultiDimMeshgrid)
		else:
			pointsi = self._multiDimMeshgrid()
		for i in range(self.nBasis):
			#transform to list - necassary when removing NaNs via list.pop()
			pointsi[i] = list(pointsi[i].flatten())
		#points = []
		merge = list(deepcopy(self.mergeMatrix[mergeIndex]).flatten())
		j = 0
		
		while j < len(merge):
			#remove point if merge == nan
			if np.isnan(merge[j]):
				#for i in range(self.nMerge):
				merge.pop(j)
				for k in range(self.nBasis):
					#print i,k,j, len(points[i][k]), len(merge[i])
					pointsi[k].pop(j)
				j -= 1
			j += 1
		print "done"

		return pointsi, merge


	def posterize(self, **kwargs):
		'''
		This method discretize/posterize the values in the mergeMatrix (of a given mergeDimension)
		to a given ammount of values (e.g. nValues= 4 ) or to a given list or values
		(e.g. values = [1,2,4])

		**Optional kwargs** ("keyword arguments") are:

		==================     ================= =========    ================
		Keyword	               Type              Default      Description
		==================     ================= =========    ================
		*mergeName*             list(mergeNames) [{all}]      one or more merge-dims to do the method on
		*nValues*              int               5            the amount of different values
		*values*               list              None         given different values
		==================     ================= =========    ================
		'''

		#standard
		mergeNames = deepcopy(self.mergeNames)
		
		nValues=5
		values=None
		#individual
		for key in kwargs:
			if key == "mergeName":
				mergeNames = []
				if type(kwargs[key]) != list and type(kwargs[key]) != tuple:
					kwargs[key] = [ kwargs[key] ]
					
				for m in kwargs[key]:
					#_utils.checkClassInstance(m,mergeDimension)
					if m not in self.mergeNames:
						exit("ERROR: mergeName %s not known" %m)
					mergeNames.append(m)
			elif key == "nValues":
				nValues = int(kwargs[key])
			elif key == "values":
				values = list(kwargs[key])
			else:
				raise KeyError("keyword '%s' not known" %key)


		print "-> Posterize mergeMatrices..."
		for i in mergeNames:
			#which mergeMatrix is involved?
			#find index
			merge_index = self.mergeNames.index(i)
			m=self.mergeMatrix[merge_index]
			
			if values == None:
				#create values-list
				values_i = np.linspace(bn.nanmin(m),bn.nanmax(m),nValues)
			else:
				values_i = np.array(values)
			print "... %s to the values %s" %(i, values_i)

			#do posterizing
			for x in np.nditer(m, op_flags=['readwrite']):
				diff=values_i-x
				diff=abs(diff)
				nearest = diff.argmin()
				x[...] = values_i[ nearest ]


#######PRIVATE########

	def _multiDimMeshgrid(self):
		'''like np.meshgrid but can also produce multi-dimensional meshgrids
		takes  list of arrays, where len(list)=nBasis'''
		
		print "create a multiDimMeshgrid"
		#if type(basisMatrix)=array an error will be produced in np.repeat
		basisMatrix = list(self.basisMatrix)
		basisMatrix.reverse()
		
		lenBasis = []
		newShape = [self.nBasis]
	
		for i in basisMatrix:
			lenBasis.append(len(i))
		lenBasisrev = deepcopy(lenBasis)
		lenBasisrev.reverse()
		newShape.extend(lenBasisrev)
		
		for i in range(self.nBasis):
			if i==0:
				nRepeat = 1
			else:
				nRepeat = lenBasis[i-1]
				lenBasis[i]*=nRepeat
			#double items
			basisMatrix[i] = basisMatrix[i].repeat(nRepeat)
	
		lenGrid = len(basisMatrix[-1])
		for i in range(self.nBasis):
			#repeate blocks
			basisMatrix[i] = np.lib.stride_tricks.as_strided(
				basisMatrix[i], (lenGrid/len(basisMatrix[i]),)+basisMatrix[i].shape, (0,)+basisMatrix[i].strides).flatten()
			
		#reshape blocks
		basisMatrix = np.array(basisMatrix)#reshape need an array
		print "done"
		return list(basisMatrix.reshape(tuple(newShape)))
