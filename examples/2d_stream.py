# -*- coding: utf-8 *-*

# In this example we want to read values from a programm generating a stream.
# diaGrabber is able to plot the values in realtime - therefore it's possible
# to build something like an oscilloscope.


# business as usual: we import everything that we need from diaGrabber
from diaGrabber import source, target, plot
from diaGrabber.source.methods import merge, calc, exclude, transform



# we create a instance of the stream-source-class
f = source.stream(
	# i've written a programm which will generate a sine and a cosine-stream
	# its written in quess what ... python
	command = "python",
	# thats the name of the file
	file="ressources/test_stream.py",
	# if the stream is complete it will print "done". giving this information to
	# diaGrabber will stopp the readout-process when the stream is done.
	stopVia="done",
	# all values printed in one line are seperated by a space:
	dimSeparator=" ",
	# the stream produces float-numbers:
	dataType= "float",
	# if we want to kill the stream direct from diaGrabber:
	keyToEndProcess="\x1a", #Esc
	# this python-script only works when it's started in a shell - other executables
	# can run without it
	runInShell=True)


# the stream only gives merge-(y)-values.
# therefore we create a basis as a counter
n = f.basisDimension(
	name="n",
	unit="-",
	resolution=50,
	# there are two different counters available:
	index="fixedCounter",#from 0 to 49 (resolution-1)
	#and: index="runningCounter", #from 0 to x, where x in the number of readed lines
	include="chronic"
	# with 'chronic' we define that this basis stores only the last n values,
	# where n is the resolution
	)

# here are our two mergeDimensions:
ch0 = f.mergeDimension(
	name="ch0",
	unit="m",
	index=0)
ch1 = f.mergeDimension(
	name="ch1",
	unit="m",
	index=1)

# to explain to you the merge-method 'alias' we add annother mergeDimension
# which only stores  new value if this value is bigger than the last value at
# the same basis-position
ch0max = f.mergeDimension(
	name="ch0max",
	unit="m",
	index=0,
	merge=merge.max())

# with the following command we let the mergeDimension 'ch1' only to take new
# values if the last value of 'ch0max' also was taken
ch1.alias().append(ch0max)


# now we set some arguments for our stream:
f.setArgs(
	# in many cases the stream-source would produce faster new output, than
	# diaGrabber can process and plot
	# therefore we tell diaGrabber only to grab as much values as it can
	# process in the same time:
	readoutEveryNLine="calc",
	# we want to know the number of skipped lines:
	showCalcNLine = True,
	# every n lines diaGrabber will print a status:
	infoEveryNLine=1e3)

# we give our source to the target:
t = target.coarseMatrix(f)

# we create a Gui-instance (graphical user interface)
p = plot.Gui(t)

# we start the interactive plotting of the readout:
t.fillInteractive(p,
	# we have per default 20 frames-per-second ... but 15 are enough for us
	fps = 15,
	# because our sine-waves increase there values continous an autorange
	# of the y-axis is reasonable
	enableAutoRange = ['y'],
	# one of the tree mergeDimensions was just a 'helper' and we dont want to
	# plot it. so we define what merge to plot over what basis:
	show=[('ch0','n'),('ch1','n')],
	# the the stream in done, the Gui will close too
	closeWhenFinished = True)

# if the stream is complete we save its last values in file:
t.save(name="stream", folder="output",ftype="txt")
