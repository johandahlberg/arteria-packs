import os
import argparse
import yaml
import logging

#
# Script that parses all yaml files in actions and rules and checks
# that all* referenced files exist. This script assumes that
# action/rule/workflow name and file name are the same, e.g.
# Workflow name: ngi_uu_workflow
# File name: ngi_uu_workflow.yaml
#
# Keys searched for are specifically:
# In actions:
# - entry_point
# - default (parameters -> workflow -> default)
#
# In workflows:
# - action (workflows -> main -> tasks -> <task_name> -> action)
#
# In rules:
# - ref (action -> ref)
#
# * Not really all:
# TODO: Referenced actions should probably be compared with action names rather
# than file name. Because of the current implementation sensors are not included
# in check.

def find(d, tag):
    if tag in d:
        logger.debug("Found tag: {}, with value: {}".format(tag,d[tag]))
        yield d[tag]
    for k, v in d.items():
        if isinstance(v, dict):
            for i in find(v, tag):
                yield i

def check_action(pack_location, file, action):
    if os.path.isfile(os.path.join(pack_location,"actions","{}.yaml".format(action))):
        logger.debug("In file {}: {} exists".format(file, action))
    else:
        logger.error("In file {}: {} does not exist!".format(file, action))

def check_file(pack_location, parsed_file, referenced_file):
    if os.path.isfile(os.path.join(pack_location,"actions",referenced_file)):
        logger.debug("In file {}: {} exists".format(parsed_file, referenced_file))
    else:
        logger.error("In file {}: {} does not exist!".format(parsed_file, referenced_file))

def check_files_in_folder(folder_path, tags):
    for file in os.listdir(os.path.join(pack_location,folder_path)):
        logger.debug("Found file: {} in {}".format(file, folder_path))
        if file.endswith(".yaml"):
            logger.debug("Found file, {}, is a yaml file".format(file))
            full_path_file = os.path.join(pack_location,folder_path,file)
            yaml_dict = yaml.load(open(full_path_file))
            for tag in tags:
                if tag == "workflow":
                    for ref in find(yaml_dict, tag):
                        workflow = ref["default"]
                        pack, action = workflow.split(".")
                        if pack == "snpseq_packs":
                            check_action(pack_location, full_path_file, action)
                else:
                    for ref in find(yaml_dict, tag):
                        if tag == "entry_point":
                            # Some runner types like run-local or remote-shell-cmd
                            # have no value for entry_point
                            if ref != '':
                                check_file(pack_location, full_path_file, ref)
                        else:
                            if "." in ref:
                                pack, action = ref.split(".")
                                if pack == "snpseq_packs":
                                    check_action(pack_location, full_path_file, action)
                            else:
                                check_action(pack_location, full_path_file, ref)

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

    # Check actions
    check_files_in_folder("actions", ["entry_point", "workflow"])

    # Check workflows
    check_files_in_folder("actions/workflows", ["action"])

    # Check rules
    check_files_in_folder("rules", ["ref"])
