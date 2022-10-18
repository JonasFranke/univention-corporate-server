#!/usr/bin/python3
# vim:set fileencoding=utf-8:
#
# Unit tests for ucr type checking
#
# Copyright 2022 Univention GmbH
#
# https://www.univention.de/
#
# All rights reserved.
#
# The source code of this program is made available
# under the terms of the GNU Affero General Public License version 3
# (GNU AGPL V3) as published by the Free Software Foundation.
#
# Binary versions of this program provided by Univention to you as
# well as other copyrighted, protected or trademarked materials like
# Logos, graphics, fonts, specific documentations and configurations,
# cryptographic keys etc. are subject to a license agreement between
# you and Univention and not subject to the GNU AGPL V3.
#
# In the case you use this program under the terms of the GNU AGPL V3,
# the program is provided in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public
# License with the Debian GNU/Linux or Univention distribution in file
# /usr/share/common-licenses/AGPL-3; if not, see
# <https://www.gnu.org/licenses/>.

"""Unit test for univention.config_registry.validation."""

import pytest
import univention.config_registry.validation as ttyp


@pytest.mark.parametrize(
	'value',
	[
		'String',
		'1234',
		'',
	]
)
def test_string(value):
	sval = ttyp.String({})
	assert sval.is_valid(value)


@pytest.mark.parametrize(
	('regex', 'expected'),
	[
		('^(19|20)\\d\\d[- /.](0[1-9]|1[012])[- /.](0[1-9]|[12][0-9]|3[01])$', True),
		('/foo\\1/', False),
		('', True),
	]
)
def test_string_set_regex(regex, expected):
	sval = ttyp.String({})
	try:
		sval.regex = regex
	except ValueError:
		assert not expected
	else:
		assert expected


@pytest.mark.parametrize(
	('value', 'regex', 'expected'),
	[
		('http://univention.de', '^(https?)://(www)?.?(\\w+).(\\w+)/?(\\w+)?', True),
		('2021-12-31', '^(19|20)\\d\\d[- /.](0[1-9]|1[012])[- /.](0[1-9]|[12][0-9]|3[01])$', True),
		('2021-13-31', '^(19|20)\\d\\d[- /.](0[1-9]|1[012])[- /.](0[1-9]|[12][0-9]|3[01])$', False),
	]
)
def test_string_regex(value, regex, expected):
	sval = ttyp.String({"regex": regex})
	assert sval.is_valid(value) == expected


@pytest.mark.parametrize(
	("value", "expected"),
	[
		('http://1.2.3.4', True),
		('https://1.2.3.4', True),
		('http://1.2.3.4:3128', True),
		('http://foo:bar@1.2.3.4:3128', True),
		('http://a%3ab%40c:a%3ab%40c@[1:2::7]:3128', True),
		('http://[0::1]', True),
		('http://[0::1]:3128', True),
		('http://proxy', True),
		('http://proxy.my.domain:3128', True),
		('http://localhost/', False),
		('http://localhost/path', False),
		('http://localhost?query', False),
		('http://localhost#fragment', False),
		('ldap://', False),
	]
)
def test_url_proxy(value, expected):
	up = ttyp.URLProxy({})
	assert up.is_valid(value) == expected


IPV4 = [
	('192.168.1.42', True),
	('1234', False),  # FIXME: use --ignore-check for now
	('127.0.0.1', True),
	('255.255.255.255', True),
	('192.4.5.256', False),
]
IPV6 = [
	('0123:4567:89ab:cdef:0123:4567:89AB:CDEF', True),
	('0:1:2:3:4:5:6:7', True),
	('0::1', True),
	('0::2::3', False),
	('::1.2.3.4', True),
]
IPV6_ONLY = [
	('1.2.3.4', False),
]


@pytest.mark.parametrize(('value', 'expected'), IPV4)
def test_ipv4address(value, expected):
	ipa = ttyp.IPv4Address({})
	assert ipa.is_valid(value) == expected


@pytest.mark.parametrize(('value', 'expected'), IPV6 + IPV6_ONLY)
def test_ipv6address(value, expected):
	ipa = ttyp.IPv6Address({})
	assert ipa.is_valid(value) == expected


@pytest.mark.parametrize(('value', 'expected'), IPV4 + IPV6)
def test_ipaddress(value, expected):
	ipa = ttyp.IPAddress({})
	assert ipa.is_valid(value) == expected


@pytest.mark.parametrize(
	('value', 'expected'),
	[
		('42', True),
		('', False),
		('Text', False),
		(' 42', True),
		('12345678', True),
		('-500', True),
		('0', True),
	]
)
def test_integer(value, expected):
	ival = ttyp.Integer({})
	assert ival.is_valid(value) == expected


@pytest.mark.parametrize(
	('value', 'min', 'max', 'expected'),
	[
		('50', None, None, True),
		('42', '10', None, True),
		('42', '42', None, True),
		('42', '43', None, False),
		('42', None, '42', True),
		('22', None, '42', True),
		('42', None, '40', False),
		('42', '0', '42', True),
		('0', '0', '42', True),
		('22', '0', '42', True),
		('-1', '0', '42', False),
		('43', '0', '42', False),
	]
)
def test_integer_range(value, min, max, expected):
	ival = ttyp.Integer({"min": min, "max": max})
	assert ival.is_valid(value) == expected


@pytest.mark.parametrize(
	('min', 'max', 'expected'),
	[
		(None, None, True),
		('10', '10', True),
		('10', '100', True),
		('10', None, True),
		(None, '200', True),
		('10 ', ' 100', True),
		('100', '10', False),
		('text', '10', False),
		(None, 'text', False),
		('100', 'text', False),
	]
)
def test_integer_set_range(min, max, expected):
	ival = ttyp.Integer({})
	try:
		ival.min = min
		ival.max = max
	except (TypeError, ValueError):
		assert not expected
	else:
		assert expected


@pytest.mark.parametrize(
	('value', 'expected'),
	[
		('-1', False),
		('0', True),
		('1', True),
	]
)
def test_uinteger(value, expected):
	uval = ttyp.UnsignedNumber({})
	assert uval.is_valid(value) == expected


@pytest.mark.parametrize(
	('value', 'expected'),
	[
		('-1', False),
		('0', False),
		('1', True),
	]
)
def test_pinteger(value, expected):
	pval = ttyp.PositiveNumber({})
	assert pval.is_valid(value) == expected


@pytest.mark.parametrize(
	('port', 'expected'),
	[
		('42', True),
		('', False),
		('Text', False),
		(' 42', True),
		('-1', False),
		('0', True),
		('65535', True),
		('65536', False),
	]
)
def test_portnumber(port, expected):
	pp = ttyp.PortNumber({})
	assert pp.is_valid(port) == expected


@pytest.mark.parametrize(
	('value', 'expected'),
	[
		('Yes', True),
		('yes', True),
		('TRUE', True),
		('true', True),
		('1', True),
		('ENABLE', True),
		('enable', True),
		('ENABLED', True),
		('enabled', True),
		('ENABLE', True),
		('ON', True),
		('on', True),
		('No', True),
		('no', True),
		('FALSE', True),
		('false', True),
		('0', True),
		('DISABLE', True),
		('disable', True),
		('DISABLED', True),
		('disabled', True),
		('OFF', True),
		('off', True),
		('', False),
		('text', False),
		('y', False),
		('n', False),
	]
)
def test_bool(value, expected):
	bb = ttyp.Bool({})
	assert bb.is_valid(value) == expected


@pytest.mark.parametrize(
	('value', 'expected'),
	[
		('{"name": "Egon Testmann", "salary": 9000, "email": "egon@testmail.com",}', False),
		('{"name": "Egon Testmann", "salary": 9000, "email": "egon@testmail.com"}', True),
	]
)
def test_json(value, expected):
	jj = ttyp.Json({})
	assert jj.is_valid(value) == expected


@pytest.fixture()
def var():
	"""Fake Variable type."""
	return {
		"description": "description",
		"categories": "category",
		"default": "default",
	}


@pytest.mark.parametrize(
	('value', 'element_type', 'separator', 'expected'),
	[
		('abc,12,cde', 'str', None, True),
		('"abc", "fgh" ,"cde"', 'str', None, True),
		('abc;12;cde', 'str', ';', True),
		('abc;fgh;cde', 'str', ';', True),
		('abc,12,cde', 'str', ';', True),
		('abc, fgh, cde', 'str', '#', True),
		('10,20 , 30', 'int', None, True),
		('10,aaa,30', 'int', None, False),
		('10,20,aaa', 'int', None, False),
		('10;20 ; 30', 'int', ';', True),
		('10; 20; 30', 'int', ';', True),
		('10,20,30', 'int', ';', False),
		('10, -5555, 30', 'int', None, True),
		('true,false,0', 'bool', None, True),
		('true,false,42', 'bool', None, False),
		('true;false;0', 'bool', ';', True),
		('true, false,0', 'bool', None, True),
		('{"name": "Egon Testmann", "salary": 9000, "email": "egon@testmail.com"};{"name": "Hans Wurst", "car": "Audi"}', 'json', ';', True),
		('{"name": "Egon Testmann", "salary": 9000, "email": "egon@testmail.com"};{42}', 'json', ';', False),
	]
)
def test_list(value, element_type, separator, expected, var):
	var['type'] = 'list'
	var['elementtype'] = element_type
	if separator is not None:
		var['separator'] = separator
	checker = ttyp.List(var)
	assert checker.is_valid(value) == expected


@pytest.mark.parametrize(
	('name', 'typ'),
	[
		('int', ttyp.Integer),
		('uint', ttyp.UnsignedNumber),
		('pint', ttyp.PositiveNumber),
		('bool', ttyp.Bool),
		('ipv4address', ttyp.IPv4Address),
		('ipv6address', ttyp.IPv6Address),
		('ipaddress', ttyp.IPAddress),
		('url_proxy', ttyp.URLProxy),
		('portnumber', ttyp.PortNumber),
		('str', ttyp.String),
		('json', ttyp.Json),
		('list', ttyp.List),
	]
)
def test_type(name, typ, var):
	var['type'] = name

	tt = ttyp.Type(var)
	assert isinstance(tt.checker, typ)