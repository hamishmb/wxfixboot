#!/usr/bin/env python3
# -*- coding: utf-8 -*- 
# Test functions for Displaying Dialogs for WxFixBoot
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

#If you're wondering why this is here, it's so that there are some known good/sane functions to
#aid testing the ones in DialogTools.

#Do future imports to prepare to support python 3. Use unicode strings rather than ASCII
#strings, as they fix potential problems.
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import sys
import wx

#Make unicode an alias for str in Python 3.
if sys.version_info[0] == 3:
    #Disable cos necessary to keep supporting python 2.
    unicode = str #pylint: disable=redefined-builtin,invalid-name

#These hold results from the dialog functions.
MSG_DLG_MESSAGES = []
YESNO_DLG_RESULTS = []
CHOICE_DLG_RESULTS = []
TEXT_ENTRY_DLG_RESULTS = []
SAVE_FILE_DLG_RESULTS = []

def ask_user_if_correct(info):
    dlg = wx.MessageDialog(None, "Was the correct dialog shown and displayed properly? Was your "
                           + "result "+unicode(info)+"?", "WxFixBoot - Dialog Tests",
                           wx.YES_NO | wx.ICON_QUESTION)

    result = (dlg.ShowModal() == wx.ID_YES)

    dlg.Destroy()

    return result

#These all trick the Tools into calling a different function to those found in DialogTools without
#modifying the code. Return dlg_result too so it behaves the same way.

def show_msg_dlg(message, kind="info"):
    """
    Shows a message dialog from a thread upon instruction.
    All of these windows are logged but silenced.
    """

    if kind == "info":
        title = "WxFixBoot - Information" #pylint: disable=unused-variable
        style = wx.OK | wx.ICON_INFORMATION #pylint: disable=unused-variable

    elif kind == "warning":
        title = "WxFixBoot - Warning" #pylint: disable=unused-variable
        style = wx.OK | wx.ICON_EXCLAMATION #pylint: disable=unused-variable

    elif kind == "error":
        title = "WxFixBoot - Error" #pylint: disable=unused-variable
        style = wx.OK | wx.ICON_ERROR #pylint: disable=unused-variable

    MSG_DLG_MESSAGES.append(message)

def show_real_msg_dlg(message, kind="info"):
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

    dlg = wx.MessageDialog(wx.GetApp().TopWindow, message, title, style, pos=wx.DefaultPosition)
    dlg.ShowModal()
    dlg.Destroy()
    wx.GetApp().Yield()

def show_yes_no_dlg(message, title="WxFixBoot - Question", buttons=(None, None)):
    """Shows a yes/no dialog from a thread upon instruction"""
    dlg = wx.MessageDialog(wx.GetApp().TopWindow, message, title, wx.YES_NO | wx.ICON_QUESTION)

    #Try to set custom buttons labels if needed (handle attribute error on wx 2.8.11).
    if buttons != (None, None):
        try:
            if dlg.SetYesNoLabels(buttons[0], buttons[1]):
                #If it worked get rid of the last unneccessary sentence in the message.
                dlg.SetMessage('.'.join(message.split(".")[0:-1]))

        except AttributeError:
            pass

    #Where possible, destroy just before setting dlg_result to avoid potential race conditions.
    if dlg.ShowModal() == wx.ID_YES:
        dlg.Destroy()
        dlg_result = True

    else:
        dlg.Destroy()
        dlg_result = False

    wx.GetApp().Yield()

    YESNO_DLG_RESULTS.append(dlg_result)

    return dlg_result

def show_choice_dlg(message, choices, title="WxFixBoot - Select an Option"):
    """Shows a choice dialog from a thread upon instruction"""
    dlg = wx.SingleChoiceDialog(wx.GetApp().TopWindow, message, title, choices,
                                pos=wx.DefaultPosition)

    #Where possible, destroy just before setting dlg_result to avoid potential race conditions.
    if dlg.ShowModal() == wx.ID_OK:
        dlg_result = dlg.GetStringSelection()
        dlg.Destroy()

    else:
        dlg.Destroy()
        dlg_result = False

    wx.GetApp().Yield()

    CHOICE_DLG_RESULTS.append(dlg_result)

    return dlg_result

def show_text_entry_dlg(message, title="WxFixBoot - Text Entry"):
    """Shows a text entry dialog from a thread upon instruction"""
    dlg = wx.TextEntryDialog(wx.GetApp().TopWindow, message, title, "", style=wx.OK|wx.CANCEL,
                             pos=wx.DefaultPosition)

    #Where possible, destroy just before setting dlg_result to avoid potential race conditions.
    if dlg.ShowModal() == wx.ID_OK:
        dlg_result = dlg.GetValue()
        dlg.Destroy()

    else:
        dlg.Destroy()
        dlg_result = False

    wx.GetApp().Yield()

    TEXT_ENTRY_DLG_RESULTS.append(dlg_result)

    return dlg_result

def show_save_file_dlg(title="WxFixBoot - Select A File", wildcard="All Files/Devices (*)|*"):
    """Shows a save file choice dialog from a thread upon instruction"""
    dlg = wx.FileDialog(wx.GetApp().TopWindow, message=title, defaultDir="/home", wildcard=wildcard,
                        style=wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT)

    #Where possible, destroy just before setting dlg_result to avoid potential race conditions.
    if dlg.ShowModal() == wx.ID_OK:
        dlg.Destroy()
        dlg_result = dlg.GetPath()

    else:
        dlg.Destroy()
        dlg_result = False

    wx.GetApp().Yield()

    SAVE_FILE_DLG_RESULTS.append(dlg_result)

    return dlg_result

#End Main Class.
