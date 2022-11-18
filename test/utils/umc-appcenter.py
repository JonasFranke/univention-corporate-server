#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
install/remove/update apps via UMC
"""

import os
from argparse import ArgumentParser
from tempfile import gettempdir
from time import sleep
from typing import Any, Dict, Optional

from requests import get

import univention.lib.umc
from univention.config_registry import ucr
from univention.appcenter.actions import get_action
from univention.appcenter.app_cache import Apps as FindApps
from univention.appcenter.utils import call_process, get_local_fqdn


class Apps(object):

	def __init__(self) -> None:
		parser = ArgumentParser(description=__doc__)
		parser.add_argument("-U", "--username", help="username", required=True)
		parser.add_argument("-p", "--password", help="password", required=True)
		parser.add_argument("-a", "--app", help="app id", required=True)
		parser.add_argument("-r", "--remove", action="store_true", help="remove app")
		parser.add_argument("-u", "--update", action="store_true", help="upgrade app")
		parser.add_argument(
			"-i", "--ignore-no-update",
			action="store_true",
			help="normally -u fails if no update is available, with this switch just return in that case")
		self.options = parser.parse_args()
		self.client = None  # type: Optional[univention.lib.umc.Client]
		print(self.options)

	def umc(self, path: str, data: Dict[str, Any]) -> Dict[str, Any]:
		print('-> invoke {path} with options {data}'.format(path=path, data=data))
		if self.client is None:
			self.client = univention.lib.umc.Client(username=self.options.username, password=self.options.password)
		print('-> headers: {headers}'.format(headers=self.client._headers))
		resp = self.client.umc_command(path, data)
		assert resp.status == 200
		result = resp.result
		print('<- {res}'.format(res=result))
		return result

	def wait(self, result: Dict[str, Any], app: str) -> None:
		pid = result['id']
		path = 'appcenter/progress'
		data = {"progress_id": pid}
		waited = 0
		while waited <= 720:
			sleep(10)
			waited += 1
			try:
				result = self.umc(path, data)
			except univention.lib.umc.ConnectionError:
				print('... Apache down? Ignoring...')
				continue

			for message in result.get('intermediate', []):
				print('   {msg}'.format(msg=message.get('message')))

			if result.get('finished', False):
				break
		else:
			raise Exception("wait timeout")
		print(result)
		assert result['result'][get_local_fqdn()][app]['success'] is True

	def run_script(self, app_id: str, script: str) -> None:
		app = FindApps().find(app_id)
		url = os.path.join('http://appcenter-test.software-univention.de', 'univention-repository', app.get_ucs_version(), 'maintained', 'component', app.component_id, 'test_%s' % script)
		print(url)
		response = get(url)
		if response.ok is not True:
			print(' no %s script found for app %s: %r' % (script, app.id, response.content))
			return
		fname = os.path.join(gettempdir(), '%s.%s' % (app.id, script))
		with open(fname, 'wb') as f:
			f.write(response.content)

		os.chmod(fname, 0o755)
		bind_dn = ucr.get('tests/domainadmin/account')
		if bind_dn is None:
			bind_dn = 'uid=Administrator,%(ldap/base)s' % ucr

		pwd_file = ucr.get('tests/domainadmin/pwdfile')
		unlink_pwd_file = False
		if pwd_file is None:
			pwd_file = '/tmp/app-installation.pwd'
			with open(pwd_file, 'w') as fd:
				fd.write('univention')

			unlink_pwd_file = True

		try:
			cmd = [fname, '--binddn', bind_dn, '--bindpwdfile', pwd_file]
			print('running ', cmd)
			assert call_process(cmd).returncode == 0
		finally:
			if unlink_pwd_file:
				os.unlink(pwd_file)

	def make_args(self, action: str, app: str) -> Dict[str, Any]:
		host = get_local_fqdn()
		settings = {}  # type: Dict[str, Any]
		return {
			"action": action,
			"auto_installed": [],
			"hosts": {host: app},
			"apps": [app],
			"dry_run": False,
			"settings": {app: settings},
		}

	def run_action(self, action: str, app: str) -> None:
		data = self.make_args(action, app)
		resp = self.umc("appcenter/run", data)
		self.wait(resp, app)

	def install(self) -> None:
		self.run_script(self.options.app, 'preinstall')
		self.run_action("install", self.options.app)

	def uninstall(self) -> None:
		self.run_script(self.options.app, 'preremove')
		self.run_action("remove", self.options.app)

	def update(self) -> None:
		self.run_script(self.options.app, 'preupgrade')
		result = self.umc('appcenter/get', {"application": self.options.app})
		for host in result.get('installations', []):
			if host == ucr['hostname']:
				print('-> installations: {inst}'.format(inst=result['installations']))
				if result['installations'][host]['update_available']:
					break
		else:
			if self.options.ignore_no_update:
				return
		self.run_action("upgrade", self.options.app)

	def main(self) -> None:
		update = get_action('update')
		update.call()
		if self.options.remove:
			self.uninstall()
		elif self.options.update:
			self.update()
		else:
			self.install()


if __name__ == '__main__':
	apps = Apps()
	apps.main()
