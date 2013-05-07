# -*- coding: utf-8 *-*
from sys import stdout, exit
import os
from copy import deepcopy
import numpy as np
import inspect
import bottleneck as bn


def statusBar(step, total, bar_len=20):
	'''print a statusbar like:
[===o----] 40%
step  = your iterator e.g. 0,1,2,3
total = target-value e.g. 10
bar_len = len of the statusbar
'''
	norm=100.0/total
	step *= norm
	step = int(step)
	increment = 100/bar_len
	n = (step / increment)
	m = bar_len - n
	stdout.write("\r[" + "="*n +"o" +  "-"*m + "]" +  str(step) + "%")
	stdout.flush()


def pktAbs(vector):
	'''calculate the magnitude of a given vector'''
	a = 0
	for i in vector:
		a += i**2
	a = a**0.5
	return a


def pktAbs2(p1,p2):
	'''calculate the distance between two given n-dimensionnal points'''
	vector = deepcopy(p1)
	for i in range(len(p1)):
		vector[i] = abs(p1[i]-p2[i])
	a = 0
	for i in vector:
		a += i**2
	a = a**0.5
	return a


def recursive(coll):
	'''
	Return a generator for all atomic values in coll and its subcollections.
	An atomic value is one that's not iterable as determined by iter.
	'''
	try:
		k = iter(coll)
		for x in k:
			for y in recursive(x):
				yield y
	except TypeError:
		yield coll


def adaptMasterStaticsToSlaveDict(master,slave):
	'''
	copy all stativ values of type int, str and float from an arbitrary nested
	master-dictionary to a same-shaped slave dict
	trough this method the slave keep all of its (dynamic) content
	master and slave has to have the same structure!
	'''
	def print_dict(master,slave):
		'''allow recustive call'''
		for (k1, v1),(k2,v2) in zip(master.iteritems(),slave.iteritems()):
			if k1 == k2:
				if isinstance(v1, dict) and len(v1) != 0:
					v1,v2 = print_dict(v1,v2)
				elif isinstance(v1, str) or isinstance(v1, int) or isinstance(v1, float):
					if v1 != v2:
						slave[k1] = v1
			return v1,v2
	print_dict(master,slave)
	return slave


def prepareFileSystem(file_name, folder_name = ""):
	'''generate the necassary folrderstrukture to save 'file_name' in 'folder_name'
	return a composed file_name like ../analyzed/folder/file'''
	if folder_name != "":
		if folder_name[-1] != "/":
			folder_name += "/"
		file_name = folder_name + file_name
	folder_step = ""
	for i in file_name.split("/")[:-1]:
		folder_step += i + "/"
		if os.path.isdir(folder_step) == False:
			os.mkdir(folder_step)
	return file_name


def nearestPosition(array, value):
	difference_list = array - value
	difference_list = abs(difference_list)
	return difference_list.argmin()


def checkRequiredArgs(kwargs):
	not_def = ""
	for key in kwargs:
		if kwargs[key] == None:
			not_def += ", %s" %key
	if not_def != "":
		raise KeyError("required keyArgs where not set: %s"
			%(not_def[1:]) )


def nanToZeros(matrix, value=0):
	'''change all nan-values in a given nD-array to 0'''
	#whereAreNaNs = np.isnan(matrix)
	matrix2 = deepcopy(matrix)
	#matrix2[whereAreNaNs] = 0
	bn.replace(matrix2, np.nan, value)
	return matrix2


def legalizeFilename(filename):
	import string, unicodedata
	validFilenameChars = "/-_.%s%s" % (string.ascii_letters, string.digits)
	filename = unicode(filename.replace(" ","-").replace("ä","ae").replace("ö","oe").replace("ü","ue"))
	cleanedFilename = unicodedata.normalize('NFKD', filename).encode('ASCII', 'ignore')
	return ''.join(c for c in cleanedFilename if c in validFilenameChars)[:255]


def linspace(a, b, n):
	n = int(n)
	if n < 2:
		return b
	diff = (float(b) - a)/(n - 1)
	return [diff * i + a  for i in range(n)]


def linspace2(a, b, n):
	'''exclude the boundayries'''
	###very unclean ...
	a = linspace(a, b, n+1)
	a.pop(-1)
	diff01 = (a[1]-a[0])/2
	for i in range(len(a)):
		a[i] += diff01
	return a


def checkClassInstance(classInstance, prooveClass, returnFalseThanExit=False):
	'''
	check whether 'classInstance' is instance of class 'prooveClass'
	exit if not
	'''
	if classInstance.__class__.__name__ != prooveClass.__name__:
		if returnFalseThanExit:
			return False
		else:
			exit("ERROR: instance %s has to be an instance of class %s" %(
				classInstance, prooveClass))
	else:
		return True


def checkModuleInstance(instance, prooveModule, returnFalseThanExit=False):
	'''
	check whether 'instance' is instance of one class in module 'prooveModule'
	exit if not
	'''
	#check whether mergeMethod is a instande of one class in diagrabber-methods.merge
	all_prooveModule_classes = getAvailableClassesInModule(prooveModule)
	instance_of_some_class_in_prooveModule = False
	for m in all_prooveModule_classes:
		if isinstance(instance, m):
			instance_of_some_class_in_prooveModule = True
	if not instance_of_some_class_in_prooveModule:
		if returnFalseThanExit:
			return False
		else:
			exit("ERROR: instance %s has to be an instance of classes in the module %s" %(instance, prooveModule))
	else:
		return True


def getAvailableClassesInModule(prooveModule):
	return tuple(x[1] for x in inspect.getmembers(prooveModule,inspect.isclass))


def countLines(filename):
	f = open(filename)
	try:
		lines = 1
		buf_size = 1024 * 1024
		read_f = f.read # loop optimization
		buf = read_f(buf_size)
		# Empty file
		if not buf:
			return 0
		while buf:
			lines += buf.count('\n')
			buf = read_f(buf_size)
		return lines
	finally:
		f.close()


class Logger:
	'''writes into log-file and on screen at the same time'''
	from time import ctime

	def __init__(self, stdout, filename):
		self.stdout = stdout
		self.logfile = file(filename, 'a')
		self.logfile.write('\n\n####################################\nNew run at %s\n####################################\n\n' % ctime())

	def write(self, text):
		self.stdout.write(text)
		self.logfile.write(text)
		self.logfile.flush()

	def close(self):
		"""Does this work or not?"""
		self.stdout.close()
		self.logfile.close()