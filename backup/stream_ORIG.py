# -*- coding: utf-8 *-*
#from copy import deepcopy
from sys import exit
import os
import select
import subprocess
import time
import fcntl

#from cStringIO import StringIO


from . import _dimension
from _source import _source

class stream(_source):
	def __init__(self, command, start_via, stop_via,
			dim_seperator, data_type = "unknown", key_to_end_process = ""):

		super(stream,self).__init__(data_type)
		self.command = command
		self.file_name = command
		self.key_to_end_process = key_to_end_process
		#self.key_to_kill_process = key_to_kill_process
		#self.folder = folder
		#if self.folder[-1] != "/":
		#	self.folder += "/"
		#self.dat_file = self.folder + self.file_name
		self.dim_seperator = dim_seperator
		self.start_via = start_via
		self.stop_via = stop_via
		#self.readout_every_n_line = 1
		#self.len_dat_file = len(file(self.dat_file, "r").readlines())
		self.dimension = _dimension.dimension

		#loading stream-file
		
		#target = "%s %s" %(self.command, self.dat_file)
		PIPE = subprocess.PIPE
		self.engine = subprocess.Popen(self.command, shell=True, bufsize=-1, stdin=PIPE, stdout=PIPE, stderr=PIPE)

		fcntl.fcntl(
			self.engine.stdout.fileno(),
			fcntl.F_SETFL,
			fcntl.fcntl(self.engine.stdout.fileno(), fcntl.F_GETFL) | os.O_NONBLOCK)
		for line in self.engine.stdout:
			print line
		#self.engine.stdin.write("wsf\n")
		#print self.engine.stdout.readline()
		
	def _prepareReadOut(self, matrixClass):
		self._prepareStandard(matrixClass)
		#start stream
		if self.start_via != "":
			self.engine.stdin.write(b"%s\n" %self.start_via)
			self.engine.stdin.flush()
		
		self.proc_stdout = _LineReader(self.engine.stdout.fileno())
		self.proc_stderr = _LineReader(self.engine.stderr.fileno())
		self.readable = [self.proc_stdout, self.proc_stderr]
		
		self.check_duration = 1 #check every n seconds whether stream-engine is big enough
		self.end_of_stream = False
		self.delta_n_lines = 1000
		self.read_n_lines = 0
		self.step_n_lines = 0

	def _readOut(self, readout_interrupt, end_readOut):

		
		while self.readable and not self.end_of_stream:
		#try:
			#if self.key_to_kill_process != "":
			#	out = keyPressed()
			#	if out == self.key_to_kill_process:
			#		self.engine.stdin.write(b"%s" %out)
			#		
			
			#self.proc_stderr.readlines()

				
			ready = select.select(self.readable, [], [], self.check_duration)[0]
			if not ready:
				print "... collecting"
				continue
			for stream in ready:
				lines = stream.readlines()
				#print lines
				if lines is None:
					# got EOF on this stream
					self.readable.remove(stream)
					continue
				for line in lines:
					if line == self.stop_via:
						self.end_of_stream = True
						break
					file_dim = line.split(self.dim_seperator)
					
					print file_dim
					#print step_n_lines, delta_n_lines
					self.read_n_lines += 1
					self.step_n_lines += 1

					self._assignValues(file_dim)
								
					if self.step_n_lines == self.delta_n_lines:
						print "readout %s lines" %self.read_n_lines
						self.step_n_lines = 0
						
				

				
			# ensure, that the process will terminate
			if end_readOut:
				#time.sleep(1)
				try:
					if self.key_to_end_process != "":
						print "finish process via key '%s'" %self.key_to_end_process
						for h in range(10): # to ensure ending
							self.engine.stdin.write(b"%s" %self.key_to_end_process)
				except IOError:
					pass
				try:
					print "closing process"
					self.engine.stdin.close()
				except IOError:
					pass
				return True #i'm done


			if readout_interrupt:
				return False

		#return mergeMatrix, densityMatrix
	
	

	
	
	def _getMinMax(self,dims):
		exit("ERROR: source.stream need a given dimension.includeFromTo()-range")
	

class _LineReader(object):

	def __init__(self, fd):
		self._fd = fd
		self._buf = ''

	def fileno(self):
		return self._fd

	def readlines(self):
		#print 55, self._fd
		data = os.read(self._fd, 4096)
		#print data
		if not data:
			# EOF
			return None
		self._buf += data
		if '\n' not in data:
			return []
		tmp = self._buf.split('\n')
		lines, self._buf = tmp[:-1], tmp[-1]
		return lines
	
