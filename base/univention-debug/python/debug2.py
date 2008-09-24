#!/usr/bin/python2.4
# -*- coding: utf-8 -*-
#
# Univention Debug2
#  debug2.py
#
# Copyright (C) 2008 Univention GmbH
#
# http://www.univention.de/
#
# All rights reserved.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.
#
# Binary versions of this file provided by Univention to you as
# well as other copyrighted, protected or trademarked materials like
# Logos, graphics, fonts, specific documentations and configurations,
# cryptographic keys etc. are subject to a license agreement between
# you and Univention.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import logging
#import logging.handlers

ERROR = 0
WARN = 1
PROCESS = 2
INFO = 3
ALL = 4
DEFAULT = WARN

# The default levels provided are DEBUG(10), INFO(20), WARNING(30), ERROR(40) and CRITICAL(50).
# Mapping old levels to new ones
_map_lvl_old2new = {
	0: logging.ERROR,    # 40
	1: logging.WARNING,  # 30
	2: 25,               # 25
	3: logging.INFO,     # 20
	4: logging.DEBUG,    # 10
}

MAIN = 0x00
LDAP = 0x01
USERS = 0x02
NETWORK = 0x03
SSL = 0x04
SLAPD = 0x05
SEARCH = 0x06
TRANSFILE = 0x07
LISTENER = 0x08
POLICY = 0x09
ADMIN = 0x0A
CONFIG = 0x0B
LICENSE = 0x0C
KERBEROS = 0x0D
DHCP = 0x0E

_map_id_old2new = {
	MAIN: "MAIN",
	LDAP: "LDAP",
	USERS: "USERS",
	NETWORK: "NETWORK",
	SSL: "SSL",
	SLAPD: "SLAPD",
	SEARCH: "SEARCH",
	TRANSFILE: "TRANSFILE",
	LISTENER: "LISTENER",
	POLICY: "POLICY",
	ADMIN: "ADMIN",
	CONFIG: "CONFIG",
	LICENSE: "LICENSE",
	KERBEROS: "KERBEROS",
	DHCP: "DHCP",
}


#13.08.08 13:13:57  LISTENER    ( ERROR   ) : listener: 1
#13.08.08 13:13:57  LISTENER    ( WARN    ) : received signal 2
#13.08.08 13:14:02  DEBUG_INIT
_outfmt = '%(asctime)s,%(msecs)d %(name)-11s (%(levelname)-7s): %(message)s'
_outfmt_syslog = '%(name)-11s (%(levelname)-7s): %(message)s'
_datefmt = '%d.%m.%Y %H:%M:%S'

_logfilename = None
_handler_console = None
_handler_file = None
_handler_syslog = None
_do_flush = False
_enable_function = False
_enable_syslog = False
_logger_level = {}

# set default level for each logger
for key in _map_id_old2new.values():
	_logger_level[key] = _map_lvl_old2new[DEFAULT]

def init( logfilename, do_flush=0, enable_function=0, enable_syslog=0 ):
	_logfilename = logfilename

	# create root logger
	logging.basicConfig(level=logging.DEBUG,       # disabled
						filename = '/dev/null',
						format = _outfmt,
						datefmt = _datefmt)

	formatter = logging.Formatter( _outfmt, _datefmt )
	if logfilename == 'stderr' or logfilename == 'stdout':
		# add stderr or stdout handler
		try:
			if logfilename == 'stdout':
				_handler_console = logging.StreamHandler( sys.stdout )
			else:
				_handler_console = logging.StreamHandler( sys.stderr )
			_handler_console.setLevel( logging.DEBUG )
			_handler_console.setFormatter(formatter)
			logging.getLogger('').addHandler(_handler_console)
		except:
			print 'opening %s failed' % logfilename
	else:
		try:
			# add file handler
			_handler_file = logging.FileHandler( logfilename, 'a+' )
			_handler_file.setLevel( logging.DEBUG )
			_handler_file.setFormatter(formatter)
			logging.getLogger('').addHandler(_handler_file)
		except:
			print 'opening %s failed' % logfilename

# 	if enable_syslog:
# 		try:
# 			# add syslog handler
# 			_handler_syslog = logging.handlers.SysLogHandler( ('localhost', 514), logging.handlers.SysLogHandler.LOG_ERR )
# 			_handler_syslog.setLevel( _map_lvl_old2new[ERROR] )
# 			_handler_syslog.setFormatter(formatter)
# 			logging.getLogger('').addHandler(_handler_syslog)
# 		except:
# 			raise
# 			print 'opening syslog failed'

	logging.addLevelName( 25, 'PROCESS' )
	logging.addLevelName( 99, 'ALL' )
	logging.addLevelName( 100, '------' )

	logging.getLogger('MAIN').log( _map_lvl_old2new[ ALL ], 'DEBUG_INIT' )

	_do_flush = do_flush
	_enable_function = enable_function
	_enable_syslog = enable_syslog


def reopen():
	init( _logfilename, _do_flush, _enable_function, _enable_syslog )

def set_level( id, level ):
	new_id = _map_id_old2new.get(id, 'MAIN')
	new_level = _map_lvl_old2new[ level ]
	_logger_level[ new_id ] = new_level

def set_function( activated ):
	_enable_function = activated


def debug( id, level, msg, utf8=1 ):
	new_id = _map_id_old2new.get(id, 'MAIN')
	new_level = _map_lvl_old2new[ level ]
	if new_level >= _logger_level[ new_id ]:
		logging.getLogger( new_id ).log( new_level, msg )
	if _do_flush:
		logging.flush()

class function:
	def __init__(self, text,  utf8=1):
		self.text=text
		if _enable_function:
			logging.getLogger('MAIN').log( _map_lvl_old2new[ ALL ], 'UNIVENTION_DEBUG_BEGIN : ' + self.text )
		if _do_flush:
			logging.flush()

	def __del__(self):
		if _enable_function:
			logging.getLogger('MAIN').log( _map_lvl_old2new[ ALL ], 'UNIVENTION_DEBUG_END   : ' + self.text )
		if _do_flush:
			logging.flush()
