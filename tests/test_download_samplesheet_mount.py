import os
import tempfile
from st2tests.base import BaseActionTestCase
from download_samplesheet_mount import DownloadSamplesheetMount

class DownloadSamplesheetMountTestCase(BaseActionTestCase):
    action_cls = DownloadSamplesheetMount
    samplesheet_names_and_contents = []
    tempdir = None
    test_files = []

    @classmethod
    def setUpClass(cls):
        #Build a directory of "samplesheets" to scan (the stackstorm action doesn't validate file content)
        cls.samplesheet_names_and_contents = [("FC1_samplesheet.csv", "samplesheet 1"), ("FC2_samplesheet.csv", "samplesheet 2"),
                ("PREFIX-FC2_samplesheet.csv", "samplesheet 3"), ("000000000-FC3_samplesheet.csv", "samplesheet 4")]
        cls.tempdir = tempfile.mkdtemp()
        for name, content in cls.samplesheet_names_and_contents:
            samplesheet_path = cls.tempdir + "/" + name
            with open(samplesheet_path, 'w') as file:
                file.write(content)
                cls.test_files.append(samplesheet_path)

    def run_action_and_check_result_string(self, flowcell_name, samplesheet_path, expected_exit_status, expected_result):
        exit_status, result = self.get_action_instance().run(flowcell_name, samplesheet_path)
        self.assertTrue(exit_status == expected_exit_status)
        self.assertEquals(result, expected_result)

    def run_action_and_check_exception(self, flowcell_name, samplesheet_path, expected_exception_text):
        with self.assertRaises(Exception) as context:
            self.get_action_instance().run(flowcell_name, samplesheet_path)

        self.assertTrue(expected_exception_text in str(context.exception))

    def test_run_single_matching_std_samplesheet(self):
        expected_exit_status = True
        expected_result = "samplesheet 1"
        flowcell_name = "FC1"
        samplesheet_path = self.tempdir
        self.run_action_and_check_result_string(flowcell_name, samplesheet_path, expected_exit_status, expected_result)

    def test_run_multiple_matching_samplesheets(self):
        flowcell_name = "FC2"
        samplesheet_path = self.tempdir
        expected_exception_text = "Multiple matching samplesheets"
        self.run_action_and_check_exception(flowcell_name, samplesheet_path, expected_exception_text)

    def test_run_single_matching_myseq_prefixed_samplesheet(self):
        expected_exit_status = True
        expected_result = "samplesheet 4"
        flowcell_name = "FC3"
        samplesheet_path = self.tempdir
        self.run_action_and_check_result_string(flowcell_name, samplesheet_path, expected_exit_status, expected_result)

    def test_run_no_matching_samplesheet(self):
        flowcell_name = "FC99"
        samplesheet_path = self.tempdir
        expected_exception_text = "No matching samplesheet found"
        self.run_action_and_check_exception(flowcell_name, samplesheet_path, expected_exception_text)

    @classmethod
    def tearDownClass(cls):
        #Remove tempfiles here
        for test_file in cls.test_files:
            os.remove(test_file)

        if (cls.tempdir):
            os.rmdir(cls.tempdir)
