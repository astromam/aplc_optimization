'''
DO NOT RUN THIS SCRIPT - this is the launcher template for GPI design surveys.

Workflow:
- Make a copy of this script.
- rename the copy under the following naming schema: 'do_gpi_<survey_name>_<machine>.py', designating the survey you
  are running and the name of the machine you will be running it on.
- Define the Survey Information, Input File and Survey Design parameters, as desired.
- Run the launcher script on the designated machine.
'''

import os

os.chdir('../..')
instrument = 'sphere'  # do not edit
from aplc_optimization.survey import DesignParameterSurvey
from aplc_optimization.aplc import APLC
from aplc_optimization.Inputs_Generation.SPHERE_inputs_Generation import SPHERE_inputs_gen

"""
Survey information
------------------
survey_name: str
    The designated name of the design survey.
machine: str
    The name of the machine on which to run the design survey.
N: int
    The number of pixels in the input (Primary, LS) and final (apodizer) arrays.
"""
survey_name = "refin"
machine = "rita"
N = 800

'''
Input File Parameters
----------------------
N: int
    The number of pixels in input (primary and lyot stop) arrays.
ap_spid: bool
    Whether to include the secondary supports primary (which are masked out in the Lyot planes regardless).
ap_sym: bool
    Whether to model the primary as precisely symmetric by treating all 4 struts as the same thickness.
satspots: bool
    Whether to include satellite spots grid.
ls_tabs: bool
    Whether to block out the bad actuators with tabs in the Lyot masks.
lyot_mask: string
    The name of the Lyot mask. Available lyot masks are: '080m12_02', '080m12_03', '080m12_04', '080m12_04_c', 
    '080m12_06', '080m12_06_03', '080mgit 12_07', '080m12_10', 'Open' and 'Blank'.
ls_spid: string
    Whether to include the secondary supports in the Lyot stop mask.
'''
# Aperture parameters
ap_spid = True
ap_sym = True
pupil_name = 'vlt_btw'

# Lyot stop parameters
ls_multi = False

# INPUT FILES PARAMETER DICTIONARY
input_files_dict = {'directory': 'SPHERE/', 'N': N,
                    'aperture': {'ap_spid': True, 'ap_sym': True, 'pupil_name': pupil_name},
                    'lyot_stop': {'ls_multi': ls_multi}}

# INPUT FILE GENERATION
pup_filename, ls_filenames = SPHERE_inputs_gen(
    input_files_dict)  # generate input mask files according to the parameters defined above

'''
Survey Design Parameters
------------------------
- for multiple design parameters as a grid, input as list
- for multiple design parameters NOT as a grid, create multiple entries of below 
  (as shown in the commented block, at bottom of this script)

N: int
    The number of pixels in input (TelAP, LS) and final (apodizer) arrays.
alignment_tolerance: int
    The Lyot stop alignment tolerance in pixels. 
ls_num: int
    The number of translated Lyot stops to optimize for simultaneously. If 1, design will be non-robust.
radius: float
    The radius of the focal plane mask in lambda_0/D.
num_pix: float
    The number of pixels in the focal plane mask array.
FPM_name: str
    Name of the focal plane mask. Available FPMs are: 'Y', 'J', 'H' or 'K1'
contrast: int
    The contrast goal in the dark zone of the coronagraphic image (negative exponent of 10).
iwa: float
    The inner edge of dark zone region in coronagraphic image in lambda_0/D.
owa: float
    The outer edge of dark zone region in coronagraphic image in lambda0/D.
bandwidth: float
    The spectral bandwidth over which to optimize (fractional).
num_wavelengths: int
    The number of wavelengths spanning the design bandpass.
resolution: float
    The image resolution.
starting_scale: int
    The number of pixels per unit cell for the initial solution. This is used for the adaptive algorithm. 
    It must be a power of 2 times the `ending_scale`.
ending_scale: int
    The number of pixels per unit cell for the final solution. If this is the same as `starting_scale`,
    the adaptive algorithm is essentially turned off.
'''
# Focal plane mask parameters
nFPM = 50
radius = 2.252  # K1 FPM

# Optimization constraints
contrast = 6
IWA = 5
OWA = 20
bandwidth = 0.2
num_wavelengths = 1

# Robustness parameters
alignment_tolerance = 1
num_lyot_stops = 1

# Optimization method
starting_scale = 2
ending_scale = 1

# SURVEY PARAMETER DICTIONARY
survey_parameters = {'instrument': {'inst_name': instrument.upper()},
                     'pupil': {'N': N, 'filename': pup_filename},
                     'lyot_stop': {'filename': ls_filenames, 'alignment_tolerance': alignment_tolerance,
                                   'num_lyot_stops': num_lyot_stops},
                     'focal_plane_mask': {'radius': radius, 'num_pix': N},
                     'image': {'contrast': contrast, 'iwa': IWA, 'owa': OWA, 'bandwidth': bandwidth,
                               'num_wavelengths': num_wavelengths},
                     'method': {'starting_scale': starting_scale, 'ending_scale': ending_scale}}

# RUN DESIGN SURVEY
sphere = DesignParameterSurvey(APLC, survey_parameters,
                            'surveys/{}_{}_N{:04d}_{}/'.format(instrument, survey_name, N, machine),
                            'masks/')
sphere.describe()

sphere.write_drivers(True)
sphere.run_optimizations(True)
sphere.run_analyses(False)

