import os
import argparse
import yaml
import logging
import sys

"""
 Script that parses all yaml files in actions and rules and checks
 that all referenced files exist. This script assumes that
 action/rule/workflow/sensor name and file name are the same, e.g.
 Workflow name: ngi_uu_workflow
 File name: ngi_uu_workflow.yaml

 Keys searched for are specifically:
 In actions:
 - entry_point
 - default (parameters -> workflow -> default)

 In workflows:
 - action (workflows -> main -> tasks -> <task_name> -> action)

In rules:
 - ref (action -> ref)

 In sensors:
 - entry_point
"""

class CheckReferencedFiles():

    def __init__(self, pack_location):
        self.pack_location = pack_location
        self.pack_name = os.path.basename(pack_location)
        self.exit_status = 0

    def find(self, d, tag):
        if tag in d:
            logger.debug("Found tag: {}, with value: {}".format(tag,d[tag]))
            yield d[tag]
        for k, v in d.items():
            if isinstance(v, dict):
                for i in self.find(v, tag):
                    yield i

    def check_action(self, file, action):
        if os.path.isfile(os.path.join(self.pack_location,"actions","{}.yaml".format(action))):
            logger.debug("In file {}: {} exists".format(file, action))
        else:
            logger.error("In file {}: {} does not exist!".format(file, action))
            self.exit_status = 1

    def check_file(self, folder_path, parsed_file, referenced_file):
        if os.path.isfile(os.path.join(self.pack_location, folder_path, referenced_file)):
            logger.debug("In file {}: {} exists".format(parsed_file, referenced_file))
        else:
            logger.error("In file {}: {} does not exist!".format(parsed_file, referenced_file))
            self.exit_status = 1

    def check_files_in_folder(self, folder_path, tags):
        for file in os.listdir(os.path.join(self.pack_location,folder_path)):
            logger.debug("Found file: {} in {}".format(file, folder_path))
            if file.endswith(".yaml"):
                logger.debug("Found file, {}, is a yaml file".format(file))
                full_path_file = os.path.join(self.pack_location,folder_path,file)
                yaml_dict = yaml.safe_load(open(full_path_file))
                for tag in tags:
                    if tag == "workflow":
                        for ref in self.find(yaml_dict, tag):
                            workflow = ref["default"]
                            pack, action = workflow.split(".")
                            if pack == self.pack_name:
                                self.check_action(full_path_file, action)
                    else:
                        for ref in self.find(yaml_dict, tag):
                            if tag == "entry_point":
                                # Some runner types like run-local or remote-shell-cmd
                                # have no value for entry_point
                                if ref != '':
                                    self.check_file(folder_path, full_path_file, ref)
                            else:
                                if "." in ref:
                                    pack, action = ref.split(".")
                                    if pack == self.pack_name:
                                        self.check_action(full_path_file, action)
                                else:
                                    self.check_action(full_path_file, ref)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Check that all referenced \
                                     files in rules and actions exist")
    parser.add_argument('-p','--pack-location', required = True)
    parser.add_argument('-d','--debug', action='store_true')
    args = parser.parse_args()

    pack_location = args.pack_location
    debug_mode = args.debug

    logger = logging.getLogger('check_referenced_files')

    if debug_mode:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    ch = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    checker = CheckReferencedFiles(pack_location)

    # Check actions
    checker.check_files_in_folder("actions", ["entry_point", "workflow"])

    # Check workflows
    checker.check_files_in_folder("actions/workflows", ["action"])

    # Check rules
    checker.check_files_in_folder("rules", ["ref"])

    # Check sensors
    checker.check_files_in_folder("sensors", ["entry_point"])

    logger.info("Exit status was: {}".format(checker.exit_status))

    if checker.exit_status == 0:
        sys.exit(0)
    else:
        sys.exit(1)

