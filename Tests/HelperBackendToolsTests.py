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

#Import test functions & data.
from . import HelperBackendToolsTestFunctions as Functions
from . import HelperBackendToolsTestData as Data

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
        Functions.ShowMsgDlg("Please ensure the package manager is not in use.")
        HelperBackendTools().WaitUntilPackageManagerNotInUse(MountPoint="", PackageManager="apt-get")

    def testWaitUntilPackageManagerNotInUse2(self):
        #Ask user to enable internet connection.
        Functions.ShowMsgDlg("Please open Synaptic or similar to lock the package manager, then click ok. After a few seconds, close it.")
        HelperBackendTools().WaitUntilPackageManagerNotInUse(MountPoint="", PackageManager="apt-get")
        self.assertTrue(Functions.ShowYesNoDlg("Is Synaptic/similar now closed?"))
