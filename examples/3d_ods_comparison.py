# -*- coding: utf-8 *-*

# this example shows you the posiblity to compaire and connect values of
# different sources.

# the make this more elusive imagine there are two bavarian professors
# roaming trough the deep bavarian forest (in direction x,y) and explore rare butterflies.
# there are 5 different types of them: (0,1,2,3,4).
# both professors want to know whats the best height for its habitat
# there are some differences in the written results of the professors:
	# * different prefixes (one write distances in km, the other im m)
	# * differenct ammount of values
	# * different resolutions of the basiDimensions
	
# the aim is to connect the results of the 'Type' and to compair the results of
# "best height/Mueller" with "best height/Schroeder"

from diaGrabber import source, target, plot
from diaGrabber.source.methods import merge, calc, exclude, transform


#here are Prof. Muellers results:
#################################
mueller = source.libreOfficeCalc(
	file= "3d_b.ods", folder="ressources/", sheet="result", dataType="float")
##BASIS (in km)
x = mueller.basisDimension(
	name="x",unit="m", prefix='k',cellRange="a2:a229", resolution=20)

y = mueller.basisDimension(
	name="y", unit="m", prefix="k", cellRange="b2:b229", resolution=20)

##MERGE
type_max = mueller.mergeDimension(
	name="Type", unit="-", cellRange="d2:d229", merge=merge.max())

bestHeight = mueller.mergeDimension(
	name="best height/Mueller", unit="m", prefix="c", cellRange="c2:c229")
# the best height is defined as the height, where the type is maximal
bestHeight.alias().append(type_max)



# and this are Prof. Schroeder results:
#######################################
schroeder = source.libreOfficeCalc(
	folder="ressources/", file= "3d_a.ods", sheet="sheet1", dataType="float")

##BASIS## (in m)
x = schroeder.basisDimension(
	name="x",unit="m", cellRange="a2:a317", resolution=30)

y = schroeder.basisDimension(
	name="y", unit="m", cellRange="b2:b317", resolution=30)

##MERGE##
type_max = schroeder.mergeDimension(
	name="Type", unit="-",
	cellRange="d2:d317",merge=merge.max())

bestHeight = schroeder.mergeDimension(
	name="best height/Schroeder",  prefix="c",
	unit="m", cellRange="c2:c317")
bestHeight.alias().append(type_max)
# in contrast to prof. mueller prof. schroeder also captured the quantity of the
# butterflies:
quantity = schroeder.mergeDimension(
	name="Quantity", unit="-", cellRange="e2:e317")



# now we hand over the results of Prof. Schroeder and Prof. Mueller to the target:
t = target.coarseMatrix( (schroeder,mueller) )


#we create the Gui-instance
p = plot.Gui(t, colorTheme = "bright")

# we fill our target interactive
# (later we will see the routes that both profs. have taken)
t.fillInteractive(p,
	# ..and limit the number of readout-lines per second to 20
	lps=20,
	# ... frames per second will be 5
	fps=5,
	# ... and show (at first) only two merge-values
	show=[("best height/Schroeder",'x','y'),("best height/Mueller",'x','y')]
	)

# we like to interpolate one the results without ovewriting them
# that's why we copy the relevant result
t.copyMerge("Type","Type2")

# now we start the interpolation with 'interpolateFine'
# this is a very powerfull, but slow method:
t.interpolateFine(
	# we want to interpolate only the following result:
	mergeName=["Type2"],
	# the focusexponent weight the moments of the existent point on an empty
	# point as follows: moment = 1 / (distance_to_point^focusExponent)
	# therefore a big focusExponent gives very sharp crossover between points
	focusExponent=12,
	# the moment of existent points depends on the ammount of points in this cell
	evalPointDensity=True,
	# we dont want to get interpolated values on points which are to far away
	# so we define a max. absolute distance:
	maxDistance={"x":1e3,"y":1e3} # which is 1 km
	)

# we copy the result again
t.copyMerge("Type2","Type3")

# the last copy will be posterized. with this method it is quit easy to
# recognize areas in an image which belongs together.
t.posterize(
	# because there were only 5 discrete types (0-4) we take this values again:
	values=[0,1,2,3,4],
	mergeName="Type3" )


# now we want to see all merges - that's why we don't set the show-argument this time
p.plot()
# diaGrabber only draw four different displays - all other are tabbet bedind
# the last display
# trough the power of 'Qt' you can grab a tab and move it wherever you want.
# klick on a display the the right preference-tab will be shown.
