from survey import DesignParameterSurvey
from por_aplc import PorAPLC

varying_parameters = {'pupil': {'filename': 'ehpor_hicat_apodizer_mask_256_gy.fits'}, 'lyot_stop': {'filename': 'ehpor_hicat_lyot_mask_256_gy_2.fits'}, 'image': {'owa': 15}}

survey = DesignParameterSurvey(PorAPLC, varying_parameters, 'magnfication_survey1/', 'masks/')
survey.describe()

survey.write_drivers(True)
survey.run_optimizations(True)
survey.run_analyses(True)

varying_parameters = {'pupil': {'filename': 'ehpor_hicat_apodizer_mask_256_gy.fits'}, 'lyot_stop': {'filename': 'ehpor_hicat_lyot_mask_256_gy_{:d}.fits', 'num_lyot_stops': 5}, 'image': {'owa': 15}}

survey = DesignParameterSurvey(PorAPLC, varying_parameters, 'magnfication_survey5/', 'masks/')
survey.describe()

survey.write_drivers(True)
survey.run_optimizations(True)
survey.run_analyses(True)