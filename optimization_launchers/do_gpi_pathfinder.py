import os
os.chdir('..')

from aplc_optimization.survey import DesignParameterSurvey
from aplc_optimization.aplc import APLC
from astropy.io import fits
from aplc_optimization.Inputs_Generation.GPI_Inputs_Generation import GPI_inputs_gen

'''
DO NOT RUN THIS SCRIPT - It is the launcher template. 
Default parameters for 1000 pix BW10 small design

Workflow: 
- Make a copy
- rename the copy to designate survey you are running and the machine name you will be 
  running it on (do_luvoir_BW10_small_telserv3.py , for example, designates the BW10 small 
  design run on telserv3)

- set survey_name the same as survey name you use in the launcher file name
- Set the machine to be the name of the machine you're running on (need to write this to 
  grab machine name automatically)

- run the launcher
- after survey is done, move the launcher script into the survey directory
'''

nArray = 1168  # number of pixels in input and final arrays - with 10µm pixels (so we have 11.68mm instead of 11.67mm diameter)
instrument = "gpi"  # instrument name
survey_name = "pathfinder_new_robust"  # survey name
machine = "telserv3"  # machine the survey is run on.


ap_spid = True # the secondary supports are masked out in the Lyot planes regardless
ap_sym = True # symmetric supports
satspots = False # whether to include satellite spots grid
ls_tabs = False # whether to block out the bad actuators with tabs in the Lyot masks
lyot_mask = '080m12_03' # name of Lyot mask. - '080m12_03' because it has the thinnest spiders
                        # available lyot masks are: '080m12_02', '080m12_03', '080m12_04', '080m12_04_c',
                        # '080m12_06', '080m12_06_03', '080m12_07', '080m12_10', 'Open' and 'Blank'.
ls_spid = True


input_files_dict = {'directory': 'GPI/', 'N': nArray,
                    'aperture': {'ap_spid': True, 'ap_sym': True},
                    'lyot_stop': {'lyot_mask':lyot_mask, 'ls_tabs': ls_tabs, 'ls_spid': ls_spid}}

# GENERATE INPUT FILES
pup_filename, ls_filename = GPI_inputs_gen(input_files_dict)
#pup_filename = 'GPI/Primary_GPI_grey_oversamp04_symmetric_N1168.fits'
#ls_filename = 'GPI/LS_GPI_080m12_03_grey_oversamp04_notabs_N1168.fits'

# Focal plane mask parameters
nFPM = 80 # number of pixels across the focal plane mask
FPM_name = 'K1' # name of FPM. Available FPMs are: 'Y', 'J', 'H' or 'K1'
FPM_radius = 3.476449131 # lambda_0/D: focal plane mask radius

# Optimization parameters
contrast = 8 # contrast goal in the dark zone, where 10 ^-{contrast}
IWA = 3 # lamda_0/D: dark zone inner radius (rho_i) - minimum distance at which the transmission of an off-axis companion is significantly high.
OWA = 22 # lambda_0/D: dark zone outer radius (rho_o)
spectral_bandwidth = 0.2 # fractional: spectral bandwidth over which we want to optimize
nLams = 3 # number of wavelengths spanning the design bandpass
res = 2

# method parameters
starting_scale = 4 # number of pixels per unit cell for the initial solution.
ending_scale = 1

alignment_tolerance = 1 # Lyot stop pixel shifts: tolerance to Lyot stop misalignments
num_lyot_stops = 9

survey_parameters = {'instrument': {'inst_name': instrument.upper()}, 'pupil': {'N': nArray, 'filename': pup_filename}, 'lyot_stop': {'filename': ls_filename, 'ls_tabs': True, 'alignment_tolerance': alignment_tolerance, 'num_lyot_stops': num_lyot_stops}, 'focal_plane_mask': {'FPM_name': FPM_name, 'radius': FPM_radius, 'num_pix': nArray}, 'image': {'contrast': contrast,'iwa': IWA,'owa': OWA,'bandwidth': spectral_bandwidth,'num_wavelengths':nLams, 'resolution': res}, 'method': {'starting_scale': starting_scale, 'ending_scale': ending_scale}}


# RUN DESIGN SURVEY
gpi = DesignParameterSurvey(APLC, survey_parameters, 'surveys/{}_{}_N{:04d}_{}/'.format(instrument,survey_name,nArray,machine), 'masks/')
gpi.describe()

gpi.write_drivers(True)
gpi.run_optimizations(True)
gpi.run_analyses(True)
