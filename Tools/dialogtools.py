#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Dialog Tools in the Tools Package for WxFixBoot Version 3.0.0
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
import time
import wx
import logging

#Set up logging. FIXME Set logger level as specified on cmdline.
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

#Global declarations.
DlgClosed = False
DlgResult = False

def ShowThreadMsgDlg(msg, kind="info"):
    """Shows a message dialog from a thread upon instruction"""
    logger.debug("ShowThreadMessageDlg(): Showing Thread Message Dialog...")
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

    global DlgClosed
    DlgClosed = True

    logger.debug("ShowThreadMessageDlg(): Thread Message Dialog has been closed by user.")

def ShowMsgDlg(Message, Kind="info"):
    """Handle showing thread message dialogs, reducing code duplication and complications and errors.
    It can be used like this: DialogTools().ShowMsgDlg(Kind=<kind>, Message=<message>).
    Kind is one of 'info', 'warning' or 'error'.
    Message is whatever you want the dialog to say.
    """
    global DlgClosed
    DlgClosed = None
    wx.CallAfter(ShowThreadMsgDlg, kind=Kind, msg=Message)

    #Trap the thread until the user responds.
    while DlgClosed == None:
        time.sleep(0.5)

def ShowThreadYesNoDlg(msg, title="WxFixBoot - Question", buttons=(None, None)):
    """Shows a yes/no dialog from a thread upon instruction"""
    logger.debug("ShowThreadYesNoDlg(): Showing Thread Yes/No Dialog...")
    dlg = wx.MessageDialog(ParentWindow.Panel, msg, title, wx.YES_NO | wx.ICON_QUESTION)

    global DlgResult

    #Try to set custom buttons labels if needed (handle attribute error on wx 2.8.11).
    if buttons != (None, None):
        try:
            if dlg.SetYesNoLabels(buttons[0], buttons[1]):
                #If it worked get rid of the last unneccessary sentence in the message.
                dlg.SetMessage(' '.join(msg.split(".")[0:-1]))

        except AttributeError: pass

    #Where possible, destroy just before setting DlgResult to avoid potential race conditions.
    if dlg.ShowModal() == wx.ID_YES:
        dlg.Destroy()
        DlgResult = True

    else:
        dlg.Destroy()
        DlgResult = False

    logger.debug("ShowThreadYesNoDlg(): Result of Thread Yes/No Dialog was: "+unicode(DlgResult))

def ShowYesNoDlg(Message, Title="WxFixBoot - Question", Buttons=(None, None)):
    """Handle showing thread yes/no dialogs, reducing code duplication and compilications and errors.
    It can be used like this: DialogTools().ShowYesNoDlg(Message=<message>, Title=<title>)
    Message is whatever you want the dialog to say.
    Buttons is the text for the button labels.
    Title sets the title bar text on the dialog.
    """
    global DlgResult
    DlgResult = None

    wx.CallAfter(ShowThreadYesNoDlg, msg=Message, title=Title, buttons=Buttons)

    #Trap the thread until the user responds.
    while DlgResult == None:
        time.sleep(0.5)

    return DlgResult

def ShowThreadChoiceDlg(msg, choices, title="WxFixBoot - Select an Option"):
    """Shows a choice dialog from a thread upon instruction"""
    global DlgResult

    logger.debug("ShowThreadChoiceDlg(): Showing Thread Choice Dialog...")
    dlg = wx.SingleChoiceDialog(ParentWindow.Panel, msg, title, choices, pos=wx.DefaultPosition)

    #Where possible, destroy just before setting DlgResult to avoid potential race conditions.
    if dlg.ShowModal() == wx.ID_OK:
        DlgResult = dlg.GetStringSelection()
        dlg.Destroy()

    else:
        dlg.Destroy()
        DlgResult = False

    logger.debug("ShowThreadChoiceDlg(): Result of Thread Choice Dialog was: "+unicode(DlgResult))

def ShowChoiceDlg(Message, Title, Choices, AllowCancel=False):
    """Handle showing thread choice dialogs, reducing code duplication and complications and errors.
    It can be used like this: DialogTools().ShowChoiceDlg(Message=<message>, Title=<title>, Choices=<choices>)
    Message is whatever you want the dialog to say.
    Title sets the title bar text on the dialog.
    Choices is a list of choices you want the dialog to display.
    """
    global DlgResult

    while True:
        DlgResult = None

        wx.CallAfter(ShowThreadChoiceDlg, msg=Message, title=Title, choices=Choices)

        #Trap the thread until the user responds.
        while DlgResult == None:
            time.sleep(0.5)

        #Don't let the user bypass any choice dialogs.
        if DlgResult in ("", False) and AllowCancel == False:
            logger.warning("ShowChoiceDlg(): User closed dialog without answering. Warning user and asking again...")
            ShowMsgDlg(Kind="warning", Message="Please select an option.")

        else:
            return DlgResult

def ShowThreadTextEntryDlg(msg, title="WxFixBoot - Text Entry"):
    """Shows a text entry dialog from a thread upon instruction"""
    global DlgResult

    logger.debug("ShowThreadTextEntryDlg(): Showing Thread Text Entry Dialog...")
    dlg = wx.TextEntryDialog(ParentWindow.Panel, msg, title, "", style=wx.OK|wx.CANCEL, pos=wx.DefaultPosition)

    #Where possible, destroy just before setting DlgResult to avoid potential race conditions.
    if dlg.ShowModal() == wx.ID_OK:
        DlgResult = dlg.GetValue()
        dlg.Destroy()

    else:
        dlg.Destroy()
        DlgResult = False

    logger.debug("ShowThreadTextEntryDlg(): Result of Thread Text Entry Dlg was: "+unicode(DlgResult))

def ShowTextEntryDlg(Message, Title="WxFixBoot - Text Entry"):
    """Handle showing thread text entry dialogs, reducing code duplication and compilications and errors.
    It can be used like this: DialogTools().ShowTextEntryDlg(Message=<message>, Title=<title>)
    Message is whatever you want the dialog to say.
    Title sets the title bar text on the dialog.
    """
    global DlgResult

    while True:
        DlgResult = None

        wx.CallAfter(ShowThreadTextEntryDlg, msg=Message, title=Title)

        #Trap the thread until the user responds.
        while DlgResult == None:
            time.sleep(0.5)

        #Stop the user from avoiding entering anything.
        if DlgResult in ("", False):
            ShowMsgDlg(Kind="warning", Message="Please enter a valid name.")

        else:
            return DlgResult

def ShowThreadSaveFiledlg(title="WxFixBoot - Select A File", wildcard="All Files/Devices (*)|*"):
    """Shows a save file choice dialog from a thread upon instruction"""
    global DlgResult

    logger.debug("ShowThreadSaveFileDlg(): Showing Thread Save File Dialog...")
    dlg = wx.FileDialog(ParentWindow.Panel, message=title, defaultDir="/home", wildcard=wildcard, style=wx.SAVE|wx.OVERWRITE_PROMPT)

    #Where possible, destroy just before setting DlgResult to avoid potential race conditions.
    if dlg.ShowModal() == wx.ID_OK:
        dlg.Destroy()
        DlgResult = dlg.GetPath()

    else:
        dlg.Destroy()
        DlgResult = False

    logger.debug("ShowThreadSaveFileDlg(): Result of Thread Save File Dialog was: "+unicode(DlgResult))

def ShowSaveFileDlg(Title="WxFixBoot - Select A File", Wildcard="All Files/Devices (*)|*"):
    """Handle showing thread file dialogs, reducing code duplication and compilications and errors.
    It can be used like this: ShowFileDlg(Title=<title>, Wildcard=<wildcard>)
    Message is whatever you want the dialog to say.
    Wildcard is a | seperated list of file types to show, including their names as visible to the user.
    """
    global DlgResult

    while True:
        DlgResult = None

        wx.CallAfter(ShowThreadSaveFiledlg, title=Title, wildcard=Wildcard)

        #Trap the thread until the user responds.
        while DlgResult == None:
            time.sleep(0.5)

        #Stop the user from avoiding entering anything.
        if DlgResult == False:
            ShowMsgDlg(Kind="warning", Message="Please select a valid file.")

        else:
            return DlgResult
