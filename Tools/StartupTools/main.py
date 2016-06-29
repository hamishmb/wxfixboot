#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Main Startup Tools in the StartupTools Package for WxFixBoot Version 2.0~pre2
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

    def GetLinuxOSs(self):
        """Get the names of all Linux OSs on the HDDs."""
        #*** Crashes at log line in InitThread().run() if we couldn't detect the current OS ***
        logger.info("MainStartupTools: Main().GetLinuxOSs(): Finding Linux operating systems...")
        RootFS = CoreTools.GetPartitionMountedAt("/")
        OSInfo = {}
        SystemInfo["UserFriendlyOSNames"] = []

        #Get Linux OSs.
        Keys = DiskInfo.keys()
        Keys.sort()

        for Partition in Keys:
            if DiskInfo[Partition]["Type"] == "Device":
                continue

            logger.debug("MainStartupTools: Main().GetLinuxOSs(): Looking on "+Partition+"...")

            if Partition == RootFS:
                Cmd = "python2 -c \"import platform; print ' '.join(platform.linux_distribution());\""
                APTCmd = "which apt-get"
                YUMCmd = "which yum"
                Chroot = False
                IsCurrentOS = True
                MountPoint = ""

            else:
                MountPoint = "/tmp/wxfixboot/mountpoints"+Partition
                Cmd = "chroot "+MountPoint+" python2 -c \"import platform; print ' '.join(platform.linux_distribution());\""
                APTCmd = "chroot "+MountPoint+" which apt-get"
                YUMCmd = "chroot "+MountPoint+" which yum"
                Chroot = True
                IsCurrentOS = False

                #Mount the partition and check if anything went wrong.
                if CoreTools.MountPartition(Partition=Partition, MountPoint=MountPoint) != 0:
                    #Ignore the partition.
                    logger.warning("MainStartupTools: Main().GetLinuxOSs(): Couldn't mount "+Partition+"! Skipping this partition...")
                    continue

            #Look for an OS on this partition.
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
                SystemInfo["UserFriendlyOSNames"].append(OSName)

                if Chroot == False:
                    SystemInfo["CurrentOS"] = OSInfo[OSName].copy()

            if Chroot:
                #Unmount the filesystem.
                if CoreTools.Unmount(MountPoint) != 0: #*** What shall we do if this doesn't work? Is emergency exit okay, or try again? ***
                    logger.error("MainStartupTools: Main().GetLinuxOSs(): Couldn't unmount "+Partition+"! Doing emergency exit...")
                    CoreTools.EmergencyExit("Couldn't unmount "+Partition+" after looking for operating systems on it! Please reboot your computer and try again.")

                #Remove the temporary mountpoint
                os.rmdir(MountPoint)

        #Check that at least one Linux OS was detected.
        if len(OSInfo) >= 1:
            logger.debug("MainStartupTools: Main().GetLinuxOSs(): Done, OSInfo Populated okay. Contents: "+unicode(OSInfo))
            return OSInfo, SystemInfo

        else:
            logger.critical("MainStartupTools: Main().GetLinuxOSs(): Couldn't find any linux operating systems! Linux partitions were detected, but don't appear to contain any OSs! WxFixBoot will now exit, and warn the user...")
            CoreTools.EmergencyExit("Linux partitions were found on your computer, but no Linux operating systems were found! Perhaps you need to recover data from your hard drive, or restore an image first? If you're using Parted Magic, you'll have access to tools that can do that for you now. Otherwise, you may need to install them.")

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

            #Look for bootloaders.
            BootloaderInfo[OS] = {}
            BootloaderInfo[OS]["OSName"] = OS
            BootloaderInfo[OS]["Bootloader"] = CoreStartupTools.LookForBootloadersOnPartition(OSInfo[OS]["PackageManager"], MountPoint, not OSInfo[OS]["IsCurrentOS"])

            BootloaderInfo[OS]["Timeout"], BootloaderInfo[OS]["GlobalKernelOptions"], BootloaderInfo[OS]["BootDisk"], BootloaderInfo[OS]["DefaultOS"] = (10, "Unknown", "Unknown", "Unknown")

            #For EFI bootloaders, set the boot disk to the OS's EFI Partition.
            if BootloaderInfo[OS]["Bootloader"] in ("GRUB-UEFI", "ELILO"):
                BootloaderInfo[OS]["BootDisk"] = OSInfo[OS]["EFIPartition"]

            if BootloaderInfo[OS]["Bootloader"] in ("GRUB-UEFI", "GRUB2") and os.path.isfile(MountPoint+"/etc/default/grub"):
                #Find grub.cfg. (different place on Fedora)
                if os.path.isdir(MountPoint+"/boot/grub"):
                    GRUBDir = MountPoint+"/boot/grub"

                elif os.path.isdir(MountPoint+"/boot/grub2"):
                    GRUBDir = MountPoint+"/boot/grub2"

                BootloaderInfo[OS]["MenuEntries"], BootloaderInfo[OS]["MenuIDs"] = BootloaderConfigObtainingTools.ParseGRUB2MenuEntries(GRUBDir+"/grub.cfg")
                BootloaderInfo[OS]["Timeout"], BootloaderInfo[OS]["GlobalKernelOptions"], BootloaderInfo[OS]["DefaultOS"] = BootloaderConfigObtainingTools.GetGRUB2Config(MountPoint+"/etc/default/grub", GRUBDir+"/grubenv", BootloaderInfo[OS]["MenuEntries"])

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
                BootloaderInfo[OS]["GlobalKernelOptions"] = "quiet splash nomodeset" #*** Guess this from menu entries ***

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
            #*** Implemment this ***
            BootloaderInfo[OS]["IsModifyable"] = "Unknown"
            BootloaderInfo[OS]["Comments"] = "N/A"

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

    def SetDefaults(self): #*** Modify to use dictionaries later ***
        """Set Default for some variables"""
        #Options in MainWindow
        QuickFSCheck = False
        BadSectCheck = False

        #Options in Optionsdlg1
        #Set them up for default settings.
        SaveOutput = True
        FullVerbose = False
        Verify = True
        MakeSystemSummary = True

        #Options in Bootloader Options dlg
        BLOptsDlgRun = False

        #Other Options
        OptionsDlg1Run = False

        SystemInfo["PreviousOSChoice"] = ""

        return QuickFSCheck, BadSectCheck, SaveOutput, FullVerbose, Verify, MakeSystemSummary, BLOptsDlgRun, OptionsDlg1Run

    def FinalCheck(self):
        """Check for any conflicting options, and that each variable is set."""
        #Create a temporary list containing all variables to be checked, and a list to contain failed variables. *** Adapt to check dictionary stuff too! *** TODO: SystemInfo["IsLiveDisk"], SystemInfo["DefaultOS"], SystemInfo["FirmwareType"], SystemInfo["EmptyEFIPartition"], SystemInfo["FirmwareType"], OSInfo.
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

        #Check and warn about conflicting settings. *** TODO ***

#End main Class.
