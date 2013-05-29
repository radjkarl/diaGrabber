# -*- coding: utf-8 *-*
#from copy import deepcopy
#import select
import time
import sys, os
from sys import stdout, stdin
try:
	import fcntl
except ImportError:
	print "import of 'stream'-module failed. at the moment 'stream' only works on linux."
import subprocess

import _source
import _dimension

from diaGrabber import _utils

class stream(_source.source):
	'''
	Readout values from a process which produces unlimited or limited output to RAM.
	The process output after the following scheme::

		time0 --> "value00 value01 value02"
		time1 --> "value10 value11 value12"
		...
	
	Where the values of all dimensions are written in one line, seperated by one or
	more signs like spaces ' ' or tab '\t'.
	'''
	def __init__(self, **kwargs):
		##standard
			#required
		self.file_name = None
		self.dim_seperator = None
		self.stop_via = None

			#optional
		self.data_type = "unknown"
		self.folder = ""
		self.key_to_end_process = ""
		self.run_in_shell = False
		self._readout_every_n_line = 1
		self._infoEveryNLines = 1000
		self.start_via = ""
		self._print_readoutEverNLine = False
		self.silent_readout = False


		#individual
		self.setArgs(**kwargs)
		_utils.checkRequiredArgs({
			"command":self.command,
			"file":self.file_name,
			"dimSeparator":self.dim_seperator,
			"stopVia":self.stop_via})

		super(stream,self).__init__(self.data_type)

		#helpers
		self.engine = None
		self._calc_readoutEverNLine = False
		self._old_stream_len = 0


	def setArgs(self, **kwargs):
		'''
		**Required kwargs** ("keyword arguments") are:

		==================     ========  =================       ============================
		Keyword	               Type      Example                 Description
		==================     ========  =================       ============================
		*command*              string    'python'
		                                 **OR** './'             The command to start the stream
		*file*                 string    'test.py'               The name of the stream
		*dimSeparator*         string    **space**: ' '
		                                 **OR TAB**: '\t'        One or more signs which seperates the values in every line
		*stopVia*              string    'done'                  If the stream is limited
		                                                         this string let's diaGrabber
		                                                         when the stream finishes
		==================     ========  =================       ============================

		**Optional kwargs** ("keyword arguments") are:

		====================   ===========  ==========       ================================
		Keyword	               Type         Default          Description
		====================   ===========  ==========       ================================
		*folder*               string       ""               Name of the parent folder of
		                                                     the stream
		*readoutEveryNLine*    string/int   1                if you don't need every line of
		                                                     your file you can spare time by
		                                                     readout only every n line of it.
		                                                     Most likely the stream generates
		                                                     faster new output than
		                                                     diaGrabber can process, In this
		                                                     case this value has to be
		                                                     greater than 1, Type **'calc'**
		                                                     to let diaGrabber decide this
		                                                     value corresponding to the
		                                                     development of the amount of
		                                                     unprocessed output.
		
		*showCalcNLine*        bool         False            if *readoutEveryNLine* == 'calc'
		                                                     Setting this value to True print
		                                                     out every new calculated value
		                                                     of *readoutEveryNLine*
		
		*infoEveryNLine*       int          1000             Prints every n reaout-lines
		                                                     a status.
		*dataType*             string       "unknown"        for all possible values are
		                                                     defined see :py:func:`diaGrabber.source._source.source._evalDataType`

		*keyToEndProcess*      string       ""               This entry will finish the
		                                                     stream-output
		*runInShell*           bool         False            Decide whether a process has to
		                                                     be called out of a shell.
		                                                     Set this value to True if the
		                                                     stream doesn't start.
		*silentReadout*        bool         False            set True if you dont want to see
		                                                     a statusBar or similar while
		                                                     readOut
		====================   ===========  ==========       ================================
		'''
		
#		*startEntry*           string       ""               Use this key if the stream
#		                                                     waint's an entry to start
#		                                                     producing output
		for key in kwargs:
			if key == "command":
				self.command = str(kwargs[key])
			elif key == "file":
				self.file_name = str(kwargs[key])
			elif key == "dimSeparator":
				self.dim_seperator = str(kwargs[key])
			elif key == "stopVia":
				self.stop_via = str(kwargs[key])
			elif key == "folder":
				self.folder = str(kwargs[key])
			elif key == "readoutEveryNLine":
				self._setReadoutEveryNLine(kwargs[key])
			elif key == "showCalcNLine":
				self._print_readoutEverNLine = bool(kwargs[key])
			elif key == "infoEveryNLine":
				self._infoEveryNLines = int(kwargs[key])
			elif key == "dataType":
				self.data_type = str(kwargs[key])
			elif key == "keyToEndProcess":
				self.key_to_end_process = str(kwargs[key])
			elif key == "runInShell":
				self.run_in_shell = bool(kwargs[key])
			elif key == "silentReadout":
				self.silent_readout  = bool(kwargs[key])
			#elif key == "startEntry":
			#	self.start_via = str(kwargs[key])
			else:
				raise KeyError("keyword '%s' not known" %key)

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

	#def getReadoutEverNLine(self):
	#	return self._readout_every_n_line

	def _setReadoutEveryNLine(self,readout_every_n_line):
		if readout_every_n_line == "calc":
			self._calc_readoutEverNLine = True
			self._readout_every_n_line = 0#symbolic value
		else:
			if self.readout_every_n_line < 1:
				raise ValueError(
					"StreamSources doesn't support negative readoutNLine-Values ")
			else:
				self._readout_every_n_line = int(readout_every_n_line)


	def _getMinMax(self,dims):
		sys.exit("ERROR: source.stream need a given dimension.includeFromTo()-range")

	def _nonBlockRead(self, output):
		''' even in a thread, a normal read with block until the buffer is full '''
		fd = output.fileno()
		fl = fcntl.fcntl(fd, fcntl.F_GETFL)
		fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)
		try:
			return output.read().strip().split("\n")
		except:
			return []

	def _prepareReadOut(self):
		self._prepareStandard()
		#start stream
		print "%s %s" %(self.command,self.dat_file)
		self.engine = subprocess.Popen(
			"%s %s" %(self.command,self.dat_file),
			bufsize=-1,
			stdin = sys.stdin,
			shell = self.run_in_shell,
			stdout=subprocess.PIPE,
			stderr=subprocess.PIPE)
		#if self.start_via != "":
		#	for i in range(10):
		#		self.engine.stdin.write("%s\n" %self.start_via)
		#		print i
			#stdin.write(b"%s\n" %self.start_via)
			#print("%s\n" %self.start_via)
			#print ""
			#self.engine.stdin.flush()

		self.done_reading_old_output = True
		self.done_readout = False
		self.output = []
		self.len_output = 0
		self._old_len_output = 0
		self._max_len_output = 0
		self.pos_output = 0
		self.read_n_lines = 0
		self.step_n_lines = 0

	def _endReadOut(self):
		try:
			if self.key_to_end_process != "":
				print "finish process via key ' %s '" %self.key_to_end_process
				for h in range(10): # to ensure ending
					###dont work at the moment
					self.engine.stdin.write(b"%s" %self.key_to_end_process)
					#self.engine.stdin.flush()
					#self.engine.stdin.close()
		except (IOError, AttributeError):
			pass
		try:
			print "closing process"
			time.sleep(1)
			#for h in range(10):
			#self.engine.close()
			self.engine.kill()
			#self.engine.wait()
		except (IOError, AttributeError):
			pass

	def _getNewOutput(self):
		#get new output
		self.output = self._nonBlockRead(self.engine.stdout)
		#reset position
		if self.len_output > 0:
			self.len_output -=1
		self.pos_output -= self.len_output
		self._old_len_output = self.len_output
		self.len_output = len(self.output)

	def _getValueLine(self):

		while self.pos_output >= self.len_output or self.len_output <= 1:#got no output
			self._getNewOutput()
			if self._calc_readoutEverNLine:
				self._calcReadoutEverNLine()
		line = self.output[self.pos_output]
		if line == self.stop_via:
			self._endReadOut()
			self.done_readout = True
			return
			#raise StopIteration
		self.read_n_lines += 1
		self.step_n_lines += 1
		self.pos_output += self._readout_every_n_line
		#return line.split(self.dim_seperator)
		self.value_line = line.split(self.dim_seperator)

	def _calcReadoutEverNLine(self):
		'''calculates self._readout_every_n_line according to the increase of stdout'''
		#refresh max_len_output
		if self.len_output > self._max_len_output:
			self._max_len_output = self.len_output

		if self._readout_every_n_line == 0:
			#init
			self._readout_every_n_line = int(0.5 * self.len_output)

		elif self.len_output == self._max_len_output:
			#in this case it seems to be that the max buffersize i reached
			#thats not desired because now output-information will get lost
			#therefore we make a big step, like ...
			 self._readout_every_n_line = self._max_len_output#self.len_output

		elif self.len_output == 0:# or self._old_len_output == 0:
			#maybe we readout to fast -> downsize readout-step
			#or thers no new output becuse the stream finisht -> we have time to process
			#	every step
				self._readout_every_n_line -= 1
			
		else:
			#delta_len_output = self.len_output - self._old_len_output
			if self.len_output - self._old_len_output > 0:
				self._readout_every_n_line += 1
			else:
				self._readout_every_n_line -= 1
	
		if self._readout_every_n_line == 0:
			self._readout_every_n_line = 1


	def _printStatus(self):
		if not self.silent_readout:
			if self.step_n_lines == self._infoEveryNLines:
				print "readout %s lines" %self.read_n_lines
				self.step_n_lines = 0
				if self._print_readoutEverNLine:
					print "readout every %s line" %self._readout_every_n_line


	def _resetReadout(self):
		self._resetStandard()
		# if process still running
		if self.engine and self.engine.poll():
			self._endReadout()

