#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Uses getdevinfo to gather device information when requested for WxFixBoot.
# This file is part of WxFixBoot.
# Copyright (C) 2013-2020 Hamish McIntyre-Bhatty
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
This is used to run getdevinfo to obtain device information.
This must be run as root to work correctly on Linux.
"""

import sys

import getdevinfo

sys.stdout.write(str(getdevinfo.getdevinfo.get_info()))
sys.exit(0)
