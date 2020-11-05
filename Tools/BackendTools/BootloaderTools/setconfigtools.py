#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Bootloader Configuration Setting Tools in the Bootloader Tools Package in the Backend Tools
# package for WxFixBoot
# This file is part of WxFixBoot.
# Copyright (C) 2013-2020 Hamish McIntyre-Bhatty
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

#Import modules.
import sys
import logging

#Import other modules.
sys.path.append('../../..') #Need to be able to import the Tools module from here.
import Tools.coretools as CoreTools #pylint: disable=wrong-import-position
import Tools.dialogtools as DialogTools #pylint: disable=wrong-import-position
from Tools.dictionaries import BOOTLOADER_INFO #pylint: disable=wrong-import-position
from .. import helpers as HelperBackendTools #pylint: disable=wrong-import-position

#Set up logging.
logger = logging.getLogger(__name__)
logger.setLevel(logging.getLogger("WxFixBoot").getEffectiveLevel())

def set_grub2_config(_os, filetoopen, bootloader_timeout, kernel_options, package_manager):
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
                                 + " has detected! As a fallback, the first "
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
                         + str(bootloader_timeout)+"'...")

            set_timeout = True
            line = "GRUB_TIMEOUT="+str(bootloader_timeout)

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

        #Comment out the GRUB_CMDLINE_LINUX line, unless on Fedora.
        elif 'GRUB_CMDLINE_LINUX' in line and 'GRUB_CMDLINE_LINUX_DEFAULT' not in line \
            and '=' in line and '#' not in line:

            if package_manager == "apt-get":
                logger.debug("set_grub2_config(): Commenting out GRUB_CMDLINE_LINUX...")
                line = "#"+line

            elif package_manager == "dnf":
                #Found it! Set it to the options in kernel_options, carefully making sure we aren't
                #double-quoting it.
                logger.debug("set_grub2_config(): Found GRUB_CMDLINE_LINUX, setting it to '"
                             + kernel_options+"'...")

                set_kernel_options = True
                line = "GRUB_CMDLINE_LINUX='"+kernel_options+"'"

        new_file_contents.append(line+"\n")

    #Check that everything was set. If not, write that config now.
    if set_timeout is False:
        logger.debug("set_grub2_config(): Didn't find GRUB_TIMEOUT in config file. "
                     + "Creating and setting it to '"+str(bootloader_timeout)+"'...")

        new_file_contents.append("GRUB_TIMEOUT="+str(bootloader_timeout)+"\n")

    if set_kernel_options is False:
        temp = kernel_options.replace('\"', '').replace("\'", "").replace("\n", "")
        logger.debug("set_grub2_config(): Didn't find GRUB_CMDLINE_LINUX_DEFAULT in config file. "
                     + "Creating and setting it to '"+kernel_options+"'...")

        if package_manager == "apt-get":
            new_file_contents.append("GRUB_CMDLINE_LINUX_DEFAULT='"+temp+"'\n")

        elif package_manager == "dnf":
            new_file_contents.append("GRUB_CMDLINE_LINUX='"+temp+"'\n")

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

    elif package_manager == "dnf":
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

    elif package_manager == "dnf":
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

    elif package_manager == "dnf" and BOOTLOADER_INFO[_os]["Settings"]["NewBootloader"] == "GRUB2":
        cmd = "grub2-mkconfig -o /boot/grub2/grub.cfg"

    elif package_manager == "dnf":
        cmd = "grub2-mkconfig -o /boot/efi/EFI/fedora/grub.cfg"

    if use_chroot:
        cmd = "chroot "+mount_point+" "+cmd

    retval = CoreTools.start_process(cmd, show_output=False, privileged=True)

    #Return the return value.
    return retval
