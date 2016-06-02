#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Main Startup Tools in the StartupTools Package for WxFixBoot Version 2.0~pre1
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
        CmdList = ("lshw", "mount", "lsb_release", "dmidecode", "chroot", "dd", "gdisk", "blkid", "strings")

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

    def UnmountAllFS(self):
        """Unmount any unnecessary filesystems, to prevent data corruption."""
        #Warn about removing devices. *** Allow this if possible ***
        logger.info("MainStartupTools: Main().UnmountAllFS(): Unmounting all Filesystems...")
        DialogTools.ShowMsgDlg(Kind="info", Message="WxFixBoot is about to gather device information. After this point, you must not remove/add any devices from/to your computer, so do that now if you wish to.")

        #Attempt unmount of all filesystems. *** Check which filesystems can be unmounted first, and use the global mount function ***
        logger.debug("MainStartupTools: Main().UnmountAllFS(): Running 'unmount -ad'...")

        if CoreTools.StartProcess("umount -ad") != 0:
            logger.error("MainStartupTools: Main().UnmountAllFS(): Failed to unmount all filesystems! For the time being, this is normal cos we try to unmount all filesystems...")

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

    def SortSomeInfo(self): #*** Put this somewhere else ***
        """TEMPORARY function to hold this stuff before I put it somewhere else"""
        SystemInfo["Devices"] = []

        Keys = DiskInfo.keys()
        Keys.sort()

        for Disk in Keys:
            if DiskInfo[Disk]["Type"] == "Device":
                if Disk[5:7] in ("sd", "hd"):
                    SystemInfo["Devices"].append(Disk)

            try:
                Temp = DiskInfo[Disk]["Partitioning"]

            except: pass

        #Detect Linux Partitions.
        SystemInfo["LinuxPartitions"] = []

        for Disk in Keys:
            if DiskInfo[Disk]["FileSystem"] in ("ext", "ext2", "ext3", "ext4", "btrfs", "xfs", "jfs", "zfs", "minix", "reiserfs"):
                SystemInfo["LinuxPartitions"].append(Disk)

    def MountCoreFS(self):
        """Mount all core filsystems defined in the /etc/fstab of the current operating system."""
        logger.info("MainStartupTools: Main().MountCoreFS(): Mounting core filesystems in /etc/fstab. Calling 'mount -avw'...")

        #Don't worry about this error when running on Parted Magic.
        if CoreTools.StartProcess("mount -avw") != 0 and SystemInfo["OnPartedMagic"] == False:
            logger.critical("MainStartupTools: Main().MountCoreFS(): Failed to re-mount your filesystems after checking them! Doing emergency exit...")
            CoreTools.EmergencyExit("Failed to re-mount your filesystems after checking them!")

    def GetLinuxOSs(self):
        """Get the names of all Linux OSs on the HDDs."""
        #*** Crashes at log line in InitThread().run() if we couldn't detect the current OS ***
        logger.info("MainStartupTools: Main().GetLinuxOSs(): Finding Linux operating systems...")
        RootFS = CoreTools.GetPartitionMountedAt("/")
        OSInfo = {}
        SystemInfo["UserFriendlyOSNames"] = []
        SystemInfo["OSsWithPackageManagers"] = []

        #Get Linux OSs.
        for Partition in SystemInfo["LinuxPartitions"]:
            logger.debug("MainStartupTools: Main().GetLinuxOSs(): Looking on "+Partition+"...")

            if Partition == RootFS:
                Cmd = "lsb_release -sd"
                APTCmd = "which apt-get"
                Chroot = False
                IsCurrentOS = True
                MountPoint = ""

            else:
                Cmd = "chroot /mnt"+Partition+" lsb_release -sd"
                APTCmd = "chroot /mnt"+Partition+" which apt-get"
                Chroot = True
                IsCurrentOS = False
                MountPoint = "/mnt"+Partition

                #Mount the partition and check if anything went wrong.
                if CoreTools.MountPartition(Partition=Partition, MountPoint=MountPoint) != 0:
                    #Ignore the partition.
                    logger.warning("MainStartupTools: Main().GetLinuxOSs(): Couldn't mount "+Partition+"! Skipping this partition...")
                    continue

            #Look for an OS on this partition.
            Retval, Temp = CoreTools.StartProcess(Cmd, ReturnOutput=True)
            OSName = Temp.replace('\n', '')

            #Run the function to get the architechure.
            OSArch = CoreStartupTools.DetermineOSArchitecture(Partition=Partition, Chroot=Chroot)

            #If the OS's name wasn't found, but its architecture was, there must be an OS here, so ask the user for its name. *** For current OS, quit if not named ***
            if Retval != 0 and OSArch != None:
                OSName = CoreStartupTools.AskForOSName(Partition=Partition, OSArch=OSArch)

            #Look for APT.
            Retval = CoreTools.StartProcess(APTCmd, ShowOutput=False)

            if Retval != 0:
                #Couldn't find apt!
                logger.info("MainBootloaderTools: Main().LookForAPTOnPartition(): Didn't find apt...")
                APT = False

            else:
                #Found APT!
                logger.info("MainBootloaderTools: Main().LookForAPTOnPartition(): Found apt...")
                APT = True

            #Also check if CoreStartupTools.AskForOSName was used to determine the name. If the user skipped naming the OS, ignore it and skip the rest of this loop iteration.
            if OSName != None and OSArch != None and APT:
                #Add this information to OSInfo.
                OSInfo[OSName] = {}
                OSInfo[OSName]["Name"] = OSName
                OSInfo[OSName]["IsCurrentOS"] = IsCurrentOS
                OSInfo[OSName]["Arch"] = OSArch
                OSInfo[OSName]["Partition"] = Partition
                OSInfo[OSName]["PackageManager"] = "apt-get"
                OSInfo[OSName]["RawFSTabInfo"], OSInfo[OSName]["EFIPartition"], OSInfo[OSName]["BootPartition"] = CoreStartupTools.GetFSTabInfo(MountPoint, OSName)
                SystemInfo["UserFriendlyOSNames"].append(OSName)
                SystemInfo["OSsWithPackageManagers"].append(OSName) #*** Get rid of this soon ***

                if Chroot == False:
                    SystemInfo["CurrentOS"] = OSInfo[OSName].copy()

            if Chroot:
                #Unmount the filesystem.
                if CoreTools.Unmount(MountPoint) != 0: #*** What shall we do if this doesn't work? Is emergency exit okay, or try again? ***
                    logger.error("MainStartupTools: Main().GetLinuxOSs(): Couldn't unmount "+Partition+"! Doing emergency exit...")
                    CoreTools.EmergencyExit("Couldn't unmount "+Partition+" after looking for operating systems on it! Please reboot your computer and try again.")

                #Remove the temporary mountpoint
                os.rmdir("/mnt"+Partition)

        #Check that at least one Linux OS was detected.
        if len(OSInfo) >= 1:
            logger.debug("MainStartupTools: Main().GetLinuxOSs(): Done, OSInfo Populated okay. Contents: "+unicode(OSInfo))
            return OSInfo, SystemInfo

        else:
            logger.critical("MainStartupTools: Main().GetLinuxOSs(): Couldn't find any linux operating systems! Linux partitions were detected, but don't appear to contain any OSs! WxFixBoot will now exit, and warn the user...")
            CoreTools.EmergencyExit("Linux partitions were found on your computer, but no Linux operating systems were found! Perhaps you need to recover data from your hard drive, or restore an image first? If you're using Parted Magic, you'll have access to tools that can do that for you now. Otherwise, you may need to install them.")

    def SetDefaultOS(self):
        """*** ABSTRACTION CODE *** Set the default OS"""
        Keys = OSInfo.keys()
        Keys.sort()

        if len(Keys) == 0:
            CoreTools.EmergencyExit("No Linux Operating systems were found on your system, even though Linux partitions were found! This is very likely a bug in WxFixBoot.")

        elif len(Keys) == 1:
            SystemInfo["DefaultOS"] = Keys[0]

        else:
            SystemInfo["DefaultOS"] = DialogTools.ShowChoiceDlg(Message="Please select the Linux Operating System you normally boot.", Title="WxFixBoot - Select Operating System", Choices=Keys)

    def GetFirmwareType(self):
        """Get the firmware type"""
        #Check if the firmware type is UEFI.
        #Also, look for UEFI variables.
        #Make sure efivars module is loaded. If it doesn't exist, continue anyway.
        CoreTools.StartProcess("modprobe efivars")

        #Look for the UEFI vars in some common directories. *** Just because the dir is there doesn't mean the vars are (I think) ***
        if os.path.isdir("/sys/firmware/efi/vars"):
            UEFIVariables = True
            logger.info("MainStartupTools: Main().GetFirmwareType(): Found UEFI Variables at /sys/firmware/efi/vars...")

        elif os.path.isdir("/proc/efi/vars"):
            UEFIVariables = True
            logger.info("MainStartupTools: Main().GetFirmwareType(): Found UEFI Variables at /sys/firmware/efi/efivars...")

        else:
            logger.warning("MainStartupTools: Main().GetFirmwareType(): UEFI vars not found in /sys/firmware/efi/vars or /sys/firmware/efi/efivars. Attempting manual mount...")

            #Attempt to manually mount the efi vars, as we couldn't find them. *** Disabled for the time being *** *** Where should they be mounted? ***
            #if not os.path.isdir("/sys/firmware/efi/vars"):
            #    os.mkdir("/sys/firmware/efi/vars")

            #if CoreTools.MountPartition(Partition="efivars", MountPoint="/sys/firmware/efi/vars", Options="-t efivarfs") != 0: #*** Check this works ***
            #    logger.warning("MainStartupTools: Main().GetFirmwareType(): Failed to mount UEFI vars! Warning user. Ignoring and continuing.")

            #UEFI vars not available or couldn't be mounted. *** This is an incorrect warning on BIOS systems ***
            DialogTools.ShowMsgDlg(Kind="warning", Message="Your computer uses UEFI firmware, but the UEFI variables couldn't be mounted or weren't found. Please ensure you've booted in UEFI mode rather than legacy mode to enable access to the UEFI variables. You can attempt installing a UEFI bootloader without them, but it might not work, and it isn't recommended.")
            UEFIVariables = False

            #else:
            #    #Successfully mounted them.
            #    UEFIVariables = True
            #    logger.info("MainStartupTools: Main().GetFirmwareType(): Mounted UEFI Variables at: /sys/firmware/efi/vars. Continuing...")

        if UEFIVariables:
            #It's UEFI.
            logger.info("MainStartupTools: Main().GetFirmwareType(): Detected Firmware Type as UEFI.")
            Settings["MainSettings"]["FirmwareType"] = "UEFI"
            SystemInfo["DetectedFirmwareType"] = "UEFI"

        else:
            #Look a second way.
            Output = CoreTools.StartProcess("dmidecode -q -t BIOS", ReturnOutput=True)[1]

            if "UEFI" not in Output:
                #It's BIOS.
                logger.info("MainStartupTools: Main().GetFirmwareType(): Detected Firmware Type as BIOS...")
                Settings["MainSettings"]["FirmwareType"] = "BIOS"
                SystemInfo["DetectedFirmwareType"] = "BIOS"
                UEFIVariables = False

            else:
                #It's UEFI.
                logger.info("MainStartupTools: Main().GetFirmwareType(): Detected Firmware Type as UEFI. Looking for UEFI Variables...")
                Settings["MainSettings"]["FirmwareType"] = "UEFI"
                SystemInfo["DetectedFirmwareType"] = "UEFI"
                UEFIVariables = False

    def GetBootloader(self):
        """*** DEPRECATED *** Determine the current bootloader."""
        #*** This is DEPRECATED ***
        logger.debug("MainStartupTools: Main().GetBootloader(): Trying to determine bootloader...")

        #Run some inital scripts
        logger.debug("MainStartupTools: Main().GetBootloader(): Copying MBR bootsector to RAM...")
        MBR = CoreTools.StartProcess("dd if="+SystemInfo["RootDevice"]+" bs=512 count=1", ReturnOutput=True)[1]

        #Wrap this in a loop, so once a Bootloader is found, searching can stop.
        while True:
            #Check for a UEFI partition.
            #Check for a UEFI system partition.
            logger.debug("MainStartupTools: Main().GetBootloader(): Checking For a UEFI partition...")
            SystemInfo["AutoUEFISystemPartition"] = CoreStartupTools.CheckForUEFIPartition(SystemInfo)
            SystemInfo["UEFISystemPartition"] = SystemInfo["AutoUEFISystemPartition"]

            #If there is no UEFI partition, only look for BIOS bootloaders.
            if SystemInfo["UEFISystemPartition"] == None:
                #There is no UEFI partition.
                SystemInfo["EmptyEFIPartition"] = True

                #Look for BIOS bootloaders here.
                #No bootloader was found, so ask the user instead.
                break

            #Mount (or skip if mounted) the UEFI partition.
            logger.info("MainStartupTools: Main().GetBootloader(): Attempting to mount the UEFI partition (if it isn't already)...")
            UEFISYSPMountPoint = "/boot/efi"
            Retval = CoreTools.MountPartition(Partition=SystemInfo["UEFISystemPartition"], MountPoint=UEFISYSPMountPoint)

            if Retval == 0:
                logger.info("MainStartupTools: Main().GetBootloader(): Successfully Mounted UEFI Partition...")

            else:
                #This very rarely happens! *** Is continuing anyway a good idea? ***
                logger.error("MainStartupTools: Main().GetBootloader(): Failed to mount UEFI Partition! Continuing anyway, with reported mountpoint as /boot/efi...")

            logger.info("MainStartupTools: Main().GetBootloader(): UEFI Partition mounted at: "+UEFISYSPMountPoint+". Continuing to look for UEFI bootloaders...")

            #Attempt to figure out which bootloader is present.
            #Obviously, no bootloader has been found.

            #The program waits until something was chosen, so if it executes this, the bootloader has been set.
            break

        #Set the default bootloader value.
        SystemInfo["Bootloader"] = SystemInfo["AutoBootloader"]

    def GetBootloaders(self): #*** Test this thoroughly *** *** Fedora: Check under /boot/grub2, and also check for subdirs like i386-pc in grubdir *** *** Check for separate /boot partition ***
        """Find all bootloaders (for each OS), and gather some information about them"""
        Keys = OSInfo.keys()
        Keys.sort()

        for OS in Keys:
            #If this isn't the current OS, do some preparation.
            if not OSInfo[OS]["IsCurrentOS"]:
                #Mount the OS's partition.
                MountPoint = "/mnt"+OSInfo[OS]["Partition"]
                Chroot = True

                if CoreTools.MountPartition(OSInfo[OS]["Partition"], MountPoint) != 0:
                    logger.error("MainStartupTools: Main().GetBootloaders(): Failed to mount "+OS+"'s partition! Skipping bootloader detection for this OS.")

                #Set up chroot.
                Retval = CoreTools.SetUpChroot(MountPoint)

                if Retval != 0:
                    logger.error("MainStartupTools: Main().GetBootloaders(): Couldn't set up chroot on "+MountPoint+"! Attempting to remove it in case it's partially set up, and then skipping this OS...")
                    CoreTools.TearDownChroot(MountPoint)

            else:
                MountPoint = ""
                Chroot = False

            #Look for bootloaders.
            BootloaderInfo[OS] = {}
            BootloaderInfo[OS]["OSName"] = OS
            BootloaderInfo[OS]["Bootloader"] = CoreStartupTools.LookForBootloadersOnPartition(OSInfo[OS]["PackageManager"], MountPoint, not OSInfo[OS]["IsCurrentOS"])

            BootloaderInfo[OS]["Timeout"], BootloaderInfo[OS]["GlobalKernelOptions"], BootloaderInfo[OS]["BootDisk"], BootloaderInfo[OS]["DefaultOS"] = ("Unknown", "Unknown", "Unknown", "Unknown")

            #For EFI bootloaders, set the boot disk to the OS's EFI Partition.
            if BootloaderInfo[OS]["Bootloader"] in ("GRUB-UEFI", "ELILO"):
                BootloaderInfo[OS]["BootDisk"] = OSInfo[OS]["EFIPartition"]

            if BootloaderInfo[OS]["Bootloader"] in ("GRUB-UEFI", "GRUB2") and os.path.isfile(MountPoint+"/etc/default/grub"):
                BootloaderInfo[OS]["MenuEntries"], BootloaderInfo[OS]["MenuIDs"] = BootloaderConfigObtainingTools.ParseGRUB2MenuEntries(MountPoint+"/boot/grub/grub.cfg")
                BootloaderInfo[OS]["Timeout"], BootloaderInfo[OS]["GlobalKernelOptions"], BootloaderInfo[OS]["DefaultOS"] = BootloaderConfigObtainingTools.GetGRUB2Config(MountPoint+"/etc/default/grub", MountPoint+"/boot/grub/grubenv", BootloaderInfo[OS]["MenuEntries"])

                #Try to find GRUB's location if this is GRUB2.
                if BootloaderInfo[OS]["Bootloader"] == "GRUB2":
                    BootloaderInfo[OS]["BootDisk"] = BootloaderConfigObtainingTools.FindGRUB(OSInfo[OS]["Partition"], "GRUB2")

            elif BootloaderInfo[OS]["Bootloader"] == "ELILO" and os.path.isfile(MountPoint+"/etc/elilo.conf"):
                BootloaderInfo[OS]["MenuEntries"], BootloaderInfo[OS]["MenuIDs"] = BootloaderConfigObtainingTools.ParseLILOMenuEntries(MountPoint+"/etc/elilo.conf")
                BootloaderInfo[OS]["Timeout"], BootloaderInfo[OS]["GlobalKernelOptions"], BootloaderInfo[OS]["DefaultOS"] = BootloaderConfigObtainingTools.GetLILOConfig(MountPoint+"/etc/elilo.conf")

            elif BootloaderInfo[OS]["Bootloader"] == "LILO" and os.path.isfile(MountPoint+"/etc/lilo.conf"):
                BootloaderInfo[OS]["MenuEntries"], BootloaderInfo[OS]["MenuIDs"] = BootloaderConfigObtainingTools.ParseLILOMenuEntries(MountPoint+"/etc/lilo.conf")
                BootloaderInfo[OS]["Timeout"], BootloaderInfo[OS]["GlobalKernelOptions"], BootloaderInfo[OS]["BootDisk"], BootloaderInfo[OS]["DefaultOS"] = BootloaderConfigObtainingTools.GetLILOConfig(MountPoint+"/etc/lilo.conf")

            elif BootloaderInfo[OS]["Bootloader"] == "GRUB-LEGACY" and os.path.isfile(MountPoint+"/boot/grub/menu.lst"):
                BootloaderInfo[OS]["MenuEntries"], BootloaderInfo[OS]["MenuIDs"] = BootloaderConfigObtainingTools.ParseGRUBLEGACYMenuEntries(MountPoint+"/boot/grub/menu.lst")
                BootloaderInfo[OS]["Timeout"] = BootloaderConfigObtainingTools.GetGRUBLEGACYConfig(MountPoint+"/boot/grub/menu.lst")
                BootloaderInfo[OS]["BootDisk"] = BootloaderConfigObtainingTools.FindGRUB(OSInfo[OS]["Partition"], "GRUB-LEGACY")

            #*****************
            Keys = BootloaderInfo[OS]["MenuEntries"].keys()
            Keys.sort()

            for Menu in Keys:
                print("\n\n\nMenu Name: "+Menu+"\n\n\n")

                MenuEntries = BootloaderInfo[OS]["MenuEntries"][Menu].keys()
                MenuEntries.sort()

                for MenuEntry in MenuEntries:
                    print("\tMenu Entry Name: "+MenuEntry+"\n\n")
                    print("\t\tID: "+BootloaderInfo[OS]["MenuEntries"][Menu][MenuEntry]["ID"]+"\n\n")
                    print("\t\tMenu Entry Data:\n\n")

                    for Thing in BootloaderInfo[OS]["MenuEntries"][Menu][MenuEntry]["RawMenuEntryData"]:
                        print("\t\t\t"+Thing)

            #*****************

            BootloaderInfo[OS]["IsModifyable"] = "Unknown"
            BootloaderInfo[OS]["Comments"] = "N/A"

            #Clean up if needed.
            if not OSInfo[OS]["IsCurrentOS"]:
                #Remove chroot.
                Retval = CoreTools.TearDownChroot(MountPoint)

                if Retval != 0:
                    logger.error("MainStartupTools: Main().GetBootloaders(): Failed to remove chroot from "+MountPoint+"! Attempting to continue anyway...") #*** What should we do here? ***

                #Unmount the OS's partition.
                if CoreTools.Unmount(MountPoint) != 0:
                    logger.error("MainStartupTools: Main().GetBootloaders(): Failed to unmount "+OS+"'s partition! This could indicate that chroot wasn't removed correctly. Continuing anyway...")

    def SetDefaults(self): #*** Modify to use dictionaries later ***
        """Set Default for some variables"""
        #Options in MainWindow
        ReinstallBootloader = False
        UpdateBootloader = False 
        QuickFSCheck = False
        BadSectCheck = False

        #Options in Optionsdlg1
        #Set them up for default settings.
        SaveOutput = True
        FullVerbose = False
        Verify = True
        BackupBootSector = False
        BackupPartitionTable = False
        MakeSystemSummary = True
        BootloaderTimeout = -1 #Don't change the timeout by default.

        #Options in Bootloader Options dlg
        SystemInfo["BootloaderToInstall"] = "None"
        BLOptsDlgRun = False

        #Options in Restore dlgs
        RestoreBootSector = False
        BootSectorFile = "None"
        BootSectorTargetDevice = "None"
        BootSectorBackupType = "None"
        RestorePartitionTable = False
        PartitionTableFile = "None"
        PartitionTableTargetDevice = "None"
        PartitionTableBackupType = "None"

        #Other Options
        OptionsDlg1Run = False

        return ReinstallBootloader, UpdateBootloader, QuickFSCheck, BadSectCheck, SaveOutput, FullVerbose, Verify, BackupBootSector, BackupPartitionTable, MakeSystemSummary, BootloaderTimeout, BLOptsDlgRun, RestoreBootSector, BootSectorFile, BootSectorTargetDevice, BootSectorBackupType, RestorePartitionTable, PartitionTableFile, PartitionTableTargetDevice, PartitionTableBackupType, OptionsDlg1Run

    def FinalCheck(self):
        """Check for any conflicting options, and that each variable is set."""
        #Create a temporary list containing all variables to be checked, and a list to contain failed variables. *** Adapt to check dictionary stuff too! *** TODO: SystemInfo["IsLiveDisk"], SystemInfo["Devices"], SystemInfo["DefaultOS"], SystemInfo["DetectedFirmwareType"], SystemInfo["LinuxPartitions"], SystemInfo["RootFS"], SystemInfo["AutoRootDevice"], SystemInfo["RootDevice"], SystemInfo["Bootloader"], SystemInfo["Bootloader"], SystemInfo["UEFISystemPartition"], SystemInfo["EmptyEFIPartition"], Settings["MainSettings"]["FirmwareType"], OSInfo.
        VarList = ()
        FailedList = []

        #Check each global variable (visible to this function as local) is set and declared.
        for var in VarList:
            if var in locals():
                if var == None:
                    #It isn't set.                    
                    logger.critical("MainStartupTools: Main().FinalCheck(): Variable "+var+" hasn't been set, adding it to the failed list...")
                    FailedList.append(var)

            else:
                #It isn't declared.                    
                logger.critical("MainStartupTools: Main().FinalCheck(): Variable "+var+" hasn't been declared, adding it to the failed list...")
                FailedList.append(var)

        #Check if any variables weren't set.
        if FailedList != []:
            #Missing dependencies!
            logger.critical("MainStartupTools: Main().FinalCheck(): Required Settings: "+', '.join(FailedList)+" have not been Determined! This is probably a bug in the program! Exiting...")
            CoreTools.EmergencyExit("The required variables: "+', '.join(FailedList)+", have not been set! WxFixBoot will now shut down to prevent damage to your system. This is probably a bug in the program.")

        #Check and warn about conflicting settings. *** These aren't helpful to people who are new and just want to fix it quick. Maybe try to clarify them/automatically deal with this stuff? Perhaps avoid some of these situations completely by improving startup code *** *** Check we're doing the right things here ***
        #Firmware type warnings.
        if Settings["MainSettings"]["FirmwareType"] == "BIOS" and SystemInfo["Bootloader"] in ('GRUB-UEFI', 'ELILO'):
            logger.warning("MainStartupTools: Main().FinalCheck(): Bootloader is UEFI-type, but system firmware is BIOS! Odd, perhaps a migrated drive? Continuing and setting firmware type to UEFI...")
            DialogTools.ShowMsgDlg(Kind="warning", Message="Your computer seems to use BIOS firmware, but you're using a UEFI-enabled bootloader! WxFixBoot reckons your firmware type was misdetected, and will now set it to UEFI. BIOS firmware does not support booting UEFI-enabled bootloaders, so if you think your firmware type actually is BIOS, it is recommended to install a BIOS-enabled bootloader instead, such as GRUB2. You can safely ignore this message if your firmware type is UEFI.")
            SystemInfo["DetectedFirmwareType"] = "UEFI"
            Settings["MainSettings"]["FirmwareType"] = "UEFI"

        #if Settings["MainSettings"]["FirmwareType"] == "BIOS" and SystemInfo["GPTDisks"] != []: *** Check if we're booting from said device ***
        #    logger.warning("MainStartupTools: Main().FinalCheck(): Firmware is BIOS, but at least one device on the system is using a gpt partition table! This device probably won't be bootable. WxFixBoot suggests repartitioning, if you intend to boot from that device.")
        #    DialogTools.ShowMsgDlg(Kind="warning", Message="Your computer uses BIOS firmware, but you're using an incompatable partition system on at least one device! BIOS firmware will probably fail to boot your operating system, if it resides on that device, so a repartition may be necessary for that device. You can safely ignore this message if your firmware type has been misdetected, or if you aren't booting from that device.")

        #Partition scheme warnings. *** Be more intelligent with these warnings ***
        #if SystemInfo["GPTDisks"] != [] and SystemInfo["Bootloader"] in ('GRUB2', 'LILO', 'GRUB-LEGACY'): *** Check if we boot from said device ***
        #    logger.warning("MainStartupTools: Main().FinalCheck(): GPT Partition table on at least one device with msdos bootloader! Most BIOS firmware cannot read GPT disks. WxFixBoot suggests repartitioning.")
        #    DialogTools.ShowMsgDlg(Kind="warning", Message="You're using a BIOS-enabled bootloader, but you're using an incompatable partition system on at least one device! Most firmware will not support this setup. Ignore this message if you do not boot from this device.")

        #Bootloader warnings.
        if SystemInfo["EmptyEFIPartition"] == True and SystemInfo["UEFISystemPartition"] != None:
            logger.warning("MainStartupTools: Main().FinalCheck(): Empty UEFI partition!")
            DialogTools.ShowMsgDlg(Kind="warning", Message="Your UEFI system partition is empty or doesn't contain any detected bootloaders. If you just created your UEFI system partition, please ensure it's formatted as fat32 or fat16 (Known as vfat in Linux), and then you may continue to install a UEFI bootloader on it. If WxFixBoot didn't detect your UEFI-enabled bootloader, it's still safe to perform operations on the bootloader.")

#End main Class.
