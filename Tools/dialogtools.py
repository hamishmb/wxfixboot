#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Dialog Tools in the Tools Package for WxFixBoot
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

# pylint: disable=logging-not-lazy, global-statement
#
# Reason (logging-not-lazy): This is a more readable way of logging.
# Reason (global-statement): Need to use it here.

"""
This module provides the standard dialogs and related control functions used by WxFixBoot.

This provides the extra "show_thread..." functions to enable calling dialogs from background
threads - for example the thread that is used for backend operations when modifying the
bootloader.
"""

#Do future imports to prepare to support python 3. Use unicode strings rather than ASCII
#strings, as they fix potential problems.
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

#Import modules.
import time
import sys
import threading
import logging
import wx

#Make unicode an alias for str in Python 3.
if sys.version_info[0] == 3:
    unicode = str #pylint: disable=redefined-builtin,invalid-name
    str = bytes #pylint: disable=redefined-builtin,invalid-name

#Set up logging.
logger = logging.getLogger(__name__)
logger.setLevel(logging.getLogger("WxFixBoot").getEffectiveLevel())

#Global declarations.
DLGCLOSED = False
DLGRESULT = False

def is_gui_thread():
    """
    Used to determine if the current thread is the GUI thread.
    Performing this check enables us to use theese convenience
    functions in the GUI thread as well.

    Args:
        None

    Returns:
        boolean - Whether or not this is the GUI thread.
    """
    #New version for Python 3 (more reliable).
    if sys.version_info[0] == 3:
        return threading.current_thread() is threading.main_thread()

    #Legacy support for Python 2.
    else:
        return isinstance(threading.current_thread(), threading._MainThread)

def show_thread_msg_dlg(msg, kind="info"):
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

    dlg = wx.MessageDialog(wx.GetApp().TopWindow.panel, msg, title, style, pos=wx.DefaultPosition)
    dlg.ShowModal()
    dlg.Destroy()

    global DLGCLOSED
    DLGCLOSED = True

    logger.debug("ShowThreadMessageDlg(): Thread Message Dialog has been closed by user.")

def show_msg_dlg(message, kind="info"):
    """
    Handle showing thread message dialogs, reducing code duplication and complications and errors.
    It can be used like this: DialogTools().show_msg_dlg(kind=<kind>, message=<message>).
    kind is one of 'info', 'warning' or 'error'.
    message is whatever you want the dialog to say.
    """

    if is_gui_thread():
        show_thread_msg_dlg(message, kind)
        return

    global DLGCLOSED
    DLGCLOSED = None
    wx.CallAfter(show_thread_msg_dlg, kind=kind, msg=message)

    #Trap the thread until the user responds.
    while DLGCLOSED is None:
        time.sleep(0.5)

def show_thread_yes_no_dlg(msg, title="WxFixBoot - Question", buttons=(None, None)):
    """Shows a yes/no dialog from a thread upon instruction"""
    logger.debug("show_thread_yes_no_dlg(): Showing Thread Yes/No Dialog...")
    dlg = wx.MessageDialog(wx.GetApp().TopWindow.panel, msg, title, wx.YES_NO | wx.ICON_QUESTION)

    global DLGRESULT

    #Try to set custom button labels if desired.
    if buttons != (None, None):
        if dlg.SetYesNoLabels(buttons[0], buttons[1]):
            #If it worked get rid of the last unneccessary sentence in the message.
            #(A click yes for X, click no for Y sentence).
            dlg.SetMessage('.'.join(msg.split(".")[0:-1]))

    #Where possible, destroy just before setting DLGRESULT to avoid potential race conditions.
    if dlg.ShowModal() == wx.ID_YES:
        dlg.Destroy()
        DLGRESULT = True

    else:
        dlg.Destroy()
        DLGRESULT = False

    logger.debug("show_thread_yes_no_dlg(): Result of Thread Yes/No Dialog was: "
                 + unicode(DLGRESULT))

def show_yes_no_dlg(message, title="WxFixBoot - Question", buttons=(None, None)):
    """
    Handle showing thread yes/no dialogs, reducing code duplication and compilications and errors.
    It can be used like this: DialogTools().show_yes_no_dlg(message=<message>, title=<title>)
    message is whatever you want the dialog to say.
    buttons is the text for the button labels.
    title sets the title bar text on the dialog.
    """

    global DLGRESULT
    DLGRESULT = None

    if is_gui_thread():
        show_thread_yes_no_dlg(message, title, buttons)
        return DLGRESULT

    wx.CallAfter(show_thread_yes_no_dlg, msg=message, title=title, buttons=buttons)

    #Trap the thread until the user responds.
    while DLGRESULT is None:
        time.sleep(0.5)

    return DLGRESULT

def show_thread_choice_dlg(msg, choices, title="WxFixBoot - Select an Option"):
    """Shows a choice dialog from a thread upon instruction"""
    global DLGRESULT

    logger.debug("show_thread_choice_dlg(): Showing Thread Choice Dialog...")
    dlg = wx.SingleChoiceDialog(wx.GetApp().TopWindow.panel, msg, title, choices,
                                pos=wx.DefaultPosition)

    #Where possible, destroy just before setting DLGRESULT to avoid potential race conditions.
    if dlg.ShowModal() == wx.ID_OK:
        DLGRESULT = dlg.GetStringSelection()
        dlg.Destroy()

    else:
        dlg.Destroy()
        DLGRESULT = False

    logger.debug("show_thread_choice_dlg(): Result of Thread Choice Dialog was: "
                 + unicode(DLGRESULT))

def show_choice_dlg(message, title, choices, allow_cancel=False):
    """
    Handle showing thread choice dialogs, reducing code duplication and complications and errors.
    It can be used like this:

    DialogTools().show_choice_dlg(message=<message>, title=<title>, choices=<choices>)

    message is whatever you want the dialog to say.
    title sets the title bar text on the dialog.
    choices is a list of choices you want the dialog to display.
    """

    global DLGRESULT

    if is_gui_thread():
        show_thread_choice_dlg(message, choices, title)
        return DLGRESULT

    while True:
        DLGRESULT = None

        wx.CallAfter(show_thread_choice_dlg, msg=message, title=title, choices=choices)

        #Trap the thread until the user responds.
        while DLGRESULT is None:
            time.sleep(0.5)

        #Don't let the user bypass this choice dialog if we aren't allowing it.
        if DLGRESULT in ("", False) and allow_cancel is False:
            logger.warning("show_choice_dlg(): User closed dialog without answering. Warning user "
                           + "and asking again...")

            show_msg_dlg(kind="warning", message="Please select an option.")

        else:
            return DLGRESULT

def show_thread_text_entry_dlg(msg, title="WxFixBoot - Text Entry"):
    """Shows a text entry dialog from a thread upon instruction"""
    global DLGRESULT

    logger.debug("show_thread_text_entry_dlg(): Showing Thread Text Entry Dialog...")
    dlg = wx.TextEntryDialog(wx.GetApp().TopWindow.panel, msg, title, "",
                             style=wx.OK|wx.CANCEL, pos=wx.DefaultPosition)

    #Where possible, destroy just before setting DLGRESULT to avoid potential race conditions.
    if dlg.ShowModal() == wx.ID_OK:
        DLGRESULT = dlg.GetValue()
        dlg.Destroy()

    else:
        dlg.Destroy()
        DLGRESULT = False

    logger.debug("show_thread_text_entry_dlg(): Result of Thread Text Entry Dlg was: "
                 + unicode(DLGRESULT))

def show_text_entry_dlg(message, title="WxFixBoot - Text Entry"):
    """
    Handle showing thread text entry dialogs, reducing code duplication, compilications and errors.
    It can be used like this: DialogTools().show_text_entry_dlg(message=<message>, title=<title>)
    message is whatever you want the dialog to say.
    title sets the title bar text on the dialog.
    """

    global DLGRESULT

    if is_gui_thread():
        show_thread_text_entry_dlg(message, title)
        return DLGRESULT

    while True:
        DLGRESULT = None

        wx.CallAfter(show_thread_text_entry_dlg, msg=message, title=title)

        #Trap the thread until the user responds.
        while DLGRESULT is None:
            time.sleep(0.5)

        #Stop the user from avoiding entering anything.
        if DLGRESULT in ("", False):
            show_msg_dlg(kind="warning", message="Please enter a valid name.")

        else:
            return DLGRESULT

def show_thread_save_file_dlg(title="WxFixBoot - Select A File",
                              wildcard="All Files/Devices (*)|*"):
    """Shows a save file choice dialog from a thread upon instruction"""
    global DLGRESULT

    logger.debug("show_thread_save_file_dlg(): Showing Thread Save File Dialog...")
    dlg = wx.FileDialog(wx.GetApp().TopWindow.panel, message=title, defaultDir="/home",
                        wildcard=wildcard, style=wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT)

    #Destroy just before setting DLGRESULT to avoid potential race conditions.
    #This is because another dialog might be opened immediately afterwards and reset DLGRESULT,
    #which would potentially cause issues.
    if dlg.ShowModal() == wx.ID_OK:
        temp = dlg.GetPath()
        dlg.Destroy()
        DLGRESULT = temp

    else:
        dlg.Destroy()
        DLGRESULT = False

    logger.debug("show_thread_save_file_dlg(): Result of Thread Save File Dialog was: "
                 + unicode(DLGRESULT))

def show_save_file_dlg(title="WxFixBoot - Select A File", wildcard="All Files/Devices (*)|*"):
    """
    Handle showing thread file dialogs, reducing code duplication and compilications and errors.
    It can be used like this: ShowFileDlg(title=<title>, wildcard=<wildcard>)
    message is whatever you want the dialog to say.
    wildcard is a | seperated list of file types to show, including their names as visible to
    the user.
    """

    global DLGRESULT

    if is_gui_thread():
        show_thread_save_file_dlg(title, wildcard)
        return DLGRESULT

    while True:
        DLGRESULT = None

        wx.CallAfter(show_thread_save_file_dlg, title=title, wildcard=wildcard)

        #Trap the thread until the user responds.
        while DLGRESULT is None:
            time.sleep(0.5)

        #Stop the user from avoiding entering anything.
        if DLGRESULT is False:
            show_msg_dlg(kind="warning", message="Please select a valid file.")

        else:
            return DLGRESULT
