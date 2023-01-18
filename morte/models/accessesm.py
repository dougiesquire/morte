"""
Interface for the ACCESS-CM2 coupled model
"""

from .model import Model


class AccessESM(Model):
    class PerformanceInfo(Model.PerformanceInfo):
        pass

    class ReproducibilityInfo(Model.ReproducibilityInfo):
        pass

    def __init__(self, output_paths):

        super(AccessESM, self).__init__(output_paths)
