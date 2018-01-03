#!/usr/bin/env python
# -*- coding: utf-8 -*- 
# MainStartupTools test functions for WxFixBoot Version 2.0.2
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

#If you're wondering why this is here, it's so that there are some known good/sane functions to aid testing the ones in DialogTools.

#Do future imports to prepare to support python 3. Use unicode strings rather than ASCII strings, as they fix potential problems.
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

WouldEmergencyExit = False
WouldEmergencyExitBecause = []

def EmergencyExit(Message):
    """Test suite special: sets a variable so the tests know if an Emergency Exit would have been triggered."""
    global WouldEmergencyExit
    global WouldEmergencyExitBecause

    WouldEmergencyExit = True
    WouldEmergencyExitBecause.append(Message)

def CheckDepends():
    """Check dependencies, and show an error message and kill the app if the dependencies are not met."""
    #Create a temporary list to allow WxFixBoot to notify the user of particular unmet dependencies.
    CmdList = ("cp", "mv", "which", "uname", "fsck", "ls", "modprobe", "mount", "umount", "rm", "ping", "badblocks", "arch", "python", "file", "sh", "echo", "lshw", "lvdisplay", "dmidecode", "chroot", "strings", "dd", "blkid")

    #Create a list to contain names of failed commands.
    FailedList = []

    for Command in CmdList:
        #Run the command with its argument and log the output (if in debug mode)
        Retval, Output = CoreTools.StartProcess("which "+Command, ReturnOutput=True)

        if Retval != 0:
            FailedList.append(Command)

    #Check if any commands failed.
    if FailedList != []:
        #Missing dependencies!
        EmergencyExit("The following dependencies could not be found on your system: "+', '.join(FailedList)+".\n\nPlease install the missing dependencies.")

def CheckForLiveDisk():
    """Try to determine if we're running on a live disk."""
    #Detect Parted Magic automatically.
    if "pmagic" in CoreTools.StartProcess("uname -r", ReturnOutput=True)[1]:
        SystemInfo["IsLiveDisk"] = True
        SystemInfo["OnPartedMagic"] = True

    #Try to detect ubuntu-based livecds.
    elif CoreTools.IsMounted("/cow", "/") and os.path.isfile("/cdrom/casper/filesystem.squashfs"):
        SystemInfo["IsLiveDisk"] = True
        SystemInfo["OnPartedMagic"] = False

    #Try to detect fedora-based livecds.
    elif CoreTools.IsMounted("/dev/mapper/live-rw", "/") and os.path.isfile("/run/initramfs/live/LiveOS/squashfs.img"):
        SystemInfo["IsLiveDisk"] = True
        SystemInfo["OnPartedMagic"] = False

    #Try to detect if we're not running on a live disk (on a HDD).
    elif "/dev/sd" in CoreTools.GetPartitionMountedAt("/"):
        SystemInfo["IsLiveDisk"] = False
        SystemInfo["OnPartedMagic"] = False

    #Try to detect if we're not running on a live disk (on LVM).
    elif "/dev/mapper/" in CoreTools.GetPartitionMountedAt("/"):
        SystemInfo["IsLiveDisk"] = False
        SystemInfo["OnPartedMagic"] = False

    #Ask the user if we're running on a live disk.
    else:
        SystemInfo["IsLiveDisk"] = DialogTools.ShowYesNoDlg(Message="Is WxFixBoot being run on live media, such as an Ubuntu Installer Disk?", Title="WxFixBoot - Live Media?")
        SystemInfo["OnPartedMagic"] = False

    #Get current OS architecture.
    SystemInfo["CurrentOSArch"] = CoreStartupTools.DetermineOSArchitecture(MountPoint="")

def GetOSs():
    """Get the names of all OSs on the HDDs."""
    RootFS = CoreTools.GetPartitionMountedAt("/")
    OSInfo = {}

    #Get Linux OSs.
    Keys = DiskInfo.keys()
    Keys.sort()

    for Partition in Keys:
        if DiskInfo[Partition]["Type"] == "Device":
            continue

        elif DiskInfo[Partition]["FileSystem"] in ("hfsplus", "hfs", "apfs"):
            #Look for Mac OS X.
            OSName = "Mac OS X ("+Partition+")"

            #Check if we need to mount the partition.
            WasMounted = False

            if CoreTools.IsMounted(Partition):
                #If mounted, get the mountpoint.
                MountPoint = CoreTools.GetMountPointOf(Partition)

            else:
                #Mount the partition and check if anything went wrong.
                MountPoint = "/tmp/wxfixboot/mountpoints"+Partition

                if CoreTools.MountPartition(Partition=Partition, MountPoint=MountPoint) != 0:
                    #Ignore the partition.
                    continue

                WasMounted = True

            if os.path.exists(MountPoint+"/mach_kernel") or os.path.exists(MountPoint+"/System/Library/Kernels/kernel"):
                #Create OSInfo entry for it.
                OSInfo[OSName] = {}
                OSInfo[OSName]["Name"] = OSName
                OSInfo[OSName]["IsCurrentOS"] = False
                OSInfo[OSName]["Arch"] = "Unknown"
                OSInfo[OSName]["Partition"] = Partition
                OSInfo[OSName]["PackageManager"] = "Mac App Store"
                OSInfo[OSName]["RawFSTabInfo"], OSInfo[OSName]["EFIPartition"], OSInfo[OSName]["BootPartition"] = ("Unknown", "Unknown", "Unknown")

            #Unmount the filesystem if needed.
            if WasMounted:
                if CoreTools.Unmount(MountPoint) != 0: break
                    #CoreTools.EmergencyExit("Couldn't unmount "+Partition+" after looking for operating systems on it! Please reboot your computer and try again.")

        elif DiskInfo[Partition]["FileSystem"] in ("vfat", "ntfs", "exfat"):
            #Look for Windows. NOTE: It seems NTFS volumes can't be mounted twice, which is why we're being more careful here.
            #Check if we need to mount the partition.
            WasMounted = False

            if CoreTools.IsMounted(Partition):
                #If mounted, get the mountpoint.
                MountPoint = CoreTools.GetMountPointOf(Partition)

            else:
                #Mount the partition and check if anything went wrong.
                MountPoint = "/tmp/wxfixboot/mountpoints"+Partition

                if CoreTools.MountPartition(Partition=Partition, MountPoint=MountPoint) != 0:
                    #Ignore the partition.
                    continue

                WasMounted = True

            #Check if there's a Windows/WinNT dir.
            if not (os.path.isdir(MountPoint+"/WinNT") or os.path.isdir(MountPoint+"/Windows") or os.path.isdir(MountPoint+"/WINDOWS")):
                #Skip this partition, and unmount if needed.
                pass

            else:
                #Look for lots of different Windows editions.
                if CoreStartupTools.HasWindows9X(MountPoint):
                    OSName = "Windows 95/98/ME"

                elif CoreStartupTools.HasWindowsXP(MountPoint):
                    OSName = "Windows XP"

                elif CoreStartupTools.HasWindowsVista(MountPoint):
                    OSName = "Windows Vista"

                elif CoreStartupTools.HasWindows7(MountPoint):
                    OSName = "Windows 7"

                elif CoreStartupTools.HasWindows8(MountPoint):
                    OSName = "Windows 8/8.1"

                elif CoreStartupTools.HasWindows10(MountPoint):
                    OSName = "Windows 10"

                else:
                    #Unknown Windows.
                    OSName = "Windows"

                #Create OSInfo entry for it.
                OSName = OSName+" ("+Partition+")"
                OSInfo[OSName] = {}
                OSInfo[OSName]["Name"] = OSName
                OSInfo[OSName]["IsCurrentOS"] = False
                OSInfo[OSName]["Arch"] = "Unknown"
                OSInfo[OSName]["Partition"] = Partition
                OSInfo[OSName]["PackageManager"] = "Windows Installer"
                OSInfo[OSName]["RawFSTabInfo"], OSInfo[OSName]["EFIPartition"], OSInfo[OSName]["BootPartition"] = ("Unknown", "Unknown", "Unknown")

            #Unmount the filesystem if needed.
            if WasMounted:
                if CoreTools.Unmount(MountPoint) != 0: break
                    #CoreTools.EmergencyExit("Couldn't unmount "+Partition+" after looking for operating systems on it! Please reboot your computer and try again.")

        else:
            #Look for Linux.
            #The python command runs on python 2 and python 3.
            #If there are aliases for Partition, check if the root FS is one of those too.
            RootFSIsAlias = False

            if "Aliases" in DiskInfo[Partition]:
                if RootFS in DiskInfo[Partition]["Aliases"]:
                    RootFSIsAlias = True

                else:
                    RootFSIsAlias = False

            if Partition == RootFS or RootFSIsAlias:
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
                    continue

            #Look for Linux on this partition.
            Retval, Temp = CoreTools.StartProcess(Cmd, ReturnOutput=True)
            OSName = Temp.replace('\n', '')

            #Run the function to get the architechure.
            OSArch = CoreStartupTools.DetermineOSArchitecture(MountPoint=MountPoint)

            #If the OS's name wasn't found, but its architecture was, there must be an OS here, so try to use lsb_release if possible before asking the user. Catch if the name is just whitespace too.
            if (Retval != 0 or OSName == "" or OSName.isspace()) and OSArch != None:
                OSName = CoreStartupTools.GetOSNameWithLSB(Partition=Partition, MountPoint=MountPoint, IsCurrentOS=IsCurrentOS)

                #If we really have to, ask the user.
                if OSName == None:
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
                if CoreTools.Unmount(MountPoint) != 0: break
                    #CoreTools.EmergencyExit("Couldn't unmount "+Partition+" after looking for operating systems on it! Please reboot your computer and try again.")

                #Remove the temporary mountpoint
                os.rmdir(MountPoint)

    #Check that at least one OS was detected.
    if len(OSInfo) >= 1:
        return OSInfo, SystemInfo

    else:
        return (False, False)

        #Exit.
        #CoreTools.EmergencyExit("You don't appear to have any Linux installations on your hard disks. If you do have Linux installations but WxFixBoot hasn't found them, please file a bug or ask a question on WxFixBoot's launchpad page. If you're using Windows or Mac OS X, then sorry as WxFixBoot has no support for these operating systems. You could instead use the tools provided by Microsoft and Apple to fix any issues with your computer.")

def GetFirmwareType():
    """Get the firmware type"""
    #Check if the firmware type is UEFI.
    #Also, look for UEFI variables.
    #Make sure efivars module is loaded. If it doesn't exist, continue anyway.
    CoreTools.StartProcess("modprobe efivars")

    #Look for the UEFI vars in some common directories.
    if os.path.isdir("/sys/firmware/efi/vars") and CoreTools.StartProcess("ls /sys/firmware/efi/vars", ReturnOutput=True)[1] != "":
        UEFIVariables = True

    elif os.path.isdir("/proc/efi/vars") and CoreTools.StartProcess("ls /proc/efi/vars", ReturnOutput=True)[1] != "":
        UEFIVariables = True

    elif os.path.isdir("/sys/firmware/efi/efivars") and CoreTools.StartProcess("ls /sys/firmware/efi/efivars", ReturnOutput=True)[1] != "":
        UEFIVariables = True

    else:
        UEFIVariables = False

    if UEFIVariables:
        #It's UEFI.
        SystemInfo["FirmwareType"] = "UEFI"

    else:
        #Look a second way.
        Output = CoreTools.StartProcess("dmidecode -q -t BIOS", ReturnOutput=True)[1]

        if "UEFI" not in Output:
            #It's BIOS.
            SystemInfo["FirmwareType"] = "BIOS"

        else:
            #It's UEFI.
            SystemInfo["FirmwareType"] = "UEFI"
            DialogTools.ShowMsgDlg(Kind="warning", Message="Your computer uses UEFI firmware, but the UEFI variables couldn't be mounted or weren't found. Please ensure you've booted in UEFI mode rather than legacy mode to enable access to the UEFI variables. You can attempt installing a UEFI bootloader without them, but it might not work, and it isn't recommended.")
