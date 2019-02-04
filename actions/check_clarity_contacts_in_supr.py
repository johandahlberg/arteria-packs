#!/usr/bin/env python

from st2common.runners.base_action import Action

from genologics.lims import *
from genologics.config import BASEURI, USERNAME, PASSWORD
from lib.supr_utils import * 

#disable ssl warnings
import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()


class NoEmailInClarity(AssertionError):
    pass


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

    def check_email_of_role(self, project, role):
        try:
            email = project.udf.get("Email of {}".format(role))
            if email:
                email = email.strip()
            name = project.udf.get("Name of {}".format(role)) or "Name missing from LIMS"

            if not email:
                raise NoEmailInClarity()
            # Normal dashes and en dashes are used to indicate that the field is intentionally left blank
            if email == '-' or email == u'\u2013' or email == 'N/A':
                return None

            SuprUtils.search_by_email(self.supr_api_url, email, self.supr_api_user, self.supr_api_key)
        except NoHitForEmailInSupr:
            self.logger.info(u"{} had no email registered in Supr for role: {}. Email was: {}".format(project.name,
                                                                                                      role,
                                                                                                      email))
            return u"{}: {} ({}), {}<br><hr>\n".format(project.name, name, role,
                                                       u"has no email registered in Supr.")
        except MoreThanOneHitForEmailInSuper:
            self.logger.info(u"{} had multiple accounts for email"
                             u" registered in Supr for role: {}. Email was: ".format(project.name, role, email))
            return u"{}: {} ({}), {}<br><hr>\n".format(project.name, name, role,
                                                      u"appears to have multiple accounts "
                                                      u"registered in Supr, for that email. "
                                                      u"This is very odd...")
        except NoEmailInClarity:
            return u"{}: {} ({}), {}<br><hr>\n".format(project.name, name, role,
                                                       u"has no email registered in Clarity.")
        return None

    def run(self, supr_api_url, supr_api_user, supr_api_key):

        self.supr_api_url = supr_api_url
        self.supr_api_user = supr_api_user
        self.supr_api_key = supr_api_key

        projects = self.fetch_open_projects()
        email_body = ""
        for project in projects:
            roles = ["PI", "bioinformatics responsible person"]
            for role in roles:
                email_text = self.check_email_of_role(project, role)
                if email_text:
                    email_body += email_text

        return True, email_body

