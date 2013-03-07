# -*- coding: utf-8 *-*
from sys import stdout#, stderr#for statusBar
import os
from copy import deepcopy
import numpy as np

def statusBar(step, total, bar_len):
	'''print a statusbar like:
[===o----] 40%
step  = your iterator e.g. 0,1,2,3
total = target-value e.g. 10
bar_len = len of the statusbar
'''
	norm=100/total
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

def prepareFileSystem(file_name, folder_name = ""):
	'''generate the necassary folrderstrukture to save 'file_name' in 'folder_name'
	return a composed file_name like ../analyzed/folder/file'''
	#main_folder = "../analyzed/"
	if folder_name != "":
		folder_step = ""#folder_list[0]
		for i in folder_name.split("/"):
			folder_step += i
			if os.path.isdir(folder_step) == False:
				os.mkdir(folder_step)
	#if folder_name != "":
		#if os.path.isdir(main_folder + folder_name) == False:
			#os.mkdir(main_folder + folder_name)
			
		if folder_name[-1] != "/":
			folder_name += "/"
		#file_name = main_folder  + folder_name +"/" + file_name
	#else:
	#	file_name = main_folder + file_name
	file_name = folder_name + file_name
	return file_name


def nanToZeros(matrix):
	'''change all nan-values in a given nD-array to 0'''
	whereAreNaNs = np.isnan(matrix)
	matrix2 = deepcopy(matrix)
	matrix2[whereAreNaNs] = 0
	return matrix2


def legalizeFilename(filename):
	import string, unicodedata
	validFilenameChars = "/-_.%s%s" % (string.ascii_letters, string.digits)
	filename = unicode(filename.replace(" ","-").replace("ä","ae").replace("ö","oe").replace("ü","ue"))
	cleanedFilename = unicodedata.normalize('NFKD', filename).encode('ASCII', 'ignore')
	return ''.join(c for c in cleanedFilename if c in validFilenameChars)[:255]



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
