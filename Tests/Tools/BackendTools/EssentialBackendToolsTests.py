#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# EssentialBackendTools tests for WxFixBoot Version 3.0.0
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

#Import other modules.
sys.path.append('../../..') #Need to be able to import the Tools module from here.

import Tools
import Tests.DialogFunctionsForTests as DialogTools
import Tools.BackendTools.essentials as EssentialBackendTools
import Tools.BackendTools.main as MainBackendTools

#Import test data.
from . import EssentialBackendToolsTestData as Data

class TestPanel(wx.Panel):
    def __init__(self, parent):
        """Initialises the panel"""
        wx.Panel.__init__(self, parent=parent)
        self.frame = parent

class TestWindow(wx.Frame):
    def __init__(self):
        """Initialises TestWindow"""
        wx.Frame.__init__(self, parent=None, title="WxFixBoot Tests", size=(1, 1), style=wx.SIMPLE_BORDER)

class TestCheckInternetConnection(unittest.TestCase):
    def setUp(self):
        self.app = wx.App()
        self.frame = TestWindow()
        self.panel = TestPanel(self.frame)
        DialogTools.parent_window = self.panel

        Tools.coretools.startup = True
        Tools.BackendTools.essentials.SystemInfo = Data.return_initial_system_info_dict()
        Tools.BackendTools.essentials.DialogTools = DialogTools #Define here to avoid calling another thread that doesn't exist when trying to show a dialog.

    def tearDown(self):
        del Tools.coretools.startup
        del Tools.BackendTools.essentials.SystemInfo
        del Tools.BackendTools.essentials.DialogTools

        self.panel.Destroy()
        del self.panel

        self.frame.Destroy()
        del self.frame

        self.app.Destroy()
        del self.app

    def testCheckInternetConnection1(self):
        #Ask user to disable internet connection and give up when test fails.
        DialogTools.show_real_msg_dlg("Please disable your internet connection, and opt to \"Cancel/Skip Bootloader Operations\" when prompted.")
        EssentialBackendTools.check_internet_connection()
        self.assertEqual(Tools.BackendTools.essentials.SystemInfo, Data.return_system_info_dict_with_disabled_bl_opts())

    def testCheckInternetConnection2(self):
        #Ask user to enable internet connection.
        DialogTools.show_real_msg_dlg("Please enable your internet connection.")
        EssentialBackendTools.check_internet_connection()
        self.assertEqual(Tools.BackendTools.essentials.SystemInfo, Data.return_system_info_dict_with_enabled_bl_opts())

class TestHandleFilesystemCheckReturnValues(unittest.TestCase):
    def setUp(self):
        self.app = wx.App()
        self.frame = TestWindow()
        self.panel = TestPanel(self.frame)
        DialogTools.parent_window = self.panel

        self.SystemInfo = Data.return_initial_system_info_dict()
        Tools.BackendTools.essentials.SystemInfo = self.SystemInfo
        Tools.BackendTools.essentials.DialogTools = DialogTools

    def tearDown(self):
        del self.SystemInfo
        del Tools.BackendTools.essentials.SystemInfo
        del Tools.BackendTools.essentials.DialogTools

        self.panel.Destroy()
        del self.panel

        self.frame.Destroy()
        del self.frame

        self.app.Destroy()
        del self.app

    def testHandleFilesystemCheckReturnValues1(self):
        #All of these should behave in exactly the same way.
        EssentialBackendTools.handle_filesystem_check_return_values(exec_cmds="xfs_repair -Pvd /dev/sda1", retval=1, partition="/dev/sda1", manage_bootloader_function=MainBackendTools.manage_bootloader)
        self.assertEqual(DialogTools.MSG_DLG_MESSAGES[-1], "Corruption was found on the filesystem: /dev/sda1! Fortunately, it looks like the checker utility has fixed the corruption. Click okay to continue.")

        EssentialBackendTools.handle_filesystem_check_return_values(exec_cmds="xfs_repair -Pvd /dev/sda1", retval=2, partition="/dev/sda1", manage_bootloader_function=MainBackendTools.manage_bootloader)
        self.assertEqual(DialogTools.MSG_DLG_MESSAGES[-1], "Corruption was found on the filesystem: /dev/sda1! Fortunately, it looks like the checker utility has fixed the corruption. Click okay to continue.")

        EssentialBackendTools.handle_filesystem_check_return_values(exec_cmds="xfs_repair -Pvd /dev/sda1", retval=3, partition="/dev/sda1", manage_bootloader_function=MainBackendTools.manage_bootloader)
        self.assertEqual(DialogTools.MSG_DLG_MESSAGES[-1], "Corruption was found on the filesystem: /dev/sda1! Fortunately, it looks like the checker utility has fixed the corruption. Click okay to continue.")
