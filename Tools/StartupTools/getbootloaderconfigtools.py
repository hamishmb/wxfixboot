#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Bootloader Configuration Obtaining Tools in the Startup Tools Package for WxFixBoot Version 2.0.3
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

#Do future imports to prepare to support python 3. Use unicode strings rather than ASCII strings, as they fix potential problems.
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

#Import modules
import os
import sys
import logging

#Import other modules.
from ..dictionaries import *

#Make unicode an alias for str in Python 3.
if sys.version_info[0] == 3:
    unicode = str #pylint: disable=redefined-builtin,invalid-name
    str = bytes #pylint: disable=redefined-builtin,invalid-name

#Set up logging. FIXME Set logger level as specified on cmdline.
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def find_grub(os_partition, grub_version):
    """Find GRUB for the given OS."""
    logger.info("find_grub(): Looking for "+grub_version+"...")

    #Do some setup.
    likely_grub_install_disks = (DISK_INFO[os_partition]["HostDevice"], os_partition)

    logger.info("find_grub(): Looking in "+', '.join(likely_grub_install_disks)+"...")

    #Look for the right string for each boot loader.
    if grub_version == "GRUB2":
        look_for = ("ZRr=", "TCPAf")

    else:
        look_for = ("ZRrI", "")

    for disk in likely_grub_install_disks:
        logger.info("find_grub(): "+DISK_INFO[disk]["Name"]+" "+', '.join(unicode(DISK_INFO[disk]["BootRecordStrings"])))

        for line in DISK_INFO[disk]["BootRecordStrings"]:
            line = unicode(line)

            #Check that we have the right version of GRUB, and double check that GRUB is present.
            if line in look_for and "GRUB" in DISK_INFO[disk]["BootRecordStrings"]:
                logger.info("find_grub(): Found "+grub_version+" on "+disk+"...")
                logger.info("find_grub(): Done!")
                return disk

    logger.info("find_grub(): Didn't find "+grub_version+" on any likely disks...")
    return "Unknown"

def parse_grub2_menu_data(menu_data="", mount_point="", menu_entries=None, menu_name="MainMenu", menu_ids=None, menu_id=""):
    """Find and parse GRUB2 (EFI and BIOS) menu entries in the given line list"""
    if menu_entries is None:
        menu_entries = {}

    if menu_ids is None:
        menu_ids = {}

    if menu_data != "":
        logger.info("parse_grub2_menu_data(): Finding and parsing menu entries in given menu data...")
        grub_dir = ""

    else:
        logger.info("parse_grub2_menu_data(): Finding and opening GRUB config file...")

        #Find grub.cfg. (Ubuntu).
        if os.path.isdir(mount_point+"/boot/grub"):
            grub_dir = mount_point+"/boot/grub"

        #(Fedora, BIOS)
        elif os.path.isdir(mount_point+"/boot/grub2"):
            grub_dir = mount_point+"/boot/grub2"

        #(Fedora, EFI)
        if os.path.isfile(grub_dir+"/grub.cfg") is False and os.path.isdir(mount_point+"/boot/efi/EFI/fedora"):
            grub_dir = mount_point+"/boot/efi/EFI/fedora"

        #Process menu entries, and pass the entire contents of the menu entries file to the parser.
        menu_entries_file = open(grub_dir+"/grub.cfg", "r")
        menu_data = menu_entries_file.readlines()
        menu_entries_file.close()

        logger.info("parse_grub2_menu_data(): Finding and parsing menu entries in "+grub_dir+"/grub.cfg...")

    logger.debug("parse_grub2_menu_data(): Parsing menu data for menu: "+menu_name+"...")

    menu_entries[menu_name] = {}
    menu_entries[menu_name]["Order"] = []
    menu_ids[menu_name] = {}
    menu_ids[menu_name]["ID"] = menu_id

    entry_counter = 0
    skip_until = 0
    line_counter = 0

    #Read each line.
    for line in menu_data:
        line_counter += 1

        #Skip some lines if needed.
        if line_counter < skip_until:
            continue

        #Parse any menu entries we find.
        if "menuentry " in line:
            logger.info("parse_grub2_menu_data(): Found a menu entry. Assembling into a dictionary with assemble_grub2_menu_entry()...")
            menu_entries = assemble_grub2_menu_entry(menu_entries, menu_ids, menu_data, menu_name, line, entry_counter)
            logger.info("parse_grub2_menu_data(): Done!")

            #Increment the entry counter.
            entry_counter += 1

        #Handle submenus correctly.
        elif "submenu " in line:
            logger.info("parse_grub2_menu_data(): Found submenu...")
            #Get the submenu's name, create a sub-dictionary for it, save its ID, and change the Value of "menu_name" to the submenu's name.
            #Keep compatibility with older versions of GRUB2.
            try:
                sub_menu_name = line.split("'")[1].replace("\"", "").replace("\'", "")

            except IndexError:
                sub_menu_name = line.split("\"")[1].replace("\"", "").replace("\'", "")

            #Get the entire contents of the submenu.
            logger.info("parse_grub2_menu_data(): Getting the entire text content of the submenu...")
            bracket_count = 0
            sub_menu_data = []

            for sub_menu_data_line in menu_data[menu_data.index(line):]:
                #Don't add the first line to the sub_menu_data to avoid an endless recursive call.
                if "submenu " not in sub_menu_data_line:
                    sub_menu_data.append(sub_menu_data_line)

                if "{" in sub_menu_data_line:
                    bracket_count += 1

                elif "}" in sub_menu_data_line:
                    bracket_count -= 1

                if bracket_count == 0:
                    break

            logger.info("parse_grub2_menu_data(): Done! Processing any menu entries in the submenu with recursive call...")

            #Call this function again with the contents of the submenu, and some arguments so everything works correctly.
            menu_entries, menu_ids = parse_grub2_menu_data(sub_menu_data, mount_point=mount_point, menu_entries=menu_entries, menu_name=sub_menu_name, menu_ids=menu_ids, menu_id=unicode(entry_counter)+">")[1:]

            logger.info("parse_grub2_menu_data(): Done! Jumping past the submenu data to avoid duplicating menu entries...")

            #Increment the entry counter.
            entry_counter += 1

            #Skip the submenu data, and set "menu" back to "MainMenu" again so entries are added correctly.
            skip_until = line_counter+len(sub_menu_data)

    logger.info("parse_grub2_menu_data(): Finished!")
    return grub_dir, menu_entries, menu_ids

def assemble_grub2_menu_entry(menu_entries, menu_ids, menu_entries_file_contents, menu, line, entry_counter):
    """Assemble a menu entry in the dictionary for GRUB2 (BIOS and UEFI)"""
    logger.info("assemble_grub2_menu_entry(): Preparing to get menu entry info...")

    #Get the menu entry name.
    if "\'" in line:
        menu_entry_name = line.split("\'")[1]

    else:
        menu_entry_name = line.split("\"")[1]

    logger.debug("assemble_grub2_menu_entry(): Menu Entry name: "+menu_entry_name+"...")

    #Handle duplicate names.
    if menu_entry_name in menu_entries[menu]["Order"]:
        menu_entry_name = menu_entry_name+" (ID "+menu_ids[menu]["ID"]+unicode(entry_counter)+")"

    #Get the menu entry ID.
    menu_entries[menu]["Order"].append(menu_entry_name)
    menu_entries[menu][menu_entry_name] = {}
    menu_entries[menu][menu_entry_name]["ID"] = menu_ids[menu]["ID"]+unicode(entry_counter)

    logger.debug("assemble_grub2_menu_entry(): Menu Entry ID: "+menu_entries[menu][menu_entry_name]["ID"]+"...")

    #Get the full contents of the menuentry (keep adding lines to the list until we find a "}").
    logger.info("assemble_grub2_menu_entry(): Getting menu entry data...")

    menu_entries[menu][menu_entry_name]["RawMenuEntryData"] = []

    for menu_entry_data in menu_entries_file_contents[menu_entries_file_contents.index(line):]:
        menu_entries[menu][menu_entry_name]["RawMenuEntryData"].append(menu_entry_data)

        if menu_entry_data.split()[-1] == "}":
            break

    #Get boot partition.
    logger.info("assemble_grub2_menu_entry(): Getting menu entry's boot partition with entry name...")

    #Try multiple methods to get this info.
    menu_entries[menu][menu_entry_name]["Partition"] = "Unknown"

    #Try to get it from the menu entry name (older GRUB2 versions).
    try:
        #Remove the brackets, split with " ", and grab the last element in the resulting list, which is hopefully the partition name e.g. /dev/sdc.
        menu_entries[menu][menu_entry_name]["Partition"] = menu_entry_name.replace(")", "").split(" (")[1].split(" ")[-1]

    except IndexError:
        pass

    #If this fails, try finding the UUID in the menu-entry data and converting that to a device name.
    if menu_entries[menu][menu_entry_name]["Partition"] == "Unknown" or "/dev/" not in menu_entries[menu][menu_entry_name]["Partition"]:
        logger.info("assemble_grub2_menu_entry(): Getting menu entry's boot partition with UUID...")
        uuid = ""

        for each_line in menu_entries[menu][menu_entry_name]["RawMenuEntryData"]:
            if "search " in each_line:
                uuid = each_line.split()[-1]
                logger.info("assemble_grub2_menu_entry(): Found UUID...")
                break

        if uuid != "":
            #Convert to device name if possible.
            logger.info("assemble_grub2_menu_entry(): Matching UUID to disk...")
            for disk in DISK_INFO:
                if DISK_INFO[disk]["UUID"] == uuid:
                    menu_entries[menu][menu_entry_name]["Partition"] = disk

    #If THAT fails, try to use the "set root=" line to find the device name.
    if menu_entries[menu][menu_entry_name]["Partition"] == "Unknown" or "/dev/" not in menu_entries[menu][menu_entry_name]["Partition"]:
        logger.info("assemble_grub2_menu_entry(): Getting menu entry's boot partition with GRUB2's 'set root=' line...")
        root_line = ""

        for each_line in menu_entries[menu][menu_entry_name]["RawMenuEntryData"]:
            if "set root" in each_line:
                root_line = each_line
                logger.info("assemble_grub2_menu_entry(): Found GRUB2's 'set root=' line...")
                break

        if root_line != "":
            #Get the numbers used in this line.
            logger.info("assemble_grub2_menu_entry(): Finding GRUB device name numbers...")
            numbers = []

            for char in root_line:
                if char.isdigit():
                    numbers.append(int(char))

            #chr(97) is 'a', so add 97 to first number to get the linux name (e.g. sda). The device number is 0-based.
            letter = chr(numbers[0]+97)

            #Check it's a letter from a to z.
            if numbers[0] in range(0, 25):
                menu_entries[menu][menu_entry_name]["Partition"] = "/dev/sd"+letter+unicode(numbers[1]) #The partition number is 1-based.

    #Log if we STILL haven't found the disk.
    if menu_entries[menu][menu_entry_name]["Partition"] == "Unknown" or "/dev/" not in menu_entries[menu][menu_entry_name]["Partition"]:
        menu_entries[menu][menu_entry_name]["Partition"] = "Unknown"
        logger.error("assemble_grub2_menu_entry(): Couldn't find boot partition for menu entry! Continuing anyway...")

    else:
        logger.debug("assemble_grub2_menu_entry(): Menu Entry Boot Partition: "+menu_entries[menu][menu_entry_name]["Partition"]+"...")

    #Get the kernel options for this menuentry.
    logger.info("assemble_grub2_menu_entry(): Getting kernel options...")

    menu_entries[menu][menu_entry_name]["KernelOptions"] = ["Unknown"]

    for line in menu_entries[menu][menu_entry_name]["RawMenuEntryData"]:
        if "linux" in line:
            menu_entries[menu][menu_entry_name]["KernelOptions"] = line.split()[3:]

    #Check we got them.
    if menu_entries[menu][menu_entry_name]["KernelOptions"] == ["Unknown"]:
        logger.error("assemble_grub2_menu_entry(): Couldn't find kernel options for menu entry! Continuing anyway...")

    else:
        logger.debug("assemble_grub2_menu_entry(): Menu Entry Kernel Options: "+', '.join(menu_entries[menu][menu_entry_name]["KernelOptions"])+"...")

    return menu_entries

def get_grub2_config(config_file_path, grubenv_file_path, menu_entries):
    """Get important bits of config from grub2 (MBR or UEFI)"""
    logger.info("get_grub2_config(): Getting config at "+config_file_path+"...")

    #Set temporary vars
    timeout = "Unknown"
    kernel_options = "Unknown"
    default_os = "Unknown"

    #Open the config file in read mode, so we can save the important bits of config.
    logger.info("get_grub2_config(): Getting config...")
    config_file = open(config_file_path, 'r')

    #Loop through each line in the file, paying attention only to the important ones.
    for line in config_file:
        #Look for the timeout setting.
        if 'GRUB_TIMEOUT' in line and '=' in line:
            #Get only the numbers.
            temp = line.split("=")[1].replace("\n", "")

            #Check this worked properly.
            if temp.isdigit():
                #Great! We got it.
                logger.info("get_grub2_config(): Found bootloader timeout...")
                timeout = int(temp)

        #Look for kernel options used globally in all the boot options.
        elif 'GRUB_CMDLINE_LINUX' in line and '=' in line:
            #Split by ' or ", and check the result isn't an empty string in case there was nothing there.
            if "\'" in line:
                temp = line.split("\'")[1]

            elif "\"" in line:
                temp = line.split("\"")[1]

            if temp != "":
                kernel_options = temp
                logger.info("get_grub2_config(): Found global kernel options...")

        #Look for default OS setting.
        elif "GRUB_DEFAULT" in line and "=" in line:
            #Setup.
            match_by_name = False
            match_by_id = False

            #If this is an integer or string that == "saved", we need to match it to GRUB's grub.cfg menu_entries.
            logger.info("get_grub2_config(): Found default OS line....")
            grub_default = line.split("=")[1].replace("\"", "").replace("\'", "").replace("\n", "")

            if grub_default.isdigit() or ">" in grub_default:
                #Match By ID.
                match_by_id = True

            elif grub_default == "saved":
                #Find the corresponding GRUB menuentry, matching by name or ID.
                logger.info("get_grub2_config(): Looking for default OS in GRUB environment file...")
                grubenv_file = open(grubenv_file_path, "r")

                for variable in grubenv_file:
                    if "saved_entry=" in variable or "default=" in variable:
                        grub_default = variable.split("=")[1].replace("\n", "")

                #Match by ID if possible.
                match_by_id = (grub_default.isdigit() or ">" in grub_default)

                #Otherwise match by name.
                match_by_name = (not match_by_id)

            else:
                #Match by name.
                match_by_name = True

            if match_by_id:
                #Find the corresponding GRUB menuentry, matching by ID.
                logger.info("get_grub2_config(): Matching default OS by ID...")
                for menu in menu_entries.keys():
                    for _os in menu_entries[menu]["Order"]:
                        if menu_entries[menu][_os]["ID"] == grub_default:
                            default_os = _os
                            break

            if match_by_name:
                #Check in the menuentries list.
                logger.info("get_grub2_config(): Finding default OS by name...")
                found = False

                for menu in menu_entries.keys():
                    for menu_entry in menu_entries[menu]["Order"]:
                        if grub_default == menu_entry:
                            default_os = grub_default
                            found = True

                if found:
                    logger.info("get_grub2_config(): Found default OS by name...")

                else:
                    logger.warning("get_grub2_config(): Didn't find default OS by name, setting it to the 1st menu entry instead...")

                    #Find the 1st menu entry.
                    for entry in menu_entries["MainMenu"]["Order"]:
                        if menu_entries["MainMenu"][entry]["ID"] == 0:
                            default_os = entry
                            logger.info("get_grub2_config(): Set default OS to "+entry+" instead. Continuing...")

            logger.info("get_grub2_config(): Done!")

    #Close the file.
    logger.info("get_grub2_config(): Done! Returning information...")
    config_file.close()

    return (timeout, kernel_options, default_os)

def parse_grublegacy_menu_entries(menu_entries_file_path):
    """Find and parse GRUB LEGACY menu entries."""
    logger.info("parse_grublegacy_menu_entries(): Finding and parsing menu entries...")

    #Open the menu entries file to find and save all the menu entries.
    menu_entries_file = open(menu_entries_file_path, "r")
    menu_entries_file_contents = menu_entries_file.readlines()
    menu_entries_file.close()

    #Setup.
    menu_entries = {}
    menu_entries["MainMenu"] = {}
    menu_entries["MainMenu"]["Order"] = []
    entry_counter = 0

    #Read each line in the file.
    for line in menu_entries_file_contents:
        #Process all menu entries.
        if "title" in line and "#" not in line:
            logger.info("parse_grublegacy_menu_entries(): Found a menu entry. Assembling into a dictionary with assemble_grublegacy_menu_entry()...")
            menu_entries = assemble_grublegacy_menu_entry(menu_entries, menu_entries_file_contents, line, entry_counter)
            entry_counter += 1
            logger.info("parse_grublegacy_menu_entries(): Done!")

    #Close the file.
    logger.info("parse_grublegacy_menu_entries(): Finished!")
    return menu_entries

def assemble_grublegacy_menu_entry(menu_entries, menu_entries_file_contents, line, entry_counter):
    """Assemble a menu entry in the dictionary for GRUB LEGACY"""
    logger.info("assemble_grublegacy_menu_entry(): Preparing to get menu entry info...")
    menu_entry = ' '.join(line.split("\t")[1:])

    #Make it work on Fedora.
    if menu_entry == "":
        menu_entry = ' '.join(line.split(" ")[1:])

    menu_entries["MainMenu"]["Order"].append(menu_entry)
    menu_entries["MainMenu"][menu_entry] = {}
    menu_entries["MainMenu"][menu_entry]["ID"] = unicode(entry_counter)

    menu_entries["MainMenu"][menu_entry]["RawMenuEntryData"] = []

    #Get the full contents of the menuentry (keep adding lines to the list until we find "title").
    logger.info("assemble_grublegacy_menu_entry(): Getting menu entry data...")
    for menu_entry_data in menu_entries_file_contents[menu_entries_file_contents.index(line)+1:]:
        menu_entries["MainMenu"][menu_entry]["RawMenuEntryData"].append(menu_entry_data)

        if "title" in menu_entry_data:
            #Remove the last line.
            menu_entries["MainMenu"][menu_entry]["RawMenuEntryData"].pop()
            break

    menu_entries["MainMenu"][menu_entry]["Partition"] = "Unknown"
    menu_entries["MainMenu"][menu_entry]["KernelOptions"] = ["Unknown"]

    logger.info("assemble_grublegacy_menu_entry(): Getting menu entry boot partition and kernel options...")

    for line in menu_entries["MainMenu"][menu_entry]["RawMenuEntryData"]:
        if "kernel" not in line:
            continue

        #Get the partition.
        try:
            partition = line.split(" ")[1]

        except IndexError:
            continue

        #Make it work on Fedora.
        if "vmlinuz" in partition:
            partition = line.split(" ")[3]

        #If we have a UUID, convert it into a device node.
        if "UUID=" in partition:
            uuid = partition.split("=")[2]

            for disk in DISK_INFO:
                if DISK_INFO[disk]["UUID"] == uuid:
                    menu_entries["MainMenu"][menu_entry]["Partition"] = disk

        else:
            menu_entries["MainMenu"][menu_entry]["Partition"] = partition.split("=")[1]

        logger.info("assemble_grublegacy_menu_entry(): Found boot partition...")

        #Kernel Options.
        menu_entries["MainMenu"][menu_entry]["KernelOptions"] = line.split(" ")[2:]
        logger.info("assemble_grublegacy_menu_entry(): Found kernel options...")

    return menu_entries

def get_grublegacy_config(config_file_path, menu_entries):
    """Get important bits of config from grub-legacy"""
    logger.info("get_grublegacy_config(): Getting config at "+config_file_path+"...")

    #Set temporary vars
    timeout, default_os = ("Unknown", "Unknown")

    #Open the file in read mode, so we can save the important bits of config.
    config_file = open(config_file_path, 'r')

    for line in config_file:
        #Look for the default setting.
        if "default" in line and "#" not in line:
            logger.info("get_grublegacy_config(): Getting default OS...")

            #Handle different versions of GRUB-LEGACY.
            if "=" in line:
                grub_default = line.split("=")[1].replace("\n", "")

            else:
                grub_default = line.split()[1].replace("\n", "")

            if grub_default.isdigit() is False:
                #Ignore it.
                logger.info("get_grublegacy_config(): Default OS is not a digit (probably set to \"saved\"), ignoring it...")
                continue

            #Find the corresponding GRUB menuentry, matching by ID.
            logger.info("get_grublegacy_config(): Matching default OS by ID...")
            for menu in menu_entries.keys():
                for _os in menu_entries[menu]["Order"]:
                    if menu_entries[menu][_os]["ID"] == grub_default:
                        default_os = _os
                        break

        #Look for the timeout setting.
        if 'timeout' in line and 'sec' not in line and "#" not in line:
            #Found it!
            try:
                timeout = line.split()[1].replace('\n', '')

            except IndexError:
                timeout = line.split("=")[1].replace('\n', '')

            if timeout.isdigit():
                #Great! We got it.
                logger.info("get_grublegacy_config(): Found bootloader time out...")
                timeout = int(timeout)

            #Exit the loop to save time.
            break

    #Close the file.
    logger.info("get_grublegacy_config(): Done! Returning Information...")
    config_file.close()

    return timeout, default_os

def parse_lilo_menu_entries(menu_entries_file_path):
    """Find and parse LILO and ELILO menu entries."""
    logger.info("parse_lilo_menu_entries(): Finding and parsing menu entries...")

    #Open the menu entries file to find and save all the menu entries.
    menu_entries_file = open(menu_entries_file_path, "r")
    menu_entries_file_contents = menu_entries_file.readlines()
    menu_entries = {}
    menu_entries["MainMenu"] = {}
    menu_entries["MainMenu"]["Order"] = []
    entry_counter = 0

    #Read each line.
    for line in menu_entries_file_contents:
        #Process all menu entries.
        if "image" in line and "#" not in line:
            logger.info("parse_lilo_menu_entries(): Found a menu entry. Assembling into a dictionary with assemble_lilo_menu_entry()...")
            menu_entries = assemble_lilo_menu_entry(menu_entries, menu_entries_file_contents, line, entry_counter)
            entry_counter += 1
            logger.info("parse_lilo_menu_entries(): Done!")

    #Close the file.
    logger.info("parse_lilo_menu_entries(): Finished!")
    menu_entries_file.close()
    return menu_entries

def assemble_lilo_menu_entry(menu_entries, menu_entries_file_contents, line, entry_counter):
    """Assemble a menu entry in the dictionary for LILO/ELILO"""
    logger.info("assemble_lilo_menu_entry(): Preparing to get menu entry info...")

    raw_menu_entry_data = []

    #Get the full contents of the menuentry (keep adding lines to the list until we find another menu entry).
    logger.info("assemble_lilo_menu_entry(): Getting menu entry data...")

    for menu_entry_data in menu_entries_file_contents[menu_entries_file_contents.index(line):]:
        raw_menu_entry_data.append(menu_entry_data)

        if "label" in menu_entry_data:
            menu_entry = menu_entry_data.split("=")[1].replace("\n", "")

        if menu_entry_data != line and "image" in menu_entry_data.split() and "=" in menu_entry_data.split() and "#" not in menu_entry_data.split():
            #Remove the last line.
            raw_menu_entry_data.pop()
            break

    menu_entries["MainMenu"][menu_entry] = {}
    menu_entries["MainMenu"]["Order"].append(menu_entry)
    menu_entries["MainMenu"][menu_entry]["RawMenuEntryData"] = raw_menu_entry_data
    menu_entries["MainMenu"][menu_entry]["ID"] = unicode(entry_counter)
    menu_entries["MainMenu"][menu_entry]["Partition"] = "Unknown"
    menu_entries["MainMenu"][menu_entry]["KernelOptions"] = ["Unknown"]

    for line in menu_entries["MainMenu"][menu_entry]["RawMenuEntryData"]:
        if "root" in line:
            #Get the partition.
            partition = '='.join(line.replace("\n", "").split("=")[1:])

            #If we get a UUID, convert it to a device node.
            if "UUID=" in partition:
                uuid = partition.split("=")[1].replace("\"", "")
                logger.info("assemble_lilo_menu_entry(): Found UUID "+uuid+". Finding device node...")

                for disk in DISK_INFO:
                    if DISK_INFO[disk]["UUID"] == uuid:
                        menu_entries["MainMenu"][menu_entry]["Partition"] = disk
                        logger.info("assemble_lilo_menu_entry(): Found device node "+disk+". Continuing...")

            else:
                menu_entries["MainMenu"][menu_entry]["Partition"] = partition

            logger.info("assemble_lilo_menu_entry(): Found boot partition...")

        elif "append" in line:
            #Get the kernel options.
            menu_entries["MainMenu"][menu_entry]["KernelOptions"] = line.replace("\n", "").split("=")[1].replace("\"", "").split()
            logger.info("assemble_lilo_menu_entry(): Found kernel options...")

    return menu_entries

def get_lilo_config(config_file_path, _os):
    """Get important bits of config from lilo and elilo"""
    logger.info("get_lilo_config(): Getting config at "+config_file_path+"...")

    #Set temporary vars
    timeout, kernel_options, boot_disk, default_os = ("Unknown", "Unknown", "Unknown", "Unknown")

    #Open the file in read mode, so we can save the important bits of config.
    config_file = open(config_file_path, 'r')

    #Loop through each line in the file, paying attention only to the important ones.
    for line in config_file:
        #Look for the delay/timeout setting.
        if ('delay' in line or 'timeout' in line) and '=' in line and "#" not in line:
            #Save it, carefully avoiding errors.
            timeout = line.split("=")[1].replace(" ", "").replace("\n", "")

            if timeout.isdigit():
                #Great! We got it.
                #However, because lilo and elilo save this in 10ths of a second, divide it by ten first.
                timeout = int(timeout)//10
                logger.info("get_lilo_config(): Found bootloader timeout...")

        #Look for kernel options used globally in all the boot options.
        elif 'append' in line and '=' in line and "#" not in line and kernel_options == "Unknown":
            #Found them! Save it to GlobalKernelOptions
            kernel_options = ' '.join(line.split("=")[1:]).replace("\"", "").replace("\n", "")
            logger.info("get_lilo_config(): Found global kernel options...")

        #Look for the 'boot' setting.
        elif 'boot' in line and '=' in line and '#' not in line and 'map' not in line:
            #Found it!
            temp = line.split("=")[1].replace("\n", "")

            #Convert to a device node if we have an ID.
            if "by-id" in temp:
                _id = temp.split("/")[-1].replace("\n", "").replace(" ", "")

                for disk in DISK_INFO:
                    if DISK_INFO[disk]["ID"] == _id:
                        temp = disk
                        break

            #Check we got the device node in case we had an ID.
            if "by-id" not in temp and "/dev/" in temp:
                boot_disk = temp
                logger.info("get_lilo_config(): Found boot disk "+boot_disk+"...")

        #Look for the default OS setting.
        elif "default" in line and "=" in line and "#" not in line:
            #Found it.
            default_os = line.split("=")[1].replace("\n", "")
            logger.info("get_lilo_config(): Found default OS "+default_os+"...")

    #Close the file.
    logger.info("get_lilo_config(): Done! Returning information...")
    config_file.close()

    #Find the 1st menu entry and use that if we couldn't find the default OS.
    if default_os == "Unknown":
        for entry in BOOTLOADER_INFO[_os]["MenuEntries"]["MainMenu"]["Order"]:
            if BOOTLOADER_INFO[_os]["MenuEntries"]["MainMenu"][entry]["ID"] == 0:
                default_os = entry
                logger.info("get_lilo_config(): Set default OS to "+entry+" instead. Continuing...")

    #Ignore ELILO's boot disk setting.
    if "/etc/lilo.conf" in config_file_path:
        return (timeout, kernel_options, boot_disk, default_os)

    #Otherwise...
    logger.info("get_lilo_config(): Ignoring ELILO's book disk setting, instead preferring the detected EFI partition for this OS...")
    return (timeout, kernel_options, default_os)
