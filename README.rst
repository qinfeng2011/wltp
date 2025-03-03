################################################################
wltp: generate WLTC gear-shifts based on vehicle characteristics
################################################################
:versions:      1.0.0.dev12 (2019-08-30 14:55:39) |br|
                |gh-version| |pypi-version| |conda-version| |dev-status| |br|
                |python-ver|  |conda-plat|
:documentation: https://wltp.readthedocs.org/ |br|
                |docs-status| build-date: |today|
:live-demo:     |binder|
:sources:       https://github.com/JRCSTU/wltp |br|
                |travis-status| |appveyor-status| |downloads-count| |codestyle| |br|
                |gh-watch| |gh-star| |gh-fork| |gh-issues|
:keywords:      UNECE, automotive, car, cars, driving, engine, emissions, fuel-consumption,
                gears, gearshifts, rpm, simulation, simulator, standard, vehicle, vehicles, WLTC, NEDC
:copyright:     2013-2019 European Commission (`JRC-IET <https://ec.europa.eu/jrc/en/institutes/iet>`_) |br|
                |proj-lic|

A python package to generate the *gear-shifts* of Light-duty vehicles
running the :term:`WLTP` driving-cycles, according to :term:`UNECE`'s :term:`GTR`\s.

.. figure:: docs/_static/wltc_class3b.png
    :align: center

    **Figure 1:** :ref:`annex-2:cycles` for class-3b Vehicles


.. Attention::
    This *wltp* python project is still in *alpha* stage, in the send that
    its results are not "correct" by the standard, and no WLTP dyno-tests should rely
    currently on them.

    Some of the known limitations are described in these places:

    * In the :doc:`CHANGES`.
    * Compare results with AccDB in ``Notebooks/CarsDB-compare.ipynb`` notebook;
      launch your private *demo-server* (|binder|) to view it.

.. _end-opening:
.. contents:: Table of Contents
  :backlinks: top
.. _begin-intro:

Introduction
============

Overview
--------
The calculator accepts as input the vehicle's technical data, along with parameters for modifying the execution
of the :term:`WLTC` cycle, and it then spits-out the gear-shifts of the vehicle, the attained speed-profile,
and any warnings.  It does not calculate any |CO2| emissions.


An "execution" or a "run" of an experiment is depicted in the following diagram::

                .-----------------.                         .------------------.
                :      Input      :                         :      Output      :
                ;-----------------;                         ;------------------;
               ; +--test_mass    ;     ____________        ; +--pmr           ;
              ;  +--n_idle      ;     |            |      ;  +--wltc_class   ;
             ;   +--f0,f1,f2   ;  ==> |   Cycle    | ==> ;   +--...         ;
            ;    +--wot/      ;       | Generator  |    ;    +--cycle      ;
           ;         +--     ;        |____________|   ;     |    +--     ;
          ;      +--n2vs    ;                         ;      +--gwots    ;
         ;           +--   ;                         ;            +--   ;
        '-----------------'                         '------------------'

The *Input*, *Output* and all its contents are instances of :term:`datamodel`
(trees of strings, numbers & pandas objects)


Quick-start
-----------
- Launch the example *jupyter notebooks* in a private *demo server* (|binder|).
- Otherwise, install it locally, preferably from the sources (instructions below).

Prerequisites:
^^^^^^^^^^^^^^
**Python-3.6+** is required and **Pytrhon-3.7** recommended.
It requires **numpy/scipy** and **pandas** libraries with native backends.

.. Tip::
    On *Windows*, it is preferable to use the `miniconda <https://docs.conda.io/en/latest/miniconda.html>`_
    distribution; although its `conda` command adds another layer of complexity on top of ``pip``,
    unlike standard Python, it has pre-built all native libraries required
    (e.g. **numpy/scipy** and **pandas**).

    If nevertheless you choose the *standard Python*, and some packages fail to build when `pip`-installing them,
    download these packages from `Gohlke's "Unofficial Windows Binaries"
    <https://www.lfd.uci.edu/~gohlke/pythonlibs/>`_ and install them manually with::

        pip install <package-file-v1.2.3.whl>

Download:
^^^^^^^^^
Download the sources,

- either with *git*, by giving this command to the terminal::

      git clone https://github.com/JRCSTU/wltp/ --depth=1

- or download and extract the project-archive from the release page:
  https://github.com/JRCSTU/wltp/archive/v1.0.0.dev12.zip


Install:
^^^^^^^^
From within the project directory, run one of these commands to install it:

- for standard python, installing with ``pip`` is enough (but might)::

      pip install -e .[test]

- for *conda*, prefer to install the conda-packages listed in :file:`Notebooks/conda/conda-reqs.txt`,
  before running the same `pip` command, like this::

      conda install  --override-channels -c ankostis -c conda-forge -c defaults --file Notebooks/conda/conda-reqs.txt
      pip install -e .[dev]


- Check installation:

  .. code-block:: bash

      $ wltp --version
      1.0.0.dev12

      $ wltp --help
        ...

    See: :ref:`wltp-usage`

- Recreate jupyter notebooks from the paired ``*.Rmd`` files
  (only these files are stored in git-repo).

- Run pyalgo on all AccDB cars to re-create the H5 file
  needed for ``CarsDB-compare`` notebook, etc::

      jupytext --sync /Notebooks/*.Rmd


Usage:
^^^^^^
.. code-block:: python

    import pandas as pd
    from wltp import datamodel
    from wltp.experiment import Experiment

    inp_mdl = datamodel.get_model_base()
    inp_mdl.update({
        "unladen_mass": None,
        "test_mass": 1100,  # in kg
        "p_rated": 95.3,  # in kW
        "n_rated": 3000,  # in RPM
        "n_idle": 600,
        "gear_ratios": [122.88, 75.12, 50.06, 38.26, 33.63],

        ## For giving absolute P numbers,
        #  rename `p_norm` column to `p`.
        #
        "wot": pd.DataFrame(
            [[600, 0.1],
            [2500, 1],
            [3500, 1],
            [5000, 0.7]], columns=["n", "p_norm"]
        ),
        'f0': 395.78,
        'f1': 0,
        'f2': 0.15,
    })
    datamodel.validate_model(inp_mdl, additional_properties=True)
    exp = Experiment(inp_mdl, skip_model_validation=True)

    # exp = Experiment(inp_mdl)
    out_mdl = exp.run()
    print(f"Available values: \n{list(out_mdl.keys())}")
    print(f"Cycle: \n{out_mdl['cycle']}")

See: :ref:`python-usage`



Project files and folders
-------------------------
The files and folders of the project are listed below (see also :ref:`architecture:Architecture`)::

    +--bin/                     # (shell-scripts) Utilities & preprocessing of WLTC data on GTR and the wltp_db
    |   +--bumpver.py           # (script) Update project's version-string
    +--wltp/                    # (package) python-code of the calculator
    |   +--cycles/              # (package) code & data for the WLTC data
    |   +--experiment           # top-level code running the algo
    |   +--datamodel            # schemas & defaults for data of algo
    |   +--cycler               # code for generating the cycle
    |   +--engine               # formulae for engine power & revolutions and gear-box
    |   +--vehicle              # formulae for cyle/vehicle dynamics
    |   +--vmax                 # formulae estimating `v_max` from wot
    |   +--downscale            # formulae downscaling cycles based on pmr/test_mass ratio
    |   +--invariants           # definitions & idenmpotent formulae for physics/engineering
    |   +--io                   # utilities for starting-up, parsing, naming and spitting data
    |   +--utils                # software utils unrelated to physics or engineering
    |   +--cli                  # (OUTDATED) command-line entry-point for launching this wltp tool
    |   +--plots                # (OUTDATED) code for plotting diagrams related to wltp cycles & results
    |   +--idgears              # (OUTDATED) reconstructs the gears-profile by identifying the actual gears
    +--tests/                   # (package) Test-TestCases
        +--vehdb                # Utils for manipulating h5db with accdb & pyalgo cases.
    +--docs/                    # (folder) documentation
    |   +--pyplots/             # (DEPRECATED by notebooks) scripts plotting the metric diagrams embeded in the README
    +--Notebooks/               # Jupyter notebooks for running & comparing results (see `Notebooks/README.md`)
        +--AccDB_src/           # AccDB code & queries extracted and stored as text
    +--setup.py                 # (script) The entry point for `setuptools`, installing, testing, etc
    +--requirements/            # (txt-files) Various pip-dependencies for tools.
    +--README.rst
    +--CHANGES.rst
    +--LICENSE.txt



.. _wltp-usage:

Usage
=====
.. _python-usage:

Python usage
------------
First run :command:`python` or :command:`ipython` :abbr:`REPL (Read-Eval-Print Loop)` and
try to import the project to check its version:

.. doctest::

    >>> import wltp

    >>> wltp.__version__            ## Check version once more.
    '1.0.0.dev12'

    >>> wltp.__file__               ## To check where it was installed.         # doctest: +SKIP
    /usr/local/lib/site-package/wltp-...


.. Tip:
    The use :command:`ipython` is preffered over :command:`python` since it offers various user-friendly
    facilities, such as pressing :kbd:`Tab` for completions, or allowing you to suffix commands with ``?`` or ``??``
    to get help and read their source-code.

    Additionally you can <b>copy any python commands starting with ``>>>`` and ``...``</b> and copy paste them directly
    into the ipython interpreter; it will remove these prefixes.
    But in :command:`python` you have to remove it youself.

If everything works, create the :term:`datamodel` of the experiment.
You can assemble the model-tree by the use of:

* sequences,
* dictionaries,
* :class:`pandas.DataFrame`,
* :class:`pandas.Series`, and
* URI-references to other model-trees.


For instance:

.. doctest::

    >>> from wltp import datamodel
    >>> from wltp.experiment import Experiment

    >>> mdl = {
    ...     "unladen_mass": 1430,
    ...     "test_mass":    1500,
    ...     "v_max":        195,
    ...     "p_rated":      100,
    ...     "n_rated":      5450,
    ...     "n_idle":       950,
    ...     "n_min":        None,                           ## Manufacturers my overridde it
    ...     "gear_ratios":         [120.5, 75, 50, 43, 37, 32],
    ...     "f0":   100,
    ...     "f1":   0.5,
    ...     "f2":   0.04,
    ... }
    >>> mdl = datamodel.upd_default_load_curve(mdl)                   ## need some WOT


For information on the accepted model-data, check the :ref:`code:Schema`:

.. doctest::

    >>> from wltp import utils
    >>> utils.yaml_dumps(datamodel.model_schema(), indent=2)                                # doctest: +SKIP
    $schema: http://json-schema.org/draft-07/schema#
    $id: /wltc
    title: WLTC data
    type: object
    additionalProperties: false
    required:
    - classes
    properties:
    classes:
    ...


You then have to feed this model-tree to the :class:`~wltp.experiment.Experiment`
constructor. Internally the :class:`pandalone.pandel.Pandel` resolves URIs, fills-in default values and
validates the data based on the project's pre-defined :term:`JSON-schema`:

.. doctest::

    >>> processor = Experiment(mdl)         ## Fills-in defaults and Validates model.


Assuming validation passes without errors, you can now inspect the defaulted-model
before running the experiment:

.. doctest::

    >>> mdl = processor.model               ## Returns the validated model with filled-in defaults.
    >>> sorted(mdl)                         ## The "defaulted" model now includes the `params` branch.
    ['driver_mass', 'f0', 'f1', 'f2', 'f_downscale_decimals', 'f_downscale_threshold', 'f_inertial',
     'f_n_clutch_gear2', 'f_n_min', 'f_n_min_gear2', 'f_safety_margin', 'gear_ratios', 'n_idle', 'n_min',
     'n_min_drive1', 'n_min_drive2', 'n_min_drive2_stopdecel', 'n_min_drive2_up', 'n_min_drive_dn_start',
     'n_min_drive_down', 'n_min_drive_set', 'n_min_drive_up', 'n_min_drive_up_start', 'n_rated',
     'p_rated', 't_cold_end', 'test_mass', 'unladen_mass', 'v_max', 'v_stopped_threshold', 'wltc_data',
     'wot']


Now you can run the experiment:

.. doctest::

    >>> mdl = processor.run()               ## Runs experiment and augments the model with results.
    >>> sorted(mdl)                         ## Print the top-branches of the "augmented" model.
    [`cycle`, 'driver_mass', 'f0', 'f1', 'f2', `f_downscale`, 'f_downscale_decimals',
     'f_downscale_threshold', `f_dscl_orig`, 'f_inertial', 'f_n_clutch_gear2', 'f_n_min',
     'f_n_min_gear2', 'f_safety_margin', `g_vmax`, 'gear_ratios', `is_n_lim_vmax`, `n95_high`, `n95_low`,
     'n_idle', `n_max`, `n_max1`, `n_max2`, `n_max3`, 'n_min', 'n_min_drive1', 'n_min_drive2',
     'n_min_drive2_stopdecel', 'n_min_drive2_up', 'n_min_drive_dn_start', 'n_min_drive_down',
     'n_min_drive_set', 'n_min_drive_up', 'n_min_drive_up_start', 'n_rated', `n_vmax`, 'p_rated', `pmr`,
     't_cold_end', 'test_mass', 'unladen_mass', 'v_max', 'v_stopped_threshold', `wltc_class`,
     'wltc_data', 'wot', `wots_vmax`]

To access the time-based cycle-results it is better to use a :class:`pandas.DataFrame`:

.. doctest::

    >>> import pandas as pd, wltp.cycler as cycler, wltp.io as wio
    >>> df = pd.DataFrame(mdl['cycle']); df.index.name = 't'
    >>> df.shape                            ## ROWS(time-steps) X COLUMNS.
    (1801, 94)
    >>> wio.flatten_columns(df.columns)
    ['t', 'v_cycle', 'v_target', 'a', 'phase_1', 'phase_2', 'phase_3', 'phase_4', 'accel_raw', 'run',
     'stop', 'accel', 'cruise', 'decel', 'initaccel', 'stopdecel', 'up', 'p_inert', 'n/g1', 'n/g2',
     'n/g3', 'n/g4', 'n/g5', 'n/g6', 'n_norm/g1', 'n_norm/g2', 'n_norm/g3', 'n_norm/g4', 'n_norm/g5',
     'n_norm/g6', 'p/g1', 'p/g2', 'p/g3', 'p/g4', 'p/g5', 'p/g6', 'p_avail/g1', 'p_avail/g2',
     'p_avail/g3', 'p_avail/g4', 'p_avail/g5', 'p_avail/g6', 'p_avail_stable/g1', 'p_avail_stable/g2',
     'p_avail_stable/g3', 'p_avail_stable/g4', 'p_avail_stable/g5', 'p_avail_stable/g6', 'p_norm/g1',
     'p_norm/g2', 'p_norm/g3', 'p_norm/g4', 'p_norm/g5', 'p_norm/g6', 'p_resist', 'p_req', 'ok_gear0/g0',
     'ok_max_n/g1', 'ok_max_n/g2', 'ok_max_n/g3', 'ok_max_n/g4', 'ok_max_n/g5', 'ok_max_n/g6',
     'ok_min_n_g1/g1', 'ok_min_n_g1_initaccel/g1', 'ok_min_n_g2/g2', 'ok_min_n_g2_stopdecel/g2',
     'ok_min_n_g3plus_dns/g3', 'ok_min_n_g3plus_dns/g4', 'ok_min_n_g3plus_dns/g5',
     'ok_min_n_g3plus_dns/g6', 'ok_min_n_g3plus_ups/g3', 'ok_min_n_g3plus_ups/g4',
     'ok_min_n_g3plus_ups/g5', 'ok_min_n_g3plus_ups/g6', 'ok_p/g3', 'ok_p/g4', 'ok_p/g5', 'ok_p/g6',
     'ok_n/g1', 'ok_n/g2', 'ok_n/g3', 'ok_n/g4', 'ok_n/g5', 'ok_n/g6', 'ok_gear/g0', 'ok_gear/g1',
     'ok_gear/g2', 'ok_gear/g3', 'ok_gear/g4', 'ok_gear/g5', 'ok_gear/g6', 'g_min', 'g_max0']
    >>> 'Mean engine_speed: %s' % df.n.mean()                                       # doctest: +SKIP
    'Mean engine_speed: 1908.9266796224322'
    >>> df.describe()                                                               # doctest: +SKIP
               v_class     v_target  ...     rpm_norm       v_real
    count  1801.000000  1801.000000  ...  1801.000000  1801.000000
    mean     46.361410    46.361410  ...     0.209621    50.235126
    std      36.107745    36.107745  ...     0.192395    32.317776
    min       0.000000     0.000000  ...    -0.205756     0.200000
    25%      17.700000    17.700000  ...     0.083889    28.100000
    50%      41.300000    41.300000  ...     0.167778    41.300000
    75%      69.100000    69.100000  ...     0.285556    69.100000
    max     131.300000   131.300000  ...     0.722578   131.300000
    <BLANKLINE>
    [8 rows x 10 columns]

    >>> processor.driveability_report()                                             # doctest: +SKIP
    ...
      12: (a: X-->0)
      13: g1: Revolutions too low!
      14: g1: Revolutions too low!
    ...
      30: (b2(2): 5-->4)
    ...
      38: (c1: 4-->3)
      39: (c1: 4-->3)
      40: Rule e or g missed downshift(40: 4-->3) in acceleration?
    ...
      42: Rule e or g missed downshift(42: 3-->2) in acceleration?
    ...

You can export the cycle-run results in a CSV-file with the following pandas command:

.. code-block:: pycon

    >>> df.to_csv('cycle.csv')                                                      # doctest: +SKIP


For more examples, download the sources and check the test-cases
found under the :file:`/tests/` folder.

.. _cmd-line-usage:

Cmd-line usage
--------------
.. Warning:: Not implemented in yet.

The command-line usage below requires the Python environment to be installed, and provides for
executing an experiment directly from the OS's shell (i.e. :program:`cmd` in windows or :program:`bash` in POSIX),
and in a *single* command.  To have precise control over the inputs and outputs
(i.e. experiments in a "batch" and/or in a design of experiments)
you have to run the experiments using the API python, as explained below.


The entry-point script is called :program:`wltp`, and it must have been placed in your :envvar:`PATH`
during installation.  This script can construct a *model* by reading input-data
from multiple files and/or overriding specific single-value items. Conversely,
it can output multiple parts of the resulting-model into files.

To get help for this script, use the following commands:

.. code-block:: bash

    $ wltp --help                               ## to get generic help for cmd-line syntax
    $ wltcmdp.py -M vehicle/full_load_curve     ## to get help for specific model-paths


and then, assuming ``vehicle.csv`` is a CSV file with the vehicle parameters
for which you want to override the ``n_idle`` only, run the following:

.. code-block:: bash

    $ wltp -v \
        -I vehicle.csv file_frmt=SERIES model_path=params header@=None \
        -m vehicle/n_idle:=850 \
        -O cycle.csv model_path=cycle


.. _excel-usage:

Excel usage
-----------
.. Attention:: OUTDATED!!! Excel-integration requires Python 3 and *Windows* or *OS X*!

In *Windows* and *OS X* you may utilize the excellent `xlwings <http://xlwings.org/quickstart/>`_ library
to use Excel files for providing input and output to the experiment.

To create the necessary template-files in your current-directory you should enter:

.. code-block:: shell

     $ wltp --excel


You could type instead :samp:`wltp --excel {file_path}` to specify a different destination path.

In *windows*/*OS X* you can type :samp:`wltp --excelrun` and the files will be created in your home-directory
and the excel will open them in one-shot.

All the above commands creates two files:

:file:`wltp_excel_runner.xlsm`
    The python-enabled excel-file where input and output data are written, as seen in the screenshot below:

    .. image:: docs/xlwings_screenshot.png
        :scale: 50%
        :alt: Screenshot of the `wltp_excel_runner.xlsm` file.

    After opening it the first tie, enable the macros on the workbook, select the python-code at the left and click
    the :menuselection:`Run Selection as Pyhon` button; one sheet per vehicle should be created.

    The excel-file contains additionally appropriate *VBA* modules allowing you to invoke *Python code*
    present in *selected cells* with a click of a button, and python-functions declared in the python-script, below,
    using the ``mypy`` namespace.

    To add more input-columns, you need to set as column *Headers* the *json-pointers* path of the desired
    model item (see :ref:`python-usage` below,).

:file:`wltp_excel_runner.py`
    Utility python functions used by the above xls-file for running a batch of experiments.

    The particular functions included reads multiple vehicles from the input table with various
    vehicle characteristics and/or experiment parameters, and then it adds a new worksheet containing
    the cycle-run of each vehicle .
    Of course you can edit it to further fit your needs.


.. Note:: You may reverse the procedure described above and run the python-script instead.
    The script will open the excel-file, run the experiments and add the new sheets, but in case any errors occur,
    this time you can debug them, if you had executed the script through *LiClipse*, or *IPython*!

Some general notes regarding the python-code from excel-cells:

* On each invocation, the predefined VBA module ``pandalon`` executes a dynamically generated python-script file
  in the same folder where the excel-file resides, which, among others, imports the "sister" python-script file.
  You can read & modify the sister python-script to import libraries such as 'numpy' and 'pandas',
  or pre-define utility python functions.
* The name of the sister python-script is automatically calculated from the name of the Excel-file,
  and it must be valid as a python module-name.  Therefore do not use non-alphanumeric characters such as
  spaces(`` ``), dashes(``-``) and dots(``.``) on the Excel-file.
* On errors, a log-file is written in the same folder where the excel-file resides,
  for as long as **the message-box is visible, and it is deleted automatically after you click 'ok'!**
* Read http://docs.xlwings.org/quickstart.html


.. _architecture:

Architecture
============
The Python code is highly modular, with `testability in mind
<https://en.wikipedia.org/wiki/Test-driven_development>`_.
so that specific parts can run in isolation.
This facilitates studying tough issues, such as, `double-precision reproducibility
<https://gist.github.com/ankostis/895ba33f05a5a76539cb689a2f366230>`_, boundary conditions,
comparison of numeric outputs, and studying the code in sub-routines.

.. tip::
    Run test-cases with ``pytest`` command.

Data Structures:
----------------
.. default-role:: term

Computations are vectorial, based on `hierarchical dataframes
<https://pandas.pydata.org/pandas-docs/stable/user_guide/advanced.html>`_,
all of them stored in a single structure, the `datamodel`.
In case the computation breaks, you can still retrive all intermediate results
till that point.

.. TODO::
    Almost all of the names of the `datamodel` and `formulae` can be remapped,
    For instance, it is possible to run the tool on data containing ``n_idling_speed``
    instead of ``n_idle`` (which is the default), without renaming the input data.

.. glossary::

    mdl
    datamodel
        The container of all the scalar Input & Output values, the WLTC constants factors,
        and 3 matrices: `WOT`, `gwots`, and the `cycle run` time series.

        It is composed by a stack of mergeable `JSON-schema` abiding trees of *string, numbers & pandas objects*,
        formed with python *sequences & dictionaries, and URI-references*.
        It is implemented in :mod:`~wltp.datamodel`, supported by :class:`pandalone.pandata.Pandel`.


    WOT
    Full Load Curve
        An *input* array/dict/dataframe with the full load power curves for (at least) 2 columns for ``(n, p)``
        or their normalized values ``(n_norm, p_norm)``.
        See also https://en.wikipedia.org/wiki/Wide_open_throttle

    gwots
    Grid WOTs
        A dataframe produced from `WOT` for all gear-ratios, indexed by a grid of rounded velocities,
        and with 2-level columns ``(item, gear)``.
        It is generated by :func:`~wltp.engine.interpolate_wot_on_v_grid()`, and augmented
        by :func:`~wltp.engine.calc_p_avail_in_gwots()` & :func:`~wltp.vehicle.calc_road_load_power()` .

        .. TODO::
            Move `Grid WOTs` code in own module :mod:`~wltp.gwots`.

    cycle
    Cycle run
        A dataframe with all the time-series, indexed by the time of the samples.
        The velocities for each time-sample must exist in the `gwots`.
        The columns are the same 2-level columns like *gwots*.
        it is implemented in :mod:`~wltp.cycler`.

Code Structure:
---------------
The computation code is roughly divided in these python modules:

.. glossary::

    formulae
        Physics and engineering code, implemented in modules:

        - :mod:`~wltp.engine`
        - :mod:`~wltp.vmax`
        - :mod:`~wltp.downscale`
        - :mod:`~wltp.vehicle`

    - orchestration
        The code producing the actual gear-shifting, implemented in modules:

        - :mod:`~wltp.datamodel`
        - :mod:`~wltp.cycler`
        - :mod:`~wltp.gridwots` (TODO)
        - :mod:`~wltp.scheduler` (TODO)
        - :mod:`~wltp.experiment` (TO BE DROPPED, :mod:`~wltp.datamodel` will assume all functionality)

    scheduler
        (TODO) The internal software component which decides which `formulae` to execute
        based on given inputs and requested outputs.

The blueprint for the underlying software ideas is given with this diagram:

.. image:: docs/_static/WLTP_architecture.png
    :alt: Software architectural concepts underlying WLTP code structure.

Note that currently there is no `scheduler` component, which will allow to execute the tool
with a varying list of available inputs & required data, and automatically compute
only what is not already given.


Specs & Algorithm
-----------------
This program imitates to some degree the  `MS Access DB` (as of July 2019),
following  this *08.07.2019_HS rev2_23072019 GTR specification*
(:download:`docs/_static/WLTP-GS-TF-41 GTR 15 annex 1 and annex 2 08.07.2019_HS rev2_23072019.docx`,
included in the :file:`docs/_static` folder).

.. Note::
    There is a distinctive difference between this implementation and the `AccDB`:

    All computations are *vectorial*, meaning that all intermediate results are calculated & stored,
    for all time sample-points,
    and not just the side of the conditions that evaluate to *true* on each sample.

The latest official version of this GTR, along
with other related documents maybe found at UNECE's site:

* http://www.unece.org/trans/main/wp29/wp29wgs/wp29grpe/grpedoc_2013.html
* https://www2.unece.org/wiki/pages/viewpage.action?pageId=2523179


.. default-role:: obj
.. _begin-annex:


Cycles
======
The WLTC-profiles for the various classes were generated from the tables
of the specs above using the :file:`devtools/csvcolumns8to2.py` script, but it still requires
an intermediate manual step involving a spreadsheet to copy the table into ands save them as CSV.


.. image:: docs/_static/wltc_class1.png
    :align: center
.. image:: docs/_static/wltc_class2.png
    :align: center
.. image:: docs/_static/wltc_class3a.png
    :align: center
.. image:: docs/_static/wltc_class3b.png
    :align: center

Phases
------
As reported by :func:`wltp.cycles.cycle_phases()`, where *phasing* refers to:

- **V:** phases for quantities dependent on **Velocity** samples
- **VA0:** phases for **Acceleration**\-dependent quantities starting on *t=0*.
- **VA1:** phases for **Acceleration**\-dependent quantities starting on *t=1*
  (e.g. Energy in Annex 7).

=======  ========   ========    ===========     ============    ============
class    phasing    part-1      part-2          part-3          part-4
=======  ========   ========    ===========     ============    ============
class1   **V**      [0, 589]    [589, 1022]     [1022, 1612]
\        **VA0**    [0, 588]    [589, 1021]     [1022, 1611]
\        **VA1**    [1, 589]    [590, 1022]     [1023, 1612]
class2   **V**      [0, 589]    [589, 1022]     [1022, 1477]    [1477, 1801]
\        **VA0**    [0, 588]    [589, 1021]     [1022, 1476]    [1477, 1800]
\        **VA1**    [1, 589]    [590, 1022]     [1023, 1477]    [1478, 1801]
class3a  **V**      [0, 589]    [589, 1022]     [1022, 1477]    [1477, 1801]
\        **VA0**    [0, 588]    [589, 1021]     [1022, 1476]    [1477, 1800]
\        **VA1**    [1, 589]    [590, 1022]     [1023, 1477]    [1478, 1801]
class3b  **V**      [0, 589]    [589, 1022]     [1022, 1477]    [1477, 1801]
\        **VA0**    [0, 588]    [589, 1021]     [1022, 1476]    [1477, 1800]
\        **VA1**    [1, 589]    [590, 1022]     [1023, 1477]    [1478, 1801]
=======  ========   ========    ===========     ============    ============


Checksums
---------

As computed by :func:`wltp.cycles.crc_velocity()`,
reported by :func:`wltp.cycles.cycle_checksums()`, and
identified back by :func:`wltp.cycles.identify_cycle_v_crc`:

=======  =========  =====  ======  ====  ====  ====  ====  ========  ===========
\                   CRC32                                  SUM
------------------  -------------------------------------  ---------------------
\                   by_phase             cummulative       by_phase  cummulative
------------------  -------------------  ----------------  --------  -----------
*class*  *part*     *V*    *A0*    *A1*  *V*   *A0*  *A1*  *V*       *V*
=======  =========  =====  ======  ====  ====  ====  ====  ========  ===========
class1   **part1**  9840   4438    97DB  9840  4438  97DB  11988.4   11988.4
\        **part2**  8C34   8C8D    D9E8  DCF2  90BE  4295  17162.8   29151.2
\        **part3**  9840   9840    97DB  6D1D  6D1D  F523  11988.4   41139.6
class2   **part1**  8591   CDD1    8A0A  8591  CDD1  8A0A  11162.2   11162.2
\        **part2**  312D   391A    64F1  A010  606E  3E77  17054.3   28216.5
\        **part3**  81CD   E29E    9560  28FB  9261  D162  24450.6   52667.1
\        **part4**  8994   8994    2181  474B  474B  F70F  28869.8   81536.9
class3a  **part1**  48E5   910C    477E  48E5  910C  477E  11140.3   11140.3
\        **part2**  1494   D93B    4148  403D  2487  DE5A  16995.7   28136.0
\        **part3**  8B3B   9887    9F96  D770  3F67  2EE9  25646.0   53782.0
\        **part4**  F962   F962    5177  9BCE  9BCE  2B8A  29714.9   83496.9
class3b  **part1**  48E5   910C    477E  48E5  910C  477E  11140.3   11140.3
\        **part2**  AF1D   E501    FAC1  FBB4  18BD  65D3  17121.2   28261.5
\        **part3**  15F6   A779    15B8  43BC  B997  BA25  25782.2   54043.7
\        **part4**  F962   F962    5177  639B  639B  D3DF  29714.9   83758.6
=======  =========  =====  ======  ====  ====  ====  ====  ========  ===========


.. _begin-contribute:

Getting Involved
================
This project is hosted in **github**.
To provide feedback about bugs and errors or questions and requests for enhancements,
use `github's Issue-tracker <https://github.com/JRCSTU/wltp/issues>`_.

Development procedure
---------------------
For submitting code, use ``UTF-8`` everywhere, unix-eol(``LF``) and set ``git --config core.autocrlf = input``.

The typical development procedure is like this:

0. Install and arm a `pre-commit hook <https://github.com/pre-commit/pre-commit-hooks>`_
   with *black* to auto-format you python-code.

1. Modify the sources in small, isolated and well-defined changes, i.e.
   adding a single feature, or fixing a specific bug.

2. Add test-cases "proving" your code.

3. Rerun all test-cases to ensure that you didn't break anything,
   and check their *coverage* remain above the limit set in :file:`setup.cfg`.

4. If you made a rather important modification, update also the :doc:`CHANGES` file and/or
   other documents (i.e. README.rst).  To see the rendered results of the documents,
   issue the following commands and read the result html at :file:`build/sphinx/html/index.html`:

   .. code-block:: shell

        python setup.py build_sphinx                  # Builds html docs
        python setup.py build_sphinx -b doctest       # Checks if python-code embeded in comments runs ok.

5. If there are no problems, commit your changes with a descriptive message.

6. Repeat this cycle for other bugs/enhancements.
7. When you are finished, push the changes upstream to *github* and make a *merge_request*.
   You can check whether your merge-request indeed passed the tests by checking
   its build-status |travis-status| on the integration-server's site (TravisCI).

   .. Hint:: Skim through the small IPython developer's documentantion on the matter:
        `The perfect pull request <https://github.com/ipython/ipython/wiki/Dev:-The-perfect-pull-request>`_


.. _dev-team:

Development team
----------------

* Author:
    * Kostis Anagnostopoulos
* Contributing Authors:
    * Heinz Steven (test-data, validation and review)
    * Georgios Fontaras (simulation, physics & engineering support)
    * Alessandro Marotta (policy support)
    * Jelica Pavlovic (policy support)
    * Eckhard Schlichte (discussions & advice)


.. _begin-glossary:

Glossary
========
See also :ref:`architecture:Architecture`.

.. default-role:: term

.. glossary::

    WLTP
        The `Worldwide harmonised Light duty vehicles Test Procedure <https://www2.unece.org/wiki/pages/viewpage.action?pageId=2523179>`_,
        a `GRPE` informal working group

    UNECE
        The United Nations Economic Commission for Europe, which has assumed the steering role
        on the `WLTP`.

    GRPE
        `UNECE` Working party on Pollution and Energy - Transport Programme

    GTR
        Any of the *Global Technical Regulation* documents of the `WLTP` .

    GS Task-Force
        The Gear-shift Task-force of the `GRPE`. It is the team of automotive experts drafting
        the gear-shifting strategy for vehicles running the `WLTP` cycles.

    WLTC
        The family of pre-defined *driving-cycles* corresponding to vehicles with different
        :abbr:`PMR (Power to Mass Ratio)`. Classes 1,2, 3a/b are split in 3, 4 and 4 *parts* respectively.

    AccDB
    MS Access DB
        The original implementation of the algorithm in *MS Access* by Heinz Steven.

        To facilitate searching and cross-referencing the existing routines,
        all the code & queries of the database have been extracted and stored in as text
        under the `Notebooks/AccDB_src/
        <https://github.com/JRCSTU/wltp/tree/master/Notebooks/AccDB_src/>`_ folder
        of this project.

    MRO
    Mass in running order
        The mass of the vehicle, with its fuel tank(s) filled to at least 90 per cent
        of its or their capacity/capacities, including the mass of the driver and the liquids,
        fitted with the standard equipment in accordance with the manufacturer’s specifications and,
        where they are fitted, the mass of the bodywork, the cabin,
        the coupling and the spare wheel(s) as well as the tools when they are fitted.

    UM
    Kerb mass
    Curb weight
    Unladen mass
        The `Mass in running order` minus the `Driver mass`.

    Driver weight
    Driver mass
        75 kgr

    TM
    Test mass
        The representative weight of the vehicle used as input for the calculations of the simulation,
        derived by interpolating between high and low values for the |CO2|-family of the vehicle.

    Downscaling
        Reduction of the top-velocity of the original drive trace to be followed, to ensure that the vehicle
        is not driven in an unduly high proportion of "full throttle".

    JSON-schema
        The `JSON schema <http://json-schema.org/>`_ is an `IETF draft <http://tools.ietf.org/html/draft-zyp-json-schema-03>`_
        that provides a *contract* for what JSON-data is required for a given application and how to interact
        with it.  JSON Schema is intended to define validation, documentation, hyperlink navigation, and
        interaction control of JSON data.

        The schema of this project has its own section: :ref:`code:Schema`

        You can learn more about it from this `excellent guide <http://spacetelescope.github.io/understanding-json-schema/>`_,
        and experiment with this `on-line validator <http://www.jsonschema.net/>`_.

    JSON-pointer
        JSON Pointer(:rfc:`6901`) defines a string syntax for identifying a specific value within
        a JavaScript Object Notation (JSON) document. It aims to serve the same purpose as *XPath* from the XML world,
        but it is much simpler.

    sphinx
        The text-oriented language, a superset of `Restructured Text <https://en.wikipedia.org/wiki/ReStructuredText>`_,
        used to write the documentation for this project, with simlar capabilities to *LaTeX*,
        but for humans, e.g.,  the Linux kernel adopted this textual format on 2016.
        http://sphinx-doc.org/

    notebook
    jupyter notebook
    Jupyter
        *Jupyter* is a web-based interactive computational environment for creating *Jupyter notebook* documents.
        The "notebook" term can colloquially make reference to many different entities,
        mainly the Jupyter web application, Jupyter Python web server, or Jupyter document format,
        depending on context.

        A *Jupyter Notebook* document is composed of an ordered list of input/output *cells*
        which contain code in variou languages, text (using Markdown), mathematics, plots and
        rich media, usually ending with the ".ipynb" extension.

.. _begin-replacements:

.. |br| raw:: html

   <br />

.. |CO2| replace:: CO\ :sub:`2`

.. |virtualenv| replace::  *virtualenv* (isolated Python environment)
.. _virtualenv: http://docs.python-guide.org/en/latest/dev/virtualenvs/

.. |binder| image:: https://mybinder.org/badge_logo.svg
    :target: https://mybinder.org/v2/gh/JRCSTU/wltp/master?urlpath=lab/tree/Notebooks/README.md
    :alt: JupyterLab for WLTP

.. |pypi| replace:: *PyPi* repo
.. _pypi: https://pypi.python.org/pypi/wltp

.. |winpython| replace:: *WinPython*
.. _winpython: http://winpython.github.io/

.. |anaconda| replace:: *Anaconda*
.. _anaconda: http://docs.continuum.io/anaconda/

.. |travis-status| image:: https://travis-ci.org/JRCSTU/wltp.svg
    :alt: Travis continuous integration testing ok? (Linux)
    :scale: 100%
    :target: https://travis-ci.org/JRCSTU/wltp/builds

.. |appveyor-status| image:: https://ci.appveyor.com/api/projects/status/0e2dcudyuku1w1gd?svg=true
    :alt: Apveyor continuous integration testing ok? (Windows)
    :scale: 100%
    :target: https://ci.appveyor.com/project/JRCSTU/wltp

.. |cover-status| image:: https://coveralls.io/repos/JRCSTU/wltp/badge.png?branch=master
    :target: https://coveralls.io/r/JRCSTU/wltp?branch=master

.. |docs-status| image:: https://readthedocs.org/projects/wltp/badge/
    :alt: Documentation status
    :scale: 100%
    :target: https://readthedocs.org/projects/wltp/builds/

.. |gh-version| image::  https://img.shields.io/github/v/release/JRCSTU/wltp.svg?label=GitHub%20release&include_prereleases
    :target: https://github.com/JRCSTU/wltp/releases
    :alt: Latest version in GitHub

.. |pypi-version| image::  https://img.shields.io/pypi/v/wltp.svg?label=PyPi%20version
    :target: https://pypi.python.org/pypi/wltp/
    :alt: Latest version in PyPI

.. |conda-version| image::  https://img.shields.io/conda/v/ankostis/wltp?label=conda%20version
    :target: https://anaconda.org/ankostis/wltp
    :alt: Latest version in Anaconda cloud

.. |python-ver| image:: https://img.shields.io/pypi/pyversions/wltp.svg?label=PyPi%20Python
    :target: https://pypi.python.org/pypi/wltp/
    :alt: Supported Python versions of latest release in PyPi

.. |conda-plat| image:: https://img.shields.io/conda/pn/ankostis/wltp.svg?label=conda%20platforms
    :target: https://anaconda.org/ankostis/wltp
    :alt: Supported conda platforms

.. |dev-status| image:: https://pypip.in/status/wltp/badge.svg
    :target: https://pypi.python.org/pypi/wltp/
    :alt: Development Status

.. |downloads-count| image:: https://pypip.in/download/wltp/badge.svg?period=month&label=PyPi%20downloads
    :target: https://pypi.python.org/pypi/wltp/
    :alt: PyPi downloads

.. |codestyle| image:: https://img.shields.io/badge/code%20style-black-black.svg
    :target: https://github.com/ambv/black
    :alt: Code Style

.. |gh-watch| image:: https://img.shields.io/github/watchers/JRCSTU/wltp.svg?style=social
    :target: https://github.com/JRCSTU/wltp
    :alt: Github watchers

.. |gh-star| image:: https://img.shields.io/github/stars/JRCSTU/wltp.svg?style=social
    :target: https://github.com/JRCSTU/wltp
    :alt: Github stargazers

.. |gh-fork| image:: https://img.shields.io/github/forks/JRCSTU/wltp.svg?style=social
    :target: https://github.com/JRCSTU/wltp
    :alt: Github forks

.. |gh-issues| image:: http://img.shields.io/github/issues/JRCSTU/wltp.svg?style=social
    :target: https://github.com/JRCSTU/wltp/issues
    :alt: Issues count

.. |proj-lic| image:: https://img.shields.io/pypi/l/wltp.svg
    :target:  https://joinup.ec.europa.eu/software/page/eupl
    :alt: EUPL 1.1+
