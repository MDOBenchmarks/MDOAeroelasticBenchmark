Optimization Problems
=====================

This section describes our three proposed benchmark optimization problems to be applied to the STW.
The three problems build on one another with the intention of allowing researchers to test their tools on increasingly complex problems:

1. **Case 1**: Structural mass minimization with a fixed geometry.
2. **Case 2**: Fuel burn minimization with a fixed wing planform.
3. **Case 3**: Fuel burn minimization with a variable wing planform.

:numref:`tabAircraftSpec` and :numref:`tabFlightConditions` list information about the aircraft and the flight conditions used in the optimization problems, which are all based on publicly available data on the high gross-weight variant of the Boeing 717.

.. \input{\tablepath/AircraftSpec.tex}

.. table:: Aircraft and mission specifications, based on the Boeing 717 high gross-weight variant.
   :name: tabAircraftSpec

   +-------------------------------------------+---------------------------------------+-------------------------------------------------------+--------------------------------------------+
   |                                           | **Quantity**                          | **Description**                                       |  **Value**                                 |
   +===========================================+=======================================+=======================================================+============================================+
   |  **Baseline wing geometry**               |                                       |                                                       |                                            |
   +-------------------------------------------+---------------------------------------+-------------------------------------------------------+--------------------------------------------+
   |                                           | :math:`b`                             | Semispan                                              | :math:`14\,\text{m}`                       |
   +-------------------------------------------+---------------------------------------+-------------------------------------------------------+--------------------------------------------+
   |                                           | :math:`C_\text{root}`                 | Root chord                                            | :math:`5\,\text{m}`                        |
   +-------------------------------------------+---------------------------------------+-------------------------------------------------------+--------------------------------------------+
   |                                           | :math:`C_\text{tip}`                  | Tip chord                                             | :math:`1.5\,\text{m}`                      |
   +-------------------------------------------+---------------------------------------+-------------------------------------------------------+--------------------------------------------+
   |                                           | :math:`S`                             | Planform area (single wing)                           | :math:`45.5\,\text{m}^2`                   |
   +-------------------------------------------+---------------------------------------+-------------------------------------------------------+--------------------------------------------+
   |                                           | :math:`\text{MAC}`                    | Mean aerodynamic chord                                | :math:`3.56\,\text{m}`                     |
   +-------------------------------------------+---------------------------------------+-------------------------------------------------------+--------------------------------------------+
   |  **Masses**                               |                                       |                                                       |                                            |
   +-------------------------------------------+---------------------------------------+-------------------------------------------------------+--------------------------------------------+
   |                                           | :math:`M_\text{payload}`              | Payload mass                                          | :math:`14.5e3\,\text{kg}`                  |
   +-------------------------------------------+---------------------------------------+-------------------------------------------------------+--------------------------------------------+
   |                                           | :math:`M_\text{frame}`                | Operating empty mass (minus wing)                     | :math:`25e3\,\text{kg}`                    |
   +-------------------------------------------+---------------------------------------+-------------------------------------------------------+--------------------------------------------+
   |                                           | :math:`M_\text{fuel, res}`            | Reserve fuel mass                                     | :math:`2e3\,\text{kg}`                     |
   +-------------------------------------------+---------------------------------------+-------------------------------------------------------+--------------------------------------------+
   |  **Fuelburn calculation parameters**      |                                       |                                                       |                                            |
   +-------------------------------------------+---------------------------------------+-------------------------------------------------------+--------------------------------------------+
   |                                           | :math:`R`                             | Nominal range                                         | :math:`3815\,\text{km}`                    |
   +-------------------------------------------+---------------------------------------+-------------------------------------------------------+--------------------------------------------+
   |                                           | :math:`R_\text{climb}`                | Climb segment range                                   | :math:`290\,\text{km}`                     |
   +-------------------------------------------+---------------------------------------+-------------------------------------------------------+--------------------------------------------+
   |                                           | :math:`V_\text{climb}`                | Average climb speed                                   | :math:`350\,\text{mph}`                    |
   +-------------------------------------------+---------------------------------------+-------------------------------------------------------+--------------------------------------------+
   |                                           | :math:`C_{D,\text{frame}}`            | Airframe drag coefficient (fuselage + tail + nacelle) | :math:`0.01508`                            |
   +-------------------------------------------+---------------------------------------+-------------------------------------------------------+--------------------------------------------+
   |                                           | :math:`k_\text{tank}`                 | Assumed fraction of wingbox that can store fuel       | :math:`0.85`                               |
   +-------------------------------------------+---------------------------------------+-------------------------------------------------------+--------------------------------------------+
   |                                           | :math:`V_\text{aux}`                  | Auxilliary fuel tank volume                           | :math:`2.763\,\text{m}^{3}`                |
   +-------------------------------------------+---------------------------------------+-------------------------------------------------------+--------------------------------------------+
   |                                           | :math:`\text{TSFC}`                   | Thrust specific fuel consumption                      | :math:`18e-6\,\text{kg}/\text{N\,s}`       |
   +-------------------------------------------+---------------------------------------+-------------------------------------------------------+--------------------------------------------+
   |                                           | :math:`\rho_\text{fuel}`              | Fuel density                                          | :math:`804\,\text{kg}/\text{m}^3`          |
   +-------------------------------------------+---------------------------------------+-------------------------------------------------------+--------------------------------------------+


.. \|put{\tablepath/FlightConditions.tex}

.. table:: Flight conditions
   :name: tabFlightConditions
   
   +--------------------+-------------------------+-----------------+-----------------+-------------------------------------------------+
   | **Flight point**   | **Altitude**            | **Mach number** | **Load factor** | **Aircraft mass**                               |
   +====================+=========================+=================+=================+=================================================+
   | Cruise             | :math:`10400\,\text{m}` | 0.7             | 1               | :math:`\sqrt{M_\text{cruise, start}\times LGM}` |
   +--------------------+-------------------------+-----------------+-----------------+-------------------------------------------------+
   | Pull-up Maneuver   | :math:`0\,\text{m}`     | 0.458           | 2.5             | :math:`LGM`                                     |
   +--------------------+-------------------------+-----------------+-----------------+-------------------------------------------------+
   | Push-down Maneuver | :math:`0\,\text{m}`     | 0.458           | -1              | :math:`LGM`                                     |
   +--------------------+-------------------------+-----------------+-----------------+-------------------------------------------------+

Objectives
----------

The objective function to be minimized in **Case 1** is the wingbox mass, computed from the FE model.
The objective function for cases 2 and 3 is the fuel burn over a given mission.
The fuel burn is computed using a two-stage process that accounts for the fuel burn in both cruise and climb.
This process starts by computing the landing gross mass (:math:`\text{LGM}`):

.. math::

   \text{LGM} = M_\text{payload} + M_\text{frame} + M_\text{fuel, res} + 2M_\text{wing}

The total mass of a single wing is computed using the regression model created by :cite:t:`Mariens2013`:

.. math::

  M_\text{wing} = 10.147  M_\text{wingbox}^{0.8162}

Where :math:`M_\text{wingbox}` is the wingbox mass.

Assuming the fuel burn during descent and landing is negligible, the mass at the start of the cruise phase, and then the takeoff gross mass (:math:`\text{TOGM}`) are computed by rearranging the Breguet range equation:

.. math::
   :label: eqFuelBurn

   \begin{align}
   M_\text{cruise, start} & = \text{LGM} \exp\left(\frac{R \times TSFC}{V_\text{cruise}}  \left(\frac{D_\text{cruise}}{L_\text{cruise}}\right)\right)                                                      \\
   \text{TOGM}            & = M_\text{cruise, start} \exp\left(\frac{R_\text{climb} \times TSFC}{V_\text{climb}}  \left(\frac{\cos(\gamma) }{L_\text{cruise}/D_\text{cruise}} + \sin(\gamma)\right)\right) \\
   FB                     & = \text{TOGM} - \text{LGM}
   \end{align}

Where :math:`\gamma` is the climb angle (\SI{2.054}{\degree}), computed based on the assumed climb range and cruise altitude given in :numref:`tabAircraftSpec` and :numref:`tabFlightConditions`.

The lift and drag in the cruise condition are computed using an aeroelastic analysis, the values are doubled to get the full aircraft values, and the drag of un-modeled components (fuselage, tail, and nacelles) is added:

.. math::

  L_\text{cruise} = 2L_\text{wing} \qquad D_\text{cruise} = 2\left(D_\text{wing} + q_\text{cruise} S C_{D,\text{frame}}\right)


Where :math:`C_{D,\text{frame}}` is estimated using a conceptual drag build-up implemented by :cite:t:`Adler2023a` based on the methods of :cite:t:`Torenbeek` and :cite:t:`Raymer1992`.
:math:`S` is the baseline single wing planform area from :numref:`tabAircraftSpec` and does not vary during optimization since we assume that the remainder of the aircraft remains identical.

Design Variables
----------------

The primary differences between the three benchmark problems are the amount of design freedom given to the optimizer through the design variables.
:numref:`tabOptProb-DVs` summarizes these design variables.
Note that, the exact number and form of some design variables will depend on the structural modeling and geometric parameterization approaches used, as is explained in the following sections.

.. \input{\tablepath/DesignVariablesGeneric.tex}

.. table:: Design variables to be used in the benchmark problems
   :name: tabOptProb-DVs

   +-------------------------------------+----------------------+---------------------+----------------------+
   |  **Variable**                       | **Case 1**           | **Case 2**          | **Case 3**           |    
   +=====================================+======================+=====================+======================+
   |  Structural sizing                  | :math:`\checkmark`   | :math:`\checkmark`  | :math:`\checkmark`   |   
   +-------------------------------------+----------------------+---------------------+----------------------+
   |  Pull-up maneuver angle of attack   | :math:`\checkmark`   | :math:`\checkmark`  | :math:`\checkmark`   |   
   +-------------------------------------+----------------------+---------------------+----------------------+
   |  Push-down maneuver angle of attack | :math:`\checkmark`   | :math:`\checkmark`  | :math:`\checkmark`   |   
   +-------------------------------------+----------------------+---------------------+----------------------+
   |  Cruise angle of attack             |                      | :math:`\checkmark`  | :math:`\checkmark`   |   
   +-------------------------------------+----------------------+---------------------+----------------------+
   |  Twist distribution                 |                      | :math:`\checkmark`  | :math:`\checkmark`   |   
   +-------------------------------------+----------------------+---------------------+----------------------+
   |  Section shapes                     |                      | :math:`\checkmark`  | :math:`\checkmark`   |   
   +-------------------------------------+----------------------+---------------------+----------------------+
   |  Chord distribution                 |                      |                     | :math:`\checkmark`   |   
   +-------------------------------------+----------------------+---------------------+----------------------+
   |  Span                               |                      |                     | :math:`\checkmark`   |   
   +-------------------------------------+----------------------+---------------------+----------------------+
   |  Sweep                              |                      |                     | :math:`\checkmark`   |   
   +-------------------------------------+----------------------+---------------------+----------------------+



Structural Variables
--------------------

Due to the variety of structural modeling approaches we want to support in these benchmark problems, we do not prescribe a specific set of structural sizing variables.
Instead we specify the following requirements for the parameterization of the wingbox:

1. A stiffener pitch of :math:`150mm` should be used on all panels.
2. Each rib, and each skin and spar segment between a pair of ribs, should be treated as a separate panel with its own structural sizing variables, as shown in :numref:`figStructuralParameterisation`.
3. The parameterization should allow the optimizer to vary the thickness of the panels.
4. The parameterization should allow the optimizer to vary the thickness of stiffeners, and ideally their cross-section dimensions\footnote{If parameterizing the stiffener cross-section, we recommend participants link the flange width, :math:`W_\text{stiff}`, to the web height, :math:`h_\text{stiff}` (e.g keeping :math:`w_\text{stiff} = h_\text{stiff}`) rather than treating it as a separate variable.}.

This structural parameterization should remain the same for all three optimization problems.


.. figure:: figures/SimpleTransonicWing/StructuralParameterisation-General.png
   :name: figStructuralParameterisation
   :align: center

   Each separately colored wingbox panel should be given it's own structural sizing variables.

Geometric Variables
-------------------

In **Case 1**, the wing geometry is fixed and thus there are no geometric design variables.
In **Case 2**, the section shapes of the wing may be changed in the z direction, and the twist distribution may be varied.
In **Case 3**, the optimizer may also vary the span, sweep, and chord distribution.
The parameterization method used to achieve these changes (e.g FFD, CAD etc) and the level of detail (e.g number of values used to define the twist distribution) are left free.
However, the following requirements must be satisfied:

* The twisting must occur about the leading edge of the wing.
* The root of the wing (at the symmetry plane) must not be twisted.
* The shape changes must be parameterized in a manner that does not allow the optimizer to achieve twisting of the section shapes.
* The SOB junction of the wingbox should not move in the y direction.
* The leading edge of the wing must remain straight, save for a potential break at the SOB junction.

Aerodynamic Variables
---------------------

Finally, the optimizer can control the angles of attack at each flight point to meet the lift constraints described in the Constraints section.

Constraints
-----------

:numref:`tabOptProb-Constraints` provides a high-level summary the constraints applied in the 3 benchmark problems.
As with the design variables, the exact formulation of the constraints in each benchmark problem will depend to some extent on the structural modeling and geometric parameterization approaches used by participants.

Structural Constraints
----------------------

The primary structural constraints enforce that the wingbox has a safety factor of 1.5 to both material and buckling failure in both maneuver flight conditions.
How this is achieved is left free.

Adjacency constraints are enforced to avoid abrupt changes in panel sizing.
The change in panel and stiffener thicknesses between adjacent skin and spar panels is limited to :math:`2.5mm` and the change in stiffener height to :math:`10mm`. (By this we mean that the difference between variables on two adjacent skin panels, or two adjacent spar panels, are constrained, but not the difference between a spar panel and an adjacent skin panel.)
Some basic structural sizing rules suggested by :cite:t:`Kassapoglou2013` should be used on all panels:

* The skin and stiffener thicknesses should be at least :math:`0.6mm`
* The stiffener heights should be at least :math:`18mm`
* The stiffener flange widths should be at least :math:`25.4mm`
* The aspect-ratio of the stiffener web (:math:`h_\text{stiff}/t_\text{stiff}`) should be between 5 and 30.
* The thickness of the stiffener flanges on a panel should be no more than 15 times the panel thickness.
* The stiffener flange width should be less than the stiffener pitch to avoid overlapping flanges.

Participants should enforce as many of these constraints as are applicable to their structural sizing parameterization in all three benchmark problems.

Geometric Constraints
---------------------

Since the benchmark problems consider a limited selection of flight points, additional geometric constraints are required to ensure the optimizer produces a realistic wing geometry:

* The wing's leading edge radius must be at least 90% of its baseline value throughout the span to maintain reasonable low-speed performance.
* The front and rear spars must be at least 75% of their baseline height throughout the span to maintain the space required to mount components such as control surface actuators :cite:p:`Liem2015a`.
* The region between the rear spar and the trailing edge must be at least 50% of its baseline thickness to prevent the optimizer creating an unrealistically thin trailing edge.
* The wingbox volume must be large enough to store the amount of fuel required for the mission, as computed in the objective function.
* When the planform is varied, the wing loading :math:`\left(\text{TOGM}/2S\right)` must be no greater than :math:`600kg / m^2`.

When computing the fuel volume constraint, the total available fuel tank volume is the auxiliary tank volume plus the fraction of both wingboxes that is assumed to be available for fuel storage, the constraint can therefore be written as:

.. math::

   M_\text{fuel}/\rho_\text{fuel} \leq V_\text{aux} + 2k_\text{tank} V_\text{wingbox}

or:

.. math::

   \frac{M_\text{fuel}/\rho_\text{fuel} - V_\text{aux}}{2k_\text{tank} V_\text{wingbox}} \leq 1

which is better scaled.
Note that the total fuel mass, :math:`M_\text{fuel}`, is the sum of the fuel burn computed using :eq:`eqFuelBurn` and the reserve fuel mass given in :numref:`tabAircraftSpec`.

Aerodynamic Constraints
-----------------------

The lift produced by the wing at each flight point must be equal to the aircraft weight multiplied by the relevant load factor.
The maneuvers are assumed to be performed at the LGM since the inertial relief of the fuel is not included in the structural model.
The aircraft mass for the cruise condition is taken to be the mid-cruise mass, which is the geometric average of the cruise start and end masses.
This accounts for the non-uniform rate of fuel burn over the segment.

.. \input{\tablepath/ConstraintsGeneric.tex}

.. table:: Constraints to be enforced in the benchmark problems
   :name: tabOptProb-Constraints

   +--------------------------------------------------------------------------------------------+------------------------------------------------+---------------------+---------------------+---------------------+
   | :math:`SR_\text{2.5g} \leq 1 / 1.5`                                                        | Pull-up maneuver strength ratio                | :math:`\checkmark`  | :math:`\checkmark`  | :math:`\checkmark`  |
   +============================================================================================+================================================+=====================+=====================+=====================+
   | :math:`SR_\text{-1g} \leq 1 / 1.5`                                                         | Push-down maneuver strength ratio              | :math:`\checkmark`  | :math:`\checkmark`  | :math:`\checkmark`  |
   +--------------------------------------------------------------------------------------------+------------------------------------------------+---------------------+---------------------+---------------------+
   | :math:`\left|t_{\text{panel},i} - t_{\text{panel},j}\right| \leq` \SI{2.5}{\milli\metre}   | Skin/spar panel thickness adjacency            | :math:`\checkmark`  | :math:`\checkmark`  | :math:`\checkmark`  |
   +--------------------------------------------------------------------------------------------+------------------------------------------------+---------------------+---------------------+---------------------+
   | :math:`\left|t_{\text{stiff},i} - t_{\text{stiff},j}\right| \leq` \SI{2.5}{\milli\metre}   | Skin/spar stiffener thickness adjacency        | :math:`\checkmark`  | :math:`\checkmark`  | :math:`\checkmark`  |
   +--------------------------------------------------------------------------------------------+------------------------------------------------+---------------------+---------------------+---------------------+
   | :math:`\left|h_{\text{stiff},i} - h_{\text{stiff},j}\right| \leq` \SI{10}{\milli\metre}    | Skin/spar stiffener height adjacency \tnote{*} | :math:`\checkmark`  | :math:`\checkmark`  | :math:`\checkmark`  |
   +--------------------------------------------------------------------------------------------+------------------------------------------------+---------------------+---------------------+---------------------+
   | :math:`t_{\text{stiff},i} \leq 15 t_{\text{panel},i}`                                      | Maximum stiffener thickness \tnote{*}          | :math:`\checkmark`  | :math:`\checkmark`  | :math:`\checkmark`  |
   +--------------------------------------------------------------------------------------------+------------------------------------------------+---------------------+---------------------+---------------------+
   | :math:`h_{\text{stiff},i} \leq 30 t_{\text{stiff},i}`                                      | Maximum stiffener aspect-ratio \tnote{*}       | :math:`\checkmark`  | :math:`\checkmark`  | :math:`\checkmark`  |
   +--------------------------------------------------------------------------------------------+------------------------------------------------+---------------------+---------------------+---------------------+
   | :math:`h_{\text{stiff},i} \geq 5 t_{\text{stiff},i}`                                       | Minimum stiffener aspect-ratio \tnote{*}       | :math:`\checkmark`  | :math:`\checkmark`  | :math:`\checkmark`  |
   +--------------------------------------------------------------------------------------------+------------------------------------------------+---------------------+---------------------+---------------------+
   | :math:`w_{\text{stiff},i} \leq p_{\text{stiff},i}`                                         | Minimum stiffener spacing \tnote{*}            | :math:`\checkmark`  | :math:`\checkmark`  | :math:`\checkmark`  |
   +--------------------------------------------------------------------------------------------+------------------------------------------------+---------------------+---------------------+---------------------+
   | :math:`L_\text{2.5g} = 2.5 LGM g`                                                          | Pull-up maneuver lift level                    | :math:`\checkmark`  | :math:`\checkmark`  | :math:`\checkmark`  |
   +--------------------------------------------------------------------------------------------+------------------------------------------------+---------------------+---------------------+---------------------+
   | :math:`L_\text{-1g} = -LGM g`                                                              | Push-down maneuver lift level                  | :math:`\checkmark`  | :math:`\checkmark`  | :math:`\checkmark`  |
   +--------------------------------------------------------------------------------------------+------------------------------------------------+---------------------+---------------------+---------------------+
   | :math:`L_\text{cruise} = M_\text{mid-cruise} g`                                            | Cruise maneuver lift level                     |                     | :math:`\checkmark`  | :math:`\checkmark`  |
   +--------------------------------------------------------------------------------------------+------------------------------------------------+---------------------+---------------------+---------------------+
   | :math:`t_\text{spar} \geq 0.75 t_{\text{spar},0}`                                          | Minimum Spar height                            |                     | :math:`\checkmark`  | :math:`\checkmark`  |
   +--------------------------------------------------------------------------------------------+------------------------------------------------+---------------------+---------------------+---------------------+
   | :math:`t \geq  0.5 t_{0}`                                                                  | Minimum TE thickness                           |                     | :math:`\checkmark`  | :math:`\checkmark`  |
   +--------------------------------------------------------------------------------------------+------------------------------------------------+---------------------+---------------------+---------------------+
   | :math:`R_\text{LE} \geq 0.9 R_{\text{LE},0}`                                               | Minimum Leading edge radius                    |                     | :math:`\checkmark`  | :math:`\checkmark`  |
   +--------------------------------------------------------------------------------------------+------------------------------------------------+---------------------+---------------------+---------------------+
   | :math:`M_\text{fuel}/\rho_\text{fuel} \leq V_\text{aux} + 2k_\text{tank} V_\text{wingbox}` | Fuel volume                                    |                     | :math:`\checkmark`  | :math:`\checkmark`  |
   +--------------------------------------------------------------------------------------------+------------------------------------------------+---------------------+---------------------+---------------------+
   | :math:`TOGM / 2S \leq` \SI{600}{\kg\per\metre\squared}                                     | Maximum wing loading                           |                     |                     | :math:`\checkmark`  |
   +--------------------------------------------------------------------------------------------+------------------------------------------------+---------------------+---------------------+---------------------+
