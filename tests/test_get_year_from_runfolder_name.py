import unittest

from lib.get_year_from_runfolder_name import GetYearFromRunfolderNameAction


class TestGetYearFromRunfolderNameAction(unittest.TestCase):
    action_cls = GetYearFromRunfolderNameAction

    def test_two_digit_year(self):
        gy = GetYearFromRunfolderNameAction()
        year = gy.get_year("150204_D00458_0062_BC6L37ANXX")
        self.assertEquals(year, "2015")

        year = gy.get_year("130109_M00485_0028_000000000-A3349")
        self.assertEquals(year, "2013")

    def test_four_digit_year(self):
        gy = GetYearFromRunfolderNameAction()
        year = gy.get_year("20180926_FS10000263_2_BNT40323-2137")
        self.assertEquals(year, "2018")
