#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Core Startup Tools in the StartupTools Package for WxFixBoot Version 3.0.0
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

#Do future imports to prepare to support python 3. Use unicode strings rather than ASCII strings, as they fix potential problems.
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

#Import modules.
import os
import sys
import logging

#Import other modules.
from .. import coretools as CoreTools
from .. import dialogtools as DialogTools

#Make unicode an alias for str in Python 3.
if sys.version_info[0] == 3:
    unicode = str #pylint: disable=redefined-builtin,invalid-name
    str = bytes #pylint: disable=redefined-builtin,invalid-name

#Set up logging. FIXME Set logger level as specified on cmdline.
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

#Silence pylint errors about missing global dictionaries.
DiskInfo = {}
SystemInfo = {}
BootloaderInfo = {}
OSInfo = {}

def make_bootloaderinfo_entry_for_macos(the_os):
    """Makes an entry in BootloaderInfo for macOS"""
    BootloaderInfo[the_os] = {}
    BootloaderInfo[the_os]["OSName"] = the_os
    BootloaderInfo[the_os]["Bootloader"] = "BootX/BootROM/boot.efi"
    BootloaderInfo[the_os]["AvailableBootloaders"] = []
    BootloaderInfo[the_os]["MenuEntries"] = {}
    BootloaderInfo[the_os]["IsModifyable"] = False
    BootloaderInfo[the_os]["Comments"] = "WxFixBoot cannot modify macOS."
    BootloaderInfo[the_os]["Timeout"], BootloaderInfo[the_os]["GlobalKernelOptions"], BootloaderInfo[the_os]["BootDisk"], BootloaderInfo[the_os]["BLSpecificDefaultOS"], BootloaderInfo[the_os]["DefaultOS"] = (10, "Unknown", OSInfo[the_os]["Partition"], the_os, the_os)

    #Initialise some default no-action settings.
    BootloaderInfo[the_os]["Settings"] = {}
    BootloaderInfo[the_os]["Settings"]["Reinstall"] = False
    BootloaderInfo[the_os]["Settings"]["Update"] = False
    BootloaderInfo[the_os]["Settings"]["KeepExistingTimeout"] = False
    BootloaderInfo[the_os]["Settings"]["KeepExistingKernelOptions"] = False
    BootloaderInfo[the_os]["Settings"]["NewKernelOptions"] = BootloaderInfo[the_os]["GlobalKernelOptions"]
    BootloaderInfo[the_os]["Settings"]["NewTimeout"] = BootloaderInfo[the_os]["Timeout"]
    BootloaderInfo[the_os]["Settings"]["DefaultOS"] = BootloaderInfo[the_os]["DefaultOS"]
    BootloaderInfo[the_os]["Settings"]["InstallNewBootloader"] = False
    BootloaderInfo[the_os]["Settings"]["NewBootloader"] = "-- Please Select --"
    BootloaderInfo[the_os]["Settings"]["BackupBootloader"] = False
    BootloaderInfo[the_os]["Settings"]["BootloaderBackupTarget"] = "-- Please Select --"
    BootloaderInfo[the_os]["Settings"]["RestoreBootloader"] = False
    BootloaderInfo[the_os]["Settings"]["BootloaderRestoreSource"] = "-- Please Select --"
    BootloaderInfo[the_os]["Settings"]["ChangeThisOS"] = False

    #Initialise GUI state for the_os (True = Enabled, False = Disabled).
    BootloaderInfo[the_os]["GUIState"] = {}
    BootloaderInfo[the_os]["GUIState"]["ReinstallCheckBoxState"] = True
    BootloaderInfo[the_os]["GUIState"]["UpdateCheckBoxState"] = True
    BootloaderInfo[the_os]["GUIState"]["KeepExistingTimeoutCheckBoxState"] = False
    BootloaderInfo[the_os]["GUIState"]["NewTimeoutSpinnerState"] = False
    BootloaderInfo[the_os]["GUIState"]["KeepExistingKernelOptionsCheckBoxState"] = False
    BootloaderInfo[the_os]["GUIState"]["NewKernelOptionsTextCtrlState"] = False
    BootloaderInfo[the_os]["GUIState"]["DefaultOSChoiceState"] = False
    BootloaderInfo[the_os]["GUIState"]["InstallNewBootloaderCheckBoxState"] = True
    BootloaderInfo[the_os]["GUIState"]["NewBootloaderChoiceState"] = False
    BootloaderInfo[the_os]["GUIState"]["BackupBootloaderCheckBoxState"] = True
    BootloaderInfo[the_os]["GUIState"]["BackupBootloaderChoiceState"] = False
    BootloaderInfo[the_os]["GUIState"]["RestoreBootloaderCheckBoxState"] = True
    BootloaderInfo[the_os]["GUIState"]["RestoreBootloaderChoiceState"] = False

def make_bootloaderinfo_entry_for_windows(the_os):
    """Makes an entry in BootloaderInfo for Windows"""
    BootloaderInfo[the_os] = {}
    BootloaderInfo[the_os]["OSName"] = the_os

    if the_os == "Windows 95/98/ME":
        BootloaderInfo[the_os]["Bootloader"] = "AUTOEXEC.BAT"

    elif the_os == "Windows XP":
        BootloaderInfo[the_os]["Bootloader"] = "NTLoader"

    else:
        BootloaderInfo[the_os]["Bootloader"] = "Windows Boot Manager"

    BootloaderInfo[the_os]["AvailableBootloaders"] = []
    BootloaderInfo[the_os]["MenuEntries"] = {}
    BootloaderInfo[the_os]["IsModifyable"] = False
    BootloaderInfo[the_os]["Comments"] = "WxFixBoot cannot modify Windows."
    BootloaderInfo[the_os]["Timeout"], BootloaderInfo[the_os]["GlobalKernelOptions"], BootloaderInfo[the_os]["BootDisk"], BootloaderInfo[the_os]["BLSpecificDefaultOS"], BootloaderInfo[the_os]["DefaultOS"] = (10, "Unknown", "Unknown", the_os, the_os)

    #Initialise some default no-action settings.
    BootloaderInfo[the_os]["Settings"] = {}
    BootloaderInfo[the_os]["Settings"]["Reinstall"] = False
    BootloaderInfo[the_os]["Settings"]["Update"] = False
    BootloaderInfo[the_os]["Settings"]["KeepExistingTimeout"] = False
    BootloaderInfo[the_os]["Settings"]["KeepExistingKernelOptions"] = False
    BootloaderInfo[the_os]["Settings"]["NewKernelOptions"] = BootloaderInfo[the_os]["GlobalKernelOptions"]
    BootloaderInfo[the_os]["Settings"]["NewTimeout"] = BootloaderInfo[the_os]["Timeout"]
    BootloaderInfo[the_os]["Settings"]["DefaultOS"] = BootloaderInfo[the_os]["DefaultOS"]
    BootloaderInfo[the_os]["Settings"]["InstallNewBootloader"] = False
    BootloaderInfo[the_os]["Settings"]["NewBootloader"] = "-- Please Select --"
    BootloaderInfo[the_os]["Settings"]["BackupBootloader"] = False
    BootloaderInfo[the_os]["Settings"]["BootloaderBackupTarget"] = "-- Please Select --"
    BootloaderInfo[the_os]["Settings"]["RestoreBootloader"] = False
    BootloaderInfo[the_os]["Settings"]["BootloaderRestoreSource"] = "-- Please Select --"
    BootloaderInfo[the_os]["Settings"]["ChangeThisOS"] = False

    #Initialise GUI state for this the_os (True = Enabled, False = Disabled).
    BootloaderInfo[the_os]["GUIState"] = {}
    BootloaderInfo[the_os]["GUIState"]["ReinstallCheckBoxState"] = True
    BootloaderInfo[the_os]["GUIState"]["UpdateCheckBoxState"] = True
    BootloaderInfo[the_os]["GUIState"]["KeepExistingTimeoutCheckBoxState"] = False
    BootloaderInfo[the_os]["GUIState"]["NewTimeoutSpinnerState"] = False
    BootloaderInfo[the_os]["GUIState"]["KeepExistingKernelOptionsCheckBoxState"] = False
    BootloaderInfo[the_os]["GUIState"]["NewKernelOptionsTextCtrlState"] = False
    BootloaderInfo[the_os]["GUIState"]["DefaultOSChoiceState"] = False
    BootloaderInfo[the_os]["GUIState"]["InstallNewBootloaderCheckBoxState"] = True
    BootloaderInfo[the_os]["GUIState"]["NewBootloaderChoiceState"] = False
    BootloaderInfo[the_os]["GUIState"]["BackupBootloaderCheckBoxState"] = True
    BootloaderInfo[the_os]["GUIState"]["BackupBootloaderChoiceState"] = False
    BootloaderInfo[the_os]["GUIState"]["RestoreBootloaderCheckBoxState"] = True
    BootloaderInfo[the_os]["GUIState"]["RestoreBootloaderChoiceState"] = False

def has_windows_9x(mount_point):
    """Try to find a Windows 9X installation. Return True if found, False if not."""
    return (os.path.isdir(mount_point+"/WINDOWS") and os.path.exists(mount_point+"/AUTOEXEC.BAT") and os.path.exists(mount_point+"/COMMAND.COM") and os.path.isdir(mount_point+"/My Documents"))

def has_windows_xp(mount_point):
    """Try to find a Windows XP installation. Return True if found, False if not."""
    return (os.path.isfile(mount_point+"/boot.ini") and os.path.isfile(mount_point+"/ntldr") and os.path.isfile(mount_point+"/NTDETECT.COM") and os.path.isdir(mount_point+"/Documents and Settings"))

def has_windows_vista(mount_point):
    """Try to find a Windows Vista installation. Return True if found, False if not."""
    return (os.path.isfile(mount_point+"/bootmgr") and os.path.isdir(mount_point+"/Users") and os.path.isdir(mount_point+"/Boot"))

def has_windows_7(mount_point):
    """Try to find a Windows 7 installation. Return True if found, False if not."""
    return ((not os.path.isfile(mount_point+"/bootmgr")) and os.path.isdir(mount_point+"/Recovery") and os.path.isdir(mount_point+"/Windows/BitLockerDiscoveryVolumeContents"))

def has_windows_8(mount_point):
    """Try to find a Windows 8/8.1 installation. Return True if found, False if not."""
    return (os.path.isfile(mount_point+"/BOOTNXT") and os.path.isdir(mount_point+"/Windows/DesktopTileResources"))

def has_windows_10(mount_point):
    """Try to find a Windows 10 installation. Return True if found, False if not."""
    return (os.path.isdir(mount_point+"/Windows/HoloShell") and os.path.isdir(mount_point+"/Apps"))

def get_defaultoss_partition(the_os):
    """Get the partition for the given OS's default OS to boot"""
    default_boot_device = "Unknown"

    for menu in BootloaderInfo[the_os]["MenuEntries"]:
        for entry in BootloaderInfo[the_os]["MenuEntries"][menu]:

            if entry == BootloaderInfo[the_os]["BLSpecificDefaultOS"]:
                default_boot_device = BootloaderInfo[the_os]["MenuEntries"][menu][entry]["Partition"]
                logger.info("get_defaultoss_partition(): Found Default OS's partition...")
                break

        #Break out if possible.
        if default_boot_device != "Unknown":
            break

    if default_boot_device != "Unknown":
        BootloaderInfo[the_os]["DefaultBootDevice"] = default_boot_device

        #Try to get the UUID too.
        if BootloaderInfo[the_os]["DefaultBootDevice"] in DiskInfo:
            BootloaderInfo[the_os]["DefaultBootDeviceUUID"] = DiskInfo[BootloaderInfo[the_os]["DefaultBootDevice"]]["UUID"]

        else:
            BootloaderInfo[the_os]["DefaultBootDeviceUUID"] = "Unknown"

def match_partition_to_os(the_os):
    """Matches the default boot device (in a menu entry) to an OS in OSInfo"""
    BootloaderInfo[the_os]["DefaultBootDeviceMatchedWith"] = "Unknown"
    BootloaderInfo[the_os]["DefaultOS"] = "Unknown"

    for os_name in OSInfo:
        if os_name not in BootloaderInfo:
            continue

        if "DefaultBootDeviceUUID" in BootloaderInfo[the_os]:
            disk = BootloaderInfo[the_os]["DefaultBootDeviceUUID"]

        else:
            disk = BootloaderInfo[the_os]["DefaultBootDevice"]

        if OSInfo[os_name]["Partition"] != "Unknown" and disk in (OSInfo[os_name]["Partition"], DiskInfo[OSInfo[os_name]["Partition"]]["UUID"]):
            #Set it.
            BootloaderInfo[the_os]["DefaultBootDeviceMatchedWith"] = "Partition"
            BootloaderInfo[the_os]["DefaultOS"] = os_name
            logger.info("match_partition_to_os(): Successfully matched with the partition. The Default OS is "+os_name+"...")
            break

        elif OSInfo[os_name]["BootPartition"] != "Unknown" and disk in (OSInfo[os_name]["BootPartition"], DiskInfo[OSInfo[os_name]["BootPartition"]]["UUID"]):
            #Set it.
            BootloaderInfo[the_os]["DefaultBootDeviceMatchedWith"] = "BootPartition"
            BootloaderInfo[the_os]["DefaultOS"] = os_name
            logger.info("match_partition_to_os(): Successfully matched with the boot partition. The Default OS is "+os_name+"...")
            break

        elif OSInfo[os_name]["EFIPartition"] != "Unknown" and disk in (OSInfo[os_name]["EFIPartition"], DiskInfo[OSInfo[os_name]["EFIPartition"]]["UUID"]):
            #Set it.
            BootloaderInfo[the_os]["DefaultBootDeviceMatchedWith"] = "EFIPartition"
            BootloaderInfo[the_os]["DefaultOS"] = os_name
            logger.info("match_partition_to_os(): Successfully matched with the EFI partition. The Default OS is "+os_name+"...")
            break

def determine_package_manager(apt_cmd, yum_cmd):
    """Determine and return the package manager using the given command strings."""
    package_manager = "Unknown"

    for cmd in (apt_cmd, yum_cmd):
        retval = CoreTools.start_process(cmd, show_output=False)

        if retval != 0:
            if cmd == apt_cmd:
                #Couldn't find apt!
                logger.info("MainStartupTools: Main().determine_package_manager(): Didn't find apt. Looking for yum...")
                continue

            else:
                logger.info("MainStartupTools: Main().determine_package_manager(): Didn't find apt or yum. Returning 'Unknown'...")

        else:
            if cmd == apt_cmd:
                #Found APT!
                logger.info("MainStartupTools: Main().determine_package_manager(): Found apt...")
                package_manager = "apt-get"
                break

            else:
                #Found YUM!
                logger.info("MainStartupTools: Main().determine_package_manager(): Found yum...")
                package_manager = "yum"
                break

    return package_manager

def look_for_bootloaders_on_partition(the_os, package_manager, mount_point, using_chroot):
    """Look for bootloaders installed in the OS in the given mount point."""
    if using_chroot:
        logger.debug("look_for_bootloaders_on_partition(): Looking for bootloaders in "+mount_point+"...")

    else:
        logger.debug("look_for_bootloaders_on_partition(): Looking for bootloaders in / (Current OS)...")

    bootloader = "Unknown"
    available_bootloaders = []

    #Okay, let's run a command in the chroot that was set up in FindBootloaderRemovalOSs(), depending on which package manager this OS uses, and which bootloader is currently installed.
    if package_manager == "apt-get":
        cmd = "dpkg --get-selections"

    else:
        #TODO Do we actually just want yum list?
        cmd = "yum -C list installed"

    if using_chroot:
        cmd = "chroot "+mount_point+" "+cmd

    output = CoreTools.start_process(cmd, show_output=False, return_output=True)[1].split("\n")

    #Look for them in a specific order to be as fast a possible and to avoid false positives.
    if package_manager == "apt-get":
        bootloader_packages = ("grub-efi", "elilo", "grub-pc", "lilo", "grub")
        package_dictionary = {"grub-efi": "GRUB-UEFI", "elilo": "ELILO", "grub-pc": "GRUB2", "lilo": "LILO", "grub": "GRUB-LEGACY"}

    else:
        bootloader_packages = ("grub2-efi", "grub2", "grub")
        package_dictionary = {"grub2-efi": "GRUB-UEFI", "grub2": "GRUB2", "grub": "GRUB-LEGACY"}

    for package in bootloader_packages:
        found = False

        for line in output:
            if package in line:
                if package_manager == "apt-get":
                    if line.split()[1] != "install":
                        continue

                found = True
                break

        if found:
            #On Fedora, GRUB2 for BIOS and GRUB2 for UEFI are both installed by default!
            #To figure out which way we're booting (and which is being used), see whether we are booting in EFI mode or not.
            if package_dictionary[package] == "GRUB-UEFI" and OSInfo[the_os]["PackageManager"] == "yum" and SystemInfo["FirmwareType"] == "BIOS":
                #We're booting with GRUB2.
                continue

            bootloader = package_dictionary[package]
            logger.info("look_for_bootloaders_on_partition(): Found "+bootloader+"...")
            break

    #Look for any other bootloaders that might be available for installation. Ignore GRUB-LEGACY.
    for package in bootloader_packages:
        if package_manager == "apt-get":
            cmd = "apt-cache search "+package

        else:
            cmd = "yum -C search "+package

        if using_chroot:
            cmd = "chroot "+mount_point+" "+cmd

        output = CoreTools.start_process(cmd, show_output=False, return_output=True)[1].split("\n")

        #Only look in the package name.
        for line in output:
            try:
                if package_manager == "apt-get":
                    correct_section = line.split()[0]

                else:
                    correct_section = line.split()[0].split(".")[0]

            except IndexError:
                continue

            if package == correct_section:
                if package_dictionary[package] not in available_bootloaders and package_dictionary[package] != "GRUB-LEGACY":
                    available_bootloaders.append(package_dictionary[package])

    #Log info.
    available_bootloaders.sort()
    logger.info("look_for_bootloaders_on_partition(): Found available bootloaders: "+', '.join(available_bootloaders))

    #Return info.
    return bootloader, available_bootloaders

def get_fstab_info(mount_point, os_name):
    """Get /etc/fstab info and related info (EFI Partition, /boot partition) for the given OS at the given mountpoint."""
    logger.debug("get_fstab_info(): Getting FSTab info in "+mount_point+"/etc/fstab for "+os_name+"...")

    #Do some setup.
    efi_partition = "Unknown"
    boot_partition = "Unknown"

    #Read the raw contents of the /etc/fstab file.
    fstab_file = open(mount_point+"/etc/fstab", "r")
    raw_fstab_contents = fstab_file.read().split("\n")
    fstab_file.close()

    #Gather some info from it.
    for line in raw_fstab_contents:
        #Ignore any comments.
        if "#" in line or line == "":
            continue

        #Try to find this OS's EFI and boot partitions (if there are any).
        if line.split()[1] == "/boot/efi" or line.split()[1] == "/boot":
            logger.debug("get_fstab_info(): Finding partition that automounts at /boot/efi or /boot...")
            temp = line.split()[0]

            #If we have a UUID, convert it into a device node.
            if "UUID=" in temp:
                uuid = temp.split("=")[1]
                logger.debug("get_fstab_info(): Found UUID "+uuid+". Trying to find device name...")

                for disk in DiskInfo:
                    if DiskInfo[disk]["UUID"] == uuid:
                        temp = disk
                        break

            #In case we had a UUID with no match, check again before adding it to OSInfo, else ignore it.
            if "/dev/" in temp:
                logger.debug("get_fstab_info(): Found EFI/Boot Partition "+temp+"...")
                disk = temp

            else:
                logger.error("get_fstab_info(): Couldn't determine device name! Ignoring this device...")
                disk = "Unknown"

        #Try to find this OS's /boot partition (if there is one).
        if line.split()[1] == "/boot/efi":
            efi_partition = disk

        elif line.split()[1] == "/boot":
            boot_partition = disk

    #Return stuff.
    return (raw_fstab_contents, efi_partition, boot_partition)

def determine_os_architecture(mount_point):
    """Look for OS architecture on given partition."""
    if mount_point != "":
        logger.info("determine_os_architecture(): Trying to find OS arch for OS at "+mount_point+"...")

    else:
        logger.info("determine_os_architecture(): Trying to find OS arch for Current OS...")

    #Do setup.
    os_architecture = None
    cmd = "arch"

    while True:
        if mount_point != "":
            cmd = "chroot "+mount_point+" "+cmd

        retval, os_architecture = CoreTools.start_process(cmd, return_output=True)

        #If the command failed, try a second approach.
        if retval != 0 and "arch" in cmd:
            cmd = "file /sbin/init"

        elif retval != 0:
            os_architecture = None
            break

        else:
            break

    #If the command that worked was 'arch', or both failed, we can just return it.
    if "arch" in cmd or retval != 0:
        #Return the arch (or None, if we didn't find it).
        return os_architecture

    else:
        if "32-bit" in os_architecture:
            os_architecture = "i386"

        else:
            os_architecture = "x86_64"

        return os_architecture

def get_os_name_with_lsb(partition, mount_point, is_current_os):
    """Attempt to get an OS's name using lsb_release -sd as a fallback."""
    logger.info("get_os_name_with_lsb(): Attempting to get OS name for OS on "+partition+"...")

    if is_current_os:
        logger.info("get_os_name_with_lsb(): OS is the currently running OS...")
        cmd = "lsb_release -sd"

    else:
        logger.info("get_os_name_with_lsb(): OS isn't the currently running OS...")
        cmd = "chroot "+mount_point+" lsb_release -sd"

    retval, output = CoreTools.start_process(cmd, show_output=False, return_output=True)

    if retval != 0 or output == "":
        logger.error("get_os_name_with_lsb(): Couldn't get OS name! Returning 'Unknown'...")
        return "Unknown"

    #otherwise...
    logger.info("get_os_name_with_lsb(): Success. OS name is "+output+". Returning it...")
    return output

def ask_for_os_name(partition, is_current_os):
    """Ask the user if an OS exists on the given partition."""
    logger.info("ask_for_os_name(): Asking the user for the name of the OS in "+partition+"...")

    if is_current_os:
        DialogTools.show_msg_dlg(kind="warning", message="WxFixBoot couldn't find the name of the current OS. Please name it so that WxFixBoot can function correctly.")
        result = True

    else:
        result = DialogTools.show_yes_no_dlg(message="There is a Linux operating system on partition: "+partition+" but WxFixBoot couldn't find its name. It isn't the currently running OS. Do you want to name it and include it in the list? Only click yes if you believe it is a recent OS. Click Yes if you want to name it, otherwise click No", buttons=("Name it", "Don't name it."))

    if result is False:
        logger.info("ask_for_os_name(): User didn't want to name the OS in "+partition+"! Ignoring it...")
        #User reported no OS in this partition, ignore it.
        return None

    #otherwise...
    logger.debug("ask_for_os_name(): User reported recent Linux OS in "+partition+" (or OS is current OS). Asking name of OS...")
    #User reported that an OS is here.
    result = DialogTools.show_text_entry_dlg(message="Please enter the name of the operating system that is on "+partition+".\nThe name you specify will be used later in the program", title="WxFixBoot - Enter OS Name")

    return result
