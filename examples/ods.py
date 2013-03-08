# -*- coding: utf-8 *-*

from diaGrabber import source, target, plot
from diaGrabber.methods import merge, calc, exclude, transform

#folder = "/home/bedrich/Arbeitsfläche/Strahlvermessung/"
#folder = "/home/bedrich/Dokumente/HiWi/Strahlvermessung/"

file_name = "ressources/ods_example.ods"#"
#seperator = " "
data_type = "float"


###############
p = source.libreOfficeCalc(file_name, "Tabelle1", data_type)

#f.setReadoutEvery_n_line = 10


#one = p.basisDimension("I [mA]",50, "A2:A100", [0,100])
one = p.basisDimension("I [mA]",50, "A2:A100")

#resolution = 50
#one.includeFromTo(0, 100, resolution)


two = p.mergeDimension("time", "B2:B100")
#two.merge = merge.mean()


#basis_dim = [one]
#merge_dim = [two]
#derivate_dim = one#nicht impl.


#s.Ux.resolution = 100
#s.Uy.resolution = 100
p.setReadoutEveryNLine = 3

t = target.coarseMatrix(p)
t.fill()
#t.transformDim()

#t.interpolate('cubic')

#t.eval2dGaussianDistribution([0.5])

p = plot.matPlotLib(t)
p.graph()
#p.heatMap()
#p = plot.multiPlot(t)
p.show()
#t.save("fein", "test","bin")
#t.save("fein", "test","txt")

#if __name__ == '__main__':
#	import sys
#	sys.path.insert(0,"../")
#	test()
