#!/usr/bin/env python
# -*- coding: utf-8 -*- 
# CoreStartupTools tests for WxFixBoot Version 2.0.1
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
from . import CoreStartupToolsTestFunctions as Functions
from . import CoreStartupToolsTestData as Data

class TestDeterminePackageManager(unittest.TestCase):
    def setUp(self):
        Tools.coretools.Startup = True
        Functions.CoreTools = CoreTools()

    def tearDown(self):
        del Tools.coretools.Startup
        del Functions.CoreTools

    def testDeterminePackageManager1(self):
        self.assertEqual(CoreStartupTools().DeterminePackageManager(APTCmd="which apt-get", YUMCmd="which yum"), Functions.DeterminePackageManager(APTCmd="which apt-get", YUMCmd="which yum"))

class TestGetFSTabInfo(unittest.TestCase): #*** Do another test with a fake fstab file(s) XD ***
    def setUp(self):
        Tools.StartupTools.core.DiskInfo = Data.ReturnEmptyDiskInfoDict()
        Functions.DiskInfo = Data.ReturnEmptyDiskInfoDict()

    def tearDown(self):
        del Tools.StartupTools.core.DiskInfo
        del Functions.DiskInfo

    def testGetFSTabInfo1(self):
        self.assertEqual(CoreStartupTools().GetFSTabInfo(MountPoint="", OSName="ThisIsATest"), Functions.GetFSTabInfo(MountPoint="", OSName="ThisIsATest"))

class TestDetermineOSArchitecture(unittest.TestCase):
    def setUp(self):
        Tools.coretools.Startup = True
        Functions.CoreTools = CoreTools()

    def tearDown(self):
        del Tools.coretools.Startup
        del Functions.CoreTools

    def testDetermineOSArchitecture1(self):
        self.assertEqual(CoreStartupTools().DetermineOSArchitecture(MountPoint=""), Functions.DetermineOSArchitecture(MountPoint=""))

class TestGetOSNameWithLSB(unittest.TestCase):
    def setUp(self):
        Tools.coretools.Startup = True
        Functions.CoreTools = CoreTools()

    def tearDown(self):
        del Tools.coretools.Startup
        del Functions.CoreTools

    def testGetOSNameWithLSB(self):
        self.assertEqual(CoreStartupTools().GetOSNameWithLSB(Partition="RootFS", MountPoint="", IsCurrentOS=True), Functions.GetOSNameWithLSB(Partition="RootFS", MountPoint="", IsCurrentOS=True))

class TestAskForOSName(unittest.TestCase):
    def setUp(self):
        self.app = wx.App()

        Tools.StartupTools.core.DialogTools = DialogFunctionsForTests

    def tearDown(self):
        del Tools.StartupTools.core.DialogTools

        self.app.Destroy()
        del self.app

    def testAskForOSName1(self):
        DialogFunctionsForTests.ShowRealMsgDlg(Message="Enter \"Linux\" in the text entry dialog that you're about to be shown.")
        Result = CoreStartupTools().AskForOSName(Partition="RootFS", OSArch="x86_64", IsCurrentOS=True)
        self.assertEqual(DialogFunctionsForTests.MsgDlgMessages[-1], "WxFixBoot couldn't find the name of the current OS. Please name it so that WxFixBoot can function correctly.")
        self.assertIsNot(DialogFunctionsForTests.TextEntryDlgResults[-1], False, "User didn't follow the instructions.")
        self.assertEqual(DialogFunctionsForTests.TextEntryDlgResults[-1], "Linux")
        self.assertEqual(Result, "Linux")

    def testAskForOSName2(self):
        DialogFunctionsForTests.ShowRealMsgDlg(Message="Click \"No\" in the yes/no dialog that you're about to be shown.")
        Result = CoreStartupTools().AskForOSName(Partition="RootFS", OSArch="x86_64", IsCurrentOS=False)
        self.assertFalse(DialogFunctionsForTests.YesNoDlgResults[-1], "User didn't follow the instructions.")
        self.assertIsNot(DialogFunctionsForTests.TextEntryDlgResults[-1], True, "User didn't follow the instructions.")
        self.assertIsNone(Result)

    def testAskForOSName3(self):
        DialogFunctionsForTests.ShowRealMsgDlg(Message="Click \"Yes\" in the yes/no dialog that you're about to be shown, then enter \"Linux\" in the text entry dialog.")
        Result = CoreStartupTools().AskForOSName(Partition="RootFS", OSArch="x86_64", IsCurrentOS=False)
        self.assertTrue(DialogFunctionsForTests.YesNoDlgResults[-1], "User didn't follow the instructions.")
        self.assertIsNot(DialogFunctionsForTests.TextEntryDlgResults[-1], False, "User didn't follow the instructions.")
        self.assertEqual(DialogFunctionsForTests.TextEntryDlgResults[-1], "Linux")
        self.assertEqual(Result, "Linux")
