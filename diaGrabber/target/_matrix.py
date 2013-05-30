# -*- coding: utf-8 *-*

#foreign modules
import numpy
from sys import exit
from copy import deepcopy

#own modules
from diaGrabber import _utils
from diaGrabber import source
from _matrixMethods import matrixMethods


class matrixBase(matrixMethods):
	'''
	Base-Class for all matix-like-targets.
	Includes every method that is equal for them.

	:param sourceClassList: One or more instances of source-classes
	:type sourceClassList: tuple, list

	Using more source-classes can be usefull to:

		* combine (**same merge-dimensions**)
		* compare (**different merge-dimensions**)

	values.
	When more sources are used each source has to have
	**the same basis (with same names and units)**
	Different ranges and resolutions will be fitted.
	If different sources includes mergeDimensions of the same name (**and unit**)
	their values are assembled.
	Depending on the number of used basis- and mergeDimensions all matrix-targets
	create three different matrices:

		* basisMatrix (1D-numpy.array)
		* mergeMatrix (nD-numpy.array)
		* densityMatrix (nD-numpy.array)

	...

	.. image:: _static/matrix_build_scheme.png
	   :scale: 70 %
	'''

	def __init__(self, sourceClassList):
		###SOURCECLASS-HANDLING
		self.sourceClassList = sourceClassList
			#if only one list is given or lists are given in tuple: formal as list
		if type(self.sourceClassList) != list:
			if type(self.sourceClassList) == tuple:
				self.sourceClassList = list(self.sourceClassList)
			else:
				self.sourceClassList = [self.sourceClassList]
			#check whether all entries in sourceClassList belongs to the module 'source'
		for sourceClass in self.sourceClassList:
			_utils.checkModuleInstance(sourceClass, source)

		self._fitBasisDims()
		self._combineMergeDims()

		self.mergeNames = []
		for i in self._merge_dim:
			self.mergeNames.append(i.name)
		self.basisNames = []
		for i in self._basis_dim:
			self.basisNames.append(i.name)
		self._setPlotOverlay()


	def fill(self):
		'''
		Readout the whole source, then continue.
		'''
		#check and get min-max-values for unbounded basis-dim
		self._checkMinMax()
		self._prepareFill()
		print "reading out file(s):"
		for sourceClass in self.sourceClassList:
			print sourceClass.file_name
			sourceClass._prepareReadOut()
		self._fill(False, False)
		self._resetReadout()
		print "done"


	def fillInteractive(self, plotInstance, **kwargs):
		'''
		Fill the matrix with the source-values and plot the progress.
		Therefore a plotInstance which is able to plot interactive is needed.
		kwargs can be those from the plot-method of the used 'plotInstance'
		'''
		#check whether plotInstance is able to plot interactive
		if not plotInstance.hasInteractiveModus:
			exit("ERROR: plotInstance %s cannot be used for method 'fillInteractive' of %s!"
				%(plotInstance.__class__, self.__class__) )

		#start interactive plotting/readout
		kwargs["interactive"] = True
		#check and get min-max-values for unbounded basis-dim
		self._checkMinMax()
		self._prepareFill()
		print "reading out file(s):"
		for sourceClass in self.sourceClassList:
			print "   " + sourceClass.file_name
			sourceClass._prepareReadOut()
		plotInstance.plot(**kwargs)
		print "done"
		self._resetReadout()



	def save(self, **kwargs):
		'''
		Save the following matrices (of all mergeDimensions) to file:
			* basisMatrix
			* mergeMatrix
			* densityMatrix

		**Required kwargs** ("keyword arguments") are:

		==================     ===============  =============    ================
		Keyword	               Type             Example          Description
		==================     ===============  =============    ================
		*name*                 string           "test"           prename of the saved files.
		==================     ===============  =============    ================

		Optional kwargs ("keyword arguments") are:

		==================     ========  =======          ============================
		Keyword	               Type      Default          Description
		==================     ========  =======          ============================
		*folder*               string    ""               Name of the folder to save in
		==================     ========  =======          ============================
		'''
##	*ftype*                string    "bin"            "bin": output is saved in computer-readable binary-form, "txt": output is saved in a human-readable-form


		#standard
		file_name = None

		folder_name = ""
		#save_type = "bin"

		#individual
		for key in kwargs:
			if key == "name":
				file_name = str(kwargs[key])
			elif key == "folder":
				folder_name = str(kwargs[key])
			#elif key == "ftype":
				#if kwargs[key] == "bin":
					#save_type = "bin"
				#elif kwargs[key] == "txt":
					#save_type = "txt"
				#else:
					#raise KeyError("ERROR: target.save 'type' must be 'bin' or 'txt'")
			else:
				raise KeyError("keyword '%s' not known" %key)
		_utils.checkRequiredArgs({
				"name":file_name})

		print "saving matrix ..."
		file_name = _utils.prepareFileSystem(file_name, folder_name)#combining file and folder
		file_name = _utils.prepareFileSystem("",file_name)#creating file-folder
		#print file_name
		#if save_type == "bin":
		for i in range(self.nMerge):
			f = "%s%s_merge" %(file_name, self._merge_dim[i].name)
			numpy.save(f, self.mergeMatrix[i])
			numpy.savetxt(f, self.mergeMatrix[i], fmt = "%10.5f")
			print "created %s" %f
			f = "%s%s_density" %(file_name, self._merge_dim[i].name)
			numpy.save(f, self.densityMatrix[i])
			numpy.savetxt(f, self.densityMatrix[i], fmt = "%10.5f")
			print "created %s" %f
		f = "%sbasis" %(file_name)
		numpy.save(f, self.basisMatrix)
		numpy.savetxt(f, numpy.array(self.basisMatrix), fmt = "%10.5f")
		print "created %s" %f
		#else:
			#for i in range(self.nMerge):
				#f = "%s_%s_merge" %(file_name, self._merge_dim[i].name)
				#numpy.savetxt(f, self.mergeMatrix[i], fmt = "%10.5f")
				#print "created txt-file %s" %f
				#f = "%s_%s_density" %(file_name, self._merge_dim[i].name)
				#numpy.savetxt(f, self.densityMatrix[i], fmt = "%10.5f")
				#print "created txt-file %s" %f
			#f = "%s_basis" %(file_name)
			#numpy.savetxt(f, numpy.array(self.basisMatrix), fmt = "%10.5f")
			#print "created txt-file %s" %f


	def load(self, name, folder = ""):
		'''
		Load previous saved matrices.
		'''
		print "loading matrix"
		file_name = _utils.prepareFileSystem(name, folder)
		file_name = _utils.prepareFileSystem("",file_name)#creating file-folder
		#if ftype == "bin":
		self.mergeMatrix = []
		self.basisMatrix = []
		self.densityMatrix = []
		for i in range(self.nMerge):
			##MERGE
			f = "%s%s_merge.npy" %(file_name, self._merge_dim[i].name)
			self.mergeMatrix.append(numpy.load(f))
			print "loaded binary-file %s" %f
			##DENSITY
			f = "%s%s_density.npy" %(file_name, self._merge_dim[i].name)
			self.densityMatrix.append(numpy.load(f))
			print "loaded binary-file %s" %f
		#BASIS
		f = f = "%sbasis.npy" %(file_name)
		self.basisMatrix = numpy.load(f)
		print "loaded binary-file %s" %f
		#else:
			#exit("ERROR: only ftype=bin implemented at the moment")

		for i in range(len(self._basis_dim)):
			if self._basis_dim[i]._take_all_values:
				#define range for _include_range from loaded basisMatrix
				self._basis_dim[i]._includeRange(
					[min(self.basisMatrix[i]),max(self.basisMatrix[i])])


#####PRIVATE######

	def _fitBasisDims(self):
		self._basis_dim = self.sourceClassList[0]._basis_dim
		self.nBasis = len(self._basis_dim)
		if self.nBasis == 0:
			exit("ERROR: no basisDimension in source %s defined" %self.sourceClassList[0].dat_file)
		basis_names = []
		basis_units = []
		for basis in self._basis_dim:
			basis_names.append(basis.name)
			basis_units.append(basis.unit)
		basis_sort_list = []
		#check name and unitof all basis-dims
		for sourceClass in self.sourceClassList[1:]:
			basis_sort_list.append([])
			for basis in sourceClass._basis_dim:
				if basis.name in basis_names:
					i = basis_names.index(basis.name)
					if basis.unit != basis_units[i]:
						exit("ERROR found same basis with different units")
					else:
						basis_sort_list[-1].append(i)
				else:
					exit("ERROR: basis-names in different sources different")
			#prove whether basi-dims are complete
			if len(sourceClass._basis_dim) != self.nBasis:
				exit("ERROR: number of basisDimensions in sources are different!")

		#sort basis_dims in all sources
		for s_i,sourceClass in enumerate(self.sourceClassList[1:]):
			sorted_basis = []
			for i in basis_sort_list[s_i]:
				sorted_basis.append(sourceClass._basis_dim[i])
			sourceClass.setBasis(sorted_basis)

		#fit range and resolution for all same basis-dims - use max values
		for n in range(self.nBasis):
			max_resolution = self._basis_dim[n].resolution
			min_range = self._basis_dim[n]._include_range[0]
			max_range = self._basis_dim[n]._include_range[1]
			resolution_changed = False
			range_changed = False
			for sourceClass in self.sourceClassList[1:]:
				#resolution
				#print sourceClass._basis_dim
				if sourceClass._basis_dim[n].resolution > max_resolution:
					max_resolution = sourceClass._basis_dim[n].resolution
					resolution_changed = True
				#min_range
				if sourceClass._basis_dim[n]._include_range[0] < min_range:
					min_range = sourceClass._basis_dim[n]._include_range[0]
					range_changed = True
				#max range
				if sourceClass._basis_dim[n]._include_range[1] > max_range:
					max_range = sourceClass._basis_dim[n]._include_range[1]
					range_changed = True
			#define new
			if resolution_changed:
				print "fitted different resolution for all basisDim %s to %s" %(self._basis_dim[n].name,max_resolution)
				for sourceClass in self.sourceClassList:
					sourceClass._basis_dim[n].resolution = max_resolution
			if range_changed:
				print "fitted different ranges for all basisDim %s" %(i)
				for sourceClass in self.sourceClassList:
					sourceClass._basis_dim[n]._includeRange([min_range,max_range])


	def _combineMergeDims(self):
		# assign indicex of mergeDimensions to those of the mergeMatrices
		self.merge_to_matrix = []
		# a list of all DIFFERENT mergeDimensions in the target
		self._merge_dim = []
		merge_names = []
		merge_units = []
		for sourceClass in self.sourceClassList:
			self.merge_to_matrix.append([])
			merge_names_in_source = []
			for merge in sourceClass._merge_dim:
				if merge.name not in merge_names:
					#append new merge-dim
					self._merge_dim.append(merge)
					merge_names.append(merge.name)
					merge_units.append(merge.unit)
					merge_names_in_source.append(merge.name)
					self.merge_to_matrix[-1].append(len(self._merge_dim)-1)
				else:
					#check whether same merge-dim same source
					if merge.name in merge_names_in_source:
						exit("ERROR: found same mergeDimension '%s' in same source '%s'. thats illegal!" %(merge.name,sourceClass.dat_file) )

					#combine same merge-dims
					i = merge_names.index(merge.name)
					if merge_units[i] != merge.unit:
						exit("ERROR: found same mergeDimension '%s' in different sources with different units ('%s' and '%s'). thats illegal!" %(merge.name,merge.unit, merge_units[i]) )

					self.merge_to_matrix[-1].append(i )
		self.nMerge = len(self._merge_dim)


	def _setPlotOverlay(self):
		self.plot_overlay = []
		#every merge-dim has its on plot-overlay
		for i in range(self.nMerge):
			self.plot_overlay.append([[], [], [], [], [], [],[]])
			#plot_overlay = [(points), (lines), (broken lines), , (ellipses), (rectangles), (text), (legend)]
				#(points),(broken lines), (lines)  = [x-list,y-list]
				#(ellipses) = list[ tuple(x,y), float(width), float(height), float(angle) ) ## str(color) ]
				#(rectangles) = list[ tuple(x,y), float(width), float(height) ]
				#(text) = list[ tuple(x,y), string(text)
				#(legend) = list[str(...),... ]


	def _prepareFill(self):
		self._setPlotOverlay()
		#build basisMatrix, mergeMatrices, densityMatrices
		self._buildMatrices()

	def _setReadoutEveryNLine(self, readoutEveryNLine):
		'''
		Try to set the value _readout_every_n_line in every given source-class.
		If a source-class donst has this attribute, restore the original value.
		'''
		original_readout_value = []
		try:
			for sourceClass in self.sourceClassList:
				original_readout_value.append(sourceClass._readout_every_n_line)
				sourceClass._setReadoutEveryNLine(readoutEveryNLine)
		except (AttributeError, ValueError):
			print "ERROR: couldnt set readoutEveryNLine to %s to all sourceClasses." %readoutEveryNLine
			for n,sourceClass in enumerate(self.sourceClassList):
				#restore the original value
				sourceClass._setReadoutEveryNLine(original_readout_value[n])


	def _getReadoutEveryNLine(self):
		'''
		because every source-file has a identically
		value for it we can take the first one
		'''
		return self.sourceClassList[0]._readout_every_n_line


	def _buildMatrices(self):
		'''
		create:

			* **mergeMatrix** - a list of nD-arrays containing nan (later overridden bymerge-values
			* **densityMatrix** - a list of nD-arrays containing the number of overridden-merge-values
			* **basisMatrix** - a list of 1D-arrays containing th range of all basis-values
		'''
		#empty matrix
		matrix_str = "numpy.zeros(shape=("
		for i in range(len(self._basis_dim)):
			if self._basis_dim[i].resolution <= 0:
				exit("ERROR: to build a matrix you need to set a number for %s.resolution" %self._basis_dim[i].name)
			matrix_str += "%s," %self._basis_dim[i].resolution
		matrix_str += "))"
		
		self.densityMatrix = []
		for i in range(self.nMerge):
			#an empty densityMatrix contins only zeros
			self.densityMatrix.append(eval(matrix_str))
		self.mergeMatrix = deepcopy(self.densityMatrix)
		for i in range(self.nMerge):
			#fill every mergeMatrix with nan - saying: ther are no values, i'm empty
			self.mergeMatrix[i].fill(numpy.nan)

		self.basisMatrix = []
		for i in range(len(self._basis_dim)):
			self.basisMatrix.append(self._basis_dim[i]._sort_range)


	def _fill(self, readout_one_line, end_readOut):
		'''
		Intrinsic method to readout all sources and to fill the matrix.
		'''
		while True:
			try:
				if end_readOut:
					for sourceClass in self.sourceClassList:
						sourceClass._endReadOut()
					break
				done_readout = True

				for s_i, sourceClass in enumerate(self.sourceClassList):
					#print sourceClass.done_readout, sourceClass._last_file
					if not sourceClass.done_readout:
						sourceClass._getValueLine()
						in_range = sourceClass._getBasisMergeValues()
						if in_range:
							self._assign(sourceClass, self.merge_to_matrix[s_i])
						done_readout = False
					elif not sourceClass._last_file:
						sourceClass._prepareReadOut()
						done_readout = False
					sourceClass._printStatus()
				if done_readout:
					break
				if readout_one_line:
					return False #i'm not done with readout
			#except StopIteration:
			#	break
			except KeyboardInterrupt:
				for sourceClass in self.sourceClassList:
					sourceClass._endReadOut()
				break
		print ""
		return True # i'm done with readout


	def _resetReadout(self):
		for sourceClass in self.sourceClassList:
			sourceClass._resetReadout()


	def _assign(self, sourceClass, merge_to_matrix):
		'''
		Assign all self.merge_values to the self.mergeMatrix
		Get the position/intensity of a value
		'''
		self._getPositionsIntensities(sourceClass)

		for position, intensity in self.positionsIntensities:
			tPostion = tuple(position)
			for n,merge in enumerate(sourceClass._merge_dim):
				#create a merge-value that replaces an old value in the matrix
				#and geting the info. whether to replace with the mergeMethod of the dim.
				if merge._in_range:
					(merge.replace_value, merge._in_range)= merge._mergeMethod._get(
						merge._recent_value,#sourceClass.merge_values[n],
						self.mergeMatrix[merge_to_matrix[n]][tPostion],
						self.densityMatrix[merge_to_matrix[n]][tPostion],intensity)
			#for every alias-connection in every merge_dim
			for n,merge in enumerate(sourceClass._merge_dim):
				for aliasMerge in merge._alias._list:
					# the value on a mergeDim. with alias-connections can only be set,
					# if all mergeDims in the _alias-list are 'do_replace=True'
					if not aliasMerge._in_range:
						merge._in_range = False
			# finally: write new values in an extra cycle is necassary for
			# the alias-comparisons
			for n,merge in enumerate(sourceClass._merge_dim):
				if merge._in_range:
					#replace_value
					self.mergeMatrix[merge_to_matrix[n]][tPostion] = merge.replace_value
					#intensity
					self.densityMatrix[merge_to_matrix[n]][tPostion] += intensity


	def _checkMinMax(self):
		'''
		get minMax-range for all unlimited dimensions
		'''
		#get_MinMax_values = []
		for sourceClass in self.sourceClassList:
			dims = []
			dim_names = []
			for i in range(sourceClass.nBasis):
				if sourceClass._basis_dim[i]._take_all_values:
					dims.append(sourceClass._basis_dim[i])#.index)
					dim_names.append(sourceClass._basis_dim[i].name)
			if len(dims) > 0:
				print "-> in source %s" %sourceClass.file_name
				print "...getting range for dims %s" %dim_names
				min_max = sourceClass._getMinMax(dims)
				for n in range(len(dims)):
					dims[n]._includeRange(min_max[n])
