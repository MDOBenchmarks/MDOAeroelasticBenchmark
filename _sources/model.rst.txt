Wing Model 
==========

The benchmark model is based on an OML geometry originally defined by :cite:t:`Kenway2013`, who referred to it is as the STW.
In this document we simply refer to it as `the wing` or `the benchmark model`.


Wing Geometry
-------------

The wing geometry is shown in :numref:`figWingPlanform`, :numref:`figBoundaryConditions` and :numref:`figAirfoilSection`.
It has a simple trapezoidal planform, based on the Boeing 717, with a constant, untwisted RAE2822 cross-section, shown in :numref:`figAirfoilSection`.
Note that this cross section cuts through the wing on planes normal to the global Y-axis, rather than normal the quarter-chord axis.
The cross section extends out to the nominal semispan of :math:`14\,\text{m}`, beyond which a small rounded tip cap extends a further :math:`42.5\,\text{mm}`.

The wing contains a conformal wingbox with upper and lower skins, leading and trailing edge spars, and 23 ribs.
The wingbox features a typical SOB break at a semispan of :math:`y = 1.5\,\text{m}`, inboard of which the wingbox is unswept, resembling a center-box.
Outboard of the SOB, the wingbox extends from 15 to 65% of the chord.
Four of the ribs are evenly spaced between the centerline and the SOB, the remaining ribs are evenly spaced between the SOB and the tip.
The wingbox is subject to symmetry conditions at the centerline and is fixed in the chordwise and vertical directions at the SOB as shown in :numref:`figBoundaryConditions`.

CAD files of both the wing OML and wingbox geometries are provided in the repository.


.. figure:: figures/SimpleTransonicWing/wingPlanform.png
   :name: figWingPlanform
   :alt: Wing Planform
   :align: center

   Wing Planform

.. figure:: figures/SimpleTransonicWing/BoundaryConditions.png
   :name: figBoundaryConditions
   :alt: Wing BCs
   :align: center

   Wing OML and wingbox, boundary conditions are applied to the wingbox at the side-of-body junction and symmetry plane

.. figure:: figures/SimpleTransonicWing/AirfoilSection.png
   :name: figAirfoilSection
   :alt: RAE2822 airfoil section
   :align: center

   RAE2822 airfoil section


.. \begin{figure}[ht!]
..   \centering
..   \begin{subfigure}{0.49\textwidth}
..     \centering
..     \includegraphics[width=0.99\textwidth]{SimpleTransonicWing/wingPlanform}
..     \captionsetup{width=0.9\linewidth}
..     \caption{Wing planform}
..     \label{fig:wingPlanform}
..   \end{subfigure}
..   \begin{subfigure}{0.49\textwidth}
..     \centering
..     \includegraphics[width=0.99\textwidth]{SimpleTransonicWing/BoundaryConditions}
..     \captionsetup{width=0.9\linewidth}
..     \caption{Wing OML and wingbox, boundary conditions are applied to the wingbox at the side-of-body junction and symmetry plane}
..     \label{fig:BoundaryConditions}
..   \end{subfigure}
..   \begin{subfigure}{0.8\textwidth}
..     \centering
..     \includegraphics[width=0.99\textwidth]{SimpleTransonicWing/AirfoilSection}
..     \captionsetup{width=0.9\linewidth}
..     \caption{RAE2822 airfoil section}
..     \label{fig:AirfoilSection}
..   \end{subfigure}
..   \caption{OML and wingbox geometries.}
..   \label{fig:SimpleTransonicWing}
.. \end{figure}

Aerodynamic Model 
-----------------

A family of 3 structured multiblock CFD meshes for the wing are provided in the repository, which are summarized in :numref:`tabAeroMeshes`.
The finest mesh (L1) is intended only for mesh convergence and analysis studies, the L2 mesh is intended for final optimizations, and the L3 mesh for debugging.
The coarser meshes are created by repeatedly coarsening the L0 surface mesh by a factor of 2 in each direction before extruding up to a distance of :math:`300\,\text{m}` from the wing surface.
The advantage of this approach is that it results in higher quality volume meshes than simply coarsening the L1 volume mesh.
The disadvantage is that it does not provide the parametrically-similar series of grids necessary for a mathematically rigorous convergence study :cite:p:`Vassberg2011a`.

Use of these meshes is not required.
Participants are encouraged to submit results using meshes with topologies and sizes that are suitable for their CFD codes and available computational resources.

.. \input{\tablepath/AeroMeshes.tex}

.. table:: CFD mesh information.
   :name: tabAeroMeshes

   +-----------+--------------------------+---------------------------+----------------------------------+
   | **Mesh**  | **Cells**                | **First cell height (m)** |  **Target cruise** :math:`y^{+}` |
   +===========+==========================+===========================+==================================+
   | L1        | :math:`7.8 \times 10^6`  | :math:`3 \times 10^{-6}`  | 0.125-0.25                       |
   +-----------+--------------------------+---------------------------+----------------------------------+
   | L2        | :math:`9.7 \times 10^5`  | :math:`6 \times 10^{-6}`  | 0.25-0.5                         |
   +-----------+--------------------------+---------------------------+----------------------------------+
   | L3        | :math:`1.8 \times 10^5`  | :math:`1.2 \times 10^{-5}`| 0.5-1                            |
   +-----------+--------------------------+---------------------------+----------------------------------+

.. \begin{figure}[ht!]
..   \begin{subfigure}{0.49\textwidth}
..     \centering
..     \includegraphics[width=0.99\textwidth]{AeroMeshes/L1Mesh}
..     \caption{L1, 7.8m cells}
..   \end{subfigure}
..   \begin{subfigure}{0.49\textwidth}
..     \centering
..     \includegraphics[width=0.99\textwidth]{AeroMeshes/L2Mesh}
..     \caption{L2, 1.0m cells}
..   \end{subfigure}
..   \begin{subfigure}{0.49\textwidth}
..     \centering
..     \includegraphics[width=0.99\textwidth]{AeroMeshes/L1Mesh-TipLE}
..     \caption{L1, wing-tip leading edge}
..   \end{subfigure}
..   \begin{subfigure}{0.49\textwidth}
..     \centering
..     \includegraphics[width=0.99\textwidth]{AeroMeshes/L2Mesh-TipLE}
..     \caption{L2, wing-tip leading edge}
..   \end{subfigure}
..   \begin{subfigure}{0.49\textwidth}
..     \centering
..     \includegraphics[width=0.99\textwidth]{AeroMeshes/L1Mesh-TipTE}
..     \caption{L1, wing-tip trailing edge}
..   \end{subfigure}
..   \begin{subfigure}{0.49\textwidth}
..     \centering
..     \includegraphics[width=0.99\textwidth]{AeroMeshes/L2Mesh-TipTE}
..     \caption{L2, wing-tip trailing edge}
..   \end{subfigure}
..   \caption{Structured multiblock \gls{cfd} meshes provided for the benchmark model.}
..   \label{fig:AeroMeshes}
.. \end{figure}

Structural Model
----------------

A series of shell FE meshes of the wingbox are also provided in the repository in BDF format.
These are summarized in :numref:`tabStructMeshes` and consist of 4-node quad elements.
Equivalent meshes with higher order 9 and 16-node quad elements are also available in the repository however, these element types are not widely supported by commercial FE codes.

.. \input{\tablepath/StructMeshes.tex}

.. table:: FE mesh information.
   :name: tabStructMeshes

   +-------------+----------------------------+----------------------------+----------------------------+--------------------+---------------+
   | - **Mesh**  |  **Elements between ribs** | **Elements between spars** | **Elements between skins** | **Total Elements** | **Total DOF** |
   +=============+============================+============================+============================+====================+===============+
   | L1          | 20                         | 40                         | 20                         | 71,200             | 419,778       |
   +-------------+----------------------------+----------------------------+----------------------------+--------------------+---------------+
   | L2          | 10                         | 20                         | 10                         | 17,800             | 103,158       |
   +-------------+----------------------------+----------------------------+----------------------------+--------------------+---------------+
   | L3          | 5                          | 10                         | 5                          | 4,450              | 24,948        |
   +-------------+----------------------------+----------------------------+----------------------------+--------------------+---------------+
   | L4          | 3                          | 5                          | 3                          | 1,401              | 7,536         |
   +-------------+----------------------------+----------------------------+----------------------------+--------------------+---------------+


.. figure:: figures/StructMeshes/L1StructMesh.png
   :name: figStructMesh
   :alt: Structural mesh
   :align: center

   The finest wingbox mesh contains 71,200 quadrilateral elements and 419,778 DOF.

To test the modeling capabilities relevant for analysis of modern aircraft structures, the wingbox is assumed to be made of stiffened composite panels.
The stiffeners are assumed to have a T-shaped cross section, as shown in :numref:`figCrossSection`.
The composite ply properties used throughout the wingbox are shown in :numref:`tabCompositeProperties`, taken from :cite:t:`Brooks2020a`.
Both the shell and stiffeners in every panel of the wingbox are assumed to consist of a [:math:`0^{\circ}`, :math:`-45^{\circ}`, :math:`45^{\circ}`, :math:`0-^{\circ}`] layup.
Different layups of these plies are used for different components in the wingbox based on values used by :cite:t:`Dillinger2014`.
In the upper and lower skin shells and in all stiffeners, we assume a :math:`0^{\circ}` biased layup with ply fractions of [44.41%, 22.2%, 22.2%, 11.19%], while in the spar and rib shells we use a more isotropic [10%, 35%, 35%, 20%].
In the skins, the stiffeners and :math:`0^{\circ}` plies are aligned with the trailing edge spar, in the spars and ribs they are vertically oriented.

.. figure:: figures/StiffenedShellModel/CrossSection.svg
   :name: figCrossSection
   :align: center

   Cross section of the panel

There are a wide variety of approaches to modeling stiffened shells in FE models and predicting their failure, particularly in the context of optimization.
We therefore do not believe it is practical to enforce a single approach.
However, the models used by participants should:

1. Be able to model the anisotropic composite laminate properties given above.
2. Be able to model the presence of panel stiffeners and, ideally, be able to parameterize their cross-section.
3. Use sufficient failure criteria to constrain that the structure has a safety factor of at least 1.5 to both material and buckling failure.

.. \input{\tablepath/CompositeProperties.tex}

.. table:: Composite ply properties.
   :name: tabCompositeProperties

   +---------------------+-----------------------------------------+-----------------------------------+
   | **Property**        | **Description**                         |    **Value**                      |
   +=====================+=========================================+===================================+
   | :math:`E_{11}`      | Fiber direction modulus                 |  :math:`117.7\,\text{GPa}`        |
   +---------------------+-----------------------------------------+-----------------------------------+
   | :math:`E_{22}`      | Transverse modulus                      | :math:`9.7\,\text{GPa}`           |
   +---------------------+-----------------------------------------+-----------------------------------+
   | :math:`G_{12}`      | In-plane shear modulus                  | :math:`4.8\,\text{GPa}`           |
   +---------------------+-----------------------------------------+-----------------------------------+
   | :math:`G_{13}`      | Transverse shear modulus                | :math:`4.8\,\text{GPa}`           |
   +---------------------+-----------------------------------------+-----------------------------------+
   | :math:`G_{23}`      | Transverse shear modulus                | :math:`4.8\,\text{GPa}`           |
   +---------------------+-----------------------------------------+-----------------------------------+
   | :math:`T_{1}`       | Fiber direction tensile strength        | :math:`1648\,\text{MPa}`          |
   +---------------------+-----------------------------------------+-----------------------------------+
   | :math:`C_{1}`       | Fiber direction compressive strength    | :math:`1034\,\text{MPa}`          |
   +---------------------+-----------------------------------------+-----------------------------------+
   | :math:`T_{2}`       | Transverse tensile strength             | :math:`64\,\text{MPa}`            |
   +---------------------+-----------------------------------------+-----------------------------------+
   | :math:`C_{2}`       | Transverse compressive strength         | :math:`228\,\text{MPa}`           |
   +---------------------+-----------------------------------------+-----------------------------------+
   | :math:`S_{12}`      | Shear strength                          | :math:`71\,\text{MPa}`            |
   +---------------------+-----------------------------------------+-----------------------------------+
   | :math:`\nu_{12}`    | Major Poisson’s ratio                   | :math:`0.35`                      |
   +---------------------+-----------------------------------------+-----------------------------------+
   | :math:`\rho`        | Density                                 | :math:`1550\,\text{kg}/\text{m}^3`|
   +---------------------+-----------------------------------------+-----------------------------------+


In all flight conditions, the structural model is subject to aerodynamic forces and the wingbox's self-weight.
For the sake of simplicity, we do not include any inertial forces due to non-structural masses such as fuel, or leading and trailing edge devices.
Although such loads are simple enough to include in a standalone analysis, they are difficult to include in an optimization problem due to the need to keep them consistent with the wing's geometry as it changes.


