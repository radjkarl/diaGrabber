# -*- coding: utf-8 *-*
# this is the most easiest example: one file, two dimensions, a simple graph to plot
#######################


# after installing diaGrabber you can create procedures everywhere
# you just have to include some of the modules of diaGrabber via...
from diaGrabber import source, target, plot
from diaGrabber.source.methods import merge, calc, exclude, transform

# thats your source: a libreOffice-file
s = source.libreOfficeCalc(
	file= "ressources/2d.ods", sheet="Tabelle1", dataType="float")

# this will be our 'x'
x = s.basisDimension(
	name="I",unit="mA", cellRange="A2:A100", resolution=50)
# and this our 'y'
y = s.mergeDimension(
	name="time", unit="s", cellRange="B2:B100")

# read more about merge- and basis-dimensions the the documentation
# to understand its differences


# we need a target to fill with the values from our source:
t = target.coarseMatrix(s)
t.fill()


# ... and something to plot:
p = plot.Gui(t, showPreferences=False)
p.plot()

# at the end: we save the plot in file
t.save(name="test",folder="output",ftype="txt")
