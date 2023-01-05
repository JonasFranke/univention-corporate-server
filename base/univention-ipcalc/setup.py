#!/usr/bin/python3
# Like what you see? Join us!
# https://www.univention.com/about-us/careers/vacancies/
#
# SPDX-License-Identifier: AGPL-3.0
# Copyright 2021-2023 Univention GmbH

from setuptools import setup

version = open("debian/changelog", "r").readline().split()[1][1:-1]

setup(
    version=version,
)
