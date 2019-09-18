#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Bootloader Configuration Setting Tools in the Bootloader Tools Package in the Backend Tools
# package for WxFixBoot
# This file is part of WxFixBoot.
# Copyright (C) 2013-2019 Hamish McIntyre-Bhatty
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
This module contains the tools used to set the configuration of bootloaders
when performing operations with WxFixBoot.
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

#Import other modules.
sys.path.append('../../..') #Need to be able to import the Tools module from here.
import Tools.coretools as CoreTools #pylint: disable=wrong-import-position
import Tools.dialogtools as DialogTools #pylint: disable=wrong-import-position
from Tools.dictionaries import DISK_INFO, OS_INFO, BOOTLOADER_INFO #pylint: disable=wrong-import-position
from .. import helpers as HelperBackendTools #pylint: disable=wrong-import-position

#Make unicode an alias for str in Python 3.
if sys.version_info[0] == 3:
    unicode = str #pylint: disable=redefined-builtin,invalid-name
    str = bytes #pylint: disable=redefined-builtin,invalid-name

#Set up logging.
logger = logging.getLogger(__name__)
logger.setLevel(logging.getLogger("WxFixBoot").getEffectiveLevel())

def set_grub2_config(_os, filetoopen, bootloader_timeout, kernel_options):
    """Set GRUB2 config."""
    logger.info("set_grub2_config(): Setting GRUB2 Config in "+filetoopen+"...")
    set_timeout, set_kernel_options, set_default = (False, False, False)

    #Match the bootloader-specific default OS to WxFixBoot's OSs by partition.
    logger.info("set_grub2_config(): Attempting to match the WxFixBoot's default OS for this "
                + "bootloader to any OS that GRUB2 detected...")

    #Find the ID for the menu entry that correspondes to that OS (Main Menu only to avoid
    #recovery options + misc).
    bootloader_specific_default_os = "Unknown"

    for entry in BOOTLOADER_INFO[_os]["NewMenuEntries"]["MainMenu"]["Order"]:
        if HelperBackendTools.partition_matches_os(BOOTLOADER_INFO[_os]["NewMenuEntries"]["MainMenu"][entry]["Partition"],
                                                   BOOTLOADER_INFO[_os]["Settings"]["DefaultOS"]):
            bootloader_specific_default_os = \
            BOOTLOADER_INFO[_os]["NewMenuEntries"]["MainMenu"][entry]["ID"]

            logger.info("set_grub2_config(): Found Default OS's GRUB2 ID...")
            break

    #Log if we couldn't match them.
    if bootloader_specific_default_os == "Unknown":
        logger.warning("set_grub2_config(): Couldn't match! We will instead pick the 1st menu "
                       + "entry. Warning user...")

        DialogTools.show_msg_dlg(message="Couldn't match the default OS you picked to any that "
                                 + BOOTLOADER_INFO[_os]["Settings"]["NewBootloader"]
                                 + " has detected! This doesn't matter, so instead, the first "
                                 + "menu entry will be the default. Click okay to continue...")

        bootloader_specific_default_os = "0"

    #Open the file in read mode, so we can find the new config that needs setting. Also, use a
    #list to temporarily store the modified lines.
    logger.debug("set_grub2_config(): Attempting to modify existing lines in the config file "
                 + "first, without making any new ones...")

    config_file = CoreTools.read_privileged_file(filetoopen)

    new_file_contents = []

    #Loop through each line in the file, paying attention only to the important ones.
    for line in config_file:
        #Look for the timeout setting.
        if 'GRUB_TIMEOUT' in line and '=' in line and set_timeout is False:
            #Found it! Set the value to the current value of bootloader_timeout.
            logger.debug("set_grub2_config(): Found GRUB_TIMEOUT, setting it to '"
                         + unicode(bootloader_timeout)+"'...")

            set_timeout = True
            line = "GRUB_TIMEOUT="+unicode(bootloader_timeout)

        #Look for kernel options setting.
        elif 'GRUB_CMDLINE_LINUX_DEFAULT' in line and '=' in line and set_kernel_options is False:
            #Found it! Set it to the options in kernel_options, carefully making sure we aren't
            #double-quoting it.
            logger.debug("set_grub2_config(): Found GRUB_CMDLINE_LINUX_DEFAULT, setting it to '"
                         + kernel_options+"'...")

            set_kernel_options = True
            line = "GRUB_CMDLINE_LINUX_DEFAULT='"+kernel_options+"'"

        #Look for the "GRUB_DEFAULT" setting.
        elif "GRUB_DEFAULT" in line and '=' in line and set_default is False:
            #Found it. Set it to 'saved', so we can set the default bootloader.
            logger.debug("set_grub2_config(): Found GRUB_DEFAULT, setting it to '"
                         + bootloader_specific_default_os+"' (ID of default OS)...")

            set_default = True
            line = "GRUB_DEFAULT="+bootloader_specific_default_os

        #Comment out the GRUB_HIDDEN_TIMEOUT line.
        elif 'GRUB_HIDDEN_TIMEOUT' in line and 'GRUB_HIDDEN_TIMEOUT_QUIET' not in line \
            and '=' in line and '#' not in line:

            logger.debug("set_grub2_config(): Commenting out GRUB_HIDDEN_TIMEOUT...")
            line = "#"+line

        #Comment out the GRUB_CMDLINE_LINUX line.
        elif 'GRUB_CMDLINE_LINUX' in line and 'GRUB_CMDLINE_LINUX_DEFAULT' not in line \
            and '=' in line and '#' not in line:

            logger.debug("set_grub2_config(): Commenting out GRUB_CMDLINE_LINUX...")
            line = "#"+line

        new_file_contents.append(line+"\n")

    #Check that everything was set. If not, write that config now.
    if set_timeout is False:
        logger.debug("set_grub2_config(): Didn't find GRUB_TIMEOUT in config file. "
                     + "Creating and setting it to '"+unicode(bootloader_timeout)+"'...")

        new_file_contents.append("GRUB_TIMEOUT="+unicode(bootloader_timeout)+"\n")

    if set_kernel_options is False:
        temp = kernel_options.replace('\"', '').replace("\'", "").replace("\n", "")
        logger.debug("set_grub2_config(): Didn't find GRUB_CMDLINE_LINUX_DEFAULT in config file. "
                     + "Creating and setting it to '"+kernel_options+"'...")

        new_file_contents.append("GRUB_CMDLINE_LINUX_DEFAULT='"+temp+"'\n")

    if set_default is False:
        logger.debug("set_grub2_config(): Didn't find GRUB_DEFAULT in config file. "
                     + "Creating and setting it to 'saved'...")

        new_file_contents.append("GRUB_DEFAULT="+bootloader_specific_default_os+"\n")

    #Write the finished lines to the file.
    logger.info("set_grub2_config(): Writing new config to file...")
    CoreTools.write_privileged_file(filetoopen, ''.join(new_file_contents))

    logger.info("set_grub2_config(): Done!")

def install_grub2_to_mbr(package_manager, use_chroot, mount_point, device):
    """Install GRUB2 (BIOS version) into the MBR of the hard drive"""
    #Okay, we've modified the kernel options and the timeout. Now we need to install grub to find
    #the MBR. Use --force to make sure grub installs it even on a GPT disk with no bios boot
    #partition. Can flag as a warning on Fedora systems when just updating, but ignore it.
    if package_manager == "apt-get":
        cmd = "grub-install --force "+device

    elif package_manager == "yum":
        cmd = "grub2-install --force --target=i386-pc "+device

    if use_chroot:
        cmd = "chroot "+mount_point+" "+cmd

    retval = CoreTools.start_process(cmd, show_output=False, privileged=True)

    #Return the return value.
    return retval

def install_grub2_to_efi_partition(package_manager, use_chroot, mount_point,
                                   uefi_system_partition_mount_point, arch):

    """Install GRUB2 (EFI/UEFI version) into the EFI/UEFI partition"""
    #Okay, we've modified the kernel options and the timeout. Now we need to install grub
    #to the UEFI partition.
    #NB: May need --force if EFI vars not present on newer GRUB-EFI versions (Ubuntu 18.10+) check!
    #NB: Don't think so - files touched anyway, but good to double check.
    #NB: Keep an eye on this.
    if package_manager == "apt-get":
        cmd = "grub-install --efi-directory="+uefi_system_partition_mount_point \
              + " --target="+arch+"-efi"

    elif package_manager == "yum":
        #Don't install on fedora, it messes stuff up.
        cmd = "echo 'Disabled on Fedora'"

    if use_chroot:
        cmd = "chroot "+mount_point+" "+cmd

    retval = CoreTools.start_process(cmd, show_output=False, privileged=True)

    #Return the return value.
    return retval

def update_grub2(_os, package_manager, use_chroot, mount_point):
    """
    Run 'update-grub' to update GRUB2's (BIOS and EFI/UEFI) configuration
    and bootloader menu
    """

    #We need to update grub.
    if package_manager == "apt-get":
        cmd = "update-grub2"

    elif package_manager == "yum" and BOOTLOADER_INFO[_os]["Settings"]["NewBootloader"] == "GRUB2":
        cmd = "grub2-mkconfig -o /boot/grub2/grub.cfg"

    elif package_manager == "yum":
        cmd = "grub2-mkconfig -o /boot/efi/EFI/fedora/grub.cfg"

    if use_chroot:
        cmd = "chroot "+mount_point+" "+cmd

    retval = CoreTools.start_process(cmd, show_output=False, privileged=True)

    #Return the return value.
    return retval

def set_lilo_config(_os, filetoopen):
    """Set config for both LILO and ELILO"""
    logger.info("set_lilo_config(): Setting LILO config in "+filetoopen+"...")
    set_timeout, set_boot_device = (False, False)

    #Find the ID for the boot device if possible.
    logger.info("set_lilo_config(): Getting ID for boot device...")

    if BOOTLOADER_INFO[_os]["Settings"]["NewBootloader"] == "LILO":
        if DISK_INFO[DISK_INFO[OS_INFO[_os]["Partition"]]["HostDevice"]]["ID"] != "Unknown":
            #Good, we've got the ID.
            logger.debug("set_lilo_config(): Found ID /dev/disk/by-id/"
                         + DISK_INFO[DISK_INFO[OS_INFO[_os]["Partition"]]["HostDevice"]]["ID"]
                         + "...")

            #Set it to RootDevice's ID.
            boot_device = \
            "/dev/disk/by-id/"+DISK_INFO[DISK_INFO[OS_INFO[_os]["Partition"]]["HostDevice"]]["ID"]

        else:
            #Not so good... We'll have to use the device name, which may change, especially if
            #we're using chroot.
            logger.warning("set_lilo_config(): We don't have the ID! Using "
                           + DISK_INFO[OS_INFO[_os]["Partition"]]["HostDevice"]
                           + " instead. This may cause problems if the device name changes!")

            boot_device = DISK_INFO[OS_INFO[_os]["Partition"]]["HostDevice"]

    elif BOOTLOADER_INFO[_os]["Settings"]["NewBootloader"] == "ELILO":
        if DISK_INFO[OS_INFO[_os]["EFIPartition"]]["ID"] != "Unknown":
            #Good, we've got the ID.
            logger.debug("set_lilo_config(): Found ID /dev/disk/by-id/"
                         + DISK_INFO[OS_INFO[_os]["EFIPartition"]]["ID"]+"...")

            #Set it to RootDevice's ID.
            boot_device = "/dev/disk/by-id/"+DISK_INFO[OS_INFO[_os]["EFIPartition"]]["ID"]

        else:
            #Not so good... We'll have to use the device name, which may change, especially if
            #we're using chroot.
            logger.warning("set_lilo_config(): We don't have the ID! Using "
                           + OS_INFO[_os]["EFIPartition"]+" instead. This may cause problems if "
                           + "the device name changes!")

            boot_device = OS_INFO[_os]["EFIPartition"]

    #Open the file in read mode, so we can find the important bits of config to edit. Also, use a
    #list to temporarily store the modified lines.
    logger.debug("set_lilo_config(): Attempting to modify existing lines in the config file "
                 + "first, without creating any new ones...")

    config_file = CoreTools.read_privileged_file(filetoopen)
    new_file_contents = []

    #Loop through each line in the file, paying attention only to the important ones.
    for line in config_file:
        #Look for the timeout setting (ELILO).
        if BOOTLOADER_INFO[_os]["Settings"]["NewBootloader"] == "ELILO" \
            and 'delay' in line and '=' in line and '#' not in line and set_timeout is False:

            #Found it! Set it to our value.
            logger.debug("set_lilo_config(): Found timeout setting, setting it to "
                         + unicode(BOOTLOADER_INFO[_os]["Settings"]["NewTimeout"])+"...")

            set_timeout = True

            #Also set prompt to use the text menu, chooser to textmenu, and the text menu file.
            logger.debug("set_lilo_config(): Setting up ELILO's text menu...")
            new_file_contents.append("prompt\n")
            new_file_contents.append("chooser=textmenu\n")
            new_file_contents.append("message=elilomenu.msg\n")

            line = "delay="+unicode(BOOTLOADER_INFO[_os]["Settings"]["NewTimeout"]*10)

        #Look for the timeout setting (LILO).
        elif BOOTLOADER_INFO[_os]["Settings"]["NewBootloader"] == "LILO" \
            and 'timeout' in line and '=' in line and '#' not in line and set_timeout is False:

            #Found it! Set it to our value.
            logger.debug("set_lilo_config(): Found timeout setting, setting it to "
                         + unicode(BOOTLOADER_INFO[_os]["Settings"]["NewTimeout"])+"...")

            set_timeout = True
            line = "timeout="+unicode(BOOTLOADER_INFO[_os]["Settings"]["NewTimeout"]*10)

        #Look for the 'boot' setting.
        elif 'boot' in line and '=' in line and '#' not in line and 'map' not in line \
            and set_boot_device is False:

            #Found it, seperate the line.
            logger.debug("set_lilo_config(): Found boot setting, setting it to "+boot_device+"...")
            set_boot_device = True

            #Reassemble the line.
            line = "boot="+boot_device

        #Get rid of any boot entries.
        elif 'image=' in line or '\t' in line:
            #Skip this line, and don't append it to the list.
            logger.debug("set_lilo_config(): Found boot entry, removing it...")
            continue

        new_file_contents.append(line+"\n")

    #Check that everything was set. If not, write that config now.
    if BOOTLOADER_INFO[_os]["Settings"]["NewBootloader"] == "ELILO" and set_timeout is False:
        logger.debug("set_lilo_config(): Didn't find timeout in config file. Creating it and "
                     + "setting it to "+unicode(BOOTLOADER_INFO[_os]["Settings"]["NewTimeout"])
                     + "...")

        #Also set prompt to use the text menu, chooser to textmenu, and the text menu file.
        logger.debug("set_lilo_config(): Setting up ELILO's text menu...")
        new_file_contents.append("prompt\n")
        new_file_contents.append("chooser=textmenu\n")
        new_file_contents.append("message=elilomenu.msg\n")

        new_file_contents.append("delay="+unicode(BOOTLOADER_INFO[_os]["Settings"]["NewTimeout"])
                                 + "\n")

    elif BOOTLOADER_INFO[_os]["Settings"]["NewBootloader"] == "LILO" and set_timeout is False:
        logger.debug("set_lilo_config(): Didn't find timeout in config file. Creating it and "
                     + "setting it to "+unicode(BOOTLOADER_INFO[_os]["Settings"]["NewTimeout"])
                     + "...")

        new_file_contents.append("timeout="+unicode(BOOTLOADER_INFO[_os]["Settings"]["NewTimeout"])
                                 + "\n")

    #Use LILO's compact option to speed the boot process up.
    if BOOTLOADER_INFO[_os]["Settings"]["NewBootloader"] == "LILO":
        new_file_contents.append("compact\n")

    if set_boot_device is False:
        #Now let's find the ID of RootDevice.
        logger.debug("set_lilo_config(): Didn't find boot setting in config file. Creating it and "
                     + "setting it to "+boot_device+"...")

        new_file_contents.append("boot="+boot_device+"\n")

    #Write the finished lines to the file.
    logger.info("set_lilo_config(): Writing new config to file...")
    CoreTools.write_privileged_file(filetoopen, ''.join(new_file_contents))

    logger.info("set_lilo_config(): Done!")

def make_lilo_os_entries(_os, filetoopen, mount_point, kernel_options):
    """Make OS Entries in the bootloader menu for LILO and ELILO, and then the default OS"""
    logger.info("make_lilo_os_entries(): Preparing to make OS entries for "
                + BOOTLOADER_INFO[_os]["Settings"]["NewBootloader"]+"...")

    #Okay, we've saved the kopts, timeout, and the boot device in the list.
    #Now we'll set the OS entries, and then the default OS.
    #Open the file, and add each entry to a temporary list, which will be written to the file
    #later.
    config_file = CoreTools.read_privileged_file(filetoopen)
    new_file_contents = []

    #First, make sure everything else comes first, because LILO and ELILO are picky with the
    #placement of the image files (they must be at the end of the file).
    #We'll also make a placeholder for the default OS, so it comes before the image entries too.
    #Also remove existing entries first.
    logger.debug("make_lilo_os_entries(): Making placeholder for default OS if needed...")

    temp = False

    for line in config_file:
        if 'default' in line and '=' in line and '#' not in line:
            #The place holder already exists. Set a variable so we don't make one.
            temp = True

        elif ("image" in line or "initrd" in line or "label" in line) and "=" in line:
            continue

        elif "read-only" in line or "read-write" in line:
            continue

        new_file_contents.append(line+"\n")

    #If there isn't a placeholder, make one now.
    if temp is False:
        new_file_contents.append("default=setthis\n")

    #Make the OS entries.
    logger.info("make_lilo_os_entries(): Making OS Entries...")

    if BOOTLOADER_INFO[_os]["Settings"]["NewBootloader"] == "ELILO":
        new_file_contents.append("#################### ELILO per-image section "
                                 + "####################\n")

    #As we make these entries, we'll record which ones were actually made, as the user can cancel
    #them if it looks like it won't work.
    completed_entries_list = []

    keys = list(OS_INFO.keys())
    keys.sort()

    for __os in keys:
        logger.info("make_lilo_os_entries(): Preparing to make an entry for: "+__os)

        if not os.path.isfile(mount_point+"/vmlinuz") \
            or not os.path.isfile(mount_point+"/initrd.img"):

            #We can't make an entry for this OS. Warn the user.
            logger.warning("make_lilo_os_entries(): Couldn't find /vmlinuz or /initrd.img for "
                           +__os+ "! Telling the user we can't make an entry...")

            DialogTools.show_msg_dlg(message="Warning: The shortcut to the latest kernel or "
                                     + "initrd weren't found for "+__os+"! Unfortunately, this "
                                     + "means WxFixBoot can't make a bootloader entry for this "
                                     + "OS. Click okay to continue.", kind="warning")

            continue

        #Names in LILO are not allowed to have spaces, so let's remove the spaces from them.
        os_name = __os.replace(' ', '')

        #Check that the name is no longer than 15 characters.
        if len(os_name) > 15:
            #The name is too long! Truncate it to 15 characters.
            logger.warning("make_lilo_os_entries(): Truncating OS Name: "+os_name
                           + " to 15 characters...")

            os_name = os_name[0:15]

        #Now let's make the entries (both standard and recovery).
        assemble_lilo_menu_entry(os_name, __os, kernel_options, new_file_contents)
        assemble_lilo_menu_entry(os_name[0:-4]+"recv", __os, kernel_options+" recovery",
                                 new_file_contents)

        #Add this OS to the Completed Entries List, because if we got this far it's done and added.
        logger.debug("make_lilo_os_entries(): OS Entry for "+__os+" is done!")
        completed_entries_list.append(os_name)

    #Now set the default OS.
    #First, write the semi-finished lines to the file.
    logger.info("make_lilo_os_entries(): Writing OS Entries and config to file...")
    CoreTools.write_privileged_file(filetoopen, ''.join(new_file_contents))
    logger.info("make_lilo_os_entries(): Done!")

    #Open the file again, with the new files written.
    logger.debug("make_lilo_os_entries(): Preparing to set default OS to boot...")
    config_file = CoreTools.read_privileged_file(filetoopen)
    new_file_contents = []

    #Remove all of the spaces, truncating the OS name if necessary.
    defaultos_name = BOOTLOADER_INFO[_os]["Settings"]["DefaultOS"].replace(' ', '')

    #Check that the name is no longer than 15 characters.
    if len(defaultos_name) > 15:
        #The name is too long! Truncate it to 15 characters.
        logger.warning("make_lilo_os_entries(): Truncating OS Name: "+defaultos_name
                       + " to 15 characters...")

        defaultos_name = defaultos_name[0:15]

    #Now, check if its entry was added to the file, and ask the user for a new one if it wasn't.
    if defaultos_name not in completed_entries_list:
        logger.info("make_lilo_os_entries(): Default OS not in the Completed Entries List! "
                    + "Asking the user for a new one...")

        if len(completed_entries_list) <= 0:
            #Something went wrong here! No OSs appear to have been added to the list.
            #Warn the user.
            logger.error("make_lilo_os_entries(): completed_entries_list is empty! "
                         + "This suggests that no OSs have been added to the list! "
                         + "Warn the user, and skip this part of the operation.")

            DialogTools.show_msg_dlg(kind="error", message="No Operating Systems have "
                                     + "had entries created for them! If you canceled creating "
                                     + "the entries, please reboot WxFixBoot and select only the "
                                     + "option 'Update Bootloader Config'. If you didn't do that, "
                                     + "and WxFixBoot either couldn't create them, or you see "
                                     + "this error with no previous warnings, you may have to "
                                     + "create your own bootloader config. If you wish to, you "
                                     + "can email me directly via my Launchpad page "
                                     + "(www.launchpad.net/~hamishmb) with the contents of "
                                     + "/tmp/wxfixboot.log and I'll help you do that.")

        else:
            #Ask the user for a new default OS.
            defaultos_name = DialogTools.show_choice_dlg(message="The OS you previously selected "
                                                         + "as the default wasn't added to the "
                                                         + "boot menu. Please select a new OS you "
                                                         + "want to use as "
                                                         + BOOTLOADER_INFO[_os]["Settings"]["NewBootloader"]
                                                         + "'s Default OS. You are setting "
                                                         + "configuration for "+_os,
                                                         title="WxFixBoot - Select Default OS",
                                                         choices=completed_entries_list)

            logger.info("make_lilo_os_entries(): User selected new default OS: "+defaultos_name
                        + "...")

    #Make the entry for the default OS.
    logger.debug("make_lilo_os_entries(): Setting default OS...")

    for line in config_file:
        if 'default' in line and '=' in line and '#' not in line:
            logger.debug("make_lilo_os_entries(): Found default OS setting, setting it to "
                         + defaultos_name+"...")

            line = "default="+defaultos_name

        new_file_contents.append(line+"\n")

    #Write the finished lines to the file.
    logger.info("make_lilo_os_entries(): Writing finished config to file...")
    CoreTools.write_privileged_file(filetoopen, ''.join(new_file_contents))

    logger.info("make_lilo_os_entries(): Done!")

def assemble_lilo_menu_entry(os_name, _os, kernel_options, new_file_contents):
    """Create a LILO menu entry in the config file, and return it"""
    #Set kernel and initrd.
    logger.info("assemble_lilo_menu_entry(): Adding /vmlinuz to the config file...")
    new_file_contents.append("\nimage=/vmlinuz\n")

    logger.info("assemble_lilo_menu_entry(): Adding /initrd.img to the config file...")
    new_file_contents.append("\tinitrd=/initrd.img\n")

    #Set the root device.
    #Use UUID's here if we can.
    logger.debug("assemble_lilo_menu_entry(): Setting OS rootfs as a UUID if possible...")

    if DISK_INFO[OS_INFO[_os]["Partition"]]["UUID"] == "Unknown":
        logger.warning("assemble_lilo_menu_entry(): Setting OS rootfs to "
                       + OS_INFO[_os]["Partition"]+"! This might not work cos it can change!")

        new_file_contents.append("\troot="+OS_INFO[_os]["Partition"]+"\n")

    else:
        logger.debug("assemble_lilo_menu_entry(): Setting OS rootfs to "
                     + DISK_INFO[OS_INFO[_os]["Partition"]]["UUID"]+"...")

        if BOOTLOADER_INFO[_os]["Settings"]["NewBootloader"] == "ELILO":
            new_file_contents.append("\troot=UUID="+DISK_INFO[OS_INFO[_os]["Partition"]]["UUID"]
                                     + "\n")

        else:
            new_file_contents.append("\troot=\"UUID="+DISK_INFO[OS_INFO[_os]["Partition"]]["UUID"]
                                     + "\"\n")

    #Set the label.
    logger.debug("assemble_lilo_menu_entry(): Setting OS label to "+os_name+"...")
    new_file_contents.append("\tlabel="+os_name+"\n")

    #Set the kernel options.
    logger.debug("assemble_lilo_menu_entry(): Setting OS Kernel Options to "+kernel_options+"...")
    new_file_contents.append("\tappend=\""+kernel_options+"\"\n")

    #Set one other necessary boot option.
    logger.debug("assemble_lilo_menu_entry(): Adding 'read-only' to mount rootfs in ro mode on "
                 + "startup...")

    new_file_contents.append("\tread-only\n")

    return new_file_contents

def install_lilo_to_mbr(use_chroot, mount_point):
    """Install LILO into the MBR."""
    cmd = "lilo"

    if use_chroot:
        cmd = "chroot "+mount_point+" "+cmd

    retval = CoreTools.start_process(cmd, show_output=False, privileged=True)

    #Return the return value.
    return retval

def install_elilo_to_partition(_os, package_manager, use_chroot, mount_point):
    """Install ELILO to the EFI/UEFI Partition"""
    #Okay, we've modified the kernel options and the timeout. Now we need to install grub to the
    #UEFI partition.
    if package_manager == "apt-get":
        cmd = "elilo -b "+BOOTLOADER_INFO[_os]["BootDisk"]+" --efiboot"

    if use_chroot:
        cmd = "chroot "+mount_point+" "+cmd

    retval = CoreTools.start_process(cmd, show_output=False, privileged=True)

    #Return the return value.
    return retval
