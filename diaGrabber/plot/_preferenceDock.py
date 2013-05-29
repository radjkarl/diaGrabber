# -*- coding: utf-8 *-*
'''
The classes in this module were not controlled or called by the user itself.
Only :class:`diaGrabber.plot.Gui.Gui` controll calls it.
Nethertheless most methods are described and viewable in the API.
'''
#own
from diaGrabber import _utils
import sys
from copy import deepcopy
#foreign
import pyqtgraph.parametertree.parameterTypes as pTypes
from pyqtgraph.parametertree import Parameter, ParameterTree, ParameterItem, registerParameterType
import pyqtgraph.dockarea as pgDock
from pyqtgraph.Qt import QtGui
from pyqtgraph import ViewBox
from pyqtgraph import LineSegmentROI, AxisItem, PlotDataItem


class preferenceDock(object):
	'''main-class for the whole preference-dock-system'''

	def __init__(self, Gui):
		self.Gui = Gui
		self.exist = False

	def build(self,preferences_size):
		'''does:
			
			* add mainTab
			* add preferenceTab for each display
			* add the pref.Dock to the gui
			* save the widget-layout
		'''
		self.exist = True
		self.size = preferences_size
		self.tab = QtGui.QTabWidget()#TabWidget()
		#build main tab
		self.main = mainTab(self)
		#add main tab to tab-instance
		self.tab.addTab(self.main, 'Main')
		for d in self.Gui.display_list:
			self.addPrefTab(d)
		#create new dock
		self.pref_dock = pgDock.Dock("Preferences", size=(self.size, 1))
		#add tab-instance to dock
		self.pref_dock.addWidget(self.tab)
		#add dock to area
		self.addToArea()
		#autosave
		self.main.saveWidgetLayout()


	def createNewDisplay(self):
		'''
		* ask Gui to create a new display
		* add a new pref.Tab for it
		* save the new layout
		'''
		display = self.Gui._createNewDisplay()
		self.addPrefTab(display)
		self.addToArea()
		#autosave
		self.main.saveWidgetLayout()


	def addPrefTab(self,display):
		'''add a tab owned by its display'''
		display.prefTab = preferenceTab(display, self)
		self.tab.addTab(display.prefTab, str(display.index))


	def removeTab(self, tab):
		'''remove a pref.Tab from the preferenceDock, save widget-layout'''
		self.tab.removeTab(self.tab.indexOf(tab))
		#autosave
		self.main.saveWidgetLayout()


	def addToArea(self):
		'''append parameterTree-instance to dockarea'''
		self.Gui.area.addDock(self.pref_dock, 'left')
		self.pref_dock.setStretch(x=self.size)



class mainTab(ParameterTree):
	'''class for the main-Tab'''
	def __init__(self, prefDock):
		self.Gui = prefDock.Gui
		super(mainTab, self).__init__()
		## Create tree of Parameter objects
		self.p= Parameter.create(name='params', type='group')
		#add parameters
		self.pAddWidget = self.p.addChild(
			{'name': 'Add widget', 'type': 'action'})
		self.pSaveRestoreLayout = self.p.addChild(
			{'name': 'Save/Restore widget-layout', 'type': 'group', 'children': [
				{'name': 'Save', 'type': 'action', 'children': [
					{'name': 'Save to file', 'type': 'bool', 'value': False},
					{'name': 'Filename', 'type': 'str', 'value': 'preferences/my_widget_layout'},
				]},
				{'name': 'Restore', 'type': 'action', 'children': [
					{'name': 'Restore from file', 'type': 'bool', 'value': False},
					{'name': 'Filename', 'type': 'str', 'value': 'preferences/my_widget_layout'},
				]},
			]})

		if self.Gui.interactive:
			self.pPlotRates = self.p.addChild(
				readoutPlotRates(self.Gui, name='Readout/Plot-Rates'))
		#signals
		self.pAddWidget.sigActivated.connect(prefDock.createNewDisplay)
		self.pSaveRestoreLayout.param(
			'Save').sigActivated.connect(self.saveWidgetLayout)
		self.pSaveRestoreLayout.param(
			'Restore').sigActivated.connect(self.restoreWidgetLayout)

		self.setParameters(self.p, showTop=False)


	def saveWidgetLayout(self):
		'''
		save the state of the widgetlayout to 'self.stateWidgetLayout'
		and (in case ''Save to file' is active) in file.
		'''
		self.stateWidgetLayout = self.Gui.area.saveState()
		if self.pSaveRestoreLayout['Save', 'Save to file']:
			#write state to file
			filename = self.pSaveRestoreLayout['Save', 'Filename']
			_utils.prepareFileSystem(filename)
			saveWidgetFile = open(filename, "w")
			saveWidgetFile.write(str(self.stateWidgetLayout))
			saveWidgetFile.close()


	def restoreWidgetLayout(self):
		'''
		Restore widget-layout from 'self.stateWidgetLayout' or
		(in case 'Restore from file' is active) from file.
		'''
		if self.pSaveRestoreLayout['Restore', 'Restore from file']:
			filename = self.pSaveRestoreLayout['Restore', 'Filename']
			self.stateWidgetLayout = saveWidgetFile = eval(open(filename, "r").read())
		self.Gui.area.restoreState(self.stateWidgetLayout)



class preferenceTab(ParameterTree):
	'''
	the preference tab that belongs to each Display
	'''

	def __init__(self,display, prefDock):
		self.Gui = prefDock.Gui
		self.prefDock = prefDock
		self.display = display
		super(preferenceTab, self).__init__()

		self.p = Parameter.create(name='params', type='group')
		#add parameters
		self.pRemoveWidget = self.p.addChild(
			{'name': 'Remove widget', 'type': 'action'})
		self.plot_merge_dims = self.p.addChild(
			plotMergeDims(self, self.display, name='Plot merge-dimensions'))
		self.slice_image = self.p.addChild(
			sliceImage(self, self.display, name='Slice Image'))
		self.plot_basis_dims = self.p.addChild(
			plotBasisDims(self, self.display, name='Plot basis-dimensions'))
		self.pAddContentOf = self.p.addChild(
			addContentOf(self, self.display, name='add Content of...'))
		self.pViewOptions = self.p.addChild(
			viewOptions(self, self.display, name='View Options'))
		self.save_restore = self.p.addChild(
			saveRestorePrefs(self, name='Save/Restore preferences'))

		#signals
		self.pRemoveWidget.sigActivated.connect(self.remove)
		if self.Gui.printChanges:
			self.p.sigTreeStateChanged.connect(self.printChange)

		self.setParameters(self.p, showTop=False)
		
		#autosave
		self.statePreferences = self.p.saveState()
		self.showTabOnClick()


	def printChange(self, param, changes):
		'''If anything changes in the tree, print a message'''
		print("tree changes:")
		for param, change, data in changes:
			path = self.p.childPath(param)
			if path is not None:
				childName = '.'.join(path)
			else:
				childName = param.name()
			print('  parameter: %s'% childName)
			print('  change:	%s'% change)
			print('  data:	  %s'% str(data))
			print('  ----------')


	def remove(self):
		'''remove a display and it's appendant preferenceTab'''
		self.Gui._removeDisplay(self.display.index)
		self.prefDock.removeTab(self)


	def showTabOnClick(self):
		'''
		show the related preference-tab if the mouse click on the viewBox of
		a display.
		this is done trough manipluating the 'mouseClickEvent'-routine of
		the viewBox of the display.
		'''
		def newMouseClickEvent(ev):
			'''add to normal mouseClickEvent the feature
			to show the corresponding prefTab when clicking on the display'''
			self.prefDock.tab.setCurrentWidget(self)
			ViewBox.mouseClickEvent(self.display.view.vb, ev)
		self.display.view.mouseClickEvent = newMouseClickEvent



class saveRestorePrefs(pTypes.GroupParameter):
	'''save/restore parameters in the preferenceTab'''

	def __init__(self,prefTab, **opts):#
		self.prefTab = prefTab
		opts['type'] = 'group'
		opts['value'] = True
		opts['children'] = [
				{'name': 'Save', 'type': 'action'},
				{'name': 'Restore', 'type': 'action', 'children': [
					{'name': 'Add missing items', 'type': 'bool', 'value': True},
					{'name': 'Remove extra items', 'type': 'bool', 'value': True},
				]}]
		pTypes.GroupParameter.__init__(self, **opts)
		##SAVE PREFERENCES
		self.param('Save').sigActivated.connect(self.savePreferences)
		self.param('Restore').sigActivated.connect(self.restorePreferences)


	def savePreferences(self):
		self.prefTab.statePreferences = self.prefTab.p.saveState()


	def restorePreferences(self, sgn,state = None,add_missing_remove_extra=None):
		if state == None:
			state = self.prefTab.statePreferences
		if add_missing_remove_extra == None:
			add = self.param('Restore', 'Add missing items')
			rem = self.param('Restore', 'Remove extra items')
		else:
			add,rem = add_missing_remove_extra,add_missing_remove_extra
		self.prefTab.p.restoreState(state, addChildren=add, removeChildren=rem)



class plotBasisDims(pTypes.GroupParameter):

	def __init__(self,prefTab, display, **opts):#
		self.display = display
		self.prefTab = prefTab
		self.concBasisDict = {} #basis_index, concBasis-instance
		opts['type'] = 'bool'
		opts['value'] = True
		pTypes.GroupParameter.__init__(self, **opts)
		self.basis_opt = []
		for n,b in enumerate(self.display._basis_dim):
			plot_basis = b._basisIndex in self.display.show_basis
			self.basis_opt.append(
				self.addChild({'name': b.name, 'type': 'bool', 'value': plot_basis}))
			if plot_basis:
				self.addPlotRange(n,b)
			else:
				self.addConcentrateOpt(n,b)
			self.param(b.name).sigValueChanged.connect(self.changePlotStatus)


	def addPlotRange(self,n,b):
		self.display._changeTitleOpt(b)
		#add parameters
		self.basis_opt[n].addChild({'name': 'Plot-Range', 'type': 'group', 'children': [
			{'name': 'from', 'type': 'int', 'value': 0, 'limits': (0, b.resolution-1)},
			{'name': 'to', 'type': 'int', 'value':b.resolution, 'limits': (1, b.resolution-1)},
			{'name': 'step', 'type': 'int', 'value': 1, 'limits': (1, b.resolution-1)},
			]})
		#signals
		self.param(b.name,'Plot-Range','from').sigValueChanged.connect(
			self.changePlotRangeFrom)
		self.param(b.name,'Plot-Range','to').sigValueChanged.connect(
			self.changePlotRangeTo)
		self.param(b.name,'Plot-Range','step').sigValueChanged.connect(
			self.changePlotRangeStep)


	def addConcentrateOpt(self,n,b):
		self.concBasisDict[b.name] = self.basis_opt[n].addChild(
			ConcentrateOpt(n,self.display,b, self.concBasisDict,
			name='Concentrate-Basis') )


	def changePlotRangeFrom(self):
		for n,b in enumerate(self.display._basis_dim):
			try:
				new = self.param(b.name, 'Plot-Range','from')
				#if not new.valueIsDefault():
				orig=self.display.basis_dim_plot_range[n]
				self.display.basis_dim_plot_range[n] = slice(new.value(),orig.stop,orig.step)
			except Exception:#basis-dim isnt active
				pass
		self.display.update()


	def changePlotRangeTo(self):
		for n,b in enumerate(self.display._basis_dim):
			try:
				new = self.param(b.name, 'Plot-Range','to')
				#if not new.valueIsDefault():
				orig=self.display.basis_dim_plot_range[n]
				self.display.basis_dim_plot_range[n] = slice(orig.start,new.value(),orig.step)
			except Exception:#basis-dim isnt active
				pass
		self.display.update()


	def changePlotRangeStep(self):
		for n,b in enumerate(self.display._basis_dim):
			try:
				new = self.param(b.name, 'Plot-Range','step')
				#if not new.valueIsDefault():
				orig=self.display.basis_dim_plot_range[n]
				self.display.basis_dim_plot_range[n] = slice(orig.start,orig.stop,new.value())
			except Exception:#basis-dim isnt active
				pass
		self.display.update()


	def changePlotStatus(self):
		for n,b in enumerate(self.display._basis_dim):
			pa = self.param(b.name)
			if (not pa.value() and n in self.display.show_basis
				and len(self.display.show_basis) ==1):
				#dont shut down last (active) dimension
				pa.setValue(True, blockSignal=self.changePlotStatus)
			else:
				#remove all children
				self.basis_opt[n].clearChildren()
				#max 2 basis-dim to view
				if ((pa.value() and pa.defaultValue()) or
					(pa.value() and len(self.display.show_basis) < 2)):
					if not pa.value():
						pa.setValue(True, blockSignal=self.changePlotStatus)
					if n not in self.display.show_basis:
						self.display.show_basis.append(n)
						self.display.show_basis.sort()#show_basis has to be sorted
						self.display.basis_dim_plot_range[n] = slice(None,None,None)
						#set all paratemers of the view-option to default
						self.prefTab.pViewOptions.setToDefault()
						self.display.create()
						self.prefTab.showTabOnClick()
					self.display.concentrate_basis_dim[n] = "mean"
					self.addPlotRange(n,b)
					#because 'as-time' will only be shown for2+basis-dims
					#it has to be reinitialized
					for i,ba in enumerate(self.display._basis_dim):
						if i not in self.display.show_basis: # if concentrated
							if ba != b:#change only other conc. basis
								self.concBasisDict[ba.name].setPAsTime()
				else:
					if pa.value():
						pa.setValue(False, blockSignal=self.changePlotStatus)
					if n in self.display.show_basis:
						self.display.show_basis.pop(self.display.show_basis.index(n))
						#self.display.nBasis -= 1
						if len(self.display.show_basis) == 0: #no basis to show
							self.param(b.name).setValue(True)
							break #do not create concentrato opts if reset to active basis
						#set all paratemers of the view-option to default
						self.prefTab.pViewOptions.setToDefault()
						self.display.create()
						self.prefTab.showTabOnClick()
					self.display.concentrate_basis_dim[n] = "mean"
					self.addConcentrateOpt(n,b)
		self.display.scale_plot = True
		self.display.update()



class ConcentrateOpt(pTypes.GroupParameter):
	'''class to handle all concentrated basisDimensions'''

	def __init__(self, n,display, b, concBasisDict, **opts):
		self.n = n
		self.basis = b
		self.display = display
		self.concBasisDict = concBasisDict
		pTypes.GroupParameter.__init__(self, **opts)
		#add parameters
		self.pMean=self.addChild(
			{'name': 'mean', 'type': 'bool', 'value': True})
		self.pSum=self.addChild(
			{'name': 'sum', 'type': 'bool', 'value': False})
		self.pMax=self.addChild(
			{'name': 'max', 'type': 'bool', 'value': False})
		self.pMin=self.addChild(
			{'name': 'min', 'type': 'bool', 'value': False})
		self.pAtPosition=self.addChild(
			{'name': 'at position', 'type': 'int', 'value': -1,
			'limits': (-1, self.basis.resolution-1)})
		self.pValue=self.addChild(
			{'name': '     value', 'type': 'float', 'value': 0, 'readonly': True})
		self.setPAsTime()
		#signals
		self.pAtPosition.sigValueChanged.connect(self.changePlotRangeToPosition)
		self.pSum.sigValueChanged.connect(self.changeSum)
		self.pMean.sigValueChanged.connect(self.changeMean)
		self.pMin.sigValueChanged.connect(self.changeMin)
		self.pMax.sigValueChanged.connect(self.changeMax)
		#init default
		#self.changeMean()


	def setPAsTime(self):
		'''
		the parameter 'as time' is only visible if 2 basisDimensions are active
		(in case of a plotted image)
		'''
		if len(self.display.show_basis) == 2:
			#does pAsTime exist?
			try:
				self.pAsTime.setValue(False) # as standard
			except AttributeError: # no: create it
				self.pAsTime = self.addChild(
					{'name': 'as time', 'type': 'bool', 'value': False})
				self.pAsTime.sigValueChanged.connect(self.changeAsTime)


	def changeAsTime(self):
		if self.pAsTime.value() == True:
			#set other options to false/default
			self.pSum.setValue(False, blockSignal=self.changeSum)
			self.pMean.setValue(False, blockSignal=self.changeMean)
			self.pMin.setValue(False, blockSignal=self.changeMin)
			self.pMax.setValue(False, blockSignal=self.changeMax)
			self.pAtPosition.setToDefault()
			#set 'as-time' values of the other conc. basis to false
			for i,b in enumerate(self.display._basis_dim):
				if i not in self.display.show_basis: # if concentrated
					if b != self.basis:#change only other conc. basis
						self.concBasisDict[b.name].pAsTime.setValue(False)
			#restore plot range
			self.display.basis_dim_plot_range[self.n] = slice(None,None,None)
			self.display.concentrate_basis_dim[self.n] = "time"
			self.display._changeTitleOpt(self.basis, "time")
			self.display.show_basis.append(self.n)
		else:
			self.display._changeTitleOpt(self.basis)
			if self.pMean.value() == False:
				self.pMean.setValue(True)
		#update plot
		self.scale_plot=True
		self.display.update()


	def changeSum(self):
		if self.pSum.value() == True:
			#set other options to false/default
			if len(self.display.show_basis) == 2:
				self.pAsTime.setValue(False, blockSignal=self.changeAsTime)
			self.pMean.setValue(False, blockSignal=self.changeMean)
			self.pMin.setValue(False, blockSignal=self.changeMin)
			self.pMax.setValue(False, blockSignal=self.changeMax)
			self.pAtPosition.setToDefault()
			#restore plot range
			self.display.basis_dim_plot_range[self.n] = slice(None,None,None)
			self.display.concentrate_basis_dim[self.n] = "sum"
			self.display._changeTitleOpt(self.basis, "sum")
		else:
			self.display._changeTitleOpt(self.basis)
			if self.pMean.value() == False:
				self.pMean.setValue(True)
		#update plot
		self.scale_plot=True
		self.display.update()


	def changeMean(self):
		if self.pMean.value() == True:
			#set other options to false/default
			self.pSum.setValue(False, blockSignal=self.changeSum)
			self.pMin.setValue(False, blockSignal=self.changeMin)
			self.pMax.setValue(False, blockSignal=self.changeMax)
			self.pAtPosition.setToDefault()
			if len(self.display.show_basis) == 2:
				self.pAsTime.setValue(False, blockSignal=self.changeAsTime)
			#restore plot range
			self.display.basis_dim_plot_range[self.n] = slice(None,None,None)
			self.display.concentrate_basis_dim[self.n] = "mean"
			self.display._changeTitleOpt(self.basis, "mean")
		else:
			self.display._changeTitleOpt(self.basis)
			if self.pSum.value() == False:
				self.pSum.setValue(True)
		#update plot
		self.scale_plot=True
		self.display.update()


	def changeMin(self):
		if self.pMin.value() == True:
			#set other options to false/default
			self.pSum.setValue(False, blockSignal=self.changeSum)
			self.pMean.setValue(False, blockSignal=self.changeMean)
			self.pMax.setValue(False, blockSignal=self.changeMax)
			self.pAtPosition.setToDefault()
			if len(self.display.show_basis) == 2:
				self.pAsTime.setValue(False, blockSignal=self.changeAsTime)
			#restore plot range
			self.display.basis_dim_plot_range[self.n] = slice(None,None,None)
			self.display.concentrate_basis_dim[self.n] = "min"
			self.display._changeTitleOpt(self.basis, "min")
		else:
			self.display._changeTitleOpt(self.basis)
			if self.pMean.value() == False:
				self.pMean.setValue(True)
		#update plot
		self.scale_plot=True
		self.display.update()


	def changeMax(self):
		if self.pMax.value() == True:
			#set other options to false/default
			self.pSum.setValue(False, blockSignal=self.changeSum)
			self.pMean.setValue(False, blockSignal=self.changeMean)
			self.pMin.setValue(False, blockSignal=self.changeMin)
			self.pAtPosition.setToDefault()
			if len(self.display.show_basis) == 2:
				self.pAsTime.setValue(False, blockSignal=self.changeAsTime)
			#restore plot range
			self.display.basis_dim_plot_range[self.n] = slice(None,None,None)
			self.display.concentrate_basis_dim[self.n] = "max"
			self.display._changeTitleOpt(self.basis, "max")
		else:
			self.display._changeTitleOpt(self.basis)
			if self.pMean.value() == False:
				self.pMean.setValue(True)
		#update plot
		self.scale_plot=True
		self.display.update()


	def changePlotRangeToPosition(self):
		if not self.pAtPosition.valueIsDefault():
			position = self.pAtPosition.value()
			#get value for position
			value=self.display.basisMatrix[self.n][position]
			self.pValue.setValue(value)
			#set other options to false
			self.pSum.setValue(False, blockSignal=self.changeSum)
			self.pMean.setValue(False, blockSignal=self.changeMean)
			self.pMin.setValue(False, blockSignal=self.changeMin)
			self.pMax.setValue(False, blockSignal=self.changeMax)
			if len(self.display.show_basis) == 2:
				self.pAsTime.setValue(False, blockSignal=self.changeAsTime)
			#set plot range
			self.display.basis_dim_plot_range[self.n] = position
			self.display.concentrate_basis_dim[self.n] = "pos"
			self.display._changeTitleOpt(self.basis, "%.3f" % value)
		else:#position is default "-1"
			self.pValue.setToDefault()
			self.display._changeTitleOpt(self.basis)
			if self.pMean.value() == False:
				self.pMean.setValue(True)
		#update plot
		self.display.scale_plot = True
		self.display.update()



class sliceImage(pTypes.GroupParameter):
	def __init__(self, prefTab, display, **opts):
		self.display = display
		self.prefTab = prefTab
		opts['type'] = 'bool'
		opts['value'] = False
		pTypes.GroupParameter.__init__(self, **opts)
		#add parameters
		self.activate = self.addChild(
			{'name': 'activate', 'type': 'bool',
			'value': False, 'tip': "activate to slice an image - this only works for 2+ active basisDimensions"})
		self.err_add_display = self.addChild(
			{'name': 'Error1:', 'type': 'str','value': "Add another widget!",
			'readonly': True, 'visible': False})
		self.errorMsg = self.addChild(
			{'name': 'Error2', 'type': 'str',
			'value': "Need at least two active basisDimensions", 'visible': False})
		av_displays = self.getAvDisplays()
		self.which_display = self.addChild(
			{'name': 'slice to display','type': 'list', 'values': av_displays,
			'value': av_displays[0], 'visible': False})
		self.pSlave = self.addChild(
			{'name': 'SLAVE OF Widget', 'type': 'str','value': str(self.display.index),
				'readonly': True, 'visible': False })
		self.err_which_basis = self.addChild(
			{'name': 'Error3:', 'type': 'str',
			'value': "No conc. basisDim to show!",'readonly': True,
			'visible': False})
		show_basis = self.getShowBasis()
		self.which_basis = self.addChild(
			{'name': "show conc. basis",'type': 'list', 'values': show_basis,
			'value': show_basis[0], 'visible': False})
		#signals
		self.activate.sigValueChanged.connect(self.changeActivate)
		self.which_display.sigValueChanged.connect(self.changeWhichDisplay)
		self.which_basis.sigValueChanged.connect(self.changeWhichBasis)


	def getAvDisplays(self):
		'''get the name of all other displays than the own one'''
		av_displays= ["-"]
		for i in range(1,self.prefTab.prefDock.tab.count()):
			#exclude own display-pref-tab
			if str(self.display.index) != self.prefTab.prefDock.tab.tabText(i):
				av_displays.append(self.prefTab.prefDock.tab.tabText(i) )
		return av_displays


	def changeActivate(self):
		if self.activate.value():
			if len(self.display.show_basis) == 1:
				self.errorMsg.show()
			else:
				self.errorMsg.hide()
				av_displays = self.getAvDisplays()
				if len(av_displays) == 1:
					self.err_add_display.show()
				else:
					self.err_add_display.hide()
					self.which_display.setLimits( self.getAvDisplays() )
					self.which_display.setToDefault()
					self.which_display.show()
		else:
			self.errorMsg.hide()
			self.err_add_display.hide()
			self.which_display.hide()
			#am i the master-display?
			if self.pSlave.opts.get('enabled', False):
				#deslaving slave-display
				try:
					self.slave_display.prefTab.save_restore.restorePreferences(True)
					self.slave_display.prefTab.slice_image.pSlave.hide()
				except AttributeError:
					pass # ther is not slave-display
			try:
				self.display.plot.removeItem(self.display.plot.lineRoi)
			except AttributeError:
				pass # no roi-line generated so far
			self.which_basis.hide()
			try: #unblock 'conentrate-opt' of last sliceBasis
				self.recentSliceBasis.parent().show()
			except Exception: #no last parameter exist
				pass


	def changeWhichDisplay(self):
		#if a display was chosen
		if self.which_display.value() != self.which_display.defaultValue():
			#get tab-index from tab-text
			self.slave_display = None
			for i in range(self.prefTab.prefDock.tab.count()):
				if self.prefTab.prefDock.tab.tabText(i) == str(self.which_display.value()):
					self.slave_display = self.prefTab.prefDock.tab.widget(i).display
					break
			if self.slave_display == None:
				sys.exit("ERRORsearchcode 23675367")
			#transfer the parameter-state from active (master)preference tab to
			# preference tab of the chosen display (slave)
			masterState = self.prefTab.p.saveState()
			slaveState = self.slave_display.prefTab.p.saveState()
			slaveState = _utils.adaptMasterStaticsToSlaveDict(
				masterState,slaveState)
			self.slave_display.prefTab.save_restore.restorePreferences(
				True, slaveState, True)
			#save last preferences (to restore, when slave_display
			#is not a slave of self.display)
			self.slave_display.prefTab.save_restore.savePreferences()
			self.slave_display.prefTab.slice_image.pSlave.show()
			#hide activate-button - slave can only be unslaved via master
			self.slave_display.prefTab.slice_image.activate.hide()
			#hide all options which a slave mustn't handle
			for c in  self.slave_display.prefTab.plot_basis_dims.children():
				self.slave_display.prefTab.p.param(
					self.slave_display.prefTab.plot_basis_dims.name(),c.name()).hide()
			for c in  self.slave_display.prefTab.plot_merge_dims.children():
				self.slave_display.prefTab.p.param(
					self.slave_display.prefTab.plot_merge_dims.name(),c.name()).hide()
			for c in  self.slave_display.prefTab.save_restore.children():
				self.slave_display.prefTab.p.param(
					self.slave_display.prefTab.save_restore.name(),c.name()).hide()
			#generate a which-basis list containing all concentrated basis-dims
			show_basis = self.getShowBasis()
			if len(show_basis) == 1:
				self.err_which_basis.show()
				self.which_basis.hide()
			else:
				self.err_which_basis.hide()
				self.which_basis.setToDefault()
				self.which_basis.setLimits(show_basis)
				self.which_basis.show()


	def getShowBasis(self):
		'''get the name of all inactive/concentrated basisDimensions'''
		show_basis = ["-"]
		self.basis_name_index={}
		for i,b in enumerate(self.display._basis_dim):
			if i not in self.display.show_basis:
				show_basis.append(b.name)
				self.basis_name_index[b.name]= i
		return show_basis


	def changeWhichBasis(self):
		#if basis-dim was chosen
		if self.which_basis.value() != self.which_basis.defaultValue():
			##add slice-ROI:
			thirdLenX = int( len(self.display.basisMatrix[self.display.show_basis[0]])/3 )
			halfLenY = int( len(self.display.basisMatrix[self.display.show_basis[1]])/2 )
			#set coords for the slice-line
			startX = self.display.basisMatrix[self.display.show_basis[0]][thirdLenX]
			startY = self.display.basisMatrix[self.display.show_basis[1]][halfLenY]
			stopX = self.display.basisMatrix[self.display.show_basis[0]][-thirdLenX]
			stopY = startY
			#only draw one line - so remove old ones
			try:
				self.display.plot.removeItem(self.display.plot.lineRoi)
			except AttributeError:
				pass # no line to remove
			#new roi-line
			self.display.plot.lineRoi = LineSegmentROI(
				[[startX, startY], [stopX,stopY]], pen='r')
			#add new roi-line to plot
			self.display.plot.addItem(self.display.plot.lineRoi)
			#set chosen concentrated basis to concentrateOption: 'as time'
			# thats necassary go get a slice-able-3d-array
			try: #unblock 'conentrate-opt' of last sliceBasis
				self.recentSliceBasis.parent().show()
			except Exception: #no last parameter exist
				pass
			self.recentSliceBasis = self.prefTab.plot_basis_dims.concBasisDict[
				self.which_basis.value()]
			self.recentSliceBasis.pAsTime.setValue(True)
			self.recentSliceBasis.parent().hide()
			#y-axis becoms the new appeared-basis-axis
			self.slave_display.show_basis[0] = self.basis_name_index[self.which_basis.value()]
			shown_basis = self.slave_display.show_basis[0]
			self.slave_display._setAxisLabels()
			self.firstAutoRange = True

			def updateROIline():
				'''procedure when moving the slice-line'''
				#get new image from master-display
				slicedImg = self.display.plot.lineRoi.getArrayRegion(
					self.display.merge_extract,
					self.display.plot.imageItem, axes=(1,2))
				#get axis-scale of sliced image
				#as long as there is no easy option to show two different y-axes
				#(which where the sliced ones) in pyqtgraph i wil only show
				#the x-axis
				y0=0
				yscale=1 # doesn't matter because yAxis wont be shown
				x0=self.slave_display._basis_dim[shown_basis]._include_range[0]
				x1=self.slave_display._basis_dim[shown_basis]._include_range[1]
				xscale = (x1-x0) / self.slave_display._basis_dim[shown_basis].resolution
				if self.slave_display.transpose_axes:
					p = [y0, x0]
					s = [yscale, xscale]
					self.slave_display.view.showAxis("bottom", show=False)
				else:
					p =[x0, y0]
					s = [xscale, yscale]
					self.slave_display.view.showAxis("left", show=False)
				#set new image
				self.slave_display.plot.setImage(
					slicedImg, autoRange = self.firstAutoRange, pos = p,scale=s)
				self.firstAutoRange = False
			#signal
			self.display.plot.lineRoi.sigRegionChanged.connect(updateROIline)
			#copy title from masterdisplay
			self.slave_display.title_opt = deepcopy(self.display.title_opt)
			#change title
			appear_basis = self.display._basis_dim[
				self.basis_name_index[self.which_basis.value()]]
			self.slave_display._changeTitleOpt(appear_basis)
			self.slave_display._changeTitleOpt(
				self.display._basis_dim[self.display.show_basis[0]],"slice")
			self.slave_display._changeTitleOpt(
				self.display._basis_dim[self.display.show_basis[1]],"slice")
			#to show an image even if the slice-line wont be moved
			updateROIline()



class plotMergeDims(pTypes.GroupParameter):
	def __init__(self, prefTab, display, **opts):
		self.display = display
		self.prefTab = prefTab
		opts['type'] = 'bool'
		opts['value'] = True
		pTypes.GroupParameter.__init__(self, **opts)
		self.mergeToPlot = []
		self.asDensity = []
		for n,m in enumerate(self.display._merge_dim):
			is_merge_in_view = n in self.display.show_merge
			#add parameters
			self.mergeToPlot.append(self.addChild(
				{'name': m.name, 'type': 'bool', 'value':is_merge_in_view}))
			self.asDensity.append(self.mergeToPlot[-1].addChild(
				{'name': "as density", 'type': 'bool', 'value':False,'enabled':False}))
			#signals
			self.mergeToPlot[-1].sigValueChanged.connect(self.changePlotMerge)
			self.asDensity[-1].sigValueChanged.connect(self.changeAsDensity)

		self.changePlotMerge()


	def changePlotMerge(self):
		for n,m in  enumerate(self.mergeToPlot):
			if m.value():
				self.asDensity[n].show()
				if n not in self.display.show_merge:
					#deactivate all other merges in case of imagePlot
					#because the staple of images removes the exact character
					#of the plot
					if len(self.display.show_basis) != 1:
						for j in self.display.show_merge:
							if j != n:
								self.mergeToPlot[j].setValue(
									False, blockSignal=self.changePlotMerge)
								self.asDensity[j].hide()
								self.display.show_merge.pop(
									self.display.show_merge.index(j))
					self.display.show_merge.append(n)
			else:
				self.asDensity[n].hide()
				if n in self.display.show_merge:
					#dont remove the last shown merge
					if len(self.display.show_merge) == 1:
						m.setValue(True)
					else:
						self.display.show_merge.pop(
							self.display.show_merge.index(n))
		if len(self.display.show_basis) == 1:
			self.display._createCurves1D()
		else:
			self.display._setTitle()
		self.display.update()


	def changeAsDensity(self):
		for n,m in  enumerate(self.display._merge_dim):
			try:
				show_as_density = self.param(m.name, "as density").value()
				self.display.show_merge_as_density[n] = show_as_density
				if show_as_density:
					m.use_unit = "PointDensity"
				else:
					m.use_unit = m.unit
			except Exception:#merge not in show_merge
				pass
		self.display._setTitle()
		self.display._setAxisLabels()
		self.display.update()



class addContentOf(pTypes.GroupParameter):
	'''whith the class plotMergeDims it's possible to plot merges together
	over the same basis. in case a display needs other merges with a different
	base it can be added trough this class.
	'''

	def __init__(self, prefTab, display, **opts):
		self.display = display
		self.prefTab = prefTab
		opts['type'] = 'bool'
		opts['value'] = True
		pTypes.GroupParameter.__init__(self, **opts)
		#add parameters
		self.p2dPlots = self.addChild(
			{'name': "2d-Plots", 'type': 'bool', 'value':False})
		av_displays = self.get2dPlotDisplays()
		self.p2dPlotList = self.addChild(
			{'name': 'from display...:',
			'type': 'list', 'values': av_displays,
			'value': av_displays[0], 'visible':False})
		#signals
		self.p2dPlots.sigValueChanged.connect(self.change2dPlots)
		self.p2dPlotList.sigValueChanged.connect(self.change2dPlotList)
		self.Content2d = []


	def get2dPlotDisplays(self):
		'''get a name of all displays having only one basis
		exclude displays with imageplots to prevent a staple of images
		'''
		av_displays= ["-"]
		for i in range(1,self.prefTab.prefDock.tab.count()):
			#exclude own display-pref-tab
			if ( str(self.display.index) != self.prefTab.prefDock.tab.tabText(i)
					and len(self.prefTab.prefDock.tab.widget(i).display.show_basis) == 1 ):
				av_displays.append(self.prefTab.prefDock.tab.tabText(i) )
		if len(av_displays) == 1:
			av_displays.append("no 2D-Plots found")
		return av_displays


	def change2dPlots(self):
		if self.p2dPlots.value():
			av_displays = self.get2dPlotDisplays()
			self.p2dPlotList.setLimits(av_displays)
			self.p2dPlotList.setToDefault()
			self.p2dPlotList.show()
		else:
			self.p2dPlotList.hide()
			for c in self.Content2d:
				self.display.view.removeItem(c)


	def change2dPlotList(self):
		if self.p2dPlotList.value() != self.p2dPlotList.defaultValue():
			for i in range(self.prefTab.prefDock.tab.count()):
				if self.prefTab.prefDock.tab.tabText(i) == str(self.p2dPlotList.value()):
					self.Content2d = []
					for n,c in enumerate(
							self.prefTab.prefDock.tab.widget(i).display.curves):
						self.Content2d.append(PlotDataItem(c.xData, c.yData,
							pen=self.display.colorList[n%len(
							self.display.colorList)], symbol='+'))
						self.display.view.addItem(self.Content2d[-1])
					break
		else:
			for c in self.Content2d:
				self.display.view.removeItem(c)



class viewOptions(pTypes.GroupParameter):
	'''this class includes all otions manipulating the view of the display'''

	def __init__(self, prefTab, display, **opts):
		self.display = display
		self.prefTab = prefTab
		opts['type'] = 'bool'
		opts['value'] = True
		pTypes.GroupParameter.__init__(self, **opts)
		#add parameters
		self.lockAspect = self.addChild(
			{'name': "lockAspect", 'type': 'bool', 'value':False})
		self.crosshair = self.addChild(
			{'name': "Crosshair", 'type': 'bool', 'value':False})
		self.poiShowOnlyMerge = self.crosshair.addChild(
			{'name': "show only merge", 'type': 'bool',
				'value':self.display.poi_show_only_merge, 'visible':False})
		self.poiClean = self.crosshair.addChild(
			{'name': "clean clicked points", 'type': 'bool', 'value':self.display.poi_show_only_merge, 'visible':False})
		self.plotOverlay = self.addChild(
			{'name': "PlotOverlay", 'type': 'bool', 'value':False})
		self.transposeAxes = self.addChild(
			{'name': 'transpose Axes', 'type': 'bool', 'value': False})
		self.autoRangeX = self.addChild(
			{'name': 'autoRange X', 'type': 'bool', 'value': False})
		self.autoRangeY = self.addChild(
			{'name': 'autoRange Y', 'type': 'bool', 'value': False})
		#signals
		self.plotOverlay.sigValueChanged.connect(self.changePlotOverlay)
		self.transposeAxes.sigValueChanged.connect(self.changeTransposeAxes)
		self.lockAspect.sigValueChanged.connect(self.changeLockAspect)
		self.autoRangeX.sigValueChanged.connect(self.changeAutoRangeX)
		self.autoRangeY.sigValueChanged.connect(self.changeAutoRangeY)
		self.crosshair.sigValueChanged.connect(self.changeCrosshair)
		self.poiShowOnlyMerge.sigValueChanged.connect(self.changePoiShowOnlyMerge)
		self.poiClean.sigValueChanged.connect(self.changePoiClean)


	def setToDefault(self):
		for i in self.childs:
			i.setToDefault()
		#for i in self.crosshair:
		#	i.setToDefault()


	def changeCrosshair(self):
		if self.crosshair.value():
			self.poiShowOnlyMerge.show()
			self.poiClean.show()
			self.display._setCrosshair()
		else:
			self.poiShowOnlyMerge.hide()
			self.poiClean.hide()
			self.display._unsetCrosshair()


	def changePoiShowOnlyMerge(self):
		self.display.poi_show_only_merge = self.poiShowOnlyMerge.value()


	def changePoiClean(self):
		self.display._cleanPOI()
		self.poiClean.setValue(False, blockSignal=self.changePoiClean)


	def changeTransposeAxes(self):
		self.display.transpose_axes = self.transposeAxes.value()
		self.display.scale_plot = True
		self.display._setAxisLabels()
		self.display.update()


	def changePlotOverlay(self):
		if self.plotOverlay.value():
			self.display.addPlotOverlay()
		else:
			self.display.removePlotOverlay()
		self.display.update()


	def changeAutoRangeX(self):
		if self.autoRangeX.value():
			self.display.enableAutoRangeX = True
		else:
			self.display.enableAutoRangeX = False
		self.display.update()


	def changeAutoRangeY(self):
		if self.autoRangeY.value():
			self.display.enableAutoRangeY = True
		else:
			self.display.enableAutoRangeY = False
		self.display.update()


	def changeLockAspect(self):
		if self.lockAspect.value():
			self.display.view.setAspectLocked(True)
		else:
			self.display.view.setAspectLocked(False)
		self.display.scale_plot = True
		self.display.update()



class readoutPlotRates(pTypes.GroupParameter):
	'''
	in case of an interactive plotted readout of the sources
	this class provides the parameters to change the plotrate (frames per second)
	and the readoutrate (lines per second)
	'''

	def __init__(self,Gui,**opts):#
		self.Gui = Gui
		opts['type'] = 'bool'
		opts['value'] = True
		pTypes.GroupParameter.__init__(self, **opts)
		#add parameters
		self.paramFPS = self.addChild(
			{'name': 'Plot frames per second', 'type': 'int',
			'value': self.Gui.fps, 'limits': (1, 200)})
		self.paramLimitLPS = self.addChild(
			{'name': 'Limit readout-rate', 'type': 'bool',
			'value': self.Gui.limitReadoutRate})
		self.paramLPS = self.paramLimitLPS.addChild(
				{'name': 'lines per second', 'type': 'int',
				'value': self.Gui.lps, 'limits': (0, 100000), 'visible':False})
		self.readoutEveryNLine = self.addChild(
			{'name': 'Readout every n line (+-)', 'type': 'int',
			'value': self.Gui.matrixClass._getReadoutEveryNLine()})
		#signals
		self.paramLPS.sigValueChanged.connect(self.changeLPS)
		self.paramFPS.sigValueChanged.connect(self.changeFPS)
		self.paramLimitLPS.sigValueChanged.connect(self.changeLimitReadoutRate)
		self.readoutEveryNLine.sigValueChanged.connect(self.changeReadoutEveryNLine)
		self.changeLimitReadoutRate()


	def changeReadoutEveryNLine(self):
		self.Gui.matrixClass._setReadoutEveryNLine(self.readoutEveryNLine.value())


	def changeLimitReadoutRate(self):
		self.Gui.limitReadoutRate = self.paramLimitLPS.value()
		if self.paramLimitLPS.value():
			self.paramLPS.show()
		else:
			self.paramLPS.hide()
		self.changeLPS()


	def changeFPS(self):
		self.Gui._setFPS(self.paramFPS.value())


	def changeLPS(self):
		self.Gui._setLPS(self.paramLPS.value())