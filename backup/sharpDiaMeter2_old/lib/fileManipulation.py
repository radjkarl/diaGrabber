# -*- coding: utf-8 -*-
import os

def writeValues(file_name, output_dimensions, print_values, header_string, folder_name):
	if len(print_values) != 0 and len(print_values[0]) != 0:
		###create file-structure
		folder_name_parts = folder_name.split("/")
		folder_name = folder_name_parts[0]
		for i in range(1,len(folder_name_parts)):
			if os.path.isdir(folder_name) == False:
				os.mkdir(folder_name)
			folder_name += ("/" + folder_name_parts[i])


		if not os.path.isdir(folder_name):
			os.mkdir(folder_name)

		dat_file = folder_name + "/" + str(file_name)
		
		##format print-values
		
		


	
		dat_file = file(dat_file, 'w')
		##get the optional space between the collumns
		space = []
		space2 = []
		for line in print_values:
			for values in line:
				space.append(len(str(values)))
		space = max(space)
		for values in output_dimensions:
			space2.append(len(str(values)))
		space2 = max(space2)
		if space2 > space: ## sort after existing space if those is longer
			space = space2
		space = '{:>' + str(space) + '}'
	
			## create header ##
		output_dimensions_line = ""
		print_line = ""
		print >> dat_file, header_string
		for m in range(len(output_dimensions)):
			output_dimensions_line += space.format(output_dimensions[m]) + "\t"
		print >> dat_file, "#  ",output_dimensions_line
	
		for line in print_values:
			## fill-in the values ##
			for values in line:
				print_line += space.format(values)  + "\t"
			print >> dat_file, "   ", print_line
			print_line = ""
		dat_file.close()
