import math
n=0

while True:
	n+=0.01
	
	print 40*math.sin(n)+n, 40*math.cos(n)+n
	if n>1e4:
		break

while True:
	print "done"
