#!/usr/bin/env python
# -*- coding: utf-8 -*- 
# HelperBackendTools tests for WxFixBoot Version 2.0.1
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
from . import HelperBackendToolsTestFunctions as Functions
from . import HelperBackendToolsTestData as Data

#Setup test functions.
Functions.os = os

class TestPanel(wx.Panel):
    def __init__(self, parent):
        """Initialises the panel"""
        wx.Panel.__init__(self, parent=parent)
        self.frame = parent

class TestWindow(wx.Frame):
    def __init__(self):
        """Initialises TestWindow"""
        wx.Frame.__init__(self, parent=None, title="WxFixBoot Tests", size=(1,1), style=wx.SIMPLE_BORDER)

class TestWaitUntilPackageManagerNotInUse(unittest.TestCase):
    def setUp(self):
        self.app = wx.App()
        self.Frame = TestWindow()
        self.Panel = TestPanel(self.Frame)
        Functions.ParentWindow = self

        Tools.coretools.Startup = True

    def tearDown(self):
        del Tools.coretools.Startup
        del Functions.ParentWindow

        self.Panel.Destroy()
        del self.Panel

        self.Frame.Destroy()
        del self.Frame

        self.app.Destroy()
        del self.app

    def testWaitUntilPackageManagerNotInUse1(self):
        DialogFunctionsForTests.ShowRealMsgDlg("Please ensure the package manager is not in use.")
        HelperBackendTools().WaitUntilPackageManagerNotInUse(MountPoint="", PackageManager="apt-get")

    def testWaitUntilPackageManagerNotInUse2(self):
        #Ask user to enable internet connection.
        DialogFunctionsForTests.ShowRealMsgDlg("Please open Synaptic or similar to lock the package manager, then click ok. After a few seconds, close it.")
        HelperBackendTools().WaitUntilPackageManagerNotInUse(MountPoint="", PackageManager="apt-get")

class TestFindMissingFSCKModules(unittest.TestCase):
    def setUp(self):
        Tools.coretools.Startup = True
        Tools.BackendTools.helpers.DiskInfo = Data.ReturnFakeDiskInfo()
        Functions.DiskInfo = Data.ReturnFakeDiskInfo()
        Functions.CoreTools = CoreTools()

    def tearDown(self):
        del Tools.coretools.Startup
        del Tools.BackendTools.helpers.DiskInfo
        del Functions.DiskInfo
        del Functions.CoreTools

    @unittest.skipUnless(Functions.CanPerformFindMissingFSCKModulesTest1(), "FSCK modules not available on system.")
    def testFindMissingFSCKModules1(self):
        self.assertEqual(HelperBackendTools().FindMissingFSCKModules(), Data.ReturnExpectedResultFindingMissingFSCKModules())

    def testFindMissingFSCKModules2(self):
        self.assertEqual(HelperBackendTools().FindMissingFSCKModules(), Functions.FindMissingFSCKModules())

class TestFindCheckableFileSystems(unittest.TestCase):
    def setUp(self):
        self.app = wx.App()
        self.Frame = TestWindow()
        self.Panel = TestPanel(self.Frame)
        Functions.ParentWindow = self

        Tools.coretools.Startup = True
        DevInfoTools().GetInfo(Standalone=True) #We need real disk info for these ones.
        self.DiskInfo = GetDevInfo.getdevinfo.DiskInfo
        Functions.DiskInfo = self.DiskInfo
        Functions.CoreTools = CoreTools()
        Tools.BackendTools.helpers.DiskInfo = self.DiskInfo
        Tools.BackendTools.helpers.DialogTools = DialogFunctionsForTests

    def tearDown(self):
        del Tools.coretools.Startup
        del GetDevInfo.getdevinfo.DiskInfo
        del self.DiskInfo
        del Functions.DiskInfo
        del Functions.CoreTools
        del Tools.BackendTools.helpers.DiskInfo
        del Tools.BackendTools.helpers.DialogTools
        del Functions.ParentWindow

        self.Panel.Destroy()
        del self.Panel

        self.Frame.Destroy()
        del self.Frame

        self.app.Destroy()
        del self.app

    def testFindCheckableFileSystems1(self):
        #More setup.
        Tools.BackendTools.helpers.SystemInfo = Data.ReturnInitialSystemInfoDict()
        Functions.SystemInfo = Data.ReturnInitialSystemInfoDict()

        #Test.
        self.assertEqual(HelperBackendTools().FindCheckableFileSystems(), Functions.FindCheckableFileSystems())

        #More teardown.
        del Tools.BackendTools.helpers.SystemInfo
        del Functions.SystemInfo

class TestHandleFilesystemCheckReturnValues(unittest.TestCase):
    def setUp(self):
        self.app = wx.App()
        self.Frame = TestWindow()
        self.Panel = TestPanel(self.Frame)
        Functions.ParentWindow = self

        self.SystemInfo = Data.ReturnInitialSystemInfoDict()
        Tools.BackendTools.helpers.SystemInfo = self.SystemInfo
        Tools.BackendTools.helpers.DialogTools = DialogFunctionsForTests

    def tearDown(self):
        del self.SystemInfo
        del Tools.BackendTools.helpers.SystemInfo
        del Tools.BackendTools.helpers.DialogTools

        self.Panel.Destroy()
        del self.Panel

        self.Frame.Destroy()
        del self.Frame

        self.app.Destroy()
        del self.app

    def testHandleFilesystemCheckReturnValues1(self):
        #All of these should behave in exactly the same way.
        HelperBackendTools().HandleFilesystemCheckReturnValues(ExecCmds="xfs_repair -Pvd /dev/sda1", Retval=1, Partition="/dev/sda1")
        self.assertEqual(DialogFunctionsForTests.MsgDlgMessages[-1], "Corruption was found on the filesystem: /dev/sda1! Fortunately, it looks like the checker utility has fixed the corruption. Click okay to continue.")

        HelperBackendTools().HandleFilesystemCheckReturnValues(ExecCmds="xfs_repair -Pvd /dev/sda1", Retval=2, Partition="/dev/sda1")
        self.assertEqual(DialogFunctionsForTests.MsgDlgMessages[-1], "Corruption was found on the filesystem: /dev/sda1! Fortunately, it looks like the checker utility has fixed the corruption. Click okay to continue.")

        HelperBackendTools().HandleFilesystemCheckReturnValues(ExecCmds="xfs_repair -Pvd /dev/sda1", Retval=3, Partition="/dev/sda1")
        self.assertEqual(DialogFunctionsForTests.MsgDlgMessages[-1], "Corruption was found on the filesystem: /dev/sda1! Fortunately, it looks like the checker utility has fixed the corruption. Click okay to continue.")
