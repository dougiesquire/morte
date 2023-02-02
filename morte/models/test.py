# Copyright 2022 ACCESS-NRI and contributors. See the top-level COPYRIGHT file for details.
# SPDX-License-Identifier: Apache-2.0

"""
Interface for testing model classes
"""

from .base import BasePerformanceInfo, BaseReproducibilityInfo

REPRO_OUTPUT_FILES = ["foo/file1", "bar/file2"]  # Must have at least two files
PBS_OUTPUT_FILE = "pbs.output"


class PerformanceInfo(BasePerformanceInfo):
    def __init__(self, base_dir, reference_file):
        super().__init__(base_dir, reference_file)

        self.PBS_output_file = PBS_OUTPUT_FILE

        self.setup()


class ReproducibilityInfo(BaseReproducibilityInfo):
    def __init__(self, base_dir, reference_dir, manifest_file):
        super().__init__(base_dir, reference_dir, manifest_file)

        self.output_files = REPRO_OUTPUT_FILES

        self.setup()
