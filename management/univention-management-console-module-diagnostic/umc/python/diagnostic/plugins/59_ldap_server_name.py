#!/usr/bin/python3
# -*- coding: utf-8 -*-

import univention.uldap
from univention.config_registry import handler_set as ucr_set, ucr_live as ucr
from univention.lib.i18n import Translation
from univention.management.console.modules.diagnostic import Critical, Warning

_ = Translation('univention-management-console-module-diagnostic').translate

title = _('Check primary LDAP server')

run_descr = ['This can be checked by running: ucr get ldap/server/name']


links = [{
	'name': 'sdb',
	'href': 'https://help.univention.com/t/changing-the-primary-ldap-server-to-redistribute-the-server-load/14138',
	'label': _('Univention Support Database - Change the primary LDAP Server to redistribute the server load')
}]


def deactivate_test(umc_instance):
	ucr_set(['diagnostic/check/disable/59_ldap_server_name=yes'])


actions = {
	'deactivate_test': deactivate_test,
}


def run(_umc_instance):
	if ucr.is_true('diagnostic/check/disable/59_ldap_server_name') or ucr.get('server/role') != 'memberserver':
		return

	ldap_server_name = ucr.get('ldap/server/name')
	domainname = ucr.get('domainname')
	lo = univention.uldap.getMachineConnection()
	master = lo.search(base=ucr.get('ldap/base'), filter='(univentionServerRole=master)', attr=['cn'])
	try:
		master_cn = master[0][1].get('cn')[0].decode('UTF-8')
	except IndexError:
		raise Critical('Could not find a Primary Directory Node %s' % (master,))

	master_fqdn = '.'.join([master_cn, domainname])

	if master_fqdn == ldap_server_name:
		res = lo.searchDn(base=ucr.get('ldap/base'), filter='univentionServerRole=backup')

		# Case: ldap/server/name is the Primary Directory Node and there are Backup Directory Nodes available.
		if res:
			button = [{
				'action': 'deactivate_test',
				'label': _('Deactivate test'),
			}]
			warn = (_('The primary LDAP Server of this System (UCR ldap/server/name) is set to the Primary Directory Node of this UCS domain (%s).\nSince this environment provides further LDAP Servers, we recommend a different configuration to reduce the load on the Primary Directory Node.\nPlease see {sdb} for further information.') % (master_fqdn,))
			raise Warning(warn, buttons=button)


if __name__ == '__main__':
	from univention.management.console.modules.diagnostic import main
	main()
