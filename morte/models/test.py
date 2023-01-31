"""
Interface for testing base classes
"""

from .base import BaseInfo, BaseFileManifest

OUTPUT_FILES = ["foo/file1", "bar/file2"]


class PerformanceInfo(BaseInfo):
    def __init__(self, base_dir, reference_file=None):
        super().__init__(base_dir, reference_file)


class ReproducibilityInfo(BaseFileManifest):
    def __init__(self, base_dir, reference_dir, manifest_file):
        super().__init__(base_dir, reference_dir, manifest_file)

        self.output_files = OUTPUT_FILES

        self.setup()
