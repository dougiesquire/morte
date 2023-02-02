# Copyright 2022 ACCESS-NRI and contributors. See the top-level COPYRIGHT file for details.
# SPDX-License-Identifier: Apache-2.0

import os
import shutil

import pytest

from yamanifest import Manifest as Yamanifest

from morte.models.base import YAMANIFEST_HASH
from morte.models.test import PBS_OUTPUT_FILE, REPRO_OUTPUT_FILES


def make_random_binary_file(fname, size):
    """
    Stolen from yamanifest
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
    """Output directory for testing"""
    base_dir = tmp_path_factory.mktemp("output")

    # Creat some test model output files
    for file in REPRO_OUTPUT_FILES:
        os.makedirs(os.path.dirname(base_dir / file), exist_ok=True)
        make_random_binary_file(base_dir / file, 20 * 1024 * 1024)

    # Create a test PBS summary
    example_summary = (
        "Some\n"
        "random\n"
        "text\n\n"
        "======================================================================================\n"
        "                  Resource Usage on 2022-11-17 10:08:57:\n"
        "   Job Id:             63911854.gadi-pbs\n"
        "   Project:            tm70\n"
        "   Exit Status:        0\n"
        "   Service Units:      123.45\n"
        "   NCPUs Requested:    234                    NCPUs Used: 123\n"
        "                                           CPU Time Used: 20:30:00\n"
        "   Memory Requested:   1.5TB                 Memory Used: 200GB\n"
        "   Walltime requested: 01:00:00            Walltime Used: 00:30:36\n"
        "   JobFS requested:    1.00KB                 JobFS used: 0.00MB\n"
        "======================================================================================\n"
    )
    with open(base_dir / PBS_OUTPUT_FILE, "w") as file:
        file.write(example_summary)
    return base_dir


@pytest.fixture(scope="session")
def repro_dirs_same(tmp_path_factory, base_dir):
    """Reference directory and manifest with same model output as output directory"""
    reference_dir = tmp_path_factory.mktemp("references_same")
    mf = Yamanifest(reference_dir / "kgo_manifest.yaml", [YAMANIFEST_HASH])
    for file in REPRO_OUTPUT_FILES:
        filepath = reference_dir / file
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        shutil.copy(base_dir / file, os.path.dirname(filepath))
        mf.add(filepaths=str(file), fullpaths=str(filepath))
    mf.dump()
    return base_dir, reference_dir


@pytest.fixture(scope="session")
def repro_dirs_diff(tmp_path_factory, base_dir):
    """Reference directory and manifest with different model output to output directory"""
    reference_dir = tmp_path_factory.mktemp("references_diff")
    mf = Yamanifest(reference_dir / "kgo_manifest.yaml", [YAMANIFEST_HASH])
    for file in REPRO_OUTPUT_FILES:
        filepath = reference_dir / file
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        make_random_binary_file(filepath, 20 * 1024 * 1024)
        mf.add(filepaths=str(file), fullpaths=str(filepath))
    mf.dump()
    return base_dir, reference_dir


@pytest.fixture(scope="session")
def repro_dirs_missing(tmp_path_factory, base_dir):
    """Reference directory and manifest with missing model output relative to output directory"""
    reference_dir = tmp_path_factory.mktemp("references_missing")
    mf = Yamanifest(reference_dir / "kgo_manifest.yaml", [YAMANIFEST_HASH])
    for file in REPRO_OUTPUT_FILES[:-1]:
        filepath = reference_dir / file
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        shutil.copy(base_dir / file, os.path.dirname(filepath))
        mf.add(filepaths=str(file), fullpaths=str(filepath))
    mf.dump()
    return base_dir, reference_dir


@pytest.fixture(scope="session")
def repro_dirs_empty(tmp_path_factory, base_dir):
    """Reference directory and manifest with no model output"""
    reference_dir = tmp_path_factory.mktemp("references_empty")
    return base_dir, reference_dir
