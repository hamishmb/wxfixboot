#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Core Startup Tools in the StartupTools Package for WxFixBoot Version 2.0~pre2
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

#Begin Main Class. *** Optimise/Reorganise this again later ***
class Main():
    def LookForBootloadersOnPartition(self, PackageManager, MountPoint, UsingChroot): #*** Test this thoroughly ***
        """Look for bootloaders installed in the OS in the given mount point."""
        if UsingChroot:
            logger.debug("CoreStartupTools: Main().LookForBootloadersOnPartition(): Looking for bootloaders in "+MountPoint+"...")

        else:
            logger.debug("CoreStartupTools: Main().LookForBootloadersOnPartition(): Looking for bootloaders in / (Current OS)...")

        #Okay, let's run a command in the chroot that was set up in self.FindBootloaderRemovalOSs(), depending on which package manager this OS uses, and which bootloader is currently installed.
        if PackageManager == "apt-get":
            Cmd = "dpkg --get-selections"

        else:
            Cmd = "yum list installed"

        if UsingChroot:
            Cmd = "chroot "+MountPoint+" "+Cmd

        Output = CoreTools.StartProcess(Cmd, ShowOutput=False, ReturnOutput=True)[1].split("\n")

        #Look for them in a specific order (grub2 before legacy) to be as fast a possible and to avoid false positives.
        if PackageManager == "apt-get":
            BootloaderPackages = ("grub-efi", "elilo", "grub-pc", "lilo", "grub")
            PackageDict = {"grub-efi": "GRUB-UEFI", "elilo": "ELILO", "grub-pc": "GRUB2", "lilo": "LILO", "grub": "GRUB-LEGACY"}

        else:
            BootloaderPackages = ("grub2-efi", "grub2", "grub")
            PackageDict = {"grub2-efi": "GRUB-UEFI", "grub2": "GRUB2", "grub": "GRUB-LEGACY"}

        for Package in BootloaderPackages:
            Found = False

            for Line in Output:
                if Package in Line:
                    if PackageManager == "apt-get":
                        if Line.split()[1] != "install":
                            continue

                    Found = True
                    break

            if Found:
                Bootloader = PackageDict[Package]
                logger.info("CoreStartupTools: Main().LookForBootloadersOnPartition(): Found "+Bootloader+"...")
                return Bootloader

        #If we get here, we didn't find anything.
        return None

    def GetFSTabInfo(self, MountPoint, OSName): #*** Test this thoroughly ***
        """Get /etc/fstab info and related info (EFI Partition, /boot partition) for the given OS at the given mountpoint."""
        logger.debug("CoreStartupTools: Main().GetFSTabInfo(): Getting FSTab info in "+MountPoint+"/etc/fstab for "+OSName+"...")

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
                logger.debug("CoreStartupTools: Main().GetFSTabInfo(): Finding partition that automounts at /boot/efi or /boot...")
                Temp = Line.split()[0]

                #If we have a UUID, convert it into a device node.
                if "UUID=" in Temp:
                    UUID = Temp.split("=")[1]
                    logger.debug("CoreStartupTools: Main().GetFSTabInfo(): Found UUID "+UUID+". Trying to find device name...")

                    for Disk in DiskInfo.keys():
                        if DiskInfo[Disk]["UUID"] == UUID:
                            Temp = Disk
                            break

                #In case we had a UUID with no match, check again before adding it to OSInfo, else ignore it.
                if "/dev/" in Temp:
                    logger.debug("CoreStartupTools: Main().GetFSTabInfo(): Found EFI/Boot Partition "+Temp+"...")
                    Disk = Temp

                else:
                    logger.error("CoreStartupTools: Main().GetFSTabInfo(): Couldn't determine device name! Ignoring this device...")
                    Disk = "Unknown"

            #Try to find this OS's /boot partition (if there is one).
            if Line.split()[1] == "/boot/efi":
                EFIPartition = Disk

            elif Line.split()[1] == "/boot":
                BootPartition = Disk

        #Return stuff.
        return (RawFSTABContents, EFIPartition, BootPartition)

    def DetermineOSArchitecture(self, Partition, Chroot):
        """Look for OS architecture on given partition, looking for 64-bit first, then 32-bit."""
        logger.info("CoreStartupTools: Main().DetermineOSArchitecture(): Trying to find OS arch for OS on "+Partition+"...")

        #Do setup and look for 64-bit first.
        OSArch = None
        WantedArch = "64-bit"

        cmd = "file -L /usr/bin/ld"

        #If we're using chroot, add that to the command.
        if Chroot == True:
            cmd = "chroot /mnt"+Partition+" "+cmd

        Retval, Output = CoreTools.StartProcess(cmd, ReturnOutput=True)

        #If the command failed, give up.
        if Retval != 0:
            return None

        #Use a loop to avoid duplicating code.
        while OSArch == None:
            #Now let's check if the OS uses this architecture.
            if WantedArch in Output:
                logger.info("CoreStartupTools: Main().DetermineOSArchitecture(): OS on "+Partition+" is "+WantedArch+"...")
                OSArch = WantedArch

            elif WantedArch == "64-bit":
                #Now look for 32-bit and restart the loop.
                logger.info("CoreStartupTools: Main().DetermineOSArchitecture(): OS on "+Partition+" isn't 64-bit. Looking for a 32-bit OS...")
                WantedArch = "32-bit"

            else:
                #We couldn't find it as either 32-bit or 64-bit!
                logger.info("CoreStartupTools: Main().DetermineOSArchitecture(): Couldn't find architecture for OS on "+Partition+"! Returning None...")
                break

        #Return the arch (or None, if we didn't find it).
        return OSArch

    def AskForOSName(self, Partition, OSArch, IsCurrentOS):
        """Ask the user if an OS exists on the given partition."""
        logger.info("CoreStartupTools: Main().AskForOSName(): Asking the user for the name of the OS in "+Partition+"...")

        if IsCurrentOS:
            DialogTools.ShowMsgDlg(Kind="warning", Message="WxFixBoot couldn't find the name of the current OS. Please name it so that WxFixBoot can function correctly.")
            Result = True

        else:
            Result = DialogTools.ShowYesNoDlg(Message="There is a Linux operating system on partition: "+Partition+" but WxFixBoot couldn't find its name. It isn't the currently running OS. Do you want to name it and include it in the list? Only click yes if you believe it is a recent OS. Click Yes if you want to name it, otherwise click No.", Buttons=("Name it", "Don't name it."))

        if Result == False:
            logger.info("CoreStartupTools: Main().AskForOSName(): User didn't want to name the OS in "+Partition+"! Ignoring it...")
            #User reported no OS in this partition, ignore it.
            return None

        else:
            logger.debug("CoreStartupTools: Main().AskForOSName(): User reported recent Linux OS in "+Partition+". Asking name of OS...")
            #User reported that an OS is here.
            Result = DialogTools.ShowTextEntryDlg(Message="Please enter the name of the operating system that is on "+Partition+".\nThe name you specify will be used later in the program", Title="WxFixBoot - Enter OS Name")

            return Result

#End main Class.
