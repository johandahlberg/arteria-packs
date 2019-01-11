import re
from st2common.runners.base_action import Action


class GetYearFromRunfolderNameAction(Action):
    """
    Parses the year from the name of a runfolder.
    Assumes the format is:
    150204_D00458_0062_BC6L37ANXX (hiseq-family)
    130109_M00485_0028_000000000-A3349 (miseq)
    20180926_FS10000263_2_BNT40323-2137 (iseq)
    """

    def get_year(self, runfolder_name):
        m = re.match(r"^([\d]*)[\d]{4}_", runfolder_name)
        base_year = m.group(1)

        if len(base_year) is 4:
            return base_year
        else:
            return "20" + base_year

    def run(self, **kwargs):
        return self.get_year(kwargs["runfolder_name"])


