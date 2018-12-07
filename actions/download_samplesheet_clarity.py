from st2common.runners.base_action import Action

from clarity_ext.context import ExtensionContext
from genologics.lims import *
from genologics.config import BASEURI, USERNAME, PASSWORD

import os
from tempfile import mkdtemp
import zipfile
import re

import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()

class DownloadSamplesheetClarity(Action):
    """
    Downloads a samplesheet from Clarity LIMS (instead of Hermes)
    keyed on the flowcell id.
    """

    def get_processes(self, containers):
        for container in containers:
            placement = container.get_placements()
            artifact = placement[placement.keys()[0]]
            yield artifact.parent_process.id

    def highest_id(self, process_ids):
        highest_proc_number = 0
        highest_proc_type = ''
        for process_id in process_ids:
            (proc_type, proc_number) = process_id.split('-')
            if highest_proc_number == 0 or int(proc_number) > highest_proc_number:
                highest_proc_number = int(proc_number)
                highest_proc_type = proc_type
        return highest_proc_type + '-' + str(highest_proc_number)


    def run(self, flowcell_name):
        lims = Lims(BASEURI, USERNAME, PASSWORD) #Need credentials on stackstorm server for genologics package.
        containers = lims.get_containers(name=flowcell_name)
        processes = list(self.get_processes(containers))
        newest_process_id = self.highest_id(processes)
        cwd = os.getcwd()
        #generate a fresh temp dir to mimic lims behaviour (avoid overwriting samplesheets)
        temp_wd = mkdtemp()
        os.chdir(temp_wd)
        context = ExtensionContext.create(newest_process_id)
        try:
            samplesheet_file = context.local_shared_file("Sample Sheet")
            # samplesheet file can be both single file and zip file with names like 92-102630_HH7LMCCXY_samplesheet.csv in archive.
            if zipfile.is_zipfile(samplesheet_file):
                #extract appropriate zip member
                zf = zipfile.ZipFile(samplesheet_file, 'r')
                zipped_files = zf.namelist()
                flowcell_pattern = re.compile('_' + flowcell_name + '_samplesheet')
                matching_files = []
                for filename in zipped_files:
                    if flowcell_pattern.search(filename):
                        matching_files.append(filename)
                if len(matching_files) > 1:
                    raise LookupError('More than one samplesheet matching flowcell name in zipfile!')
                elif len(matching_files) == 0:
                    raise LookupError('No matching samplesheet in zipfile')
                else:
                    samplesheet = zf.read(matching_files[0])

            else:
                samplesheet_file.seek(0)
                samplesheet = samplesheet_file.read()

        except IOError as err:
            self.logger.error('IOError while attempting to read samplesheet: {}'.format(err.message))
            raise err
        except LookupError as err:
            self.logger.error('LookupError while attempting to read samplesheet in zip: {}'.format(err.message))
            raise err

        os.chdir(cwd)
        return (True, samplesheet)
