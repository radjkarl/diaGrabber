.. _introduction:


***************
Introduction
***************
The basic idea of diaGrabber is shown in the following image and will be described now.

.. image:: _static/idea_of_diaGrabber.png
   :scale: 50 %

Imagine to have some data, maybe stored in a file or generated through a stream. 
``diaGrabber`` calls this **source**.
Each source includes values sorted in **basis-** and **mergeDimensions**. See :ref:`dimension` for more information.


The values of the source were stored in a **target** which usualy is a matrix. See :ref:`target` for more information.
It is possible to filter the values before they are stored in a target.
Some of those filters are:

	* **include**: only take values in a range [from,to]
	* **exclude**: exclude values which fullfills some criteria

It is also possible to process the values via:
	* **calc**
	* **transform**

These methods are callable through the dimension-classes. For the methods see :ref:`methods`.

Once the source-values are stored in a target you can do some operations on it. See :ref:`matrixMethods <matrixMethods>` for everything possible.

Finally you can visualize the target with :ref:`Gui`.


You get all possible methods of all modules used in ``diaGrabber`` at :ref:`api`.
Another possibility is to (install and) open an interactive python-shell, like `iPython <http://ipython.org/>`_ or `IDLE <http://en.wikipedia.org/wiki/IDLE_(Python)>`_ 
and to import diaGrabber in it via::

	import diGrabber
	diaGrabber.

and then pressing the **[TAB]-key** shows all possible classes and functions including its `docstrings <http://www.python.org/dev/peps/pep-0257/>`_.

To import all necassary moduls directly type::

	from diaGrabber import source, target, plot
	from diaGrabber.source.methods import merge, calc, exclude, transform
