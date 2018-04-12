#!/usr/bin/env python
# -*- coding: utf-8 -*- 
# HelperBackendTools test functions for WxFixBoot Version 2.0.3
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

#If you're wondering why this is here, it's so that there are some known good/sane functions to aid testing the ones in DialogTools.

#Do future imports to prepare to support python 3. Use unicode strings rather than ASCII strings, as they fix potential problems.
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

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

                if MountPoint in ("/", "/home"): #Don't actually unmount, would cause differences in output. Try to simulate if it was successful or not instead.
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

#Checks if system can perform certain tests.
def CanPerformFindMissingFSCKModulesTest1():
    return (os.path.isfile("/sbin/fsck.jfs") and os.path.isfile("/sbin/fsck.ext4") and os.path.isfile("/sbin/fsck.ext3") and os.path.isfile("/sbin/fsck.vfat"))

#End Main Class.
