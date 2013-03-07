#!/usr/bin/env python
from distutils.core import setup

setup(name= "diaGrabber",
	version = "0.1.1",
	description = "...",
	long_description = "...",
	author = "Karl Bedrich",
	author_email = "karl@bedrich.de",
	url = "???",
	packages = ['diaGrabber', 'diaGrabber.source', 'diaGrabber.target', 'diaGrabber.methods', 'diaGrabber.plot'],
	data_files = [],#[('mingus_examples/pygame-drum', ['mingus_examples/pygame-drum/pad.png',\
			  		#     'mingus_examples/pygame-drum/pygame-drum.py']),\
			#('mingus_examples/pygame-piano', ['mingus_examples/pygame-piano/pygame-piano.py',
				 			#   'mingus_examples/pygame-piano/keys.png'])],
	classifiers = [
			'Intended Audience :: Developers',
			'Intended Audience :: Science/Research',
			'Intended Audience :: Other Audience',
			'License :: OSI Approved :: GNU General Public License (GPL)',
			'Operating System :: OS Independent',
			'Programming Language :: Python',
			'Topic :: Scientific/Engineering :: Information Analysis',
			'Topic :: Scientific/Engineering :: Visualization',
			'Topic :: Software Development :: Libraries :: Python Modules',
			]
	)
