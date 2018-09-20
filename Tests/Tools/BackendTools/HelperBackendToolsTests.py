#!/usr/bin/env python
# -*- coding: utf-8 -*-
# HelperBackendTools tests for WxFixBoot Version 3.0.0
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

# pylint: disable=too-many-ancestors, too-few-public-methods, wrong-import-order, no-self-use
#
# Reason (too-many-ancestors): These are wxPython ancestors.
# Reason (too-few-public-methods): Test classes.
# Reason (wrong-import-order): These are just unit tests.
# Reason (no-self-use): Just test methods.

#Do future imports to prepare to support python 3. Use unicode strings rather than ASCII
#strings, as they fix potential problems.
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

#Import modules
import unittest
import sys
import subprocess
import wx

import getdevinfo
import getdevinfo.linux

#Import other modules.
sys.path.append('../../..') #Need to be able to import the Tools module from here.

import Tools
from Tools.dictionaries import *
import Tools.BackendTools.helpers as HelperBackendTools
import Tests.DialogFunctionsForTests as DialogTools

#Declare global dictionaries to silence pylint warnings.
SystemInfo = {}
DiskInfo = {}

#Import test functions & data.
from . import HelperBackendToolsTestFunctions as Functions
from . import HelperBackendToolsTestData as Data

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

class TestWaitUntilPackageManagerFree(unittest.TestCase):
    def setUp(self):
        self.app = wx.App()
        self.frame = TestWindow()

        Tools.coretools.startup = True

    def tearDown(self):
        del Tools.coretools.startup

        self.frame.Destroy()
        del self.frame

        self.app.Destroy()
        del self.app

    @unittest.skipUnless(subprocess.Popen("which apt-get", shell=True, stdout=subprocess.PIPE).wait() == 0, "Package Manager isn't apt-get.")
    def test_wait_until_packagemanager_free_1(self):
        DialogTools.show_real_msg_dlg("Please ensure the package manager is not in use.")
        HelperBackendTools.wait_until_packagemanager_free(mount_point="",
                                                          package_manager="apt-get")

    @unittest.skipUnless(subprocess.Popen("which apt-get", shell=True, stdout=subprocess.PIPE).wait() == 0, "Package Manager isn't apt-get.")
    def test_wait_until_packagemanager_free_2(self):
        #Ask user to enable internet connection.
        DialogTools.show_real_msg_dlg("Please open Synaptic or similar to lock the package "
                                      + "manager, then click ok. After a few seconds, close it.")

        HelperBackendTools.wait_until_packagemanager_free(mount_point="",
                                                          package_manager="apt-get")

    @unittest.skipUnless(subprocess.Popen("which yum", shell=True, stdout=subprocess.PIPE).wait() == 0, "Package Manager isn't yum.")
    def test_wait_until_packagemanager_free_3(self):
        DialogTools.show_real_msg_dlg("Please ensure the package manager is not in use.")
        HelperBackendTools.wait_until_packagemanager_free(mount_point="",
                                                          package_manager="yum")

    @unittest.skipUnless(subprocess.Popen("which yum", shell=True, stdout=subprocess.PIPE).wait() == 0, "Package Manager isn't yum.")
    def test_wait_until_packagemanager_free_4(self):
        #Ask user to enable internet connection.
        DialogTools.show_real_msg_dlg("Please open YUM Extender or similar to lock the package "
                                      + "manager, then click ok. After a few seconds, close it.")

        HelperBackendTools.wait_until_packagemanager_free(mount_point="",
                                                          package_manager="yum")

class TestFindMissingFSCKModules(unittest.TestCase):
    def setUp(self):
        Tools.coretools.startup = True
        Tools.BackendTools.helpers.DiskInfo = Data.return_fake_disk_info()
        Functions.DiskInfo = Data.return_fake_disk_info()

    def tearDown(self):
        del Tools.coretools.startup
        del Tools.BackendTools.helpers.DiskInfo
        del Functions.DiskInfo

    @unittest.skipUnless(Functions.can_perform_find_missing_fsck_modules_test_1(), "FSCK modules not available on system.")
    def test_find_missing_fsck_modules_1(self):
        self.assertEqual(HelperBackendTools.find_missing_fsck_modules(),
                         Data.return_expected_result_finding_missing_fsck_modules())

    def test_find_missing_fsck_modules_2(self):
        self.assertEqual(HelperBackendTools.find_missing_fsck_modules(),
                         Functions.find_missing_fsck_modules())

class TestFindCheckableFileSystems(unittest.TestCase):
    def setUp(self):
        self.app = wx.App()
        self.frame = TestWindow()

        Tools.coretools.startup = True
        Tools.BackendTools.helpers.DialogTools = DialogTools

        DISK_INFO.update(getdevinfo.getdevinfo.get_info()) #We need real disk info for these ones.
        SYSTEM_INFO.update(Data.return_initial_system_info_dict())

    def tearDown(self):
        DISK_INFO.clear()
        SYSTEM_INFO.clear()

        del Tools.coretools.startup
        del Tools.BackendTools.helpers.DialogTools

        self.frame.Destroy()
        del self.frame

        self.app.Destroy()
        del self.app

    def test_find_checkable_file_systems_1(self):
        print(Functions.find_checkable_file_systems())
        print("\n\n")
        print(HelperBackendTools.find_checkable_file_systems())

        self.assertEqual(Functions.find_checkable_file_systems(),
                         HelperBackendTools.find_checkable_file_systems())
