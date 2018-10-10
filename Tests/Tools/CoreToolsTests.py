#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# CoreTools tests for WxFixBoot Version 3.0.0
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

# pylint: disable=too-many-ancestors, too-few-public-methods
#
# Reason (too-many-ancestors): These are wxPython ancestors.
# Reason (too-few-public-methods): Test classes.

#Do future imports to prepare to support python 3. Use unicode strings rather than ASCII
#strings, as they fix potential problems.
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

#Import modules
import unittest
import os
import sys
import wx

#Import other modules.
sys.path.append('../..') #Need to be able to import the Tools module from here.

import Tools
import Tools.coretools as CoreTools

#Import test data and functions.
from . import CoreToolsTestData as Data
from . import CoreToolsTestFunctions as Functions
from .. import DialogFunctionsForTests

#Set up autocomplete vars.
POTENTIAL_DEVICE_PATH = ""
POTENTIAL_PARTITION_PATH = ""

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

class TestStartProcess(unittest.TestCase):
    def setUp(self):
        self.commands = Data.return_fake_commands()

        #Stops startprocess from trying to send data to the output box.
        Tools.coretools.startup = True

    def tearDown(self):
        del self.commands
        del Tools.coretools.startup

    def test_start_process(self):
        for command in self.commands:
            retval, output = CoreTools.start_process(command, return_output=True, testing=True)
            self.assertEqual(retval, self.commands[command]["Retval"])
            self.assertEqual(output, self.commands[command]["Output"])

class TestIsMounted(unittest.TestCase):
    def setUp(self):
        self.app = wx.App()
        self.frame = TestWindow()
        self.panel = TestPanel(self.frame)
        DialogFunctionsForTests.parent_window = self.panel

        global POTENTIAL_PARTITION_PATH

        self.path = POTENTIAL_PARTITION_PATH

        if POTENTIAL_PARTITION_PATH == "":
            #Get a device path from the user to test against.
            DialogFunctionsForTests.show_text_entry_dlg("WxFixBoot needs a partition name to test "
                                                        + "against.\nNo data on your device will "
                                                        + "be modified. Suggested: insert a USB "
                                                        + "disk and leave it mounted.\nNote: Do "
                                                        + "not use your device while these test "
                                                        + "are running, or it may interfere with "
                                                        + "the tests.", "WxFixBoot - Tests")

            self.path = DialogFunctionsForTests.TEXT_ENTRY_DLG_RESULTS[-1]

            #Save it for autocomplete with other dialogs.
            POTENTIAL_PARTITION_PATH = self.path

        #Stops startprocess from trying to send data to the output box.
        Tools.coretools.startup = True

    def tearDown(self):
        #Check if anything is mounted at our temporary mount point.
        if Functions.is_mounted(self.path):
            Functions.unmount_disk(self.path)

        #Remove the mount point.
        if os.path.isdir("/tmp/wxfixbootmtpt"):
            if os.path.isdir("/tmp/wxfixbootmtpt/subdir"):
                os.rmdir("/tmp/wxfixbootmtpt/subdir")

            os.rmdir("/tmp/wxfixbootmtpt")

        self.panel.Destroy()
        del self.panel

        self.frame.Destroy()
        del self.frame

        self.app.Destroy()
        del self.app

        del self.path
        del DialogFunctionsForTests.parent_window
        del Tools.coretools.startup

    def test_is_mounted1(self):
        #If not mounted, mount it
        if not Functions.is_mounted(self.path):
            self.assertEqual(CoreTools.mount_partition(self.path, "/tmp/wxfixbootmtpt"), 0)

        self.assertTrue(CoreTools.is_mounted(self.path))

    def test_is_mounted2(self):
        #Unmount it.
        Functions.unmount_disk(self.path)

        self.assertFalse(CoreTools.is_mounted(self.path))

class TestGetMountPointOf(unittest.TestCase):
    def setUp(self):
        self.app = wx.App()
        self.frame = TestWindow()
        self.panel = TestPanel(self.frame)
        DialogFunctionsForTests.parent_window = self.panel

        #Get a device path from the user to test against.
        global POTENTIAL_PARTITION_PATH

        self.path = POTENTIAL_PARTITION_PATH

        if POTENTIAL_PARTITION_PATH == "":
            #Get a device path from the user to test against.
            DialogFunctionsForTests.show_text_entry_dlg("WxFixBoot needs a partition name to test "
                                                        + "against.\nNo data on your device will "
                                                        + "be modified. Suggested: insert a USB "
                                                        + "disk and leave it mounted.\nNote: Do "
                                                        + "not use your device while these test "
                                                        + "are running, or it may interfere with "
                                                        + "the tests.", "WxFixBoot - Tests")

            self.path = DialogFunctionsForTests.TEXT_ENTRY_DLG_RESULTS[-1]

            #Save it for autocomplete with other dialogs.
            POTENTIAL_PARTITION_PATH = self.path

        #Stops startprocess from trying to send data to the output box.
        Tools.coretools.startup = True

    def tearDown(self):
        self.panel.Destroy()
        del self.panel

        self.frame.Destroy()
        del self.frame

        self.app.Destroy()
        del self.app

        del self.path
        del DialogFunctionsForTests.parent_window
        del Tools.coretools.startup

    def test_get_mount_point_of_1(self):
        #Mount disk if not mounted.
        if not Functions.is_mounted(self.path):
            Functions.mount_partition(self.path, "/tmp/wxfixbootmtpt")

        #Get mount point and verify.
        self.assertEqual(CoreTools.get_mount_point_of(self.path),
                         Functions.get_mount_point_of(self.path))

    def test_get_mount_point_of_2(self):
        #Unmount disk.
        Functions.unmount_disk(self.path)

        #Get mount point.
        self.assertIsNone(CoreTools.get_mount_point_of(self.path))

class TestGetPartitionMountedAt(unittest.TestCase):
    def setUp(self):
        self.app = wx.App()
        self.frame = TestWindow()
        self.panel = TestPanel(self.frame)
        DialogFunctionsForTests.parent_window = self.panel

        #Get a device path from the user to test against.
        global POTENTIAL_PARTITION_PATH

        self.path = POTENTIAL_PARTITION_PATH

        if POTENTIAL_PARTITION_PATH == "":
            #Get a device path from the user to test against.
            DialogFunctionsForTests.show_text_entry_dlg("WxFixBoot needs a partition name to test "
                                                        + "against.\nNo data on your device will "
                                                        + "be modified. Suggested: insert a USB "
                                                        + "disk and leave it mounted.\nNote: Do "
                                                        + "not use your device while these test "
                                                        + "are running, or it may interfere with "
                                                        + "the tests.", "WxFixBoot - Tests")

            self.path = DialogFunctionsForTests.TEXT_ENTRY_DLG_RESULTS[-1]

            #Save it for autocomplete with other dialogs.
            POTENTIAL_PARTITION_PATH = self.path

        #Mount disk if not mounted.
        if not Functions.is_mounted(self.path):
            Functions.mount_partition(self.path, "/tmp/wxfixbootmtpt")

        self.mount_point = Functions.get_mount_point_of(self.path)

        #Stops startprocess from trying to send data to the output box.
        Tools.coretools.startup = True

    def tearDown(self):
        self.panel.Destroy()
        del self.panel

        self.frame.Destroy()
        del self.frame

        self.app.Destroy()
        del self.app

        del DialogFunctionsForTests.parent_window
        del self.path
        del self.mount_point
        del Tools.coretools.startup

    def test_get_partition_mounted_at_1(self):
        self.assertEqual(CoreTools.get_partition_mounted_at(self.mount_point), self.path)

class TestMountPartition(unittest.TestCase):
    def setUp(self):
        self.app = wx.App()
        self.frame = TestWindow()
        self.panel = TestPanel(self.frame)
        DialogFunctionsForTests.parent_window = self.panel

        #Get a device path from the user to test against.
        global POTENTIAL_PARTITION_PATH

        self.path = POTENTIAL_PARTITION_PATH
        self.path2 = None

        if POTENTIAL_PARTITION_PATH == "":
            #Get a device path from the user to test against.
            DialogFunctionsForTests.show_text_entry_dlg("WxFixBoot needs a partition name to test "
                                                        + "against.\nNo data on your device will "
                                                        + "be modified. Suggested: insert a USB "
                                                        + "disk and leave it mounted.\nNote: Do "
                                                        + "not use your device while these test "
                                                        + "are running, or it may interfere with "
                                                        + "the tests.", "WxFixBoot - Tests")

            self.path = DialogFunctionsForTests.TEXT_ENTRY_DLG_RESULTS[-1]

            #Save it for autocomplete with other dialogs.
            POTENTIAL_PARTITION_PATH = self.path

        self.mount_point = Functions.get_mount_point_of(self.path)

        if self.mount_point is None:
            self.mount_point = "/tmp/wxfixbootmtpt"

            if not os.path.isdir(self.mount_point):
                os.mkdir(self.mount_point)

        #Stops startprocess from trying to send data to the output box.
        Tools.coretools.startup = True

    def tearDown(self):
        #Unmount.
        Functions.unmount_disk(self.path)

        self.panel.Destroy()
        del self.panel

        self.frame.Destroy()
        del self.frame

        self.app.Destroy()
        del self.app

        del DialogFunctionsForTests.parent_window
        del self.path
        del Tools.coretools.startup

        if os.path.isdir("/tmp/wxfixbootmtpt"):
            if os.path.isdir("/tmp/wxfixbootmtpt/subdir"):
                os.rmdir("/tmp/wxfixbootmtpt/subdir")

            os.rmdir("/tmp/wxfixbootmtpt")

    def test_mount_partition1(self):
        Functions.mount_partition(self.path, self.mount_point)

        #partition should be mounted, so we should pass this without doing anything.
        self.assertEqual(CoreTools.mount_partition(self.path, self.mount_point), 0)

        Functions.unmount_disk(self.path)

    def test_mount_partition2(self):
        #Unmount disk.
        Functions.unmount_disk(self.path)

        self.assertEqual(CoreTools.mount_partition(self.path, self.mount_point), 0)

        Functions.unmount_disk(self.path)

    def test_mount_partition3(self):
        #Get another device path from the user to test against.
        DialogFunctionsForTests.show_text_entry_dlg("WxFixBoot needs a second (different) "
                                                    + "partition name to test against.\nNo "
                                                    + "data on your device will be modified. "
                                                    + "Suggested: insert a USB disk and leave "
                                                    + "it mounted.\nNote: Do not use your device "
                                                    + "while these test are running, or it may "
                                                    + "interfere with the tests.",
                                                    "WxFixBoot - Tests")

        self.path2 = DialogFunctionsForTests.TEXT_ENTRY_DLG_RESULTS[-1]

        #Unmount both partitions.
        for partition in [self.path, self.path2]:
            Functions.unmount_disk(partition)

        #Mount the 2nd one on the desired path for the 1st one.
        CoreTools.mount_partition(self.path2, self.mount_point)

        #Now try to mount the first one there.
        CoreTools.mount_partition(self.path, self.mount_point)

        #Now the 2nd should have been unmounted to get it out of the way, and the 1st
        #should be there.
        self.assertFalse(Functions.is_mounted(self.path2, self.mount_point))
        self.assertTrue(Functions.is_mounted(self.path, self.mount_point))

        Functions.unmount_disk(self.path)

        #Clean up.
        del self.path2

    def test_mount_partition4(self):
        #Unmount partition.
        Functions.unmount_disk(self.path)

        #Try to mount in subdir of usual mount point.
        CoreTools.mount_partition(self.path, self.mount_point+"/subdir")

        #Check is mounted.
        self.assertTrue(Functions.is_mounted(self.path, self.mount_point+"/subdir"))

        #Unmount.
        Functions.unmount_disk(self.path)

        #Clean up.
        if os.path.isdir(self.mount_point+"/subdir"):
            os.rmdir(self.mount_point+"/subdir")
