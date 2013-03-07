# -*- coding: utf-8 *-*

from diaGrabber import source, target, plot
from diaGrabber.methods import merge, calc, exclude, transform




class settings4:
	
	#def __init__(self):
		

	command = "./../../Treiber/cSpcm/0_KARL_rec_fifo_single_ascifile/rec_single_asciifile"
	start_via = ""
	stop_via = "done"#"Finished..."
	output_file = "./../../Treiber/cSpcm/0_KARL_rec_fifo_single_ascifile/FIFO_ascii_test.txt"
	dim_seperator = " "
	#data_type = "hex"
	#data_type = "int"
	data_type = "float"
	key_to_end_process = "\x1a"#esc
	
	f = source.plainTextStream(command, start_via, stop_via,
		dim_seperator, output_file, data_type, key_to_end_process)
	
	c = f.dimension("counter",None)
	c.setCounter(0,1)
	resolution = 50
	#c.setCounter(0,1)
	#resolution = 1
	c.includeChronic(resolution)

	I = f.dimension("I [mA]",1)
	I.merge = merge.mean()
	#I.includeFromTo(-0.05566, 0.0293)
	#I.transform =  transform.fx("x*1e-3", "I [A]")

	t = f.dimension("time", 0)
	resolution = 300
	t.includeFromTo(-0.0262144, 0.02621435, resolution)

	#Ux = f.dimension("Ux",3)
	##Ux.includeFromTo(-0.4043, 0.4043)#alles
	#resolution = 90
	#Ux.includeFromTo(-0.017, 0.01, resolution)#ausschnitt
	#Ux.calc.append(calc.delta(100))
	#Ux.exclude.append(exclude.calcSmallerValue(0, 0.0))

	#Ux.transform =  transform.fx("x*23.4/0.8", "x [mm]")
	#
	#Uy = f.dimension("Uy",2)
	#resolution = 100
	##Uy.includeFromTo(-0.46582, 0.70313)#alles
	#Uy.includeFromTo(-0.025, 0.002, resolution)#ausschitt-0.04, -0.01
	#Uy.transform = transform.fx("x*23.4/0.8", "y [mm]")


	basis_dim = [c]
	merge_dim = [I,t]
	derivate_dim = t#nicht impl.



class settings2:
	
	def __init__(self):
		
	
		#folder = "../"
		#file_name = "testStream.py"#"
		command = "python ../testStream.py"
		start_via = "go"
		stop_via = "done"#"Finished..."
	
		dim_seperator = " "
		data_type = "float"
		
		f = source.stream(command, start_via, stop_via,
			dim_seperator, data_type)
	
		c = f.dimension("counter",None)
		c.setCounter(0,1)
		resolution = 30
		#c.setCounter(0,1)
		#resolution = 1
		c.includeChronic(resolution)
		sin = f.dimension(" sin",1)
		sin.merge = merge.mean()
		cos = f.dimension(" cos",2)
		cos.merge = merge.mean()
		
		basis_dim = [c]#
		merge_dim = [sin,cos]
	
	
	
		#basis_dim = [Ux,Uy]
		#merge_dim = [I]
		derivate_dim = c#nicht impl.


class settings3:
	command = "./../../Treiber/cSpcm/0_KARL_rec_fifo_single_terminal/rec_single_terminal"
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



class vglGrobFein:
	
	def __init__(self):
		
		s = settings1()
		
		s.f.readout_every_n_line = 50
		s.Ux.resolution = 20
		s.Uy.resolution = 20
	
		t1 = target.coarseMatrix(s.basis_dim,s.merge_dim,s.derivate_dim, s.f)
		t1.fill(s.f)
		p = plot.matrix(t1)
		p.heatMap("grob20")
		p.save("20grob", "vglGrobFein")
	
		t2 = target.fineMatrix(s.basis_dim,s.merge_dim,s.derivate_dim, s.f)
		t2.fill(s.f)
		p = plot.matrix(t2)
		p.heatMap("fein20")
		p.save("20fein", "vglGrobFein")
		


		s.Ux.resolution = 150
		s.Uy.resolution = 150
	
		t1 = target.coarseMatrix(s.basis_dim,s.merge_dim,s.derivate_dim, s.f)
		t1.fill(s.f)
		p = plot.matrix(t1)
		p.graph("3D")
		p.show()

		p.heatMap("grob150")
		p.save("150fein", "vglGrobFein")

		t1.interpolate("cubic")
		p = plot.matrix(t1)
		p.heatMap("grob150-int")
		p.save("150int_grob", "vglGrobFein")

		t2 = target.fineMatrix(s.basis_dim,s.merge_dim,s.derivate_dim, s.f)
		t2.fill(s.f)
		p = plot.matrix(t2)
		p.heatMap("fein150")
		p.save("150fein", "vglGrobFein")
		
		p = plot.matrix(t2, "densityMatrix")
		p.heatMap("fein155_dichte")
		p.save("150fein_density", "vglGrobFein")

		t2.interpolate("cubic")
		p = plot.matrix(t2)
		p.heatMap("fein150-int")
		p.save("150int_fein", "vglGrobFein")

class speichern:
	def __init__(self):
		
		s = settings1()

		#s.Ux.resolution = 100
		#s.Uy.resolution = 100
		s.f.readout_every_n_line = 1
		
		t = target.coarseMatrix(s.basis_dim,s.merge_dim,s.derivate_dim, s.f)
		t.fill()
		t.interpolate('cubic')

		p = plot.matPlotLib(t)
		#p.graph()
		p.heatMap()
		#p = plot.multiPlot(t)
		p.show()
		t.save("fein", "test","bin")
		t.save("fein", "test","txt")

class streamHolen:
	def __init__(self):
		
		s = settings3
		s.f.setReadoutEverNLine(1000)#(1000)##e5)
		
		s.f.setInfoEveryNLines(1e5)

		t = target.coarseMatrix(s.basis_dim,s.merge_dim,s.derivate_dim, s.f)
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
		
class streamTxtHolen:
	def __init__(self):
		
		s = settings4
		s.f.setReadoutEverNLine(100)#(1000)##e5)
		
		s.f.setInfoEveryNLines(1000)

		t = target.coarseMatrix(s.basis_dim,s.merge_dim,s.derivate_dim, s.f)
		t.fill()
		#t.interpolate('cubic')

		#p = plot.matPlotLib(t)
		##p.graph()
		#p.heatMap()
		##p = plot.multiPlot(t)
		#p.show()
		#s.c.setPlotRange(None,None,10)
		#s.c.setPlotOnlyRecentPosition()
		
		#p = plot.interactive(t, fps = 20, enableAutoRange = ['x'])
		

		t.save("fein_s", "test","bin")
		#t.save("fein_s", "test","txt")

class speichern2:
	def __init__(self):
		
		s = settings1()
		file_name = "50ma scharf 622ma 50µm.txt"#"

		s.Ux.resolution = 100
		s.Uy.resolution = 100
		s.f.setReadoutEverNLine(1)
		
		t = target.coarseMatrix(s.basis_dim,s.merge_dim,s.derivate_dim, s.f)
		t.fill(s.f)
		t.save("fein2", "test","bin")
		t.save("fein2", "test","txt")

class ladenEval:
	def __init__(self):
		
		s = settings1()
		
		t = target.coarseMatrix(s.basis_dim,s.merge_dim,s.derivate_dim, s.f)
		t.load("fein2", "test","bin")
		t.transformDim()
		t.interpolate('cubic')
		

		
		dEB_types = [0.6]
		t.eval2dGaussianDistribution(dEB_types, 0)
	
		p = plot.matrix(t)
		
		#p = plot.multiPlot(t)
		p.plot()
		
		p.heatMap()
		p.show()
		p.save("dEB", "test")


class multiPlot:
	def __init__(self):
		
		s = settings1()
		
		#s.f.readout_every_n_line = 50
		#s.basis_dim.append(s.t)
		#s.t.resolution = 1000

		t = target.coarseMatrix(s.basis_dim,s.merge_dim,s.derivate_dim, s.f)
		#t.fill(s.f)
		t.load("fein2", "test","bin")
		t.transformDim()
		t.interpolate('cubic')
		

		
		#dEB_types = [0.6]
		#t.eval2dGaussianDistribution(dEB_types)
	
		#p = plot.matrix(t)
		
		p = plot.multiPlot(t)
		p.show()
		
		#p.heatMap()
		#p.show()
		#p.save("dEB", "test")


class counter1:
	def __init__(self):
		
		s = settings1()
		s.f.readout_every_n_line = 10
		
		s.Ux.calc = []
		s.Ux.exclude = []
		#counter
		c = s.f.dimension("counter",None)
		c.setCounter(0,1/20e6)
		resolution = 300
		#c.setCounter(0,1)
		#resolution = 1
		c.includeChronic(resolution)
		#Ux.includeFromTo(-0.017, 0.01)#ausschnitt
		

		s.basis_dim = [c]#
		s.merge_dim = [s.Ux,s.Uy]
		
		c.setPlotRange(None,None,10)
		
		#c.setPlotOnlyRecentPosition()
		#s.f.readout_every_n_line = 50
		#s.basis_dim.append(s.t)
		#s.t.resolution = 1000

		t = target.coarseMatrix(s.basis_dim,s.merge_dim,s.derivate_dim, s.f)
		
		p = plot.interactive(t, fps = 20, enableAutoRange = ['x'])
		
		#t.fill(s.f)
		
		t.save("counter1", "test","bin")
		t.save("counter1", "test","txt")

		#t.load("fein2", "test","bin")
		#t.transformDim()
		#t.interpolate('cubic')
		

		
		#dEB_types = [0.6]
		#t.eval2dGaussianDistribution(dEB_types)
	
		#p = plot.matrix(t)
		
		#p = plot.multiPlot(t)
		#p.graph()
		#p.show()
		
		#p.heatMap()
		#p.show()
		#p.save("dEB", "test")



class rein:
	def __init__(self):
		
		s = settings1()
		
		s.Ux.exclude = []
		
		t = target.coarseMatrix(s.basis_dim,s.merge_dim,s.derivate_dim)
		t.fill(s.f)
		
		t.interpolate('cubic')
		p = plot.matrix(t)
		p.heatMap()
		p.show()
		p.save("rein", "test")
		
class zweiD:
	def __init__(self):
		
		s = settings1()
		s.basis_dim = [s.t]
		s.merge_dim = s.I
		
		
		t = target.coarseMatrix(s.basis_dim,s.merge_dim,s.derivate_dim)
		t.fill(s.f)
		
		t.interpolate('cubic')
		p = plot.matrix(t)
		p.graph()
		p.show()
		p.save("zweiD", "test")
