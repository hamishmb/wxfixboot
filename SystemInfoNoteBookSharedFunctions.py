#!/usr/bin/env python
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

#Do future imports to prepare to support python 3. Use unicode strings rather than ASCII strings, as they fix potential problems.
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

#Import modules.
import logging
import wx

#Set up logging. FIXME Set logger level as specified on cmdline.
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def bind_events(self):
    """Bind all events for the caller"""
    self.Bind(wx.EVT_BUTTON, self.SystemInfoWindow.OnExit, self.OkayButton)
    self.Bind(wx.EVT_SIZE, self.OnSize)

def create_widgets(self):
    """Create all widgets for the caller"""
    self.TitleText = wx.StaticText(self, -1, self.Title)
    self.list_ctrl = wx.ListCtrl(self, -1, style=wx.LC_REPORT|wx.LC_VRULES)
    self.OkayButton = wx.Button(self, -1, "Okay")

def setup_sizers(self):
    """Set up the sizers for the caller"""
    #Make a boxsizer.
    main_sizer = wx.BoxSizer(wx.VERTICAL)

    #Add each object to the main sizer.
    main_sizer.Add(self.TitleText, 0, wx.ALL|wx.CENTER, 10)
    main_sizer.Add(self.list_ctrl, 1, wx.EXPAND|wx.ALL ^ wx.TOP, 10)
    main_sizer.Add(self.OkayButton, 0, wx.ALIGN_CENTER|wx.ALL ^ wx.TOP, 10)

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

    keys = dictionary.keys()
    keys.sort()

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
                self.list_ctrl.InsertStringItem(index=number, label=data)

            else:
                self.list_ctrl.SetStringItem(index=number, col=column, label=data)

            column += 1

    #Auto Resize the columns.
    self.OnSize()
