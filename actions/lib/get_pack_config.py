import sys

from st2common.runners.base_action import Action

class GetPackConfig(Action):
    """
    Used to access the config file.
    """

    def run(self, **kwargs):
        return self.config

