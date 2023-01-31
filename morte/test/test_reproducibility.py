import logging

from morte.models.test import REPRO_OUTPUT_FILES, ReproducibilityInfo


def test_no_change(repro_dirs_same):
    """
    Test case where the output and reference directories contain the same files
    """
    ri = ReproducibilityInfo(
        repro_dirs_same[0],
        repro_dirs_same[1],
        str(repro_dirs_same[1] / "manifest.yaml"),
    )
    differences = ri.compare()
    assert not differences


def test_all_changed(repro_dirs_diff):
    """
    Test case where the reference data has changed relative to the output data
    """
    ri = ReproducibilityInfo(
        repro_dirs_diff[0],
        repro_dirs_diff[1],
        str(repro_dirs_diff[1] / "manifest.yaml"),
    )
    differences = ri.compare()
    assert set(differences) == set(REPRO_OUTPUT_FILES)

    # Update only one of the references
    ri.update_reference(differences[:1])
    differences = ri.compare()
    assert set(differences) == set(REPRO_OUTPUT_FILES[1:])

    # Update the reference for the files that are different
    ri.update_reference(differences)
    differences = ri.compare()
    assert not differences


def test_missing_reference(repro_dirs_missing, caplog):
    """
    Test case where some reference datasets are missing
    """
    with caplog.at_level(logging.WARNING):
        ri = ReproducibilityInfo(
            repro_dirs_missing[0],
            repro_dirs_missing[1],
            str(repro_dirs_missing[1] / "manifest.yaml"),
        )
    assert (
        "Not all reference files exist. Copying from current model output"
        in caplog.text
    )
    differences = ri.compare()
    assert not differences


def test_missing_manifest(repro_dirs_same, repro_dirs_empty, caplog):
    """
    Test cases where the manifest file does not exist
    """
    # Reference directory consistent with outputs
    with caplog.at_level(logging.WARNING):
        ri = ReproducibilityInfo(
            repro_dirs_same[0],
            repro_dirs_same[1],
            str(repro_dirs_empty[1] / "manifest.yaml"),
        )
    assert (
        "Manifest file does not exist. Generating manifest from reference files"
        in caplog.text
    )
    differences = ri.compare()
    assert not differences


def test_initial_run(repro_dirs_empty, caplog):
    """
    Test cases where no reference data or manifest exists. This would be the
    situation the first time a test model experiment is run.
    """
    # Reference directory consistent with outputs
    with caplog.at_level(logging.WARNING):
        ri = ReproducibilityInfo(
            repro_dirs_empty[0],
            repro_dirs_empty[1],
            str(repro_dirs_empty[1] / "manifest.yaml"),
        )
    assert (
        "Not all reference files exist. Copying from current model output"
        in caplog.text
    )
    assert (
        "Manifest file does not exist. Generating manifest from reference files"
        in caplog.text
    )
    differences = ri.compare()
    assert not differences
