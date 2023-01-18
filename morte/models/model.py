"""
Generic model class, primarily to be inherited by other models.
"""

from yamanifest.manifest import Manifest as YaManifest


class Model:
    """Abstract model class"""

    class PerformanceInfo:
        """Object for keeping track of performance/timing information"""

    class ReproducibilityInfo(YaManifest):
        """
        Object for keeping track of reproducibility hashes (inherited
        from yamanifest.manifest)
        """

    def __init__(self, output_paths):

        self.output_paths = output_paths

        self.PerformanceInfo = self.PerformanceInfo()
        self.ReproducibilityInfo = self.ReproducibilityInfo()
