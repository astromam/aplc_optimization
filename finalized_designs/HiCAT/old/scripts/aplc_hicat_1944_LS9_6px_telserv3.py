run_without_gurobipy = False

import matplotlib as mpl
mpl.use('Agg')
from hcipy import *
import numpy as np
import matplotlib.pyplot as plt
if not run_without_gurobipy:
	import gurobipy as gp
from scipy.ndimage.morphology import grey_erosion, grey_dilation
import time

def calculate_pixels_to_optimize(last_optim, pupil_subsampled):
	"""Calculate the pixels to be used for the optimization for the adaptive algorithm.

	The exact selection of the pixels to be taken into account depends on future research.

	Parameters
	----------
	last_optim : Field
		The previously-optimized apodizer.
	pupil_subsampled : Field
		The telescope pupil subsampled to the same resolution as `last_optim`.

	Returns
	-------
	Field
		A boolean mask to indicate which pixels to take into account.
	"""
	if last_optim is None:
		return pupil_subsampled > 0

	structure = np.array([[0,1,0],[1,1,1],[0,1,0]])
	#structure = np.array([[0,1,1,0],[1,1,1,1],[1,1,1,1],[0,1,1,0]])
	#structure = np.array([[0,1,1,1,0],[1,1,1,1,1],[1,1,1,1,1],[1,1,1,1,1],[0,1,1,1,0]])

	a = (grey_dilation(last_optim.shaped, structure=structure) - grey_erosion(last_optim.shaped, structure=structure)).ravel() - 2
	a = np.abs(a) > 1e-3

	b = np.logical_and(last_optim < (1 - 1e-3), last_optim > 1e-3)

	c = np.logical_or(a, b)

	return np.logical_and(c, pupil_subsampled > 0)

def optimize_aplc(pupil, focal_plane_mask, lyot_stops, dark_zone_mask, wavelengths, contrast, num_scalings=1,
	force_no_x_symmetry=False, force_no_y_symmetry=False, do_apodizer_throughput_maximization=False):
	"""Optimize an APLC with a (optional) iterative algorithm taking into account x and/or y mirror symemtries.

	Parameters
	----------
	pupil : Field
		The telescope pupil
	focal_plane_mask : Field
		The focal plane mask of the APLC. The grid is assumed to be in lambda_0/D.
	lyot_stops : list of Fields
		A list of the Lyot stops used in the optimization problem.
	dark_zone_mask : Field
		A binary field indicating which pixels belong to the dark zone.
	wavelengths : array_like
		An array of wavelengths as fractions of lambda_0.
	contrast : scalar
		The contrast that needs to be achieved in the dark zone.
	num_scalings : int
		The number of scalings that need to be performed in the adaptive algorithm. A value of 1 effectively turns
		the adaptive algorithm off.
	force_no_x_symmetry : boolean
		Force the algorithm to ignore any x mirror symmetry that might exist in the problem.
	force_no_y_symmetry : boolean
		Force the algorithm to ignore any y mirror symmetry that might exist in the problem.

	Returns
	-------
	Field
		The optimized apodizer for the APLC. This has not been multiplied by the telescope pupil.
	"""
	pupil_grid = pupil.grid
	focal_grid = dark_zone_mask.grid

	aplc = LyotCoronagraph(pupil_grid, focal_plane_mask)

	focal_grid_0 = CartesianGrid(UnstructuredCoords([np.array([0.0]), np.array([0.0])]), np.array([1.0]))
	prop_0 = FraunhoferPropagator(pupil_grid, focal_grid_0)

	prior = None
	subsamplings = 2**np.arange(num_scalings)[::-1]

	# Determine pupil symmetries
	x_symm_pupil = np.allclose(pupil.shaped[:,::-1], pupil.shaped)
	y_symm_pupil = np.allclose(pupil.shaped[::-1,:], pupil.shaped)

	print('Telescope pupil:')
	print('   Mirror symmetry in x: %s' % ('yes' if x_symm_pupil else 'no'))
	print('   Mirror symmetry in y: %s' % ('yes' if y_symm_pupil else 'no'))
	print('')

	# Determine lyot stop symmetries
	x_symm_lyot_stops = [np.allclose(lyot_stop.shaped[:,::-1], lyot_stop.shaped) for lyot_stop in lyot_stops]
	y_symm_lyot_stops = [np.allclose(lyot_stop.shaped[::-1,:], lyot_stop.shaped) for lyot_stop in lyot_stops]

	lyot_stop_duplication = np.zeros(len(lyot_stops), dtype='bool')
	lyot_stop_duplication_reason = [[] for i in range(len(lyot_stops))]

	x_symm = x_symm_pupil
	y_symm = y_symm_pupil

	# X mirror symmetry for Lyot stops
	for i, a in enumerate(lyot_stops):
		print('Lyot stop #%d:' % i)

		if lyot_stop_duplication[i]:
			print('   Will be ignored due to symmetries with Lyot stops #' + str(lyot_stop_duplication_reason[i]))
			continue

		print('   Mirror symmetry in x: %s' % ('yes' if x_symm_lyot_stops[i] else 'no'))

		if x_symm_pupil and not x_symm_lyot_stops[i]:
			print('   Searching for mirror symmetric Lyot stops in x...')
			for j, b in enumerate(lyot_stops):
				if j <= i:
					continue

				if np.allclose(a.shaped[:,::-1], b.shaped):
					print('      Found Lyot stop #%d to fit.' % j)
					lyot_stop_duplication[j] = True
					lyot_stop_duplication_reason[j].append(i)
					x_symm = True
					break
			else:
				print('      No Lyot stop found with this symmetry. This breaks the mirror symmetry in x of the optimization.')
				x_symm = False

	# Y mirror symmetry for Lyot stops
	for i, a in enumerate(lyot_stops):
		print('Lyot stop #%d:' % i)

		if lyot_stop_duplication[i]:
			print('   Will be ignored due to symmetries with Lyot stops #' + str(lyot_stop_duplication_reason[i]))
			continue

		print('   Mirror symmetry in y: %s' % ('yes' if y_symm_lyot_stops[i] else 'no'))

		if y_symm_pupil and not y_symm_lyot_stops[i]:
			print('   Searching for mirror symmetric Lyot stops in y...')
			for j, b in enumerate(lyot_stops):
				if j <= i:
					continue

				if np.allclose(a.shaped[::-1,:], b.shaped):
					print('      Found Lyot stop #%d to fit.' % j)
					lyot_stop_duplication[j] = True
					lyot_stop_duplication_reason[j].append(i)
					y_symm = True
					break
			else:
				print('      No Lyot stop found with this symmetry. This breaks the mirror symmetry in y of the optimization.')
				y_symm = False
	print('')

	print('Complete APLC:')
	print('   Mirror symmetry in x: %s' % ('yes' if x_symm else 'no'))
	print('   Mirror symmetry in y: %s' % ('yes' if y_symm else 'no'))

	if force_no_x_symmetry:
		print('   The user forced me to ignore mirror-symmetries in x.')
		x_symm = False
	if force_no_y_symmetry:
		print('   The user forced me to ignore mirror-symmetries in y.')
		y_symm = False
	print('')

	# Find number of constraints per focal-plane point
	num_constraints_per_focal_point = []
	for i, lyot_stop in enumerate(lyot_stops):
		if lyot_stop_duplication[i]:
			# Lyot stop already taken into account due to symmetries
			num_constraints_per_focal_point.append(0)
		elif (x_symm and x_symm_lyot_stops[i]) and (y_symm and y_symm_lyot_stops[i]):
			# Only constrain real part
			num_constraints_per_focal_point.append(1)
		else:
			# Constrain both real and imag part
			num_constraints_per_focal_point.append(2)

	num_constraints_per_focal_point = np.array(num_constraints_per_focal_point)

	dark_zone_masks = []
	dark_zone_masks_full = []
	propagators = []
	num_focal_points = []
	for i, lyot_stop in enumerate(lyot_stops):
		if lyot_stop_duplication[i]:
			# Lyot stop was removed due to symmetries
			dark_zone_masks.append(None)
			dark_zone_masks_full.append(np.zeros(focal_grid.size, dtype='bool'))
			propagators.append(None)
			num_focal_points.append(0)
			continue

		# Separated coords for sub focal grid
		x, y = focal_grid.separated_coords

		# Hermitian symmetry (all planes are real)
		m = focal_grid.x > 0
		x = x[x > 0]

		# Only optimize quarter of roi is mirror symmetric in one or two axes
		if (x_symm and x_symm_lyot_stops[i]) or (y_symm and y_symm_lyot_stops[i]):
			m *= focal_grid.y > 0
			y = y[y > 0]

		# Make grid with subset of focal grid
		focal_grid_sub = CartesianGrid(SeparatedCoords((x, y)))
		#focal_grid_sub = focal_grid

		# Make propagator for this Lyot stop
		propagators.append(FraunhoferPropagator(pupil_grid, focal_grid_sub))

		# Recalculate dark zone mask for the sub focal grid
		dark_zone_masks.append(Field(dark_zone_mask[m > 0], focal_grid_sub).astype('bool'))
		dark_zone_masks_full.append((dark_zone_mask * m).astype('bool'))
		#dark_zone_masks.append((dark_zone_mask * m).astype('bool'))

		# Calculating number of focal points
		num_focal_points.append(int(np.sum(dark_zone_masks[-1])))

	num_focal_points = np.array(num_focal_points)

	# Calculate number of constraints per wavelength
	m = int(np.sum(num_constraints_per_focal_point * num_focal_points))
	cum_mms = np.concatenate(([0], np.cumsum(num_constraints_per_focal_point * num_focal_points))).astype('int')

	# Iterate from lowest to highest resolution
	for subsampling in subsamplings:
		# Calculated subsampled pupil and lyot stops
		pupil_subsampled = subsample_field(pupil, subsampling)
		lyot_stops_subsampled = [subsample_field(lyot_stop, subsampling) for lyot_stop in lyot_stops]
		pupil_grid_subsampled = pupil_subsampled.grid

		# Calculate which pixels belong to which superpixel
		inds = np.arange(pupil_grid.size).reshape((pupil_grid.shape[1]//subsampling, subsampling, pupil_grid.shape[0]//subsampling, subsampling))
		inds = np.swapaxes(inds, 1, 2).reshape((pupil_grid_subsampled.shape[0], pupil_grid_subsampled.shape[1], -1))#.reshape((pupil_grid.size//(subsampling**2), -1))

		# Apply x,y-mirror-symmetries
		symmetry_mask = Field(np.ones(pupil_grid_subsampled.size), pupil_grid_subsampled)
		if x_symm:
			inds = np.concatenate((inds, inds[:,::-1,:]), axis=2)
			symmetry_mask *= pupil_grid_subsampled.x < 0
		if y_symm:
			inds = np.concatenate((inds, inds[::-1,:,:]), axis=2)
			symmetry_mask *= pupil_grid_subsampled.y < 0

		symmetry_mask = symmetry_mask.astype('bool')
		inds = inds.reshape((pupil_grid_subsampled.size, -1))
		#inds = [inds[i,:] for i in range(pupil_grid_subsampled.size) if mask[i]]

		# Upscale last optim to current resolution
		blind = prior is None
		if blind:
			# No prior information; assume totally dark apodizer
			last_optim = Field(np.zeros(pupil_grid_subsampled.size), pupil_grid_subsampled)
			prior = Field(np.zeros(pupil_grid.size), pupil_grid)
		else:
			# Upscale prior information by factor 2
			last_optim = subsample_field(prior, subsampling)

		# Write prior to file
		write_fits(prior * pupil, 'display/prior%d.fits' % subsampling)
		write_fits(last_optim * pupil_subsampled, 'display/last_optim%d.fits' % subsampling)

		# Get pixels to optimize
		optimize_mask = np.logical_and(calculate_pixels_to_optimize(last_optim, pupil_subsampled), symmetry_mask)
		if blind:
			optimize_mask[:] = np.logical_and(pupil_subsampled > 0, symmetry_mask)
		n = int(np.sum(optimize_mask * symmetry_mask))

		# Write optimize mask to file
		write_fits(optimize_mask.astype('int'), 'display/optimize_mask%d.fits' % subsampling)

		print('Starting optimization at scale %d with %d variables and %d constraints.' % (subsampling, n, m*len(wavelengths)))
		print('Creating model...')

		# Create Gurobi model
		if not run_without_gurobipy:
			model = gp.Model('lp')
			model.Params.Threads = 0
			model.Params.Crossover = 0
			model.Params.Method = 2
			x_vars = model.addVars(n, lb=0, ub=1)

		print('Calculating and adding constraints...')

		# Create problem matrix for one wavelength but for all Lyot stops
		M = np.empty((m, n))

		# Add constraints for each wavelength
		for wl_i, wavelength in enumerate(wavelengths):
			j = 0
			x0 = Field(np.zeros(pupil_grid.size, dtype='complex'), pupil_grid)
			x = Field(np.zeros(pupil_grid.size, dtype='complex'), pupil_grid)

			# Calculate norm electric field for each Lyot stop
			norms = []
			for lyot_stop in lyot_stops:
				norms.append(prop_0(Wavefront(pupil * lyot_stop, wavelength)).electric_field[0])

			for ind, amp, to_optimize, masked_by_symmetry in zip(inds, last_optim, optimize_mask, symmetry_mask):
				if not to_optimize:
					# Do not optimize this pixel
					# Add to accumulator pupil-plane wavefront
					if masked_by_symmetry:
						x0[ind] += pupil[ind] * amp
				else:
					x[:] = 0
					x[ind] = pupil[ind]

					# Calculate field before the Lyot stop
					lyot = aplc(Wavefront(x, wavelength))

					k = 0
					for i, lyot_stop in enumerate(lyot_stops):
						if num_constraints_per_focal_point[i] == 0:
							continue

						# Apply the Lyot stop and get focal-plane electric field
						lyot_copy = lyot.copy()
						lyot_copy.electric_field *= lyot_stop
						E = propagators[i](lyot_copy).electric_field[dark_zone_masks[i]]
						E /= norms[i]

						# Add only imaginary or both imaginary and real constraints depending on symmetry
						if num_constraints_per_focal_point[i] == 1:
							M[cum_mms[i]:cum_mms[i+1], j] = E.real
						if num_constraints_per_focal_point[i] == 2:
							M[cum_mms[i]:cum_mms[i] + num_focal_points[i], j] = E.real + E.imag
							M[cum_mms[i] + num_focal_points[i]:cum_mms[i+1], j] = E.real - E.imag

						k += num_constraints_per_focal_point[i]
					j += 1

					if j % 1000 == 0:
						print('Wavelength %d/%d; Variable %d/%d' % (wl_i + 1, len(wavelengths), j, n))

			# Display x0
			imshow_field(x0.real)
			plt.colorbar()
			plt.savefig('display/base_aperture%d.pdf' % subsampling)
			plt.clf()

			# Calculate base electric field
			base_electric_field = []
			for i, lyot_stop in enumerate(lyot_stops):
				if num_constraints_per_focal_point[i] == 0:
					continue

				wf = aplc(Wavefront(x0, wavelength))
				wf.electric_field *= lyot_stop
				E = propagators[i](wf).electric_field[dark_zone_masks[i]]
				E /= norms[i]

				if num_constraints_per_focal_point[i] == 1:
					base_electric_field.append(E.real)
				if num_constraints_per_focal_point[i] == 2:
					base_electric_field.append(E.real + E.imag)
					base_electric_field.append(E.real - E.imag)
			base_electric_field = np.concatenate(base_electric_field)

			# Calculate contrast requirement
			contrast_requirement = []
			for p, q, r in zip(num_focal_points, num_constraints_per_focal_point, dark_zone_masks_full):
				temp = np.repeat((np.ones(focal_grid.size) * np.sqrt(contrast))[r], q)
				contrast_requirement.append(temp)
			contrast_requirement = np.concatenate(contrast_requirement)
			#contrast_requirement = np.concatenate([np.repeat((np.ones(p) * np.sqrt(contrast))[dark_zone_mask], q) for p, q in zip(num_focal_points, num_constraints_per_focal_point)])

			# Add constraints
			for ee, e0, c0 in zip(M, base_electric_field, contrast_requirement):
				e = gp.LinExpr(ee, x_vars.values())
				model.addConstr(e <= (c0 - e0))
				model.addConstr(e >= (-c0 - e0))

		del M

		# Use central Lyot stop for throughput metric (assume that this is the unshifted Lyot stop)
		if do_apodizer_throughput_maximization:
			M_max = pupil_subsampled[optimize_mask]
		else:
			M_max = (pupil_subsampled * lyot_stops_subsampled[0])[optimize_mask]
		obj = gp.LinExpr(M_max, x_vars.values())
		model.setObjective(obj, gp.GRB.MAXIMIZE)

		# Optimize model
		print('Start optimization...')
		model.optimize()
		print('Optimization finished!')

		# Extract solution from Gurobi
		solution = np.array([x_vars[i].x for i in range(n)])

		# Integrate solution into upsampled old solution
		sol = prior
		j = 0
		for ind, to_optimize in zip(inds, optimize_mask):
			if to_optimize:
				sol[ind] = solution[j]
				j += 1
		sol = Field(sol, pupil_grid)
		prior = sol

		# Write result to display
		write_fits(prior * (pupil > 0), 'display/result%d.fits' % subsampling)

	return prior

if __name__ == '__main__':
	contrast = 1e-8
	num_pix = 1944
	q_sci = 2.5 # px / (lambda_0/D)
	iwa = 3.75 # lambda_0/D
	owa = 15 # lambda_0/D
	n_foc = 80 # px diameter
	foc_inner = 8.543 # lambda_0/D diameter
	spectral_bandwidth = 0.1 # fractional
	num_wavelengths = 4
	num_lyot_stops = 9
	lyot_stop_shift = 6 # px
	tau = 0.55 # expected planet peak intensity (relative to without focal plane mask)
	gray_focal_plane_mask_type = True
	gray_pupil = False
	gray_lyot_stop = True
	num_scalings = 3

	# Build filename
	# fname = 'apodizers/HiCAT-N%04d_NFOC%04d_DZ%04d_%04d_C%03d_BW%02d_NLAM%02d_SHIFT%02d_%02dLS_ADAP%d' % (num_pix, n_foc, iwa*100, owa*100, -10*np.log10(contrast), spectral_bandwidth*100, num_wavelengths, lyot_stop_shift*10, num_lyot_stops, num_scalings)
	#fname = 'apodizers/LUVOIR_IWA=3.0_OWA=12.0_BW=0.18_nlam=08'
	fname = 'apodizers/HICAT_1944_LS9_6pix_telserv3'
	print('Apodizer will be saved to:')
	print('   ' + fname + '.fits')
	print('')

	# Read in pupil and Lyot stop generated by ehpor script (HiCATApertureGenerationPython.ipynb)
	#fname_pupil = 'masks/ehpor_apodizer_mask_%d_%s.fits' % (num_pix, 'gy' if gray_pupil else 'bw')
	#fname_lyot_stop = 'masks/ehpor_lyot_mask_%d_%s.fits' % (num_pix, 'gy' if gray_lyot_stop else 'bw')

	# Read in directly for LUVOIR
	#fname_pupil = 'masks/LUVOIR/TelAp_full_luvoirss100cobs1gap2_N0250.fits'
	#fname_lyot_stop = 'masks/LUVOIR/LS_full_luvoir_ann19D94_clear_N0250.fits'

	fname_pupil = 'masks/HiCAT/hicat_apodizer_mask_1944_bw.fits' # for HiCAT we need a b/w aperture support becasue the apodizer defines the pupil outline as well
	fname_lyot_stop = 'masks/HiCAT/hicat_lyot_mask_1944_gy_0.fits' # this one is really gray

	pupil_grid = make_uniform_grid((num_pix, num_pix), 1)

	pupil = read_fits(fname_pupil)
	pupil = Field(pupil.ravel(), pupil_grid)

	lyot_stop = read_fits(fname_lyot_stop)
	lyot_stop = Field(lyot_stop.ravel(), pupil_grid)

	# Build Lyot stop configuration
	if num_lyot_stops in [1, 5, 9]:
		lyot_stops = [lyot_stop]
	else:
		lyot_stops = []

	if num_lyot_stops in [4, 5, 9]:
		lyot_stop_pos_x = np.roll(lyot_stop.shaped, lyot_stop_shift, 1).ravel()
		lyot_stop_neg_x = np.roll(lyot_stop.shaped, -lyot_stop_shift, 1).ravel()
		lyot_stop_pos_y = np.roll(lyot_stop.shaped, lyot_stop_shift, 0).ravel()
		lyot_stop_neg_y = np.roll(lyot_stop.shaped, -lyot_stop_shift, 0).ravel()

		lyot_stops.extend([lyot_stop_pos_x, lyot_stop_neg_x, lyot_stop_pos_y, lyot_stop_neg_y])

	if num_lyot_stops in [9]:
		lyot_stop_pos_x_pos_y = np.roll(np.roll(lyot_stop.shaped, lyot_stop_shift, 1), lyot_stop_shift, 0).ravel()
		lyot_stop_pos_x_neg_y = np.roll(np.roll(lyot_stop.shaped, lyot_stop_shift, 1), -lyot_stop_shift, 0).ravel()
		lyot_stop_neg_x_pos_y = np.roll(np.roll(lyot_stop.shaped, -lyot_stop_shift, 1), lyot_stop_shift, 0).ravel()
		lyot_stop_neg_x_neg_y = np.roll(np.roll(lyot_stop.shaped, -lyot_stop_shift, 1), -lyot_stop_shift, 0).ravel()

		lyot_stops.extend([lyot_stop_pos_x_pos_y, lyot_stop_pos_x_neg_y, lyot_stop_neg_x_pos_y, lyot_stop_neg_x_neg_y])

	# Build science focal grid
	n_sci = int((np.ceil(owa) + 1) * q_sci) * 2
	x_sci = (np.arange(n_sci) + 0.5 - n_sci / 2) / q_sci
	focal_grid = CartesianGrid(SeparatedCoords((x_sci, x_sci)))

	dark_zone_mask = circular_aperture(owa * 2)(focal_grid) - circular_aperture(iwa * 2)(focal_grid)

	# Build focal plane mask
	q_foc = n_foc / foc_inner
	x_foc = (np.arange(n_foc) + 0.5 - n_foc / 2) / q_foc
	focal_mask_grid = CartesianGrid(RegularCoords(1.0 / q_foc, [n_foc, n_foc], x_foc.min()))

	if gray_focal_plane_mask_type:
		focal_plane_mask = 1 - evaluate_supersampled(circular_aperture(foc_inner), focal_mask_grid, 8)
	else:
		focal_plane_mask = 1 - circular_aperture(foc_inner)(focal_mask_grid)

	if num_wavelengths == 1:
		wavelengths = [1]
	else:
		wavelengths = np.linspace(-spectral_bandwidth / 2, spectral_bandwidth / 2, num_wavelengths) + 1

	# Optimize and write to file
	apodizer = optimize_aplc(pupil, focal_plane_mask, lyot_stops, dark_zone_mask, wavelengths, contrast * tau, num_scalings=num_scalings, force_no_x_symmetry=False, force_no_y_symmetry=False, do_apodizer_throughput_maximization=True)
	write_fits(apodizer * (pupil > 0), fname + '.fits')
