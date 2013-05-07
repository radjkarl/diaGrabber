# -*- coding: utf-8 *-*
from _matrix import matrixBase
from copy import deepcopy

class fineMatrix(matrixBase):
	'''
	Takes one or more source-instances as list.
	Create like this::

		myMatrix = diaGrabber.target.fineMatrix( (mySource1,...mySourceN) )

	This class isn't as fast as :class:`.coarseMatrix` but can assign values
	in a more accurate way if the following condition is fullfilled:
	
	.. note:: number of datapoints in matrix>> matrix-resolution
	
	In a fineMatrix the values of the mergeDimensions were stored in the mergeMatrix
	at the nearest point (analoque to the procedure of the :class:`.coarseMatrix`)
	AND all points near this point. Depending on the number of basisDimensions the following
	number of positions were filled:
	
	=======  ==========
	nBasis   nPositions
	=======  ==========
	1        2
	2        4
	3        8
	=======  ==========


	This splitted values are wheighted through
	its values in the densityMatrix - ther pointsdensity.
	The sum of this pointsdensity is allways one. The following images should illustrate this procedure:
	
	.. image:: _static/fineMatrix_1D.png
	   :scale: 60 %

	.. image:: _static/fineMatrix_2D.png
	   :scale: 60 %
	'''

	def __init__(self, sourceClassList):
		super(fineMatrix, self).__init__(sourceClassList)
		self.positionsIntensities = [[[ ],1]]
		self.anzAffectedCells = 2**self.nBasis
		self.affectedCellCounter =  []
		for i in range(1,self.nBasis+1,1):
			self.affectedCellCounter.append((2**i/2) -1)
		
		for i in range(self.nBasis):
			self.positionsIntensities[0][0].append(0)

		for i in range(self.anzAffectedCells-1):
			#1D: 2 cells
			#2D: 4 cells
			#3D: 8 cells
			self.positionsIntensities.append(deepcopy(self.positionsIntensities[0]))

	def _getPositionsIntensities(self, sourceClass):
		
		for i in range(self.anzAffectedCells):
			#reset intensities (later there is a *=)
			self.positionsIntensities[i][1] = 1
		
		for i,basis in enumerate(sourceClass._basis_dim):
			difference_list = self.basisMatrix[i] - basis._recent_value
			difference_list = abs(difference_list)
			nearest_point = difference_list.argmin()
			self._basis_dim[i]._recent_position = nearest_point
			if nearest_point == 0:#is first point of array - neared point is second point
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
