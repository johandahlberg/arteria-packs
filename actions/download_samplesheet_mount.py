from st2common.runners.base_action import Action
import os.path

class DownloadSamplesheetMount(Action):
    """
    Reads a samplesheet from a local mount, mainly used as a fallback for
    Clarity lims downloads after moving away from the Hermes service.
    Keyed on the flowcell id.
    """

    def run(self, flowcell_name, samplesheet_path):
        path_and_file = os.path.join(samplesheet_path, flowcell_name + '_samplesheet.csv')
        try:
            with open(path_and_file, 'r') as samplesheet_file:
                samplesheet = samplesheet_file.read()

        except IOError as err:
            self.logger.error('IOError while attempting to read local samplesheet: {}'.format(err.message))
            raise err

        return (True, samplesheet)

