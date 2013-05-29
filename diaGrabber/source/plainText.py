# -*- coding: utf-8 *-*
import linecache, sys

from diaGrabber import _utils
import _source
import _dimension

from os import path

class plainText(_source.source):
	'''
	Readout values from a plain-text saved in file. The format has to be similar to the following example::
		
		value00 value01 value02
		value10 value11 value12
		...
	
	Where the values of all dimensions are written in one line, seperated by one or
	more signs like spaces ' ' or tab '\t'.
	
	For a list of all possible Keyword-arguments have a look at :py:func:`setArgs`
	'''
	def __init__(self, **kwargs):
		#standard
			#required
		self.file_name = None
		self.dim_seperator = None
			#optional
		self.data_type = "unknown"
		self.len_dat_file = 0
		self._readout_every_n_line = 1
		self.folder = ""
		self.buffer = int(10e6)
		self.silent_readout = False


		#individual
		self.setArgs(**kwargs)
		_utils.checkRequiredArgs({"file":self.file_name,
				"dimSeperator":self.dim_seperator})

		#init baseClass
		super(plainText,self).__init__(self.data_type)
		#count lines

		self._setReadoutEveryNLine(self._readout_every_n_line)
		#helper-values
		self.n_line = 0


	def setArgs(self, **kwargs):
		'''
		**Required kwargs** ("keyword arguments") are:

		==================     ========  ================   ============================
		Keyword	               Type      Example            Description
		==================     ========  ================   ============================
		*file*                 string    **'myFile.txt'**   the name of your plainText-file
		*dimSeperator*         string    **' '** (space)    the sign, that seperates the values in one line e.g. '\t' for a tab
		==================     ========  ================   ============================

		**Optional kwargs** ("keyword arguments") are:

		===================    ========  ================   ============================
		Keyword	               Type      Default            Description
		===================    ========  ================   ============================
		*dataType*             string    "unknown"          for all possible values are defined  see :func:`diaGrabber.source._source.source._evalDataType`
		*nFileLines*           int       0                  if you know the number of lines in your file you can avoid the (time-consuming) counting of it through *diaGrabber*
		*readoutEveryNLine*	   int       1                  if you don't need every line of your file you can spare time by readout only every n line of it
		*folder*               string    ""                 the name of the folder of the file
		*buffer*               int       10e6               max. size(byte) loaded into RAM
		                                                    insert '0' to read the whole file
		*silentReadout*        bool      False              set True if you dont want to see
		                                                    a statusBar or similar while
		                                                    readOut
		===================    ========  ================   ============================
		'''
		#individual
		for key in kwargs:
			#required
			if key == "file":
				self.file_name = str(kwargs[key])
			elif key == "dimSeperator":
				self.dim_seperator = str(kwargs[key])
			#optional
			elif key == "dataType":
				self.data_type = str(kwargs[key])
			elif key == "nFileLines":
				self.len_dat_file = int(kwargs[key])
			elif key == "readoutEveryNLine":
				self._readout_every_n_line = int(kwargs[key])
			elif key == "folder":
				self.folder = str(kwargs[key])
				if self.folder != "" and self.folder[-1] != "/":
					self.folder += "/"
			elif key == "buffer":
				self.buffer = int(kwargs[key])
				if self.buffer <= 0:
					raise ValueError("buffer has to be >=1")
			elif key == "silentReadout":
				self.silent_readout  = bool(kwargs[key])
			else:
				raise ValueError("keyword '%s' not known" %key)


	def basisDimension(self, **kwargs):
		'''
		includes
		:class:`diaGrabber.source._dimension.basisDimension`
		to the source
		'''	
		new_dimension  = _dimension.basisDimension(self, **kwargs)
		self._embeddBasisDim(new_dimension)
		return new_dimension


	def mergeDimension(self, **kwargs):
		'''
		includes
		:class:`diaGrabber.source._dimension.mergeDimension`
		to the source
		'''	
		new_dimension  = _dimension.mergeDimension(self, **kwargs)
		self._embeddMergeDim(new_dimension)
		return new_dimension

#######PRIVATE############

	def _setReadoutEveryNLine(self,readout_every_n_line):
		if readout_every_n_line < 1:
			raise ValueError("plainText with attribute 'buffer' doesn't support negative readoutNLine-Values")
		else:
			self._readout_every_n_line = readout_every_n_line
		self._initPrintStatus()


	def _countFileLines(self):
		print "...counting lines in file %s" %self.file_name
		self.len_dat_file = 0
		thefile = open(self.dat_file)
		while 1:
			buffer = thefile.read(self.buffer)
			if not buffer: break
			self.len_dat_file += buffer.count('\n')
		thefile.close()
		print "--> %s lines" %self.len_dat_file


	def _prepareReadOut(self):
		self.n_line = 0
		self._initPrintStatus()
		self._prepareStandard()
		if not path.isfile(self.dat_file):
			sys.exit("ERROR: does your output_file exist?")
		#counting files is only necassary when showing a statusbar
		if not self.len_dat_file and not self.silent_readout:
			self._countFileLines()
		self.file = open(self.dat_file, 'r')
		self._getNextPiece()
		if len(self.file_piece) < self._readout_every_n_line:
			sys.exit("ERROR: buffer to small [len(file_piece):%s < readoutEveryNLine:%s]" %(
				len(self.file_piece), self._readout_every_n_line) )
		if not self.silent_readout:
			self.len_dat_file_minus_n = self.len_dat_file - (self._readout_every_n_line-1)


	def _initPrintStatus(self):
		if not self.silent_readout:
			self.n = 0
			self.sum_bar = 100
			self.showBar_counter = self.len_dat_file / (abs(self._readout_every_n_line) * self.sum_bar)
			if self.showBar_counter == 0:
				self.showBar_counter = 1


	def _getNextPiece(self):
		'''read the next peace from the dat_file'''
		self.file_piece = self.file.readlines(self.buffer)
		self.len_file_piece = len(self.file_piece)
		if self.len_file_piece == 0:
			self.done_readout = True
			if not self.silent_readout:
				self.n = self.showBar_counter #to print last status
				self.n_line = self.len_dat_file #to print 100%
		self.get_next_piece = False
		self.n_line_in_peace = 0


	def _getValueLine(self):
		if self.get_next_piece:
			self._getNextPiece()
		if self.n_line_in_peace < self.len_file_piece:
			self.value_line = self.file_piece[self.n_line_in_peace][:-1].split(
				self.dim_seperator)
			self.n_line += self._readout_every_n_line
			self.n_line_in_peace += self._readout_every_n_line
		else:
			self.get_next_piece = True
			self.n_line += (self.n_line_in_peace  - self.len_file_piece)
			if not self.done_readout:
				self._getValueLine()


	def _printStatus(self):
		if not self.silent_readout:
			if self.n == self.showBar_counter:
				_utils.statusBar(self.n_line+1,self.len_dat_file)
				self.n = 0
			self.n+= 1


	def _resetReadout(self):
		self._resetStandard()
		self._initPrintStatus()
