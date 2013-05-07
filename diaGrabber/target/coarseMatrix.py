# -*- coding: utf-8 *-*
from _matrix import matrixBase
from diaGrabber import _utils

class coarseMatrix(matrixBase):
	'''
	Takes one or more source-instances as list or tuple. Create like this::
	
		myMatrix = diaGrabber.target.coarseMatrix( (mySource1,...mySourceN) )
	
	Coarse matrices store values of the mergeDimension at the nearest point in the
	mergeMatrix given by the difference of the values of the basisDimension and
	and the values of the basisMatrix. The following images iluustrated this procedure.
	
	.. image:: _static/coarseMatrix_1D.png
	   :scale: 60 %
	.. image:: _static/coarseMatrix_2D.png
	   :scale: 60 %
	'''

	def __init__(self, sourceClassList):
		super(coarseMatrix, self).__init__(sourceClassList)
		#intensity in every situation =1 because thers no splitting of the merge-values
		self.positionsIntensities = [[[ ],1]]
		for i in range(self.nBasis):
			self.positionsIntensities[0][0].append(0)

	def _getPositionsIntensities(self, sourceClass):
		for i,basis in enumerate(sourceClass._basis_dim):#range(self.nBasis):
			nearest_point=_utils.nearestPosition(self.basisMatrix[i],basis._recent_value)
			self._basis_dim[i]._recent_position = nearest_point
			self.positionsIntensities[0][0][i] = nearest_point
