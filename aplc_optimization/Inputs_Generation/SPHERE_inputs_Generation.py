from pathlib import Path

import astropy.units as u
import numpy as np
import poppy
from astropy.io import fits

_default_pupil_array_size = 8 * u.m


def SPHERE_inputs_gen(input_files_dict):
    """Generate the GPI Primary and Lyot stop(s) for the APLC coronagraph and write to file.
        
    Parameters
    ----------
    input_files_dict: dict
        A dictionary of input mask parameters.
        
    Returns
    -------
    pup_filename: str
        The name of the generated telescope aperture FITS file.
    ls_filename: list
        The name(s) of the generated Lyot stop FITS file(s).
    """

    filepath = input_files_dict['directory']
    N = input_files_dict['N']
    #lyot_mask = input_files_dict['lyot_stop']['lyot_mask']
    #ls_tabs = input_files_dict['lyot_stop']['ls_tabs']
    #ls_spid = input_files_dict['lyot_stop']['ls_spid']
    ls_sym = input_files_dict['lyot_stop']['ls_sym']
    #ap_spid = input_files_dict['aperture']['ap_spid']
    ap_sym = input_files_dict['aperture']['ap_sym']
    pupil_name = input_files_dict['aperture']['pupil_name']

    if ap_sym:
        pup_filename = filepath + f'pupil={pupil_name}_nPup={N}.fits'
    else:
        raise TypeError(f'pupil is expected to be symmetric')

    if ls_sym:
        ls_filename = filepath + f'pupil={pupil_name}_nPup={N}.fits'
    else:
        ls_filename = filepath + f'sphere_stop_ST_ALC2_nPup{N:04d}.fits'

    config = Path('masks/' + pup_filename)

    # Check if primary file already exists, otherwise create GPI primary file
    if config.is_file():
        print('{0:s} exists'.format('masks/' + pup_filename))
    else:
        raise TypeError(f'{pup_filename} not found')

    config = Path('masks/' + ls_filename)

    # Check if lyot stop file already exists, otherwise create GPI Lyot mask file
    if config.is_file():
        print('{0:s} exists'.format('masks/' + ls_filename))
    else:
        raise TypeError(f'{ls_filename} not found')
    
    return pup_filename, ls_filename
