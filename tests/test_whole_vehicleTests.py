#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2013-2019 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl
"""Tests check top-level functionality. """

import logging
import os, io
import pickle
import tempfile
import unittest

from matplotlib import pyplot as plt

import numpy as np
import numpy.testing as npt

from wltp.experiment import Experiment
from .goodvehicle import goodVehicle


log = logging.getLogger(__name__)

driver_weight = 70
"For calculating unladen_mass."


class ExperimentWholeVehs(unittest.TestCase):
    def setUp(self):
        logging.basicConfig(level=logging.DEBUG)
        self.run_comparison = (
            True
        )  # NOTE: Set once to False to UPDATE sample-results (assuming they are ok).

    def _compare_exp_results(self, tabular, fname, run_comparison):
        tmpfname = os.path.join(tempfile.gettempdir(), "%s.pkl" % fname)
        if run_comparison:
            try:
                with io.open(tmpfname, "rb") as tmpfile:
                    data_prev = pickle.load(tmpfile)
                    ## Compare changed-tabular
                    #
                    npt.assert_array_equal(tabular["gears"], data_prev["gears"])
                    # Unreached code in case of assertion.
                    # cmp = tabular['gears'] != data_prev['gears']
                    # if (cmp.any()):
                    #     self._plotResults(data_prev)
                    #     print('>> COMPARING(%s): %s'%(fname, cmp.nonzero()))
                    # else:
                    #     print('>> COMPARING(%s): OK'%fname)
            except (FileNotFoundError, ValueError) as ex:  # @UnusedVariable
                print(
                    ">> COMPARING(%s): No old-tabular found, 1st time to be stored in: "
                    % fname,
                    tmpfname,
                )
                run_comparison = False

        if not run_comparison:
            with io.open(tmpfname, "wb") as tmpfile:
                pickle.dump(tabular, tmpfile)

    def _plotResults(self, mdl):
        cycle = mdl["cycle"]
        gears = cycle["gears"]
        target = cycle["v_target"]
        realv = cycle["v_real"]
        clutch = cycle["clutch"]

        clutch = clutch.nonzero()[0]
        plt.vlines(clutch, 0, 40)
        plt.plot(target)
        plt.plot(gears * 12, "+")
        plt.plot(realv)

    def testGoodVehicle(self, plot_results=False):
        logging.getLogger().setLevel(logging.DEBUG)

        mdl = goodVehicle()

        experiment = Experiment(mdl)
        mdl = experiment.run()
        self.assertTrue("cycle" in mdl, 'No result "cycle" in Model: %s' % mdl)

        print("DRIVEABILITY: \n%s" % experiment.driveability_report())
        cycle = mdl["cycle"]
        gears = cycle["gears"]
        print(
            "G1: %s, G2: %s"
            % (np.count_nonzero(gears == 1), np.count_nonzero(gears == 2))
        )

        self._compare_exp_results(cycle, "goodveh", self.run_comparison)

        if plot_results:
            print(mdl["cycle"])
            # print([get_wltc_data()['classes']['class3b']['cycle'][k] for k in mdl['cycle']['driveability_issues'].keys()])
            self._plotResults(mdl)

            np.set_printoptions(edgeitems=16)
            # print(driveability_issues)
            # print(v_max)
            # results['target'] = []; print(results)
            plt.show()

    def testUnderPowered(self, plot_results=False):
        mdl = goodVehicle()
        mdl["vehicle"]["p_rated"] = 50

        experiment = Experiment(mdl)
        mdl = experiment.run()
        print("DRIVEABILITY: \n%s" % experiment.driveability_report())
        self._compare_exp_results(mdl["cycle"], "unpower1", self.run_comparison)

        mdl = goodVehicle()
        veh = mdl["vehicle"]
        veh["test_mass"] = 1000
        veh["unladen_mass"] = veh["test_mass"] - driver_weight
        veh["p_rated"] = 80
        veh["v_max"] = 120
        veh["gear_ratios"] = [120.5, 95, 72, 52]

        experiment = Experiment(mdl)
        mdl = experiment.run()
        print("DRIVEABILITY: \n%s" % experiment.driveability_report())
        self._compare_exp_results(mdl["cycle"], "unpower2", self.run_comparison)

        if plot_results:
            self._plotResults(mdl)
            plt.show()


if __name__ == "__main__":
    import sys

    # sys.argv = ['', 'Test.testName']
    unittest.main(argv=sys.argv[1:])
