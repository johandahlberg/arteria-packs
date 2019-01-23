#!/usr/bin/python

import argparse
import datetime
import json
import logging
import os
import shutil
import socket


class PurgeRemoteFolders(object):

    def __init__(self, biotank_archive_folder, age_in_days, dryrun, execution_id):
        # do some explicit sanity checking here
        if not biotank_archive_folder:
            raise ValueError(
                "an illegal value for biotank_archive_folder was specified: {val}".format(val=biotank_archive_folder))
        if int(age_in_days) <= 0:
            raise ValueError(
                "an illegal value for age_in_days was specified: {val}".format(val=age_in_days))

        self.biotank_archive_folder = str(biotank_archive_folder)
        self.age_in_days = int(age_in_days)
        self.dryrun = bool(dryrun)

        # the directory to look for things to clean are constructed from e.g. the hostname of the machine
        # as a precaution, this is hardcoded here and can not be supplied as a parameter
        # also, remove the '.sequencing'-suffix if present
        hostname = socket.gethostname().replace(".sequencing", "")
        self.archive_base_dir = self.sanitize_path(
            self.biotank_archive_folder,
            os.path.join(
                "/data",
                hostname))
        self.log = self.setup_logger(execution_id)

    def setup_logger(self, execution_id):

        # setup a formatter that will include the st2 execution id with the log
        formatter = logging.Formatter('%(message)s,%(asctime)s,{id}'.format(id=execution_id))

        # the logfile will be written in the folder where the cleanup is taking place, the "KEEP" prefix will keep it
        # from being removed
        logfile = os.path.join(self.archive_base_dir, "KEEP_removed_archives.log")
        ch = logging.FileHandler(logfile, delay=True)
        ch.setFormatter(formatter)

        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)
        logger.addHandler(ch)

        return logger

    @staticmethod
    def sanitize_path(dirty_path, directory):
        if os.path.isabs(dirty_path):
            raise ValueError(
                "{p} is an absolute path which is not allowed at this point".format(
                    p=dirty_path))
        # fully resolve path to make sure that no symlinks or upward references are left and cause surprises
        clean_path = os.path.realpath(
            os.path.join(directory, dirty_path))
        # ensure that the resulting path is below the directory
        if not clean_path.startswith(directory):
            raise ValueError(
                "{p} appears to resolve to a path outside of {d} which is not allowed at this point".format(
                    p=dirty_path, d=directory))
        return clean_path

    def get_files_and_folders(self):
        remove_if_modified_before_this = datetime.date.today() - datetime.timedelta(days=self.age_in_days)

        def _path_should_be_purged(p):
            path_modtimestamp = os.stat(os.path.join(self.archive_base_dir, p)).st_mtime
            path_modification_date = datetime.date.fromtimestamp(path_modtimestamp)
            return path_modification_date < remove_if_modified_before_this and not p.startswith("KEEP")

        return filter(
            _path_should_be_purged,
            os.listdir(self.archive_base_dir))

    def purge_files_and_folders(self, files_and_folders_to_purge):

        for file_or_folder_to_purge in files_and_folders_to_purge:
            sanitized_path = self.sanitize_path(file_or_folder_to_purge, self.archive_base_dir)
            # use shutil.rmtree for directories and os.unlink for everything else
            purge_fn = shutil.rmtree if os.path.isdir(sanitized_path) else os.unlink
            if not self.dryrun:
                purge_fn(sanitized_path)
                self.log.info(sanitized_path)

    def purge(self):

        try:
            files_and_folders_to_purge = self.get_files_and_folders()
        except Exception as e:
            self.log.error(
                "encountered the following error when trying to determine files and folders to purge: {msg}".format(
                    msg=e))
            raise

        try:
            self.purge_files_and_folders(files_and_folders_to_purge)
        except Exception as e:
            self.log.error(
                "encountered the following error when trying to purge files and folders: {msg}".format(
                    msg=e))
            raise

        return files_and_folders_to_purge


def main():

    parser = argparse.ArgumentParser(
        description="Purge archived runfolders from biotanks based on age")

    # Required arguments
    parser.add_argument(
        "--biotank_archive_folder",
        required=True,
        help="Path to the folder for archived runfolders, relative to the host-specific data path")
    parser.add_argument(
        "--age_in_days",
        required=True,
        help="Files and folders that haven't been modified in this many days will be removed")
    parser.add_argument(
        "--dryrun",
        required=False,
        action="store_true",
        help="If true, only a dry-run will be performed and nothing is removed")
    parser.set_defaults(dryrun=False)
    args = parser.parse_args()

    execution_id = os.environ.get("ST2_ACTION_EXECUTION_ID", "")
    cleaner = PurgeRemoteFolders(args.biotank_archive_folder, args.age_in_days, args.dryrun, execution_id)

    result_as_json = cleaner.purge()
    print(json.dumps(result_as_json))


if __name__ == '__main__':
    main()
