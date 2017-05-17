#!/usr/bin/env python
# -*- coding: utf-8 -*- 
# HelperBackendTools test functions for WxFixBoot Version 2.0.1
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

#If you're wondering why this is here, it's so that there are some known good/sane functions to aid testing the ones in DialogTools.

#Do future imports to prepare to support python 3. Use unicode strings rather than ASCII strings, as they fix potential problems.
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

MsgDlgMessages = []

def AskUserIfCorrect(Info):
    Dlg = wx.MessageDialog(None, "Was the correct dialog shown and displayed properly? Was your result "+unicode(Info)+"?", "WxFixBoot - Dialog Tests", wx.YES_NO | wx.ICON_QUESTION)

    if Dlg.ShowModal() == wx.ID_YES:
        Result = True

    else:
        Result = False

    Dlg.Destroy()

    return Result

#For comparing to functions with same name in HelpersBackendTools.
def FindMissingFSCKModules():
    """Check for and return all missing fsck modules (fsck.vfat, fsck.minix, etc)."""
    FailedList = []

    Keys = DiskInfo.keys()
    Keys.sort()

    for Disk in Keys:
        #Check the FSType is known and isn't swap.
        if DiskInfo[Disk]["FileSystem"] not in ("Unknown", "N/A"):
            #Check if this module is present.
            if CoreTools.StartProcess("which fsck."+DiskInfo[Disk]["FileSystem"], ShowOutput=False) != 0:
                #Couldn't find it, add it to the failed list.
                FailedList.append("fsck."+DiskInfo[Disk]["FileSystem"])

            else:
                pass

    #Return the list, so FSCheck functions know which FSes to ignore.
    return FailedList

def FindCheckableFileSystems():
    """Find all checkable filesystems, and then return them to EssentialBackendTools().FileSystemCheck()"""
    #Do setup.
    DoNotCheckList = []
    FileSystemsToCheck = {}
    RootFS = CoreTools.GetPartitionMountedAt("/")

    #Get a list of missing fsck modules (if any) based on the existing filesystems.
    MissingFSCKModules = FindMissingFSCKModules()

    Keys = DiskInfo.keys()
    Keys.sort()

    #Determine checkable partitions.
    for Disk in Keys:
        #Ignore all devices.
        if DiskInfo[Disk]["Type"] == "Device":
            continue

        #Check if the required fsck module is present, and that the partition isn't RootFS
        if "fsck."+DiskInfo[Disk]["FileSystem"] in MissingFSCKModules:
            MountPoint = "None"
            CheckTheFS = False
            RemountPartitionAfter = False

        else:
            #If we're not running on a live disk, skip the filesystem if it's the same as RootFS (in which case checking it may corrupt data).
            if SystemInfo["IsLiveDisk"] == False and Disk == RootFS:
                MountPoint = "/"
                CheckTheFS = False
                RemountPartitionAfter = False
                continue

            #Check if the partition is mounted.
            if CoreTools.IsMounted(Disk) == False:
                MountPoint = "None"
                CheckTheFS = True
                RemountPartitionAfter = False

            else:
                #Unmount the FS temporarily, to avoid data corruption.
                MountPoint = CoreTools.GetMountPointOf(Disk)

                if CoreTools.Unmount(Disk) != 0:
                    CheckTheFS = False
                    RemountPartitionAfter = False

                else:
                    CheckTheFS = True
                    RemountPartitionAfter = True

        if CheckTheFS:
            #Add it to the dictionary for checking.
            FileSystemsToCheck[Disk] = {}
            FileSystemsToCheck[Disk]["Remount"] = RemountPartitionAfter
            FileSystemsToCheck[Disk]["MountPoint"] = MountPoint

        else:
            #Add it to the non-checkable list
            DoNotCheckList.append(Disk+" with Filesystem: "+DiskInfo[Disk]["FileSystem"])

    #Report uncheckable partitions.
    if DoNotCheckList != []: pass
        #Some filesystems will not be checked. Tell the user. ***DISABLED
        #DialogTools.ShowMsgDlg(Kind="info", Message="The following filesystems will not be checked:\n\n"+'\n'.join(DoNotCheckList)+".\n\nThe most likely reason for this is that some of the filesystems are in use, or that the required filesystem checkers weren't found. WxFixBoot will now continue to check the remaining filesystems.")

    return FileSystemsToCheck

#These all trick the HelperBackendTools to calling a different function to those found in DialogTools without modifying the code.
#Return DlgResult too so it behaves the same way.

def ShowMsgDlg(Message, Kind="info"):
    """Shows a message dialog from a thread upon instruction. All of these windows are logged but silenced."""
    if Kind == "info":
        Title = "WxFixBoot - Information"
        style = wx.OK | wx.ICON_INFORMATION

    elif Kind == "warning":
        Title = "WxFixBoot - Warning"
        style = wx.OK | wx.ICON_EXCLAMATION

    elif Kind == "error":
        Title = "WxFixBoot - Error"
        style = wx.OK | wx.ICON_ERROR

    MsgDlgMessages.append(Message)

def ShowRealMsgDlg(Message, Kind="info"):
    """Shows a message dialog from a thread upon instruction"""
    if Kind == "info":
        Title = "WxFixBoot - Information"
        style = wx.OK | wx.ICON_INFORMATION

    elif Kind == "warning":
        Title = "WxFixBoot - Warning"
        style = wx.OK | wx.ICON_EXCLAMATION

    elif Kind == "error":
        Title = "WxFixBoot - Error"
        style = wx.OK | wx.ICON_ERROR

    dlg = wx.MessageDialog(ParentWindow.Panel, Message, Title, style, pos=wx.DefaultPosition)
    dlg.ShowModal()
    dlg.Destroy()

def ShowYesNoDlg(Message, Title="WxFixBoot - Question", Buttons=(None, None)):
    """Shows a yes/no dialog from a thread upon instruction"""
    dlg = wx.MessageDialog(ParentWindow.Panel, Message, Title, wx.YES_NO | wx.ICON_QUESTION)

    #Try to set custom Buttons labels if needed (handle attribute error on wx 2.8.11).
    if Buttons != (None, None):
        try:
            if dlg.SetYesNoLabels(Buttons[0], Buttons[1]):
                #If it worked get rid of the last unneccessary sentence in the message.
                dlg.SetMessage(' '.join(Message.split(".")[0:-1]))

        except AttributeError: pass

    #Where possible, destroy just before setting DlgResult to avoid potential race conditions.
    if dlg.ShowModal() == wx.ID_YES:
        dlg.Destroy()
        DlgResult = True

    else:
        dlg.Destroy()
        DlgResult = False

    return DlgResult

def ShowChoiceDlg(Message, Choices, Title="WxFixBoot - Select an Option"):
    """Shows a choice dialog from a thread upon instruction"""
    dlg = wx.SingleChoiceDialog(ParentWindow.Panel, Message, Title, Choices, pos=wx.DefaultPosition)

    #Where possible, destroy just before setting DlgResult to avoid potential race conditions.
    if dlg.ShowModal() == wx.ID_OK:
        DlgResult = dlg.GetStringSelection()
        dlg.Destroy()

    else:
        dlg.Destroy()
        DlgResult = False

    return DlgResult

def ShowTextEntryDlg(Message, Title="WxFixBoot - Text Entry"):
    """Shows a text entry dialog from a thread upon instruction"""
    dlg = wx.TextEntryDialog(ParentWindow.Panel, Message, Title, "", style=wx.OK|wx.CANCEL, pos=wx.DefaultPosition)

    #Where possible, destroy just before setting DlgResult to avoid potential race conditions.
    if dlg.ShowModal() == wx.ID_OK:
        DlgResult = dlg.GetValue()
        dlg.Destroy()

    else:
        dlg.Destroy()
        DlgResult = False

    return DlgResult

def ShowSaveFiledlg(Title="WxFixBoot - Select A File", Wildcard="All Files/Devices (*)|*"):
    """Shows a save file choice dialog from a thread upon instruction"""
    dlg = wx.FileDialog(ParentWindow.Panel, message=Title, defaultDir="/home", wildcard=Wildcard, style=wx.SAVE|wx.OVERWRITE_PROMPT)

    #Where possible, destroy just before setting DlgResult to avoid potential race conditions.
    if dlg.ShowModal() == wx.ID_OK:
        dlg.Destroy()
        DlgResult = dlg.GetPath()

    else:
        dlg.Destroy()
        DlgResult = False

    return DlgResult

#Checks if system can perform certain tests.
def CanPerformFindMissingFSCKModulesTest1():
    return (os.path.isfile("/sbin/fsck.jfs") and os.path.isfile("/sbin/fsck.ext4") and os.path.isfile("/sbin/fsck.ext3") and os.path.isfile("/sbin/fsck.vfat"))

#End Main Class.
