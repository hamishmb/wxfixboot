#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Core Tools in the Tools Package for WxFixBoot Version 1.1~pre1
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

#Begin Main Class.
class Main():
    def ShowThreadMsgDlg(self, msg, kind="info"):
        """Shows a message dialog from a thread upon instruction"""
        if kind == "info":
            title = "WxFixBoot - Information"
            style = wx.OK | wx.ICON_INFORMATION

        elif kind == "warning":
            title = "WxFixBoot - Warning"
            style = wx.OK | wx.ICON_EXCLAMATION

        elif kind == "error":
            title = "WxFixBoot - Error"
            style = wx.OK | wx.ICON_ERROR

        dlg = wx.MessageDialog(ParentWindow.Panel, msg, title, style, pos=wx.DefaultPosition)
        dlg.ShowModal()
        dlg.Destroy()
        self.DlgClosed = True

        logger.debug("DialogTools: Main().ShowThreadMessageDlg(): Thread Message Dialog has been closed by user.")

    def ShowMsgDlg(self, Message, Kind="info"):
        """Handle showing thread message dialogs, reducing code duplication and compilications and errors.
        It can be used like this: DialogTools().ShowMsgDlg(Kind=<kind>, Message=<message>).
        Kind is one of 'info', 'warning' or 'error'.
        Message is whatever you want the dialog to say.
        """
        self.DlgClosed = None

        wx.CallAfter(self.ShowThreadMsgDlg, kind=Kind, msg=Message)

        #Trap the thread until the user responds.
        while self.DlgClosed == None:
            time.sleep(0.5)

    def ShowThreadYesNoDlg(self, msg, title="WxFixBoot - Question"):
        """Shows a yes/no dialog from a thread upon instruction"""
        dlg = wx.MessageDialog(ParentWindow.Panel, msg, title, wx.YES_NO | wx.ICON_QUESTION)

        #Where possible, destroy just before setting self.DlgResult to avoid potential race conditions.
        if dlg.ShowModal() == wx.ID_YES:
            dlg.Destroy()
            self.DlgResult = True

        else:
            dlg.Destroy()
            self.DlgResult = False

        logger.debug("DialogTools: Main().ShowThreadYesNoDlg(): Result of Thread Yes/No Dialog was: "+unicode(self.DlgResult))

    def ShowYesNoDlg(self, Message, Title="WxFixBoot - Question"):
        """Handle showing thread yes/no dialogs, reducing code duplication and compilications and errors.
        It can be used like this: DialogTools().ShowYesNoDlg(Message=<message>, Title=<title>)
        Message is whatever you want the dialog to say.
        Title sets the title bar text on the dialog.
        """
        self.DlgResult = None

        wx.CallAfter(self.ShowThreadYesNoDlg, msg=Message, title=Title)

        #Trap the thread until the user responds.
        while self.DlgResult == None:
            time.sleep(0.5)

        return self.DlgResult

    def ShowThreadChoiceDlg(self, msg, choices, title="WxFixBoot - Select an Option"):
        """Shows a choice dialog from a thread upon instruction"""
        dlg = wx.SingleChoiceDialog(ParentWindow.Panel, msg, title, choices, pos=wx.DefaultPosition)

        #Where possible, destroy just before setting self.DlgResult to avoid potential race conditions.
        if dlg.ShowModal() == wx.ID_OK:
            self.DlgResult = dlg.GetStringSelection()
            dlg.Destroy()

        else:
            dlg.Destroy()
            self.DlgResult = False

        logger.debug("DialogTools: Main().ShowThreadChoiceDlg(): Result of Thread Choice Dialog was: "+unicode(self.DlgResult))

    def ShowChoiceDlg(self, Message, Title, Choices):
        """Handle showing thread choice dialogs, reducing code duplication and compilications and errors.
        It can be used like this: DialogTools().ShowChoiceDlg(Message=<message>, Title=<title>, Choices=<choices>)
        Message is whatever you want the dialog to say.
        Title sets the title bar text on the dialog.
        Choices is a list of choice you want the dialog to display.
        """
        while True:
            self.DlgResult = None

            wx.CallAfter(self.ShowThreadChoiceDlg, msg=Message, title=Title, choices=Choices)

            #Trap the thread until the user responds.
            while self.DlgResult == None:
                time.sleep(0.5)

            #Don't let the user bypass any choice dialogs.
            if self.DlgResult in ("", False):
                logger.warning("DialogTools: Main().ShowChoiceDlg(): User closed dialog without answering. Warning user and asking again...")
                self.ShowMsgDlg(Kind="warning", Message="Please select an option.")

            else:
                return self.DlgResult

    def ShowThreadTextEntryDlg(self, msg, title="WxFixBoot - Text Entry"):
        """Shows a text entry dialog from a thread upon instruction"""
        dlg = wx.TextEntryDialog(ParentWindow.Panel, msg, title, "", style=wx.OK|wx.CANCEL, pos=wx.DefaultPosition)

        #Where possible, destroy just before setting self.DlgResult to avoid potential race conditions.
        if dlg.ShowModal() == wx.ID_OK:
            self.DlgResult = dlg.GetValue()
            dlg.Destroy()

        else:
            dlg.Destroy()
            self.DlgResult = False

        logger.debug("DialogTools: Main().ShowThreadTextEntryDlg(): Result of Thread Text Entry Dlg was: "+unicode(self.DlgResult))

    def ShowTextEntryDlg(self, Message, Title="WxFixBoot - Text Entry"):
        """Handle showing thread text entry dialogs, reducing code duplication and compilications and errors.
        It can be used like this: DialogTools().ShowTextEntryDlg(Message=<message>, Title=<title>)
        Message is whatever you want the dialog to say.
        Title sets the title bar text on the dialog.
        """
        while True:
            self.DlgResult = None

            wx.CallAfter(self.ShowThreadTextEntryDlg, msg=Message, title=Title)

            #Trap the thread until the user responds.
            while self.DlgResult == None:
                time.sleep(0.5)

            #Stop the user from avoiding entering anything.
            if self.DlgResult in ("", False):
                self.ShowMsgDlg(Kind="warning", Message="Please enter a valid name.")

            else:
                return self.DlgResult

    def ShowThreadSaveFiledlg(self, title="WxFixBoot - Select A File", wildcard="All Files/Devices (*)|*"):
        """Shows a save file choice dialog from a thread upon instruction"""
        dlg = wx.FileDialog(ParentWindow.Panel, message=title, defaultDir="/home", wildcard=wildcard, style=wx.SAVE|wx.OVERWRITE_PROMPT)

        #Where possible, destroy just before setting self.DlgResult to avoid potential race conditions.
        if dlg.ShowModal() == wx.ID_OK:
            dlg.Destroy()
            self.DlgResult = dlg.GetPath()

        else:
            dlg.Destroy()
            self.DlgResult = False

        logger.debug("DialogTools: Main().ShowThreadFileDlg(): Result of Thread File Dialog was: "+unicode(self.DlgResult))

    def ShowSaveFileDlg(self, Title="WxFixBoot - Select A File", Wildcard="All Files/Devices (*)|*"):
        """Handle showing thread file dialogs, reducing code duplication and compilications and errors.
        It can be used like this: self.ShowFileDlg(Title=<title>, Wildcard=<wildcard>)
        Message is whatever you want the dialog to say.
        Wildcard is a | seperated list of file types to show, including their names as visible to the user.
        """
        while True:
            self.DlgResult = None

            wx.CallAfter(self.ShowThreadSaveFiledlg, title=Title, wildcard=Wildcard)

            #Trap the thread until the user responds.
            while self.DlgResult == None:
                time.sleep(0.5)

            #Stop the user from avoiding entering anything.
            if self.DlgResult == False:
                self.ShowMsgDlg(Kind="warning", Message="Please select a valid file.")

            else:
                return self.DlgResult

#End Main Class.
