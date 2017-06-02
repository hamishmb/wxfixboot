#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Core Startup Tools in the StartupTools Package for WxFixBoot Version 2.0.1
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

#Do future imports to prepare to support python 3. Use unicode strings rather than ASCII strings, as they fix potential problems.
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

#Begin Main Class.
class Main():
    def MakeBootloaderInfoEntryForOSX(self, OS):
        """Makes an entry in BootloaderInfo for Mac OS X"""
        BootloaderInfo[OS] = {}
        BootloaderInfo[OS]["OSName"] = OS
        BootloaderInfo[OS]["Bootloader"] = "BootX/BootROM/boot.efi"
        BootloaderInfo[OS]["AvailableBootloaders"] = []
        BootloaderInfo[OS]["MenuEntries"] = {}
        BootloaderInfo[OS]["IsModifyable"] = False
        BootloaderInfo[OS]["Comments"] = "WxFixBoot cannot modify Mac OS X."
        BootloaderInfo[OS]["Timeout"], BootloaderInfo[OS]["GlobalKernelOptions"], BootloaderInfo[OS]["BootDisk"], BootloaderInfo[OS]["BLSpecificDefaultOS"], BootloaderInfo[OS]["DefaultOS"] = (10, "Unknown", OSInfo[OS]["Partition"], OS, OS)

        #Initialise some default no-action settings.
        BootloaderInfo[OS]["Settings"] = {}
        BootloaderInfo[OS]["Settings"]["Reinstall"] = False
        BootloaderInfo[OS]["Settings"]["Update"] = False
        BootloaderInfo[OS]["Settings"]["KeepExistingTimeout"] = False
        BootloaderInfo[OS]["Settings"]["KeepExistingKernelOptions"] = False
        BootloaderInfo[OS]["Settings"]["NewKernelOptions"] = BootloaderInfo[OS]["GlobalKernelOptions"]
        BootloaderInfo[OS]["Settings"]["NewTimeout"] = BootloaderInfo[OS]["Timeout"]
        BootloaderInfo[OS]["Settings"]["DefaultOS"] = BootloaderInfo[OS]["DefaultOS"]
        BootloaderInfo[OS]["Settings"]["InstallNewBootloader"] = False
        BootloaderInfo[OS]["Settings"]["NewBootloader"] = "-- Please Select --"
        BootloaderInfo[OS]["Settings"]["BackupBootloader"] = False
        BootloaderInfo[OS]["Settings"]["BootloaderBackupTarget"] = "-- Please Select --"
        BootloaderInfo[OS]["Settings"]["RestoreBootloader"] = False
        BootloaderInfo[OS]["Settings"]["BootloaderRestoreSource"] = "-- Please Select --"
        BootloaderInfo[OS]["Settings"]["ChangeThisOS"] = False

        #Initialise GUI state for this OS (True = Enabled, False = Disabled).
        BootloaderInfo[OS]["GUIState"] = {}
        BootloaderInfo[OS]["GUIState"]["ReinstallCheckBoxState"] = True
        BootloaderInfo[OS]["GUIState"]["UpdateCheckBoxState"] = True
        BootloaderInfo[OS]["GUIState"]["KeepExistingTimeoutCheckBoxState"] = False
        BootloaderInfo[OS]["GUIState"]["NewTimeoutSpinnerState"] = False
        BootloaderInfo[OS]["GUIState"]["KeepExistingKernelOptionsCheckBoxState"] = False
        BootloaderInfo[OS]["GUIState"]["NewKernelOptionsTextCtrlState"] = False
        BootloaderInfo[OS]["GUIState"]["DefaultOSChoiceState"] = False
        BootloaderInfo[OS]["GUIState"]["InstallNewBootloaderCheckBoxState"] = True
        BootloaderInfo[OS]["GUIState"]["NewBootloaderChoiceState"] = False
        BootloaderInfo[OS]["GUIState"]["BackupBootloaderCheckBoxState"] = True
        BootloaderInfo[OS]["GUIState"]["BackupBootloaderChoiceState"] = False
        BootloaderInfo[OS]["GUIState"]["RestoreBootloaderCheckBoxState"] = True
        BootloaderInfo[OS]["GUIState"]["RestoreBootloaderChoiceState"] = False

    def MakeBootloaderInfoEntryForWindows(self, OS):
        """Makes an entry in BootloaderInfo for Windows"""
        BootloaderInfo[OS] = {}
        BootloaderInfo[OS]["OSName"] = OS

        if OS == "Windows 95/98/ME":
            BootloaderInfo[OS]["Bootloader"] = "AUTOEXEC.BAT"

        elif OS == "Windows XP":
            BootloaderInfo[OS]["Bootloader"] = "NTLoader"

        else:
            BootloaderInfo[OS]["Bootloader"] = "Windows Boot Manager"

        BootloaderInfo[OS]["AvailableBootloaders"] = []
        BootloaderInfo[OS]["MenuEntries"] = {}
        BootloaderInfo[OS]["IsModifyable"] = False
        BootloaderInfo[OS]["Comments"] = "WxFixBoot cannot modify Windows."
        BootloaderInfo[OS]["Timeout"], BootloaderInfo[OS]["GlobalKernelOptions"], BootloaderInfo[OS]["BootDisk"], BootloaderInfo[OS]["BLSpecificDefaultOS"], BootloaderInfo[OS]["DefaultOS"] = (10, "Unknown", "Unknown", OS, OS)

        #Initialise some default no-action settings.
        BootloaderInfo[OS]["Settings"] = {}
        BootloaderInfo[OS]["Settings"]["Reinstall"] = False
        BootloaderInfo[OS]["Settings"]["Update"] = False
        BootloaderInfo[OS]["Settings"]["KeepExistingTimeout"] = False
        BootloaderInfo[OS]["Settings"]["KeepExistingKernelOptions"] = False
        BootloaderInfo[OS]["Settings"]["NewKernelOptions"] = BootloaderInfo[OS]["GlobalKernelOptions"]
        BootloaderInfo[OS]["Settings"]["NewTimeout"] = BootloaderInfo[OS]["Timeout"]
        BootloaderInfo[OS]["Settings"]["DefaultOS"] = BootloaderInfo[OS]["DefaultOS"]
        BootloaderInfo[OS]["Settings"]["InstallNewBootloader"] = False
        BootloaderInfo[OS]["Settings"]["NewBootloader"] = "-- Please Select --"
        BootloaderInfo[OS]["Settings"]["BackupBootloader"] = False
        BootloaderInfo[OS]["Settings"]["BootloaderBackupTarget"] = "-- Please Select --"
        BootloaderInfo[OS]["Settings"]["RestoreBootloader"] = False
        BootloaderInfo[OS]["Settings"]["BootloaderRestoreSource"] = "-- Please Select --"
        BootloaderInfo[OS]["Settings"]["ChangeThisOS"] = False

        #Initialise GUI state for this OS (True = Enabled, False = Disabled).
        BootloaderInfo[OS]["GUIState"] = {}
        BootloaderInfo[OS]["GUIState"]["ReinstallCheckBoxState"] = True
        BootloaderInfo[OS]["GUIState"]["UpdateCheckBoxState"] = True
        BootloaderInfo[OS]["GUIState"]["KeepExistingTimeoutCheckBoxState"] = False
        BootloaderInfo[OS]["GUIState"]["NewTimeoutSpinnerState"] = False
        BootloaderInfo[OS]["GUIState"]["KeepExistingKernelOptionsCheckBoxState"] = False
        BootloaderInfo[OS]["GUIState"]["NewKernelOptionsTextCtrlState"] = False
        BootloaderInfo[OS]["GUIState"]["DefaultOSChoiceState"] = False
        BootloaderInfo[OS]["GUIState"]["InstallNewBootloaderCheckBoxState"] = True
        BootloaderInfo[OS]["GUIState"]["NewBootloaderChoiceState"] = False
        BootloaderInfo[OS]["GUIState"]["BackupBootloaderCheckBoxState"] = True
        BootloaderInfo[OS]["GUIState"]["BackupBootloaderChoiceState"] = False
        BootloaderInfo[OS]["GUIState"]["RestoreBootloaderCheckBoxState"] = True
        BootloaderInfo[OS]["GUIState"]["RestoreBootloaderChoiceState"] = False

    def HasWindows9X(self, MountPoint):
        """Try to find a Windows 9X installation. Return True if found, False if not."""
        return (os.path.isdir(MountPoint+"/WINDOWS") and os.path.exists(MountPoint+"/AUTOEXEC.BAT") and os.path.exists(MountPoint+"/COMMAND.COM") and os.path.isdir(MountPoint+"/My Documents"))

    def HasWindowsXP(self, MountPoint):
        """Try to find a Windows XP installation. Return True if found, False if not."""
        return (os.path.isfile(MountPoint+"/boot.ini") and os.path.isfile(MountPoint+"/ntldr") and os.path.isfile(MountPoint+"/NTDETECT.COM") and os.path.isdir(MountPoint+"/Documents and Settings"))

    def HasWindowsVista(self, MountPoint):
        """Try to find a Windows Vista installation. Return True if found, False if not."""
        return (os.path.isfile(MountPoint+"/bootmgr") and os.path.isdir(MountPoint+"/Users") and os.path.isdir(MountPoint+"/Boot"))

    def HasWindows7(self, MountPoint):
        """Try to find a Windows 7 installation. Return True if found, False if not."""
        return ((not os.path.isfile(MountPoint+"/bootmgr")) and os.path.isdir(MountPoint+"/Recovery") and os.path.isdir(MountPoint+"/Windows/BitLockerDiscoveryVolumeContents"))

    def HasWindows8(self, MountPoint):
        """Try to find a Windows 8/8.1 installation. Return True if found, False if not."""
        return (os.path.isfile(MountPoint+"/BOOTNXT") and os.path.isdir(MountPoint+"/Windows/DesktopTileResources"))

    def HasWindows10(self, MountPoint):
        """Try to find a Windows 10 installation. Return True if found, False if not."""
        return (os.path.isdir(MountPoint+"/Windows/HoloShell") and os.path.isdir(MountPoint+"/Apps"))

    def GetDefaultOSsPartition(self, OS):
        """Get the partition for the given OS's default OS to boot"""
        DefaultBootDevice = "Unknown"

        for Menu in BootloaderInfo[OS]["MenuEntries"]:
            for Entry in BootloaderInfo[OS]["MenuEntries"][Menu]:
                if Entry == BootloaderInfo[OS]["BLSpecificDefaultOS"]:
                    DefaultBootDevice = BootloaderInfo[OS]["MenuEntries"][Menu][Entry]["Partition"]
                    logger.info("CoreStartupTools: Main().GetDefaultOSsPartition(): Found Default OS's partition...")
                    break

        if DefaultBootDevice != "Unknown":
            BootloaderInfo[OS]["DefaultBootDevice"] = DefaultBootDevice

            #Try to get the UUID too.
            if BootloaderInfo[OS]["DefaultBootDevice"] in DiskInfo:
                BootloaderInfo[OS]["DefaultBootDeviceUUID"] = DiskInfo[BootloaderInfo[OS]["DefaultBootDevice"]]["UUID"]

            else:
                BootloaderInfo[OS]["DefaultBootDeviceUUID"] = "Unknown" #Try harder? ***

    def MatchPartitionToOS(self, OS):
        """Matches the default boot device (in a menu entry) to an OS in OSInfo"""
        for OSName in OSInfo:
            if OSName not in BootloaderInfo:
                continue

            if "DefaultBootDeviceUUID" in BootloaderInfo[OS]:
                Disk = BootloaderInfo[OS]["DefaultBootDeviceUUID"]

            else:
                Disk = BootloaderInfo[OS]["DefaultBootDevice"]

            print(BootloaderInfo[OS]["DefaultBootDevice"], OSInfo[OSName]["Partition"], OSName)

            if OSInfo[OSName]["Partition"] != "Unknown" and Disk in (OSInfo[OSName]["Partition"], DiskInfo[OSInfo[OSName]["Partition"]]["UUID"]):
                #Set it.
                BootloaderInfo[OS]["DefaultBootDeviceMatchedWith"] = "Partition"
                BootloaderInfo[OS]["DefaultOS"] = OSName
                logger.info("MainStartupTools: Main().GetBootloaders(): Successfully matched with the partition. The Default OS is "+OSName+"...")
                break

            elif OSInfo[OSName]["BootPartition"] != "Unknown" and  Disk in (OSInfo[OSName]["BootPartition"], DiskInfo[OSInfo[OSName]["BootPartition"]]["UUID"]):
                #Set it.
                BootloaderInfo[OS]["DefaultBootDeviceMatchedWith"] = "BootPartition"
                BootloaderInfo[OS]["DefaultOS"] = OSName
                logger.info("MainStartupTools: Main().GetBootloaders(): Successfully matched with the boot partition. The Default OS is "+OSName+"...")
                break

            elif OSInfo[OSName]["EFIPartition"] != "Unknown" and Disk in (OSInfo[OSName]["EFIPartition"], DiskInfo[OSInfo[OSName]["EFIPartition"]]["UUID"]):
                #Set it.
                BootloaderInfo[OS]["DefaultBootDeviceMatchedWith"] = "EFIPartition"
                BootloaderInfo[OS]["DefaultOS"] = OSName
                logger.info("MainStartupTools: Main().GetBootloaders(): Successfully matched with the EFI partition. The Default OS is "+OSName+"...")
                break

    def DeterminePackageManager(self, APTCmd, YUMCmd):
        """Determine and return the package manager using the given command strings."""
        PackageManager = "Unknown"

        for Cmd in (APTCmd, YUMCmd):
            Retval = CoreTools.StartProcess(Cmd, ShowOutput=False)

            if Retval != 0:
                if Cmd == APTCmd:
                    #Couldn't find apt!
                    logger.info("MainStartupTools: Main().DeterminePackageManager(): Didn't find apt. Looking for yum...")
                    continue

                else:
                    logger.info("MainStartupTools: Main().DeterminePackageManager(): Didn't find apt or yum. Returning 'Unknown'...")

            else:
                if Cmd == APTCmd:
                    #Found APT!
                    logger.info("MainStartupTools: Main().DeterminePackageManager(): Found apt...")
                    PackageManager = "apt-get"
                    break

                else:
                    #Found YUM!
                    logger.info("MainStartupTools: Main().DeterminePackageManager(): Found yum...")
                    PackageManager = "yum"
                    break

        return PackageManager

    def LookForBootloadersOnPartition(self, OS, PackageManager, MountPoint, UsingChroot):
        """Look for bootloaders installed in the OS in the given mount point."""
        if UsingChroot:
            logger.debug("CoreStartupTools: Main().LookForBootloadersOnPartition(): Looking for bootloaders in "+MountPoint+"...")

        else:
            logger.debug("CoreStartupTools: Main().LookForBootloadersOnPartition(): Looking for bootloaders in / (Current OS)...")

        Bootloader = None
        AvailableBootloaders = []

        #Okay, let's run a command in the chroot that was set up in self.FindBootloaderRemovalOSs(), depending on which package manager this OS uses, and which bootloader is currently installed.
        if PackageManager == "apt-get":
            Cmd = "dpkg --get-selections"

        else:
            Cmd = "yum -C list installed"

        if UsingChroot:
            Cmd = "chroot "+MountPoint+" "+Cmd

        Output = CoreTools.StartProcess(Cmd, ShowOutput=False, ReturnOutput=True)[1].split("\n")

        #Look for them in a specific order to be as fast a possible and to avoid false positives.
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
                #On Fedora, GRUB2 for BIOS and GRUB2 for UEFI are both installed by default!
                #To figure out which way we're booting (and which is being used), see whether we detected an EFI partition.
                if PackageDict[Package] == "GRUB-UEFI" and OSInfo[OS]["PackageManager"] == "yum" and OSInfo[OS]["EFIPartition"] == "Unknown":
                    #We're booting with GRUB2.
                    continue

                Bootloader = PackageDict[Package]
                logger.info("CoreStartupTools: Main().LookForBootloadersOnPartition(): Found "+Bootloader+"...")
                break

        #Look for any other bootloaders that might be available for installation. Ignore GRUB-LEGACY.
        for Package in BootloaderPackages:
            if PackageManager == "apt-get":
                Cmd = "apt-cache search "+Package

            else:
                Cmd = "yum -C search "+Package

            if UsingChroot: 
                Cmd = "chroot "+MountPoint+" "+Cmd

            Output = CoreTools.StartProcess(Cmd, ShowOutput=False, ReturnOutput=True)[1].split("\n")

            #Only look in the package name.
            for Line in Output:
                try:
                    if PackageManager == "apt-get":
                        CorrectSection = Line.split()[0]

                    else:
                        CorrectSection = Line.split()[0].split(".")[0]

                except IndexError: continue

                if Package == CorrectSection:
                    if PackageDict[Package] not in AvailableBootloaders and PackageDict[Package] != "GRUB-LEGACY":
                        AvailableBootloaders.append(PackageDict[Package])

        #Log info.
        AvailableBootloaders.sort()
        logger.info("CoreStartupTools: Main().LookForBootloadersOnPartition(): Found available bootloaders: "+', '.join(AvailableBootloaders))

        #Return info.
        return Bootloader, AvailableBootloaders

    def GetFSTabInfo(self, MountPoint, OSName):
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

    def DetermineOSArchitecture(self, MountPoint):
        """Look for OS architecture on given partition."""
        if MountPoint != "":
            logger.info("CoreStartupTools: Main().DetermineOSArchitecture(): Trying to find OS arch for OS at "+MountPoint+"...")

        else:
            logger.info("CoreStartupTools: Main().DetermineOSArchitecture(): Trying to find OS arch for Current OS...")

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

    def GetOSNameWithLSB(self, Partition, MountPoint, IsCurrentOS):
        """Attempt to get an OS's name using lsb_release -sd as a fallback."""
        logger.info("CoreStartupTools: Main().GetOSNameWithLSB(): Attempting to get OS name for OS on "+Partition+"...")

        if IsCurrentOS:
            logger.info("CoreStartupTools: Main().GetOSNameWithLSB(): OS is the currently running OS...")
            Cmd = "lsb_release -sd"

        else:
            logger.info("CoreStartupTools: Main().GetOSNameWithLSB(): OS isn't the currently running OS...")
            Cmd = "chroot "+MountPoint+" lsb_release -sd"

        Retval, Output = CoreTools.StartProcess(Cmd, ShowOutput=False, ReturnOutput=True)

        if Retval != 0 or Output == "":
            logger.error("CoreStartupTools: Main().GetOSNameWithLSB(): Couldn't get OS name! Returning 'Unknown'...")
            return "Unknown"

        else:
            logger.info("CoreStartupTools: Main().GetOSNameWithLSB(): Success. OS name is "+Output+". Returning it...")
            return Output

    def AskForOSName(self, Partition, OSArch, IsCurrentOS):
        """Ask the user if an OS exists on the given partition."""
        logger.info("CoreStartupTools: Main().AskForOSName(): Asking the user for the name of the OS in "+Partition+"...")

        if IsCurrentOS:
            DialogTools.ShowMsgDlg(Kind="warning", Message="WxFixBoot couldn't find the name of the current OS. Please name it so that WxFixBoot can function correctly.")
            Result = True

        else:
            Result = DialogTools.ShowYesNoDlg(Message="There is a Linux operating system on partition: "+Partition+" but WxFixBoot couldn't find its name. It isn't the currently running OS. Do you want to name it and include it in the list? Only click yes if you believe it is a recent OS. Click Yes if you want to name it, otherwise click No", Buttons=("Name it", "Don't name it."))

        if Result == False:
            logger.info("CoreStartupTools: Main().AskForOSName(): User didn't want to name the OS in "+Partition+"! Ignoring it...")
            #User reported no OS in this partition, ignore it.
            return None

        else:
            logger.debug("CoreStartupTools: Main().AskForOSName(): User reported recent Linux OS in "+Partition+" (or OS is current OS). Asking name of OS...")
            #User reported that an OS is here.
            Result = DialogTools.ShowTextEntryDlg(Message="Please enter the name of the operating system that is on "+Partition+".\nThe name you specify will be used later in the program", Title="WxFixBoot - Enter OS Name")

            return Result

#End main Class.
