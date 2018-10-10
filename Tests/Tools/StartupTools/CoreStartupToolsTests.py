#!/usr/bin/env python2
# -*- coding: utf-8 -*- 
# CoreStartupTools tests for WxFixBoot Version 3.0.0
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
import wx

#Import test functions & data.
from . import CoreStartupToolsTestFunctions as Functions
from . import CoreStartupToolsTestData as Data

#Import other modules.
sys.path.append('../..') #Need to be able to import the Tools module from here.

import Tools
import Tools.coretools as CoreTools
import Tools.StartupTools.core as CoreStartupTools
import Tests.DialogFunctionsForTests as DialogFunctionsForTests

class TestPanel(wx.Panel):
    def __init__(self, parent):
        """Initialises the panel"""
        wx.Panel.__init__(self, parent=parent)
        self.frame = parent

class TestWindow(wx.Frame):
    def __init__(self):
        """Initialises TestWindow"""
        wx.Frame.__init__(self, parent=None, title="WxFixBoot Tests", size=(1,1), style=wx.SIMPLE_BORDER)

class TestDeterminePackageManager(unittest.TestCase):
    def setUp(self):
        Tools.coretools.startup = True

    def tearDown(self):
        del Tools.coretools.startup

    def testDeterminePackageManager1(self):
        self.assertEqual(CoreStartupTools.determine_package_manager(apt_cmd="which apt-get", yum_cmd="which yum"), Functions.determine_package_manager(apt_cmd="which apt-get", yum_cmd="which yum"))

class TestGetFSTabInfo(unittest.TestCase): #*** Do another test with a fake fstab file(s) XD ***
    def setUp(self):
        Tools.StartupTools.core.DiskInfo = Data.return_empty_disk_info_dict()
        Functions.DiskInfo = Data.return_empty_disk_info_dict()

    def tearDown(self):
        del Tools.StartupTools.core.DiskInfo
        del Functions.DiskInfo

    def testGetFSTabInfo1(self):
        self.assertEqual(CoreStartupTools.get_fstab_info(mount_point="", os_name="ThisIsATest"), Functions.get_fstab_info(mount_point="", os_name="ThisIsATest"))

class TestDetermineOSArchitecture(unittest.TestCase):
    def setUp(self):
        Tools.coretools.startup = True

    def tearDown(self):
        del Tools.coretools.startup

    def testDetermineOSArchitecture1(self):
        self.assertEqual(CoreStartupTools.determine_os_architecture(mount_point=""), Functions.determine_os_architecture(mount_point=""))

class TestGetOSNameWithLSB(unittest.TestCase):
    def setUp(self):
        Tools.coretools.startup = True

    def tearDown(self):
        del Tools.coretools.startup

    def testGetOSNameWithLSB(self):
        self.assertEqual(CoreStartupTools.get_os_name_with_lsb(partition="RootFS", mount_point="", is_current_os=True), Functions.get_os_name_with_lsb(partition="RootFS", mount_point="", is_current_os=True))

class TestAskForOSName(unittest.TestCase):
    def setUp(self):
        self.app = wx.App()
        self.frame = TestWindow()
        self.panel = TestPanel(self.frame)

        DialogFunctionsForTests.parent_window = self.panel

        Tools.StartupTools.core.DialogTools = DialogFunctionsForTests

    def tearDown(self):
        del Tools.StartupTools.core.DialogTools
        del DialogFunctionsForTests.parent_window

        self.panel.Destroy()
        del self.panel

        self.frame.Destroy()
        del self.frame

        self.app.Destroy()
        del self.app

    def testAskForOSName1(self):
        DialogFunctionsForTests.show_real_msg_dlg(message="Enter \"Linux\" in the text entry dialog that you're about to be shown.")
        result = CoreStartupTools.ask_for_os_name(partition="RootFS", is_current_os=True)
        self.assertEqual(DialogFunctionsForTests.MSG_DLG_MESSAGES[-1], "WxFixBoot couldn't find the name of the current OS. Please name it so that WxFixBoot can function correctly.")
        self.assertIsNot(DialogFunctionsForTests.TEXT_ENTRY_DLG_RESULTS[-1], False, "User didn't follow the instructions.")
        self.assertEqual(DialogFunctionsForTests.TEXT_ENTRY_DLG_RESULTS[-1], "Linux")
        self.assertEqual(result, "Linux")

    def testAskForOSName2(self):
        DialogFunctionsForTests.show_real_msg_dlg(message="Click \"No\" in the yes/no dialog that you're about to be shown.")
        result = CoreStartupTools.ask_for_os_name(partition="RootFS", is_current_os=False)
        self.assertFalse(DialogFunctionsForTests.YESNO_DLG_RESULTS[-1], "User didn't follow the instructions.")
        self.assertIsNot(DialogFunctionsForTests.TEXT_ENTRY_DLG_RESULTS[-1], True, "User didn't follow the instructions.")
        self.assertIsNone(result)

    def testAskForOSName3(self):
        DialogFunctionsForTests.show_real_msg_dlg(message="Click \"Yes\" in the yes/no dialog that you're about to be shown, then enter \"Linux\" in the text entry dialog.")
        result = CoreStartupTools.ask_for_os_name(partition="RootFS", is_current_os=False)
        self.assertTrue(DialogFunctionsForTests.YESNO_DLG_RESULTS[-1], "User didn't follow the instructions.")
        self.assertIsNot(DialogFunctionsForTests.TEXT_ENTRY_DLG_RESULTS[-1], False, "User didn't follow the instructions.")
        self.assertEqual(DialogFunctionsForTests.TEXT_ENTRY_DLG_RESULTS[-1], "Linux")
        self.assertEqual(result, "Linux")
