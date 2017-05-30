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
import os

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

class TestGetOSs(unittest.TestCase):
    def setUp(self):
        self.app = wx.App()

        Tools.coretools.Startup = True
        DevInfoTools().GetInfo(Standalone=True) #We need real disk info for these ones.
        self.DiskInfo = GetDevInfo.getdevinfo.DiskInfo
        Functions.DiskInfo = self.DiskInfo
        Tools.StartupTools.main.DiskInfo = self.DiskInfo
        Tools.StartupTools.core.DiskInfo = self.DiskInfo
        Tools.StartupTools.core.os = os

        Tools.StartupTools.main.SystemInfo = {}
        Functions.SystemInfo = {}

        Functions.CoreTools = CoreTools()
        Functions.CoreStartupTools = CoreStartupTools()
        Functions.os = os

        Tools.StartupTools.core.DialogTools = DialogFunctionsForTests

    def tearDown(self):
        del Tools.coretools.Startup
        del GetDevInfo.getdevinfo.DiskInfo
        del self.DiskInfo
        del Functions.DiskInfo
        del Functions.SystemInfo
        del Functions.CoreTools
        del Functions.CoreStartupTools
        del Functions.os
        del Tools.StartupTools.main.DiskInfo
        del Tools.StartupTools.core.DiskInfo
        del Tools.StartupTools.core.os
        del Tools.StartupTools.main.SystemInfo
        del Tools.StartupTools.core.DialogTools

        self.app.Destroy()
        del self.app

    def testGetOSs1(self):
        #Only run if there are Linux OSs, because otherwise the unmodified functions could cause an emergency exit which would mess up testing.
        if Functions.GetOSs() != ("Unknown", "Unknown"):
            self.assertEqual(MainStartupTools().GetOSs(), Functions.GetOSs())

class TestGetFirmwareType(unittest.TestCase):
    def setUp(self):
        self.app = wx.App()

        Tools.coretools.Startup = True

        Tools.StartupTools.main.SystemInfo = {}
        Tools.StartupTools.main.DialogTools = DialogFunctionsForTests

        Functions.SystemInfo = {}
        Functions.CoreTools = CoreTools()
        Functions.DialogTools = DialogFunctionsForTests
        Functions.os = os

    def tearDown(self):
        del Tools.coretools.Startup
        del Tools.StartupTools.main.SystemInfo
        del Tools.StartupTools.main.DialogTools
        del Functions.SystemInfo
        del Functions.CoreTools
        del Functions.DialogTools
        del Functions.os

    def testGetFirmwareType1(self):
        #Run them.
        MainStartupTools().GetFirmwareType()
        Functions.GetFirmwareType()

        #Test that the result is the same.
        self.assertEqual(Tools.StartupTools.main.SystemInfo, Functions.SystemInfo)

        #If a dialog was going to be displayed to the user, make sure it would be displayed both times.
        if len(DialogFunctionsForTests.MsgDlgMessages) > 0 and DialogFunctionsForTests.MsgDlgMessages[-1] == "Your computer uses UEFI firmware, but the UEFI variables couldn't be mounted or weren't found. Please ensure you've booted in UEFI mode rather than legacy mode to enable access to the UEFI variables. You can attempt installing a UEFI bootloader without them, but it might not work, and it isn't recommended.":
            self.assertEqual(DialogFunctionsForTests.MsgDlgMessages[-1], DialogFunctionsForTests.MsgDlgMessages[-2])

class TestFinalCheck(unittest.TestCase):
    def setUp(self):
        Tools.StartupTools.main.DialogTools = DialogFunctionsForTests

    def tearDown(self):
        del Tools.StartupTools.main.DialogTools
        del Tools.StartupTools.main.BootloaderInfo #Will be present after test.
        DialogFunctionsForTests.MsgDlgMessages = [] #Reset so we can check if there are any new messages from the 2nd test.

    def testFinalCheck1(self):
        #Get the dict for this test.
        Tools.StartupTools.main.BootloaderInfo = Data.ReturnFakeBLInfo1()
        MainStartupTools().FinalCheck()
        self.assertEqual(DialogFunctionsForTests.MsgDlgMessages[-1], Data.ReturnFinalCheckResults1())

    def testFinalCheck2(self):
        #Get the dict for this test.
        Tools.StartupTools.main.BootloaderInfo = Data.ReturnFakeBLInfo2()
        MainStartupTools().FinalCheck()
        self.assertTrue(len(DialogFunctionsForTests.MsgDlgMessages) == 0)
