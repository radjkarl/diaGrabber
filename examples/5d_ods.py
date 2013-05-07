# -*- coding: utf-8 -*-

# This example show you the possibility of working with multidimensional problems

# As usual we need to include all modules of diaGrabber
from diaGrabber import source, target, plot
from diaGrabber.source.methods import merge, calc, exclude, transform


# This is our source: a libreOffice-document.
# There are two sheets in the document:
	# in 'functions' are all values written as a function of the mergeDimension
	# in 'values' are only the raw values of it.
	# REMEMBER: source.libreOfficeCalc can only read out values, not functions!
ods = source.libreOfficeCalc(
	file= "5d.ods", folder="ressources/", sheet="values", dataType="float")

# In this dokument one mergeDimension (merge) depends on four different
# basisDimensions (one,two,tree,four)
merge = ods.mergeDimension(
	name="merge", unit="-", cellRange="F3:F600", merge=merge.max())

# the given prefix 'm' stands for milli. If you use this attribute all values
# were transformed in the readout. in this case /1000
one = ods.basisDimension(
	name="one",unit="m/s", cellRange="A3:A600", resolution=40)
two = ods.basisDimension(
	name="two", prefix="m", unit="m/s", cellRange="B3:B600", resolution=40)
three = ods.basisDimension(
	name="three", prefix="m", unit="m/s", cellRange="C3:C600", resolution=40)
four = ods.basisDimension(
	name="four", prefix="m", unit="m/s", cellRange="D3:D600", resolution=40)


# now we put the source 'ods' into the target
t = target.fineMatrix( ods )

# the command to fill the target with the values of the source
t.fill()


# to see the result we need to create a instance of plot.Gui:
p = plot.Gui(t,
	colorTheme = "bright",
	closeWhenFinished = False)
# there are many ways to individualize the Gui. You can find all possible
# attributes in the documentation of this class.


# now the command to plot:
p.plot()

# if everything worked well you should see a grey-image and on the left side
# a preference-menue. Right-click on the colorbar to choose a different set of
# colors.
# because its very hard to visualize data with more than 3 dimensions (x,y,contrast)
# the mergeValues in the basisDimensions 'tree' and 'four' were concentrated.
# the standard for this procedure is 'mean'

# if a mergeDimension is fragmented in a basisDimension it can be better to
# use 'sum' instead of 'mean'.

# it is also possible to show the mergeValues at a given 'position' of the
# basisDimension or to show the basisDimension a a timeline via 'as time'.

# a very fancy method is to slice your nD-target. to understand this think of
# a tasty smoked peanut-tofu. imagine the color the tofu is your mergeDimension
# and the position x,y,z are your basisDimensions. your are not able to see
# through the tofu. you only see the border.
# using slices is like taking a knife and slice the tofu in every position you want.
# to use this function you first have to create a second display-widget with
# the add-button on the main widget.
# than 'activate' the slice, choose this its displaynumber and the basisDimension
# you want to look at.
# et voila: a line appears and on the second image the slice is shown.


# now close the image.
# i want you to show the method 'fillInteractive'. With this you can watch the
# plot while the sources were readout.
t.fillInteractive(p,lps=10)
# lps stands here for 'lines-per-second'

# if everything works you see the plot -black-.
# as you see the image 'is filled' with the values of the source - but quite slow.
# you can speed up the readout trough deactivating the limit of the readout-rate.
# the main reason of the slow readout is however the time-expensive plotting of the image.
# therefore you can fill your target faster is you decrease the 'frames per second'
# from 20 (default) to ... maybe 5?

# annother method to accelerate the procedure is to decrease the displayed size of
# your target trough manipulating the 'plot-range' of the displayed basisDimensions
# there are three values: the start- and stop-position and the step.
# if your basis has a resolution of 40 there are 0 to 39 positions.
# increasing the 'step' indicates diaGrabber only to plot every 'step' position
# eg. start=0, stop=20, step=5 will only plot the positions 0,5,10,15,20