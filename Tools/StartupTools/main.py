#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Main Startup Tools in the StartupTools Package for WxFixBoot Version 2.0~rc1
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

#Begin Main Class.
class Main():
    def CheckDepends(self):
        """Check dependencies, and show an error message and kill the app if the dependencies are not met."""
        logger.info("MainStartupTools(): Main().CheckDepends(): Checking dependencies...")
        #Create a temporary list to allow WxFixBoot to notify the user of particular unmet dependencies.
        CmdList = ("arch", "lshw", "mount", "dmidecode", "chroot", "dd", "gdisk", "blkid", "strings", "lvdisplay")

        #Create a list to contain names of failed commands.
        FailedList = []

        for Command in CmdList:
            #Run the command with its argument and log the output (if in debug mode)
            Retval, Output = CoreTools.StartProcess("which "+Command, ReturnOutput=True)

            if Retval != 0:
                logger.error("MainStartupTools: Main().CheckDepends(): Dependency problems! Command: "+Command+" failed to execute or wasn't found.")
                logger.error("MainStartupTools: Main().CheckDepends(): The error was: "+Output)
                FailedList.append(Command)

        #Check if any commands failed.
        if FailedList != []:
            #Missing dependencies!
            logger.critical("MainStartupTools: Main().CheckDepends(): Dependencies missing! WxFixBoot will exit. The missing dependencies are: "+', '.join(FailedList)+". Exiting.")
            CoreTools.EmergencyExit("The following dependencies could not be found on your system: "+', '.join(FailedList)+".\n\nPlease install the missing dependencies.")

    def CheckForLiveDisk(self):
        """Try to determine if we're running on a live disk."""
        logger.info("MainStartupTools(): Main().CheckForLiveDisk(): Attempting to check if we're on a live disk...")

        #Detect Parted Magic automatically.
        if "pmagic" in CoreTools.StartProcess("uname -r", ReturnOutput=True)[1]:
            logger.info("MainStartupTools(): Main().CheckForLiveDisk(): Running on Parted Magic...")
            SystemInfo["IsLiveDisk"] = True
            SystemInfo["OnPartedMagic"] = True

        #Try to detect ubuntu-based livecds.
        elif CoreTools.IsMounted("/cow", "/") and os.path.isfile("/cdrom/casper/filesystem.squashfs"):
            logger.info("MainStartupTools(): Main().CheckForLiveDisk(): Running on Ubuntu-based live disk...")
            SystemInfo["IsLiveDisk"] = True
            SystemInfo["OnPartedMagic"] = False

        #Try to detect fedora-based livecds.
        elif CoreTools.IsMounted("/dev/mapper/live-rw", "/") and os.path.isfile("/run/initramfs/live/LiveOS/squashfs.img"):
            logger.info("MainStartupTools(): Main().CheckForLiveDisk(): Running on Fedora-based live disk...")
            SystemInfo["IsLiveDisk"] = True
            SystemInfo["OnPartedMagic"] = False

        #Try to detect if we're not running on a live disk (on a HDD).
        elif "/dev/sd" in CoreTools.GetPartitionMountedAt("/"):
            logger.info("MainStartupTools(): Main().CheckForLiveDisk(): Not running on live disk...")
            SystemInfo["IsLiveDisk"] = False
            SystemInfo["OnPartedMagic"] = False

        #Try to detect if we're not running on a live disk (on LVM).
        elif "/dev/mapper/" in CoreTools.GetPartitionMountedAt("/"):
            logger.info("MainStartupTools(): Main().CheckForLiveDisk(): Not running on live disk...")
            SystemInfo["IsLiveDisk"] = False
            SystemInfo["OnPartedMagic"] = False

        #Ask the user if we're running on a live disk.
        else:
            logger.info("MainStartupTools(): Main().CheckForLiveDisk(): Asking the user if we're running on live media...")
            SystemInfo["IsLiveDisk"] = DialogTools.ShowYesNoDlg(Message="Is WxFixBoot being run on live media, such as an Ubuntu Installer Disk?", Title="WxFixBoot - Live Media?")
            SystemInfo["OnPartedMagic"] = False
            logger.info("MainStartupTools(): Main().CheckForLiveDisk(): Result: "+unicode(SystemInfo["IsLiveDisk"]))

        #Get current OS architecture.
        logger.info("MainStartupTools(): Main().CheckForLiveDisk(): Getting architecture of current OS...")
        SystemInfo["CurrentOSArch"] = CoreStartupTools.DetermineOSArchitecture(MountPoint="")

    def UnmountAllFS(self):
        """Unmount any unnecessary filesystems, to prevent data corruption."""
        #Warn about removing devices.
        logger.info("MainStartupTools: Main().UnmountAllFS(): Unmounting all Filesystems...")
        DialogTools.ShowMsgDlg(Kind="info", Message="WxFixBoot is about to gather device information. After this point, you must not remove/add any devices from/to your computer, so do that now if you wish to.")

        #Attempt unmount of all filesystems.
        logger.debug("MainStartupTools: Main().UnmountAllFS(): Running 'unmount -ad'...")
        CoreTools.StartProcess("umount -ad")

        #Make sure that we still have rw access on live disks.
        if SystemInfo["IsLiveDisk"]:
            logger.info("MainStartupTools: Main().UnmountAllFS(): Attempting to remount '/' to make sure it's still rw...")

            if CoreTools.RemountPartition("/") != 0:
                logger.error("MainStartupTools: Main().UnmountAllFS(): Failed to remount / as rw! This probably doesn't matter...")

    def CheckFS(self):
        """Check all unmounted filesystems."""
        logger.info("MainStartupTools: Main().CheckFS(): Checking filesystems if possible. Running 'fsck -ARMp'...")

        if CoreTools.StartProcess("fsck -ARMp") != 0:
            logger.critical("MainStartupTools: Main().CheckFS(): Failed to check filesystems! Doing emergency exit...")
            CoreTools.EmergencyExit("Failed to check filesystems! Please fix your filesystems and then run WxFixBoot again.")

    def MountCoreFS(self):
        """Mount all core filsystems defined in the /etc/fstab of the current operating system."""
        logger.info("MainStartupTools: Main().MountCoreFS(): Mounting core filesystems in /etc/fstab. Calling 'mount -avw'...")

        #Don't worry about this error when running on Parted Magic.
        if CoreTools.StartProcess("mount -avw") != 0 and SystemInfo["OnPartedMagic"] == False:
            logger.critical("MainStartupTools: Main().MountCoreFS(): Failed to re-mount your filesystems after checking them! Doing emergency exit...")
            CoreTools.EmergencyExit("Failed to re-mount your filesystems after checking them!")

    def GetOSs(self):
        """Get the names of all OSs on the HDDs."""
        logger.info("MainStartupTools: Main().GetOSs(): Finding Linux operating systems...")
        RootFS = CoreTools.GetPartitionMountedAt("/")
        OSInfo = {}

        #Get Linux OSs.
        Keys = DiskInfo.keys()
        Keys.sort()

        for Partition in Keys:
            if DiskInfo[Partition]["Type"] == "Device":
                continue

            if DiskInfo[Partition]["FileSystem"] in ("vfat", "ntfs", "exfat"): pass #*** Not fully implemented, will implement for v2.1. Disabled for now ***
                #Look for Windows. *** NTFS can't be mounted twice ***
                #logger.debug("MainStartupTools: Main().GetOSs(): Looking for Windows on "+Partition+"...")

                #Mount the partition and check if anything went wrong.
                #MountPoint = "/tmp/wxfixboot/mountpoints"+Partition

                #if CoreTools.MountPartition(Partition=Partition, MountPoint=MountPoint) != 0:
                    #Ignore the partition.
                #    logger.warning("MainStartupTools: Main().GetOSs(): Couldn't mount "+Partition+"! Skipping this partition...")
                #    continue

                #Windows XP.
                #if os.path.isfile(MountPoint+"/boot.ini") and os.path.isdir(MountPoint+"/Windows"):
                    #Add this information to OSInfo.
                #    logger.debug("MainStartupTools: Main().GetOSs(): Found Windows XP...")
                #    OSName = "Windows XP"
                #    OSInfo[OSName] = {}
                #    OSInfo[OSName]["Name"] = OSName
                #    OSInfo[OSName]["IsCurrentOS"] = False
                #    OSInfo[OSName]["Arch"] = "Unknown"
                #    OSInfo[OSName]["Partition"] = Partition
                #    OSInfo[OSName]["PackageManager"] = "Windows Installer"
                #    OSInfo[OSName]["RawFSTabInfo"], OSInfo[OSName]["EFIPartition"], OSInfo[OSName]["BootPartition"] = ("Unknown", "Unknown", "Unknown")
                    #OSInfo[OSName]["RawFSTabInfo"], OSInfo[OSName]["EFIPartition"], OSInfo[OSName]["BootPartition"] = CoreStartupTools.GetFSTabInfo(MountPoint, OSName) *** TODO ***

                #Windows Vista/7/8/8.1/10.
                #elif os.path.isdir(MountPoint+"/Windows"):
                #    logger.debug("MainStartupTools: Main().GetOSs(): Found Windows Vista/7/8/10...")
                #    OSName = "Windows Vista/7/8/10"
                #    OSInfo[OSName] = {}
                #    OSInfo[OSName]["Name"] = OSName
                #    OSInfo[OSName]["IsCurrentOS"] = False
                #    OSInfo[OSName]["Arch"] = "Unknown"
                #    OSInfo[OSName]["Partition"] = Partition
                #    OSInfo[OSName]["PackageManager"] = "Windows Installer"
                #    OSInfo[OSName]["RawFSTabInfo"], OSInfo[OSName]["EFIPartition"], OSInfo[OSName]["BootPartition"] = ("Unknown", "Unknown", "Unknown")
                    #OSInfo[OSName]["RawFSTabInfo"], OSInfo[OSName]["EFIPartition"], OSInfo[OSName]["BootPartition"] = CoreStartupTools.GetFSTabInfo(MountPoint, OSName) *** TODO ***

                #else:
                #    logger.debug("MainStartupTools: Main().GetOSs(): Didn't find Windows...")

                #Unmount the filesystem.
                #if CoreTools.Unmount(MountPoint) != 0: #*** What shall we do if this doesn't work? Is emergency exit okay, or try again? ***
                #    logger.error("MainStartupTools: Main().GetOSs(): Couldn't unmount "+Partition+"! Doing emergency exit...")
                #    CoreTools.EmergencyExit("Couldn't unmount "+Partition+" after looking for operating systems on it! Please reboot your computer and try again.")

            else:
                #Look for Linux.
                #The python command runs on python 2 and python 3.
                logger.debug("MainStartupTools: Main().GetOSs(): Looking for Linux on "+Partition+"...")

                if Partition == RootFS:
                    Cmd =  "python -c \"from __future__ import print_function; import platform; print(' '.join(platform.linux_distribution()));\""
                    APTCmd = "which apt-get"
                    YUMCmd = "which yum"
                    Chroot = False
                    IsCurrentOS = True
                    MountPoint = ""

                else:
                    MountPoint = "/tmp/wxfixboot/mountpoints"+Partition
                    Cmd = "chroot "+MountPoint+" python -c \"from __future__ import print_function; import platform; print(' '.join(platform.linux_distribution()));\""
                    APTCmd = "chroot "+MountPoint+" which apt-get"
                    YUMCmd = "chroot "+MountPoint+" which yum"
                    Chroot = True
                    IsCurrentOS = False

                    #Mount the partition and check if anything went wrong.
                    if CoreTools.MountPartition(Partition=Partition, MountPoint=MountPoint) != 0:
                        #Ignore the partition.
                        logger.warning("MainStartupTools: Main().GetOSs(): Couldn't mount "+Partition+"! Skipping this partition...")
                        continue

                #Look for Linux on this partition.
                Retval, Temp = CoreTools.StartProcess(Cmd, ReturnOutput=True)
                OSName = Temp.replace('\n', '')

                #Run the function to get the architechure.
                OSArch = CoreStartupTools.DetermineOSArchitecture(MountPoint=MountPoint)

                #If the OS's name wasn't found, but its architecture was, there must be an OS here, so ask the user for its name.
                if Retval != 0 and OSArch != None:
                    OSName = CoreStartupTools.AskForOSName(Partition=Partition, OSArch=OSArch, IsCurrentOS=IsCurrentOS)

                #Look for APT.
                PackageManager = CoreStartupTools.DeterminePackageManager(APTCmd=APTCmd, YUMCmd=YUMCmd) 

                #Also check if CoreStartupTools.AskForOSName was used to determine the name. If the user skipped naming the OS, ignore it and skip the rest of this loop iteration.
                if OSName != None and OSArch != None and PackageManager != "Unknown":
                    #Add this information to OSInfo.
                    OSInfo[OSName] = {}
                    OSInfo[OSName]["Name"] = OSName
                    OSInfo[OSName]["IsCurrentOS"] = IsCurrentOS
                    OSInfo[OSName]["Arch"] = OSArch
                    OSInfo[OSName]["Partition"] = Partition
                    OSInfo[OSName]["PackageManager"] = PackageManager
                    OSInfo[OSName]["RawFSTabInfo"], OSInfo[OSName]["EFIPartition"], OSInfo[OSName]["BootPartition"] = CoreStartupTools.GetFSTabInfo(MountPoint, OSName)

                    if Chroot == False:
                        SystemInfo["CurrentOS"] = OSInfo[OSName].copy()

                if Chroot:
                    #Unmount the filesystem.
                    if CoreTools.Unmount(MountPoint) != 0:
                        logger.error("MainStartupTools: Main().GetOSs(): Couldn't unmount "+Partition+"! Doing emergency exit...")
                        CoreTools.EmergencyExit("Couldn't unmount "+Partition+" after looking for operating systems on it! Please reboot your computer and try again.")

                    #Remove the temporary mountpoint
                    os.rmdir(MountPoint)

        #Check that at least one OS was detected.
        if len(OSInfo) >= 1:
            logger.debug("MainStartupTools: Main().GetOSs(): Done, OSInfo Populated okay. Contents: "+unicode(OSInfo))
            return OSInfo, SystemInfo

        else:
            logger.critical("MainStartupTools: Main().GetOSs(): No Linux installations found! If you do have Linux installations but WxFixBoot hasn't found them, please file a bug or ask a question on WxFixBoot's launchpad page. If you're using Windows or Mac OS X, then sorry as WxFixBoot has no support for these operating systems. You could instead use the tools provided by Microsoft and Apple to fix any issues with your computer. Exiting...")

            #Exit.
            CoreTools.EmergencyExit("You don't appear to have any Linux installations on your hard disks. If you do have Linux installations but WxFixBoot hasn't found them, please file a bug or ask a question on WxFixBoot's launchpad page. If you're using Windows or Mac OS X, then sorry as WxFixBoot has no support for these operating systems. You could instead use the tools provided by Microsoft and Apple to fix any issues with your computer.")

    def GetFirmwareType(self):
        """Get the firmware type"""
        #Check if the firmware type is UEFI.
        #Also, look for UEFI variables.
        #Make sure efivars module is loaded. If it doesn't exist, continue anyway.
        CoreTools.StartProcess("modprobe efivars")

        #Look for the UEFI vars in some common directories.
        if os.path.isdir("/sys/firmware/efi/vars") and CoreTools.StartProcess("ls /sys/firmware/efi/vars", ReturnOutput=True)[1] != "":
            UEFIVariables = True
            logger.info("MainStartupTools: Main().GetFirmwareType(): Found UEFI Variables at /sys/firmware/efi/vars...")

        elif os.path.isdir("/proc/efi/vars") and CoreTools.StartProcess("ls /proc/efi/vars", ReturnOutput=True)[1] != "":
            UEFIVariables = True
            logger.info("MainStartupTools: Main().GetFirmwareType(): Found UEFI Variables at /proc/efi/efivars...")

        else:
            logger.info("MainStartupTools: Main().GetFirmwareType(): UEFI vars not found in /sys/firmware/efi/vars or /sys/firmware/efi/efivars. This is normal if running on a BIOS system. Determining firmware type a different way...")
            UEFIVariables = False

        if UEFIVariables:
            #It's UEFI.
            logger.info("MainStartupTools: Main().GetFirmwareType(): Detected Firmware Type as UEFI.")
            SystemInfo["FirmwareType"] = "UEFI"

        else:
            #Look a second way.
            Output = CoreTools.StartProcess("dmidecode -q -t BIOS", ReturnOutput=True)[1]

            if "UEFI" not in Output:
                #It's BIOS.
                logger.info("MainStartupTools: Main().GetFirmwareType(): Detected Firmware Type as BIOS...")
                SystemInfo["FirmwareType"] = "BIOS"

            else:
                #It's UEFI.
                logger.warning("MainStartupTools: Main().GetFirmwareType(): Detected Firmware Type as UEFI, but couldn't find UEFI variables!")
                SystemInfo["FirmwareType"] = "UEFI"
                DialogTools.ShowMsgDlg(Kind="warning", Message="Your computer uses UEFI firmware, but the UEFI variables couldn't be mounted or weren't found. Please ensure you've booted in UEFI mode rather than legacy mode to enable access to the UEFI variables. You can attempt installing a UEFI bootloader without them, but it might not work, and it isn't recommended.")

    def GetBootloaders(self): #*** Test this thoroughly ***
        """Find all bootloaders (for each OS), and gather some information about them"""
        SystemInfo["ModifyableOSs"] = []

        Keys = OSInfo.keys()
        Keys.sort()

        for OS in Keys:
            #If this isn't the current OS, do some preparation.
            if not OSInfo[OS]["IsCurrentOS"]:
                #Mount the OS's partition.
                MountPoint = "/tmp/wxfixboot/mountpoints"+OSInfo[OS]["Partition"]
                Chroot = True

                if CoreTools.MountPartition(OSInfo[OS]["Partition"], MountPoint) != 0:
                    logger.error("MainStartupTools: Main().GetBootloaders(): Failed to mount "+OS+"'s partition! Skipping bootloader detection for this OS.")
                    continue

                #Set up chroot.
                if CoreTools.SetUpChroot(MountPoint) != 0:
                    logger.error("MainStartupTools: Main().GetBootloaders(): Couldn't set up chroot on "+MountPoint+"! Attempting to remove it in case it's partially set up, and then skipping this OS...")
                    CoreTools.TearDownChroot(MountPoint)
                    continue

            else:
                MountPoint = ""
                Chroot = False

            #Mount a /boot partition if it exists.
            if OSInfo[OS]["BootPartition"] != "Unknown":
                if CoreTools.MountPartition(OSInfo[OS]["BootPartition"], MountPoint+"/boot") != 0:
                    logger.error("MainStartupTools: Main().GetBootloaders(): Failed to mount "+OS+"'s /boot partition! Skipping bootloader detection for this OS.")

                    if not OSInfo[OS]["IsCurrentOS"]:
                        CoreTools.TearDownChroot(MountPoint)
                        CoreTools.Unmount(MountPoint)

                    continue

            #Mount a /boot/efi partition if it exists.
            if OSInfo[OS]["EFIPartition"] != "Unknown":
                if CoreTools.MountPartition(OSInfo[OS]["EFIPartition"], MountPoint+"/boot/efi") != 0:
                    logger.error("MainStartupTools: Main().GetBootloaders(): Failed to mount "+OS+"'s /boot/efi partition! Skipping bootloader detection for this OS.")

                    if not OSInfo[OS]["IsCurrentOS"]:
                        CoreTools.TearDownChroot(MountPoint)
                        CoreTools.Unmount(MountPoint)

                    continue

            #Look for bootloaders.
            BootloaderInfo[OS] = {}
            BootloaderInfo[OS]["OSName"] = OS
            BootloaderInfo[OS]["Bootloader"], BootloaderInfo[OS]["AvailableBootloaders"] = CoreStartupTools.LookForBootloadersOnPartition(OS, OSInfo[OS]["PackageManager"], MountPoint, not OSInfo[OS]["IsCurrentOS"])

            BootloaderInfo[OS]["Timeout"], BootloaderInfo[OS]["GlobalKernelOptions"], BootloaderInfo[OS]["BootDisk"], BootloaderInfo[OS]["BLSpecificDefaultOS"], BootloaderInfo[OS]["DefaultOS"] = (10, "Unknown", "Unknown", "Unknown", "Unknown")

            #For EFI bootloaders, set the boot disk to the OS's EFI Partition.
            if BootloaderInfo[OS]["Bootloader"] in ("GRUB-UEFI", "ELILO"):
                BootloaderInfo[OS]["BootDisk"] = OSInfo[OS]["EFIPartition"]

            if BootloaderInfo[OS]["Bootloader"] in ("GRUB-UEFI", "GRUB2") and os.path.isfile(MountPoint+"/etc/default/grub"):
                GRUBDir, BootloaderInfo[OS]["MenuEntries"] = BootloaderConfigObtainingTools.ParseGRUB2MenuData(MenuData="", MountPoint=MountPoint)[0:2]

                #Get GRUB2's config.
                #If we're using fedora, always look for grubenv in the EFI partition (the grubenv symlink is in /boot/grub2 but it doesn't work when we're chrooting).
                if OSInfo[OS]["PackageManager"] == "yum":
                    GRUBDir = MountPoint+"/boot/efi/EFI/fedora"

                BootloaderInfo[OS]["Timeout"], BootloaderInfo[OS]["GlobalKernelOptions"], BootloaderInfo[OS]["BLSpecificDefaultOS"] = BootloaderConfigObtainingTools.GetGRUB2Config(MountPoint+"/etc/default/grub", GRUBDir+"/grubenv", BootloaderInfo[OS]["MenuEntries"])

                #Try to find GRUB's location if this is GRUB2.
                if BootloaderInfo[OS]["Bootloader"] == "GRUB2":
                    BootloaderInfo[OS]["BootDisk"] = BootloaderConfigObtainingTools.FindGRUB(OSInfo[OS]["Partition"], "GRUB2")

            elif BootloaderInfo[OS]["Bootloader"] == "ELILO" and os.path.isfile(MountPoint+"/etc/elilo.conf"):
                BootloaderInfo[OS]["MenuEntries"] = BootloaderConfigObtainingTools.ParseLILOMenuEntries(MountPoint+"/etc/elilo.conf")
                BootloaderInfo[OS]["Timeout"], BootloaderInfo[OS]["GlobalKernelOptions"], BootloaderInfo[OS]["BLSpecificDefaultOS"] = BootloaderConfigObtainingTools.GetLILOConfig(MountPoint+"/etc/elilo.conf", OS=OS)

            elif BootloaderInfo[OS]["Bootloader"] == "LILO" and os.path.isfile(MountPoint+"/etc/lilo.conf"):
                BootloaderInfo[OS]["MenuEntries"] = BootloaderConfigObtainingTools.ParseLILOMenuEntries(MountPoint+"/etc/lilo.conf")
                BootloaderInfo[OS]["Timeout"], BootloaderInfo[OS]["GlobalKernelOptions"], BootloaderInfo[OS]["BootDisk"], BootloaderInfo[OS]["BLSpecificDefaultOS"] = BootloaderConfigObtainingTools.GetLILOConfig(MountPoint+"/etc/lilo.conf", OS=OS)

            elif BootloaderInfo[OS]["Bootloader"] == "GRUB-LEGACY" and os.path.isfile(MountPoint+"/boot/grub/menu.lst"):
                BootloaderInfo[OS]["MenuEntries"] = BootloaderConfigObtainingTools.ParseGRUBLEGACYMenuEntries(MountPoint+"/boot/grub/menu.lst")
                BootloaderInfo[OS]["Timeout"], BootloaderInfo[OS]["BLSpecificDefaultOS"] = BootloaderConfigObtainingTools.GetGRUBLEGACYConfig(MountPoint+"/boot/grub/menu.lst", BootloaderInfo[OS]["MenuEntries"])
                BootloaderInfo[OS]["BootDisk"] = BootloaderConfigObtainingTools.FindGRUB(OSInfo[OS]["Partition"], "GRUB-LEGACY")

                #Use safe default kernel options.
                logger.info("MainStartupTools: Main().GetBootloaders(): "+OS+" is using GRUB-LEGACY and therefore doesn't have global kernel options. For compatibility's sake, we're setting them to \"quiet splash nomodeset\"...")
                BootloaderInfo[OS]["GlobalKernelOptions"] = "quiet splash nomodeset"

            #If we didn't find the kernel options, set some defaults here, and warn the user.
            if BootloaderInfo[OS]["GlobalKernelOptions"] == "Unknown":
                BootloaderInfo[OS]["GlobalKernelOptions"] = "quiet splash nomodeset"
                logger.warning("MainStartupTools: Main().GetBootloaders(): Couldn't find "+OS+"'s global kernel options! Assuming 'quiet splash nomodeset'...")
                DialogTools.ShowMsgDlg(Message="Couldn't find "+OS+"'s default kernel options! Loading safe defaults instead. Click okay to continue.", Kind="warning")

            #Determine if we can modify this OS from our current one.
            if OSInfo[OS]["Arch"] == SystemInfo["CurrentOSArch"] or (OSInfo[OS]["Arch"] == "i386" and SystemInfo["CurrentOSArch"] == "x86_64"):
                BootloaderInfo[OS]["IsModifyable"] = True
                BootloaderInfo[OS]["Comments"] = "Architecture is "+OSInfo[OS]["Arch"]+"."
                SystemInfo["ModifyableOSs"].append(OS)

            else:
                BootloaderInfo[OS]["IsModifyable"] = False
                BootloaderInfo[OS]["Comments"] = "Architecture is "+OSInfo[OS]["Arch"]+". Not modifyable because current OS is "+SystemInfo["CurrentOSArch"]+"."

            #Match the bootloader-specific default OS to WxFixBoot's OSs by partition.
            logger.info("MainStartupTools: Main().GetBootloaders(): Attempting to match the bootloader's default OS to any OS that WxFixBoot detected...")

            DefaultBootDevice = "Unknown"

            for Menu in BootloaderInfo[OS]["MenuEntries"]:
                for Entry in BootloaderInfo[OS]["MenuEntries"][Menu]:
                    if Entry == BootloaderInfo[OS]["BLSpecificDefaultOS"]:
                        DefaultBootDevice = BootloaderInfo[OS]["MenuEntries"][Menu][Entry]["Partition"]
                        logger.info("MainStartupTools: Main().GetBootloaders(): Found Default OS's partition...")

            #We have the partition, so now find the OS that resides on that partition.
            for OSName in OSInfo:
                if OSInfo[OSName]["Partition"] == DefaultBootDevice:
                    #Set it.
                    BootloaderInfo[OS]["DefaultOS"] = OSName
                    logger.info("MainStartupTools: Main().GetBootloaders(): Successfully matched. The Default OS is "+OSName+"...")

            #Log if we couldn't match them.
            if BootloaderInfo[OS]["DefaultOS"] == "Unknown":
                logger.warning("MainStartupTools: Main().GetBootloaders(): Couldn't match! We will instead use the first OS in the list as the default OS, which is "+SystemInfo["ModifyableOSs"][0]+"...")
                BootloaderInfo[OS]["DefaultOS"] = SystemInfo["ModifyableOSs"][0]

            #*****************
            print("\n\n\n************ OS: "+OS+" ************\n\n\n")
            Keys = BootloaderInfo[OS]["MenuEntries"].keys()

            for Menu in Keys:
                print("\n\n\nMenu Name: "+Menu+"\n\n\n")

                MenuEntries = BootloaderInfo[OS]["MenuEntries"][Menu]["Order"]

                for MenuEntry in MenuEntries:
                    print("\tMenu Entry Name: "+MenuEntry)
                    print("\t\tID: "+BootloaderInfo[OS]["MenuEntries"][Menu][MenuEntry]["ID"])
                    print("\t\tPartition: "+BootloaderInfo[OS]["MenuEntries"][Menu][MenuEntry]["Partition"])
                    print("\t\tKernel Options: "+', '.join(BootloaderInfo[OS]["MenuEntries"][Menu][MenuEntry]["KernelOptions"])+"\n")

            #*****************

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

            #Unmount a /boot partition if it exists.
            if OSInfo[OS]["BootPartition"] != "Unknown":
                if CoreTools.Unmount(MountPoint+"/boot") != 0:
                    logger.error("MainStartupTools: Main().GetBootloaders(): Failed to unmount "+OS+"'s /boot partition! Continuing anyway...")

            #Clean up if needed.
            if not OSInfo[OS]["IsCurrentOS"]:
                #Remove chroot.
                Retval = CoreTools.TearDownChroot(MountPoint)

                if Retval != 0:
                    logger.error("MainStartupTools: Main().GetBootloaders(): Failed to remove chroot from "+MountPoint+"! Attempting to continue anyway...") #*** What should we do here? ***

                #Unmount the OS's partition.
                if CoreTools.Unmount(MountPoint) != 0:
                    logger.error("MainStartupTools: Main().GetBootloaders(): Failed to unmount "+OS+"'s partition! This could indicate that chroot wasn't removed correctly. Continuing anyway...")

    def FinalCheck(self):
        """Check for any conflicting options, and warn the user of any potential pitfalls."""
        #Check and warn about conflicting settings. *** TODO ***
        #Warn if any OSs aren't modifyable.
        UnmodifyableOSs = []

        for OS in BootloaderInfo:
            if BootloaderInfo[OS]["IsModifyable"] == False:
                UnmodifyableOSs.append(OS+BootloaderInfo[OS]["Comments"])

        if UnmodifyableOSs != []:
            DialogTools.ShowMsgDlg(Message="Some of the OSs found on your system cannot be modified! These are:\n\n"+'\n'.join(UnmodifyableOSs)+"\n\nClick okay to continue.")

#End main Class.
