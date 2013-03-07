# -*- coding: utf-8 *-*

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from copy import deepcopy

from diaGrabber import target, _utils
import sys
#import scipy

from ._plot import _plot


class matPlotLib(_plot):
	
	def __init__(self, matrixClass, alt_plotMatrix = "", merge_index = []):
		super(matPlotLib, self).__init__(matrixClass, alt_plotMatrix, merge_index)
		self.fig = []
		for m in range(len(self.merge_index)):
			self.fig.append(plt.figure(figsize=(11, 8), dpi=80))
			#set bg color
			self.fig[-1].patch.set_facecolor('white')
			#fig.patch.set_alpha(0.7)
		

	def graph(self, title = ""):
		if title != "":
			plt.suptitle(title)
		if self.nDim == 2:
			XY,Z = self.matrixClass.transformMatrixToPoints()
		for  m in range(len(self.merge_index)):
			ax1 = self.fig[m].add_subplot(111)
			#3D
			if self.nDim == 2:

				
				#ax = self.fig.add_subplot(111, projection='3d')
				ax = Axes3D(self.fig[m])
				ax.set_xlabel(self.basis_dim[0].name)
				ax.set_ylabel(self.basis_dim[1].name)
				ax.plot_wireframe(XY[self.merge_index[m]][0],XY[self.merge_index[m]][1], Z[self.merge_index[m]])
				
			##2D
			elif self.nDim == 1:
				
				ax1.set_ylabel(self.merge_dim[self.merge_index[m]].name)
				ax1.set_xlabel(self.basis_dim[0].name)
				#axis_values = self._getAxisValues()
				#plt.xticks( range(self.basis_dim[0].resolution), axis_values[0])
				ax1.plot(self.sortMatrix[0],self.matrix[self.merge_index[m]])
			else:
				sys.exit(NotImplemented)
	
			#self._printPlotOverlay()
			

		
	def heatMap(self, title = ""):
		if self.matrixClass.nDim != 2:
			sys.exit("ERROR: plotting heatmap work only for 2 basis_dim")
		if title != "":
			plt.suptitle(title)

		for  m in range(len(self.merge_index)):
			ax1 = self.fig[m].add_subplot(111)

			data = self.matrix[self.merge_index[m]].transpose()
	
			ax1.set_xlabel(self.basis_dim[0].name)
			ax1.set_ylabel(self.basis_dim[1].name)
			
			#axis_values = self._getAxisValues()
			#plt.xticks( range(self.basis_dim[0].resolution), axis_values[0])
			#plt.yticks( range(self.basis_dim[1].resolution), axis_values[1])
			
			
			axis_range = self._getAxisRange()
	
			#origing... Place the [0,0] index of the array in the upper left or lower left corner of the axes.
			#extend ... transform  px-positions to data-positions
			image = ax1.imshow(data, origin='lower', aspect='auto', extent=axis_range)
			image.set_interpolation('nearest')
			cBar = self.fig[m].colorbar(image)
			#cBar = image.colorbar()#colorbar(ticks=[min(data2[:,2]),max(data2[:,2])])
			#cBar.set_ticks(['Low','High'])
			cBar.set_label(self.merge_dim[m].name)
			
			
			############################
			###########################
			###########################
			##statt der px-positionen die wirktlichen positionen tracken
			###so anpassen, dass es immer ins bild passt
			self._printPlotOverlay()
		
		#alternative: 2d-contour plot:
		#x=r_[-10:10:100j]
	    #y=r_[-10:10:100j]
	    #z= add.outer(x*x, y*y)
	    #### Contour plot of z = x**2 + y**2
	    #p.contour(x,y,z)
	    #### ContourF plot of z = x**2 + y**2
	    #p.figure()
	    #p.contourf(x,y,z)
	    #p.show()
			



	def show(self):
		plt.show()
		


	def _printPlotOverlay(self):
		#plot_overlay = [(points), (lines), (broken lines), , (ellipses), (rectangles), (text), (legend)]
			#(points),(broken lines), (lines)  = [x-list,y-list]
			#(ellipses) = list[ tuple(x,y), float(width), float(height), float(angle) ) ## str(color) ]
			#(rectangles) = list[ tuple(x,y), float(width), float(height) ]
			#(text) = list[ tuple(x,y), string(text)
			#Llegend) = list[str(...),... ]
		if self.plot_overlay != []:
			
			if self.plot_overlay[0] != []:#draw points
				for i in self.plot_overlay[0]:
					plt.plot(i[0],i[1], marker='.')#, color='r', ls='')
					
			if self.plot_overlay[1] != []:#draw broken lines
				for i in self.plot_overlay[1]:
					plt.plot(i[0],i[1], marker=',')#, color='r', ls='')
					
			if self.plot_overlay[2] != []:#draw lines
				for i in self.plot_overlay[2]:
					plt.plot(i[0],i[1], marker='-')#, color='r', ls='')

			if self.plot_overlay[5] != []:#draw text
				t = ""
				y = 0.95
				for i in self.plot_overlay[5]:
					t += i + "\n"
					y -= 0.034
				t = t[:-2]
				#plt.text(2, y, t, fontsize=14)
				text_layer = plt.annotate(t, xy=(0.025, y), xycoords='axes fraction',
					color = 'black',backgroundcolor = 'white')
				#set semitransparent background for text-layer
				text_layer.set_bbox(dict(facecolor='white', alpha=0.5))
				
			if self.plot_overlay[6] != []:#draw legend

				for i in self.plot_overlay[6]:
					plt.legend(tuple(self.plot_overlay[6]),
					loc='upper center', bbox_to_anchor=(0.5, -0.05),
          fancybox=True, shadow=True, ncol=5)#, color='r', ls='')
			plt.legend()


			

	def save(self,file_name, folder_name = ""):
		file_name = _utils.prepareFileSystem(file_name, folder_name)

		self.fig.savefig(file_name,
			facecolor=self.fig.get_facecolor(), edgecolor='none')

	def _getAxisValues(self):
		###transform sort_values to viewable axis-values
		axis_values = []
		for i in range(self.nDim):
			steps = int(self.basis_dim[i].resolution/5)

			axis_values.append([])
			n = steps
			for j in range(self.basis_dim[i].resolution):
				if n == steps:
					axis_values[i].append('{0:.1g}'.format(self.sortMatrix[i][j]))
					n = 0
				else:
					axis_values[i].append("")
					n += 1
		return axis_values
		
	def _getAxisRange(self):
		axis_range = []
		for i in range(self.nDim):
			axis_range.append(self.basis_dim[i].include_from_to[0])#min
			axis_range.append(self.basis_dim[i].include_from_to[1])#max
		#extent = [xedges[0], xedges[-1], yedges[0], yedges[-1]]
		return axis_range




