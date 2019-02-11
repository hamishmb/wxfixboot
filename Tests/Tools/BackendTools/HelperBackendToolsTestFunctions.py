#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# HelperBackendTools test functions for WxFixBoot
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

#Import modules
import os
import sys

#Import other modules.
sys.path.append('../../..') #Need to be able to import the Tools module from here.

from Tools.dictionaries import *
import Tools.coretools as CoreTools

#Checks if system can perform certain tests.
def can_perform_find_missing_fsck_modules_test_1():
    return (os.path.isfile("/sbin/fsck.jfs") and os.path.isfile("/sbin/fsck.ext4")
            and os.path.isfile("/sbin/fsck.ext3") and os.path.isfile("/sbin/fsck.vfat"))
