#!/usr/bin/env python
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
import wx

#Import test functions & data.
from . import EssentialBackendToolsTestFunctions as Functions
from . import EssentialBackendToolsTestData as Data

#Setup test functions.
Functions.wx = wx

class TestPanel(wx.Panel):
    def __init__(self, parent):
        """Initialises the panel"""
        wx.Panel.__init__(self, parent=parent)
        self.frame = parent

class TestWindow(wx.Frame):
    def __init__(self):
        """Initialises TestWindow"""
        wx.Frame.__init__(self, parent=None, title="WxFixBoot Tests", size=(1,1), style=wx.SIMPLE_BORDER)

class TestCheckInternetConnection(unittest.TestCase):
    def setUp(self):
        self.app = wx.App()
        self.Frame = TestWindow()
        self.Panel = TestPanel(self.Frame)
        DialogFunctionsForTests.ParentWindow = self.Panel

        Tools.coretools.Startup = True
        Tools.BackendTools.essentials.SystemInfo = Data.ReturnInitialSystemInfoDict()
        Tools.BackendTools.essentials.DialogTools = DialogFunctionsForTests #Define here to avoid calling another thread that doesn't exist when trying to show a dialog.

    def tearDown(self):
        del DialogFunctionsForTests.ParentWindow
        del Tools.coretools.Startup
        del Tools.BackendTools.essentials.SystemInfo
        del Tools.BackendTools.essentials.DialogTools

        self.Panel.Destroy()
        del self.Panel

        self.Frame.Destroy()
        del self.Frame

        self.app.Destroy()
        del self.app

    def testCheckInternetConnection1(self):
        #Ask user to disable internet connection and give up when test fails.
        DialogFunctionsForTests.ShowRealMsgDlg("Please disable your internet connection, and opt to \"Cancel/Skip Bootloader Operations\" when prompted.")
        EssentialBackendTools().CheckInternetConnection()
        self.assertEqual(Tools.BackendTools.essentials.SystemInfo, Data.ReturnSystemInfoDictWithDisabledBLOpts())

    def testCheckInternetConnection2(self):
        #Ask user to enable internet connection.
        DialogFunctionsForTests.ShowRealMsgDlg("Please enable your internet connection.")
        EssentialBackendTools().CheckInternetConnection()
        self.assertEqual(Tools.BackendTools.essentials.SystemInfo, Data.ReturnSystemInfoDictWithEnabledBLOpts())
