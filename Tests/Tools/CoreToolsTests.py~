#!/usr/bin/env python
# -*- coding: utf-8 -*- 
# CoreTools tests for WxFixBoot Version 2.0.2
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
import subprocess
import time

#Import test data and functions.
from . import CoreToolsTestData as Data
from . import CoreToolsTestFunctions as Functions

#Set up test functions.
Functions.subprocess = subprocess
Functions.os = os
Functions.time = time

#Set up autocomplete vars.
PotentialDevicePath = ""
PotentialPartitionPath = ""

class TestPanel(wx.Panel):
    def __init__(self, parent):
        """Initialises the panel"""
        wx.Panel.__init__(self, parent=parent)
        self.frame = parent

class TestWindow(wx.Frame):
    def __init__(self):
        """Initialises TestWindow"""
        wx.Frame.__init__(self, parent=None, title="WxFixBoot Tests", size=(1,1), style=wx.SIMPLE_BORDER)

class TestStartProcess(unittest.TestCase):
    def setUp(self):
        self.Commands = Data.ReturnFakeCommands()
        Tools.coretools.Startup = True #Stops startprocess from trying to send data to the output box.

    def tearDown(self):
        del self.Commands
        del Tools.coretools.Startup

    def testStartProcess(self):
        for Command in self.Commands.keys():
            Retval, Output = CoreTools().StartProcess(Command, ReturnOutput=True, Testing=True)
            self.assertEqual(Retval, self.Commands[Command]["Retval"])
            self.assertEqual(Output, self.Commands[Command]["Output"])

class TestIsMounted(unittest.TestCase):
    def setUp(self):
        self.app = wx.App()
        self.Frame = TestWindow()
        self.Panel = TestPanel(self.Frame)
        DialogFunctionsForTests.ParentWindow = self.Panel

        global PotentialPartitionPath

        self.Path = PotentialPartitionPath

        if PotentialPartitionPath == "":
            #Get a device path from the user to test against.
            DialogFunctionsForTests.ShowTextEntryDlg("WxFixBoot needs a partition name to test against.\nNo data on your device will be modified. Suggested: insert a USB disk and leave it mounted.\nNote: Do not use your device while these test are running, or it may interfere with the tests.", "WxFixBoot - Tests")
            self.Path = DialogFunctionsForTests.TextEntryDlgResults[-1]

            #Save it for autocomplete with other dialogs.
            PotentialPartitionPath = self.Path

        Tools.coretools.Startup = True #Stops startprocess from trying to send data to the output box.

    def tearDown(self):
        #Check if anything is mounted at our temporary mount point.
        if Functions.IsMounted(self.Path):
            Functions.UnmountDisk(self.Path)

        #Remove the mount point.
        if os.path.isdir("/tmp/wxfixbootmtpt"):
            if os.path.isdir("/tmp/wxfixbootmtpt/subdir"):
                os.rmdir("/tmp/wxfixbootmtpt/subdir")

            os.rmdir("/tmp/wxfixbootmtpt")

        self.Panel.Destroy()
        del self.Panel

        self.Frame.Destroy()
        del self.Frame

        self.app.Destroy()
        del self.app

        del self.Path
        del DialogFunctionsForTests.ParentWindow
        del Tools.coretools.Startup

    def testIsMounted1(self):
        #If not mounted, mount it
        if not Functions.IsMounted(self.Path):
            self.assertEqual(CoreTools().MountPartition(self.Path, "/tmp/wxfixbootmtpt"), 0)

        self.assertTrue(CoreTools().IsMounted(self.Path))

    def testIsMounted2(self):
        #Unmount it.
        Functions.UnmountDisk(self.Path)

        self.assertFalse(CoreTools().IsMounted(self.Path))

class TestGetMountPointOf(unittest.TestCase):
    def setUp(self):
        self.app = wx.App()
        self.Frame = TestWindow()
        self.Panel = TestPanel(self.Frame)
        DialogFunctionsForTests.ParentWindow = self.Panel

        #Get a device path from the user to test against.
        global PotentialPartitionPath

        self.Path = PotentialPartitionPath

        if PotentialPartitionPath == "":
            #Get a device path from the user to test against.
            DialogFunctionsForTests.ShowTextEntryDlg("WxFixBoot needs a partition name to test against.\nNo data on your device will be modified. Suggested: insert a USB disk and leave it mounted.\nNote: Do not use your device while these test are running, or it may interfere with the tests.", "WxFixBoot - Tests")
            self.Path = DialogFunctionsForTests.TextEntryDlgResults[-1]

            #Save it for autocomplete with other dialogs.
            PotentialPartitionPath = self.Path

        Tools.coretools.Startup = True #Stops startprocess from trying to send data to the output box.

    def tearDown(self):
        self.Panel.Destroy()
        del self.Panel

        self.Frame.Destroy()
        del self.Frame

        self.app.Destroy()
        del self.app

        del self.Path
        del DialogFunctionsForTests.ParentWindow
        del Tools.coretools.Startup

    def testGetMountPointOf1(self):
        #Mount disk if not mounted.
        if not Functions.IsMounted(self.Path):
            Functions.MountPartition(self.Path, "/tmp/wxfixbootmtpt")

        #Get mount point and verify.
        self.assertEqual(CoreTools().GetMountPointOf(self.Path), Functions.GetMountPointOf(self.Path))

    def testGetMountPointOf2(self):
        #Unmount disk.
        Functions.UnmountDisk(self.Path)

        #Get mount point.
        self.assertIsNone(CoreTools().GetMountPointOf(self.Path))

class TestGetPartitionMountedAt(unittest.TestCase):
    def setUp(self):
        self.app = wx.App()
        self.Frame = TestWindow()
        self.Panel = TestPanel(self.Frame)
        DialogFunctionsForTests.ParentWindow = self.Panel

        #Get a device path from the user to test against.
        global PotentialPartitionPath

        self.Path = PotentialPartitionPath

        if PotentialPartitionPath == "":
            #Get a device path from the user to test against.
            DialogFunctionsForTests.ShowTextEntryDlg("WxFixBoot needs a partition name to test against.\nNo data on your device will be modified. Suggested: insert a USB disk and leave it mounted.\nNote: Do not use your device while these test are running, or it may interfere with the tests.", "WxFixBoot - Tests")
            self.Path = DialogFunctionsForTests.TextEntryDlgResults[-1]

            #Save it for autocomplete with other dialogs.
            PotentialPartitionPath = self.Path

        #Mount disk if not mounted.
        if not Functions.IsMounted(self.Path):
            Functions.MountPartition(self.Path, "/tmp/wxfixbootmtpt")

        self.MountPoint = Functions.GetMountPointOf(self.Path)

        Tools.coretools.Startup = True #Stops startprocess from trying to send data to the output box.

    def TearDown(self):
        self.Panel.Destroy()
        del self.Panel

        self.Frame.Destroy()
        del self.Frame

        self.app.Destroy()
        del self.app

        del DialogFunctionsForTests.ParentWindow
        del self.Path
        del self.MountPoint
        del Tools.coretools.Startup

    def testGetPartitionMountedAt1(self):
        self.assertEqual(CoreTools().GetPartitionMountedAt(self.MountPoint), self.Path)

class TestMountPartition(unittest.TestCase):
    def setUp(self):
        self.app = wx.App()
        self.Frame = TestWindow()
        self.Panel = TestPanel(self.Frame)
        DialogFunctionsForTests.ParentWindow = self.Panel

        #Get a device path from the user to test against.
        global PotentialPartitionPath

        self.Path = PotentialPartitionPath

        if PotentialPartitionPath == "":
            #Get a device path from the user to test against.
            DialogFunctionsForTests.ShowTextEntryDlg("WxFixBoot needs a partition name to test against.\nNo data on your device will be modified. Suggested: insert a USB disk and leave it mounted.\nNote: Do not use your device while these test are running, or it may interfere with the tests.", "WxFixBoot - Tests")
            self.Path = DialogFunctionsForTests.TextEntryDlgResults[-1]

            #Save it for autocomplete with other dialogs.
            PotentialPartitionPath = self.Path

        self.MountPoint = Functions.GetMountPointOf(self.Path)

        if self.MountPoint == None:
            self.MountPoint = "/tmp/wxfixbootmtpt"

            if not os.path.isdir(self.MountPoint):
                os.mkdir(self.MountPoint)

        Tools.coretools.Startup = True #Stops startprocess from trying to send data to the output box.

    def tearDown(self):
        #Unmount.
        Functions.UnmountDisk(self.Path)

        self.Panel.Destroy()
        del self.Panel

        self.Frame.Destroy()
        del self.Frame

        self.app.Destroy()
        del self.app

        del DialogFunctionsForTests.ParentWindow
        del self.Path
        del Tools.coretools.Startup

        if os.path.isdir("/tmp/wxfixbootmtpt"):
            if os.path.isdir("/tmp/wxfixbootmtpt/subdir"):
                os.rmdir("/tmp/wxfixbootmtpt/subdir")

            os.rmdir("/tmp/wxfixbootmtpt")

    def testMountPartition1(self):
        Functions.MountPartition(self.Path, self.MountPoint)

        #Partition should be mounted, so we should pass this without doing anything.
        self.assertEqual(CoreTools().MountPartition(self.Path, self.MountPoint), 0)

        Functions.UnmountDisk(self.Path)

    def testMountPartition2(self):
        #Unmount disk.
        Functions.UnmountDisk(self.Path)

        self.assertEqual(CoreTools().MountPartition(self.Path, self.MountPoint), 0)

        Functions.UnmountDisk(self.Path)

    def testMountPartition3(self):
        #Get another device path from the user to test against.
        DialogFunctionsForTests.ShowTextEntryDlg("WxFixBoot needs a second (different) partition name to test against.\nNo data on your device will be modified. Suggested: insert a USB disk and leave it mounted.\nNote: Do not use your device while these test are running, or it may interfere with the tests.", "WxFixBoot - Tests")
        self.Path2 = DialogFunctionsForTests.TextEntryDlgResults[-1]

        #Unmount both partitions.
        for Partition in [self.Path, self.Path2]:
            Functions.UnmountDisk(Partition)

        #Mount the 2nd one on the desired path for the 1st one.
        CoreTools().MountPartition(self.Path2, self.MountPoint)

        #Now try to mount the first one there.
        CoreTools().MountPartition(self.Path, self.MountPoint)

        #Now the 2nd should have been unmounted to get it out of the way, and the 1st should be there.
        self.assertFalse(Functions.IsMounted(self.Path2, self.MountPoint))
        self.assertTrue(Functions.IsMounted(self.Path, self.MountPoint))

        Functions.UnmountDisk(self.Path)

        #Clean up.
        del self.Path2

    def testMountPartition4(self):
        #Unmount partition.
        Functions.UnmountDisk(self.Path)

        #Try to mount in subdir of usual mount point.
        CoreTools().MountPartition(self.Path, self.MountPoint+"/subdir")

        #Check is mounted.
        self.assertTrue(Functions.IsMounted(self.Path, self.MountPoint+"/subdir"))

        #Unmount.
        Functions.UnmountDisk(self.Path)

        #Clean up.
        if os.path.isdir(self.MountPoint+"/subdir"):
            os.rmdir(self.MountPoint+"/subdir")

