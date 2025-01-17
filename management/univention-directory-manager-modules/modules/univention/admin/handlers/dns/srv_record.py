# -*- coding: utf-8 -*-
#
# Like what you see? Join us!
# https://www.univention.com/about-us/careers/vacancies/
#
# Copyright 2004-2024 Univention GmbH
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

"""|UDM| module for |DNS| service records (SRV)"""

import univention.admin.filter
import univention.admin.handlers
import univention.admin.handlers.dns.forward_zone
import univention.admin.localization
from univention.admin.handlers.dns import DNSBase, is_dns  # noqa: F401
from univention.admin.layout import Group, Tab


translation = univention.admin.localization.translation('univention.admin.handlers.dns')
_ = translation.translate

module = 'dns/srv_record'
operations = ['add', 'edit', 'remove', 'search']
columns = ['location']
superordinate = 'dns/forward_zone'
childs = False
short_description = _('DNS: Service record')
object_name = _('Service record')
object_name_plural = _('Service records')
long_description = _('Resolve well-known services to servers providing those services.')
options = {
    'default': univention.admin.option(
        short_description=short_description,
        default=True,
        objectClasses=['top', 'dNSZone'],
    ),
}
property_descriptions = {
    'name': univention.admin.property(
        short_description=_('Name'),
        long_description=_('The name and protocol of the service.'),
        syntax=univention.admin.syntax.dnsSRVName,
        include_in_default_search=True,
        required=True,
        identifies=True,
    ),
    'location': univention.admin.property(
        short_description=_('Location'),
        long_description=_('The host providing the service.'),
        syntax=univention.admin.syntax.dnsSRVLocation,
        multivalue=True,
        required=True,
    ),
    'zonettl': univention.admin.property(
        short_description=_('Time to live'),
        long_description=_('The time this entry may be cached.'),
        syntax=univention.admin.syntax.UNIX_TimeInterval,
        default=(('3', 'hours'), []),
        dontsearch=True,
    ),
}
layout = [
    Tab(_('General'), _('Basic settings'), layout=[
        Group(_('General service record settings'), layout=[
            'name',
            'location',
            'zonettl',
        ]),
    ]),
]


def unmapName(old, encoding=()):
    # type: (list[bytes], univention.admin.handlers._Encoding) -> list[str]
    items = old[0].decode(*encoding).split(u'.', 2)
    items[0] = items[0][1:]
    items[1] = items[1][1:]
    return items


def mapName(old, encoding=()):
    # type: (list[str], univention.admin.handlers._Encoding) -> bytes
    if len(old) == 1:
        return old[0].encode(*encoding)
    if len(old) == 3 and old[2]:
        return u'_{}._{}.{}'.format(*old).encode(*encoding)
    return u'_{}._{}'.format(*old[:2]).encode(*encoding)


def unmapLocation(old, encoding=()):
    # type: (list[bytes], univention.admin.handlers._Encoding) -> list[list[str]]
    return [
        i.decode(*encoding).split(u' ', 3)
        for i in old
    ]


def mapLocation(old, encoding=()):
    # type: (list[list[str]], univention.admin.handlers._Encoding) -> list[bytes]
    return [
        u' '.join(i).encode(*encoding)
        for i in old
    ]


mapping = univention.admin.mapping.mapping()
mapping.register('name', 'relativeDomainName', mapName, unmapName, encoding='ASCII')
mapping.register('location', 'sRVRecord', mapLocation, unmapLocation, encoding='ASCII')
mapping.register('zonettl', 'dNSTTL', univention.admin.mapping.mapUNIX_TimeInterval, univention.admin.mapping.unmapUNIX_TimeInterval)


class object(DNSBase):
    module = module

    @classmethod
    def unmapped_lookup_filter(cls):
        # type: () -> univention.admin.filter.conjunction
        return univention.admin.filter.conjunction('&', [
            univention.admin.filter.expression('objectClass', 'dNSZone'),
            univention.admin.filter.expression('sRVRecord', '*', escape=False),
        ])


lookup = object.lookup
lookup_filter = object.lookup_filter


def identify(dn, attr, canonical=False):
    # type: (str, univention.admin.handlers._Attributes, bool) -> bool
    return bool(
        attr.get('sRVRecord')
        and is_dns(attr),
    )
