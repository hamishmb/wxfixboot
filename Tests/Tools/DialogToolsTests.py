#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# DialogTools tests for WxFixBoot
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

# pylint: disable=no-self-use, too-many-ancestors, too-few-public-methods
#
# Reason (no-self-use): These are test methods, and must belong to classes.
# Reason (too-many-ancestors): These are wxPython ancestors.
# Reason (too-few-public-methods): Test classes.

#Import modules
import unittest
import sys
import wx

#Import other modules.
sys.path.append('../..') #Need to be able to import the Tools module from here.

import Tools.dialogtools as DialogTools

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
        wx.GetApp().SetTopWindow(self)

#No need for assertions, we're just making sure the functions run without errors here.
class TestShowThreadDlgs(unittest.TestCase):
    def setUp(self):
        self.app = wx.App()
        self.frame = TestWindow()

    def tearDown(self):
        self.frame.Destroy()
        del self.frame

        self.app.Yield()
        self.app.Destroy()
        del self.app


    def test_msg_dlg(self):
        DialogTools.show_thread_msg_dlg("Test message from WxFixBoot")

    def test_yes_no_dlg(self):
        DialogTools.show_thread_yes_no_dlg("Test message from WxFixBoot. Click Yes")
        DialogTools.show_thread_yes_no_dlg("Test message from WxFixBoot. Click No")
        DialogTools.show_thread_yes_no_dlg("Test message from WxFixBoot. Click either button. "
                                           + "If you can see this part of the message, custom "
                                           + "buttons aren't supported on your system",
                                           buttons=("Yay", "Nay"))

    def test_choice_dlg(self):
        DialogTools.show_thread_choice_dlg("Test message from WxFixBoot. What do programmers "
                                           + "convert into software? Select \"Pizza & Caffeine\"",
                                           choices=["Cheese & Milk", "Pizza & Caffeine",
                                                    "Dry Bread & Water"])

        DialogTools.show_thread_choice_dlg("Test message from WxFixBoot. Select \"Turtles\"",
                                           choices=["Turtles", "Tortoises", "Terrapins"])

    def test_text_entry_dlg(self):
        DialogTools.show_thread_text_entry_dlg("Test message from WxFixBoot. Type \"Linux\"")

    def test_save_file_dlg(self):
        DialogTools.show_thread_save_file_dlg("Test message from WxFixBoot. "
                                              + "Enter a path and filename.")
