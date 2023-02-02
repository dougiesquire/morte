# Copyright 2022 ACCESS-NRI and contributors. See the top-level COPYRIGHT file for details.
# SPDX-License-Identifier: Apache-2.0

from morte.models.test import PerformanceInfo


def test_parse_pbs_summary(base_dir):
    """
    Test that PBS summary is parsed correctly
    """
    pi = PerformanceInfo(base_dir, None)
    expected = {
        "Service Units": 123.45,
        "NCPUs Requested": 234,
        "NCPUs Used": 123,
        "CPU Time Used": 20.5,
        "Memory Requested": 1_649_267_441_664,
        "Memory Used": 214_748_364_800,
        "Walltime requested": 1.0,
        "Walltime Used": 0.51,
        "JobFS requested": 1024,
        "JobFS used": 0,
    }
    for key, exp in expected.items():
        res = pi.data["PBS summary"].pop(key)
        assert res == exp

    assert not pi.data["PBS summary"]
