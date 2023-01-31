import os
import shutil

from yamanifest import Manifest as Yamanifest

import pytest

from morte.models.base import YAMANIFEST_HASH
from morte.models.test import OUTPUT_FILES, ReproducibilityInfo


def make_random_binary_file(fname, size):
    """Stolen from
    https://github.com/aidanheerdegen/yamanifest/blob/master/test/test_manifest.py
    """
    numbytes = 1024
    randombytes = os.urandom(numbytes)
    pos = 0
    with open(fname, "wb") as fout:
        while pos < size:
            fout.write(randombytes)
            pos += numbytes
        fout.truncate(size)


class TestReproducibility:
    @pytest.fixture(autouse=True)
    def setup(self, tmp_path_factory):
        """Set up some temporary files to test against"""

        self.base_dir = tmp_path_factory.mktemp("outputs")
        self.output_files = OUTPUT_FILES

        # Output directory
        path = self.base_dir
        for file in self.output_files:
            filepath = path / file
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            make_random_binary_file(filepath, 20 * 1024 * 1024)

        # Reference directory with same data
        self.reference_dir_same = tmp_path_factory.mktemp("references_same")
        path = self.reference_dir_same
        mf = Yamanifest(path / "manifest.yaml", [YAMANIFEST_HASH])
        for file in self.output_files:
            filepath = path / file
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            shutil.copy(self.base_dir / file, os.path.dirname(filepath))
            mf.add(filepaths=str(file), fullpaths=str(filepath))
        mf.dump()

        # Reference directory with different data
        self.reference_dir_diff = tmp_path_factory.mktemp("references_diff")
        path = self.reference_dir_diff
        mf = Yamanifest(path / "manifest.yaml", [YAMANIFEST_HASH])
        for file in self.output_files:
            filepath = path / file
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            make_random_binary_file(filepath, 20 * 1024 * 1024)
            mf.add(filepaths=str(file), fullpaths=str(filepath))
        mf.dump()

        # Reference directory with missing data
        self.reference_dir_missing = tmp_path_factory.mktemp("references_missing")
        path = self.reference_dir_missing
        mf = Yamanifest(path / "manifest.yaml", [YAMANIFEST_HASH])
        for file in self.output_files[:-1]:
            filepath = path / file
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            shutil.copy(self.base_dir / file, os.path.dirname(filepath))
            mf.add(filepaths=str(file), fullpaths=str(filepath))
        mf.dump()

        # Reference directory with no data
        self.reference_dir_empty = tmp_path_factory.mktemp("references_empty")
        mf = Yamanifest(path / "manifest.yaml", [YAMANIFEST_HASH])

        # Non-Existent Manifest file
        self.nonexistent_manifest = path / "manifest.yaml"

    def test_no_change(self):
        """
        Test case where the output and reference directories contain the same files
        """
        ri = ReproducibilityInfo(
            self.base_dir,
            self.reference_dir_same,
            str(self.reference_dir_same / "manifest.yaml"),
        )
        differences = ri.compare()
        assert not differences

    def test_all_changed(self):
        """
        Test case where the reference data has changed relative to the output data
        """
        ri = ReproducibilityInfo(
            self.base_dir,
            self.reference_dir_diff,
            str(self.reference_dir_diff / "manifest.yaml"),
        )
        differences = ri.compare()
        assert set(differences) == set(self.output_files)

        # Update the reference for the files that are different
        ri.update_reference(differences)
        differences = ri.compare()
        assert not differences
