#!/usr/bin/env python

from st2common.runners.base_action import Action

from genologics.lims import *
from genologics.config import BASEURI, USERNAME, PASSWORD
from lib.supr_utils import * 

#disable ssl warnings
import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()


class CheckClarityContactsInSupr(Action):
    """
    Retrives contacts from open projects in ClarityLIMS and checks for
    SUPR accounts by email.
    Then composes an email body to notify project coordinators.
    """

    def fetch_open_projects(self):
        lims = Lims(BASEURI, USERNAME, PASSWORD)
        lims.check_version()
        projects = lims.get_projects()
        filtered_projects = list()
        for project in projects:
            if project.open_date and not project.close_date:
                filtered_projects.append(project)
        return filtered_projects

    def check_email_in_supr(self, email_adress):
        email_missing = False
        email_multi = False

        try:
            supr_id = SuprUtils.search_by_email(self.supr_api_url, email_adress, self.supr_api_user, self.supr_api_key)
        except AssertionError as ae:
            if ("no hits" in ae.message):
                email_missing = True
            elif ("more than one" in ae.message):
                email_multi = True

        return (email_missing, email_multi)

    def run(self, supr_api_url, supr_api_user, supr_api_key):

        self.supr_api_url = supr_api_url
        self.supr_api_user = supr_api_user
        self.supr_api_key = supr_api_key

        projects = self.fetch_open_projects()
        email_body = ""
        for project in projects:
            roles = ["PI", "bioinformatics responsible person"]
            for role in roles:
                email = project.udf.get("Email of {}".format(role))
                if not email:
                    continue
                (account_missing, multiple_accounts) = self.check_email_in_supr(email.strip())
                if not (account_missing or multiple_accounts):
                    continue
                name = project.udf.get("Name of {}".format(role)) or "Name missing from LIMS"
                email_body += "{}: {} {} SUPR {}<br><hr>".format(project.name, role, "missing from" if account_missing else "has multiple accounts in", "( {}, {} )".format(name, email))

        return (True, email_body)

