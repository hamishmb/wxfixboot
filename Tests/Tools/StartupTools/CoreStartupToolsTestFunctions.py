#!/usr/bin/env python
# -*- coding: utf-8 -*- 
# CoreStartupTools test functions for WxFixBoot Version 2.0.1
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

def DeterminePackageManager(APTCmd, YUMCmd):
    """Determine and return the package manager using the given command strings."""
    PackageManager = "Unknown"

    for Cmd in (APTCmd, YUMCmd):
        Retval = CoreTools.StartProcess(Cmd, ShowOutput=False)

        if Retval != 0:
            if Cmd == APTCmd:
                #Couldn't find apt!
                continue

            else:
                pass

        else:
            if Cmd == APTCmd:
                #Found APT!
                PackageManager = "apt-get"
                break

            else:
                #Found YUM!
                PackageManager = "yum"
                break

    return PackageManager

def GetFSTabInfo(MountPoint, OSName):
    """Get /etc/fstab info and related info (EFI Partition, /boot partition) for the given OS at the given mountpoint."""
    #Do some setup.
    EFIPartition = "Unknown"
    BootPartition = "Unknown"

    #Read the raw contents of the /etc/fstab file.
    FSTabFile = open(MountPoint+"/etc/fstab", "r")
    RawFSTABContents = FSTabFile.read().split("\n")
    FSTabFile.close()

    #Gather some info from it.
    for Line in RawFSTABContents:
        #Ignore any comments.
        if "#" in Line or Line == "":
            continue

        #Try to find this OS's EFI and boot partitions (if there are any).
        if Line.split()[1] == "/boot/efi" or Line.split()[1] == "/boot":
            Temp = Line.split()[0]

            #If we have a UUID, convert it into a device node.
            if "UUID=" in Temp:
                UUID = Temp.split("=")[1]

                for Disk in DiskInfo.keys():
                    if DiskInfo[Disk]["UUID"] == UUID:
                        Temp = Disk
                        break

            #In case we had a UUID with no match, check again before adding it to OSInfo, else ignore it.
            if "/dev/" in Temp:
                Disk = Temp

            else:
                Disk = "Unknown"

        #Try to find this OS's /boot partition (if there is one).
        if Line.split()[1] == "/boot/efi":
            EFIPartition = Disk

        elif Line.split()[1] == "/boot":
            BootPartition = Disk

    #Return stuff.
    return (RawFSTABContents, EFIPartition, BootPartition)

def DetermineOSArchitecture(MountPoint):
    """Look for OS architecture on given partition."""
    #Do setup.
    OSArch = None
    Cmd = "arch"

    while True:
        if MountPoint != "":
            Cmd = "chroot "+MountPoint+" "+Cmd

        Retval, OSArch = CoreTools.StartProcess(Cmd, ReturnOutput=True)

        #If the command failed, try a second approach.
        if Retval != 0 and "arch" in Cmd:
            Cmd = "file /sbin/init"

        elif Retval != 0:
            OSArch = None
            break

        else:
            break

    #If the command that worked was 'arch', or both failed, we can just return it.
    if "arch" in Cmd or Retval != 0:
        #Return the arch (or None, if we didn't find it).
        return OSArch

    else:
        if "32-bit" in OSArch:
            OSArch = "i386"

        else:
            OSArch = "x86_64"

        return OSArch
