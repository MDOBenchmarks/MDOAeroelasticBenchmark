
Simple Transonic Wing (STW)
===========================

This section describes the Simple Transonic Wing (STW) benchmark model and optimization problems.
These were first proposed in our paper at the 2024 AIAA SciTech Forum :cite:t:`AGray2024a`.

This section contains the model and problem description sections of that paper, with some small changes.
It should be considered the up to date reference for those planning to take part in the special session.

.. toctree::
   :maxdepth: 2

   model
   opt_problem
   required_results
   stw_papers

.. _stw_files:

STW Files
---------

A collection of files to help participants get started with the simple transonic wing benchmark problems can be found `here <https://github.com/MDOBenchmarks/MDOAeroelasticBenchmark/tree/main/STW-Files>`_.
These files include:

* OML and wingbox CAD files
* Aerodynamic and structural meshes
* FFD control volumes
* Geometry and aircraft specifications
* Python code for performing the necessary aircraft performance calculations

Reference results
-----------------

Reference results for the STW benchmark problems, and instructions for submitting your own results, can be found at X...

You can also find a list of papers that contain results using the STW on the :ref:`stw-papers` page.

Acknowledgements
----------------

We would like to thank Gaetan Kenway, who originally created the simple transonic wing geometry, and Anil Yildirim for creating the supplied CFD meshes.


Bibliography
------------

.. bibliography:: stw_refs.bib
   :filter: docname in docnames
