#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Core Startup Tools in the StartupTools Package for WxFixBoot Version 2.0~pre1
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

        if UsingChroot:
            Cmd = "chroot "+MountPoint+" "+Cmd

        Output = CoreTools.StartProcess(Cmd, ShowOutput=False, ReturnOutput=True)[1].split("\n")

        #Look for them in a specific order (grub2 before legacy) to be as fast a possible and to avoid false positives.
        if PackageManager == "apt-get":
            BootloaderPackages = ("grub-efi", "elilo", "grub-pc", "lilo", "grub")
            PackageDict = {"grub-efi": "GRUB-UEFI", "elilo": "ELILO", "grub-pc": "GRUB2", "lilo": "LILO", "grub": "GRUB-LEGACY"}

        for Package in BootloaderPackages:
            Found = False

            for Line in Output:
                if Package in Line and Line.split()[1] == "install":
                    Found = True
                    break

            if Found:
                Bootloader = PackageDict[Package]
                logger.info("CoreStartupTools: Main().LookForBootloadersOnPartition(): Found "+Bootloader+"...")
                return Bootloader

        #If we get here, we didn't find anything.
        return None

    def GetFSTabInfo(self, MountPoint, OSName): #*** Test this thoroughly *** *** Refactor ***
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

            #Try to find this OS's EFI partition (if there is one).
            if Line.split()[1] == "/boot/efi":
                logger.debug("CoreStartupTools: Main().GetFSTabInfo(): Finding partition that automounts at /boot/efi...")
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
                    logger.debug("CoreStartupTools: Main().GetFSTabInfo(): Found EFI Partition "+Temp+"...")
                    EFIPartition = Temp

                else:
                    logger.error("CoreStartupTools: Main().GetFSTabInfo(): Couldn't determine device name! Ignoring this device...")
                    EFIPartition = "Unknown"

            #Try to find this OS's /boot partition (if there is one).
            if Line.split()[1] == "/boot":
                logger.debug("CoreStartupTools: Main().GetFSTabInfo(): Finding partition that automounts at /boot...")
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
                    logger.debug("CoreStartupTools: Main().GetFSTabInfo(): Found Boot Partition "+Temp+"...")
                    BootPartition = Temp

                else:
                    logger.error("CoreStartupTools: Main().GetFSTabInfo(): Couldn't determine device name! Ignoring this device...")
                    BootPartition = "Unknown"

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

    def AskForOSName(self, Partition, OSArch):
        """Ask the user if an OS exists on the given partition.""" #*** There might be a better way of doing this ***
        logger.info("CoreStartupTools: Main().AskForOSName(): Asking the user for the name of the OS in "+Partition+"...")

        if Partition == SystemInfo["RootFS"]:
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

    def DetermineGRUBBIOSVersion(self, SystemInfo):
        """Try to determine which version of GRUB BIOS is installed""" #*** DEPRECATED ***
        logger.info("CoreStartupTools: Main().DetermineGRUBVersion(): Determining GRUB version...")
        #Check if the system is using grub-legacy or grub2.
        if SystemInfo["IsLiveDisk"] == False:
            #Ask the user if this OS installed the bootloader.
            Result = DialogTools.ShowYesNoDlg(Message="Was the bootloader installed by the current OS ("+SystemInfo["CurrentOS"]["Name"]+")? If this OS is the most recently installed one, it probably installed the bootloader. If you're not sure, click No.")
        
            if Result:
                #Run a command to print grub's version.
                Output = CoreTools.StartProcess("grub-install --version", ReturnOutput=True)[1]

                GRUBVersion = Output.split()[-1].replace(")", "")

                #Try to grab the first number in the list. If it fails, we've almost certainly got GRUB2.
                try:
                    float(GRUBVersion)

                except ValueError:
                    logger.info("CoreStartupTools: Main().DetermineGRUBVersion(): Found GRUB2 in MBR (Shown as GRUB2 in GUI). Continuing...")
                    return "GRUB2"

                else:
                    #If a number was found, check if it's lower than or equal to 1.97 (aka it's grub legacy)
                    if float(GRUBVersion) <= 1.97:
                        return "GRUB-LEGACY"
                        logger.warning("CoreStartupTools: Main().DetermineGRUBVersion(): Found GRUB-LEGACY in MBR! Some options will be disabled, as grub legacy isn't fully supported because it is obsolete. Continuing...")

                    else:
                        logger.info("CoreStartupTools: Main().DetermineGRUBVersion(): Found GRUB2 in MBR (Shown as GRUB2 in GUI). Continuing...")
                        return "GRUB2"
        
        #Ask the user (this'll be run if user said no to YesNo dlg above too -- this isn't in an else staement).
        logger.info("CoreStartupTools: Main().DetermineGRUBVersion(): Only listing GRUB2 and GRUB-LEGACY, as WxFixBoot couldn't tell if bootloader was grub2 or legacy.")
        Result = DialogTools.ShowChoiceDlg(Message="WxFixBoot was unable to automatically determine if your bootloader was GRUB-LEGACY or GRUB2, so please specify which one it is here.", Title="WxFixBoot - Select Bootloader", Choices=["GRUB-LEGACY or I don't know", "GRUB2"])

        if Result != "GRUB-LEGACY or I don't know":
            logger.debug("CoreStartupTools: Main().DetermineGRUBVersion(): User reported bootloader is: "+Result+". Continuing...")
            return Result

        else:
            logger.debug("CoreStartupTools: Main().DetermineGRUBVersion(): User reported bootloader is: GRUB-LEGACY. Continuing...")
            return "GRUB-LEGACY"

    def CheckForUEFIPartition(self, SystemInfo): #*** DEPRECATED ***
        """Find the UEFI system partition and return it"""
        logger.info("CoreStartupTools: Main().CheckForUEFIPartition(): Finding UEFI partition...")
        AskForUEFIPartition = True

        #Get a list of partitions of type vfat with boot flags, if any.
        FatPartitions = []
        Keys = DiskInfo.keys()
        Keys.sort()

        for Disk in Keys:
            if DiskInfo[Disk]["Type"] == "Partition":
                if DiskInfo[Disk]["FileSystem"] == "vfat" and ("boot" in DiskInfo[Disk]["Flags"] or "bootable" in DiskInfo[Disk]["Flags"]):
                    FatPartitions.append(Disk)

        #If this leaves just one partition, then that's out EFI partition.
        if len(FatPartitions) == 1:
            logger.info("CoreStartupTools: Main().CheckForUEFIPartition(): Found UEFI Partition at: "+FatPartitions[0])
            return FatPartitions[0]

        #Otherwise check if it's mounted at /boot/efi if we're not on a live disk.
        if SystemInfo["IsLiveDisk"] == False:
             pass

        if SystemInfo["IsLiveDisk"] or AskForUEFIPartition:
            if FatPartitions != []:
                logger.warning("CoreStartupTools: Main().CheckForUEFIPartition(): Asking user where UEFI Partition is. If you're running from a live disk, ignore this warning.")
                Result = DialogTools.ShowChoiceDlg(Message="Please select your UEFI partition. You can change this later in the bootloader options window if you change your mind, or if it's wrong.", Title="WxFixBoot - Select UEFI Partition", Choices=["I don't have one"]+FatPartitions)

                if Result == "I don't have one":
                    logger.warning("CoreStartupTools: Main().CheckForUEFIPartition(): User said no UEFI Partition exists. Continuing...")
                    return None

                else:
                    logger.info("CoreStartupTools: Main().CheckForUEFIPartition(): User reported UEFI partition at: "+Result+". Continuing...")
                    return Result

            else:
                logger.warning("CoreStartupTools: Main().CheckForUEFIPartition(): No vfat partitions found. No UEFI partition exists. Continuing...")
                return None

#End main Class.
