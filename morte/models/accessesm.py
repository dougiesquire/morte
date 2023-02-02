# Copyright 2022 ACCESS-NRI and contributors. See the top-level COPYRIGHT file for details.
# SPDX-License-Identifier: Apache-2.0

"""
Interface for the ACCESS-ESM model
"""

import os

from .base import BasePerformanceInfo, BaseReproducibilityInfo
from ..parse import YamlFile


class PerformanceInfo(BasePerformanceInfo):
    def __init__(self, base_dir, reference_file):
        super().__init__(base_dir, reference_file)

        # Payu config contains some useful info
        config = YamlFile(os.path.join(self.base_dir, "config.yaml"))
        jobname = config.get("jobname")

        if jobname:
            self.pbs_output_file = f"{jobname}.o*"
        else:
            self.pbs_output_file = "*.o*"

        self.setup()

    def parse_info(self):
        pass


class ReproducibilityInfo(BaseReproducibilityInfo):
    def __init__(self, base_dir, reference_dir, manifest_file):
        super().__init__(base_dir, reference_dir, manifest_file)

        self.output_files = [
            "archive/restart000/atmosphere/restart_dump.astart",
            "archive/restart000/coupler/a2i.nc",
            "archive/restart000/coupler/i2a.nc",
            "archive/restart000/coupler/o2i.nc",
            "archive/restart000/ice/iced.01020101",
            "archive/restart000/ice/mice.nc",
            "archive/restart000/ocean/csiro_bgc.res.nc",
            "archive/restart000/ocean/csiro_bgc_sediment.res.nc",
            "archive/restart000/ocean/ocean_age.res.nc",
            "archive/restart000/ocean/ocean_barotropic.res.nc",
            "archive/restart000/ocean/ocean_bih_friction.res.nc",
            "archive/restart000/ocean/ocean_density.res.nc",
            "archive/restart000/ocean/ocean_frazil.res.nc",
            "archive/restart000/ocean/ocean_lap_friction.res.nc",
            "archive/restart000/ocean/ocean_neutral.res.nc",
            "archive/restart000/ocean/ocean_pot_temp.res.nc",
            "archive/restart000/ocean/ocean_sbc.res.nc",
            "archive/restart000/ocean/ocean_sigma_transport.res.nc",
            "archive/restart000/ocean/ocean_solo.res",
            "archive/restart000/ocean/ocean_temp_salt.res.nc",
            "archive/restart000/ocean/ocean_thickness.res.nc",
            "archive/restart000/ocean/ocean_tracer.res",
            "archive/restart000/ocean/ocean_velocity_advection.res.nc",
            "archive/restart000/ocean/ocean_velocity.res.nc",
        ]

        self.setup()
