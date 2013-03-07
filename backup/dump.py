# -*- coding: utf-8 *-*
		def interpolateDiscrete(self, data, invalid=None):
			"""
			Replace the value of invalid 'data' cells (indicated by 'invalid')
			by the value of the nearest valid data cell
			
			Input:
				data:    numpy array of any dimension
				invalid: a binary array of same shape as 'data'. True cells set where data
				value should be replaced.
				If None (default), use: invalid  = np.isnan(data)
			
			Output:
				Return a filled array.
			"""
			if invalid is None: invalid = numpy.isnan(data)
			ind = scipy.ndimage.distance_transform_edt(invalid, return_distances=False, return_indices=True)
			return data[tuple(ind)]
