#!/usr/bin/env python3
# -*- coding: utf-8 -*- 
# MainStartupTools tests for WxFixBoot
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

# pylint: disable=too-many-ancestors, too-few-public-methods, wrong-import-order
#
# Reason (too-many-ancestors): These are wxPython ancestors.
# Reason (too-few-public-methods): Test classes.
# Reason (wrong-import-order): These are just unit tests.

#Do future imports to prepare to support python 3. Use unicode strings rather than ASCII
#strings, as they fix potential problems.
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

#Import modules
import unittest
import sys
import copy
import wx
import getdevinfo
import getdevinfo.linux

#Import test functions & data.
from . import MainStartupToolsTestFunctions as Functions
from . import MainStartupToolsTestData as Data

#Import other modules.
sys.path.append('../../..') #Need to be able to import the Tools module from here.

import Tools
from Tools.dictionaries import *
import Tools.StartupTools.main as MainStartupTools
import Tests.DialogFunctionsForTests as DialogTools

class TestPanel(wx.Panel):
    def __init__(self, parent):
        """Initialises the panel"""
        wx.Panel.__init__(self, parent=parent)
        self.frame = parent

class TestWindow(wx.Frame):
    def __init__(self):
        """Initialises TestWindow"""
        wx.Frame.__init__(self, parent=None, title="WxFixBoot Tests", size=(1, 1),
                          style=wx.SIMPLE_BORDER)

        self.panel = TestPanel(self)

class TestCheckDepends(unittest.TestCase):
    def setUp(self):
        Tools.coretools.STARTUP = True

    def tearDown(self):
        del Tools.coretools.STARTUP

        #Reset emergency exit stuff.
        Functions.WOULD_EMERGENCY_EXIT = False
        Functions.WOULD_EMERGENCY_EXIT_BECAUSE = []

    def test_check_depends_1(self):
        """Test #1: Test that we can check dependencies without error."""
        #Run the Functions version first, because it will be a problem for us if a real Emergency
        #exit is triggered.
        Functions.check_depends()

        #Let user know about the problem.
        self.assertFalse(Functions.WOULD_EMERGENCY_EXIT, Functions.WOULD_EMERGENCY_EXIT_BECAUSE)

        #If we got here okay, run the real thing. If it runs without error, we're fine.
        MainStartupTools.check_depends()

class TestCheckForLiveDisk(unittest.TestCase):
    def setUp(self):
        self.app = wx.App()
        self.frame = TestWindow()

        Tools.coretools.STARTUP = True
        SYSTEM_INFO.clear()

    def tearDown(self):
        del Tools.coretools.STARTUP

        self.frame.Destroy()
        del self.frame

        self.app.Destroy()
        del self.app

    def test_check_for_live_disk_1(self):
        """Test #1: Test that we can determine if on a live disk without error"""
        MainStartupTools.check_for_live_disk()

class TestGetOSs(unittest.TestCase):
    def setUp(self):
        self.app = wx.App()
        self.frame = TestWindow()
        self.maxDiff = None

        Tools.coretools.STARTUP = True
        Tools.StartupTools.core.DialogTools = DialogTools

        DISK_INFO.update(getdevinfo.getdevinfo.get_info()) #We need real disk info for these ones.

    def tearDown(self):
        del Tools.coretools.STARTUP
        del Tools.StartupTools.core.DialogTools

        DISK_INFO.clear()

        self.frame.Destroy()
        del self.frame

        self.app.Destroy()
        del self.app

    def test_get_oss_1(self):
        """Test #1: Test that we can get OS information without error"""
        #Only run if there are Linux OSs, because otherwise the unmodified functions could cause
        #an emergency exit which would mess up testing.
        #TODO There may be a better way of doing this.
        if Functions.get_oss() != ("Unknown", "Unknown"):
            MainStartupTools.get_oss()

class TestGetFirmwareType(unittest.TestCase):
    def setUp(self):
        self.app = wx.App()
        self.frame = TestWindow()

        SYSTEM_INFO.clear()

        Tools.coretools.STARTUP = True

    def tearDown(self):
        del Tools.coretools.STARTUP

    def test_get_firmware_type_1(self):
        """Test #1: Test that we can get the firmware type without error"""
        MainStartupTools.get_firmware_type()

class TestFinalCheck(unittest.TestCase):
    def setUp(self):
        Tools.StartupTools.main.DialogTools = DialogTools

    def tearDown(self):
        del Tools.StartupTools.main.DialogTools

        BOOTLOADER_INFO.clear()

        #Reset so we can check if there are any new messages from the 2nd test.
        DialogTools.MSG_DLG_MESSAGES = []

    def test_final_check_1(self):
        """Test #1: Test that the final check warns about not being able to modify macOS and Windows when they are present"""

        #Get the dict for this test.
        BOOTLOADER_INFO.update(Data.return_fake_bl_info1())
        MainStartupTools.final_check()
        self.assertEqual(DialogTools.MSG_DLG_MESSAGES[-1], Data.return_final_check_results1())

    def test_final_check_2(self):
        """Test #2: Test that the final check runs without error when it should"""
        #Get the dict for this test.
        BOOTLOADER_INFO.update(Data.return_fake_bl_info2())
        MainStartupTools.final_check()
        self.assertFalse(DialogTools.MSG_DLG_MESSAGES)
