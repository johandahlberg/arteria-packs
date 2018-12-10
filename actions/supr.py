#!/usr/bin/env python

from lib.supr_utils import *

# Needs to be run in a Stackstorm virtualenv
from st2common.runners.base_action import Action


class Supr(Action):

    def run(self, action, supr_base_api_url, api_user, api_key, **kwargs):
        if action == "get_id_from_email":
            return SuprUtils.search_for_pi_and_members(kwargs['project_to_email_sensitive_dict'], supr_base_api_url, api_user, api_key)
        elif action == 'create_delivery_project':
            return SuprUtils.create_delivery_project(supr_base_api_url,
                                                kwargs['project_names_and_ids'],
                                                kwargs['staging_info'],
                                                kwargs['project_info'],
                                                api_user, api_key)
        elif action == 'check_ngi_ready':
            return SuprUtils.check_ngi_ready_status(supr_base_api_url, api_user, api_key, kwargs['project'])
        else:
            raise AssertionError("Action: {} was not recognized.".format(action))

