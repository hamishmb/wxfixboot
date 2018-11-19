#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# Dictionaries in the Tools Package for WxFixBoot Version 3.0.0
# This file is part of WxFixBoot.
# Copyright (C) 2013-2018 Hamish McIntyre-Bhatty
# WxFixBoot is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License version 3 or,
# at your option, any later version.
#
# WxFixBoot is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with WxFixBoot.  If not, see <http://www.gnu.org/licenses/>.

"""
This module holds the shared dictionaries used by the rest of the program.
All you need to do to gain access to the shared dictionaries is import this module.
"""

if not 'SYSTEM_INFO' in globals():
    SYSTEM_INFO = {}

if not 'DISK_INFO' in globals():
    DISK_INFO = {}

if not 'OS_INFO' in globals():
    OS_INFO = {}

if not 'BOOTLOADER_INFO' in globals():
    BOOTLOADER_INFO = {}

if not 'SETTINGS' in globals():
    SETTINGS = {}
