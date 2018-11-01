#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# NoteBook page functions for the system info window for WxFixBoot Version 3.0.0
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

#Do future imports to prepare to support python 3. Use unicode strings rather than ASCII
#strings, as they fix potential problems.
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

#Import modules.
import logging
import sys
import wx

#Make unicode an alias for str in Python 3.
if sys.version_info[0] == 3:
    #Disable cos necessary to keep supporting python 2.
    unicode = str #pylint: disable=redefined-builtin,invalid-name

CLASSIC_WXPYTHON = int(wx.version()[0]) < 4

#Set up logging.
logger = logging.getLogger(__name__)
logger.setLevel(logging.getLogger("WxFixBoot").getEffectiveLevel())

def bind_events(self):
    """Bind all events for the caller"""
    self.Bind(wx.EVT_BUTTON, self.systeminfo_window.on_exit, self.okay_button)
    self.Bind(wx.EVT_SIZE, self.on_size)

def create_widgets(self):
    """Create all widgets for the caller"""
    self.title_text = wx.StaticText(self, -1, self.title)
    self.list_ctrl = wx.ListCtrl(self, -1, style=wx.LC_REPORT|wx.LC_VRULES)
    self.okay_button = wx.Button(self, -1, "Okay")

def setup_sizers(self):
    """Set up the sizers for the caller"""
    #Make a boxsizer.
    main_sizer = wx.BoxSizer(wx.VERTICAL)

    #Add each object to the main sizer.
    main_sizer.Add(self.title_text, 0, wx.ALL|wx.CENTER, 10)
    main_sizer.Add(self.list_ctrl, 1, wx.EXPAND|wx.ALL ^ wx.TOP, 10)
    main_sizer.Add(self.okay_button, 0, wx.ALIGN_CENTER|wx.ALL ^ wx.TOP, 10)

    #Get the sizer set up for the frame.
    self.SetSizer(main_sizer)
    main_sizer.SetMinSize(wx.Size(780, 310))
    main_sizer.SetSizeHints(self)

def update_list_ctrl(self, event=None, headings=None, dictionary=None): #pylint: disable=unused-argument
    """Update the list control"""
    if headings is None:
        headings = []

    if dictionary is None:
        dictionary = {}

    logger.debug("update_list_ctrl(): Clearing all objects in list ctrl...")
    self.list_ctrl.ClearAll()

    #Create the columns.
    logger.debug("update_list_ctrl(): Inserting columns into list ctrl...")
    column = 0
    for heading in headings:
        self.list_ctrl.InsertColumn(col=column, heading=heading, format=wx.LIST_FORMAT_CENTRE)
        column += 1

    #Add info from the custom module.
    logger.debug("update_list_ctrl(): Adding info to list ctrl...")

    keys = list(dictionary.keys())
    keys.sort()

    #Compatibility with wxpython < 4.
    if CLASSIC_WXPYTHON:
        self.list_ctrl.SetItem = self.list_ctrl.SetStringItem
        self.list_ctrl.InsertItem = self.list_ctrl.InsertStringItem

    #Do all of the data at the same time.
    number = -1
    for thing in keys:
        number += 1
        info = dictionary[thing]

        column = 0
        for heading in headings:
            data = info[heading]

            if unicode(type(data)) == type([]):
                data = ', '.join(data)

            elif unicode(type(data)) != type(""):
                data = unicode(data)

            if column == 0:
                self.list_ctrl.InsertItem(number, label=data)

            else:
                self.list_ctrl.SetItem(number, column, label=data)

            column += 1

    #Auto Resize the columns.
    self.on_size()
