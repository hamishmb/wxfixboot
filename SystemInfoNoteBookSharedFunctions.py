#!/usr/bin/env python
# -*- coding: utf-8 -*-
# NoteBook pages for the system info window for WxFixBoot Version 2.0~pre1
# This file is part of WxFixBoot.
# Copyright (C) 2013-2016 Hamish McIntyre-Bhatty
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

#Begin Main Functions.
def BindEvents(self):
    """Bind all events for the caller"""
    self.Bind(wx.EVT_BUTTON, self.GetDiskInfo, self.RefreshButton)
    #self.Bind(wx.EVT_BUTTON, self.ParentWindow.OnExit, self.OkayButton)
    self.Bind(wx.EVT_SIZE, self.OnSize)

def CreateWidgets(self):
    """Create all widgets for the caller"""
    self.TitleText = wx.StaticText(self, -1, "Here are all the detected disks on your computer")
    self.ListCtrl = wx.ListCtrl(self, -1, style=wx.LC_REPORT|wx.LC_VRULES)
    self.OkayButton = wx.Button(self, -1, "Okay")
    self.RefreshButton = wx.Button(self, -1, "Refresh")

    #Create the animation for the throbber.
    throb = wx.animate.Animation("/usr/share/wxfixboot/images/Throbber.gif")
    self.Throbber = wx.animate.AnimationCtrl(self, -1, throb)
    self.Throbber.SetUseWindowBackgroundColour(True)
    self.Throbber.SetInactiveBitmap(wx.Bitmap("/usr/share/wxfixboot/images/ThrobberRest.png", wx.BITMAP_TYPE_PNG))
    self.Throbber.SetClientSize(wx.Size(30,30))

def SetupSizers(self):
    """Set up the sizers for the caller"""
    #Make a button boxsizer.
    BottomSizer = wx.BoxSizer(wx.HORIZONTAL)

    #Add each object to the bottom sizer.
    BottomSizer.Add(self.RefreshButton, 0, wx.LEFT|wx.RIGHT|wx.ALIGN_LEFT, 10)
    BottomSizer.Add((20,20), 1)
    BottomSizer.Add(self.Throbber, 0, wx.ALIGN_CENTER|wx.FIXED_MINSIZE)
    BottomSizer.Add((20,20), 1)
    BottomSizer.Add(self.OkayButton, 0, wx.LEFT|wx.RIGHT|wx.ALIGN_RIGHT, 10)

    #Make a boxsizer.
    MainSizer = wx.BoxSizer(wx.VERTICAL)

    #Add each object to the main sizer.
    MainSizer.Add(self.TitleText, 0, wx.ALL|wx.CENTER, 10)
    MainSizer.Add(self.ListCtrl, 1, wx.EXPAND|wx.ALL, 10)
    MainSizer.Add(BottomSizer, 0, wx.EXPAND|wx.ALL ^ wx.TOP, 10)

    #Get the sizer set up for the frame.
    self.SetSizer(MainSizer)
    MainSizer.SetMinSize(wx.Size(780,310))
    MainSizer.SetSizeHints(self)

def UpdateListCtrl(self, Event=None, Headings=[]):
    """Update the list control"""
    logger.debug("SystemInfoNoteBookSharedFunctions().UpdateListCtrl(): Clearing all objects in list ctrl...")
    self.ListCtrl.ClearAll()

    #Create the columns.
    logger.debug("SystemInfoNoteBookSharedFunctions().UpdateListCtrl(): Inserting columns into list ctrl...")
    Column = 0
    for Heading in Headings:
        self.ListCtrl.InsertColumn(col=Column, heading=Heading, format=wx.LIST_FORMAT_CENTRE) 
        Column += 1

    #Add info from the custom module.
    logger.debug("SystemInfoNoteBookSharedFunctions().UpdateListCtrl(): Adding Disk info to list ctrl...")

    Keys = DiskInfo.keys()
    Keys.sort()

    #Do all of the data at the same time.
    Number = -1
    for Disk in Keys:
        Number += 1
        Info = DiskInfo[Disk]

        Column = 0
        for Heading in Headings:
            Data = Info[Heading]

            if unicode(type(Data)) == "<type 'list'>":
                Data = ', '.join(Data)

            if Column == 0:
                self.ListCtrl.InsertStringItem(index=Number, label=Data)

            else:
                self.ListCtrl.SetStringItem(index=Number, col=Column, label=Data)

            Column += 1

    #Auto Resize the columns.
    self.OnSize()

#End Main Functions.
