# -*- coding: utf-8 *-*
from diaGrabber import source, target, plot
from diaGrabber.methods import merge, calc, exclude, transform


command = "/home/bedrich/Programme/c_M2i_3013/0_KARL_rec_fifo_single_terminal/rec_single_terminal"
start_via = ""
stop_via = "done"#"Finished..."

dim_seperator = " "
#data_type = "hex"
#data_type = "int"
data_type = "float"

key_to_end_process = "\x1a"#esc

f = source.stream(command, start_via, stop_via,
	dim_seperator, data_type, key_to_end_process)

c = f.dimension("counter",None)
c.setCounter(0,1)
resolution = 50
#c.setCounter(0,1)
#resolution = 1
c.includeChronic(resolution)

ch0 = f.dimension(" ch0",0)
ch0.includeFromTo(-5, 5, resolution)#ausschnitt
ch0.merge = merge.mean()

ch1 = f.dimension(" ch1",1)
ch1.includeFromTo(-5, 5, resolution)#ausschnitt
ch1.merge = merge.mean()


basis_dim = [c]#
merge_dim = [ch0, ch1]#,cos]



#basis_dim = [Ux,Uy]
#merge_dim = [I]
derivate_dim = c#nicht impl.



f.setReadoutEverNLine(1000)#(1000)##e5)

f.setInfoEveryNLines(1e5)

t = target.coarseMatrix(basis_dim,merge_dim,derivate_dim, f)
#t.fill()
#t.interpolate('cubic')

#p = plot.matPlotLib(t)
##p.graph()
#p.heatMap()
##p = plot.multiPlot(t)
#p.show()
#s.c.setPlotRange(None,None,10)
#s.c.setPlotOnlyRecentPosition()

p = plot.interactive(t, fps = 20, enableAutoRange = ['x'])


t.save("fein_s", "test","bin")
#t.save("fein_s", "test","txt")
