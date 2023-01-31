import os
import shutil

import pytest

from yamanifest import Manifest as Yamanifest

from morte.models.base import YAMANIFEST_HASH
from morte.models.test import REPRO_OUTPUT_FILES


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


@pytest.fixture(scope="session")
def base_dir(tmp_path_factory):
    """Output directory for reproducibility testing"""
    base_dir = tmp_path_factory.mktemp("output")
    for file in REPRO_OUTPUT_FILES:
        os.makedirs(os.path.dirname(base_dir / file), exist_ok=True)
        make_random_binary_file(base_dir / file, 20 * 1024 * 1024)
    return base_dir


@pytest.fixture(scope="session")
def reference_dir_same(tmp_path_factory, base_dir):
    """Reference directory and manifest with same data as output directory"""
    reference_dir = tmp_path_factory.mktemp("references_same")
    mf = Yamanifest(reference_dir / "manifest.yaml", [YAMANIFEST_HASH])
    for file in REPRO_OUTPUT_FILES:
        filepath = reference_dir / file
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        shutil.copy(base_dir / file, os.path.dirname(filepath))
        mf.add(filepaths=str(file), fullpaths=str(filepath))
    mf.dump()
    return base_dir, reference_dir


@pytest.fixture(scope="session")
def reference_dir_diff(tmp_path_factory, base_dir):
    """Reference directory and manifest with different data to output directory"""
    reference_dir = tmp_path_factory.mktemp("references_diff")
    mf = Yamanifest(reference_dir / "manifest.yaml", [YAMANIFEST_HASH])
    for file in REPRO_OUTPUT_FILES:
        filepath = reference_dir / file
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        make_random_binary_file(filepath, 20 * 1024 * 1024)
        mf.add(filepaths=str(file), fullpaths=str(filepath))
    mf.dump()
    return base_dir, reference_dir


@pytest.fixture(scope="session")
def reference_dir_missing(tmp_path_factory, base_dir):
    """Reference directory and manifest with missing data relative to output directory"""
    reference_dir = tmp_path_factory.mktemp("references_missing")
    mf = Yamanifest(reference_dir / "manifest.yaml", [YAMANIFEST_HASH])
    for file in REPRO_OUTPUT_FILES[:-1]:
        filepath = reference_dir / file
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        shutil.copy(base_dir / file, os.path.dirname(filepath))
        mf.add(filepaths=str(file), fullpaths=str(filepath))
    mf.dump()
    return base_dir, reference_dir


@pytest.fixture(scope="session")
def reference_dir_empty(tmp_path_factory, base_dir):
    """Reference directory and manifest with no data"""
    reference_dir = tmp_path_factory.mktemp("references_empty")
    mf = Yamanifest(reference_dir / "manifest.yaml", [YAMANIFEST_HASH])
    mf.dump()
    return base_dir, reference_dir
