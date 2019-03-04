#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# CoreTools test data for WxFixBoot
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
def return_fake_commands():
    dictionary = {}
    dictionary["echo 'This is a test of the fire alarm system'"] = {}
    dictionary["echo 'This is a test of the fire alarm system'"]["Output"] = "This is a test of the fire alarm system\n"
    dictionary["echo 'This is a test of the fire alarm system'"]["Retval"] = 0
    dictionary["sh -c \"echo 'This returns 2'; exit 2\""] = {}
    dictionary["sh -c \"echo 'This returns 2'; exit 2\""]["Output"] = "This returns 2\n"
    dictionary["sh -c \"echo 'This returns 2'; exit 2\""]["Retval"] = 2
    dictionary["sh -c \"TIMES=1; while [ $TIMES -lt 6 ]; do echo 'Slow task'; sleep 2; TIMES=$(( $TIMES + 1 )); done\""] = {}
    dictionary["sh -c \"TIMES=1; while [ $TIMES -lt 6 ]; do echo 'Slow task'; sleep 2; TIMES=$(( $TIMES + 1 )); done\""]["Output"] = "Slow task\nSlow task\nSlow task\nSlow task\nSlow task\n"
    dictionary["sh -c \"TIMES=1; while [ $TIMES -lt 6 ]; do echo 'Slow task'; sleep 2; TIMES=$(( $TIMES + 1 )); done\""]["Retval"] = 0
    dictionary[""" sh -c "TIMES=1; while [ $TIMES -lt 6000 ]; do echo 'Fast Task'; sleep 0.001; TIMES=$(( $TIMES + 1 )); done" """] = {}
    dictionary[""" sh -c "TIMES=1; while [ $TIMES -lt 6000 ]; do echo 'Fast Task'; sleep 0.001; TIMES=$(( $TIMES + 1 )); done" """]["Output"] = "Fast Task\n"*5999
    dictionary[""" sh -c "TIMES=1; while [ $TIMES -lt 6000 ]; do echo 'Fast Task'; sleep 0.001; TIMES=$(( $TIMES + 1 )); done" """]["Retval"] = 0

    return dictionary
