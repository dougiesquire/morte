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


class BaseFileManifest:
    """
    Generic class for keeping track of checksums/hashes of model output files
    """

    def __init__(self, base_dir, reference_dir, manifest_file):
        """
        Initialise a BaseFileManifest object

        Parameters
        ----------
        base_dir : str
            Path to base directory of the model test experiment
        reference_dir : str
            Path to directory containing reference datasets (often called Known Good Outputs)
        manifest_file : str
            Path to manifest file containing hashes/checksums of reference datasets
        """

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

        # Initialise the reference and latest manifests
        self.reference_manifest = YaManifest(self.manifest_file, ["binhash"])

        if os.path.isfile(self.manifest_file):
            self.reference_manifest.load()
        else:
            logger.warning(
                "Manifest file does not exist. Generating one from reference files"
            )
            self.reference_manifest.add(
                filepaths=self.output_files, fullpaths=self.reference_files
            )
            self.reference_manifest.dump()

        # Initialise the manifest for the current experiment
        self.current_manifest = YaManifest(None, ["binhash"])
        self.current_manifest.add(
            filepaths=self.output_files,
            fullpaths=[
                os.path.join(self.base_dir, output) for output in self.output_files
            ],
        )

    def update_reference(self, output_file):
        """
        Copy an output file to the reference directory. Overwrite if the file already
        exists
        """

        logger.info(f"(Over)writing reference file for {output_file}")

        output_file_full = os.path.join(self.base_dir, output_file)
        reference_file = os.path.join(self.reference_dir, output_file)

        if os.path.isfile(output_file_full):
            os.makedirs(os.path.dirname(reference_file), exist_ok=True)
            shutil.copy(output_file_full, reference_file)
        else:
            logger.warning(f"Output file {output_file} does not exists")

    def compare(self):
        """Compare reference and current manifests"""

        return self.current_manifest.equals(self.reference_manifest, paths=False)

    def dump(self):
        """Dump reference manifest to yaml file"""

        self.reference_manifest.dump()


class BaseInfo:
    """
    Generic class for keeping track of information parsed from model output
    """

    def __init__(self, base_dir, reference_file):
        self.base_dir = base_dir
        self.reference_file = reference_file
