#!/usr/bin/env python

import csv
import string

# Needs to be run in a Stackstorm virtualenv
from st2common.runners.base_action import Action


class ReadProjectsEmailFile(Action):

    def run(self, file_path, projects, restrict_to_projects):

        if restrict_to_projects == 'keep_all_projects':
            projects_list = projects['projects']
        else:
            projects_list = [proj.strip() for proj in restrict_to_projects.split(",")]

        result = {}

        with open(file_path) as csv_file:
            reader = csv.DictReader(csv_file, delimiter=';')
            for row in reader:
                project = row['project']
                sensitive = self.str_to_bool(row['sensitive'])
                members_csv = row.get('members', "") or ""
                members = [email for email in map(string.strip, members_csv.split(",")) if len(email) > 0]
                if project in projects_list:
                    result[project] = {"email": row['email'], "members": members, "sensitive": sensitive}

        if len(projects_list) == len(result.keys()):
            self.logger.info("Projects given and projects found in file did match...")
            return True, result
        else:
            self.logger.error("Projects given and projects found in file did not match!")
            return False, {}

    @staticmethod
    def str_to_bool(string):
        if string == "True":
            return True
        elif string == "False":
            return False
        else:
            raise ValueError("{} is not a valid boolean.".format(string))
