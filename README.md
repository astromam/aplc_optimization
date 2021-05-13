# aplc-optimization: Apodized Pupil Lyot Coronagraph (APLC) design optimization toolkit

`aplc-optimization` is an object-orientated software toolkit to simplify the organization,
execution and evaluation of large APLC design surveys.

Documentation can be found online at [https://aplc-optimization.readthedocs.io/](https://aplc-optimization.readthedocs.io/en/latest/)

## Requirements & Installation

#### Prerequesits
- Gurobi solver for Python. For licensing and installation instructions see [gurobipy](https://www.gurobi.com/documentation/9.1/quickstart_mac/cs_grbpy_the_gurobi_python.html), as well as the `aplc-optimization` [documentation](https://aplc-optimization.readthedocs.io/en/latest/installing.html#installing-the-optimization-solver-gurobi).

#### Installing
`aplc-optmization` has the following strong depenecies:
 - numpy, scipy, matplotlib etc
 - astropy
 - hcipy
 - gurobipy
 - asdf
 - imageioad

For installation instructions, see the online [documentation](https://aplc-optimization.readthedocs.io/en/latest/installing.html) or [docs/installation.md](https://github.com/spacetelescope/aplc-optimization/blob/develop/docs/installing.md) in this source distribution.

## Contributing Code, Documentation, or Feedback

Thank you for considering contributing to `aplc-optimization`. Please read [CONTRIBUTING.md](https://github.com/spacetelescope/aplc-optimization/blob/develop/docs/CONTRIBUTING.md) for details on the process for submitting contributions and feedback.

### Authors

`aplc-optimization` has been developed by Emeil Por, Katherine St Laurent, Remi Soummer, Mamadou N'Daiye and Remi Flamary, with contributions from Bryony Nickson, Kelsey Glazer, Jamie Noss and Marshall Perrin.

### Acknowledgements

- The [Space Telescope Science Institute](stsci.edu) collaborators, in particular, the Segmented Coronagraph Design and Analysis (SCDA) team.
- The `aplc-optimization` package was created in support of the [Segmented Coronagraph Design and Analysis (SCDA) study](https://exoplanets.nasa.gov/exep/technology/SCDA/), funded by NASA's Exoplanet Exploration Program (ExEP). The goal of this study is to develop viable coronagraph instrument concepts for a LUVOIR-type mission. The apodized pupil Lyot coronagraph (APLC) is one of several coronagraph design families that the SCDA study is assessing.

