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
import _dimension

import _source

class libreOfficeCalc(_source.source):
	'''allow to read values from a libre/open-office-calc document
	prepare for reading values from an libreOffice-calc-document
	needs:
	* *ODS_file_name* = "name of the file" e.g. "myfile.ods"
	* *sheet_name_or_number* ="name" OR number of the sheet e.g. "sheet1" OR 4
	'''

	def __init__(self, ODS_file_name, sheet_name_or_number,
			data_type="unknown", print_error_when_cell_is_empty = False):

		super(libreOfficeCalc,self).__init__(data_type)

		self.file_name = ODS_file_name
		self.doc = ooolib.Calc()
		self.doc.load(self.file_name)
		self.empty_cell_list = []
		self.finished_building_empty_cell_list = False
		self.print_error_when_cell_is_empty = print_error_when_cell_is_empty
		self.sheet_name_or_number = sheet_name_or_number

		self._readout_every_n_line = 1
		
		self._index_counter = -1 #helps to indices the dimensions
		self.file_dim = []
		self.coord_list = []


	def setReadoutEveryNLine(self, readout_every_n_line):
		self._readout_every_n_line = int(readout_every_n_line)


	def basisDimension(self, name, resolution, cell_range, includeMethod=""):
		'''
		:class:`diaGrabber.source._dimension.basisDimension` \n
		needs: \n
		* *cell_range* = "START:STOP" e.g. "C2:C1000"
		* it's also possible to scan multiple collums... just type e.g. "A1:E10"
		'''	
		new_dimension  = _dimension.basisDimension(name, self._getIndex(), resolution, includeMethod)
		self.basis_dim.append(new_dimension)

		self._extendCellRangeToDimension(cell_range, new_dimension)
		self.file_dim.append("")#better genrate now than later
		self.coord_list.append([0,0])
		return new_dimension


	def mergeDimension(self, name, cell_range, mergeMethod=""):
		'''
		:class:`diaGrabber.source._dimension.mergeDimension` \n
		needs: \n
		* *cell_range* = "START:STOP" e.g. "C2:C1000"
		* it's also possible to scan multiple collums... just type e.g. "A1:E10"
		'''	
		new_dimension  = _dimension.mergeDimension(name, self._getIndex(), mergeMethod)
		self.merge_dim.append(new_dimension)

		self._extendCellRangeToDimension(cell_range, new_dimension)
		self.file_dim.append("")#better genrate now than later
		self.coord_list.append([0,0])
		return new_dimension






######PRIVATE############

	def _extendCellRangeToDimension(self, cell_range, dim_class):
		#self._getCoordRange(cell_range)


			#'''in: cell_range e.g. "A1:A100"
			#out: coord_range = [X_start, X_stop, Y_start, Y_stop] e.q. [0,10,2,2]'''
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


	def _getMinMax(self,dims):
		sys.exit(NotImplemented)
		
	def _prepareReadOut(self, matrixClass):
		self._prepareStandard(matrixClass)
		
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


	def _readOut(self, readout_one_line, end_readOut):
		while True:
			for i in range(self._readout_every_n_line):
				done_readout = self._updateCoordinates()
			if done_readout:
				return True
			self._grabODSValues()
		
			self._assignValues(self.file_dim)
			
			if readout_one_line:
				return False
			if end_readOut:
				return True

		return True # means i'm done with readout


	def _updateCoordinates(self):
		def update(dim):
			self.coord_list[dim.index] = [dim.X_step, dim.Y_step]
			dim.Y_step += 1
			if dim.Y_step > dim.Y_stop:#at end of line
				dim.Y_step = dim.Y_start
				dim.X_step += 1
				if dim.X_step > dim.X_stop:
					#as soon as the first dim reaches the end of the coord-range
					return True #done readout
		for dim in self.basis_dim:
			done_readout = update(dim)
		if not done_readout:
			for dim in self.merge_dim:
				done_readout = update(dim)
		return done_readout #continue readout


	def _grabODSValues(self):
		'''
		in: coord_list = [ [x1,y1] ,..., [xN,yN] ]
		out: value_list = [ ["value in x1","value in y1"] ,... ]
		'''
		#value_list = []
		for n,c in enumerate(self.coord_list):
			try:
				self.file_dim[n] = self.doc.get_cell_value(c[0],c[1])[1]
			except TypeError:
				if self.print_error_when_cell_is_empty:
					#print("First and last ODS-Values: %s ... %s"
					#% (value_list[0], value_list[-1]))
					sys.exit("""ERROR while reading value from the ODS-file...
					are empty cells in your range?""")
				else:
					self.file_dim[n] = ""
			except UnicodeEncodeError:
				self.file_dim[n] = ""
