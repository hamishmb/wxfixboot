#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# Main Startup Tools in the StartupTools Package for WxFixBoot Version 3.0.0
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

# pylint: disable=logging-not-lazy
#
# Reason (logging-not-lazy): This is a more readable way of logging.

"""
This module contains the main functions that form most of the cohesive whole
of WxFixBoot's startup procedures.
"""

#Do future imports to prepare to support python 3. Use unicode strings rather than ASCII
#strings, as they fix potential problems.
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

#Import modules.
import os
import sys
import logging

sys.path.append('../..') #Need to be able to import the Tools module from here.
import Tools.coretools as CoreTools #pylint: disable=wrong-import-position
import Tools.dialogtools as DialogTools #pylint: disable=wrong-import-position
from Tools.dictionaries import * #pylint: disable=wrong-import-position

#Import other modules.
from . import core as CoreStartupTools #pylint: disable=wrong-import-position
from . import getbootloaderconfigtools as BootloaderConfigObtainingTools  #pylint: disable=wrong-import-position

#Make unicode an alias for str in Python 3.
if sys.version_info[0] == 3:
    unicode = str #pylint: disable=redefined-builtin,invalid-name
    str = bytes #pylint: disable=redefined-builtin,invalid-name

#Set up logging.
logger = logging.getLogger(__name__)
logger.setLevel(logging.getLogger("WxFixBoot").getEffectiveLevel())

def check_depends():
    """
    Check dependencies, and show an error message and kill the app if the dependencies are not met.
    """

    logger.info("MainStartupTools(): check_depends(): Checking dependencies...")
    #Create a temporary list to allow WxFixBoot to notify the user of particular unmet
    #dependencies. TODO This will need to be updated.
    cmd_list = ("cp", "mv", "which", "uname", "fsck", "ls", "modprobe", "mount", "umount",
                "rm", "ping", "badblocks", "arch", "python", "file", "sh", "echo", "lshw",
                "lvdisplay", "dmidecode", "chroot", "strings", "dd", "blkid")

    #Create a list to contain names of failed commands.
    failed_list = []

    for cmd in cmd_list:
        #Run the command with its argument and log the output (if in debug mode)
        retval, output = CoreTools.start_process("which "+cmd, return_output=True)

        if retval != 0:
            logger.error("check_depends(): Dependency problems! Command: "+cmd
                         + " failed to execute or wasn't found.")

            logger.error("check_depends(): The error was: "+output)
            failed_list.append(cmd)

    #Check if any commands failed.
    if failed_list != []:
        #Missing dependencies!
        logger.critical("check_depends(): Dependencies missing! WxFixBoot will exit. The missing "
                        + "dependencies are: "+', '.join(failed_list)+". Exiting.")

        CoreTools.emergency_exit("The following dependencies could not be found on your system: "
                                 + ', '.join(failed_list)+".\n\nPlease install the missing "
                                 + "dependencies.")

def check_for_live_disk():
    """Try to determine if we're running on a live disk."""
    logger.info("MainStartupTools(): check_for_live_disk(): Attempting to check if we're on a "
                + "live disk...")

    #Detect Parted Magic automatically.
    if "pmagic" in CoreTools.start_process("uname -r", return_output=True)[1]:
        logger.info("MainStartupTools(): check_for_live_disk(): Running on Parted Magic...")
        SYSTEM_INFO["IsLiveDisk"] = True
        SYSTEM_INFO["OnPartedMagic"] = True

    #Try to detect ubuntu-based livecds.
    elif CoreTools.is_mounted("/cow", "/") and os.path.isfile("/cdrom/casper/filesystem.squashfs"):
        logger.info("MainStartupTools(): check_for_live_disk(): "
                    + "Running on Ubuntu-based live disk...")

        SYSTEM_INFO["IsLiveDisk"] = True
        SYSTEM_INFO["OnPartedMagic"] = False

    #Try to detect fedora-based livecds.
    elif CoreTools.is_mounted("/dev/mapper/live-rw", "/") and os.path.isfile("/run/initramfs/live/LiveOS/squashfs.img"):
        logger.info("MainStartupTools(): check_for_live_disk(): "
                    + "Running on Fedora-based live disk...")

        SYSTEM_INFO["IsLiveDisk"] = True
        SYSTEM_INFO["OnPartedMagic"] = False

    #Try to detect if we're not running on a live disk (on a HDD).
    elif "/dev/sd" in CoreTools.get_partition_mounted_at("/"):
        logger.info("MainStartupTools(): check_for_live_disk(): Not running on live disk...")
        SYSTEM_INFO["IsLiveDisk"] = False
        SYSTEM_INFO["OnPartedMagic"] = False

    #Try to detect if we're not running on a live disk (on LVM).
    elif "/dev/mapper/" in CoreTools.get_partition_mounted_at("/"):
        logger.info("MainStartupTools(): check_for_live_disk(): Not running on live disk...")
        SYSTEM_INFO["IsLiveDisk"] = False
        SYSTEM_INFO["OnPartedMagic"] = False

    #Ask the user if we're running on a live disk.
    else:
        logger.info("MainStartupTools(): check_for_live_disk(): Asking the user if we're running "
                    + "on live media...")

        SYSTEM_INFO["IsLiveDisk"] = DialogTools.show_yes_no_dlg(message="Is WxFixBoot being run "
                                                                + "on live media, such as an "
                                                                + "Ubuntu Installer Disk?",
                                                                title="WxFixBoot - Live Media?")

        SYSTEM_INFO["OnPartedMagic"] = False
        logger.info("MainStartupTools(): check_for_live_disk(): Result: "
                    + unicode(SYSTEM_INFO["IsLiveDisk"]))

    #Get current OS architecture.
    logger.info("MainStartupTools(): check_for_live_disk(): Getting architecture of current OS...")
    SYSTEM_INFO["CurrentOSArch"] = CoreStartupTools.determine_os_architecture(mount_point="")

def unmount_all_filesystems():
    """
    Unmount any unnecessary filesystems, to prevent data corruption.
    """

    #Warn about removing devices.
    logger.info("unmount_all_filesystems(): Unmounting all Filesystems...")
    DialogTools.show_msg_dlg(kind="info", message="WxFixBoot is about to gather device "
                             + "information. After this point, you must not remove/add any "
                             + "devices from/to your computer, so do that now if you wish to.")

    #Attempt unmount of all filesystems. TODO Why is this disabled again?
    #logger.debug("unmount_all_filesystems(): Running 'unmount -ad'...")
    #CoreTools.start_process("umount -ad")

    #Make sure that we still have rw access on live disks.
    if SYSTEM_INFO["IsLiveDisk"]:
        logger.info("unmount_all_filesystems(): Attempting to remount '/' to make sure it's "
                    + "still rw...")

        if CoreTools.remount_partition("/") != 0:
            logger.error("unmount_all_filesystems(): Failed to remount / as rw! This probably "
                         + "doesn't matter...")

def check_filesystems():
    """Check all unmounted filesystems."""
    logger.info("check_filesystems(): Checking filesystems if possible. Running 'fsck -ARMp'...")

    if CoreTools.start_process("fsck -ARMp", privileged=True) not in (0, 8):
        logger.critical("check_filesystems(): Failed to check filesystems! Doing emergency "
                        + "exit...")

        CoreTools.emergency_exit("Failed to check filesystems! Please fix your filesystems "
                                 + "and then run WxFixBoot again.")

def mount_core_filesystems():
    """
    Mount all core filsystems defined in the /etc/fstab of the current operating system.
    """

    logger.info("mount_core_filesystems(): Mounting core filesystems in /etc/fstab. Calling "
                + "'mount -avw'...")

    #Don't worry about this error when running on Parted Magic.
    if CoreTools.start_process("mount -avw", privileged=True) != 0 and SYSTEM_INFO["OnPartedMagic"] is False:
        logger.critical("mount_core_filesystems(): Failed to re-mount your filesystems after "
                        + "checking them! Doing emergency exit...")

        CoreTools.emergency_exit("Failed to re-mount your filesystems after checking them!")

def get_oss():
    """Get the names of all OSs on the HDDs."""
    logger.info("get_oss(): Finding operating systems...")
    root_filesystem = CoreTools.get_partition_mounted_at("/")
    os_info = {}

    #Get Linux OSs.
    keys = list(DISK_INFO.keys())
    keys.sort()

    for partition in keys:
        if DISK_INFO[partition]["Type"] == "Device":
            continue

        elif DISK_INFO[partition]["FileSystem"] in ("hfsplus", "hfs", "apfs"): 
            #TODO Check if this is what APFS shows up as.
            #Look for macOS.
            os_name = "macOS ("+partition+")"
            logger.debug("get_oss(): Looking for macOS on "+partition+"...")

            #Check if we need to mount the partition.
            was_mounted = False

            if CoreTools.is_mounted(partition):
                #If mounted, get the mountpoint.
                mount_point = CoreTools.get_mount_point_of(partition)

            else:
                #Mount the partition and check if anything went wrong.
                mount_point = "/tmp/wxfixboot/mountpoints"+partition

                if CoreTools.mount_partition(partition=partition, mount_point=mount_point) != 0:
                    #Ignore the partition.
                    logger.warning("get_oss(): Couldn't mount "+partition
                                   + "! Skipping this partition...")

                    continue

                was_mounted = True

            if os.path.exists(mount_point+"/mach_kernel") or os.path.exists(mount_point+"/System/Library/Kernels/kernel"):
                #Create OS_INFO entry for it.
                logger.debug("get_oss(): Found "+os_name+"...")
                os_info[os_name] = {}
                os_info[os_name]["Name"] = os_name
                os_info[os_name]["IsCurrentOS"] = False
                os_info[os_name]["Arch"] = "Unknown"
                os_info[os_name]["Partition"] = partition
                os_info[os_name]["PackageManager"] = "Mac App Store"
                os_info[os_name]["RawFSTabInfo"], os_info[os_name]["EFIPartition"], os_info[os_name]["BootPartition"] = ("Unknown", "Unknown", "Unknown")

            #unmount the filesystem if needed.
            if was_mounted:
                if CoreTools.unmount(mount_point) != 0:
                    logger.error("get_oss(): Couldn't unmount "+partition
                                 + "! Doing emergency exit...")

                    CoreTools.emergency_exit("Couldn't unmount "+partition+" after looking for "
                                             + "operating systems on it! Please reboot your "
                                             + "computer and try again.")

        elif DISK_INFO[partition]["FileSystem"] in ("vfat", "ntfs", "exfat"):
            #Look for Windows. NOTE: It seems NTFS volumes can't be mounted twice, which is why
            #we're being more careful here.
            #TODO ^ Check, I think it worked before. Good to be cautious either way.
            logger.debug("get_oss(): Looking for Windows on "+partition+"...")

            #Check if we need to mount the partition.
            was_mounted = False

            if CoreTools.is_mounted(partition):
                #If mounted, get the mountpoint.
                mount_point = CoreTools.get_mount_point_of(partition)

            else:
                #Mount the partition and check if anything went wrong.
                mount_point = "/tmp/wxfixboot/mountpoints"+partition

                if CoreTools.mount_partition(partition=partition, mount_point=mount_point) != 0:
                    #Ignore the partition.
                    logger.warning("get_oss(): Couldn't mount "+partition
                                   + "! Skipping this partition...")

                    continue

                was_mounted = True

            #Check if there's a Windows/WinNT dir.
            if not (os.path.isdir(mount_point+"/WinNT") or os.path.isdir(mount_point+"/Windows") or os.path.isdir(mount_point+"/WINDOWS")):
                #Skip this partition, and unmount if needed.
                logger.info("get_oss(): Windows wasn't found...")

            else:
                #Look for lots of different Windows editions.
                if CoreStartupTools.has_windows_9x(mount_point):
                    os_name = "Windows 95/98/ME"

                elif CoreStartupTools.has_windows_xp(mount_point):
                    os_name = "Windows XP"

                elif CoreStartupTools.has_windows_vista(mount_point):
                    os_name = "Windows Vista"

                elif CoreStartupTools.has_windows_7(mount_point):
                    os_name = "Windows 7"

                elif CoreStartupTools.has_windows_8(mount_point):
                    os_name = "Windows 8/8.1"

                elif CoreStartupTools.has_windows_10(mount_point):
                    os_name = "Windows 10"

                else:
                    #Unknown Windows.
                    os_name = "Windows"

                #Create os_info entry for it.
                os_name = os_name+" ("+partition+")"
                logger.debug("get_oss(): Found "+os_name+"...")
                os_info[os_name] = {}
                os_info[os_name]["Name"] = os_name
                os_info[os_name]["IsCurrentOS"] = False
                os_info[os_name]["Arch"] = "Unknown"
                os_info[os_name]["Partition"] = partition
                os_info[os_name]["PackageManager"] = "Windows Installer"
                os_info[os_name]["RawFSTabInfo"], os_info[os_name]["EFIPartition"], os_info[os_name]["BootPartition"] = ("Unknown", "Unknown", "Unknown")

            #unmount the filesystem if needed.
            if was_mounted:
                if CoreTools.unmount(mount_point) != 0:
                    logger.error("get_oss(): Couldn't unmount "+partition
                                 +"! Doing emergency exit...")

                    CoreTools.emergency_exit("Couldn't unmount "+partition+" after looking for "
                                             + "operating systems on it! Please reboot your "
                                             + "computer and try again.")

        else:
            #Look for Linux.
            #The python command runs on python 2 and python 3.
            #TODO Check if Fedora is deprecating "python" as a command in favour of "python3" only.
            logger.debug("get_oss(): Looking for Linux on "+partition+"...")

            #If there are aliases for partition, check if the root FS is one of those too.
            root_filesystem_is_alias = False

            if "Aliases" in DISK_INFO[partition]:
                logger.debug("get_oss(): Checking if RootFS is an alias for "+partition+"...")

                if root_filesystem in DISK_INFO[partition]["Aliases"]:
                    logger.debug("get_oss(): RootFS is an alias...")
                    root_filesystem_is_alias = True

                else:
                    logger.debug("get_oss(): RootFS isn't an alias...")
                    root_filesystem_is_alias = False

            if partition == root_filesystem or root_filesystem_is_alias:
                cmd = "python -c \"from __future__ import print_function; " \
                      "import platform; print(' '.join(platform.linux_distribution()));\""

                apt_cmd = "which apt-get"
                yum_cmd = "which yum"
                chroot = False
                is_current_os = True
                mount_point = ""

            else:
                mount_point = "/tmp/wxfixboot/mountpoints"+partition
                cmd = "chroot "+mount_point+" python -c \"from __future__ import print_function; "\
                "import platform; print(' '.join(platform.linux_distribution()));\""

                apt_cmd = "chroot "+mount_point+" which apt-get"
                yum_cmd = "chroot "+mount_point+" which yum"
                chroot = True
                is_current_os = False

                #Mount the partition and check if anything went wrong.
                if CoreTools.mount_partition(partition=partition, mount_point=mount_point) != 0:
                    #Ignore the partition.
                    logger.warning("get_oss(): Couldn't mount "+partition
                                   + "! Skipping this partition...")

                    continue

            #Look for Linux on this partition.
            retval, temp = CoreTools.start_process(cmd, return_output=True, privileged=True)
            os_name = temp.replace('\n', '')

            #Run the function to get the architechure.
            os_architecture = CoreStartupTools.determine_os_architecture(mount_point=mount_point)

            #If the OS's name wasn't found, but its architecture was, there must be an OS here, so
            #try to use lsb_release if possible before asking the user. Catch if the name is just
            #whitespace too.
            if (retval != 0 or os_name == "" or os_name.isspace()) and os_architecture != None:
                os_name = CoreStartupTools.get_os_name_with_lsb(partition=partition,
                                                                mount_point=mount_point,
                                                                is_current_os=is_current_os)

                #If we really have to, ask the user.
                if os_name is None:
                    logger.warning("get_oss(): Asking user for OS name instead...")
                    os_name = CoreStartupTools.ask_for_os_name(partition=partition,
                                                               is_current_os=is_current_os)

            #Look for APT.
            package_manager = CoreStartupTools.determine_package_manager(apt_cmd=apt_cmd,
                                                                         yum_cmd=yum_cmd)

            #Also check if CoreStartupTools.ask_for_os_name was used to determine the name.
            #If the user skipped naming the OS, ignore it and skip the rest of this loop iteration.
            if os_name != None and os_architecture != None and package_manager != "Unknown":
                #Add this information to os_info.
                os_info[os_name] = {}
                os_info[os_name]["Name"] = os_name
                os_info[os_name]["IsCurrentOS"] = is_current_os
                os_info[os_name]["Arch"] = os_architecture
                os_info[os_name]["Partition"] = partition
                os_info[os_name]["PackageManager"] = package_manager
                os_info[os_name]["RawFSTabInfo"], os_info[os_name]["EFIPartition"], os_info[os_name]["BootPartition"] = CoreStartupTools.get_fstab_info(mount_point, os_name)

                if chroot is False:
                    SYSTEM_INFO["CurrentOS"] = os_info[os_name].copy()

            if chroot:
                #unmount the filesystem.
                if CoreTools.unmount(mount_point) != 0:
                    logger.error("get_oss(): Couldn't unmount "+partition
                                 + "! Doing emergency exit...")
                    CoreTools.emergency_exit("Couldn't unmount "+partition+" after looking for "
                                             + "operating systems on it! Please reboot your "
                                             + "computer and try again.")

                #Remove the temporary mountpoint
                os.rmdir(mount_point)

    #Check that at least one Linux OS was detected.
    linux_oss = []

    #Get list of Linux OSs.
    for _os in os_info:
        if _os[0] not in ("Windows", "macOS"):
            linux_oss.append(os_name)

    if len(linux_oss) < 1:
        logger.critical("get_oss(): No Linux installations found! If you do have Linux "
                        + "installations but WxFixBoot hasn't found them, please file a bug or "
                        + "ask a question on WxFixBoot's launchpad page. If you're using Windows "
                        + "or macOS, then sorry as WxFixBoot has no support for these operating "
                        + "systems. You could instead use the tools provided by Microsoft and "
                        + "Apple to fix any issues with your computer. Exiting...")

        #Exit.
        CoreTools.emergency_exit("You don't appear to have any Linux installations on your hard "
                                 + "disks. If you do have Linux installations but WxFixBoot "
                                 + "hasn't found them, please file a bug or ask a question on "
                                 + "WxFixBoot's launchpad page. If you're using Windows or macOS, "
                                 + "then sorry as WxFixBoot has no support for these operating "
                                 + "systems. You could instead use the tools provided by Microsoft "
                                 + "and Apple to fix any issues with your computer.")

    #Otherwise...
    logger.debug("get_oss(): Done, os_info Populated okay. Contents: "+unicode(os_info))
    return os_info, SYSTEM_INFO

def get_firmware_type():
    """Get the firmware type"""
    #Check if the firmware type is UEFI.
    #Also, look for UEFI variables.
    #Make sure efivars module is loaded. If it doesn't exist, continue anyway.
    CoreTools.start_process("modprobe efivars", privileged=True)

    #Look for the UEFI vars in some common directories.
    if os.path.isdir("/sys/firmware/efi/vars") and CoreTools.start_process("ls /sys/firmware/efi/vars", return_output=True)[1] != "":
        uefi_variables = True
        logger.info("get_firmware_type(): Found UEFI Variables at /sys/firmware/efi/vars...")

    elif os.path.isdir("/proc/efi/vars") and CoreTools.start_process("ls /proc/efi/vars", return_output=True)[1] != "":
        uefi_variables = True
        logger.info("get_firmware_type(): Found UEFI Variables at /proc/efi/vars...")

    elif os.path.isdir("/sys/firmware/efi/efivars") and CoreTools.start_process("ls /sys/firmware/efi/efivars", return_output=True)[1] != "":
        uefi_variables = True
        logger.info("get_firmware_type(): Found UEFI Variables at /sys/firmware/efi/efivars...")

    else:
        logger.info("get_firmware_type(): UEFI vars not found in /sys/firmware/efi/vars, "
                    + "/sys/firmware/efi/efivars, or /proc/efi/vars. This is normal if running "
                    + "on a BIOS system. Determining firmware type a different way...")

        uefi_variables = False

    if uefi_variables:
        #It's UEFI.
        logger.info("get_firmware_type(): Detected Firmware Type as UEFI.")
        SYSTEM_INFO["FirmwareType"] = "UEFI"

    else:
        #Look a second way.
        output = CoreTools.start_process("dmidecode -q -t BIOS", return_output=True,
                                         privileged=True)[1]

        if "UEFI" not in output:
            #It's BIOS.
            logger.info("get_firmware_type(): Detected Firmware Type as BIOS...")
            SYSTEM_INFO["FirmwareType"] = "BIOS"

        else:
            #It's UEFI.
            logger.warning("get_firmware_type(): Detected Firmware Type as UEFI, but couldn't "
                           + "find UEFI variables!")

            SYSTEM_INFO["FirmwareType"] = "UEFI"
            DialogTools.show_msg_dlg(kind="warning", message="Your computer uses UEFI firmware, "
                                     + "but the UEFI variables couldn't be mounted or weren't "
                                     + "found. Please ensure you've booted in UEFI mode rather "
                                     + "than legacy mode to enable access to the UEFI variables. "
                                     + "You can attempt installing a UEFI bootloader without "
                                     + "them, but it might not work, and it isn't recommended.")

def get_bootloaders():
    """
    Find all bootloaders (for each OS), and gather some information about them
    """

    SYSTEM_INFO["ModifyableOSs"] = []

    keys = list(OS_INFO.keys())
    keys.sort()

    for _os in keys:
        #If this is a windows OS, create a standard entry.
        if "Windows" in _os:
            CoreStartupTools.make_bootloaderinfo_entry_for_windows(_os)
            continue

        #Same for macOS.
        elif "macOS" in _os:
            CoreStartupTools.make_bootloaderinfo_entry_for_macos(_os)
            continue

        #If this isn't the current OS, do some preparation.
        if not OS_INFO[_os]["IsCurrentOS"]:
            #Mount the OS's partition.
            mount_point = "/tmp/wxfixboot/mountpoints"+OS_INFO[_os]["Partition"]

            if CoreTools.mount_partition(OS_INFO[_os]["Partition"], mount_point) != 0:
                logger.error("get_bootloaders(): Failed to mount "+_os+"'s partition! Skipping "
                             + "bootloader detection for this OS.")

                continue

            #Set up chroot.
            if CoreTools.setup_chroot(mount_point) != 0:
                logger.error("get_bootloaders(): Couldn't set up chroot on "+mount_point
                             + "! Attempting to remove it in case it's partially set up, "
                             + "and then skipping this OS...")

                CoreTools.teardown_chroot(mount_point)
                continue

        else:
            mount_point = ""

        #Mount a /boot partition if it exists.
        if OS_INFO[_os]["BootPartition"] != "Unknown":
            if CoreTools.mount_partition(OS_INFO[_os]["BootPartition"], mount_point+"/boot") != 0:
                logger.error("get_bootloaders(): Failed to mount "+_os+"'s /boot partition! "
                             + "Skipping bootloader detection for this OS.")

                if not OS_INFO[_os]["IsCurrentOS"]:
                    CoreTools.teardown_chroot(mount_point)
                    CoreTools.unmount(mount_point)

                continue

        #Mount a /boot/efi partition if it exists.
        if OS_INFO[_os]["EFIPartition"] != "Unknown":
            if CoreTools.mount_partition(OS_INFO[_os]["EFIPartition"], mount_point+"/boot/efi") != 0:
                logger.error("get_bootloaders(): Failed to mount "+_os+"'s /boot/efi partition! "
                             + "Skipping bootloader detection for this OS.")

                if not OS_INFO[_os]["IsCurrentOS"]:
                    CoreTools.teardown_chroot(mount_point)
                    CoreTools.unmount(mount_point)

                continue

        #Look for bootloaders.
        BOOTLOADER_INFO[_os] = {}
        BOOTLOADER_INFO[_os]["OSName"] = _os
        BOOTLOADER_INFO[_os]["Bootloader"], BOOTLOADER_INFO[_os]["AvailableBootloaders"] = CoreStartupTools.look_for_bootloaders_on_partition(_os, OS_INFO[_os]["PackageManager"], mount_point, not OS_INFO[_os]["IsCurrentOS"])

        BOOTLOADER_INFO[_os]["Timeout"], BOOTLOADER_INFO[_os]["GlobalKernelOptions"], BOOTLOADER_INFO[_os]["BootDisk"], BOOTLOADER_INFO[_os]["BLSpecificDefaultOS"], BOOTLOADER_INFO[_os]["DefaultOS"] = (10, "Unknown", "Unknown", "Unknown", "Unknown")
        BOOTLOADER_INFO[_os]["MenuEntries"] = {_os: {}}

        #For EFI bootloaders, set the boot disk to the OS's EFI Partition.
        if BOOTLOADER_INFO[_os]["Bootloader"] in ("GRUB-UEFI", "ELILO"):
            BOOTLOADER_INFO[_os]["BootDisk"] = OS_INFO[_os]["EFIPartition"]

        if BOOTLOADER_INFO[_os]["Bootloader"] in ("GRUB-UEFI", "GRUB2") and os.path.isfile(mount_point+"/etc/default/grub"):
            grub_dir, BOOTLOADER_INFO[_os]["MenuEntries"] = BootloaderConfigObtainingTools.parse_grub2_menu_data(menu_data="", mount_point=mount_point)[0:2]

            #Get GRUB2's config.
            #If we're using fedora, always look for grubenv in the EFI partition (the grubenv
            #symlink is in /boot/grub2 but it doesn't work when we're chrooting).
            if OS_INFO[_os]["PackageManager"] == "yum":
                grub_dir = mount_point+"/boot/efi/EFI/fedora"

            BOOTLOADER_INFO[_os]["Timeout"], BOOTLOADER_INFO[_os]["GlobalKernelOptions"], BOOTLOADER_INFO[_os]["BLSpecificDefaultOS"] = BootloaderConfigObtainingTools.get_grub2_config(mount_point+"/etc/default/grub", grub_dir+"/grubenv", BOOTLOADER_INFO[_os]["MenuEntries"])

            #Try to find GRUB's location if this is GRUB2.
            if BOOTLOADER_INFO[_os]["Bootloader"] == "GRUB2":
                BOOTLOADER_INFO[_os]["BootDisk"] = BootloaderConfigObtainingTools.find_grub(OS_INFO[_os]["Partition"], "GRUB2")

        elif BOOTLOADER_INFO[_os]["Bootloader"] == "ELILO" and os.path.isfile(mount_point+"/etc/elilo.conf"):
            BOOTLOADER_INFO[_os]["MenuEntries"] = BootloaderConfigObtainingTools.parse_lilo_menu_entries(mount_point+"/etc/elilo.conf")
            BOOTLOADER_INFO[_os]["Timeout"], BOOTLOADER_INFO[_os]["GlobalKernelOptions"], BOOTLOADER_INFO[_os]["BLSpecificDefaultOS"] = BootloaderConfigObtainingTools.get_lilo_config(mount_point+"/etc/elilo.conf", _os=_os)

        elif BOOTLOADER_INFO[_os]["Bootloader"] == "LILO" and os.path.isfile(mount_point+"/etc/lilo.conf"):
            BOOTLOADER_INFO[_os]["MenuEntries"] = BootloaderConfigObtainingTools.parse_lilo_menu_entries(mount_point+"/etc/lilo.conf")
            BOOTLOADER_INFO[_os]["Timeout"], BOOTLOADER_INFO[_os]["GlobalKernelOptions"], BOOTLOADER_INFO[_os]["BootDisk"], BOOTLOADER_INFO[_os]["BLSpecificDefaultOS"] = BootloaderConfigObtainingTools.get_lilo_config(mount_point+"/etc/lilo.conf", _os=_os)

        elif BOOTLOADER_INFO[_os]["Bootloader"] == "GRUB-LEGACY" and os.path.isfile(mount_point+"/boot/grub/menu.lst"):
            BOOTLOADER_INFO[_os]["MenuEntries"] = BootloaderConfigObtainingTools.parse_grublegacy_menu_entries(mount_point+"/boot/grub/menu.lst")
            BOOTLOADER_INFO[_os]["Timeout"], BOOTLOADER_INFO[_os]["BLSpecificDefaultOS"] = BootloaderConfigObtainingTools.get_grublegacy_config(mount_point+"/boot/grub/menu.lst", BOOTLOADER_INFO[_os]["MenuEntries"])
            BOOTLOADER_INFO[_os]["BootDisk"] = BootloaderConfigObtainingTools.find_grub(OS_INFO[_os]["Partition"], "GRUB-LEGACY")

            #Use safe default kernel options.
            logger.info("get_bootloaders(): "+_os+" is using GRUB-LEGACY and therefore doesn't "
                        + "have global kernel options. For compatibility's sake, we're setting "
                        + "them to \"quiet splash nomodeset\"...")

            BOOTLOADER_INFO[_os]["GlobalKernelOptions"] = "quiet splash nomodeset"

        #If we didn't find the kernel options, set some defaults here, and warn the user.
        if BOOTLOADER_INFO[_os]["GlobalKernelOptions"] == "Unknown":
            BOOTLOADER_INFO[_os]["GlobalKernelOptions"] = "quiet splash nomodeset"
            logger.warning("get_bootloaders(): Couldn't find "+_os+"'s global kernel options! "
                           + "Assuming 'quiet splash nomodeset'...")

            DialogTools.show_msg_dlg(message="Couldn't find "+_os+"'s default kernel options! "
                                     + "Loading safe defaults instead. Click okay to continue.",
                                     kind="warning")

        #Determine if we can modify this OS from our current one.
        if OS_INFO[_os]["Arch"] == SYSTEM_INFO["CurrentOSArch"] or (OS_INFO[_os]["Arch"] == "i386" and SYSTEM_INFO["CurrentOSArch"] == "x86_64"):
            BOOTLOADER_INFO[_os]["IsModifyable"] = True
            BOOTLOADER_INFO[_os]["Comments"] = "Architecture is "+OS_INFO[_os]["Arch"]+"."
            SYSTEM_INFO["ModifyableOSs"].append(_os)

        else:
            BOOTLOADER_INFO[_os]["IsModifyable"] = False
            BOOTLOADER_INFO[_os]["Comments"] = "Architecture is "+OS_INFO[_os]["Arch"]+". Not modifyable because current OS is "+SYSTEM_INFO["CurrentOSArch"]+"."

        #Initialise some default no-action settings.
        BOOTLOADER_INFO[_os]["Settings"] = {}
        BOOTLOADER_INFO[_os]["Settings"]["Reinstall"] = False
        BOOTLOADER_INFO[_os]["Settings"]["Update"] = False
        BOOTLOADER_INFO[_os]["Settings"]["KeepExistingTimeout"] = False
        BOOTLOADER_INFO[_os]["Settings"]["KeepExistingKernelOptions"] = False
        BOOTLOADER_INFO[_os]["Settings"]["NewKernelOptions"] = BOOTLOADER_INFO[_os]["GlobalKernelOptions"]
        BOOTLOADER_INFO[_os]["Settings"]["NewTimeout"] = BOOTLOADER_INFO[_os]["Timeout"]
        BOOTLOADER_INFO[_os]["Settings"]["DefaultOS"] = BOOTLOADER_INFO[_os]["DefaultOS"]
        BOOTLOADER_INFO[_os]["Settings"]["InstallNewBootloader"] = False
        BOOTLOADER_INFO[_os]["Settings"]["NewBootloader"] = "-- Please Select --"
        BOOTLOADER_INFO[_os]["Settings"]["BackupBootloader"] = False
        BOOTLOADER_INFO[_os]["Settings"]["BootloaderBackupTarget"] = "-- Please Select --"
        BOOTLOADER_INFO[_os]["Settings"]["RestoreBootloader"] = False
        BOOTLOADER_INFO[_os]["Settings"]["BootloaderRestoreSource"] = "-- Please Select --"
        BOOTLOADER_INFO[_os]["Settings"]["ChangeThisOS"] = False

        #Initialise GUI state for this OS (True = Enabled, False = Disabled).
        BOOTLOADER_INFO[_os]["GUIState"] = {}
        BOOTLOADER_INFO[_os]["GUIState"]["ReinstallCheckBoxState"] = True
        BOOTLOADER_INFO[_os]["GUIState"]["UpdateCheckBoxState"] = True
        BOOTLOADER_INFO[_os]["GUIState"]["KeepExistingTimeoutCheckBoxState"] = False
        BOOTLOADER_INFO[_os]["GUIState"]["NewTimeoutSpinnerState"] = False
        BOOTLOADER_INFO[_os]["GUIState"]["KeepExistingKernelOptionsCheckBoxState"] = False
        BOOTLOADER_INFO[_os]["GUIState"]["NewKernelOptionsTextCtrlState"] = False
        BOOTLOADER_INFO[_os]["GUIState"]["DefaultOSChoiceState"] = False
        BOOTLOADER_INFO[_os]["GUIState"]["InstallNewBootloaderCheckBoxState"] = True
        BOOTLOADER_INFO[_os]["GUIState"]["NewBootloaderChoiceState"] = False
        BOOTLOADER_INFO[_os]["GUIState"]["BackupBootloaderCheckBoxState"] = True
        BOOTLOADER_INFO[_os]["GUIState"]["BackupBootloaderChoiceState"] = False
        BOOTLOADER_INFO[_os]["GUIState"]["RestoreBootloaderCheckBoxState"] = True
        BOOTLOADER_INFO[_os]["GUIState"]["RestoreBootloaderChoiceState"] = False

        #If there's a seperate EFI partition for this OS,
        #make sure it's unmounted before removing the chroot.
        if OS_INFO[_os]["EFIPartition"] != "Unknown":
            if CoreTools.unmount(mount_point+"/boot/efi") != 0:
                logger.error("MainBackendTools: get_bootloaders(): Failed to unmount "+mount_point
                             + "/boot/efi! This probably doesn't matter...")

        #unmount a /boot partition if it exists.
        if OS_INFO[_os]["BootPartition"] != "Unknown":
            if CoreTools.unmount(mount_point+"/boot") != 0:
                logger.error("get_bootloaders(): Failed to unmount "+_os+"'s /boot partition! "
                             + "Continuing anyway...")

        #Clean up if needed.
        if not OS_INFO[_os]["IsCurrentOS"]:
            #Remove chroot.
            if CoreTools.teardown_chroot(mount_point) != 0:
                logger.error("get_bootloaders(): Failed to remove chroot from "+mount_point
                             + "! Attempting to continue anyway...")

            #unmount the OS's partition.
            if CoreTools.unmount(mount_point) != 0:
                logger.error("get_bootloaders(): Failed to unmount "+_os+"'s partition! This "
                             + "could indicate that chroot wasn't removed correctly. Continuing "
                             + "anyway...")

    #Get default OSs.
    for _os in OS_INFO:
        #Set sensible defaults for Windows.
        if "Windows" in _os:
            BOOTLOADER_INFO[_os]["DefaultBootDevice"] = OS_INFO[_os]["Partition"]
            BOOTLOADER_INFO[_os]["DefaultOS"] = _os
            continue

        #Same for macOS.
        elif "macOS" in _os:
            BOOTLOADER_INFO[_os]["DefaultBootDevice"] = OS_INFO[_os]["Partition"]
            BOOTLOADER_INFO[_os]["DefaultOS"] = _os
            continue

        #Match the bootloader-specific default OS to WxFixBoot's OSs by partition.
        logger.info("get_bootloaders(): Attempting to match "+_os+"'s default OS to any OS that "
                    + "WxFixBoot detected...")

        BOOTLOADER_INFO[_os]["DefaultBootDevice"] = "Unknown"

        if "MenuEntries" in BOOTLOADER_INFO[_os].keys():
            CoreStartupTools.get_defaultoss_partition(_os)

        else:
            #Bootloader's configuration is missing.
            logger.error("get_bootloaders(): "+_os+"'s bootloader configuration is missing. A "
                         + "reinstall will be required for that bootloader...")

        #We have the partition, so now find the OS that resides on that partition.
        CoreStartupTools.match_partition_to_os(_os)

        #Log if we couldn't match them.
        if BOOTLOADER_INFO[_os]["DefaultOS"] == "Unknown":
            logger.warning("get_bootloaders(): Couldn't match! We will instead use the first OS "
                           + "in the list as the default OS, which is "
                           + SYSTEM_INFO["ModifyableOSs"][0]+"...")

            BOOTLOADER_INFO[_os]["DefaultOS"] = SYSTEM_INFO["ModifyableOSs"][0]

        #Set this.
        BOOTLOADER_INFO[_os]["Settings"]["DefaultOS"] = BOOTLOADER_INFO[_os]["DefaultOS"]

def final_check():
    """
    Check for any conflicting options, and warn the user of any potential pitfalls.
    """

    #Check and warn about conflicting settings.
    #Warn if any OSs aren't modifyable.
    unmodifyable_oss = []

    for _os in BOOTLOADER_INFO:
        if BOOTLOADER_INFO[_os]["IsModifyable"] is False:
            unmodifyable_oss.append(_os+", because "+BOOTLOADER_INFO[_os]["Comments"])

    if unmodifyable_oss != []:
        DialogTools.show_msg_dlg(message="Some of the OSs found on your system cannot be "
                                 + "modified! These are:\n\n"+'\n'.join(unmodifyable_oss)
                                 + "\n\nClick okay to continue.")

    #Warn if any bootloaders need reinstalling. TODO Does this work? Can it be improved?
    need_reinstalling = []

    for _os in BOOTLOADER_INFO:
        if "MenuEntries" not in BOOTLOADER_INFO[_os].keys():
            need_reinstalling.append(_os)

    if need_reinstalling != []:
        DialogTools.show_msg_dlg(message="Some of the OSs found on your system have damaged "
                                 + "bootloaders! These are:\n\n"+'\n'.join(need_reinstalling)
                                 + "\n\nPlease reinstall the bootloaders for these operating "
                                 + "systems using \"Bootloader Options\".\n\nClick okay to "
                                 + "continue.")
