#!/usr/share/ucs-test/runner /usr/share/ucs-test/selenium
# -*- coding: utf-8 -*-
## desc: test language switch, logout, module visibility, process timeout
## packages:
##  - univention-management-console-module-ucr
##  - univention-management-console-module-top
## roles-not:
##  - basesystem
## tags:
##  - skip_admember
## join: true
## exposure: dangerous

import time

import psutil

import univention.testing.ucr as ucr_test
import univention.testing.udm as udm_test
from univention.admin import localization
from univention.config_registry import handler_set
from univention.testing import selenium


translator = localization.translation('ucs-test-selenium')
_ = translator.translate


class UmcError(Exception):
    pass


class UMCTester(object):

    def test_umc(self):
        self.selenium.do_login()
        self.test_language_switch()
        self.test_logout()
        try:
            with ucr_test.UCSTestConfigRegistry():
                self.test_module_process_timeout()
        finally:
            self.selenium.restart_umc()
        self.test_module_visibility_for_regular_user()

    def test_language_switch(self):
        switch_to_language = 'de' if (self.selenium.language != 'de') else 'en'
        self.switch_language(switch_to_language)
        self.switch_language(self.selenium.language)

    def test_logout(self):
        self.selenium.open_side_menu()
        self.selenium.click_text(_('Logout'))
        self.selenium.wait_for_text(_('really want to logout'))
        self.selenium.click_button(_('Logout'), xpath_prefix="//div[contains(@class, 'dijitDialog')]")

        self.selenium.do_login(username=self.selenium.umcLoginUsername)

    def test_module_process_timeout(self, timeout=30):
        handler_set(['umc/module/timeout=%s' % (timeout,)])

        self.kill_all_module_processes()
        self.selenium.open_module(_('Univention Configuration Registry'))
        self.selenium.wait_for_text('apache2')
        self.selenium.open_module(_('Process overview'))
        self.selenium.wait_for_text(_('generates an overview'))

        loop_end = time.time() + timeout + 10
        while time.time() < loop_end:
            self.selenium.submit_input('pattern')
            self.selenium.wait_until_all_standby_animations_disappeared()

        if self.module_process_alive('ucr'):
            raise UmcError(
                "A module's process still exists after it's timeout.",
            )
        if not self.module_process_alive('top'):
            raise UmcError("A module's process died before it's timeout.")

    def test_module_visibility_for_regular_user(self):
        username = 'umc_test_user'
        self.udm.create_user(username=username, password='univention')
        self.selenium.end_umc_session()

        self.selenium.do_login(username=username, password='univention')
        self.selenium.end_umc_session()

        self.add_user_policy(username)
        self.add_group_policy(username)

        self.selenium.do_login(username=username, password='univention')
        self.check_if_allowed_modules_are_visible()

    def add_user_policy(self, username):
        self.udm.create_object(
            'policies/umc',
            name='username_policy',
            allow='cn=top-all,cn=operations,cn=UMC,cn=univention,%s' % (self.selenium.ldap_base,),
            position='cn=policies,%s' % (self.selenium.ldap_base,),
        )
        self.udm.modify_object(
            'users/user',
            dn='uid=%s,cn=users,%s' % (username, self.selenium.ldap_base),
            policy_reference='cn=username_policy,cn=policies,%s' % (self.selenium.ldap_base,),
        )

    def add_group_policy(self, username):
        self.udm.create_object(
            'groups/group',
            name='umc_test_group',
            position='cn=groups,%s' % (self.selenium.ldap_base,),
        )
        self.udm.modify_object(
            'users/user',
            dn='uid=%s,cn=users,%s' % (username, self.selenium.ldap_base),
            append={'groups': ['cn=umc_test_group,cn=groups,%s' % (self.selenium.ldap_base,)]},
        )
        self.udm.create_object(
            'policies/umc',
            name='umc_test_group_policy',
            allow='cn=ucr-all,cn=operations,cn=UMC,cn=univention,%s' % (self.selenium.ldap_base,),
            position='cn=policies,%s' % (self.selenium.ldap_base,),
        )
        self.udm.modify_object(
            'groups/group',
            dn='cn=umc_test_group,cn=groups,%s' % (self.selenium.ldap_base,),
            policy_reference='cn=umc_test_group_policy,cn=policies,%s' % (self.selenium.ldap_base,),
        )

    def check_if_allowed_modules_are_visible(self):
        available_modules = self.get_available_modules()
        required_modules = [
            _('Univention Configuration Registry'),
            _('Process overview'),
        ]
        differing_modules = {
            module.lower() for module in required_modules
        }.symmetric_difference({
            module.lower() for module in available_modules
        })
        if len(differing_modules) > 0:
            raise UmcError(
                'Applying module-visibility-policies for a regular user did not'
                ' work.\nThese modules are missing or excess in the UMC: %r'
                % (differing_modules,),
            )

    def kill_all_module_processes(self):
        return  # not necessary, causes Chromium to hang...
        for process in psutil.process_iter():
            if '/usr/sbin/univention-management-console-module' in process.cmdline():
                process.kill()

    def module_process_alive(self, module):
        return any({'/usr/sbin/univention-management-console-module', '-m', module}.issubset(set(process.cmdline())) for process in psutil.process_iter())

    def switch_language(self, target_language_code):
        iso_639_1_to_name = {
            'en': 'English',
            'de': 'Deutsch',
            'fr': u'Français',
        }
        target_language = iso_639_1_to_name[target_language_code]
        self.selenium.open_side_menu()
        self.selenium.click_text(_('Switch language'))
        self.selenium.click_text(target_language)
        self.selenium.click_button(_('Switch language'))

        translator.set_language(target_language_code)

        self.selenium.end_umc_session()
        self.selenium.do_login(language=target_language_code)

    def get_available_modules(self):
        self.selenium.search_module('*')

        xpath = '//*[contains(concat(" ", normalize-space(@class), " "), " umcGalleryName ")]'
        tile_headings = self.selenium.driver.find_elements_by_xpath(xpath)

        return [tile_heading.get_attribute("title") if tile_heading.get_attribute("title") else tile_heading.text for tile_heading in tile_headings]


if __name__ == '__main__':
    with udm_test.UCSTestUDM() as udm, selenium.UMCSeleniumTest() as s:
        umc_tester = UMCTester()
        umc_tester.udm = udm
        umc_tester.selenium = s

        umc_tester.test_umc()
