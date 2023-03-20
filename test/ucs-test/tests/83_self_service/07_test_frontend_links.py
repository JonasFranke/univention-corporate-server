#!/usr/share/ucs-test/runner python3
## desc: Tests the Self Service Subpages
## tags: [apptest]
## roles: [domaincontroller_master]
## exposure: dangerous
## packages:
##   - univention-self-service

import importlib
import os
import sys
import time


test_lib = os.environ.get('UCS_TEST_LIB', 'univention.testing.apptest')
try:
    test_lib = importlib.import_module(test_lib)
except ImportError:
    print(f'Could not import {test_lib}. Maybe set $UCS_TEST_LIB')
    sys.exit(1)


LINK_HASHES = ['profiledata', 'createaccount', 'verifyaccount', 'passwordchange', 'passwordreset', 'setcontactinformation']


def get_visible_selfservice_links(chrome):
    elements = chrome.find_all('div.umcHeaderPage a')
    return sorted({elem.get_attribute('href').rsplit('/', 1)[1] for elem in elements})


def assert_link_hashes(links, without):
    wanted_hashes = [link_hash for link_hash in LINK_HASHES if link_hash not in without]
    assert len(links) == len(wanted_hashes)
    for link_hash in wanted_hashes:
        assert f'#page={link_hash}' in links


def goto_selfservice(chrome):
    chrome.get('/univention/self-service/')
    time.sleep(2)


def test_all_links(chrome):
    goto_selfservice(chrome)
    links = get_visible_selfservice_links(chrome)
    assert_link_hashes(links, without=['verifyaccount', 'createaccount'])


def test_disabled_protectaccount(chrome, ucr):
    ucr.set({'umc/self-service/protect-account/frontend/enabled': 'false'})
    goto_selfservice(chrome)
    links = get_visible_selfservice_links(chrome)
    assert_link_hashes(links, without=['setcontactinformation', 'verifyaccount', 'createaccount'])


def test_disabled_passwordreset(chrome, ucr):
    ucr.set({'umc/self-service/passwordreset/frontend/enabled': 'false'})
    goto_selfservice(chrome)
    links = get_visible_selfservice_links(chrome)
    assert_link_hashes(links, without=['passwordreset', 'verifyaccount', 'createaccount'])


def test_disabled_passwordchange(chrome, ucr):
    ucr.set({'umc/self-service/passwordchange/frontend/enabled': 'false'})
    goto_selfservice(chrome)
    links = get_visible_selfservice_links(chrome)
    assert_link_hashes(links, without=['passwordchange', 'verifyaccount', 'createaccount'])


def test_disabled_profiledata(chrome, ucr):
    ucr.set({'umc/self-service/profiledata/enabled': 'false'})
    goto_selfservice(chrome)
    links = get_visible_selfservice_links(chrome)
    assert_link_hashes(links, without=['profiledata', 'verifyaccount', 'createaccount'])


def test_disabled_accountregistration(chrome, ucr):
    ucr.set({'umc/self-service/account-registration/frontend/enabled': 'true'})
    goto_selfservice(chrome)
    links = get_visible_selfservice_links(chrome)
    assert_link_hashes(links, without=['verifyaccount'])


def test_disabled_accountverification(chrome, ucr):
    ucr.set({'umc/self-service/account-verification/frontend/enabled': 'true'})
    goto_selfservice(chrome)
    links = get_visible_selfservice_links(chrome)
    assert_link_hashes(links, without=['createaccount'])


if __name__ == '__main__':
    test_lib.run_test_file(__file__)
