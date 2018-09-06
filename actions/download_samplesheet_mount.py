from st2common.runners.base_action import Action
import os

class DownloadSamplesheetMount(Action):
    """
    Reads a samplesheet from a local mount, mainly used as a fallback for
    Clarity lims downloads after moving away from the Hermes service.
    Keyed on the flowcell id.
    """

    def run(self, flowcell_name, samplesheet_path):
        try:
            samplesheets = [f for f in os.listdir(samplesheet_path) if os.path.isfile(os.path.join(samplesheet_path, f)) and f.endswith(flowcell_name + "_samplesheet.csv")]
            if (samplesheets):
                if(len(samplesheets) > 1):
                    raise ValueError('Multiple matching samplesheets found! ' + ' '.join(name for name in samplesheets ))
                else:
                    with open(os.path.join(samplesheet_path, samplesheets[0])) as samplesheet_file:
                        samplesheet = samplesheet_file.read()
            else:
                raise ValueError('No matching samplesheet found!')

        except IOError as err:
            self.logger.error('IOError while attempting to read samplesheet on disk: {}'.format(err.message))
            raise
        except ValueError as err:
            self.logger.error('Error scanning for samplesheet on disk: {}'.format(err.message))
            raise

        return (True, samplesheet)
