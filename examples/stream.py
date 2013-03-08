# -*- coding: utf-8 *-*
from diaGrabber import source, target, plot
from diaGrabber.methods import merge, calc, exclude, transform


#command = "/home/bedrich/Programme/c_M2i_3013/0_KARL_rec_fifo_single_terminal/rec_single_terminal"
command = "python /home/bedrich/diaGrabber3/examples/ressources/test_stream.py"

start_via = ""
stop_via = "done"
run_in_shell = True
dim_seperator = " "
data_type = "float"

key_to_end_process = "\x1a"#esc

f = source.stream(command, start_via, stop_via,
	dim_seperator, data_type, key_to_end_process, run_in_shell)
c = f.basisDimension("counter",0, 50, "chronic")


ch0 = f.mergeDimension(" ch0",0,merge.max())

ch1 = f.mergeDimension(" ch1",1)




f.setReadoutEverNLine(1)#(1000)##e5)

f.setInfoEveryNLines(1e5)

t = target.coarseMatrix(f)


p = plot.interactive(t, fps = 20, enableAutoRange = ['x'])


t.save("fein_s", "test","bin")
#t.save("fein_s", "test","txt")
