# -*- coding: utf-8 *-*
#import numpy as np
#from copy import deepcopy
import sys
#import scipy
from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph as pg

from diaGrabber import  _utils
from ._plot import _plot

class multiPlot(_plot):
	
	def __init__(self, matrixClass, alt_plotMatrix = "", merge_index = []):
		super(multiPlot, self).__init__(matrixClass, alt_plotMatrix, merge_index)
		
		#super(multiPlot, self).__init__(matrixClass, alt_plotMatrix)
		
	def show(self):

		
		app = QtGui.QApplication([])
		
		## Create window with two ImageView widgets
		win = []
		for m in self.merge_index:
				
			win.append(QtGui.QMainWindow())
			win[-1].resize(800,800)
			cw = QtGui.QWidget()
			win[-1].setCentralWidget(cw)
			l = QtGui.QGridLayout()
			cw.setLayout(l)
			
			#imv1 = pg.ImageView()
	
			self.data = _utils.nanToZeros(self.matrix[m])
	
	
			if self.nDim > 1:
				#set axis name and range
				#=========
				yAxis = pg.AxisItem("left")##y
				#yScale = self.basis_dim[1].resolution/self.basis_dim[1]
				#yAxis.setScale(0.001)
				yAxis.setLabel(units = self.basis_dim[1].name)
				xAxis = pg.AxisItem("bottom")##y
				xAxis.setLabel(units = self.basis_dim[0].name)
				#yAxis.setRange(self.basis_dim[1]._include_from_to[1],self.basis_dim[1]._include_from_to[0])
		
		
				imv1 = pg.ImageView(view=pg.PlotItem(title="hallo", axisItems = {"left": yAxis, "bottom": xAxis}))
				pi = imv1.getView()
	
			else:#simple 2d-plot - no imag
				imv1 = pg.PlotWidget(title=self.merge_dim[m].name)
				#imv1.addLegend(size=None, offset=(30, 30))
				imv1.setXRange(self.basis_dim[0]._include_from_to[0],self.basis_dim[0]._include_from_to[1], padding=0.02)
				imv1.setYRange(min(self.data),max(self.data), padding=0.02)
	
				#imv1.setRange(rect=True, xRange=tuple(self.basis_dim[0].include_from_to), yRange=(min(data),max(data)), padding=0.02, update=True, disableAutoRange=True)
				#imv1.setRange(rect=None, xRange=None, yRange=None, padding=0.02, update=True, disableAutoRange=True)
				pi = imv1.getPlotItem()
			##slice-line
			#roi = pg.LineSegmentROI([[10, 64], [120,64]], pen='r')
			#imv1.addItem(roi)
			
			
			
			l.addWidget(imv1, 0, 0)
			#l.addWidget(imv2, 1, 0)
			
			win[-1].show()
			
	
			
	
			
			#a = np.linspace(1,3,100)
			#data.append(data*2)# = np.linspace(data,data*2,10)
			#data = np.array([data, data*2,data*3])
			#data = np.array([data*10, data*15,data*20])
	
	
			#cross hair
			#===========
				#textLabel for xy
			label = pg.LabelItem(justify='right')
				#draw lines
			vLine = pg.InfiniteLine(angle=90, movable=False)
			hLine = pg.InfiniteLine(angle=0, movable=False)
				#add to image
			#imv1.addItem(vLine, ignoreBounds=True)
			#imv1.addItem(hLine, ignoreBounds=True)
				#get plotItem
				#add label to plotIdem
			pi.addItem(label)
	
				#get viewBow
			vb = pi.vb
			def mouseMoved(evt):
				pos = evt[0]  ## using signal proxy turns original arguments into a tuple
				if pi.sceneBoundingRect().contains(pos):
					mousePoint = vb.mapSceneToView(pos)
					indexX = int(mousePoint.x())
					indexY = int(mousePoint.y())
	
					
					if indexX > 0 and indexX < len(self.sortMatrix[0]):
						label.setText("<span style='font-size: 2pt'>%s=%0.3f,   <span style='color: red'>%s=%0.3f</span>,   <span style='color: green'>%s=%0.3f</span>"
							%(self.basis_dim[0].name, self.sortMatrix[0][indexX], self.basis_dim[1].name,
								self.sortMatrix[1][indexY], self.merge_dim.name, self.matrix[indexX][indexY]) ) #(mousePoint.x(), data[index], data2[index]))
					vLine.setPos(mousePoint.x())
					hLine.setPos(mousePoint.y())
	
			x = vb.scene()
			
			#proxy = pg.SignalProxy(pi.scene().sigMouseMoved, rateLimit=60, slot=mouseMoved)
			#vb.scene().sigMouseMoved.connect(mouseMoved)
	
	
	
			#def update():
				#global data, imv1#, imv2
				#d2 = roi.getArrayRegion(data, imv1.imageItem, axes=(1,2))
				#imv2.setImage(d2)
				
			#roi.sigRegionChanged.connect(update)
			#viewBox1 = imv1.getViewBox()
			#viewBox1.setYRange(0, 10, padding=0.02, update=True)
	
			if self.nDim > 1:
			## Display the data
				imv1.setImage(self.data, xvals = self.sortMatrix[-1])#, transform = True)
			else:
				imv1.plot(self.sortMatrix[0], self.data)
				#print self.sortMatrix[0]
	
			###später:
			###xvals	(np array) 1D array of z-axis values corresponding to the third axis in a 3D image. For video, this array should contain the time of each frame.
			
			
			#imv1.setHistogramRange(min(data), max(data))
			#imv1.setLevels(min(data), max(data))
			
			#update()
			
			## Start Qt event loop unless running in interactive mode.
			#if __name__ == '__main__':
				#import sys
		if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
			QtGui.QApplication.instance().exec_()
			
	
			#p6 = win.addPlot(title="Updating plot")
			#curve = p6.plot(pen='y')
			#data = np.random.normal(size=(10,1000))
	
	
	



class interactive(object):
	
	def __init__(self, matrixClass, **kwargs):
		from pyqtgraph.Qt import QtGui, QtCore
		import numpy as np
		import pyqtgraph as pg
		
		self.matrixClass = matrixClass
		
		#stardard
		fps = 20
		self.enableAutoRange = []
		#individual
		for key in kwargs:
			if key == "fps":
				fps = kwargs[key]
			if key == "enableAutoRange":
				self.enableAutoRange = kwargs[key]

		self.merge_dim = self.matrixClass.merge_dim
		self.basis_dim = self.matrixClass.basis_dim
		self.nDim = self.matrixClass.nDim
		self.nMerge = self.matrixClass.nMerge
		self.end_readOut = False

		self.wait_ms = 1000/fps #frames per second

		##create qt-window
		app = QtGui.QApplication([])
		win = pg.GraphicsWindow(title="Interactive Plot")
		win.resize(1000,600)

		
		if self.nDim > 1:
			#set axis name and range
			#=========
			yAxis = pg.AxisItem("left")##y
			#yScale = self.basis_dim[1].resolution/self.basis_dim[1]
			#yAxis.setScale(0.001)
			yAxis.setLabel(units = self.basis_dim[1].name)
			xAxis = pg.AxisItem("bottom")##y
			xAxis.setLabel(units = self.basis_dim[0].name)
			#yAxis.setRange(self.basis_dim[1].include_from_to[1],self.basis_dim[1].include_from_to[0])
			#self.p6 = pg.ImageView(view=pg.PlotItem(title="testtest", axisItems = {"left": yAxis, "bottom": xAxis}))
			#self.p6 = win.addItem(pg.ImageView())
			self.p6 = win.addViewBox(lockAspect=True)
			self.img = pg.ImageItem()
			self.p6.addItem(self.img)
			self.p6.autoRange()
			

		else:#simple 2d-plot - no imag
			yAxis = pg.AxisItem("left")##y
			xAxis = pg.AxisItem("bottom")##y
			xAxis.setLabel(units = self.basis_dim[0].name)

			self.p6 = win.addPlot(title="Updating plot", axisItems = {"left": yAxis, "bottom": xAxis})
			self.p6.enableAutoRange('xy', False)
			self.curves = []
			
			if self.nMerge > 1:#if there are more plots draw a legend
				self.p6.addLegend()
			else:
				yAxis.setLabel(units = self.merge_dim[0].name)

			#create all plots and ink in range of the colorlist
			colorList = ['r', 'g', 'b', 'c', 'm', 'y', 'k', 'w']
			for i in range(self.nMerge):
				self.curves.append(self.p6.plot(pen=colorList[i%len(colorList)], symbol='+', name=self.merge_dim[i].name))
		

		
		def updateValues():
			
			#lineWise updating data
			#try:
				#print self.end_readOut
			done_readOut = self.matrixClass._fillInteractive(self.end_readOut)
				#print self.matrixClass.mergeMatrix[0]
				#if self.end_readOut == True:
				#	done_readOut = True
			#except KeyboardInterrupt:
				#print "mngng" #dummy to ensure KeyboardInterrupt
			#	self.end_readOut = True
			#	done_readOut = False
			#print self.end_readOut, done_readOut
			if done_readOut or done_readOut == None: #done_readOut = None, if the readoutprocess doesnt func
				 app.quit()#close the window
			
		def updatePlot():
			##########################################
			if self.nDim == 1:
				basis_extract = self.matrixClass.sortMatrix[0][self.basis_dim[0]._plot_range]
				for i in range(self.nMerge):
					merge_extract = self.matrixClass.mergeMatrix[i][self.basis_dim[0]._plot_range]
					self.curves[i].setData(basis_extract, merge_extract )
				#print basis_extract
				if "x" in self.enableAutoRange:
					self.p6.setXRange(self.basis_dim[0]._include_from_to[0],self.basis_dim[0]._include_from_to[1])
				if "y" in self.enableAutoRange:
					##get min, max values for all merge-dims
					#miny = self.merge_dim[0]._include_from_to[0]
					#maxy = self.merge_dim[0]._include_from_to[1]
					#for i in range(1,self.nMerge):
						#if self.merge_dim[i]._include_from_to[0] < miny:
							#miny = self.merge_dim[i]._include_from_to[0]
						#if self.merge_dim[i]._include_from_to[1] > maxy:
							#maxy = self.merge_dim[i]._include_from_to[1]
					#print miny,maxy
					#self.p6.setYRange(miny,maxy)
					self.p6.enableAutoRange('y', True)
				
			elif self.nDim == 2:
				sys.exit("merhere mrge noch nicht drinne")
				merge_extract = self.matrixClass.mergeMatrix[self.basis_dim[0]._plot_range][self.basis_dim[1]._plot_range]
				self.img.setImage(_utils.nanToZeros(merge_extract))
			else:
				sys.exit(NotImplemented)

		timerValues = QtCore.QTimer()
		timerValues.timeout.connect(updateValues)
		timerValues.start(0)
		
		timerPlot = QtCore.QTimer()
		timerPlot.timeout.connect(updatePlot)
		timerPlot.start(self.wait_ms)
		

		if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
			QtGui.QApplication.instance().exec_()



