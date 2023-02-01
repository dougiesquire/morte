# Copyright 2022 ACCESS-NRI and contributors. See the top-level COPYRIGHT file for details.
# SPDX-License-Identifier: Apache-2.0

"""
Tools for helping to parse information from files
"""

import re
import glob
import logging

logger = logging.getLogger(__name__)
log_handler = logging.StreamHandler()
log_handler.setLevel(logging.INFO)
log_format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
log_handler.setFormatter(log_format)
logger.addHandler(log_handler)


class FileParser:
    """
    Class for parsing information from a file
    """

    def __init__(self, file):
        """
        Initialise a FileParser object.

        Parameters
        ----------
        file : str
            Path to the file to parse
        """

        found_files = glob.glob(file)
        if not found_files:
            logger.error(f"The file {file} does not exist to be parsed")
        if len(found_files) > 1:
            logger.error(f"Multiple files found with the pattern {file}")
        self.file = found_files[0]

    def read_file(self):
        """
        Return the content of a the file as a list of lines.
        """
        with open(self.file, "r") as f:
            contents = f.read().splitlines()
        return contents

    def search_regex(self, pattern):
        """
        Search the contents of a file for a provided regex pattern and return a list
        of the specified groupings (one for each occurrence). Stolen and adapted from
        https://github.com/metomi/rose/blob/master/metomi/rose/apps/ana_builtin/grepper.py#L492

        Parameters
        ----------
        pattern: str
            The regex pattern
        """
        matched_groups = []
        for line in self.read_file():
            search = re.search(pattern, line)
            if search:
                matched_groups.append(search.groups())
        return matched_groups

    def parse_pbs_summary(self):
        """
        Parse relevant information from summary footer printed to the bottom of PBS
        output files on Gadi
        """

        def _duration(s):
            """
            Given duration in hrs:mins:secs, return hrs
            """
            hms = s.split(":")
            return float(hms[0]) + float(hms[1]) / 60 + float(hms[2]) / 3600

        def _bytes(s):
            """
            Given a string, e.g. 1TB, return bytes
            """
            val, unit, _ = re.split(r"([B,K,M,G,T,P]+)", s, maxsplit=1)
            units = {
                "B": 1,
                "KB": 2**10,  # Gadi uses binary system units
                "MB": 2**20,
                "GB": 2**30,
                "TB": 2**40,
            }
            return int(round(float(val) * units[unit]))

        to_parse = {
            "Service Units": float,
            "NCPUs Requested": int,
            "NCPUs Used": int,
            "CPU Time Used": _duration,
            "Memory Requested": _bytes,
            "Memory Used": _bytes,
            "Walltime requested": _duration,
            "Walltime Used": _duration,
            "JobFS requested": _bytes,
            "JobFS used": _bytes,
        }

        info = {}
        for p, f in to_parse.items():
            groups = self.search_regex(r"\s*{}:\s*([^ ]+)".format(p))
            if not groups:
                logger.warning(f"'{p}' not found in PBS output")
            if len(groups) > 1:
                logger.error(f"Multiple values found for '{p}' in PBS output")

            info[p] = f(groups[0][0])

        return info
