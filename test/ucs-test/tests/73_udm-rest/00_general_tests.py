#!/usr/share/ucs-test/runner pytest-3 -s
## desc: Test various functions in the UDM REST API
## tags: [udm,apptest]
## roles: [domaincontroller_master]
## exposure: careful
## packages:
##   - univention-directory-manager-rest

import subprocess
import time

import pytest

from univention.admin.rest.client import UDM as UDMClient, Forbidden, PreconditionFailed, Unauthorized
from univention.config_registry import ConfigRegistry, handler_set
from univention.lib.misc import custom_groupname
from univention.testing.udm import UDM, UCSTestUDM_CreateUDMObjectFailed
from univention.testing.utils import UCSTestDomainAdminCredentials

ucr = ConfigRegistry()
ucr.load()


if ucr.is_true('ad/member'):
	# REST server needs to reload UCR variables for "Domain Adminis" group name
	subprocess.call(['service', 'univention-directory-manager-rest', 'restart'])


class UDMClient(UDMClient):

	@classmethod
	def master_connection(cls, username, password):
		return cls.http('https://%s/univention/udm/' % (ucr['ldap/master'],), username, password)

	@classmethod
	def test_connection(cls):
		account = UCSTestDomainAdminCredentials(ucr)
		return cls.master_connection(account.username, account.bindpw)


def test_authentication(udm):
	userdn, user = udm.create_user()

	print('1. invalid password must be detected')
	with pytest.raises(Unauthorized):
		udm_client = UDMClient.master_connection(user, 'foobar')
		udm_client.get('users/user')

	print('2. regular domain user must not access the API')
	with pytest.raises(Forbidden):
		udm_client = UDMClient.master_connection(user, 'univention')
		udm_client.get('users/user')

	udm.modify_object('users/user', dn=userdn, groups='cn=%s,cn=groups,%s' % (custom_groupname('Domain Admins', ucr), ucr['ldap/base'],))
	print('3. domain admin must be able to access the API')
	udm_client = UDMClient.master_connection(user, 'univention')
	udm_client.get('users/user')


def test_etag_last_modified(udm):
	userdn, user = udm.create_user()
	time.sleep(1)
	udm_client = UDMClient.test_connection()
	user = udm_client.get('users/user').get(userdn)
	assert user.etag
	assert user.last_modified
	last_modified = user.last_modified
	user.last_modified = None
	udm.modify_object('users/user', dn=userdn, description='foo')
	time.sleep(1)
	user.properties['lastname'] = 'foobar'
	with pytest.raises(PreconditionFailed) as exc:
		user.save()
	# assert 'If-Match' in str(exc)

	user.last_modified = last_modified
	user.etag = None
	with pytest.raises(PreconditionFailed) as exc:
		user.save()
	exc
	# assert 'If-Unmodified-Since' in str(exc)


@pytest.mark.parametrize('suffix', ['', 'ä'])
def test_create_modify_move_remove(random_string, suffix, ucr):
	if suffix:
		handler_set(['directory/manager/web/modules/users/user/properties/username/syntax=string'])
		subprocess.call(['systemctl', 'restart', 'univention-directory-manager-rest'])
		time.sleep(1)

	with UDM() as udm:
		username = random_string() + suffix
		userdn, user = udm.create_user(username=username)
		udm.verify_ldap_object(userdn)
		org_dn = userdn

		username = random_string() + suffix

		description = random_string()
		userdn = udm.modify_object('users/user', dn=userdn, description=description)
		udm.verify_ldap_object(userdn)
		assert userdn == org_dn

		userdn = udm.modify_object('users/user', dn=userdn, username=username)
		udm.verify_ldap_object(userdn)
		assert userdn != org_dn
		org_dn = userdn

		userdn = udm.move_object('users/user', dn=userdn, position=ucr['ldap/base'])
		udm.verify_ldap_object(userdn)
		assert userdn != org_dn

		udm.remove_object('users/user', dn=userdn)
		udm.verify_ldap_object(userdn, should_exist=False)


@pytest.mark.parametrize('name', [
	'''a !"#$%&'"()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~z''',
	'foo//bar',
	'foobär',
])
def test_special_characters_in_dn(name):
	with UDM() as udm:
		container = udm.create_object('container/cn', name=name)

		udm_client = UDMClient.test_connection()
		obj = udm_client.get('container/cn').get(container)
		print(obj)
		assert obj


@pytest.mark.parametrize('language,error_message', [
	('en-US', 'The property gecos has an invalid value: Field must only contain ASCII characters!'),
	('de-DE', 'Die Eigenschaft gecos hat einen ungültigen Wert: Der Wert darf nur ASCII Buchstaben enthalten!'),
])
def test_translation(language, error_message):
	with UDM(language=language) as udm:
		with pytest.raises(UCSTestUDM_CreateUDMObjectFailed) as exc:
			userdn, user = udm.create_user(gecos='foobär')

		assert error_message in str(exc.value)
