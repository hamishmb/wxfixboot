#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# EssentialBackendTools test data for WxFixBoot
# This file is part of WxFixBoot.
# Copyright (C) 2013-2019 Hamish McIntyre-Bhatty
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

#Do future imports to prepare to support python 3. Use unicode strings rather than ASCII
#strings, as they fix potential problems.
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

#Functions to return test data.
def return_initial_system_info_dict():
    return {"DisableBootloaderOperations": False, "DisableBootloaderOperationsBecause": []}

def return_system_info_dict_with_disabled_bl_opts():
    return {"DisableBootloaderOperations": True,
            "DisableBootloaderOperationsBecause": ["Internet Connection test failed."]}

def return_system_info_dict_with_enabled_bl_opts():
    return {"DisableBootloaderOperations": False, "DisableBootloaderOperationsBecause": []}
