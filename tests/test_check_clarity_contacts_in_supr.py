# -*- coding: utf-8 -*-

import mock
from st2tests.base import BaseActionTestCase

from lib.supr_utils import SuprUtils, NoHitForEmailInSupr
from check_clarity_contacts_in_supr import CheckClarityContactsInSupr, NoEmailInClarity


class TestCheckClarityContactsInSupr(BaseActionTestCase):
    action_cls = CheckClarityContactsInSupr

    class MockProject(object):
        def __init__(self, name):
            self.name = name
            self.udf = {'Name of PI': u'Pär Tyrsson',
                        'Email of PI': 'pi@example.com',
                        'Name of bioinformatics responsible person': u'Åsa Öman',
                        'Email of bioinformatics responsible person': 'bioinfo@example.com'}

    def test_empty_email_body_when_all_is_good(self):

        with mock.patch.object(CheckClarityContactsInSupr,
                               'fetch_open_projects',
                               return_value=[self.MockProject('proj1'), self.MockProject('proj2')]),\
                mock.patch.object(SuprUtils,
                                  'search_by_email',
                                  return_value="some-fake-id"):

            action = self.get_action_instance()
            exit_status, results = action.run(supr_api_url='http://example.com',
                                              supr_api_user='user',
                                              supr_api_key='key')
            # If there is an email in supr, the results should be
            # empty
            self.assertFalse(results)

    def test_can_create_email_body_when_no_supr_user_found(self):

        with mock.patch.object(CheckClarityContactsInSupr,
                               'fetch_open_projects',
                               return_value=[self.MockProject('proj1'), self.MockProject('proj2')]), \
             mock.patch.object(SuprUtils,
                               'search_by_email',
                               side_effect=NoHitForEmailInSupr()):

            action = self.get_action_instance()
            exit_status, results = action.run(supr_api_url='http://example.com',
                                              supr_api_user='user',
                                              supr_api_key='key')

            self.assertTrue(u"Pär Tyrsson (PI), has no email registered in Supr." in results)

    def test_can_create_email_body_when_incorrectly_entered_in_clarity(self):

        with mock.patch.object(CheckClarityContactsInSupr,
                               'fetch_open_projects',
                               return_value=[self.MockProject('proj1'), self.MockProject('proj2')]), \
             mock.patch.object(SuprUtils,
                               'search_by_email',
                               side_effect=NoEmailInClarity()):

            action = self.get_action_instance()
            exit_status, results = action.run(supr_api_url='http://example.com',
                                              supr_api_user='user',
                                              supr_api_key='key')

            self.assertTrue(u"Åsa Öman (bioinformatics responsible person), "
                            u"has no email registered in Clarity." in results)

    def test_can_create_email_body_ignores_dashes(self):

        alt_mock_proj = self.MockProject('proj1')
        alt_mock_proj.udf['Email of bioinformatics responsible person'] = '-'
        alt_mock_proj.udf['Email of PI'] = '-'

        with mock.patch.object(CheckClarityContactsInSupr,
                               'fetch_open_projects',
                               return_value=[alt_mock_proj]), \
             mock.patch.object(SuprUtils,
                               'search_by_email',
                               side_effect=NoEmailInClarity()):

            action = self.get_action_instance()
            exit_status, results = action.run(supr_api_url='http://example.com',
                                              supr_api_user='user',
                                              supr_api_key='key')

            # Email marked with dashes should be ignored, and thus
            # the results should be empty here
            self.assertFalse(results)
