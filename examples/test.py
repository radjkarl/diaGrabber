# -*- coding: utf-8 *-*



#class test:
	
	#def __init__(self):
from diaGrabber import source, target, plot
from diaGrabber.methods import merge, calc, exclude, transform

#folder = "/home/bedrich/Arbeitsfläche/Strahlvermessung/"
folder = "/home/bedrich/Dokumente/HiWi/Strahlvermessung/"

file_name = "test.txt"#"
seperator = " "
data_type = "float"
f = source.plainText(folder, file_name, seperator, data_type)
f.readout_every_n_line = 10


I = f.mergeDimension("I [mA]",1)
#I.transform =  transform.fx("x*1e-3", "I [A]")

I2 = f.mergeDimension("I2 [mA]",1,merge.max())
#I.transform =  transform.fx("x*1e-3", "I [A]")

t = f.mergeDimension("time", 0)
t.calc.append(calc.delta(10))

Ux = f.basisDimension("Ux",3,90,[-0.017, 0.01])
#Ux.includeFromTo(-0.4043, 0.4043)#alles
#Ux.calc.append(calc.delta(100))
Ux.calc.append(calc.delta(10))
Ux.calc.append(calc.divideCalcClasses(Ux.calc[0], t.calc[0]))
Ux.exclude.append(exclude.calcSmallerValue(Ux.calc[1], 0.0))

Ux.transform =  transform.fx("x*23.4/0.8", "x [mm]")

Uy = f.basisDimension("Uy",2,100,[-0.025, 0.002])
#resolution = 100
#Uy.includeFromTo(-0.46582, 0.70313)#alles
#Uy.includeFromTo(-0.025, 0.002, resolution)#ausschitt-0.04, -0.01
Uy.transform = transform.fx("x*23.4/0.8", "y [mm]")

f.setBasis([Ux, Uy])
#basis_dim = [Ux,Uy]
#merge_dim = [I,I2,t]
#derivate_dim = t#nicht impl.


#s.Ux.resolution = 100
#s.Uy.resolution = 100
f.readout_every_n_line = 1

t = target.coarseMatrix(f)
t.fill()
t.transformDim()

t.interpolate('cubic')

t.eval2dGaussianDistribution([0.5])

p = plot.matPlotLib(t)
#p.graph()
p.heatMap()
#p = plot.multiPlot(t)
p.show()
t.save("fein", "test","bin")
t.save("fein", "test","txt")

#if __name__ == '__main__':
#	import sys
#	sys.path.insert(0,"../")
#	test()
