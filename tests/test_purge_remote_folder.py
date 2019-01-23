
import datetime
import logging
import mock
import os
import shutil
import socket
import tempfile
import unittest

from lib.purge_remote_folder import PurgeRemoteFolders


class TestPurgeRemoteFolders(unittest.TestCase):

    @staticmethod
    def _to_unix_timestamp(date_obj):
        return (date_obj - datetime.date(1970, 1, 1)).total_seconds()

    def setUp(self):
        self.age_in_days = 30
        self.dryrun = True
        self.directory = tempfile.mkdtemp()
        self.files = [
            os.path.basename(tempfile.mkstemp(prefix=name, dir=self.directory)[1]) for name in [
                "too_old", "too_new", "KEEP_"]]
        for tfile in self.files:
            atime = self._to_unix_timestamp(datetime.date.today())
            mtime = atime if tfile.startswith("too_new") else \
                self._to_unix_timestamp(datetime.date.today() - datetime.timedelta(days=(self.age_in_days + 1)))
            os.utime(os.path.join(self.directory, tfile), (atime, mtime))
        self.execution_id = "this-is-an-execution-id"
        self.action = self.get_instance(
            os.path.basename(self.directory), self.age_in_days, self.dryrun, self.execution_id)
        self.action.archive_base_dir = self.directory

    def get_instance(self, *args):
        inst = PurgeRemoteFolders(*args)
        inst.log = mock.MagicMock(spec=logging.Logger)
        return inst

    def tearDown(self):
        shutil.rmtree(self.directory, ignore_errors=True)

    def test_sanitize_path(self):
        root_dir = os.path.join("/path", "to", "root")
        abs_path = os.path.join("/this", "is", "an", "absolute", "path")
        escape_path = os.path.join("..", "some", "other", "dir")
        upward_path = os.path.join("this", "..", "path", "..", "has", "..", "upward", "..", "references", "..")
        good_path = os.path.join("and", "subdirectory")
        self.assertRaisesRegexp(ValueError, "absolute path which", self.action.sanitize_path, abs_path, root_dir)
        self.assertRaisesRegexp(ValueError, "path outside of", self.action.sanitize_path, escape_path, root_dir)
        self.assertEqual(root_dir, self.action.sanitize_path(upward_path, root_dir))
        self.assertEqual(os.path.join(root_dir, good_path), self.action.sanitize_path(good_path, root_dir))
        # create symlinks that may escape from directory
        abs_symlink = "abs_symlink"
        escape_symlink = "escape_symlink"
        good_symlink = "good_symlink"
        os.symlink(abs_path, os.path.join(self.directory, abs_symlink))
        os.symlink(escape_path, os.path.join(self.directory, escape_symlink))
        os.symlink(os.path.join(self.directory, good_path), os.path.join(self.directory, good_symlink))
        self.assertRaisesRegexp(
            ValueError, "path outside of", self.action.sanitize_path, abs_symlink, self.directory)
        self.assertRaisesRegexp(
            ValueError, "path outside of", self.action.sanitize_path, escape_symlink, self.directory)
        self.assertEqual(
            os.path.join(self.directory, good_path), self.action.sanitize_path(good_symlink, self.directory))

    def test_get_files_and_folders(self):
        expected_files_and_folders = filter(
            lambda p: os.path.basename(p).startswith("too_old"),
            self.files)
        observed_files_and_folders = self.action.get_files_and_folders()
        self.assertListEqual(expected_files_and_folders, observed_files_and_folders)

    def test_purge_files_and_folders(self):
        self.action.purge_files_and_folders(self.files)
        self.assertTrue(all(map(lambda p: os.path.exists(os.path.join(self.directory, p)), self.files)))
        self.action.dryrun = False
        self.action.purge_files_and_folders(self.files)
        self.assertFalse(any(map(lambda p: os.path.exists(os.path.join(self.directory, p)), self.files)))
        self.action.purge_files_and_folders([""])
        self.assertFalse(os.path.exists(self.directory))

    def test_run(self):
        directory_pattern = os.path.join("path", "to", "archive")
        expected_directory = os.path.join("/data", socket.gethostname(), directory_pattern)
        expected_output = filter(lambda p: p.startswith("too_old"), self.files)
        self.action = self.get_instance(directory_pattern, self.age_in_days, self.dryrun, self.execution_id)
        self.assertEqual(expected_directory, self.action.archive_base_dir)
        with mock.patch.object(
                self.action, 'get_files_and_folders') as get_files_and_folders, mock.patch.object(
                self.action, 'purge_files_and_folders') as purge_files_and_folders:
            get_files_and_folders.return_value = expected_output
            observed_output = self.action.purge()
            self.assertListEqual(expected_output, observed_output)
            get_files_and_folders.assert_called_once_with()
            purge_files_and_folders.assert_called_once_with(expected_output)

            # also, ensure that exceptions are handled properly
            purge_files_and_folders.side_effect = IOError("key error raised by mock")
            self.assertRaises(IOError, self.action.purge)
            get_files_and_folders.side_effect = ValueError("value error raised by mock")
            self.assertRaises(ValueError, self.action.purge)

    def test_hostname(self):
        mocked_hostname = "host.sequencing"
        with mock.patch.object(socket, "gethostname", return_value=mocked_hostname) as socket_mock:
            relative_directory = os.path.basename(self.directory)
            expected_archive_dir = os.path.join("/data", mocked_hostname.replace(".sequencing", ""), relative_directory)
            inst = PurgeRemoteFolders(relative_directory, self.age_in_days, self.dryrun, self.execution_id)
            self.assertEqual(expected_archive_dir, inst.archive_base_dir)
