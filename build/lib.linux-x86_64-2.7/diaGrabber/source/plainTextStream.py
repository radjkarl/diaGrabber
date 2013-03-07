# -*- coding: utf-8 *-*
#from copy import deepcopy
#import select
import time
import sys#, os
#import fcntl
import subprocess
import linecache


from _dimension import _dimension
from _source import _source

class plainTextStream(_source):
	def __init__(self, command, start_via, stop_via, dim_seperator, output_file,
		data_type = "unknown",
		key_to_end_process = "",
		readoutEverNLine = 1,
		infoEveryNLines = 1000):

		super(plainTextStream,self).__init__(data_type)
		#self.dimension = _dimension._dimension
		self.file_name = output_file
		self._command = command
		#self.file_name = command
		self.key_to_end_process = key_to_end_process
		self.dim_seperator = dim_seperator
		self.start_via = start_via
		self.stop_via = stop_via
		self._readoutEverNLine = readoutEverNLine
		self._infoEveryNLines = infoEveryNLines
		
	class dimension(_dimension):
		'''...test'''
		def __init__(self, name, index=0):
			'''index = [collumn in the output-file of your stream] e.g. 2'''
			try:
				self.index = int(index)
			except TypeError:
				self.index = 0
			super(plainTextStream.dimension, self).__init__(name, self.index)
			


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




	#def _non_block_read(self, output):
		#''' even in a thread, a normal read with block until the buffer is full '''
		#fd = output.fileno()
		#fl = fcntl.fcntl(fd, fcntl.F_GETFL)
		#fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)
		#try:
			#return output.read().strip().split("\n")
		#except:
			#return []





	def _prepareReadOut(self, matrixClass):
		self._prepareStandard(matrixClass)
		#start stream
		#sys.stdin.write(b"%s\n" %self.key_to_end_process)
		#from tempfile import SpooledTemporaryFile as tempfile
		#self.tempfile = tempfile()
		self.engine = subprocess.Popen(
			self._command,
			bufsize=1,
			#shell=True,
			#close_fds=True,
			stdin =sys.stdin,#self.tempfile,#
			stdout=sys.stdout,#subprocess.PIPE,
			#stderr=subprocess.PIPE)
			)
		if self.start_via != "":
			#print self.start_via,44
			self.engine.stdin.write(b"%s" %self.start_via)
			self.engine.stdin.flush()

		#self.engine.stdin.close()#preventing senseless waiting
		#self.engine.terminate()

		#self.done_reading_old_output = True
		#self.done_readout = False
		#self.output = []
		self.pos_output = 0
		self.read_n_lines = 0
		self.step_n_lines = 0
		step = 0
		max_try = 5
		while True:#step < max_steps:
			try:
				self.len_output =  len(file(self.file_name, "r").readlines())
				break
			except IOError:#found no readable file called self.file_name
				if step == 0:
					print "found no file called %s" %self.file_name
				step+=1
				print "try again %s times" %(max_try-step)
				time.sleep(1)
				if step == max_try:
					print "ERROR: doest your output_file exist?"
					done_readout = self._endReadOut() # end subprocess
					time.sleep(1)
					sys.exit()


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
		finally:
			return True

	def _readOut(self, readout_interrupt, end_readOut):
		
		# ensure, that the process will terminate
		if end_readOut:
			done_readout = self._endReadOut()
		else:
			done_readout = False



	#def _readOut(self, readout_one_line, end_readOut):
		while True:#self.pos_output < self.len_output:
			#i = self.readOut_range[self.step_in_readOut_range]
			try:
		#for i in readOut_range:
				line = linecache.getline(self.file_name, self.pos_output+1)
				#linecache.clearcache()
				file_dim = line[:-2].split(self.dim_seperator)
				
				self._assignValues(file_dim)
				
				self.pos_output += self._readoutEverNLine
				self.read_n_lines += 1
				self.step_n_lines += 1
							
				if self.step_n_lines >= self._infoEveryNLines or \
						self.pos_output >=self.len_output:
					self.len_output =  len(file(self.file_name, "r").readlines())
					perc_done = (self.read_n_lines+1)/float(self.len_output)
					print "readout %s from approx. %s lines (%s Percent)" %(self.read_n_lines,
							self.len_output,perc_done)
					self.step_n_lines = 0
					if perc_done >=1.0:
						print 333, perc_done
						done_readout = self._endReadOut()
						break
				if readout_interrupt:
					done_readout=False
					break
					
					
			except KeyboardInterrupt:
				done_readout = self._endReadOut()


		return done_readout
