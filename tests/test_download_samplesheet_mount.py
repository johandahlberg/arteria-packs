import mock
import os
import tempfile

from st2tests.base import BaseActionTestCase
from download_samplesheet_mount import DownloadSamplesheetMount

class DownloadSamplesheetMountTestCase(BaseActionTestCase):
    action_cls = DownloadSamplesheetMount
    samplesheet_names_and_contents = []
    tempdir = ''
    test_files = []

    @classmethod
    def setUpClass(cls):
        #Build a directory of "samplesheets" to scan (the stackstorm action doesn't validate file content)
        cls.samplesheet_names_and_contents = [("FC1_samplesheet.csv", "samplesheet 1"), ("FC2_samplesheet.csv", "samplesheet 2"), 
                ("PREFIX-FC2_samplesheet.csv", "samplesheet 3"), ("000000000-FC3_samplesheet.csv", "samplesheet 4")]
        cls.tempdir = tempfile.mkdtemp()
        for name, contents in cls.samplesheet_names_and_contents:
            samplesheet_fh, samplesheet_path = tempfile.mkstemp(prefix=name, dir=cls.tempdir)
            samplesheet_fh.write(contents)
            samplesheet_fh.close()
            cls.test_files.append(samplesheet_path)

    def run_action_and_check_results(self, flowcell_name, samplesheet_path, expected_exit_status, expected_result):
        exit_status, result = self.get_action_instance().run(flowcell_name, samplesheet_path)
        self.assertTrue(exit_status == expected_exit_status)
        self.assertDictEqual(result, expected_result)





