# -*- coding: utf-8 -*-
#
# Univention Monitoring
#  listener module: update configuration of prometheus alert manager
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

import os
import yaml
from urllib.parse import quote

import requests

from listener import SetUID

import univention.debug as ud
from univention.listener.handler import ListenerModuleHandler
from univention.config_registry import ucr

name = 'monitoring-client'

DIRECTORY = '/var/lib/univention-appcenter/apps/prometheus/conf/'


def safe_path(filename):
	return quote(filename, safe='')


class MonitoringClient(ListenerModuleHandler):

	def initialize(self):
		dirname = os.path.dirname(DIRECTORY)
		if os.path.exists(dirname):
			return
		with self.as_root():
			os.makedirs(dirname)

	def create(self, dn, new):
		with self.as_root():
			self._write_config(new)

	def modify(self, dn, old, new, old_dn):
		with self.as_root():
			self._write_config(new)

	def remove(self, dn, old):
		with self.as_root():
			self._remove_config(old)

	def _write_config(self, attrs):
		if ucr['ldap/hostdn'].encode('UTF-8') not in attrs.get('univentionMonitoringAlertHosts', []):
			return

		name = attrs['cn'][0].decode('UTF-8')
		expr = attrs['univentionMonitoringAlertQuery'][0].decode('UTF-8')
		alert_group = attrs.get('univentionMonitoringAlertGroup', attrs['cn'])[0].decode('UTF-8')
		description = attrs.get('description', [b''])[0].decode('UTF-8')
		summary = attrs.get('univentionMonitoringAlertSummary', [b''])[0].decode('UTF-8')
		for_ = attrs.get('univentionMonitoringAlertFor', [b'10s'])[0].decode('UTF-8')
		labels = [
			label.decode('UTF-8').split('=', 1)
			for label in attrs.get('univentionMonitoringAlertLabel', [b''])
			if label
		]
		alert_config = {
			'groups': [{
				'name': alert_group,
				'rules': [
					{
						'alert': name,
						'expr': expr,
						'for': for_,
						'annotations': {'title': summary, 'description': description},
						'labels': dict(labels),
					}
				]
			}]
		}

		filename = os.path.join(DIRECTORY, safe_path("alert_{}.yml".format(name)))
		with open(filename, "w") as fd:
			fd.write(yaml.dump(alert_config, default_style=None, default_flow_style=False))

	def _remove_config(self, attrs):
		name = attrs['cn'][0].decode('UTF-8')
		filename = os.path.join(DIRECTORY, safe_path("alert_{}.yml".format(name)))
		try:
			os.remove(filename)
		except FileNotFoundError:
			ud.debug(ud.LISTENER, ud.WARN, 'alert definition does not exists: %s' % (filename,))

	def post_run(self):
		# type: () -> None
		ud.debug(ud.LISTENER, ud.INFO, 'Reloading prometheus alert manager')
		url = 'http://localhost/metrics-prometheus/-/reload'
		with SetUID(0), open('/etc/machine.secret') as fd:
			requests.get(url, auth=('%(hostname)ss$' % ucr, fd.read().strip()))

	class Configuration(ListenerModuleHandler.Configuration):
		name = name
		ldap_filter = '(objectClass=univentionMonitoringAlert)'
		description = 'Create configuration for Prometheus AlertManager'