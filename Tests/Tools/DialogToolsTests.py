#!/usr/bin/env python
# -*- coding: utf-8 -*- 
# DialogTools tests for WxFixBoot Version 2.0.1
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
import time

#Import test functions.
from . import DialogToolsTestFunctions as Functions

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

class TestShowThreadDlgs(unittest.TestCase):
    def setUp(self):
        self.app = wx.App()
        self.Frame = TestWindow()
        self.Panel = TestPanel(self.Frame)
        Tools.dialogtools.ParentWindow = self

    def tearDown(self):
        del Tools.dialogtools.ParentWindow

        self.Panel.Destroy()
        del self.Panel

        self.Frame.Destroy()
        del self.Frame

        self.app.Destroy()
        del self.app

    def testMsgDlg(self):
        DialogTools().ShowThreadMsgDlg("Test message from WxFixBoot")
        self.assertTrue(Functions.AskUserIfCorrect("\"Dialog Closed\""))

    def testYesNoDlg(self):
        DialogTools().ShowThreadYesNoDlg("Test message from WxFixBoot. Click Yes")
        self.assertTrue(Functions.AskUserIfCorrect("\"Yes\""))

        DialogTools().ShowThreadYesNoDlg("Test message from WxFixBoot. Click No")
        self.assertTrue(Functions.AskUserIfCorrect("\"No\""))

        DialogTools().ShowThreadYesNoDlg("Test message from WxFixBoot. Click either button. If you can see this part of the message, custom buttons aren't supported on your system", buttons=("Yay", "Nay"))
        self.assertTrue(Functions.AskUserIfCorrect("\"Custom Buttons if supported\""))

    def testChoiceDlg(self):
        DialogTools().ShowThreadChoiceDlg("Test message from WxFixBoot. What do programmers convert into software? Select \"Pizza & Caffeine\"", choices=["Cheese & Milk", "Pizza & Caffeine", "Dry Bread & Water"])
        self.assertTrue(Functions.AskUserIfCorrect("\"Pizza & Caffeine\""))

        DialogTools().ShowThreadChoiceDlg("Test message from WxFixBoot. Select \"Turtles\"", choices=["Turtles", "Tortoises", "Terrapins"])
        self.assertTrue(Functions.AskUserIfCorrect("\"Turtles\""))

    def testTextEntryDlg(self):
        DialogTools().ShowThreadTextEntryDlg("Test message from WxFixBoot. Type \"Linux\"")
        self.assertTrue(Functions.AskUserIfCorrect("\"Linux\""))

    def testSaveFileDlg(self):
        DialogTools().ShowThreadSaveFiledlg("Test message from WxFixBoot. Enter a path and filename.")
        self.assertTrue(Functions.AskUserIfCorrect("\"Displayed Properly\""))
