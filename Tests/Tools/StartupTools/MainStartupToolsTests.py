#!/usr/bin/env python
# -*- coding: utf-8 -*- 
# MainStartupTools tests for WxFixBoot Version 3.0.0
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

#Do future imports to prepare to support python 3. Use unicode strings rather than ASCII strings, as they fix potential problems.
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

#Import modules
import unittest
import sys
import os
import wx

#Import test functions & data.
from . import MainStartupToolsTestFunctions as Functions
from . import MainStartupToolsTestData as Data

#Import other modules.
sys.path.append('../../..') #Need to be able to import the Tools module from here.

import Tools
import Tools.coretools as CoreTools
import Tools.StartupTools.core as CoreStartupTools
import Tools.StartupTools.main as MainStartupTools
import Tests.DialogFunctionsForTests as DialogTools

import getdevinfo
import getdevinfo.linux

class TestPanel(wx.Panel):
    def __init__(self, parent):
        """Initialises the panel"""
        wx.Panel.__init__(self, parent=parent)
        self.frame = parent

class TestWindow(wx.Frame):
    def __init__(self):
        """Initialises TestWindow"""
        wx.Frame.__init__(self, parent=None, title="WxFixBoot Tests", size=(1, 1), style=wx.SIMPLE_BORDER)

class TestCheckDepends(unittest.TestCase):
    def setUp(self):
        Tools.coretools.startup = True

    def tearDown(self):
        del Tools.coretools.startup

        #Reset emergency exit stuff.
        Functions.WOULD_EMERGENCY_EXIT = False
        Functions.WOULD_EMERGENCY_EXIT_BECAUSE = []

    def testCheckDepends1(self):
        #Run the Functions version first, because it will be a problem for us if a real Emergency exit is triggered.
        Functions.check_depends()
        self.assertFalse(Functions.WOULD_EMERGENCY_EXIT, Functions.WOULD_EMERGENCY_EXIT_BECAUSE) #Let user know about the problem.

        #If we got here okay, run the real thing. If it runs without error, we're fine.
        MainStartupTools.check_depends()

class TestCheckForLiveDisk(unittest.TestCase):
    def setUp(self):
        self.app = wx.App()
        self.frame = TestWindow()
        self.panel = TestPanel(self.frame)

        DialogTools.parent_window = self.panel

        Tools.coretools.startup = True

    def tearDown(self):
        del Tools.coretools.startup
        del DialogTools.parent_window

        self.panel.Destroy()
        del self.panel

        self.frame.Destroy()
        del self.frame

        self.app.Destroy()
        del self.app

    def testCheckForLiveDisk1(self):
        Functions.check_for_live_disk()
        MainStartupTools.check_for_live_disk()

        self.assertEqual(Functions.SystemInfo, Tools.StartupTools.main.SystemInfo)

class TestGetOSs(unittest.TestCase):
    def setUp(self):
        self.app = wx.App()
        self.frame = TestWindow()
        self.panel = TestPanel(self.frame)

        DialogTools.parent_window = self.panel
        Tools.coretools.startup = True
        self.DiskInfo = getdevinfo.getdevinfo.get_info() #We need real disk info for these ones.
        Functions.DiskInfo = self.DiskInfo
        Tools.StartupTools.main.DiskInfo = self.DiskInfo
        Tools.StartupTools.core.DiskInfo = self.DiskInfo

    def tearDown(self):
        del DialogTools.parent_window
        del Tools.coretools.startup
        del Tools.StartupTools.main.DiskInfo
        del Tools.StartupTools.core.DiskInfo
        del Functions.DiskInfo
        del self.DiskInfo

        self.panel.Destroy()
        del self.panel

        self.frame.Destroy()
        del self.frame

        self.app.Destroy()
        del self.app

    def testGetOSs1(self):
        #Only run if there are Linux OSs, because otherwise the unmodified functions could cause an emergency exit which would mess up testing.
        if Functions.get_oss() != ("Unknown", "Unknown"):
            self.assertEqual(MainStartupTools.get_oss(), Functions.get_oss())

class TestGetFirmwareType(unittest.TestCase):
    def setUp(self):
        self.app = wx.App()
        self.frame = TestWindow()
        self.panel = TestPanel(self.frame)

        DialogTools.parent_window = self.panel

        Tools.coretools.startup = True

    def tearDown(self):
        del Tools.coretools.startup
        del DialogTools.parent_window

    def testGetFirmwareType1(self):
        #Run them.
        MainStartupTools.get_firmware_type()
        Functions.get_firmware_type()

        #Test that the result is the same.
        self.assertEqual(Tools.StartupTools.main.SystemInfo, Functions.SystemInfo)

        #If a dialog was going to be displayed to the user, make sure it would be displayed both times.
        if DialogTools.MSG_DLG_MESSAGES and DialogTools.MSG_DLG_MESSAGES[-1] == "Your computer uses UEFI firmware, but the UEFI variables couldn't be mounted or weren't found. Please ensure you've booted in UEFI mode rather than legacy mode to enable access to the UEFI variables. You can attempt installing a UEFI bootloader without them, but it might not work, and it isn't recommended.":
            self.assertEqual(DialogTools.MSG_DLG_MESSAGES[-1], DialogTools.MSG_DLG_MESSAGES[-2])

class TestFinalCheck(unittest.TestCase):
    def setUp(self):
        Tools.StartupTools.main.DialogTools = DialogTools

    def tearDown(self):
        del Tools.StartupTools.main.DialogTools
        del Tools.StartupTools.main.BootloaderInfo #Will be present after test.
        DialogTools.MSG_DLG_MESSAGES = [] #Reset so we can check if there are any new messages from the 2nd test.

    def testFinalCheck1(self):
        #Get the dict for this test.
        Tools.StartupTools.main.BootloaderInfo = Data.return_fake_bl_info1()
        MainStartupTools.final_check()
        self.assertEqual(DialogTools.MSG_DLG_MESSAGES[-1], Data.return_final_check_results1())

    def testFinalCheck2(self):
        #Get the dict for this test.
        Tools.StartupTools.main.BootloaderInfo = Data.return_fake_bl_info2()
        MainStartupTools.final_check()
        self.assertFalse(DialogTools.MSG_DLG_MESSAGES)
