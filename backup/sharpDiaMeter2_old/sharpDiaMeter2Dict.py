# -*- coding: utf-8 *-*

###################
####DIMENSIONS#####
###################
from src.corrMethods import interpolationTable
from src.corrMethods import function
from src.corrMethods import identically
from src.calcMethods import mean


t = identically()
t.name = "time"
t.index = 0
t.includeFromTo(-0.0262144, 0.02621435)
#t.build("delta") = delta()

Ux = function("x*23.4/0.8") # ==> x[mm]
Ux.name = "Ux"
Ux.index = 1
Ux.includeFromTo(-0.05566, 0.0293)
Ux.calc.append(mean(10))#t.delta,0.001))#shortMean
Ux.calc.append(mean(100))#t.delta,0.001))#shortMean

#Ux.shortMean = Ux.build(mean(t.delta,0.001))#shortMean
#Ux.build.append(mean(t.delta,0.003))
#Ux.longMean = Ux.build(mean(t.delta,0.003))

#Ux.exclude("Ux.shortMean < Ux.longMean")


Uy = function("x*23.4/0.8") # ==> y[mm]
Uy.name = "Uy"
Uy.index = 2
Uy.includeFromTo(-0.46582, 0.70313)


I = identically()
I.name = "I"
I.index = 3


#set range for Ux to [-0.05566, 0.0293]
#set range for Uy to [-0.46582, 0.70313]
#set range for I to [-0.4082, 0.41406]



###################
####PROCEDURES#####
###################
which_class = [
	#"test",
	#"test2",
	#"test3"
	"Ux_t",
	#"Uy_t",
	]



class test:
	file_name = "../test.txt"
	file_type = "plain"
	readout_every_n_line = 50
	#file_name = "../bnArray.npy"
	#file_type = "bnArray"

	categories_separation = " "
	
	matrix_resolution = 100
	fill_matrix_with = I
	middle_over = [Ux]
	plot_to_screen = False
	

class test2:
	file_name = "../test.txt"
	file_type = "plain"
	readout_every_n_line = 50
	#file_name = "../bnArray.npy"
	#file_type = "bnArray"

	categories_separation = " "
	matrix_resolution = 100
	fill_matrix_with = I
	middle_over = [Uy]
	plot_to_screen = False

class test3:
	file_name = "../test.txt"
	file_type = "plain"
	readout_every_n_line = 50
	#file_name = "../bnArray.npy"
	#file_type = "bnArray"

	categories_separation = " "
	matrix_resolution = 100
	fill_matrix_with = I
	middle_over = [Ux,Uy]
	plot_to_screen = False

class Ux_t:
	file_name = "../test.txt"
	file_type = "plain"
	readout_every_n_line = 10
	#file_name = "../bnArray.npy"
	#file_type = "bnArray"

	categories_separation = " "
	matrix_resolution = 100
	fill_matrix_with = Ux
	middle_over = [t]
	plot_to_screen = False

class Uy_t:
	file_name = "../test.txt"
	file_type = "plain"
	readout_every_n_line = 10
	#file_name = "../bnArray.npy"
	#file_type = "bnArray"

	categories_separation = " "
	matrix_resolution = 100
	fill_matrix_with = Uy
	middle_over = [t]
	plot_to_screen = False
