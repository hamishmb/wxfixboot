#!/usr/bin/env python
# -*- coding: utf-8 -*-
# HelperBackendTools test functions for WxFixBoot Version 3.0.0
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

#Import modules
import os
import sys

#Import other modules.
sys.path.append('../../..') #Need to be able to import the Tools module from here.

import Tools.coretools as CoreTools

#Declare global dictionaries to silence pylint warnings.
DiskInfo = {}
SystemInfo = {}

#For comparing to functions with same name in HelpersBackendTools.
def find_missing_fsck_modules():
    """Check for and return all missing fsck modules (fsck.vfat, fsck.minix, etc)."""
    failed_list = []

    keys = list(DiskInfo.keys())
    keys.sort()

    for disk in keys:
        #Check the FSType is known and isn't swap.
        if DiskInfo[disk]["FileSystem"] not in ("Unknown", "N/A"):
            #Check if this module is present.
            if CoreTools.start_process("which fsck."+DiskInfo[disk]["FileSystem"], show_output=False) != 0:
                #Couldn't find it, add it to the failed list.
                failed_list.append("fsck."+DiskInfo[disk]["FileSystem"])

            else:
                pass

    #Return the list, so FSCheck functions know which FSes to ignore.
    return failed_list

def find_checkable_file_systems():
    """Find all checkable filesystems, and then return them to EssentialBackendTools().FileSystemCheck()"""
    #Do setup.
    do_not_check_list = []
    filesystems_to_check = {}
    root_fs = CoreTools.get_partition_mounted_at("/")

    #Get a list of missing fsck modules (if any) based on the existing filesystems.
    missing_fsck_modules = find_missing_fsck_modules()

    keys = list(DiskInfo.keys())
    keys.sort()

    #Determine checkable partitions.
    for disk in keys:
        #Ignore all devices.
        if DiskInfo[disk]["Type"] == "Device":
            continue

        #Check if the required fsck module is present, and that the partition isn't root_fs
        if "fsck."+DiskInfo[disk]["FileSystem"] in missing_fsck_modules:
            mount_point = "None"
            check_the_fs = False
            remount_partition_after = False

        else:
            #If we're not running on a live disk, skip the filesystem if it's the same as root_fs (in which case checking it may corrupt data).
            if SystemInfo["IsLiveDisk"] is False and disk == root_fs:
                mount_point = "/"
                check_the_fs = False
                remount_partition_after = False
                continue

            #Check if the partition is mounted.
            if CoreTools.is_mounted(disk) is False:
                mount_point = "None"
                check_the_fs = True
                remount_partition_after = False

            else:
                #Unmount the FS temporarily, to avoid data corruption.
                mount_point = CoreTools.get_mount_point_of(disk)

                if mount_point in ("/", "/home"): #Don't actually unmount, would cause differences in output. Try to simulate if it was successful or not instead.
                    check_the_fs = False
                    remount_partition_after = False

                else:
                    check_the_fs = True
                    remount_partition_after = True

        if check_the_fs:
            #Add it to the dictionary for checking.
            filesystems_to_check[disk] = {}
            filesystems_to_check[disk]["Remount"] = remount_partition_after
            filesystems_to_check[disk]["MountPoint"] = mount_point

        else:
            #Add it to the non-checkable list
            do_not_check_list.append(disk+" with Filesystem: "+DiskInfo[disk]["FileSystem"])

    #Report uncheckable partitions.
    if do_not_check_list != []:
        pass
        #Some filesystems will not be checked. Tell the user. ***DISABLED
        #DialogTools.ShowMsgDlg(Kind="info", Message="The following filesystems will not be checked:\n\n"+'\n'.join(do_not_check_list)+".\n\nThe most likely reason for this is that some of the filesystems are in use, or that the required filesystem checkers weren't found. WxFixBoot will now continue to check the remaining filesystems.")

    return filesystems_to_check

#Checks if system can perform certain tests.
def CanPerformFindMissingFSCKModulesTest1():
    return (os.path.isfile("/sbin/fsck.jfs") and os.path.isfile("/sbin/fsck.ext4") and os.path.isfile("/sbin/fsck.ext3") and os.path.isfile("/sbin/fsck.vfat"))

#End Main Class.
