# -*- coding: utf-8 *-*

## this example show you to read source-files from multiple folders
## have a look at diaGrabber/examples/ressources/timeFolders
## here you will find hundreds of folders. in every folder is a file called
## "line5_T.xy". it include values of a distance and a temperature
## the folders itself represents different time-values
########################################################

## at first we import everything we need from diaGrabber
from diaGrabber import source, target, plot
from diaGrabber.source.methods import merge, calc, exclude, transform

## we create a instance of a plainText-source
f= source.plainText(
	folder="ressources/timeFolders",
	file="line5_T.xy",
	dimSeperator=" 	",
	dataType="float",
	## we don't want to see the statusbar for every file, so we set:
	silentReadout=True
	## if you want to have a message for every new file readout, set
	## silentReadout to False
	)

## if we dont want to do further work on the dimensions itself we dont have to
##  write x = source.xDimension - just calling the method is enough
f.basisDimension(name="distance",unit="m", index=0, resolution=300)
f.mergeDimension(name="Temperature",unit="K",index=1)

## here comes the new part: the folders in the main 'timeFolder' will
## represent a basisDimension. trough defining index='folder'
## if you have a nested system of folders you can add further basisDimensions
## like the following. in this case the order of reference builds the folder-system
f.basisDimension(name="time",unit="s",index="folder", resolution=300)

## we create a target and a GUI-instance
t = target.coarseMatrix( (f) )
p = plot.Gui(t,colorTheme = "bright")

## we command diaGrabber to readout all source-files and to fill the target through:
t.fill()
## we command to plot:
p.plot()


# the interactive readout works too:
t.fillInteractive(p, fps=5)
