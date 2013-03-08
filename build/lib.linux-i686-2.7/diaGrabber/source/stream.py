# -*- coding: utf-8 *-*
#from copy import deepcopy
#import select
import time
import sys, os
import fcntl
import subprocess

import _source

class stream(_source.source):
	def __init__(self, command, start_via, stop_via, dim_seperator,
		data_type = "unknown",
		key_to_end_process = "",
		run_in_shell = False,
		readoutEverNLine = 1,
		infoEveryNLines = 1000):

		super(stream,self).__init__(data_type)
		#self.dimension = _dimension._dimension

		self._command = command
		self.run_in_shell = run_in_shell
		self.file_name = command
		self.key_to_end_process = key_to_end_process
		self.dim_seperator = dim_seperator
		self.start_via = start_via
		self.stop_via = stop_via
		self._readoutEverNLine = readoutEverNLine
		self._infoEveryNLines = infoEveryNLines

	#class dimension(_dimension):
		#'''...test'''
		#def __init__(self, name, index=0):
			#'''index = [collumn in your stream-output] e.g. 2'''
			#try:
				#self.index = int(index)
			#except TypeError:
				#self.index = 0
			#super(stream.dimension, self).__init__(name, self.index)

	def basisDimension(self, name, index,  resolution, includeMethod=""):
		'''
		:class:`diaGrabber.source._dimension.basisDimension` \n
		'''	
		new_dimension  = _source.basisDimension(name, index, resolution, includeMethod)
		self.basis_dim.append(new_dimension)
		return new_dimension


	def mergeDimension(self, name, index, mergeMethod=""):
		'''
		:class:`diaGrabber.source._dimension.mergeDimension` \n
		'''	
		new_dimension  = _source.mergeDimension(name, index, mergeMethod)
		self.merge_dim.append(new_dimension)
		return new_dimension



	def setInfoEveryNLines(self,nLines):
		self._infoEveryNLines = int(nLines)
	def getInfoEveryNLines(self):
		return self._infoEveryNLines
	

	def setReadoutEverNLine(self,nLine):
		self._readoutEverNLine = int(nLine)
	def getReadoutEverNLine(self):
		return self._readoutEverNLine
	

	def _getMinMax(self,dims):
		sys.exit("ERROR: source.stream need a given dimension.includeFromTo()-range")




	def _non_block_read(self, output):
		''' even in a thread, a normal read with block until the buffer is full '''
		fd = output.fileno()
		fl = fcntl.fcntl(fd, fcntl.F_GETFL)
		fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)
		try:
			return output.read().strip().split("\n")
		except:
			return []





	def _prepareReadOut(self, matrixClass):
		self._prepareStandard(matrixClass)
		#start stream
		self.engine = subprocess.Popen(
			self._command,
			bufsize=-1,
			stdin=sys.stdin,
			shell = self.run_in_shell,
			stdout=subprocess.PIPE,
			stderr=subprocess.PIPE)
		if self.start_via != "":
			self.engine.stdin.write(b"%s\n" %self.start_via)
			self.engine.stdin.flush()

		self.done_reading_old_output = True
		self.done_readout = False
		self.output = []
		self.len_output = 0
		self.pos_output = 0
		self.read_n_lines = 0
		self.step_n_lines = 0

	def _endReadOut(self):
		try:
			if self.key_to_end_process != "":
				print "finish process via key ' %s '" %self.key_to_end_process
				for h in range(10): # to ensure ending
					#sys.stdin.write(b"%s\n" %self.key_to_end_process)

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
		#finally:
			#return True

	#def _readOut(self, readout_interrupt, end_readOut):
		#
		## ensure, that the process will terminate
		#if end_readOut:
			#done_readout = self._endReadOut()
		#else:
			#done_readout = False

		#done_one_line = False
		#while not done_readout and not done_one_line:
			#try:
				#if self.done_reading_old_output:
					##get new output
					#self.output = self._non_block_read(self.engine.stdout)
					##reset position
					#if self.len_output > 0:
						#self.len_output -=1
					#self.pos_output -= self.len_output
	#
					#self.len_output = len(self.output)
					#self.done_reading_old_output = False
				#
				#if self.len_output <= 1: #got no output
					#self.done_reading_old_output = True
				#
				#else: #process output
					#while self.pos_output < self.len_output:
						#line = self.output[self.pos_output]
						#if line == self.stop_via:
							#done_readout = self._endReadOut()
							#break
						#file_dim = line.split(self.dim_seperator)
						#self.read_n_lines += 1
						#self.step_n_lines += 1
						#
						##self._assignValues(file_dim)
						#in_range = self._getBasisMergeValues(file_dim)
						#if in_range:
							#self.matrixClass._assign(self.basis_values, self.merge_values)
						#
						#
						#self.pos_output += self._readoutEverNLine
						#if self.step_n_lines == self._infoEveryNLines:
							#print "readout %s lines" %self.read_n_lines
							#self.step_n_lines = 0
		#
						#if readout_interrupt:
							#done_one_line = True
							#break
						#if self.pos_output+1 >= self.len_output:
							#break
					#if self.pos_output+1 >= self.len_output:
						#self.done_reading_old_output = True
						#
			#except KeyboardInterrupt:
				#done_readout = self._endReadOut()
		#return done_readout


	def _getNewOutput(self):
		#get new output
		self.output = self._non_block_read(self.engine.stdout)
		#reset position
		if self.len_output > 0:
			self.len_output -=1
		self.pos_output -= self.len_output
		#print self.pos_output,77

		self.len_output = len(self.output)
		#self.done_reading_old_output = False

	def _getFileDim(self):
		#if self.done_reading_old_output:
		#	self._getNewOutput()
		
		#if self.len_output <= 1: #got no output
		#	self.done_reading_old_output = True
		#	self._getFileDim()
		#else: #process output
		while self.pos_output >= self.len_output or self.len_output <= 1:#got no output
			#self.pos_output -= self.len_output
			#self.done_reading_old_output = True
			self._getNewOutput()
				#print 55
			#else:
		#print self.pos_output, self.len_output, len(self.output)
		line = self.output[self.pos_output]
		if line == self.stop_via:
			self._endReadOut()
			raise StopIteration
			
		self.read_n_lines += 1
		self.step_n_lines += 1
		
		
		
		self.pos_output += self._readoutEverNLine



		#if self.pos_output+1 >= self.len_output:
		#	self.done_reading_old_output = True
		#print line.split(self.dim_seperator)
		return line.split(self.dim_seperator)

	def _printStatus(self):
		if self.step_n_lines == self._infoEveryNLines:
			print "readout %s lines" %self.read_n_lines
			self.step_n_lines = 0

	def _resetReadOut(self):
		pass
