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
    def CheckDepends(self): #*** Is blockdev (for blocksizes) needed? ***
        """Check dependencies, and show an error message and kill the app if the dependencies are not met."""
        logger.info("MainStartupTools(): Main().CheckDepends(): Checking dependencies...")
        #Create a temporary list to allow WxFixBoot to notify the user of particular unmet dependencies.
        CmdList = ("lshw", "mount", "lsb_release", "dmidecode", "chroot", "dd", "gdisk", "blockdev")

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

    def UnmountAllFS(self, SystemInfo):
        """Unmount any unnecessary filesystems, to prevent data corruption."""
        #Warn about removing devices. *** Fix this if possible ***
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

    def MountCoreFS(self):
        """Mount all core filsystems defined in the /etc/fstab of the current operating system."""
        logger.info("MainStartupTools: Main().MountCoreFS(): Mounting core filesystems in /etc/fstab. Calling 'mount -avw'...")

        if CoreTools.StartProcess("mount -avw") != 0:
            logger.critical("MainStartupTools: Main().MountCoreFS(): Failed to re-mount your filesystems after checking them! Doing emergency exit...")
            CoreTools.EmergencyExit("Failed to re-mount your filesystems after checking them!")

    def GetLinuxOSs(self, LinuxPartList, SystemInfo): #*** Refactor ***
        """Get the names of all Linux OSs on the HDDs."""
        #*** Crashes at log line in InitThread().run() if we couldn't detect the current OS ***
        logger.info("MainStartupTools: Main().GetLinuxOSs(): Finding Linux operating systems...")
        RootFS = ""
        OSInfo = {}
        SystemInfo["UserFriendlyOSNames"] = []

        if SystemInfo["IsLiveDisk"] == False:
            logger.info("MainStartupTools: Main().GetLinuxOSs(): Getting name and arch of current OS...")

            #Get the partition it's on.
            RootFS = CoreTools.GetPartitionMountedAt("/")

            Retval, Temp = CoreTools.StartProcess("lsb_release -sd", ReturnOutput=True)
            OSName = Temp.replace('\n', '')

            #Run the function to get the architechure, letting the function know that it shouldn't use chroot.
            OSArch = CoreStartupTools.DetermineOSArchitecture(Partition=RootFS, Chroot=False)

            #If the OS's name wasn't found, but its architecture was, there must be an OS here, so ask the user for its name.
            if Retval != 0 and OSArch != None:
                #As this is the current OS, force the user to name it, or be stuck permanently in a loop.
                OSName = None
                while OSName == None:
                    OSName = CoreStartupTools.AskForOSName(Partition=RootFS, OSArch=OSArch, AutoRootFS=AutoRootFS)

            #If we found all of the information!
            if OSName != "" and OSArch != None:
                #Add this information to OSInfo and SystemInfo.
                OSInfo[OSName] = {}
                OSInfo[OSName]["Name"] = OSName
                OSInfo[OSName]["IsCurrentOS"] = True
                OSInfo[OSName]["Arch"] = OSArch
                OSInfo[OSName]["Partition"] = RootFS
                SystemInfo["CurrentOS"] = OSInfo[OSName].copy()
                SystemInfo["UserFriendlyOSNames"].append(OSName)

        #Get Linux OSs.
        for Partition in LinuxPartList:
            if Partition != RootFS:
                #Mount the partition and check if anything went wrong.
                logger.debug("MainStartupTools: Main().GetLinuxOSs(): Looking on "+Partition+"...")

                if CoreTools.MountPartition(Partition=Partition, MountPoint="/mnt"+Partition) != 0:
                    #Ignore the partition.
                    logger.warning("MainStartupTools: Main().GetLinuxOSs(): Couldn't mount "+Partition+"! Skipping this partition...")
                    continue

                #Look for an OS on this partition.
                Retval, Temp = CoreTools.StartProcess("chroot /mnt"+Partition+" lsb_release -sd", ReturnOutput=True)
                OSName = Temp.replace('\n', '')

                #Run the function to get the architechure, letting the function know that it shouldn't use chroot.
                OSArch = CoreStartupTools.DetermineOSArchitecture(Partition=Partition, Chroot=True)

                #If the OS's name wasn't found, but its architecture was, there must be an OS here, so ask the user for its name.
                if Retval != 0 and OSArch != None:
                    OSName = CoreStartupTools.AskForOSName(Partition=Partition, OSArch=OSArch, AutoRootFS=AutoRootFS)

                #Don't use elif here, so we'll also save it if CoreStartupTools.AskForOSName was used to determine the name. If it is still None, the user skipped naming it. Ignore it instead and skip the rest of the loop. *** I don't understand this, so check back later ***
                if OSName != None and OSArch != None:
                    #Add this information to OSInfo.
                    OSInfo[OSName] = {}
                    OSInfo[OSName]["Name"] = OSName
                    OSInfo[OSName]["IsCurrentOS"] = False
                    OSInfo[OSName]["Arch"] = OSArch
                    OSInfo[OSName]["Partition"] = Partition

                #Unmount the filesystem.
                if CoreTools.Unmount("/mnt"+Partition) != 0: #*** What shall we do if this doesn't work? Is emergency exit okay, or try again? ***
                    logger.error("MainStartupTools: Main().GetLinuxOSs(): Couldn't unmount "+Partition+"! Doing emergency exit...")
                    CoreTools.EmergencyExit("Couldn't unmount "+Partition+" after looking for operating systems on it! Please reboot your computer and try again.")

                #Remove the temporary mountpoint
                os.rmdir("/mnt"+Partition)

        #Check that at least one Linux OS was detected.
        if len(OSInfo) >= 1:
            logger.debug("MainStartupTools: Main().GetLinuxOSs(): Done, OSInfo Populated okay. Contents: "+unicode(OSInfo))
            return OSInfo, SystemInfo, RootFS

        else:
            logger.critical("MainStartupTools: Main().GetLinuxOSs(): Couldn't find any linux operating systems! Linux partitions were detected, but don't appear to contain any OSs! WxFixBoot will now exit, and warn the user...")
            CoreTools.EmergencyExit("Linux partitions were found on your computer, but no Linux operating systems were found! Perhaps you need to recover data from your hard drive, or restore an image first? If you're using Parted Magic, you'll have access to tools that can do that for you now. Otherwise, you may need to install them.")

    def GetFirmwareType(self):
        """Get the firmware type"""
        #Check if the firmware type is UEFI.
        Output = CoreTools.StartProcess("dmidecode -q -t BIOS", ReturnOutput=True)[1]

        if "UEFI" not in Output:
            #It's BIOS.
            logger.info("MainStartupTools: Main().GetFirmwareType(): Detected Firmware Type as BIOS...")
            FirmwareType = "BIOS"
            AutoFirmwareType = "BIOS"
            UEFIVariables = False

        else:
            #It's UEFI.
            logger.info("MainStartupTools: Main().GetFirmwareType(): Detected Firmware Type as UEFI. Looking for UEFI Variables...")
            FirmwareType = "UEFI"
            AutoFirmwareType = "UEFI"

            #Also, look for UEFI variables.
            #Make sure efivars module is loaded. If it doesn't exist, continue anyway.
            CoreTools.StartProcess("modprobe efivars")

            #Look for the UEFI vars in some common directories. *** Just because the dir is there doesn't mean the vars are (I think) ***
            if os.path.isdir("/sys/firmware/efi/vars"):
                UEFIVariables = True
                logger.info("MainStartupTools: Main().GetFirmwareType(): Found UEFI Variables at /sys/firmware/efi/vars...")

            elif os.path.isdir("/sys/firmware/efi/efivars"):  
                UEFIVariables = True
                logger.info("MainStartupTools: Main().GetFirmwareType(): Found UEFI Variables at /sys/firmware/efi/efivars...")

            else:
                logger.warning("MainStartupTools: Main().GetFirmwareType(): UEFI vars not found in /sys/firmware/efi/vars or /sys/firmware/efi/efivars. Attempting manual mount...")

                #Attempt to manually mount the efi vars, as we couldn't find them.
                if not os.path.isdir("/sys/firmware/efi/vars"):
                    os.mkdir("/sys/firmware/efi/vars")

                if CoreTools.MountPartition(Partition="efivars", MountPoint="/sys/firmware/efi/vars", Options="-t efivarfs") != 0: #*** Check this works ***
                    logger.warning("MainStartupTools: Main().GetFirmwareType(): Failed to mount UEFI vars! Warning user. Ignoring and continuing.")

                    #UEFI vars not available or couldn't be mounted.
                    DialogTools.ShowMsgDlg(Kind="warning", Message="Your computer uses UEFI firmware, but the UEFI variables couldn't be mounted or weren't found. Please ensure you've booted in UEFI mode rather than legacy mode to enable access to the UEFI variables. You can attempt installing a UEFI bootloader without them, but it might not work, and it isn't recommended.")
                    UEFIVariables = False

                else:
                    #Successfully mounted them.
                    UEFIVariables = True
                    logger.info("MainStartupTools: Main().GetFirmwareType(): Mounted UEFI Variables at: /sys/firmware/efi/vars. Continuing...")

        return FirmwareType, AutoFirmwareType, UEFIVariables

    def GetBootloader(self, RootDevice, SystemInfo, FirmwareType):
        """Determine the current bootloader."""
        #*** Do some of this for each OS *** *** Will need a LOT of modification when I switch to dictionaries ***
        logger.debug("MainStartupTools: Main().GetBootloader(): Trying to determine bootloader...")

        #Run some inital scripts
        logger.debug("MainStartupTools: Main().GetBootloader(): Copying MBR bootsector to RAM...")
        MBR = CoreTools.StartProcess("dd if="+RootDevice+" bs=512 count=1", ReturnOutput=True)[1] #*** We probably need to do this for each and every (MBR) device with a partition containing an OS, as the rootdevice principle falls apart here *** *** Check it worked? ***

        #Wrap this in a loop, so once a Bootloader is found, searching can stop.
        while True:
            #Check for a UEFI partition.
            #Check for a UEFI system partition.
            logger.debug("MainStartupTools: Main().GetBootloader(): Checking For a UEFI partition...")
            AutoUEFISystemPartition = CoreStartupTools.CheckForUEFIPartition(SystemInfo)
            UEFISystemPartition = AutoUEFISystemPartition

            #If there is no UEFI partition, only look for BIOS bootloaders.
            if UEFISystemPartition == None:
                #There is no UEFI partition.
                HelpfulUEFIPartition = False

                #Look for BIOS bootloaders here.
                #Check for GRUB in the MBR
                logger.debug("MainStartupTools: Main().GetBootloader(): Checking for GRUB in bootsector...")
                if CoreStartupTools.CheckForGRUBBIOS(MBR):
                    #We have GRUB BIOS, now figure out which version we have!
                    AutoBootloader = CoreStartupTools.DetermineGRUBBIOSVersion(SystemInfo)
                    break

                #Check for LILO in MBR
                logger.debug("MainStartupTools: Main().GetBootloader(): Checking for LILO in bootsector...")
                if CoreStartupTools.CheckForLILO(MBR):
                    #We have LILO!
                    AutoBootloader = "LILO"
                    logger.info("MainStartupTools: Main().GetBootloader(): Found LILO in MBR (shown as LILO in GUI. Continuing...")
                    break

                #No bootloader was found, so ask the user instead.
                #Do a manual selection of the bootloader.
                logger.warning("MainStartupTools: Main().GetBootloader(): Asking user what the bootloader is, as neither GRUB nor LILO was detected in MBR, and no UEFI partition was found...")
                AutoBootloader = CoreStartupTools.ManualBootloaderSelect(UEFISystemPartition=UEFISystemPartition, FirmwareType=FirmwareType)
                break

            #Mount (or skip if mounted) the UEFI partition.
            logger.info("MainStartupTools: Main().GetBootloader(): Attempting to mount the UEFI partition (if it isn't already)...")
            UEFISYSPMountPoint = CoreStartupTools.MountUEFIPartition(UEFISystemPartition)
            logger.info("MainStartupTools: Main().GetBootloader(): UEFI Partition mounted at: "+UEFISYSPMountPoint+". Continuing to look for UEFI bootloaders...")

            #Attempt to figure out which bootloader is present.
            #Check for GRUB-UEFI.
            logger.debug("MainStartupTools: Main().GetBootloader(): Checking for GRUB-UEFI in UEFI Partition...")
            GrubEFI, HelpfulUEFIPartition = CoreStartupTools.CheckForGRUBUEFI(UEFISYSPMountPoint)

            if GrubEFI:
                #We have GRUB-UEFI!
                AutoBootloader = "GRUB-UEFI"
                logger.info("MainStartupTools: Main().GetBootloader(): Found GRUB-UEFI in UEFI Partition (shown as GRUB-UEFI in GUI). Continuing...")
                break

            #Check for ELILO
            logger.debug("MainStartupTools: Main().GetBootloader(): Checking for ELILO in UEFI Partition...")
            ELILO, HelpfulUEFIPartition = CoreStartupTools.CheckForELILO(UEFISYSPMountPoint)

            if ELILO:
                #We have ELILO!
                AutoBootloader = "ELILO"
                logger.info("MainStartupTools: Main().GetBootloader(): Found ELILO in UEFI Partition (shown as ELILO in GUI). Continuing...")
                break

            #Obviously, no bootloader has been found.
            #Do a manual selection.
            logger.warning("MainStartupTools: Main().GetBootloader(): Asking user what the bootloader is, as no bootloader was found...")
            AutoBootloader = CoreStartupTools.ManualBootloaderSelect(UEFISystemPartition=UEFISystemPartition, FirmwareType=FirmwareType)

            #The program waits until something was chosen, so if it executes this, the bootloader has been set.
            break

        #Set the default bootloader value.
        Bootloader = AutoBootloader

        return Bootloader, AutoBootloader, AutoUEFISystemPartition, UEFISystemPartition, HelpfulUEFIPartition

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
        BootloaderToInstall = "None"
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

        return ReinstallBootloader, UpdateBootloader, QuickFSCheck, BadSectCheck, SaveOutput, FullVerbose, Verify, BackupBootSector, BackupPartitionTable, MakeSystemSummary, BootloaderTimeout, BootloaderToInstall, BLOptsDlgRun, RestoreBootSector, BootSectorFile, BootSectorTargetDevice, BootSectorBackupType, RestorePartitionTable, PartitionTableFile, PartitionTableTargetDevice, PartitionTableBackupType, OptionsDlg1Run

    def FinalCheck(self, LinuxPartList, AutoRootFS, RootFS, AutoRootDevice, RootDevice, FirmwareType, AutoFirmwareType, UEFIVariables, Bootloader, AutoBootloader, UEFISystemPartition, HelpfulUEFIPartition):
        """Check for any conflicting options, and that each variable is set."""
        #Create a temporary list containing all variables to be checked, and a list to contain failed variables. *** Adapt to check dictionary stuff too! *** TODO: SystemInfo["IsLiveDisk"], SystemInfo["GPTDisks"], SystemInfo["MBRDisks"], SystemInfo["Devices"], SystemInfo["DefaultOS"], OSInfo.
        VarList = ('LinuxPartList', 'AutoRootFS', 'RootFS', 'AutoRootDevice', 'RootDevice', 'FirmwareType', 'AutoFirmwareType', 'UEFIVariables', 'Bootloader', 'AutoBootloader', 'UEFISystemPartition', 'HelpfulUEFIPartition')
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
        if FirmwareType == "BIOS" and Bootloader in ('GRUB-UEFI', 'ELILO'):
            logger.warning("MainStartupTools: Main().FinalCheck(): Bootloader is UEFI-type, but system firmware is BIOS! Odd, perhaps a migrated drive? Continuing and setting firmware type to UEFI...")
            DialogTools.ShowMsgDlg(Kind="warning", Message="Your computer seems to use BIOS firmware, but you're using a UEFI-enabled bootloader! WxFixBoot reckons your firmware type was misdetected, and will now set it to UEFI. BIOS firmware does not support booting UEFI-enabled bootloaders, so if you think your firmware type actually is BIOS, it is recommended to install a BIOS-enabled bootloader instead, such as GRUB2. You can safely ignore this message if your firmware type is UEFI.")
            AutoFirmwareType = "UEFI"
            FirmwareType = "UEFI"

        if FirmwareType == "BIOS" and SystemInfo["GPTDisks"] != []:
            logger.warning("MainStartupTools: Main().FinalCheck(): Firmware is BIOS, but at least one device on the system is using a gpt partition table! This device probably won't be bootable. WxFixBoot suggests repartitioning, if you intend to boot from that device.")
            DialogTools.ShowMsgDlg(Kind="warning", Message="Your computer uses BIOS firmware, but you're using an incompatable partition system on at least one device! BIOS firmware will probably fail to boot your operating system, if it resides on that device, so a repartition may be necessary for that device. You can safely ignore this message if your firmware type has been misdetected, or if you aren't booting from that device.")

        #Partition scheme warnings. *** Be more intelligent with these warnings ***
        if SystemInfo["GPTDisks"] != [] and Bootloader in ('GRUB2', 'LILO', 'GRUB-LEGACY'):
            logger.warning("MainStartupTools: Main().FinalCheck(): GPT Partition table on at least one device with msdos bootloader! Most BIOS firmware cannot read GPT disks. WxFixBoot suggests repartitioning.")
            DialogTools.ShowMsgDlg(Kind="warning", Message="You're using a BIOS-enabled bootloader, but you're using an incompatable partition system on at least one device! Most firmware will not support this setup. Ignore this message if you do not boot from this device.")

        #Bootloader warnings.
        if HelpfulUEFIPartition == False and UEFISystemPartition != None:
            logger.warning("MainStartupTools: Main().FinalCheck(): Empty UEFI partition!")
            DialogTools.ShowMsgDlg(Kind="warning", Message="Your UEFI system partition is empty or doesn't contain any detected bootloaders. If you just created your UEFI system partition, please ensure it's formatted as fat32 or fat16 (Known as vfat in Linux), and then you may continue to install a UEFI bootloader on it. If WxFixBoot didn't detect your UEFI-enabled bootloader, it's still safe to perform operations on the bootloader.")

        return AutoFirmwareType, FirmwareType

#End main Class.
