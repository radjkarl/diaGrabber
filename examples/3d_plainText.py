# -*- coding: utf-8 *-*

# This example shows the readout of a large plainText-file
# during this example you will see the Gui (the graphical user interface) for
# 3 times.
# to know where you are in the procedure, I will tag this positions like this:
###################
######(SEE?)#######
###################

# at first some business as usual: we import everything that we need from diaGrabber
from FEPdiaGrabber import source, target, plot
from diaGrabber.source.methods import merge, calc, exclude, transform

# our file is located in ressources/, each dimension is seperated with a space
# the values are of type float (something like 1.23)
f= source.plainText(
	folder="ressources",
	file="large.txt",
	dimSeperator=" ",
	dataType="float",
	#using the following attribute we avoid the (maybe time-expensive)
	#counting of lines:
	nFileLines=40000
	)


# this file is the result of a simulation of a 2d-scan of an electron-beam (eBeam)

# in the file is a timestamp the the beginning of each line:
time=f.mergeDimension(name="time",unit="s",index=0)
# the eBeam scans with a triangle-wave over a substrate
# therefore it moves in x-direction with a simple linear ramp-function
ramp = f.basisDimension(name="ramp",unit="V", index=1, resolution=300)
# and in y-direction with a triangle-function
triangle = f.basisDimension(name="triangle",unit="V",index=2, resolution=300)
# and the signal of an apperature to measure the eBeam:
beam=f.mergeDimension(name="beam",unit="V",index=3)



# the following definitions are optional
##############

# the sweep-signal of the scan in stored in Volt
# to get the real deviation we need to transform the Volt-signal into Meters:
Volt2m_x = transform.interpolationTable([
	[-1,-74.095e-3*2],
	[0,   0],
	[1, 64.701e-3*2]
	], "m")
Volt2m_y = transform.interpolationTable([
	[-1, -53.168e-3*2],
	[0,   0],
	[1,   51.716e-3*2]
	], "m")
# the transform-module has many other fancy classes to transform units
# checkout the documantation!

#now we append the two transform-instances to our sweep-signals:
ramp.transform().append(Volt2m_y)
triangle.transform().append(Volt2m_x)

# for some reason we only want to take those values where the triangle moves up.
# to exclude all other values we let diaGrabber calculate the middle-difference
# of the last 3 values of the triangle-signal
# because of the simulated scan we could also only use the last value, but
# in real measurements the fluctuation of a signal can be so large that we need
# to middle our calculations in some way
triangle.calc().append(calc.delta(3))
# now we define to exclude all values where the result of the calculated values
# is less than zero:
triangle.exclude().append(exclude.calcSmallerValue(triangle.calc().get(0), 0.0))

# we give the source to our target:
t = target.fineMatrix(f)

# we initiate the graphical user interface:
p = plot.Gui(t,
	colorTheme = "bright")

# our source is relatively large, maybe we dont want to readout every line in it.
# to spare time we choose only to read every fifth line in the first run:
f.setArgs(readoutEveryNLine=5)

# we readout the source and fill the target with its values
t.fill()
# we command to plot
p.plot()
###################
######(SEE?)#######
###################

# because we didn't know the range in which our basisDimensions vary diaGrabber will
# scanns the file before the first readout for the max. and min. values of
# all unbounded basisDimensions
# if we used 'fillInteractive(p)' than 'fill' we would see a bright point somewhere in the image.
# this is our point of interest.
# diaGrabber allow you to zoom to a defined point in the targetMatrix.
t.autoZoom(
	mergeName='beam',
	value="max", # in this case we are looking for the maximum value of 'beam'
	scale="relative",
	level=0.15,
	# we want to set a range for all basisDimensions of 15% above and under the point
	)

# now we want to read every line from the source:
f.setArgs(readoutEveryNLine=1)


# we fill our matrix again. but now we want to look at the readout-process
# with the following method:
t.fillInteractive(p, fps=5)


# now i want to show you some process-methods for matrix-like targets:

# this method allows you to transform all dimensions which has a filled
# transform()-container
t.transformDim(rebuildMatrix=False)
# if our tranfrom-method is far away from linear function we also can rebuild
# the matrix after the transfromation via rebuildMatrix=True

# this transformation only works for those transfrom-instances which wouldnt
# have an adhoc-transformation in the readout-process. to do this just add the
# argument 'adhoc=True' in a transform-instance


# as you have seen our bright point is better resolved now. but there is much empty
# space arround it. to fill the gaps we choose the following interpolation-method
# on our 'beam'-field
t.interpolateFast(mergeName="beam", method="cubic")


# finally we plot again.
p.plot()
###################
######(SEE?)#######
###################