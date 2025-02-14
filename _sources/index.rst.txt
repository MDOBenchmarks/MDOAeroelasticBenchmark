
Aeroelastic Optimization Benchmark
==================================

This website describes the benchmark model and optimization problems to be used by working group 1 for the special session on High-Fidelity Aeroelastic Design Optimization Applications and Benchmarks at the 2025 AIAA SciTech Forum.
These were first proposed in our paper at the 2024 AIAA SciTech Forum :cite:t:`AGray2024a`.

This website contains the model and problem description sections of that paper, with some small changes.
It should be considered the up to date reference for those planning to take part in the special session.

Table of contents
*****************

.. toctree::
   :maxdepth: 2

   model.rst
   opt_problem.rst
   required_results.rst

Simple Transonic Wing Files
---------------------------

A collection of files to help participants get started with the simple transonic wing benchmark problems can be found `here <https://github.com/MDOBenchmarks/MDOAeroelasticBenchmark/tree/main/STW-Files>`_.
These files include:
- OML and wingbox CAD files
- Aerodynamic and structural meshes
- FFD control volumes
- Geometry and aircraft specifications
- An OpenMDAO model for performing the necessary aircraft performance calculations

Acknowledgements
----------------

We would like to thank Gaetan Kenway, who originally created the simple transonic wing geometry, and Anil Yildirim for creating the supplied CFD meshes.

Bibliography
------------

.. bibliography:: refs.bib
   :cited:
