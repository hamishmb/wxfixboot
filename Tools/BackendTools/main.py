#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Main Backend Tools in the BackendTools Package for WxFixBoot
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
This module contains the functions for the main operations WxFixBoot performs:
updating, removing, and installing/reinstalling bootloaders. It also includes
high-level functions for setting bootloader configuration.
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
import time
import logging
import wx

#Import other modules.
sys.path.append('../..') #Need to be able to import the Tools module from here.
import Tools.coretools as CoreTools #pylint: disable=wrong-import-position
import Tools.dialogtools as DialogTools #pylint: disable=wrong-import-position
from Tools.dictionaries import * #pylint: disable=wrong-import-position
import Tools.StartupTools.getbootloaderconfigtools as BootloaderConfigObtainingTools #pylint: disable=wrong-import-position
from . import essentials as EssentialBackendTools #pylint: disable=wrong-import-position
from . import helpers as HelperBackendTools #pylint: disable=wrong-import-position
from . import BootloaderTools #pylint: disable=wrong-import-position
BootloaderConfigSettingTools = BootloaderTools.setconfigtools

#Make unicode an alias for str in Python 3.
if sys.version_info[0] == 3:
    unicode = str #pylint: disable=redefined-builtin,invalid-name
    str = bytes #pylint: disable=redefined-builtin,invalid-name

#Set up logging.
logger = logging.getLogger(__name__)
logger.setLevel(logging.getLogger("WxFixBoot").getEffectiveLevel())

#Silence other errors.
Operations = []

def manage_bootloader(_os):
    """Manage the installation and removal of each bootloader."""
    #Test the internet connection.
    wx.CallAfter(wx.GetApp().TopWindow.update_current_operation_text,
                 message="Checking the Internet Connection...")

    wx.CallAfter(wx.GetApp().TopWindow.update_output_box,
                 "\n###Checking the Internet Connection...###\n")

    EssentialBackendTools.check_internet_connection()

    wx.CallAfter(wx.GetApp().TopWindow.update_current_operation_text,
                 message="Finished checking the Internet Connection...")

    wx.CallAfter(wx.GetApp().TopWindow.update_output_box,
                 "\n###Finished checking the Internet Connection...###\n")

    #Don't do anything if bootloader operations have been disabled.
    if SYSTEM_INFO["DisableBootloaderOperations"]:
        logger.info("manage_bootloader(): Bootloader operations have been disabled, "
                    + "skipping this operation...")

        wx.CallAfter(wx.GetApp().TopWindow.update_current_progress, 100)
        wx.CallAfter(wx.GetApp().TopWindow.update_output_box,
                     "\n###Skipped bootloader operations for "+_os+"...###\n")

        return True

    if BOOTLOADER_INFO[_os]["Settings"]["Reinstall"] or BOOTLOADER_INFO[_os]["Settings"]["Update"]:
        BOOTLOADER_INFO[_os]["Settings"]["NewBootloader"] = BOOTLOADER_INFO[_os]["Bootloader"]

    #Create a list of functions to call.
    function_list = [set_new_bootloader_config]

    if BOOTLOADER_INFO[_os]["Settings"]["Reinstall"] \
        or BOOTLOADER_INFO[_os]["Settings"]["InstallNewBootloader"]:

        #Add more stuff to the list.
        function_list = [remove_old_bootloader, install_new_bootloader, set_new_bootloader_config]

    #Safegaurd operations using a loop.
    for function in function_list:
        logger.info("manage_bootloader(): Calling "+unicode(function)+"...")

        success = False

        #Allow the user to keep trying if stuff goes wrong.
        while success is False:
            #Create some text.
            if function == remove_old_bootloader:
                operation = "remove"

            elif function == install_new_bootloader:
                operation = "install"

            else:
                operation = "configure"

            success = function(_os)

            #Warn user if an error occured.
            if success is False:
                logger.error("manage_bootloader(): Failed to "+operation+" "+_os
                             + "'s old bootloader! Asking user whether to try again or skip "
                             + "this OS...")

                #Drop a leading 'e' for correct English.
                if operation[-1] == "e":
                    operation = operation[0:-1]

                result = DialogTools.show_yes_no_dlg(message="An error occured while "+operation
                                                     + "ing "+_os+"'s bootloader! This operating "
                                                     + "system may currently be in an unbootable "
                                                     + "state. What do you want to do? Click Yes "
                                                     + "to try again, and click No to cancel "
                                                     + "bootloader operations for this OS.",
                                                     title="WxFixBoot - Error "+operation
                                                     + "ing Bootloader!",
                                                     buttons=("Try Again",
                                                              "Skip Bootloader Operations "
                                                              + "For This OS"))

                if result:
                    logger.info("manage_bootloader(): Trying again and checking internet "
                                + "connection again...")

                    EssentialBackendTools.check_internet_connection()

                    #Don't do anything if bootloader operations have been disabled.
                    if SYSTEM_INFO["DisableBootloaderOperations"]:
                        logger.info("manage_bootloader(): Bootloader operations have been "
                                    + "disabled, skipping this operation...")

                        wx.CallAfter(wx.GetApp().TopWindow.update_current_progress, 100)
                        wx.CallAfter(wx.GetApp().TopWindow.update_output_box,
                                     "\n###Skipped bootloader operations for "+_os+"...###\n")

                        return True

                else:
                    logger.error("manage_bootloader(): Skipping the rest of the bootloader "
                                 + "operations for "+_os+"! Other operations will continue "
                                 + "as normal. Returning False...")

                    wx.CallAfter(wx.GetApp().TopWindow.update_current_progress, 100)
                    return False

    logger.info("manage_bootloader(): Done!")

def remove_old_bootloader(_os):
    """Remove the currently installed bootloader."""
    logger.info("remove_old_bootloader(): Removing "+BOOTLOADER_INFO[_os]["Bootloader"]+" from "
                + _os+"...")

    wx.CallAfter(wx.GetApp().TopWindow.update_current_progress, 27)
    wx.CallAfter(wx.GetApp().TopWindow.update_current_operation_text,
                 message="Removing "+BOOTLOADER_INFO[_os]["Bootloader"]+" from "+_os+"......")

    wx.CallAfter(wx.GetApp().TopWindow.update_output_box,
                 "\n###Removing "+BOOTLOADER_INFO[_os]["Bootloader"]+" from "+_os+"...###\n")

    #If this is the current OS, let the remover function know that we aren't using chroot.
    if OS_INFO[_os]["IsCurrentOS"]:
        logger.debug("remove_old_bootloader(): Modifying current OS so not using chroot...")
        use_chroot, unmount_after, mount_point = (False, False, "")

    else:
        logger.debug("remove_old_bootloader(): Using chroot to modify another OS...")
        use_chroot = True
        mount_point = "/tmp/wxfixboot/mountpoints"+OS_INFO[_os]["Partition"]

        #Check if the partition is mounted.
        unmount_after = not CoreTools.is_mounted(OS_INFO[_os]["Partition"], mount_point)

        if unmount_after:
            #Mount the partition using the global mount function.
            if CoreTools.mount_partition(partition=OS_INFO[_os]["Partition"],
                                         mount_point=mount_point) != 0:

                logger.error("remove_old_bootloader(): Failed to mount "+OS_INFO[_os]["Partition"]
                             + "! Warning the user and giving up...")

                DialogTools.show_msg_dlg(kind="error",
                                         message="WxFixBoot failed to mount the partition "
                                         + "containing "+_os+"! Giving up. You will be prompted "
                                         + "to try again if you wish.")

                return False

        #Set up chroot.
        if CoreTools.setup_chroot(mount_point) != 0:
            logger.error("remove_old_bootloader(): Failed to set up chroot at "+mount_point
                         + "! Giving up...")

            DialogTools.show_msg_dlg(kind="error",
                                     message="WxFixBoot failed to set up a chroot for "+_os
                                     + "! Giving up. You will be prompted to try again if "
                                     + "you wish.")
            return False

    #Mount a /boot partition if it exists.
    if OS_INFO[_os]["BootPartition"] != "Unknown":
        if CoreTools.mount_partition(OS_INFO[_os]["BootPartition"], mount_point+"/boot") != 0:
            logger.error("remove_old_bootloader(): Failed to mount "+_os+"'s /boot partition! "
                         + "Skipping bootloader removal for this OS.")

            DialogTools.show_msg_dlg(kind="error",
                                     message="WxFixBoot failed to mount the partition containing "
                                     + _os+"'s /boot partition! Giving up. You will be prompted "
                                     + "to try again if you wish.")

            if not OS_INFO[_os]["IsCurrentOS"]:
                CoreTools.teardown_chroot(mount_point)
                CoreTools.unmount(mount_point)

            return False

    #Mount the UEFI partition at mount_point/boot/efi, if it exists.
    if OS_INFO[_os]["EFIPartition"] != "Unknown":
        if CoreTools.mount_partition(partition=OS_INFO[_os]["EFIPartition"],
                                     mount_point=mount_point+"/boot/efi") != 0:
            logger.error("remove_old_bootloader(): Failed to mount "+OS_INFO[_os]["EFIPartition"]
                         + "! to "+mount_point+"/boot/efi! Aborting bootloader installation and "
                         + "warning user...")

            DialogTools.show_msg_dlg(kind="error",
                                     message="WxfixBoot failed to mount the partition containing "
                                     + _os+"'s EFI partition! Giving up. You will be prompted to "
                                     + "try again if you wish.")

            return False

    #Wait until no other application is using APT/YUM.
    #Let user know what's happening.
    wx.CallAfter(wx.GetApp().TopWindow.update_current_progress, 27)
    wx.CallAfter(wx.GetApp().TopWindow.update_current_operation_text, message="Waiting until "+_os
                 + "'s package manager is free.\nClose any open applications if this "
                 + "message persists...")

    wx.CallAfter(wx.GetApp().TopWindow.update_output_box,
                 "\n###Waiting until "+_os+"'s package manager is free...###\n")

    logger.debug("remove_old_bootloader(): Waiting until "+_os+"'s package manager is free...")
    HelperBackendTools.wait_until_packagemanager_free(mount_point=mount_point,
                                                      package_manager=\
                                                      OS_INFO[_os]["PackageManager"])

    wx.CallAfter(wx.GetApp().TopWindow.update_current_progress, 27)
    wx.CallAfter(wx.GetApp().TopWindow.update_current_operation_text,
                 message="Removing "+BOOTLOADER_INFO[_os]["Bootloader"]+" from "+_os+"...")

    wx.CallAfter(wx.GetApp().TopWindow.update_output_box,
                 "\n###Removing "+BOOTLOADER_INFO[_os]["Bootloader"]+" from "+_os+"...###\n")

    #Remove the bootloader.
    if BOOTLOADER_INFO[_os]["Bootloader"] == "GRUB2":
        logger.info("remove_old_bootloader(): Removing GRUB2...")

        if OS_INFO[_os]["PackageManager"] == "apt-get":
            cmd = "sh -c 'DEBIAN_FRONTEND=noninteractive apt-get purge -y " \
                  "grub-pc grub-pc-bin grub-common'"

        elif OS_INFO[_os]["PackageManager"] == "yum":
            cmd = "yum -y remove grub2"

    elif BOOTLOADER_INFO[_os]["Bootloader"] == "LILO":
        logger.info("remove_old_bootloader(): Removing LILO...")

        if OS_INFO[_os]["PackageManager"] == "apt-get":
            cmd = "sh -c 'DEBIAN_FRONTEND=noninteractive apt-get purge -y lilo'"

        elif OS_INFO[_os]["PackageManager"] == "yum":
            cmd = "echo 'ERROR: LILO not available on Fedora or derivatives. Continuing anyway...'"

    elif BOOTLOADER_INFO[_os]["Bootloader"] == "GRUB-UEFI":
        logger.info("remove_old_bootloader(): Removing GRUB-UEFI...")

        if OS_INFO[_os]["PackageManager"] == "apt-get":
            cmd = "sh -c 'DEBIAN_FRONTEND=noninteractive apt-get purge -y " \
                  "grub-efi grub-efi-amd64 grub-efi-amd64-bin grub-efi-ia32 " \
                  "grub-efi-ia32-bin grub-common grub2-common'"

        elif OS_INFO[_os]["PackageManager"] == "yum":
            cmd = "yum -y remove grub2-efi-x64 grub2-efi-ia32 shim-x64"

    elif BOOTLOADER_INFO[_os]["Bootloader"] == "ELILO":
        logger.info("remove_old_bootloader(): Removing ELILO...")

        if OS_INFO[_os]["PackageManager"] == "apt-get":
            cmd = "sh -c 'DEBIAN_FRONTEND=noninteractive apt-get purge -y elilo'"

        elif OS_INFO[_os]["PackageManager"] == "yum":
            cmd = "echo 'ERROR: ELILO not available on Fedora or derivatives. " \
                  "Continuing anyway...'"

    else:
        #Bootloader is unknown. Just output a warning message.
        logger.warning("remove_old_bootloader(): Cannot remove unknown bootloader! "
                       + "Continuing anyway...")

        cmd = "echo 'WARNING: Bootloader is " \
              "unknown, cannot remove. Continuing anyway...'"

    if use_chroot:
        cmd = "chroot "+mount_point+" "+cmd

    retval = CoreTools.start_process(cmd, privileged=True)

    if retval != 0:
        logger.error("remove_old_bootloader(): Failed to remove "
                     + BOOTLOADER_INFO[_os]["Bootloader"]+" from "+_os+"! Warning user...")

        DialogTools.show_msg_dlg(kind="error", message="WxFixBoot failed to remove "
                                 + BOOTLOADER_INFO[_os]["Bootloader"]+" from "+_os+"!")
        return False

    #If there's a seperate EFI partition for this OS, make sure it's unmounted before removing
    #the chroot.
    if OS_INFO[_os]["EFIPartition"] != "Unknown":
        if CoreTools.unmount(mount_point+"/boot/efi") != 0:
            logger.error("remove_old_bootloader(): Failed to unmount "+mount_point
                         + "/boot/efi! This probably doesn't matter...")

    #unmount a /boot partition if it exists.
    if OS_INFO[_os]["BootPartition"] != "Unknown":
        if CoreTools.unmount(mount_point+"/boot") != 0:
            logger.error("remove_old_bootloader(): Failed to unmount "+_os
                         + "'s /boot partition! Continuing anyway...")

    #Tear down chroot if needed.
    if use_chroot:
        if CoreTools.teardown_chroot(mount_point=mount_point) != 0:
            logger.error("remove_old_bootloader(): Failed to remove chroot at "+mount_point
                         + "! Attempting to continue anyway...")

    #unmount partition if needed.
    if unmount_after:
        if CoreTools.unmount(mount_point) != 0:
            logger.error("remove_old_bootloader(): Couldn't unmount "+mount_point
                         + "! Continuing anyway...")

    wx.CallAfter(wx.GetApp().TopWindow.update_output_box,
                 "\n###Finished removing "+BOOTLOADER_INFO[_os]["Bootloader"]+" from "
                 +_os+"...###\n")

    if retval != 0:
        #Something went wrong! Log it and notify the user.
        logger.error("remove_old_bootloader(): Failed to remove "
                     + BOOTLOADER_INFO[_os]["Bootloader"]+" from "+_os
                     + "! We'll continue anyway. Warn the user.")

        DialogTools.show_msg_dlg(kind="error", message="WxFixBoot failed to remove "
                                 + BOOTLOADER_INFO[_os]["Bootloader"]+" from "+_os
                                 + "! This probably doesn't matter; when we install the new "
                                 + "bootloader, it should take precedence over the old one "
                                 + "anyway. Make sure you check that "+_os+" boots correctly "
                                 + "after WxFixBoot finishes its operations. Reinstalling the "
                                 + "bootloader again afterwards is recommended.")

    #Attempt to clear any stuck logical volumes that may have been created by os-prober.
    CoreTools.start_process("dmsetup remove_all -y", privileged=True)

    #Log and notify the user that we're finished removing bootloaders.
    logger.info("remove_old_bootloader(): Finished removing "+BOOTLOADER_INFO[_os]["Bootloader"]
                + "...")

    wx.CallAfter(wx.GetApp().TopWindow.update_current_operation_text,
                 message="Finished removing "+BOOTLOADER_INFO[_os]["Bootloader"]+" from "
                 +_os+"......")

    wx.CallAfter(wx.GetApp().TopWindow.update_current_progress, 50)
    DialogTools.show_msg_dlg(kind="info",
                             message="Finished removing "+BOOTLOADER_INFO[_os]["Bootloader"]
                             + "! WxFixBoot will now install "
                             + BOOTLOADER_INFO[_os]["Settings"]["NewBootloader"]+" to "+_os+".")

    return True

def install_new_bootloader(_os):
    """Install a new bootloader."""
    logger.info("install_new_bootloader(): Preparing to install "
                + BOOTLOADER_INFO[_os]["Settings"]["NewBootloader"]+" in "+_os+"...")

    wx.CallAfter(wx.GetApp().TopWindow.update_current_progress, 52)
    wx.CallAfter(wx.GetApp().TopWindow.update_output_box,
                 "\n###Preparing to install "+BOOTLOADER_INFO[_os]["Settings"]["NewBootloader"]
                 + " in "+_os+"...###\n")

    wx.CallAfter(wx.GetApp().TopWindow.update_current_operation_text,
                 message="Preparing to install "+BOOTLOADER_INFO[_os]["Settings"]["NewBootloader"]
                 + " in "+_os+"...")

    #If this is the current OS, let the installer functions know that we aren't using chroot.
    if OS_INFO[_os]["IsCurrentOS"]:
        logger.debug("install_new_bootloader(): Modifying current OS so not using chroot...")
        use_chroot, unmount_after, mount_point = (False, False, "")

    #Otherwise, setup the chroot and everything else first, and tell them we are using chroot,
    #and pass the mountpoint to them.
    else:
        logger.debug("install_new_bootloader(): Using chroot to modify another OS...")
        use_chroot = True
        mount_point = "/tmp/wxfixboot/mountpoints"+OS_INFO[_os]["Partition"]

        #Check if the partition is mounted.
        unmount_after = not CoreTools.is_mounted(OS_INFO[_os]["Partition"], mount_point)

        if unmount_after:
            if CoreTools.mount_partition(partition=OS_INFO[_os]["Partition"],
                                         mount_point=mount_point) != 0:
                logger.error("install_new_bootloader(): Failed to mount "+OS_INFO[_os]["Partition"]
                             + "! Warn the user and skip this OS.")

                DialogTools.show_msg_dlg(kind="error",
                                         message="WxFixBoot failed to mount the partition "
                                         + "containing "+_os+"! Bootloader installation cannot "
                                         + "continue! This may leave your system, or this OS, in "
                                         + "an unbootable state. Please close any open programs, "
                                         + "then try again when prompted.")

                return False

        #Set up chroot.
        if CoreTools.setup_chroot(mount_point=mount_point) != 0:
            logger.error("install_new_bootloader(): Failed to set up chroot at "+mount_point
                         + "! Warning user and giving up...")

            DialogTools.show_msg_dlg(kind="error",
                                     message="WxFixBoot failed to set up a chroot for "
                                     + _os+"! Giving up. You will be prompted to try again if "
                                     + "you wish.")
            return False

    #If there's a seperate /boot partition for this OS, make sure it's mounted.
    if OS_INFO[_os]["BootPartition"] != "Unknown":
        if CoreTools.mount_partition(partition=OS_INFO[_os]["BootPartition"],
                                     mount_point=mount_point+"/boot") != 0:
            logger.error("remove_old_bootloader(): Failed to mount "
                         + OS_INFO[_os]["BootPartition"]+"! Warn the user and skip this OS.")

            DialogTools.show_msg_dlg(kind="error",
                                     message="WxFixBoot failed to mount the partition "
                                     + "containing "+_os+"'s /boot partition! Giving up. "
                                     + "You will be prompted to try again if you wish.")

            return False

    #Update the package lists.
    if OS_INFO[_os]["PackageManager"] == "apt-get":
        cmd = "sh -c 'DEBIAN_FRONTEND=noninteractive apt-get update'"

    elif OS_INFO[_os]["PackageManager"] == "yum":
        cmd = "yum check-update"

    if use_chroot:
        cmd = "chroot "+mount_point+" "+cmd

    if CoreTools.start_process(cmd, privileged=True) not in (0, 100):
        logger.error("install_new_bootloader(): Failed to Update the Package Information! "
                     + "Continuing anyway...")

        DialogTools.show_msg_dlg(kind="error", message="WxfixBoot failed to update "+_os
                                 + "'s package information! Giving up. You will be prompted "
                                 + "to try again if you wish.")

        return False

    wx.CallAfter(wx.GetApp().TopWindow.update_current_operation_text,
                 message="Installing "+BOOTLOADER_INFO[_os]["Settings"]["NewBootloader"]
                 + " in "+_os+"...")

    wx.CallAfter(wx.GetApp().TopWindow.update_current_progress, 55)
    wx.CallAfter(wx.GetApp().TopWindow.update_output_box,
                 "\n###Installing "+BOOTLOADER_INFO[_os]["Settings"]["NewBootloader"]
                 + " in "+_os+"...###\n")

    #Install the bootloader.
    if BOOTLOADER_INFO[_os]["Settings"]["NewBootloader"] == "GRUB2":
        logger.info("install_new_bootloader(): Installing GRUB2...")

        if OS_INFO[_os]["PackageManager"] == "apt-get":
            cmd = "sh -c 'DEBIAN_FRONTEND=noninteractive apt-get install -y grub-pc os-prober'"

        elif OS_INFO[_os]["PackageManager"] == "yum":
            cmd = "yum -y install grub2"

    elif BOOTLOADER_INFO[_os]["Settings"]["NewBootloader"] == "LILO":
        logger.info("install_new_bootloader(): Installing LILO...")

        if OS_INFO[_os]["PackageManager"] == "apt-get":
            cmd = "sh -c 'DEBIAN_FRONTEND=noninteractive apt-get install -y lilo'"

        elif OS_INFO[_os]["PackageManager"] == "yum":
            cmd = "echo 'ERROR: LILO not available on Fedora or derivatives. Continuing anyway...'"

    elif BOOTLOADER_INFO[_os]["Settings"]["NewBootloader"] == "GRUB-UEFI":
        logger.info("install_new_bootloader(): Installing GRUB-UEFI...")

        #Mount the UEFI partition at mount_point/boot/efi.
        if CoreTools.mount_partition(partition=OS_INFO[_os]["EFIPartition"],
                                     mount_point=mount_point+"/boot/efi") != 0:

            logger.error("install_new_bootloader(): Failed to mount "+OS_INFO[_os]["EFIPartition"]
                         + " to "+mount_point+"/boot/efi! Aborting bootloader installation and "
                         + "warning user...")

            DialogTools.show_msg_dlg(kind="error",
                                     message="WxfixBoot failed to mount the partition containing "
                                     + _os+"'s EFI partition! Giving up. You will be prompted to "
                                     + "try again if you wish.")

            return False

        if OS_INFO[_os]["PackageManager"] == "apt-get":
            cmd = "sh -c 'DEBIAN_FRONTEND=noninteractive apt-get install -y grub-efi os-prober'"

        elif OS_INFO[_os]["PackageManager"] == "yum":
            cmd = "yum -y install grub2-efi-ia32 grub2-efi-x64 shim-x64 " \
                  "fwupdate-efi fwupdate-libs"

    elif BOOTLOADER_INFO[_os]["Settings"]["NewBootloader"] == "ELILO":
        logger.info("install_new_bootloader(): Installing ELILO...")

        #unmount the UEFI Partition now, and update the mtab inside chroot (if using chroot).
        if CoreTools.unmount(OS_INFO[_os]["EFIPartition"]) != 0:
            logger.error("install_new_bootloader(): Failed to unmount the EFI partition! Giving "
                         + "up and warning user...")

            DialogTools.show_msg_dlg(message="Couldn't unmount "+_os+"'s EFI partition! "
                                     + "Giving up. You will be prompted to try again if you wish.",
                                     kind="error")

            return False

        if use_chroot:
            CoreTools.update_chroot_mtab(mount_point=mount_point)

        if OS_INFO[_os]["PackageManager"] == "apt-get":
            cmd = "sh -c 'DEBIAN_FRONTEND=noninteractive apt-get install -y elilo'"

        elif OS_INFO[_os]["PackageManager"] == "yum":
            cmd = "echo 'ERROR: ELILO not available on Fedora or derivatives. " \
                  "Continuing anyway...'"

    if use_chroot:
        cmd = "chroot "+mount_point+" "+cmd

    retval = CoreTools.start_process(cmd, privileged=True)

    if retval != 0:
        logger.error("install_new_bootloader(): Failed to install new bootloader. Warn user...")
        DialogTools.show_msg_dlg(kind="error", message="WxfixBoot failed to install "+_os
                                 + "'s new bootloader! Continuing anyway...")

    #If there's a seperate EFI partition for this OS, make sure it's unmounted before removing
    #the chroot.
    if OS_INFO[_os]["EFIPartition"] != "Unknown":
        if CoreTools.unmount(mount_point+"/boot/efi") != 0:
            logger.error("install_new_bootloader(): Failed to unmount "+mount_point
                         + "/boot/efi! This probably doesn't matter...")

    #If there's a seperate /boot partition for this OS, make sure it's unmounted before
    #removing the chroot.
    if OS_INFO[_os]["BootPartition"] != "Unknown":
        if CoreTools.unmount(mount_point+"/boot") != 0:
            logger.error("install_new_bootloader(): Failed to unmount "+mount_point
                         + "/boot! This probably doesn't matter...")

    if use_chroot:
        logger.debug("install_new_bootloader(): Removing chroot...")

        #Tear down chroot.
        if CoreTools.teardown_chroot(mount_point=mount_point) != 0:
            logger.error("install_new_bootloader(): Failed to remove chroot at "+mount_point
                         + "! Attempting to continue anyway...")

    if unmount_after:
        if CoreTools.unmount(mount_point) != 0:
            logger.error("install_new_bootloader(): Failed to unmount "+mount_point
                         + "! Continuing anyway...")

    if retval != 0:
        #Something went wrong! Log it and notify the user.
        logger.error("install_new_bootloader(): Failed to install "
                     + BOOTLOADER_INFO[_os]["Settings"]["NewBootloader"]+" in "+_os
                     + "! This may mean the system (or this OS) is now unbootable! "
                     + "Warning the user and asking to try again.")

        DialogTools.show_msg_dlg(kind="error", message="WxFixBoot failed to install "
                                 + BOOTLOADER_INFO[_os]["Settings"]["NewBootloader"]+" in "+_os
                                 + "! This may leave this OS, or your system, in an unbootable "
                                 + "state. You will now be prompted to try again.")

        return False

    wx.CallAfter(wx.GetApp().TopWindow.update_output_box, "\n###Finished installing "
                 + BOOTLOADER_INFO[_os]["Settings"]["NewBootloader"]+" in "+_os+"...###\n")

    #Attempt to clear any stuck logical volumes that may have been created by os-prober.
    CoreTools.start_process("dmsetup remove_all -y", privileged=True)

    #Log and notify the user that we're finished installing the bootloader.
    logger.info("install_new_bootloader(): Finished installing "
                + BOOTLOADER_INFO[_os]["Settings"]["NewBootloader"]+"...")

    wx.CallAfter(wx.GetApp().TopWindow.update_current_operation_text, message="Finish installing "
                 + BOOTLOADER_INFO[_os]["Settings"]["NewBootloader"]+" in "+_os+"...")

    wx.CallAfter(wx.GetApp().TopWindow.update_current_progress, 75)
    return True

def set_new_bootloader_config(_os):
    """Manage setting new bootloader config."""
    logger.info("set_new_bootloader_config(): Setting "
                + BOOTLOADER_INFO[_os]["Settings"]["NewBootloader"]+"'s config for "+_os+"...")

    wx.CallAfter(wx.GetApp().TopWindow.update_current_operation_text, message="Setting "
                 + BOOTLOADER_INFO[_os]["Settings"]["NewBootloader"]+" config for "+_os+"...")

    wx.CallAfter(wx.GetApp().TopWindow.update_current_progress, 79)
    wx.CallAfter(wx.GetApp().TopWindow.update_output_box, "\n###Setting "
                 + BOOTLOADER_INFO[_os]["Settings"]["NewBootloader"]+"'s config for "+_os
                 + "...###\n")

    #If this is the current OS, let the config functions know that we aren't using chroot.
    if OS_INFO[_os]["IsCurrentOS"]:
        logger.debug("set_new_bootloader_config(): We're modifying the current OS...")
        #If so, make sure this will work for this OS too, and avoid setting mountpoint, so the
        #config instructions below look in the right place for the config files.
        use_chroot, unmount_after, mount_point = (False, False, "")

    else:
        logger.debug("set_new_bootloader_config(): We're modifying another OS...")
        use_chroot = True
        mount_point = "/tmp/wxfixboot/mountpoints"+OS_INFO[_os]["Partition"]

        #Check if the partition is mounted.
        unmount_after = not CoreTools.is_mounted(OS_INFO[_os]["Partition"], mount_point)

        if unmount_after:
            #Mount the partition.
            if CoreTools.mount_partition(partition=OS_INFO[_os]["Partition"],
                                         mount_point=mount_point) != 0:
                #Ignore this partition.
                logger.warning("set_new_bootloader_config(): Failed to mount "
                               + OS_INFO[_os]["Partition"]+"! Giving up...")

                return False

        #Set up chroot.
        if CoreTools.setup_chroot(mount_point=mount_point) != 0:
            logger.error("set_new_bootloader_config(): Failed to set up chroot at "+mount_point
                         + "! Giving up...")

            DialogTools.show_msg_dlg(kind="error",
                                     message="WxFixBoot failed to set up a chroot for "+_os
                                     + "! Giving up. You will be prompted to try again if "
                                     + "you wish.")

            return False

        wx.CallAfter(wx.GetApp().TopWindow.update_current_progress, 81)

    #Mount a /boot partition if it exists.
    if OS_INFO[_os]["BootPartition"] != "Unknown":
        if CoreTools.mount_partition(OS_INFO[_os]["BootPartition"], mount_point+"/boot") != 0:
            logger.error("set_new_bootloader_config(): Failed to mount "+_os
                         + "'s /boot partition! Skipping bootloader config setting for this OS.")

            if not OS_INFO[_os]["IsCurrentOS"]:
                CoreTools.teardown_chroot(mount_point)
                CoreTools.unmount(mount_point)

            return False

    #If there's a seperate EFI partition for this OS, make sure it's mounted.
    if OS_INFO[_os]["EFIPartition"] != "Unknown":
        if CoreTools.mount_partition(partition=OS_INFO[_os]["EFIPartition"],
                                     mount_point=mount_point+"/boot/efi") != 0:
            logger.error("remove_old_bootloader(): Failed to mount "+OS_INFO[_os]["EFIPartition"]
                         + "! Warn the user and skip this OS.")

            DialogTools.show_msg_dlg(kind="error",
                                     message="WxFixBoot failed to mount the partition containing "
                                     + _os+"'s EFI partition! Giving up. You will be prompted to "
                                     + "try again if you wish.")

            return False

    #On GRUB2, get the new menuentries so we can set the default OS.
    logger.info("set_new_bootloader_config(): Reading GRUB2's menu entries to set default OS...")

    if BOOTLOADER_INFO[_os]["Settings"]["NewBootloader"] in ("GRUB2", "GRUB-UEFI"):
        #Update GRUB.
        logger.info("set_new_bootloader_config(): Updating GRUB2 Configuration...")
        BootloaderConfigSettingTools.update_grub2(_os=_os,
                                                  package_manager=OS_INFO[_os]["PackageManager"],
                                                  use_chroot=use_chroot, mount_point=mount_point)

        BOOTLOADER_INFO[_os]["NewMenuEntries"] = \
        BootloaderConfigObtainingTools.parse_grub2_menu_data(menu_data="",
                                                             mount_point=mount_point)[1]

    #Look for the configuration file, based on which SetConfig() function we're about to run.
    if BOOTLOADER_INFO[_os]["Settings"]["NewBootloader"] in ("GRUB2", "GRUB-UEFI"):
        #Check mount_point/etc/default/grub exists.
        if os.path.isfile(mount_point+"/etc/default/grub"):
            #It does, we'll run the function to set the config now.
            logger.info("set_new_bootloader_config(): Setting GRUB2 Configuration...")
            BootloaderConfigSettingTools.set_grub2_config(_os=_os, filetoopen=mount_point
                                                          + "/etc/default/grub",
                                                          bootloader_timeout=BOOTLOADER_INFO[_os]["Settings"]["NewTimeout"],
                                                          kernel_options=BOOTLOADER_INFO[_os]["Settings"]["NewKernelOptions"])

        if BOOTLOADER_INFO[_os]["Settings"]["NewBootloader"] == "GRUB-UEFI":
            #Mount the UEFI partition at mount_point/boot/efi.
            if CoreTools.mount_partition(partition=OS_INFO[_os]["EFIPartition"],
                                         mount_point=mount_point+"/boot/efi") != 0:
                logger.error("set_new_bootloader_config(): Couldn't mount EFI partition "
                             + OS_INFO[_os]["EFIPartition"]+" to install bootloader! Giving up "
                             + "and warning user...")

                DialogTools.show_msg_dlg(kind="error", message="WxFixBoot failed to mount "+_os
                                         + "'s EFI partition! You will now be promtped to give "
                                         + "up or try again.")

                return False

            #Now Install GRUB-UEFI to the UEFI Partition.
            logger.info("set_new_bootloader_config(): Installing GRUB-UEFI to "
                        + OS_INFO[_os]["EFIPartition"]+"...")

            BootloaderConfigSettingTools.install_grub2_to_efi_partition(package_manager=OS_INFO[_os]["PackageManager"],
                                                                        mount_point=mount_point,
                                                                        use_chroot=use_chroot,
                                                                        uefi_system_partition_mount_point="/boot/efi",
                                                                        arch=OS_INFO[_os]["Arch"])

        else:
            #Now Install GRUB2 to the MBR.
            logger.info("set_new_bootloader_config(): Installing GRUB2 to "
                        + DISK_INFO[OS_INFO[_os]["Partition"]]["HostDevice"]+"...")

            BootloaderConfigSettingTools.install_grub2_to_mbr(package_manager=OS_INFO[_os]["PackageManager"],
                                                              use_chroot=use_chroot,
                                                              mount_point=mount_point,
                                                              device=DISK_INFO[OS_INFO[_os]["Partition"]]["HostDevice"])

        #Update GRUB.
        logger.info("set_new_bootloader_config(): Updating GRUB2 Configuration...")
        BootloaderConfigSettingTools.update_grub2(_os=_os,
                                                  package_manager=OS_INFO[_os]["PackageManager"],
                                                  use_chroot=use_chroot, mount_point=mount_point)

        if BOOTLOADER_INFO[_os]["Settings"]["NewBootloader"] == "GRUB-UEFI":
            #Make an entry in fstab for the UEFI Partition, if needed.
            HelperBackendTools.write_fstab_entry_for_uefi_partition(_os=_os,
                                                                    mount_point=mount_point)

            #Copy and backup EFI files where needed.
            HelperBackendTools.backup_uefi_files(mount_point=mount_point)
            HelperBackendTools.manage_uefi_files(_os=_os, mount_point=mount_point)

        if BOOTLOADER_INFO[_os]["Settings"]["NewBootloader"] == "GRUB-UEFI" \
            and OS_INFO[_os]["PackageManager"] == "yum":

            #If we're switching to GRUB-UEFI from BIOS it can mess up GRUB2 and change the boot
            #commands to linux and initrd instead of linuxefi and initrdefi, preventing boot.
            #Fix this. The next time GRUB is updated from within the OS it will fix itself.
            logger.info("set_new_bootloader_config(): Fixing Fedora's GRUB2-UEFI config (when "
                        + "booted with BIOS, it can go wrong)...")

            logger.info("set_new_bootloader_config(): Finding and opening GRUB config file...")

            #Find grub.cfg. (Ubuntu).
            if os.path.isdir(mount_point+"/boot/grub"):
                grub_dir = mount_point+"/boot/grub"

            #(Fedora, EFI)
            elif os.path.isdir(mount_point+"/boot/efi/EFI/fedora"):
                grub_dir = mount_point+"/boot/efi/EFI/fedora"

            #Correct the commands if needed.
            config = CoreTools.read_privileged_file(grub_dir+"/grub.cfg")

            new_config = []

            for line in config:
                if "linux16" in line and "/vmlinu" in line:
                    new_config.append(line.replace("linux16", "linuxefi")+"\n")

                elif "linux" in line and "linuxefi" not in line and "/vmlinu" in line:
                    new_config.append(line.replace("linux", "linuxefi")+"\n")

                elif "initrd16" in line and ("/initrd" in line or "/initramfs" in line):
                    new_config.append(line.replace("initrd16", "initrdefi")+"\n")

                elif "initrd" in line and "initrdefi" not in line \
                    and ("/initrd" in line or "/initramfs" in line):

                    new_config.append(line.replace("initrd", "initrdefi")+"\n")

                else:
                    new_config.append(line+"\n")

            #Write the fixed config.
            CoreTools.write_privileged_file(grub_dir+"/grub.cfg", ''.join(new_config))

            #unmount the EFI partition.
            if CoreTools.unmount(OS_INFO[_os]["EFIPartition"]) != 0:
                logger.error("set_new_bootloader_config(): Couldn't unmount EFI partition! "
                             + "This probably won't matter, so we'll continue anyway...")

            logger.info("set_new_bootloader_config(): Done!")

        elif BOOTLOADER_INFO[_os]["Settings"]["NewBootloader"] == "GRUB2" \
            and OS_INFO[_os]["PackageManager"] == "yum":

            #If we're switching to GRUB2 from UEFI it can mess up GRUB2 and change the boot
            #commands to linuxefi and initrdefi instead of linux and initrd, preventing boot.
            #Fix this. The next time GRUB is updated from within the OS it will fix itself.
            logger.info("set_new_bootloader_config(): Fixing Fedora's GRUB2-BIOS config (when "
                        + "booted with EFI, it can go wrong)...")

            logger.info("set_new_bootloader_config(): Finding and opening GRUB config file...")

            #Find grub.cfg. (Ubuntu).
            if os.path.isdir(mount_point+"/boot/grub"):
                grub_dir = mount_point+"/boot/grub"

            #(Fedora, BIOS)
            elif os.path.isdir(mount_point+"/boot/grub2"):
                grub_dir = mount_point+"/boot/grub2"

            #Correct the commands if needed.
            config = CoreTools.read_privileged_file(grub_dir+"/grub.cfg")

            new_config = []

            for line in config:
                new_config.append(line.replace("linuxefi", "linux")\
                .replace("initrdefi", "initrd")+"\n")

            #Write the fixed config.
            CoreTools.write_privileged_file(grub_dir+"/grub.cfg", ''.join(new_config))

            logger.info("set_new_bootloader_config(): Done!")

    elif BOOTLOADER_INFO[_os]["Settings"]["NewBootloader"] == "LILO":
        #Make LILO's config file.
        logger.info("set_new_bootloader_config(): Making LILO's configuration file...")
        cmd = "liloconfig -f"

        if use_chroot:
            cmd = "chroot "+mount_point+" "+cmd

        if CoreTools.start_process(cmd, show_output=False, privileged=True) != 0:
            logger.error("set_new_bootloader_config(): '"+cmd
                         +"' didn't run successfully! Attempting to continue anyway...")

        #Check the config file exists for lilo.
        if os.path.isfile(mount_point+"/etc/lilo.conf"):
            #It does, we'll run the function to set the config now.
            logger.info("set_new_bootloader_config(): Setting LILO Configuration...")
            BootloaderConfigSettingTools.set_lilo_config(_os=_os, filetoopen=mount_point
                                                         + "/etc/lilo.conf")

            #Also, set the OS entries.
            logger.info("set_new_bootloader_config(): Creating LILO OS Entries...")
            BootloaderConfigSettingTools.make_lilo_os_entries(_os=_os, filetoopen=mount_point
                                                              + "/etc/lilo.conf",
                                                              mount_point=mount_point,
                                                              kernel_options=BOOTLOADER_INFO[_os]["Settings"]["NewKernelOptions"])

        #Now Install LILO to the MBR.
        logger.info("set_new_bootloader_config(): Installing LILO to the MBR...")
        BootloaderConfigSettingTools.install_lilo_to_mbr(use_chroot=use_chroot,
                                                         mount_point=mount_point)

    elif BOOTLOADER_INFO[_os]["Settings"]["NewBootloader"] == "ELILO":
        #unmount the UEFI Partition now, and update mtab in the chroot.
        #Pause for 0.5 secs.
        time.sleep(0.5)

        if CoreTools.unmount(OS_INFO[_os]["EFIPartition"]) != 0:
            logger.error("set_new_bootloader_config(): Failed to unmount "+_os
                         + "'s EFI partition! Waning user and prompting to try again...")

            DialogTools.show_msg_dlg(message="Couldn't unmount "+_os+"'s EFI partition! "
                                     + "Giving up. You will be prompted to try again if you wish.",
                                     kind="error")

            return False

        #Update chroot mtab if needed.
        if use_chroot:
            CoreTools.update_chroot_mtab(mount_point=mount_point)

        #Make ELILO's config file.
        logger.info("set_new_bootloader_config(): Making ELILO's configuration file...")

        cmd = "elilo -b "+OS_INFO[_os]["EFIPartition"]+" --autoconf"

        if use_chroot:
            cmd = "chroot "+mount_point+" "+cmd

        if CoreTools.start_process(cmd, show_output=False, privileged=True) != 0:
            logger.error("set_new_bootloader_config(): '"+cmd+"' didn't run successfully! "
                         + "Attempting to continue anyway...")

        #Check elilo's config file exists.
        if os.path.isfile(mount_point+"/etc/elilo.conf"):
            #It does, we'll run the function to set the config now.
            logger.info("set_new_bootloader_config(): Setting ELILO Configuration...")
            BootloaderConfigSettingTools.set_lilo_config(_os=_os, filetoopen=mount_point
                                                         + "/etc/elilo.conf")

            #Also, set the OS entries.
            logger.info("set_new_bootloader_config(): Creating ELILO OS Entries...")
            BootloaderConfigSettingTools.make_lilo_os_entries(_os=_os, filetoopen=mount_point
                                                              + "/etc/elilo.conf",
                                                              mount_point=mount_point,
                                                              kernel_options=BOOTLOADER_INFO[_os]["Settings"]["NewKernelOptions"])

        #Now Install ELILO to the UEFI Partition.
        logger.info("set_new_bootloader_config(): Installing ELILO to "
                    + OS_INFO[_os]["EFIPartition"]+"...")

        BootloaderConfigSettingTools.install_elilo_to_partition(_os=_os,
                                                                package_manager=OS_INFO[_os]["PackageManager"],
                                                                use_chroot=use_chroot,
                                                                mount_point=mount_point)

        #Mount the UEFI partition at mount_point/boot/efi.
        if CoreTools.mount_partition(partition=OS_INFO[_os]["EFIPartition"],
                                     mount_point=mount_point+"/boot/efi") != 0:
            logger.error("set_new_bootloader_config(): Failed to mount EFI partition "
                         + OS_INFO[_os]["EFIPartition"]+"! Continuing anyway...")

        #Copy and backup UEFI files where needed.
        HelperBackendTools.backup_uefi_files(mount_point=mount_point)
        HelperBackendTools.manage_uefi_files(_os=_os, mount_point=mount_point)

        #unmount the EFI partition.
        if CoreTools.unmount(OS_INFO[_os]["EFIPartition"]) != 0:
            logger.error("set_new_bootloader_config(): Couldn't unmount EFI partition! "
                         + "This probably won't matter, so we'll continue anyway...")

    #If there's a seperate EFI partition for this OS, make sure it's unmounted before
    #removing the chroot.
    if OS_INFO[_os]["EFIPartition"] != "Unknown":
        if CoreTools.unmount(mount_point+"/boot/efi") != 0:
            logger.error("set_new_bootloader_config(): Failed to unmount "+mount_point
                         + "/boot/efi! This probably doesn't matter...")

    #unmount a /boot partition if it exists.
    if OS_INFO[_os]["BootPartition"] != "Unknown":
        if CoreTools.unmount(mount_point+"/boot") != 0:
            logger.error("set_new_bootloader_config(): Failed to unmount "+_os
                         + "'s /boot partition! Continuing anyway...")

    #Tear down chroot if needed.
    if use_chroot:
        if CoreTools.teardown_chroot(mount_point=mount_point) != 0:
            logger.error("set_new_bootloader_config(): Failed to remove chroot at "
                         + mount_point+"! Attempting to continue anyway...")

    #unmount the partition if needed.
    if unmount_after:
        if CoreTools.unmount(mount_point) != 0:
            logger.error("set_new_bootloader_config(): Failed to unmount "+mount_point
                         + "! Continuing anyway...")

    #Attempt to clear any stuck logical volumes that may have been created by os-prober.
    CoreTools.start_process("dmsetup remove_all -y", privileged=True)

    logger.debug("set_new_bootloader_config(): Finished setting "
                 + BOOTLOADER_INFO[_os]["Settings"]["NewBootloader"]
                 + "'s config for "+_os+"...")

    wx.CallAfter(wx.GetApp().TopWindow.update_output_box, "\n###Finished setting "
                 + BOOTLOADER_INFO[_os]["Settings"]["NewBootloader"]+"'s config for "
                 + _os+"...###\n")

    wx.CallAfter(wx.GetApp().TopWindow.update_current_operation_text, message="Finished setting "
                 + BOOTLOADER_INFO[_os]["Settings"]["NewBootloader"]+"'s config for "+_os+"!")

    wx.CallAfter(wx.GetApp().TopWindow.update_current_progress, 100)
    return True
