/*
 * Python Heimdal
 *	Bindings for the credentials API of heimdal
 *
 * Like what you see? Join us!
 * https://www.univention.com/about-us/careers/vacancies/
 *
 * Copyright 2003-2022 Univention GmbH
 *
 * https://www.univention.de/
 *
 * All rights reserved.
 *
 * The source code of this program is made available
 * under the terms of the GNU Affero General Public License version 3
 * (GNU AGPL V3) as published by the Free Software Foundation.
 *
 * Binary versions of this program provided by Univention to you as
 * well as other copyrighted, protected or trademarked materials like
 * Logos, graphics, fonts, specific documentations and configurations,
 * cryptographic keys etc. are subject to a license agreement between
 * you and Univention and not subject to the GNU AGPL V3.
 *
 * In the case you use this program under the terms of the GNU AGPL V3,
 * the program is provided in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 * GNU Affero General Public License for more details.
 *
 * You should have received a copy of the GNU Affero General Public
 * License with the Debian GNU/Linux or Univention distribution in file
 * /usr/share/common-licenses/AGPL-3; if not, see
 * <https://www.gnu.org/licenses/>.
 */
#ifndef __CREDS_H__
#define __CREDS_H__

#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <krb5.h>
#include "context.h"

typedef struct {
	PyObject_HEAD
	krb5ContextObject *context;
	krb5_creds creds;
} krb5CredsObject;

PyTypeObject krb5CredsType;

krb5CredsObject *creds_from_creds(krb5ContextObject *context, krb5_creds creds);
krb5CredsObject *creds_new(PyObject *unused, PyObject *args);

#endif /* __CREDS_H__ */
