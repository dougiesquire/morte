"""
Interface for testing model classes
"""

from .base import BaseFileManifest

REPRO_OUTPUT_FILES = ["foo/file1", "bar/file2"]  # Must have at least two files


class ReproducibilityInfo(BaseFileManifest):
    def __init__(self, base_dir, reference_dir, manifest_file):
        super().__init__(base_dir, reference_dir, manifest_file)

        self.output_files = REPRO_OUTPUT_FILES

        self.setup()
