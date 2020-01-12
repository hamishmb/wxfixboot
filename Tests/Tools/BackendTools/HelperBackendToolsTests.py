#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# HelperBackendTools tests for WxFixBoot
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

# pylint: disable=too-many-ancestors, too-few-public-methods, wrong-import-order, no-self-use
#
# Reason (too-many-ancestors): These are wxPython ancestors.
# Reason (too-few-public-methods): Test classes.
# Reason (wrong-import-order): These are just unit tests.
# Reason (no-self-use): Just test methods.

#Import modules
import unittest
import sys
import threading
import fcntl
import time
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
        self.fd = None

        Tools.coretools.STARTUP = True

    def unlock_fd(self):
        time.sleep(10)
        self.fd.close()

    def tearDown(self):
        del self.fd
        del Tools.coretools.STARTUP

        self.frame.Destroy()
        del self.frame

        self.app.Destroy()
        del self.app

    @unittest.skipUnless(subprocess.Popen("which apt-get", shell=True, stdout=subprocess.PIPE).wait() == 0, "Package Manager isn't apt-get.")
    def test_packagemanager_free_1(self):
        print("Waiting until APT is free to make sure the code doesn't wait when executed.")
        #Wait until APT is free.
        unlocked = False

        while not unlocked:
            try:
                self.fd = open("/var/lib/dpkg/lock", "w")
                fcntl.lockf(self.fd, fcntl.LOCK_EX | fcntl.LOCK_NB)

            except (IOError, OSError):
                #APT is still busy. Wait a second and try again.
                time.sleep(1)

            else:
                #APT is free!
                unlocked = True

            finally:
                self.fd.close()

        HelperBackendTools.wait_until_packagemanager_free(mount_point="",
                                                          package_manager="apt-get")

    @unittest.skipUnless(subprocess.Popen("which apt-get", shell=True, stdout=subprocess.PIPE).wait() == 0, "Package Manager isn't apt-get.")
    def test_packagemanager_free_2(self):
        print("Locking APT for a few seconds, and then releasing.")
        print("Acquiring APT lock...")

        #Wait until we can acquire the lock.
        locked = False

        while not locked:
            try:
                self.fd = open("/var/lib/dpkg/lock", "w")
                fcntl.lockf(self.fd, fcntl.LOCK_EX | fcntl.LOCK_NB)

            except (IOError, OSError):
                #APT is still busy. Wait a second and try again.
                time.sleep(1)

            else:
                #APT is free!
                locked = True

        #In 10 seconds time, unlock APT.
        print("Done. If this test now hangs for a long time, consider it to have failed")

        threading.Thread(target=self.unlock_fd).start()

        HelperBackendTools.wait_until_packagemanager_free(mount_point="",
                                                          package_manager="apt-get")

    #FIXME: These two tests fail, strictly speaking, but DNF handles the lock differently;
    #it will wait instead of exiting with an error, so it doesn't matter as much.
    @unittest.skipUnless(subprocess.Popen("which yum", shell=True, stdout=subprocess.PIPE).wait() == 0, "Package Manager isn't yum.")
    def test_packagemanager_free_3(self):
        print("Waiting until DNF is free to make sure the code doesn't wait when executed.")
        #Wait until DNF is free.
        unlocked = False

        while not unlocked:
            try:
                self.fd = open("/var/lib/rpm/.rpm.lock", "w")
                fcntl.lockf(self.fd, fcntl.LOCK_EX | fcntl.LOCK_NB)

            except (IOError, OSError):
                #DNF is still busy. Wait a second and try again.
                time.sleep(1)

            else:
                #DNF is free!
                unlocked = True

            finally:
                self.fd.close()

        HelperBackendTools.wait_until_packagemanager_free(mount_point="",
                                                          package_manager="yum")

    @unittest.skipUnless(subprocess.Popen("which yum", shell=True, stdout=subprocess.PIPE).wait() == 0, "Package Manager isn't yum.")
    def test_packagemanager_free_4(self):
        print("Locking DNF for a few seconds, and then releasing.")
        print("Acquiring DNF lock...")

        #Wait until we can acquire the lock.
        locked = False

        while not locked:
            try:
                self.fd = open("/var/lib/rpm/.rpm.lock", "w")
                fcntl.lockf(self.fd, fcntl.LOCK_EX | fcntl.LOCK_NB)

            except (IOError, OSError):
                #DNF is still busy. Wait a second and try again.
                time.sleep(1)

            else:
                #DNF is free!
                locked = True

        #In 10 seconds time, unlock DNF.
        print("Done. If this test now hangs for a long time, consider it to have failed")

        threading.Thread(target=self.unlock_fd).start()

        HelperBackendTools.wait_until_packagemanager_free(mount_point="",
                                                          package_manager="yum")

class TestFindMissingFSCKModules(unittest.TestCase):
    def setUp(self):
        Tools.coretools.STARTUP = True
        Tools.BackendTools.helpers.DiskInfo = Data.return_fake_disk_info()
        Functions.DiskInfo = Data.return_fake_disk_info()

    def tearDown(self):
        del Tools.coretools.STARTUP
        del Tools.BackendTools.helpers.DiskInfo
        del Functions.DiskInfo

    @unittest.skipUnless(Functions.can_perform_find_missing_fsck_modules_test_1(), "FSCK modules not available on system.")
    def test_find_missing_fsck_modules_1(self):
        """Test #1: Test that FSCK modules are detected when they are present"""
        self.assertEqual(HelperBackendTools.find_missing_fsck_modules(),
                         Data.return_expected_result_finding_missing_fsck_modules())

    def test_find_missing_fsck_modules_2(self):
        """Test #2: Test that we can search for missing FSCK modules without error"""
        HelperBackendTools.find_missing_fsck_modules()

class TestFindCheckableFileSystems(unittest.TestCase):
    def setUp(self):
        self.app = wx.App()
        self.frame = TestWindow()

        Tools.coretools.STARTUP = True
        Tools.BackendTools.helpers.DialogTools = DialogTools

        DISK_INFO.update(getdevinfo.getdevinfo.get_info()) #We need real disk info for these ones.
        SYSTEM_INFO.update(Data.return_initial_system_info_dict())

    def tearDown(self):
        DISK_INFO.clear()
        SYSTEM_INFO.clear()

        del Tools.coretools.STARTUP
        del Tools.BackendTools.helpers.DialogTools

        self.frame.Destroy()
        del self.frame

        self.app.Destroy()
        del self.app

    def test_find_checkable_file_systems_1(self):
        """Test #1: Test that we can determine which filesystems to check without error"""
        HelperBackendTools.find_checkable_file_systems()
