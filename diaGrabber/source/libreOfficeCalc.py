# -*- coding: utf-8 *-*
#bla
#
#
import sys

import ooolib
	# open/libre-office support
	# see old: http://sourceforge.net/projects/ooolib/
	# see new: https://code.google.com/p/odslib-python/
#from _dimension import _dimension

import _source
import _dimension

from diaGrabber import _utils

class libreOfficeCalc(_source.source):
	'''
	Allow to read values from a libre/open-office-calc document
	For a list of all possible Keyword-arguments have a look at :py:func:`setArgs`
	'''

	def __init__(self, **kwargs):
		##standard
			#required
		self.file_name = None
		self.sheet_name_or_number= None
			#optional
		self.folder= ""
		self._readout_every_n_line = 1
		self.data_type = "unknown"
		self.ignore_empty_cells = True

		#individual
		self.setArgs(**kwargs)
		_utils.checkRequiredArgs({
			"file":self.file_name,
			"sheet":self.sheet_name_or_number})

		super(libreOfficeCalc,self).__init__(self.data_type)

		#helpers
		self.empty_cell_list = []
		self.finished_building_empty_cell_list = False
		self._index_counter = -1 #helps to indices the dimensions
		self.coord_list = []
		
		#load ods-document
		self.doc = ooolib.Calc()
		self.doc.load(self.dat_file)


	def setArgs(self, **kwargs):
		'''
		**Required kwargs** ("keyword arguments") are:

		==================     ===========  =============    =============
		Keyword	               Type         Example          Description
		==================     ===========  =============    =============
		*file*                 string       "myFile.ods"     Name of the ODS-File
		*sheet*                string/int   "sheet1" OR 1    Sheet-name or number in the ODS-file
		==================     ===========  =============    =============

		**Optional kwargs** ("keyword arguments") are:

		====================   ========  ==========       ============================
		Keyword	               Type      Default          Description
		====================   ========  ==========       ============================
		*folder*               string    ""               Name of the parent-folder of the file
		*readoutEveryNLine*    int       1                read every n line from the file
		*dataType*             string    "unknown"        for all possible values are defined  see :func:`diaGrabber.source._source.source._evalDataType`
		*ignoreEmptyCells*     bool      True             Set to False to exit, when cells inthe cellRange of thedimensions are empty
		====================   ========  ==========       ============================
		'''
		for key in kwargs:
			if key == "file":
				self.file_name = str(kwargs[key])
			elif key == "folder":
				self.folder = str(kwargs[key])
			elif key == "sheet":
				self.sheet_name_or_number = kwargs[key]
			elif key == "readoutEveryNLine":
				self._setReadoutEveryNLine(kwargs[key])
			elif key == "dataType":
				self.data_type = kwargs[key]
			elif key == "ignoreEmptyCells":
				self.ignore_empty_cells = bool(kwargs[key])
			else:
				raise KeyError("keyword '%s' not known" %key)
		self._setDatFile()

	#def setReadoutEveryNLine(self, readout_every_n_line):
	#	self._setReadoutEveryNLine(readout_every_n_line)

	def _setReadoutEveryNLine(self,readout_every_n_line):
		'''
		Defines ever which row diaGrabber will grab a value from the Table.
		
		:param readout_every_n_line: number of rows to jump over e.g. **100**
		:type readout_every_n_line: int
		'''
		if readout_every_n_line < 1:
			raise ValueError("Negative Values aren't supported at the moment")
		else:
			self._readout_every_n_line = int(readout_every_n_line)

	def basisDimension(self, **kwargs):
		'''
		Add a new basis-dimension to the source.
		See :class:`diaGrabber.source._dimension.basisDimension` for further explanation and options.
		Replaces keyword 'index' with 'cellRange':

		:param cellRange: ["START:STOP"] range of the cells in the ods-file e.g. "C2:C1000" or "A1:E10"
		:type cellRange: string
		'''	
		
		#modify kwargs:
		kwargs["index"] = self._getIndex() #set index as counted position
		try:
			cell_range=kwargs.pop("cellRange") #extract 'cellRange' from kwargs
		except KeyError:
			raise KeyError("required keyword 'cellRange' is missing for basisDimension")
		
		new_dimension  = _dimension.basisDimension(**kwargs)
		self._embeddBasisDim(new_dimension)
		self._extendCellRangeToDimension(cell_range, new_dimension)
		self.coord_list.append([0,0])
		return new_dimension


	def mergeDimension(self, **kwargs):
		'''
		Add a new merge-dimension to the source.
		See :class:`diaGrabber.source._dimension.mergeDimension` for further explanation and options.
		Replaces keyword 'index' with 'cellRange':

		:param cellRange: "START:STOP" range of the cells in the ods-file e.g. *"C2:C1000"* or *"A1:E10"*
		:type cellRange: string
		'''	
		#modify kwargs:
		kwargs["index"] = self._getIndex() #set index as counted position
		try:
			cell_range=kwargs.pop("cellRange") #extract 'cellRange' from kwargs
		except KeyError:
			raise KeyError("required keyword 'cellRange' is missing for basisDimension")
			
		new_dimension  = _dimension.mergeDimension(**kwargs)
		self._embeddMergeDim(new_dimension)
		self._extendCellRangeToDimension(cell_range, new_dimension)
		self.coord_list.append([0,0])
		return new_dimension

######PRIVATE############

	def _extendCellRangeToDimension(self, cell_range, dim_class):
		'''in: cell_range e.g. "A1:A100"
		out: coord_range = [X_start, X_stop, Y_start, Y_stop]
		appended to dimension-instance'''
		cell_range = cell_range.split(":")
		start = cell_range[0]
		if len(cell_range) > 1:
			stop = cell_range[1]
		else:
			stop = start

		for i in range(len(start)):
			if start[i].isdigit():
				break
		dim_class.X_start = self._transformLetters2Coordinates(start[:i])
		dim_class.Y_start = int(start[i:])
		
		dim_class.X_step = dim_class.X_start
		dim_class.Y_step = dim_class.Y_start

		for i in range(len(stop)):
			if stop[i].isdigit():
				break
		dim_class.X_stop = self._transformLetters2Coordinates(stop[:i])
		dim_class.Y_stop = int(stop[i:])


	def _transformLetters2Coordinates(self, i):
		'''
		in: letter e.g. "A" or "E"
		out: number related to letter e.g. 1 or 5
		'''
		letters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
		def letters2numbers(x, d = dict((letr,n%26+1) for n,
			letr in enumerate(letters[0:52]))):
			return d[x]
		coordinate_list = map(letters2numbers, i)
		coordinateX = 0
		n = 0
		m = len(coordinate_list) - 1
		for n in range(len(coordinate_list)):
			coordinateX += coordinate_list[n] * 26 ** m
			m -= 1
		return coordinateX


	def _getIndex(self):
		self._index_counter += 1
		return self._index_counter


	def _prepareReadOut(self):
		self._prepareStandard()
		self._resetReadOut()
		
		if type(self.sheet_name_or_number) == int:
			self.doc.set_sheet_index(self.sheet_name_or_number - 1)
		elif type(self.sheet_name_or_number) == str:
			found_sheet = False
			for i in range(self.doc.get_sheet_count()):
				self.doc.set_sheet_index(i)
				if self.doc.get_sheet_name() == self.sheet_name_or_number:
					found_sheet = True
					break
			if not found_sheet:
				sys.exit("ERROR: sheet-name '%s' doesn't exist in your ods-file"
				% self.sheet_name_or_number)
		else:
			sys.exit("""ERROR: sheet_name_or_number must be a integer (e.g. 3) or \
			a string ('name'""")
		print("reading values from sheet '%s'" % self.doc.get_sheet_name())


	def _getValueLine(self):
		for i in range(self._readout_every_n_line):
			self.done_readout = self._updateCoordinates()
		
		#if done_readout:
		#	raise StopIteration
		if not self.done_readout:
		#else:
			self._grabODSValues()


	def _printStatus(self):
		pass


	def _resetReadOut(self):
		for dim in self._basis_dim:
			dim.X_step = dim.X_start
			dim.Y_step = dim.Y_start
		for dim in self._merge_dim:
			dim.X_step = dim.X_start
			dim.Y_step = dim.Y_start
		self.done_readout = False


	def _updateCoordinates(self):
		def update(dim):
			self.coord_list[dim.index] = [dim.X_step, dim.Y_step]
			if dim.Y_step > dim.Y_stop:#at end of line
				dim.Y_step = dim.Y_start
				dim.X_step += 1
				if dim.X_step > dim.X_stop:
					#as soon as the first dim reaches the end of the coord-range
					return True #done readout
			dim.Y_step += 1
		for dim in self._basis_dim:
			done_readout = update(dim)
		if not done_readout:
			for dim in self._merge_dim:
				done_readout = update(dim)
		return done_readout #continue readout


	def _grabODSValues(self):
		'''
		in: coord_list = [ [x1,y1] ,..., [xN,yN] ]
		out: value_list = [ ["value in x1","value in y1"] ,... ]
		'''
		for n,c in enumerate(self.coord_list):
			try:
				self.value_line[n] = self.doc.get_cell_value(c[0],c[1])[1]
			except TypeError:
				if not self.ignore_empty_cells:
					sys.exit("""ERROR while reading value from the ODS-file...
					are empty cells in your range?""")
				else:
					self.value_line[n] = ""
			except UnicodeEncodeError:
				self.value_line[n] = ""
