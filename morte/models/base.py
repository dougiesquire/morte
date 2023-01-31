# Copyright 2022 ACCESS-NRI and contributors. See the top-level COPYRIGHT file for details.
# SPDX-License-Identifier: Apache-2.0

"""
Generic model class, primarily to be inherited by other models.
"""

import os
import shutil
import logging

from yamanifest.manifest import Manifest as Yamanifest

logger = logging.getLogger(__name__)
log_handler = logging.StreamHandler()
log_handler.setLevel(logging.INFO)
log_format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
log_handler.setFormatter(log_format)
logger.addHandler(log_handler)

YAMANIFEST_HASH = "binhash-nomtime"


class BaseReproducibilityInfo:
    """
    Generic class for keeping track of checksums/hashes of model output files
    """

    def __init__(self, base_dir, reference_dir, reference_file):
        """
        Initialise a BaseReproducibilityInfo object.

        Parameters
        ----------
        base_dir : str
            Path to base directory of the model test experiment
        reference_dir : str
            Path to directory containing reference datasets (often called "Known Good Outputs")
        reference_file : str
            Path to yamanifest file containing hashes/checksums of reference datasets
        """

        self.base_dir = base_dir
        self.reference_dir = reference_dir
        self.reference_file = reference_file

        self.output_files = []

        # Make sure directories exists
        os.makedirs(self.reference_dir, exist_ok=True)
        os.makedirs(os.path.dirname(self.reference_file), exist_ok=True)

        # Initialise the reference and current manifests
        self.reference_manifest = Yamanifest(self.reference_file, [YAMANIFEST_HASH])
        self.current_manifest = Yamanifest(None, [YAMANIFEST_HASH])

    def setup(self):
        # Set up the reference manifest
        if os.path.isfile(self.reference_file):
            has_reference_file = True
            self.reference_manifest.load()
        else:
            has_reference_file = False

        # Make sure all reference files ("KGO"s) exist
        outputs_missing_references = [
            output
            for output in self.output_files
            if not os.path.isfile(os.path.join(self.reference_dir, output))
        ]
        if outputs_missing_references:
            logger.warning(
                "Not all reference files exist. Copying from current model output"
            )
            self.update_reference(
                outputs_missing_references, update_manifest=has_reference_file
            )

        if not has_reference_file:
            logger.warning(
                "Manifest file does not exist. Generating manifest from reference files"
            )
            self.reference_manifest.add(
                filepaths=self.output_files,
                fullpaths=[
                    os.path.join(self.reference_dir, output)
                    for output in self.output_files
                ],
            )

        # Set up the current manifest
        self.current_manifest.add(
            filepaths=self.output_files,
            fullpaths=[
                os.path.join(self.base_dir, output) for output in self.output_files
            ],
        )

    def update_reference(self, output_files=None, update_manifest=True):
        """
        Update the reference files and manifest. I.e. copy output files to the reference
        directory and optionally update the reference manifest for these new files. Overwrite
        files that already exists.

        Parameters
        ----------
        output_files: list or str or None, optional
            The output files to update. If None, update for all filepaths in the current manifest
        update_manifest: boolean, optional
            Whether or not to update the reference manifest
        """

        if output_files is None:
            output_files = self.current_manifest.data.keys()
        else:
            if type(output_files) is str:
                output_files = [
                    output_files,
                ]

        outputs = [os.path.join(self.base_dir, output) for output in output_files]
        references = [
            os.path.join(self.reference_dir, output) for output in output_files
        ]

        for output, reference in zip(outputs, references):
            logger.info(f"(Over)writing reference file: {reference}")
            if os.path.isfile(output):
                os.makedirs(os.path.dirname(reference), exist_ok=True)
                shutil.copy(output, reference)
            else:
                logger.warning(f"Output file {output} does not exists")

        if update_manifest:
            self.update_manifest(output_files=output_files)

    def update_manifest(self, output_files=None):
        """
        Update the reference manifest for the specified output files.

        Parameters
        ----------
        output_files: list or str or None, optional
            The output files to update. If None, update for all filepaths in the current manifest
        """

        if output_files is None:
            output_files = self.current_manifest.data.keys()
        else:
            if type(output_files) is str:
                output_files = [
                    output_files,
                ]

        references = [
            os.path.join(self.reference_dir, output) for output in output_files
        ]
        self.reference_manifest.add(
            filepaths=output_files, fullpaths=references, force=True
        )

    def compare(self):
        """
        Compare current and reference manifests and return list of files with differing hashes
        """

        if isinstance(self.reference_manifest, self.current_manifest.__class__):
            different = []
            for file in self.current_manifest:
                for fn, val in self.current_manifest.data[file]["hashes"].items():
                    if fn not in self.reference_manifest.data[file]["hashes"]:
                        different.append(file)
                    if self.reference_manifest.data[file]["hashes"][fn] != val:
                        different.append(file)
            return different
        else:
            return NotImplemented

    def dump(self):
        """
        Dump the reference manifest from yaml file.
        """
        self.reference_manifest.dump()


class BasePerformanceInfo:
    """
    Generic class for keeping track of performance information parsed from model output
    """

    def __init__(self, base_dir, reference_file):
        """
        Initialise a BasePerformanceInfo object.

        Parameters
        ----------
        base_dir : str
            Path to base directory of the model test experiment
        reference_file : str
            Path to yaml file containing reference performance information
        """
        self.base_dir = base_dir
        self.reference_file = reference_file

        self.PBS_output_file = "*.o*"

    def setup(self):
        self.parse_PBS_info()
        self.parse_info()

    def parse_PBS_info(self):
        """
        Parse basic information from the PBS output file summary
        """
        pass

    def parse_info(self):
        """
        Model-specific code to parse info into dictionary
        """
        pass
