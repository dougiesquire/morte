"""
Generic model class, primarily to be inherited by other models.
"""

import os
import shutil
import logging

from yamanifest.manifest import Manifest as YaManifest

logger = logging.getLogger(__name__)
log_handler = logging.StreamHandler()
log_handler.setLevel(logging.INFO)
log_format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
log_handler.setFormatter(log_format)
logger.addHandler(log_handler)


class BaseFileManifest(YaManifest):
    """
    Generic class for keeping track of checksums/hashes of model output files
    """

    def __init__(self, base_dir, reference_dir, manifest_file):

        super().__init__(manifest_file, ["binhash"])

        self.base_dir = base_dir
        self.reference_dir = reference_dir
        self.manifest_file = manifest_file

        self.output_files = []

    def setup(self):

        # Make sure directories exists
        os.makedirs(self.reference_dir, exist_ok=True)
        os.makedirs(os.path.dirname(self.manifest_file), exist_ok=True)
        self.reference_files = [
            os.path.join(self.reference_dir, output) for output in self.output_files
        ]

        # Make sure all reference files ("KGO"s) exist
        self.outputs_missing_references = [
            output
            for output in self.output_files
            if not os.path.isfile(os.path.join(self.reference_dir, output))
        ]
        if self.outputs_missing_references:
            logger.warning(
                "Not all reference files exist. Copying from current model output"
            )
            for output in self.outputs_missing_references:
                self.update_reference(output)

        # Initialise the reference manifest
        if os.path.isfile(self.manifest_file):
            self.load()
        else:
            logger.warning(
                "Manifest file does not exist. Generating one from reference files"
            )
            self.add(filepaths=self.output_files, fullpaths=self.reference_files)
            self.dump()

    def compare(self):
        """Compare hashes"""

    def update_reference(self, output_file):

        logger.info(f"(Over)writing reference file for {output_file}")

        output_file_full = os.path.join(self.base_dir, output_file)
        reference_file = os.path.join(self.reference_dir, output_file)

        if os.path.isfile(output_file_full):
            os.makedirs(os.path.dirname(reference_file), exist_ok=True)
            shutil.copy(output_file_full, reference_file)
        else:
            logger.warning(f"Output file {output_file} does not exists")


class BaseInfo:
    """
    Generic class for keeping track of information parsed from model output
    """

    def __init__(self, base_dir, reference_file):
        self.base_dir = base_dir
        self.reference_file = reference_file
