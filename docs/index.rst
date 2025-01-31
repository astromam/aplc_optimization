########################################################
aplc_optimization: an apodized pupil Lyot coronagraph design survey toolkit
########################################################

``aplc_optimization`` is a Python software toolkit for exploring apodized pupil lyot coronagraph (APLC)
solutions for abitrary telescope apertures. It's object-orientated approach simplifies
the interface for sampling large parameter spaces, and enables flexibility for implementing various mask architectures
and symmetry cases.

.. figure:: images/HiCAT_1944_LS9_6pix_analysis.png
   :align: center
   :alt: Analysis results for HiCAT

   Figure 1: Analysis results from a HiCAT design study.

The ``aplc_optimization`` toolkit was developed by the `Segmented Coronagraph Design & Analysis (SCDA) research team <https://www.stsci.edu/stsci-research/research-topics-and-programs/russell-b-makidon-optics-laboratory/meet-the-team>`_ at the Space Telescope Science Institute
(STScI) with the support of the `NASA Exoplanet Exploration Program (ExEP) <https://exoplanets.nasa.gov/exep/technology/SCDA/>`_ and is privately hosted at `github.com/spacetelescope/aplc_optimization <github.com/spacetelescope/aplc_optimization>`_.

.. _getting_started:

======================================
Getting started with aplc_optimization
======================================

.. toctree::
   :maxdepth: 1
   :caption: Contents

   introduction.rst
   installing.rst
   workflow.rst
   contributing.rst

.. toctree::
   :maxdepth: 1
   :caption: Advanced usage

.. toctree::
   :maxdepth: 1
   :caption: Detailed API Reference

   api/aplc
   api/survey
   api/optimizer
   api/HiCAT_Inputs_Generation
   api/LUVOIR_Inputs_Generation
   api/GPI_Inputs_Generation


-------------------------------

.. admonition:: How to cite ``aplc_optimization``

   In addition to this documentation, the ``aplc_optmization`` toolkit is described in the following references.  Users of ``aplc_optimization`` are encouraged to cite one of these.

    * Por et al. 2020, `"Exploiting symmetries and progressive refinement for apodized pupil Lyot coronagraph design" <https://doi.org/10.1117/12.2562571>`_, Proc. SPIE. 114433P
    * St. Laurent et al. 2018, `"Apodized pupil Lyot coronagraphs designs for future segmented space telescopes" <https://doi.org/10.1117/12.2313902>`_, Proc. SPIE. 109682W
    * Zimmerman et al. 2016, `"Lyot coronagraph design study for large, segmented space telescope apertures” <https://doi.org/10.1117/12.2233205>`_,  Proc. SPIE. 99041Y

   If there is no appropriate place in the body of text to cite these proceedings, please include something along the
   lines of the following in your acknowledgements:


      *"This research made use if aplc_optimization, an object-orientated toolkit for performing Pupil Lyot coronagraph design surveys for segmented telescope apertures."*



------------------------------------------------

Acknowledgements:
==================
- The `Space Telescope Science Institute collaborators <https://www.stsci.edu/>`_, in particular, the Segmented Coronagraph Design and Analysis (SCDA) team.
- The ``aplc_optimization`` *package was created in support of the Segmented Coronagraph Design and Analysis (SCDA) study, funded by NASA's Exoplanet Exploration Program (ExEP). The goal of this study is to develop viable coronagraph instrument concepts for a LUVOIR-type mission. The apodized pupil Lyot coronagraph (APLC) is one of several coronagraph design families that the SCDA study is assessing.

