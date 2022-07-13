#!/usr/share/ucs-test/runner pytest-3 -s -l -vv
## desc: Change active flag to TRUE by domaincontroller master
## tags: [udm,udm-ldapextensions,apptest]
## roles: [domaincontroller_master,domaincontroller_backup,domaincontroller_slave,memberserver]
## exposure: dangerous
## packages:
##   - univention-directory-manager-tools

import base64
import bz2

import pytest

from univention.testing.strings import random_name, random_ucs_version, random_version
from univention.testing.udm_extensions import (
	VALID_EXTENSION_TYPES, get_extension_buffer, get_extension_filename, get_extension_name,
	get_package_name, get_package_version,
)
from univention.testing.utils import verify_ldap_object, wait_for_replication_and_postrun


@pytest.mark.tags('udm', 'udm-ldapextensions', 'apptest')
@pytest.mark.roles('domaincontroller_master', 'domaincontroller_backup', 'domaincontroller_slave', 'memberserver')
@pytest.mark.exposure('dangerous')
@pytest.mark.parametrize('extension_type', VALID_EXTENSION_TYPES)
def test_listener_check_active(udm, extension_type, ucr):
	"""Change active flag to TRUE by domaincontroller master"""
	print('========================= TESTING EXTENSION %s =============================' % extension_type)
	extension_name = get_extension_name(extension_type)
	extension_filename = get_extension_filename(extension_type, extension_name)
	extension_buffer = get_extension_buffer(extension_type, extension_name)

	package_name = get_package_name()
	package_version = get_package_version()
	app_id = '%s-%s' % (random_name(), random_version())
	version_start = random_ucs_version(max_major=2)
	version_end = random_ucs_version(min_major=5)

	dn = udm.create_object(
		'settings/udm_%s' % extension_type,
		name=extension_name,
		data=base64.b64encode(bz2.compress(extension_buffer.encode("UTF-8"))).decode("ASCII"),
		filename=extension_filename,
		packageversion=package_version,
		appidentifier=app_id,
		package=package_name,
		ucsversionstart=version_start,
		ucsversionend=version_end,
		active='FALSE',
		position='cn=udm_%s,cn=univention,%s' % (extension_type, ucr['ldap/base'])
	)

	wait_for_replication_and_postrun()

	verify_ldap_object(dn, {
		'cn': [extension_name],
		'univentionUDM%sFilename' % extension_type.capitalize(): [extension_filename],
		'univentionOwnedByPackage': [package_name],
		'univentionObjectType': ['settings/udm_%s' % extension_type],
		'univentionOwnedByPackageVersion': [package_version],
		'univentionUDM%sData' % extension_type.capitalize(): [bz2.compress(extension_buffer.encode('UTF-8'))],
		'univentionAppIdentifier': [app_id],
		'univentionUCSVersionStart': [version_start],
		'univentionUCSVersionEnd': [version_end],
		'univentionUDM%sActive' % extension_type.capitalize(): ['TRUE'],
	})