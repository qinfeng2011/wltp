#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2013-2019 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl


def goodVehicle():
    from wltp import datamodel

    goodVehicle = {
        "test_mass": 1500,
        "p_rated": 100,
        "n_rated": 5450,
        "n_idle": 950,
        # "n_min":   None,    # Can be overriden by manufacturer.
        "gear_ratios": [120.5, 75, 50, 43, 37, 32],
    }
    goodVehicle = datamodel.upd_default_load_curve(goodVehicle)

    return goodVehicle
