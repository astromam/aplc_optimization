from pathlib import Path

import astropy.units as u
import numpy as np
import poppy
from astropy.io import fits

_default_pupil_array_size = 8 * u.m


def SPHERE_inputs_gen(input_files_dict):
    """Generate the SPHERE Primary and Lyot stop(s) for the APLC coronagraph and write to file.
        
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
    ls_multi = input_files_dict['lyot_stop']['ls_multi']
    ap_sym = input_files_dict['aperture']['ap_sym']
    pupil_name = input_files_dict['aperture']['pupil_name']

    if ap_sym:
        pup_filename = filepath + f'pupil={pupil_name}_nPup={N}.fits'
    else:
        raise TypeError(f'pupil is expected to be symmetric')

    config = Path('masks/' + pup_filename)
    # Check if primary file already exists, otherwise create GPI primary file
    if config.is_file():
        print('{0:s} exists'.format('masks/' + pup_filename))
    else:
        raise TypeError(f'{pup_filename} not found')

    ls_filenames = []
    ls_filename = filepath + f'sphere_stop_ST_ALC2_nPup{N:04d}.fits'
    # Check if lyot stop file already exists, otherwise create GPI Lyot mask file
    config = Path('masks/' + ls_filename)
    if config.is_file():
        print('{0:s} exists'.format('masks/' + ls_filename))
    else:
        raise TypeError(f'{ls_filename} not found')
    ls_filenames.append(ls_filename)

    if ls_multi:

        ls_filename_lr = filepath + f'sphere_stop_ST_ALC2_nPup{N:04d}_lr.fits'
        # Check if lyot stop file already exists, otherwise create GPI Lyot mask file
        config = Path('masks/' + ls_filename_lr)
        if config.is_file():
            print('{0:s} exists'.format('masks/' + ls_filename))
        else:
            raise TypeError(f'{ls_filename} not found')
        ls_filenames.append(ls_filename_lr)

        ls_filename_ud = filepath + f'sphere_stop_ST_ALC2_nPup{N:04d}_ud.fits'
        # Check if lyot stop file already exists, otherwise create GPI Lyot mask file
        config = Path('masks/' + ls_filename_ud)
        if config.is_file():
            print('{0:s} exists'.format('masks/' + ls_filename))
        else:
            raise TypeError(f'{ls_filename} not found')
        ls_filenames.append(ls_filename_ud)

        ls_filename_lrud = filepath + f'sphere_stop_ST_ALC2_nPup{N:04d}_lrud.fits'
        # Check if lyot stop file already exists, otherwise create GPI Lyot mask file
        config = Path('masks/' + ls_filename_lrud)
        if config.is_file():
            print('{0:s} exists'.format('masks/' + ls_filename))
        else:
            raise TypeError(f'{ls_filename} not found')
        ls_filenames.append(ls_filename_lrud) 

    # remove duplicates
    s = set(ls_filenames)
    ls_filenames = list(s)
    
    return pup_filename, ls_filenames
