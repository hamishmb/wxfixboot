#!/usr/bin/env python
# -*- coding: utf-8 -*- 
# MainStartupTools tests for WxFixBoot Version 2.0.1
# This file is part of WxFixBoot.
# Copyright (C) 2013-2017 Hamish McIntyre-Bhatty
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

#Do future imports to prepare to support python 3. Use unicode strings rather than ASCII strings, as they fix potential problems.
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

#Import modules
import unittest
import wx

#Import test functions & data.
from . import MainStartupToolsTestFunctions as Functions
from . import MainStartupToolsTestData as Data

class TestCheckDepends(unittest.TestCase):
    def setUp(self):
        Tools.coretools.Startup = True
        Functions.CoreTools = CoreTools()

    def tearDown(self):
        del Tools.coretools.Startup
        del Functions.CoreTools

        #Reset emergency exit stuff.
        Functions.WouldEmergencyExit = False
        Functions.WouldEmergencyExitBecause = []

    def testCheckDepends1(self):
        #Run the Functions version first, because it will be a problem for us if a real Emergency exit is triggered.
        Functions.CheckDepends()
        self.assertFalse(Functions.WouldEmergencyExit, Functions.WouldEmergencyExitBecause) #Let user know about the problem.

        #If we got here okay, run the real thing. If it runs without error, we're fine.
        MainStartupTools().CheckDepends()

class TestCheckForLiveDisk(unittest.TestCase):
    def setUp(self):
        Tools.coretools.Startup = True

        Tools.StartupTools.main.SystemInfo = {}

        Functions.SystemInfo = {}
        Functions.CoreTools = CoreTools()
        Functions.CoreStartupTools = CoreStartupTools()

    def tearDown(self):
        del Tools.coretools.Startup
        del Tools.StartupTools.main.SystemInfo
        del Functions.SystemInfo
        del Functions.CoreTools
        del Functions.CoreStartupTools

    def testCheckForLiveDisk1(self):
        Functions.CheckForLiveDisk()
        MainStartupTools().CheckForLiveDisk()

        self.assertEqual(Functions.SystemInfo, Tools.StartupTools.main.SystemInfo)
