import sys

from st2common.runners.base_action import Action

class GetPackConfig(Action):
    """
    Used to access the config file.
    """

    def run(self, **kwargs):
        if not self.config:
            raise Exception("The config was empty. Are you sure that you have placed a config under: "
                            "/opt/stackstorm/configs/snpseq_packs.yaml?")
        return self.config

