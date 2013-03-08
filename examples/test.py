# -*- coding: utf-8 *-*



#class test:
	
	#def __init__(self):
from diaGrabber import source, target, plot
from diaGrabber.methods import merge, calc, exclude, transform

## we want to read data from a very big file. to save storage we create this
## file for this example. therefore we do:

# define a name for our very big file
folder = "ressources/"
file_name = "myBigFile.txt"

# get some math-functions
import math

#create a file
f = file(folder + file_name,"w")

#write one million lines of code
for i in range(100000):
	#every line is build of 3 float-numbers seperated by a space
	f.write("%s %s %s\n" %(math.sin(i),math.sin(i/1000.0), math.cos(i)) )


seperator = " " # a space seperates our float-numbers
data_type = "float" # our numbers of a float-type (other types can be hex or int)

f = source.plainText(folder, file_name, seperator, data_type)


f.readout_every_n_line = 1

t = f.mergeDimension("time", 2)
t.calc.append(calc.delta(10))

Ux = f.basisDimension("Ux",0,90)#, [-0.017, 0.01])
#Ux.includeFromTo(-0.4043, 0.4043)#alles
#Ux.calc.append(calc.delta(100))
Ux.calc.append(calc.delta(10))
Ux.calc.append(calc.divideCalcClasses(Ux.calc[0], t.calc[0]))
Ux.exclude.append(exclude.calcSmallerValue(Ux.calc[1], 0.0))

Ux.transform =  transform.fx("x*23.4/0.8", "x [mm]")

Uy = f.basisDimension("Uy",1,100)#,[-0.025, 0.002])
#resolution = 100
#Uy.includeFromTo(-0.46582, 0.70313)#alles
#Uy.includeFromTo(-0.025, 0.002, resolution)#ausschitt-0.04, -0.01
Uy.transform = transform.fx("x*23.4/0.8", "y [mm]")

f.setBasis([Ux, Uy])


t = target.fineMatrix(f)
t.fill()
#t.transformDim()

#t.interpolate('cubic')

#t.eval2dGaussianDistribution([0.5])

p = plot.matPlotLib(t)
#p.graph()
p.heatMap()
#p = plot.multiPlot(t)
p.show()
t.save("test1", "output","bin")
t.save("test1", "output","txt")


import os
os.remove(folder + file_name) # delete our file - we dont need it any more
