# -*- coding: utf-8 *-*
class _plot(object):
	
	def __init__(self, matrixClass, alt_plotMatrix, merge_index):
		self.matrixClass = matrixClass
		try:
			self.plot_overlay = self.matrixClass.plot_overlay
			if alt_plotMatrix != "":
				self.matrix = eval("self.matrixClass." + alt_plotMatrix)
			else:
				self.matrix = self.matrixClass.mergeMatrix
			self.sortMatrix = self.matrixClass.sortMatrix
			self.merge_dim = self.matrixClass.merge_dim
			self.basis_dim = self.matrixClass.basis_dim
			self.nDim = self.matrixClass.nDim
			self.nMerge = self.matrixClass.nMerge
			self.merge_index = merge_index
			if self.merge_index == []:
				#if not defined, plot all (merge)matrices
				self.merge_index = range(self.nMerge)
			
		except AttributeError:
			sys.exit("ERROR while loading matrixClass - have you loaded values before plotting?")
