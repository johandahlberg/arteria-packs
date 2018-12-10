
import sys

from st2common.runners.base_action import Action

class GetFlowcellFromRunfolderNameAction(Action):
    """
    Parses the flowcell name from the name of a runfolder.
    Assumes the format is:
    150204_D00458_0062_BC6L37ANXX (hiseq-family)
    130109_M00485_0028_000000000-A3349 (miseq)
    """

    def get_name(self, runfolder_name):
        base_name = runfolder_name.split("_")[3]

        if base_name[0] == 'A' or base_name[0] == 'B':
            # A and B are the position of the flowcell on the
            # instrument and should not be included.
            flowcell_name = base_name[1:len(base_name)]
        else:
            flowcell_name = base_name

        return flowcell_name

    def run(self, **kwargs):
        return self.get_name(kwargs["runfolder_name"])

