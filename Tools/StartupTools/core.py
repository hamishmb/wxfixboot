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

#Begin Main Class. *** Check and test all of this and optimise/reorganise it again later ***
class Main():
    def GetDevPartScheme(self, Device):
        """Get the partition type on the given Device, and return it.""" #*** Remove soon ***
        return CoreTools().StartProcess("parted -s "+Device+" print", ReturnOutput=True)[1].split("\n")[3].split()[-1]

    def DetermineOSArchitecture(self, Partition, Chroot): #*** Tidy this up ***
        """Look for OS architecture on given partition, looking for 64-bit first, then 32-bit."""
        logger.info("CoreStartupTools: Main().DetermineOSArchitecture(): Trying to find OS arch for OS on "+Partition+"...")
        #Look for the 64-bit arch first. 
        WantedArch = "64-bit"

        #Use a loop to avoid duplicating code.
        while True:
            cmd = "file -L /usr/bin/ld"

            #If we're using chroot, add that to the command.
            if Chroot == True:
                cmd = "chroot /mnt"+Partition+" "+cmd

            #Now let's check if the OS uses this architecture.
            if WantedArch in CoreTools().StartProcess(cmd, ReturnOutput=True)[1]:
                if WantedArch == "64-bit":
                    logger.info("CoreStartupTools: Main().DetermineOSArchitecture(): OS on "+Partition+" is 64-bit...")
                    OSArch = "x86_64"

                else:
                    logger.info("CoreStartupTools: Main().DetermineOSArchitecture(): OS on "+Partition+" is 64-bit...")
                    OSArch = "i686"

                break

            elif WantedArch == "64-bit":
                #Now look for 32-bit and restart the loop.
                logger.info("CoreStartupTools: Main().DetermineOSArchitecture(): OS on "+Partition+" isn't 64-bit. Looking for a 32-bit OS...")
                WantedArch = "32-bit"

            else:
                #We couldn't find it as either 32-bit or 64-bit!
                logger.info("CoreStartupTools: Main().DetermineOSArchitecture(): Couldn't find architecture for OS on "+Partition+"! Returning None...")
                OSArch = None
                break

        #Return the arch (or None, if we didn't find it).
        return OSArch

    def AskForOSName(self, Partition, OSArch, AutoRootFS):
        """Ask the user if an OS exists on the given partition.""" #*** There might be a better way of doing this *** *** Will need modification at time of switch to dictionaries as it uses AutoRootFS ***
        logger.info("CoreStartupTools: Main().AskForOSName(): Asking the user for the name of the OS in "+Partition+"...")

        if Partition == AutoRootFS:
            DialogTools().ShowMsgDlg(Kind="warning", Message="WxFixBoot couldn't find the name of the current OS. Please name it so that WxFixBoot can function correctly.")
            Result = True

        else:
            Result = DialogTools().ShowYesNoDlg(Message="There is a Linux operating system on partition: "+Partition+" but WxFixBoot couldn't find its name. It isn't the currently running OS. Do you want to name it and include it in the list?. Only click yes if you believe it is a recent OS.")

        if Result == False:
            logger.info("CoreStartupTools: Main().AskForOSName(): User didn't want to name the OS in "+Partition+"! Ignoring it...")
            #User reported no OS in this partition, ignore it.
            return None

        else:
            logger.debug("CoreStartupTools: Main().AskForOSName(): User reported recent Linux OS in "+Partition+". Asking name of OS...")
            #User reported that an OS is here.
            Result = DialogTools().ShowTextEntryDlg(Message="Please enter the name of the operating system that is on "+Partition+".\nThe name you specify will be used later in the program", Title="WxFixBoot - Enter OS Name")

            return Result

    def MountUEFIPartition(self, UEFISystemPartition):
        """Mount the UEFI partition if needed"""
        #Get the UEFI partition's current mountpoint, if it is mounted.
        logger.debug("CoreStartupTools: Main().MountUEFIPartition(): Preparing to mount UEFI system Partition if needed...")

        #It isn't mounted, mount it, and also create the directory if needed.
        logger.debug("CoreStartupTools: Main().MountUEFIPartition(): Mounting UEFI Partition at /boot/efi...")
        UEFISYSPMountPoint = "/boot/efi"

        #Mount it using the global mount function.
        Retval = CoreTools().MountPartition(Partition=UEFISystemPartition, MountPoint=UEFISYSPMountPoint)

        if Retval == 0:
            logger.info("CoreStartupTools: Main().MountUEFIPartition(): Successfully Mounted UEFI Partition...")

        else:
            #This very rarely happens! *** Is continuing anyway a good idea? ***
            logger.error("CoreStartupTools: Main().MountUEFIPartition(): Failed to mount UEFI Partition! Continuing anyway, with reported mountpoint as /boot/efi...")
        
        return UEFISYSPMountPoint

    def CheckForGRUBBIOS(self, MBR):
        """Check for the GRUB (v2 and legacy) BIOS bootloader"""
        #*** Try to find a way of distinguishing between them here, rather than later *** *** Test again ***
        if str("GRUB") in str(MBR): #*** Avoid UnicodeDecodeError ***
            #Bootloader is GRUB MBR
            return True

        else:
            return False

    def CheckForLILO(self):
        """Check for LILO in MBR""" #*** Test again ***
        if str("LILO") in str(MBR): #*** Avoid UnicodeDecodeError ***
            #Bootloader is LILO in MBR
            return True

        else:
            return False

    def DetermineGRUBBIOSVersion(self, LiveDisk):
        """Try to determine which version of GRUB BIOS is installed""" #*** See if we can find a better way of doing this *** *** This needs testing in a VM at some point ***
        logger.info("CoreStartupTools: Main().DetermineGRUBVersion(): Determining GRUB version...")
        #*** This is a mess ***
        #Check if the system is using grub-legacy or grub2. *** There are better ways of doing this, like using a variable or dictionary instead of having to find the current os's name over and over ***
        if LiveDisk == False:
            #Find the name of the current OS.
            for OS in OSList:
                if OS.split()[-5] == "OS)":
                    currentos = ' '.join(OS.split()[0:-6])

                else:
                    currentos = "Unknown"

            #Ask the user if this OS installed the bootloader.
            Result = DialogTools().ShowYesNoDlg(Message="Was the bootloader installed by the current OS ("+currentos+")? If this OS is the most recently installed one, it probably installed the bootloader. If you're not sure, click No.")
        
            if Result:
                #Run a command to print grub's version. *** There has got to be a better way of processing this ***
                Stdout = CoreTools().StartProcess("grub-install --version", ReturnOutput=True)[1].replace("(", "").replace(")", "")

                #Try to grab the first number in the list. If it fails, we've almost certainly got GRUB2.
                Temp = "empty"
                for version in Stdout.split():
                    try:
                        float(version)

                    except ValueError: pass

                    else:
                        Temp = version
                        break

                #Check if there is a version number found. If not, it's grub2.
                if Temp == "empty":
                    logger.info("CoreStartupTools: Main().DetermineGRUBVersion(): Found GRUB2 in MBR (Shown as GRUB2 in GUI). Continuing...")
                    return "GRUB2"

                else:
                    #If a number was found, check if it's lower than or equal to 1.97 (aka it's grub legacy)
                    if float(Temp) <= 1.97:
                        return "GRUB-LEGACY"
                        logger.warning("CoreStartupTools: Main().DetermineGRUBVersion(): Found GRUB-LEGACY in MBR! Some options will be disabled, as grub legacy isn't fully supported because it is obsolete. Continuing...")

                    else:
                        logger.info("CoreStartupTools: Main().DetermineGRUBVersion(): Found GRUB2 in MBR (Shown as GRUB2 in GUI). Continuing...")
                        return "GRUB2"
        
        #Ask the user (this'll be run if user said no to YesNo dlg above too -- this isn't in an else staement).
        logger.info("CoreStartupTools: Main().DetermineGRUBVersion(): Only listing GRUB2 and GRUB-LEGACY, as WxFixBoot couldn't tell if bootloader was grub2 or legacy.")
        Result = DialogTools().ShowChoiceDlg(Message="WxFixBoot was unable to automatically determine if your bootloader was GRUB-LEGACY or GRUB2, so please specify which one it is here.", Title="WxFixBoot - Select Bootloader", Choices=["GRUB-LEGACY or I don't know", "GRUB2"])

        if Result != "GRUB-LEGACY or I don't know":
            logger.debug("CoreStartupTools: Main().DetermineGRUBVersion(): User reported bootloader is: "+Result+". Continuing...")
            return Result

        else:
            logger.debug("CoreStartupTools: Main().DetermineGRUBVersion(): User reported bootloader is: GRUB-LEGACY. Continuing...")
            return "GRUB-LEGACY"

    def ManualBootloaderSelect(self, UEFISystemPartition, FirmwareType): #*** This will need modification when switching to dictionaries ***
        """Presents the user with a wx.ChoiceBox to select the bootloader manually"""
        logger.debug("CoreStartupTools: Main().ManualBootloaderSelect(): Manually selecting bootloader...")

        #Offer different selection based on the current state of the system.
        if UEFISystemPartition == "None" and FirmwareType == "UEFI":
            logger.warning("CoreStartupTools: Main().ManualBootloaderSelect(): Only listing BIOS bootloaders, as there is no UEFI partition.")
            Result = DialogTools().ShowChoiceDlg(Message="WxFixBoot was unable to automatically determine your bootloader, so please manually select it here.", Title="WxFixBoot - Select Bootloader", Choices=["GRUB-LEGACY/I don't know", "GRUB2", "LILO"])

        elif UEFISystemPartition != "None" and FirmwareType == "UEFI":
            Result = DialogTools().ShowChoiceDlg(Message="WxFixBoot was unable to automatically determine your bootloader, so please manually select it here.", Title="WxFixBoot - Select Bootloader", Choices=["GRUB-LEGACY/I don't know", "GRUB2", "GRUB-UEFI", "LILO", "ELILO"])

        else:
            logger.info("CoreStartupTools: Main().ManualBootloaderSelect(): Only listing BIOS bootloaders, as this is a BIOS system.")
            Result = DialogTools().ShowChoiceDlg(Message="WxFixBoot was unable to automatically determine your bootloader, so please manually select it here.", Title="WxFixBoot - Select Bootloader", Choices=["GRUB-LEGACY/I don't know", "GRUB2", "LILO"])

        if Result != "GRUB-LEGACY/I don't know":
            logger.debug("CoreStartupTools: Main().ManualBootloaderSelect(): User reported bootloader is: "+Result+". Continuing...")
            return Result

        else:
            logger.debug("CoreStartupTools: Main().ManualBootloaderSelect(): User reported bootloader is: GRUB-LEGACY. Continuing...")
            return "GRUB-LEGACY"

    def CheckForUEFIPartition(self, LiveDisk): #*** There is a UEFI system partition flag to check for instead, which would speed this up *** *** This will need a LOT of modification when I switch to dictionaries *** *** May be largely unneeded when using getdevinfo package *** 
        """Find the UEFI system partition and return it"""
        logger.info("CoreStartupTools: Main().CheckForUEFIPartition(): Finding UEFI partition...")
        FatPartitions = []

        #Get a list of partitions of type vfat, if any. *** Tidy this up a bit maybe ***
        TempList = CoreTools().StartProcess("lsblk -r -o NAME,FSTYPE", ReturnOutput=True)[1].split("\n")
        OutputList = []

        for Line in TempList:
            if "vfat" in Line:
                OutputList.append(Line.split()[0])
                OutputList.append(Line.split()[1])

        #Create another list of only the disks. Ignore anything else.
        for element in OutputList:
            if element[0:2] in ('sd', 'hd'):
                FatPartitions.append("/dev/"+element)

        if LiveDisk == False:
            TempList = CoreTools().StartProcess("lsblk -r -o NAME,FSTYPE,MOUNTPOINT,LABEL", ReturnOutput=True)[1].split("\n")
            UEFISystemPartition = None

            for Line in TempList:
                if "/boot/efi" in Line:
                    UEFISystemPartition = "/dev/"+Line.split()[0]

            if UEFISystemPartition == None:
                logger.warning("CoreStartupTools: Main().CheckForUEFIPartition(): Failed to find the UEFI Partition. Trying another way...")
                #Try a second way to get the UEFI system partition.
                for Line in TempList:
                    if "ESP" in Line:
                        UEFISystemPartition = "/dev/"+Line.split()[0]

                if UEFISystemPartition == None:
                    #Ask the user where it is.
                    logger.warning("CoreStartupTools: Main().CheckForUEFIPartition(): Couldn't autodetermine UEFI Partition. Asking the user instead...")
                    AskForUEFIPartition = True

                else:
                    logger.info("CoreStartupTools: Main().CheckForUEFIPartition(): Found UEFI Partition at: "+UEFISystemPartition)
                    return UEFISystemPartition, FatPartitions

            else:
                logger.info("CoreStartupTools: Main().CheckForUEFIPartition(): Found UEFI Partition at: "+UEFISystemPartition)
                return UEFISystemPartition, FatPartitions

        if LiveDisk == True or AskForUEFIPartition == True:
            logger.warning("CoreStartupTools: Main().CheckForUEFIPartition(): Asking user where UEFI Partition is. If you're running from a live disk, ignore this warning.")

            if FatPartitions != []:
                Result = DialogTools().ShowChoiceDlg(Message="Please select your UEFI partition. You can change this later in the bootloader options window if you change your mind, or if it's wrong.", Title="WxFixBoot - Select UEFI Partition", Choices=["I don't have one"]+FatPartitions)

                if Result == "I don't have one":
                    logger.warning("CoreStartupTools: Main().CheckForUEFIPartition(): User said no UEFI Partition exists. Continuing...")
                    return None, FatPartitions

                else:
                    logger.info("CoreStartupTools: Main().CheckForUEFIPartition(): User reported UEFI partition at: "+Result+". Continuing...")
                    return Result, FatPartitions
            else:
                return None, FatPartitions

    def CheckForGRUBUEFI(self, UEFISYSPMountPoint):
        """Check for GRUB-UEFI"""
        #Look for GRUB's UEFI file.
        Temp = CoreTools().Find(r"(.*)grub(.*).efi", UEFISYSPMountPoint)

        if Temp != []:
            #Bootloader is GRUB-UEFI.
            GrubEFI = True
            HelpfulUEFIPartition = True

        else:
            GrubEFI = False
            HelpfulUEFIPartition = False

        return GrubEFI, HelpfulUEFIPartition

    def CheckForELILO(self, UEFISYSPMountPoint):
        """Check for ELILO"""
        #Look for LILO's UEFI file.
        Temp = CoreTools().Find(r"(.*)elilo(.*).efi", UEFISYSPMountPoint)

        if Temp != []:
            #Bootloader is ELILO.
            ELILO = True
            HelpfulUEFIPartition = True

        else:
            ELILO = False
            HelpfulUEFIPartition = False

        return ELILO, HelpfulUEFIPartition

#End main Class.
