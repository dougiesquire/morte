import logging

from morte.models.test import REPRO_OUTPUT_FILES, ReproducibilityInfo


def test_no_change(reference_dir_same):
    """
    Test case where the output and reference directories contain the same files
    """
    base_dir = reference_dir_same[0]
    reference_dir = reference_dir_same[1]
    ri = ReproducibilityInfo(
        base_dir,
        reference_dir,
        str(reference_dir / "manifest.yaml"),
    )
    differences = ri.compare()
    assert not differences


def test_all_changed(reference_dir_diff):
    """
    Test case where the reference data has changed relative to the output data
    """
    base_dir = reference_dir_diff[0]
    reference_dir = reference_dir_diff[1]
    ri = ReproducibilityInfo(
        base_dir,
        reference_dir,
        str(reference_dir / "manifest.yaml"),
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


def test_missing_reference(reference_dir_missing, caplog):
    """
    Test case where some reference datasets are missing
    """
    base_dir = reference_dir_missing[0]
    reference_dir = reference_dir_missing[1]
    with caplog.at_level(logging.WARNING):
        ri = ReproducibilityInfo(
            base_dir,
            reference_dir,
            str(reference_dir / "manifest.yaml"),
        )
    assert (
        "Not all reference files exist. Copying from current model output"
        in caplog.text
    )
    differences = ri.compare()
    assert not differences


def test_missing_manifest(reference_dir_same, reference_dir_diff, caplog):
    """
    Test cases where the manifest file does not exist
    """
    # Reference directory consistent with outputs
    base_dir = reference_dir_same[0]
    reference_dir = reference_dir_same[1]
    with caplog.at_level(logging.WARNING):
        ri = ReproducibilityInfo(
            base_dir,
            reference_dir,
            "./doesnotexist.yaml",
        )
    assert (
        "Manifest file does not exist. Generating manifest from reference files"
        in caplog.text
    )
    differences = ri.compare()
    assert not differences


def test_initial_run(reference_dir_empty, caplog):
    """
    Test cases where no reference data or manifest exists. This would be the
    situation the first time a test model experiment is run.
    """
    # Reference directory consistent with outputs
    base_dir = reference_dir_empty[0]
    reference_dir = reference_dir_empty[1]
    with caplog.at_level(logging.WARNING):
        ri = ReproducibilityInfo(
            base_dir,
            reference_dir,
            "./doesnotexist.yaml",
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
