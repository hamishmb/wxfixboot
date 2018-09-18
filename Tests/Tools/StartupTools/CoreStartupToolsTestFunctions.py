#!/usr/bin/env python
# -*- coding: utf-8 -*-
# CoreStartupTools test functions for WxFixBoot Version 3.0.0
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

#If you're wondering why this is here, it's so that there are some known good/sane
#functions to aid testing the ones in DialogTools.

#Do future imports to prepare to support python 3. Use unicode strings rather than ASCII
#strings, as they fix potential problems.
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

#Import modules.
import sys

#Import other modules.
sys.path.append('../../..') #Need to be able to import the Tools module from here.

import Tools.coretools as CoreTools

def determine_package_manager(apt_cmd, yum_cmd):
    """Determine and return the package manager using the given command strings."""
    package_manager = "Unknown"

    for cmd in (apt_cmd, yum_cmd):
        retval = CoreTools.start_process(cmd, show_output=False)

        if retval != 0:
            if cmd == apt_cmd:
                #Couldn't find apt!
                continue

            else:
                pass

        else:
            if cmd == apt_cmd:
                #Found APT!
                package_manager = "apt-get"
                break

            else:
                #Found YUM!
                package_manager = "yum"
                break

    return package_manager

def get_fstab_info(mount_point, os_name):
    """
    Get /etc/fstab info and related info (EFI partition, /boot partition) for the given OS
    at the given mountpoint.
    """

    #Do some setup.
    efi_partition = "Unknown"
    boot_partition = "Unknown"

    #Read the raw contents of the /etc/fstab file.
    fstab_file = open(mount_point+"/etc/fstab", "r")
    raw_fstab_contents = fstab_file.read().split("\n")
    fstab_file.close()

    #Gather some info from it.
    for line in raw_fstab_contents:
        #Ignore any comments.
        if "#" in line or line == "":
            continue

        #Try to find this OS's EFI and boot partitions (if there are any).
        if line.split()[1] == "/boot/efi" or line.split()[1] == "/boot":
            temp = line.split()[0]

            #If we have a UUID, convert it into a device node.
            if "UUID=" in temp:
                uuid = temp.split("=")[1]

                for disk in DiskInfo.keys():
                    if DiskInfo[disk]["UUID"] == uuid:
                        temp = disk
                        break

            #In case we had a UUID with no match, check again before adding it to OSInfo,
            #else ignore it.
            if "/dev/" in temp:
                disk = temp

            else:
                disk = "Unknown"

        #Try to find this OS's /boot partition (if there is one).
        if line.split()[1] == "/boot/efi":
            efi_partition = disk

        elif line.split()[1] == "/boot":
            boot_partition = disk

    #Return stuff.
    return (raw_fstab_contents, efi_partition, boot_partition)

def determine_os_architecture(mount_point):
    """Look for OS architecture on given partition."""
    #Do setup.
    os_arch = None
    cmd = "arch"

    while True:
        if mount_point != "":
            cmd = "chroot "+mount_point+" "+cmd

        retval, os_arch = CoreTools.start_process(cmd, return_output=True)

        #If the command failed, try a second approach.
        if retval != 0 and "arch" in cmd:
            cmd = "file /sbin/init"

        elif retval != 0:
            os_arch = None
            break

        else:
            break

    #If the command that worked was 'arch', or both failed, we can just return it.
    if "arch" in cmd or retval != 0:
        #Return the arch (or None, if we didn't find it).
        return os_arch

    else:
        if "32-bit" in os_arch:
            os_arch = "i386"

        else:
            os_arch = "x86_64"

        return os_arch

def get_os_name_with_lsb(partition, mount_point, is_current_os):
    """Attempt to get an OS's name using lsb_release -sd as a fallback."""
    if is_current_os:
        cmd = "lsb_release -sd"

    else:
        cmd = "chroot "+mount_point+" lsb_release -sd"

    retval, output = CoreTools.start_process(cmd, show_output=False, return_output=True)

    if retval != 0 or output == "":
        return "Unknown"

    #Otherwise...
    return output
