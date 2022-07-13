#!/usr/share/ucs-test/runner pytest-3 -s -l -vv
## desc: Create full UDM extension objects via CLI
## tags: [udm,udm-ldapextensions,apptest]
## roles: [domaincontroller_master,domaincontroller_backup,domaincontroller_slave,memberserver]
## exposure: dangerous
## packages:
##   - univention-directory-manager-tools

import base64
import bz2

import pytest

import univention.testing.udm as udm_test
from univention.testing.strings import random_name, random_ucs_version, random_version
from univention.testing.udm_extensions import (
	VALID_EXTENSION_TYPES, get_extension_buffer, get_extension_filename, get_extension_name,
	get_package_name, get_package_version,
)


@pytest.mark.tags('udm', 'udm-ldapextensions', 'apptest')
@pytest.mark.roles('domaincontroller_master', 'domaincontroller_backup', 'domaincontroller_slave', 'memberserver')
@pytest.mark.exposure('dangerous')
@pytest.mark.parametrize('extension_type', VALID_EXTENSION_TYPES)
@pytest.mark.parametrize('version_start,version_end', [
	(random_ucs_version(max_major=2), random_name()),
	(random_name(), random_ucs_version(min_major=5)),
	(random_name(), random_name())
])
def test_create_with_invalid_ucsversions(udm, extension_type, version_start, version_end):
	"""Create full UDM extension objects via CLI"""
	print('========================= TESTING EXTENSION %s =============================' % extension_type)
	extension_name = get_extension_name(extension_type)
	extension_filename = get_extension_filename(extension_type, extension_name)
	extension_buffer = get_extension_buffer(extension_type, extension_name)

	package_name = get_package_name()
	package_version = get_package_version()
	app_id = '%s-%s' % (random_name(), random_version())

	with pytest.raises(udm_test.UCSTestUDM_CreateUDMObjectFailed):
		udm.create_object(
			'settings/udm_%s' % extension_type,
			name=extension_name,
			data=base64.b64encode(bz2.compress(extension_buffer.encode("UTF-8"))).decode("ASCII"),
			filename=extension_filename,
			packageversion=package_version,
			appidentifier=app_id,
			package=package_name,
			ucsversionstart=version_start,
			ucsversionend=version_end,
			active='FALSE'
		)