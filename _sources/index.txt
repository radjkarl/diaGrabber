.. diaGrabber documentation master file, created by
   sphinx-quickstart on Fri Mar  1 18:11:22 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.
 
**diaGrabber** -> read, process, plot, automate
==============================================================================
``diaGrabber`` is a module fully written in `Python <http://www.python.org/>`_.
Its main benefits are:

* no restriction to 2- or 3-dimensional problems
* handle unstructured data
* no limitation of the size of source-files
* interactive visualization of the readout of sources
* compair and connect multiple source-files (also of different file-types like plainText or libreOfficeCalc)
* fully automatable
* powerfull options to manipulate and filter values
* inter-/extrapolate between given points

some impressions:
^^^^^^^^^^^^^^^^^
.. image:: _static/screen1.png
   :scale: 25 %
   :alt: compare different sources

.. image:: _static/screen2.png
   :scale: 25 %
   :alt: readout streams in realtime

.. image:: _static/screen3.png
   :scale: 25 %
   :alt: orking with n-dimensional problems


Requirements
=============
* `Python v2.7 <http://www.python.org/download/releases/2.7.4/>`_ (the programming lanuage itself)
* `pyqtgraph <http://www.pyqtgraph.org/>`_ v.0.9.6 (for Plotting)
	* this module needs either pyQt4 or pySide to work
	* if you are using windows, install `pySide <http://qt-project.org/wiki/PySide_Binaries_Windows>`_ (pyQt4 wont support all features)
* `ooolib <https://sourceforge.net/projects/ooolib/>`_ (to read from open-/libreOffice-calc)
* `numpy/scipy <http://www.scipy.org/Download>`_ (Python modules for numeric and scientific problems)
* `bottleneck <http://berkeleyanalytics.com/bottleneck/>`_ (superfast NaN-array-handling)


Installation
============

1. download and install all required modules. 
2. `download <https://github.com/radjkarl/diaGrabber/archive/master.zip>`_ ``diaGrabber``, go to its main-directory and type in a termial:

... **in Linux**::

   sudo python setup.py install

... **in Windows**

* Start -> Run -> 'cmd'
* go to you download-directory and type::

   python setup.py install

If windows doesn't know the commend 'python', try `this <http://stackoverflow.com/questions/4621255/how-do-i-run-a-python-program-in-the-command-prompt-in-windows-7>`_.

Use the functions of diaGrabber via::

   import diaGrabber

in a Python script or shell. See the :ref:`examples` to get an idea of it.


Support
============
* `fork the code and collaborate <https://github.com/radjkarl/diaGrabber>`_
* `post issues <https://github.com/radjkarl/diaGrabber/issues>`_
* `propose improvements and send quentions <https://github.com/radjkarl/diaGrabber/wiki>`_



Contents:
=========
 
.. toctree::
   :maxdepth: 2

   introduction.rst
   examples.rst
   gui.rst
   diaGrabberAPI.rst






Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

