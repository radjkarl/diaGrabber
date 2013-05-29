# -*- coding: utf-8 *-*
#own
from diaGrabber import  _utils
from diaGrabber.plot._preferenceDock import preferenceDock
#foreign
import sys
import numpy as np
import bottleneck as bn
import signal
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
import pyqtgraph.dockarea as pgDock
from copy import deepcopy


class Gui(object):
	'''
	This class provides a graphical frontend for viewing n-dimensional targets.
	Since it's only possible to visualize exact either n mergeDimensions over one
	basisDimension (2d-graph) or one mergeDimension over two basisDimensions
	(merge coded als contrast/color) without deforming the values in the figure
	only at max. two basisDimensions are shown. All other basisDimensions were
	conentrated. By default all merge-values over that dimensions werde middled.
	
	In this class you have many options to choose which basis to show and in
	which way to concentrate other basisDimensions.
	It is also possible to slice a target and to view another basis.
	
	Each parameter and each botton controling the view is described in :class:`diaGrabber.plot._preferenceDock.preferenceDock`.
	
	Though it's possible to customize the Gui you can also preconfigure the Gui
	by setting keyword-arguments when initializing the class.
	
	For a list of all possible keyword-arguments have a look at :py:func:`setArgs`
	'''
	def __init__(self, matrixClass, **kwargs):
		#imports
		self.matrixClass = matrixClass
		self._merge_dim = self.matrixClass._merge_dim
		self._basis_dim = self.matrixClass._basis_dim

		#standard
		self.interactive = False
		self._setFPS(20)
		self.limitReadoutRate = False
		self._setLPS(1)
		self.preferenceDock_size = 350
		self.windowSize = [1200,600]
		self.display_size = int((self.windowSize[0]-self.preferenceDock_size)/2)
		self.enableAutoRange = []
		self.showType = "together"
		self._setColorTheme("default")
		self.build_preferences_dock = True
		self.end_readOut = False
		self.closeWhenFinished = False
		self.printChanges = False # whether to print every change in the preferenceDock

		#individual
		self.setArgs(**kwargs)

		#helpers
		self.hasInteractiveModus = True
		self.save_img = False
		self.show_window = True
		self.plot_method_executed = False
		self.done_readOut = False
		self.app = None


	def plot(self, **kwargs):
		'''
		For a list of all possible Keyword-arguments have a look at :py:func:`setArgs`
		'''
		self.plot_method_executed = True
		
		#by default: show everything except sth. else is defined in kwargs
		self.show_dim_list = []
		for n in range(len(self._merge_dim)):
			#as standard: display every one merge over every basis
			self.show_dim_list.append([[n],range(len(self._basis_dim))])
		
		self.setArgs(**kwargs)

		##create qt-window
		if self.app == None:
			self.app = QtGui.QApplication([])
			self.app.aboutToQuit.connect(self._quitApp)#ensure that closing realy close qt
		# exit,when strg+c are pressed
		signal.signal(signal.SIGINT, self._quitApp)

		self.win = QtGui.QMainWindow()
		self.win.resize(self.windowSize[0],self.windowSize[1])
		self.area = pgDock.DockArea()
		self.win.setCentralWidget(self.area)
		#create prefercence dock
		self._preferencesDock = preferenceDock(self)
		self._createDisplays()

		self.win.show()

		def updateValues():
			if not self.done_readOut:
				#lineWise updating data
				self.done_readOut = self.matrixClass._fill(True, self.end_readOut)
				if self.done_readOut or self.done_readOut == None:
					print "readout complete!"
					if self.closeWhenFinished:
						self._quitApp()
					else:
						self._updateDisplays()#do a last update to get the latest values
			else:
				#stop the timers because readout is done
				self.timerFPS.stop()
				self.timerLPS.stop()
				if self.save_img:
					self._save()
		if self.interactive:
			#set timer
			self.timerLPS = QtCore.QTimer()
			#get new basis-merge-values
			self.timerLPS.timeout.connect(updateValues)
			self.timerLPS.start(self.wait_ms_lps)
			self.timerFPS = QtCore.QTimer()
			self.timerFPS.timeout.connect(self._updateDisplays)
			self.timerFPS.start(self.wait_ms)

		else: #static plotting
			self._updateDisplays()
			if self.save_img:
				self._save()

		if not self.show_window:
			self._quitApp()
		elif (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
			self.app.exec_()

		self.plot_method_executed = False #reset


	def setArgs(self, **kwargs):
		'''
		Optional kwargs ("keyword arguments") are:

		====================   ========  ===========      ============================
		Keyword	               Type      Default          Description
		====================   ========  ===========      ============================
		*interactive*          bool      False            [True, False]
		*show*	               list      [{All}]          a list of lists containing names of merge-(m) and basisDimensions(b) to show e.g. show = [ (m1,b1,b2), (m2,b2) ]
		*fps*                  float     20               frames per seconds
		*lps*                  float     None              readout n lines from source per second (needs limitReadoutRate = True)
		*limitReadoutRate*     bool      False            Choose whether to limit the readoutrate via arg *lps*
		*enableAutoRange*      list      []               ["x", "y"]
		*colorTheme*           string    "default"        ["default", "bright"]
		*windowSize*           list      [1000,600]       [size_x, size_y]
		*showPreferences*      bool      True             [True, False]
		*closeWhenFinished*    bool      False            [True, False] Choose whether to close the plot-window when fillInteractive() is done
		*save*                 dict      {}               can include all keywords from the method 'save'
		====================   ========  ===========      ============================
		'''

		#individual
		for key in kwargs:
			if key == "interactive":
				self.interactive = bool(kwargs[key])
			elif key == "show":
				#e.g.: show = [ (m1,b1,b2), (m2,b2) ]
				self.show_dim_list = []
				for v in kwargs[key]:
					if (type(v) == list or type(v) == tuple) and len(v) >= 2:#valid
						self.show_dim_list.append([[],[]])#[[merges],[basis']]
						for w in v:
							#check for merge
							found = False
							for i,m in enumerate(self._merge_dim):
								if m.name == w:
									self.show_dim_list[-1][0].append(i)
									found = True
									break
							#check for basis
							if not found:
								for i,b in enumerate(self._basis_dim):
									if b.name == w:
										self.show_dim_list[-1][1].append(i)
										found = True
										break
							if not found:
								raise KeyError("name in show '%s' not valid!" %w)
							if None in self.show_dim_list[-1]:
							#else:
								raise KeyError("list-entries for 'show' has to be names of at least one basis- and one mergeDimension")
					else:
						raise KeyError("values for 'show' have to be a list of lists of dimensions")
			elif key == "fps":
				if kwargs[key] != self.fps:
					self._setFPS(kwargs[key])
			elif key == "lps":
				if (kwargs[key] != self.lps or not self.limitReadoutRate):
					self.limitReadoutRate = True
					self._setLPS(kwargs[key])
			elif key == "limitReadoutRate":
					self.limitReadoutRate = bool(kwargs[key])
					
			elif key == "enableAutoRange":
				self.enableAutoRange = kwargs[key]
			elif key == "colorTheme":
				if kwargs[key] != self.colorTheme:
					self._setColorTheme(kwargs[key])
			elif key == "windowSize":
				self.windowSize = list( int(kwargs[key][0]), int(kwargs[key][1]) )
			elif key == "showPreferences":
				self.build_preferences_dock = bool(kwargs[key])
			elif key == "closeWhenFinished":
				self.closeWhenFinished = bool(kwargs[key])
			elif key == "save":
				self.save(**kwargs[key])
			elif key == "printChages":
				self.printChanges = bool(kwargs[key])
			else:
				raise KeyError("keyword '%s' not known" %key)


	def save(self,**kwargs):
		'''
		Optional kwargs ("keyword arguments") are:

		==================     ========  =======          ============================
		Keyword	               Type      Default          Description
		==================     ========  =======          ============================
		*mergeName*            string    [{All}]          names of merges to save
		*name*	               string    ""               name-prefix of the image
		*type*                 string    "png"            typ of the image ["png","jpg","tiff","svg"]
		*parameters*           list      []               takes all parameters accepted by pyQtGraph.exporters
		==================     ========  =======          ============================
		'''
		self.save_img = True
		#standard
		self.img_name = ""
		self.merge_to_save = range(len(self._merge_dim))#show all merge-dim
		self.img_type = "png"
		self.img_parameters = []
		#individual
		for key in kwargs:
			if key == "mergeName":
				self.merge_to_save = []
				mergeNames = kwargs[key]
				if type(mergeNames) != list or type(mergeNames) != tuple:
					mergeNames = [mergeNames]
				for mergeName in mergeNames:
					found_merge = False
					for m in self._merge_dim:
						if m.name == mergeName:
							self.merge_to_save.append(m._mergeIndex)
							found_merge = True
							break
					if not found_merge:
						raise KeyError("mergeName %s not valid!" %mergeName)
			elif key == "name":
				self.img_name = str(kwargs[key])
			elif key == "type":
				self.img_type = str(kwargs[key]).lower()#only lower-size-letters
				if self.img_type not in ["png","jpg","tiff","svg"]:
					raise KeyError("save-type '%s' not valid" %self.img_type)
			elif key == "parameters":
				self.img_parameters = dict(kwargs[key])
			else:
				raise KeyError("keyword '%s' not known" %key)

		if not self.plot_method_executed:#no plot created so far
			self.show_window = False
			self.interactive = False
			self.plot()#do the plotting stuff without showing user

##private
################


	def _save(self):
		for n,d in enumerate(self.display_list):
			is_merge_in_view = False
			for i_merge in self.merge_to_save:
				if i_merge in d.show_merge:
					is_merge_in_view = True
					break
			if is_merge_in_view:
				# create an exporter instance, as an argument give it
				# the item you wish to export
				if self.img_type == "svg":
					exporter = pg.exporters.SVGExporter.SVGExporter(d.view)
				else:
					exporter = pg.exporters.ImageExporter.ImageExporter(d.view)
				for p in self.img_parameters:
					# set export parameters if needed
					try:
						exporter.parameters()[p] = self.img_parameters[p]
					except (Exception):
						print "KeyError: save-type '%s' doesn't support parameter '%s'  ...continue without it" %(self.img_type, p)

				merge_names = ""
				for i in d.show_merge:
					merge_names += "_%s" %self._merge_dim[i].name
				# save to file
				exporter.export(self.img_name + merge_names +"." + self.img_type)
		self.save_img = False #reset


	def _updateDisplays(self):
		for d in self.display_list:
			d.update()


	def _quitApp(self,signum=None, frame=None):
		if self.interactive:
			self.matrixClass._resetReadout()
			self.timerLPS.stop()
			self.timerFPS.stop()
		self.interactive = False
		self.app.closeAllWindows()
		self.app.quit()


	def _addToArea(self, display):
		args = {}
		l=len(self.display_list)
		if l > 1:
			if l == 2:
				args["position"] = 'right'
				args["relativeTo"] = self.display_list[-2].dock
			elif l < 5:
				args["position"] = 'bottom'
				args["relativeTo"] = self.display_list[-3].dock
			else:
				args["position"] = 'below'
				args["relativeTo"] = self.display_list[-2].dock
		self.area.addDock(display, **args)


	def _createNewDisplay(self):
		max_index = 0
		for i in self.display_list:
			if i.index > max_index:
				max_index = i.index
		display_name = max_index + 1
		lastDims = self.show_dim_list[-1]
		new_display = _Display(display_name, lastDims[0], lastDims[1], self)
		self.display_list.append(new_display)
		self.display_names.append(display_name)
		self._addToArea(new_display.create())
		new_display.update()
		return new_display


	def _createDisplays(self):
		self.display_list = []
		self.display_names = []
		for n,d in enumerate(self.show_dim_list):
			new_display = _Display(n, d[0], d[1], self)
			self.display_list.append(new_display)
			self.display_names.append(new_display.index)
			self._addToArea(new_display.create())
		if self.build_preferences_dock:
			if not self._preferencesDock.exist:#if this dock doesnt exist
				 self._preferencesDock.build(self.preferenceDock_size)
			else:
				self._preferencesDock.addToArea()


	def _removeDisplay(self, index_name):
		index = self.display_names.index(index_name)
		dock = self.display_list[index].dock
		#remove dock
		dock.setParent(None)
		dock.label.setParent(None)
		self.display_list.pop(index)
		self.display_names.pop(index)


	def _setFPS(self, fps):
		self.fps = float(fps)
		self.wait_ms = 1000/self.fps #frames per second
		try:
			self.timerFPS.setInterval(self.wait_ms)
		except AttributeError:#if timer is not defined yet
			pass


	def _setLPS(self, lps):
		self.lps = float(lps)
		if self.lps <= 0:
			self.lps = 1e-5
			if self.limitReadoutRate:
				print "Set readout lines per second to 1e-5"
		if self.limitReadoutRate:
			self.wait_ms_lps = 1000/self.lps #lines per second
		else:
			self.wait_ms_lps = 0
		try:
			self.timerLPS.setInterval(self.wait_ms_lps)
		except AttributeError:#if timer is not defined yet
			pass


	def _setColorTheme(self, colorTheme):
		'''choose the colortheme for the plot-output, possible values are:
				* "default"
				* "bright"
		'''
		self.colorTheme = colorTheme
		if self.colorTheme == "default" or self.colorTheme == "":
			self.ticks_color = (200,200,200)
			self.label_color = '#fff'
			self.bg_color = 'k'#black
			
		elif self.colorTheme == "bright":
			self.ticks_color = (30,30,30)
			self.label_color = 'k'
			self.bg_color = 'w'
		pg.setConfigOption('background', self.bg_color)
		pg.setConfigOption('foreground', self.label_color)



class _forkedDock(pgDock.Dock):
	'''adding function: setWidget to normal Dock-class'''


	def __init__(self, name, area=None, size=(10, 10), widget=None, hideTitle=False, autoOrientation=True):
		super(_forkedDock, self).__init__(name, area, size, widget, hideTitle, autoOrientation)


	def setWidget(self, widget, index=0, row=None, col=0, rowspan=1, colspan=1):
		"""
		Add a new widget to the interior of this Dock.
		Each Dock uses a QGridLayout to arrange widgets within.
		"""
		if row is None:
			row = self.currentRow
		self.currentRow = max(row+1, self.currentRow)
		if index > len(self.widgets)-1:
			#add ne widget
			self.widgets.append(widget)
		else:#change existing widget
			self.layout.removeWidget(self.widgets[index])
			self.widgets[index] = widget
		self.layout.addWidget(widget, row, col, rowspan, colspan)
		self.raiseOverlay()



class _Display(object):
	'''
	This class contains all attributes and methods that belongs to a displays widget.
	'''

	def __init__(self, index, show_merge, show_basis, plotC):
		self.index = index
		self.show_merge = show_merge
		self.show_basis = show_basis
		self.plotC = plotC
		self._basis_dim = self.plotC._basis_dim
		self._merge_dim = self.plotC._merge_dim
		self.enableAutoRangeX = "x" in self.plotC.enableAutoRange or "X" in self.plotC.enableAutoRange
		self.enableAutoRangeY = "Y" in self.plotC.enableAutoRange or "Y" in self.plotC.enableAutoRange

		self.mergeMatrix = self.plotC.matrixClass.mergeMatrix
		self.densityMatrix = self.plotC.matrixClass.densityMatrix
		self.basisMatrix = self.plotC.matrixClass.basisMatrix
		self.plot_overlay = self.plotC.matrixClass.plot_overlay
		self.colorList = ['r', 'g', 'b', 'c', 'm', 'y', 'k', 'w']

		self.plotOverlay_points = []
		self.plotOverlay_brokenLines = []
		self.plotOverlay_lines = []

		self.dock = _forkedDock(str(self.index), size=(self.plotC.display_size, 1))

		#self.dock = pgDock.Dock(str(self.index), size=(self.plotC.plot_size_x, 1))
		self.isFirstTime = True
		self.view = None
		self.title,self.title_opt = "",[]

		self.scale_plot = True

		self.basis_dim_plot_range = []
		self.concentrate_basis_dim = []
		self.transpose_axes = False
		self.show_merge_as_density = []
		
		for n in range(len(self._basis_dim)):
			self.basis_dim_plot_range.append(self._basis_dim[n]._plot_range)
			self.concentrate_basis_dim.append("mean")#default option

		for n in range(len(self._merge_dim)):
			self.show_merge_as_density.append(False)
			#use_unit can be overridden to show e.g. the pointdensity
			self._merge_dim[n].use_unit = self._merge_dim[n].unit

		#max 2 basis-dim can be showed - the rest has to be concentrated
		if len(self.show_basis) > 2:
			self.show_basis = self.show_basis[:2]

		self.yAxis = pg.AxisItem("left")
		self.xAxis = pg.AxisItem("bottom")

		self.poi_show_only_merge = False

	def create(self):
		'''
		create a new content in the display
		'''
		if len(self.show_basis) == 1:#1D
			self.plot = pg.PlotWidget(axisItems = {"left": self.yAxis, "bottom": self.xAxis})
			self.view = self.plot.getPlotItem()
			self.plot.setXRange(self._basis_dim[self.show_basis[0]]._include_range[0],
				self._basis_dim[self.show_basis[0]]._include_range[1])
			self.plot.addLegend()
			self._createCurves1D()

		else: #2D - image
			self.view = pg.PlotItem(axisItems = {"left": self.yAxis, "bottom": self.xAxis})
			self.plot = pg.ImageView(view=self.view)
			self.view.setAspectLocked(False)
			#by default images have an inverted y-axis in pyqtgraph
			self.view.invertY(False)

		#for crosshair and shown points-of-interest
		self.poiMarker = pg.ScatterPlotItem()
		self.view.addItem(self.poiMarker)
		self.poiTextList = []

		self._setTitle()
		self._setAxisLabels()
		self.dock.setWidget(self.plot)
		return self.dock


	def _changeTitleOpt(self, basis, newTitleOpt=None):
		#find index of old pos:#remove old entry
		for n,i in enumerate(self.title_opt):
			if "%s=" %basis.name in i:
				self.title_opt.pop(n)
				break
		if newTitleOpt != None:
			self.title_opt.append("%s=%s" %(basis.name, newTitleOpt) )
		self._setTitle()


	def _setTitle(self):
		self.title = ""
		if len(self.show_basis)>1:
			self.title = "%s (%s)" %(self._merge_dim[self.show_merge[0]].name,
				self._merge_dim[self.show_merge[0]].use_unit)
		for i in self.title_opt:
			self.title += "{%s}" %i
		self.view.setTitle(title=self.title )


	def _createCurves1D(self):
		#create all 1d-curves and ink in range of the colorlist
		self.plot.clear()
		try:
			self.plot.plotItem.legend.items = []
		except AttributeError:#when ther is no legend
			pass
		self._setAxisLabels()
		self.curves = []
		for n,i in enumerate(self.show_merge):
			self.curves.append(self.plot.plot(
				pen=self.colorList[n%len(
					self.colorList)], symbol='+',
					name=self._merge_dim[i].name))


	def _setAxisLabels(self):
		if len(self.show_basis) == 1:
			axis_units = ""
			c=0
			for i in self.show_merge:
				unit = self._merge_dim[i].use_unit
				if unit not in axis_units:
					axis_units += "%s " %unit
					c+=1
			if c > 1:
				axis_units = "[ %s]" %axis_units
			else:
				axis_units = axis_units[:-1]
				
			if self.transpose_axes:
				self.xAxis.setLabel(text= '', units = axis_units)
				self.yAxis.setLabel(text=self._basis_dim[self.show_basis[0]].name,
				units = self._basis_dim[self.show_basis[0]].unit)
			else:
				self.yAxis.setLabel(text= '', units = axis_units)
				self.xAxis.setLabel(text=self._basis_dim[self.show_basis[0]].name,
				units = self._basis_dim[self.show_basis[0]].unit)
		else:
			if self.transpose_axes:
				self.yAxis.setLabel(text=self._basis_dim[self.show_basis[0]].name,
					units = self._basis_dim[self.show_basis[0]].unit)
				self.xAxis.setLabel(text=self._basis_dim[self.show_basis[1]].name,
					units = self._basis_dim[self.show_basis[1]].unit)
			else:
				self.xAxis.setLabel(text=self._basis_dim[self.show_basis[0]].name,
					units = self._basis_dim[self.show_basis[0]].unit)
				self.yAxis.setLabel(text=self._basis_dim[self.show_basis[1]].name,
					units = self._basis_dim[self.show_basis[1]].unit)


	def update(self):
		#get merge-extract
		for n,m in enumerate(self.show_merge):
			if self.show_merge_as_density[m]:
				self.merge_extract = self.densityMatrix[m][tuple(self.basis_dim_plot_range)]
			else:
				self.merge_extract = self.mergeMatrix[m][tuple(self.basis_dim_plot_range)]
			for b in range(len(self._basis_dim)-1,-1,-1):
				#basis dim to concentrate
				if b not in self.show_basis:
					pos_corr = self.concentrate_basis_dim[:b].count("pos")
					if self.concentrate_basis_dim[b] == "sum":
						self.merge_extract = bn.nansum(self.merge_extract,b-pos_corr)
					elif self.concentrate_basis_dim[b] == "mean":
						self.merge_extract = bn.nanmean(self.merge_extract,b-pos_corr)
					elif self.concentrate_basis_dim[b] == "max":
						self.merge_extract = bn.nanmax(self.merge_extract,b-pos_corr)
					elif self.concentrate_basis_dim[b] == "min":
						self.merge_extract = bn.nanmin(self.merge_extract,b-pos_corr)

			for b in range(len(self._basis_dim)-2,-1,-1):
				# check from end to start whether to roll-axis
				# the time-axis has to be the last one
				# dont roll the last basis-dim (start with len(self._basis_dim)-2 )
				basis_time_index = None
				if b not in self.show_basis and self.concentrate_basis_dim[b] == "time":
					#reshape the matrix
					self.merge_extract = np.rollaxis(self.merge_extract,b,0)
					basis_time_index = b
					break # dont needto continue iterating because only one dim can be 'time'

			if len(self.show_basis) == 1:
				basis_extract = self.basisMatrix[self.show_basis[0]][self._basis_dim[self.show_basis[0]]._plot_range]

				#if self.plot_basis_as_merge[self.show_basis[0]]:
					##change auto-scale-axes-names
					#x="y"
					#y="x"
				#else:
					#x='x'
					#y='y'

				if self.scale_plot == True:
					self.plot.enableAutoRange('xy', True)
				else:
					if self.enableAutoRangeX:
						self.plot.enableAutoRange('x', True)
						#self.plot.setXRange(
							#self._basis_dim[self.show_basis[0]]._include_range[0],
							#self._basis_dim[self.show_basis[0]]._include_range[1])
					if self.enableAutoRangeY:
						self.plot.enableAutoRange('y', True)

				if self.transpose_axes:
					self.curves[n].setData(self.merge_extract, basis_extract)
				else:
					self.curves[n].setData(basis_extract, self.merge_extract)

			elif len(self.show_basis) >=2:
				#calc scale and zero-position for axes-tics
				x0=self._basis_dim[self.show_basis[0]]._include_range[0]
				x1=self._basis_dim[self.show_basis[0]]._include_range[1]
				y0=self._basis_dim[self.show_basis[1]]._include_range[0]
				y1=self._basis_dim[self.show_basis[1]]._include_range[1]
				xscale = (x1-x0) / self._basis_dim[self.show_basis[0]].resolution
				yscale = (y1-y0) / self._basis_dim[self.show_basis[1]].resolution
				args = {'pos':[x0, y0], 'scale':[xscale, yscale]}
				if self.transpose_axes:
					args = {'pos':[y0, x0], 'scale':[yscale, xscale]}

				#set time-ticks
				if basis_time_index != None:
					args["xvals"] = self.basisMatrix[basis_time_index]

				if self.enableAutoRangeX:
					self.view.enableAutoRange('x', True)
					#self.view.setXRange(**tuple(self._basis_dim[self.show_basis[0]]._include_range))#[0],
						#self._basis_dim[self.show_basis[0]]._include_range[1])
				if self.enableAutoRangeY:
					self.view.enableAutoRange('y', True)

				#bydefault autoLevel (the colorlevel of the merge-dims) == True
				#(calc. by pyqtgraph)
				#thus it only can process array without nan-values the calc. colorlevel
				#is wrong when the real values are boyond the nan-replacement(zero)
				#therefore i calc the colorlevel by my self in case nans arein the array:
				anynan = bn.anynan(self.merge_extract)
				if anynan:
					
					mmin = bn.nanmin(self.merge_extract)
					mmax = bn.nanmax(self.merge_extract)
					if np.isnan(mmin):
						mmin,mmax=0,0
					self.plot.setLevels(mmin, mmax)
					args["autoLevels"]= False
					##the following line dont work with my version of pyQtGraph
					#args["levels"]= [mmin,mmax]#np.nanmin(merge_extract), np.nanmax(merge_extract))
				self.merge_extract = _utils.nanToZeros(self.merge_extract)

				if self.transpose_axes:
					self.plot.setImage(self.merge_extract.transpose(),
						autoRange=self.scale_plot,**args)
				else:
					self.plot.setImage(self.merge_extract,
						autoRange=self.scale_plot,**args)
				if anynan: # scale the histogramm to the new range
					self.plot.ui.histogram.vb.setYRange(mmin,mmax)

		self.scale_plot = False

	def addPlotOverlay(self):
		#plot_overlay = [(points), (lines), (broken lines), , (ellipses), (rectangles), (text), (legend)]
			#(points),(broken lines), (lines)  = [x-list,y-list]
			#(ellipses) = list[ tuple(x,y), float(width), float(height), float(angle) ) ## str(color) ]
			#(rectangles) = list[ tuple(x,y), float(width), float(height) ]
			#(text) = list[ tuple(x,y), string(text)
			#Llegend) = list[str(...),... ]
		self.plotOverlay_legend = self.view.addLegend()
		for m in self.show_merge:
			if self.plot_overlay[m][0] != []:#draw points
				for i in self.plot_overlay[m][0]:
					self.plotOverlay_points.append(
						self.view.plot([i[0]],[i[1]],symbol='o', name=i[2]))

			if self.plot_overlay[m][1] != []:#draw broken lines
				for n,i in enumerate(self.plot_overlay[m][1]):
					self.plotOverlay_brokenLines.append(
						self.view.plot(i[0],i[1], name=i[2], pen=self.colorList[n%len(self.colorList)]))

			if self.plot_overlay[m][2] != []:#draw lines
				for n,i in enumerate(self.plot_overlay[m][2]):
					self.plotOverlay_lines.append(
						self.view.plot(i[0],i[1], name=i[2],
						 pen=self.colorList[n%len(self.colorList)]))

			if self.plot_overlay[m][5] != []:#draw text
				self.plotOverlay_text = self.view.addLegend(offset=(-30, 30))
				for i in self.plot_overlay[m][5]:
					self.plotOverlay_text.addItem(None, i)


	def removePlotOverlay(self):
		#for i in (self.plotOverlay_points,
		#		self.plotOverlay_brokenLines,self.plotOverlay_lines):
		#	for j in i:
		#		self.view.removeItem(j)
		##doest work at the moment ... wait for futher updates of pyQtGraph
		##allowing removal of legends
			#self.view.removeItem(self.plotOverlay_legend)
		self.plotOverlay_points = []
		self.plotOverlay_brokenLines = []
		self.plotOverlay_lines = []
		self.plotOverlay_text = []
		#try:
		#	self.plotOverlay_text.items = []
		#except AttributeError:
		#	pass
		self.plotOverlay_legend = []
		#because the removal of a legendItem doesnt work at the moment and
		# legend.items = [] only delete the items
		# we simply recreate the plot:
		self.create()


	def _setCrosshair(self):
		#draw text for crosshair
		self.crosshair = pg.TextItem(text='', color=(0,0,0), html=None, anchor=(0, 1), border=None, fill=pg.mkBrush(255, 255, 255, 80), angle=0)
		#draw lines
		self.vLine = pg.InfiniteLine(angle=90, movable=False)
		self.hLine = pg.InfiniteLine(angle=0, movable=False)
		#add to viewBox
		self.view.addItem(self.vLine, ignoreBounds=True)
		self.view.addItem(self.hLine, ignoreBounds=True)
		self.view.addItem(self.crosshair)

		def mouseMoved(evt):
			if self.view.sceneBoundingRect().contains(evt.x(),evt.y()):
				mousePoint = self.view.vb.mapSceneToView(evt)
				self.indexX = mousePoint.x()
				self.indexY = mousePoint.y()
				#set text of crosshair
				if len(self.show_basis) == 1:
					if self.poi_show_only_merge:
						self.poiText = "%0.3g" %self.indexY
					else:
						self.poiText = "x=%0.3g\ny=%0.3g\n" %(self.indexX, self.indexY)
				elif len(self.show_basis) == 2:
					if self.transpose_axes:
						posX = _utils.nearestPosition(
							self.basisMatrix[self.show_basis[1]],self.indexX)
						posY = _utils.nearestPosition(
							self.basisMatrix[self.show_basis[0]],self.indexY)
					else:
						posX = _utils.nearestPosition(
							self.basisMatrix[self.show_basis[0]],self.indexX)
						posY = _utils.nearestPosition(
							self.basisMatrix[self.show_basis[1]],self.indexY)
							
					z_value = self.plot.image[posX][posY]
					if self.poi_show_only_merge:
						self.poiText = "%0.3g" %z_value
					else:
						self.poiText = "x=%0.3g\ny=%0.3g\nz=%0.3g" %(
							self.indexX, self.indexY, z_value)
				else:
					self.poiText ="nD not implemented jet"

				self.crosshair.setText(self.poiText,color=(0,0,0) )
				#move text to corner
				self.crosshair.setPos(self.indexX,self.indexY)
				#move crosshair-lines to mousepos.
				self.vLine.setPos(self.indexX)
				self.hLine.setPos(self.indexY)
		##connent mouse-signals to new methods
		self.view.vb.scene().sigMouseMoved.connect(mouseMoved)
		self.view.vb.scene().sigMouseClicked.connect(self._setPOI)


	def _unsetCrosshair(self):
		self.view.removeItem(self.crosshair)
		self.view.removeItem(self.vLine)
		self.view.removeItem(self.hLine)
		self.view.vb.scene().sigMouseClicked.disconnect(self._setPOI)


	def _setPOI(self, evt):
		self.poiMarker.addPoints(x=[self.indexX],y=[self.indexY],symbol="+",size=10)
		textPOI = pg.TextItem(text=self.poiText, color=(0,0,0), html=None,
			anchor=(0,1),border=None, fill=pg.mkBrush(255, 255, 255, 80), angle=0)
		textPOI.setPos(self.indexX,self.indexY)
		self.poiTextList.append(textPOI)
		self.view.addItem(textPOI)


	def _cleanPOI(self):
		for t in self.poiTextList:
			self.view.removeItem(t)
		self.poiMarker.clear()