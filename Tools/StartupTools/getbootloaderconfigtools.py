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

#Do future imports to prepare to support python 3. Use unicode strings rather than ASCII strings, as they fix potential problems.
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

#Import modules
import os
import logging

#Import other modules.
from .. import coretools as CoreTools

#Set up logging. FIXME Set logger level as specified on cmdline.
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

#Silence pylint errors about missing global dictionaries.
DiskInfo = {}
BootloaderInfo = {}

def find_grub(os_partition, grub_version):
    """Find GRUB for the given OS."""
    logger.info("find_grub(): Looking for "+grub_version+"...")

    #Do some setup.
    likely_grub_install_disks = (DiskInfo[os_partition]["HostDevice"], os_partition)

    logger.info("find_grub(): Looking in "+', '.join(likely_grub_install_disks)+"...")

    #Look for the right string for each boot loader.
    if grub_version == "GRUB2":
        look_for = ("ZRr=", "TCPAf")

    else:
        look_for = ("ZRrI", "")

    for disk in likely_grub_install_disks:
        logger.info("find_grub(): "+DiskInfo[disk]["Name"]+" "+', '.join(DiskInfo[disk]["BootRecordStrings"]))

        for line in DiskInfo[disk]["BootRecordStrings"]:
            #Check that we have the right version of GRUB, and double check that GRUB is present.
            if line in look_for and "GRUB" in DiskInfo[disk]["BootRecordStrings"]:
                logger.info("find_grub(): Found "+grub_version+" on "+disk+"...")
                logger.info("find_grub(): Done!")
                return disk

    logger.info("find_grub(): Didn't find "+grub_version+" on any likely disks...")
    return "Unknown"

def ParseGRUB2MenuDataOld(menu_data="", mount_point="", MenuEntries={}, menu_name="MainMenu", menu_ids={}, menu_id=""):
    """Find and parse GRUB2 (EFI and BIOS) menu entries in the given line list"""
    menu_name="MainMenu "+mount_point
    MenuEntries[menu_name] = {}
    print("Bob: ", MenuEntries.keys())
    return "", MenuEntries, menu_ids

def ParseGRUB2MenuData(menu_data="", mount_point="", MenuEntries=None, menu_name="MainMenu", menu_ids={}, menu_id=""):
    """Find and parse GRUB2 (EFI and BIOS) menu entries in the given line list"""
    if MenuEntries is None:
        MenuEntries = {}

    if menu_data != "":
        logger.info("ParseGRUB2MenuData(): Finding and parsing menu entries in given menu data...")
        grub_dir = ""

    else:
        logger.info("ParseGRUB2MenuData(): Finding and opening GRUB config file...")

        #Find grub.cfg. (Ubuntu).
        if os.path.isdir(mount_point+"/boot/grub"):
            grub_dir = mount_point+"/boot/grub"

        #(Fedora, BIOS)
        elif os.path.isdir(mount_point+"/boot/grub2"):
            grub_dir = mount_point+"/boot/grub2"

        #(Fedora, EFI)
        if os.path.isfile(grub_dir+"/grub.cfg") == False and os.path.isdir(mount_point+"/boot/efi/EFI/fedora"):
            grub_dir = mount_point+"/boot/efi/EFI/fedora"

        #Process menu entries, and pass the entire contents of the menu entries file to the parser.
        MenuEntriesFile = open(grub_dir+"/grub.cfg", "r")
        menu_data = MenuEntriesFile.readlines()
        MenuEntriesFile.close()

        logger.info("ParseGRUB2MenuData(): Finding and parsing menu entries in "+grub_dir+"/grub.cfg...")

    logger.debug("ParseGRUB2MenuData(): Parsing menu data for menu: "+menu_name+"...")

    MenuEntries[menu_name] = {}
    MenuEntries[menu_name]["Order"] = []
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
            logger.info("ParseGRUB2MenuData(): Found a menu entry. Assembling into a dictionary with AssembleGRUB2MenuEntry()...")
            MenuEntries = AssembleGRUB2MenuEntry(MenuEntries, menu_ids, menu_data, menu_name, line, entry_counter)
            logger.info("ParseGRUB2MenuData(): Done!")

            #Increment the entry counter.
            entry_counter += 1

        #Handle submenus correctly.
        elif "submenu " in line:
            logger.info("ParseGRUB2MenuData(): Found submenu...")
            #Get the submenu's name, create a sub-dictionary for it, save its ID, and change the Value of "menu_name" to the submenu's name.
            #Keep compatibility with older versions of GRUB2.
            try:
                sub_menu_name = line.split("'")[1].replace("\"", "").replace("\'", "")

            except IndexError:
                sub_menu_name = line.split("\"")[1].replace("\"", "").replace("\'", "")

            #Get the entire contents of the submenu.
            logger.info("ParseGRUB2MenuData(): Getting the entire text content of the submenu...")
            bracket_count = 0
            SubMenuData = []

            for SubMenuDataLine in menu_data[menu_data.index(line):]:
                #Don't add the first line to the SubMenuData to avoid an endless recursive call.
                if "submenu " not in SubMenuDataLine:
                    SubMenuData.append(SubMenuDataLine)

                if "{" in SubMenuDataLine:
                    bracket_count += 1

                elif "}" in SubMenuDataLine:
                    bracket_count -= 1

                if bracket_count == 0:
                    break

            logger.info("ParseGRUB2MenuData(): Done! Processing any menu entries in the submenu with recursive call...")

            #Call this function again with the contents of the submenu, and some arguments so everything works correctly.
            MenuEntries, menu_ids = ParseGRUB2MenuData(SubMenuData, mount_point=mount_point, MenuEntries=MenuEntries, menu_name=sub_menu_name, menu_ids=menu_ids, menu_id=unicode(entry_counter)+">")[1:]

            logger.info("ParseGRUB2MenuData(): Done! Jumping past the submenu data to avoid duplicating menu entries...")

            #Increment the entry counter.
            entry_counter += 1

            #Skip the submenu data, and set "Menu" back to "MainMenu" again so entries are added correctly.
            skip_until = line_counter+len(SubMenuData)

    logger.info("ParseGRUB2MenuData(): Finished!")
    return grub_dir, MenuEntries, menu_ids

def AssembleGRUB2MenuEntry(MenuEntries, menu_ids, MenuEntriesFileContents, Menu, line, entry_counter):
    """Assemble a menu entry in the dictionary for GRUB2 (BIOS and UEFI)"""
    logger.info("AssembleGRUB2MenuEntry(): Preparing to get menu entry info...")

    #Get the menu entry name.
    if "\'" in line:
        MenuEntryName = line.split("\'")[1]

    else:
        MenuEntryName = line.split("\"")[1]

    logger.debug("AssembleGRUB2MenuEntry(): Menu Entry name: "+MenuEntryName+"...")

    #Handle duplicate names.
    if MenuEntryName in MenuEntries[Menu]["Order"]:
        MenuEntryName = MenuEntryName+" (ID "+menu_ids[Menu]["ID"]+unicode(entry_counter)+")"

    #Get the menu entry ID.
    MenuEntries[Menu]["Order"].append(MenuEntryName)
    MenuEntries[Menu][MenuEntryName] = {}
    MenuEntries[Menu][MenuEntryName]["ID"] = menu_ids[Menu]["ID"]+unicode(entry_counter)

    logger.debug("AssembleGRUB2MenuEntry(): Menu Entry ID: "+MenuEntries[Menu][MenuEntryName]["ID"]+"...")

    #Get the full contents of the menuentry (keep adding lines to the list until we find a "}").
    logger.info("AssembleGRUB2MenuEntry(): Getting menu entry data...")

    MenuEntries[Menu][MenuEntryName]["RawMenuEntryData"] = []

    for MenuEntryData in MenuEntriesFileContents[MenuEntriesFileContents.index(line):]:
        MenuEntries[Menu][MenuEntryName]["RawMenuEntryData"].append(MenuEntryData)

        if MenuEntryData.split()[-1] == "}":
            break

    #Get boot partition.
    logger.info("AssembleGRUB2MenuEntry(): Getting menu entry's boot partition with entry name...")

    #Try multiple methods to get this info.
    MenuEntries[Menu][MenuEntryName]["Partition"] = "Unknown"

    #Try to get it from the menu entry name (older GRUB2 versions).
    try:
        #Remove the brackets, split with " ", and grab the last element in the resulting list, which is hopefully the partition name e.g. /dev/sdc.
        MenuEntries[Menu][MenuEntryName]["Partition"] = MenuEntryName.replace(")", "").split(" (")[1].split(" ")[-1]

    except IndexError: pass

    #If this fails, try finding the UUID in the menu-entry data and converting that to a device name.
    if MenuEntries[Menu][MenuEntryName]["Partition"] == "Unknown" or "/dev/" not in MenuEntries[Menu][MenuEntryName]["Partition"]:
        logger.info("AssembleGRUB2MenuEntry(): Getting menu entry's boot partition with UUID...")
        UUID = ""

        for EachLine in MenuEntries[Menu][MenuEntryName]["RawMenuEntryData"]:
            if "search " in EachLine:
                UUID = EachLine.split()[-1]
                logger.info("AssembleGRUB2MenuEntry(): Found UUID...")
                break

        if UUID != "":
            #Convert to device name if possible.
            logger.info("AssembleGRUB2MenuEntry(): Matching UUID to disk...")
            for disk in DiskInfo.keys():
                if DiskInfo[disk]["UUID"] == UUID:
                    MenuEntries[Menu][MenuEntryName]["Partition"] = disk

    #If THAT fails, try to use the "set root=" line to find the device name.
    if MenuEntries[Menu][MenuEntryName]["Partition"] == "Unknown" or "/dev/" not in MenuEntries[Menu][MenuEntryName]["Partition"]:
        logger.info("AssembleGRUB2MenuEntry(): Getting menu entry's boot partition with GRUB2's 'set root=' line...")
        RootLine = ""

        for EachLine in MenuEntries[Menu][MenuEntryName]["RawMenuEntryData"]:
            if "set root" in EachLine:
                RootLine = EachLine
                logger.info("AssembleGRUB2MenuEntry(): Found GRUB2's 'set root=' line...")
                break

        if RootLine != "":
            #Get the numbers used in this line.
            logger.info("AssembleGRUB2MenuEntry(): Finding GRUB device name numbers...")
            Numbers = []

            for Char in RootLine:
                if Char.isdigit():
                    Numbers.append(int(Char))

            #chr(97) is 'a', so add 97 to first number to get the linux name (e.g. sda). The device number is 0-based.
            Letter = chr(Numbers[0]+97)

            #Check it's a letter from a to z.
            if Numbers[0] in range(0, 25):
                MenuEntries[Menu][MenuEntryName]["Partition"] = "/dev/sd"+Letter+unicode(Numbers[1]) #The partition number is 1-based.

    #Log if we STILL haven't found the disk.
    if MenuEntries[Menu][MenuEntryName]["Partition"] == "Unknown" or "/dev/" not in MenuEntries[Menu][MenuEntryName]["Partition"]:
        MenuEntries[Menu][MenuEntryName]["Partition"] = "Unknown"
        logger.error("AssembleGRUB2MenuEntry(): Couldn't find boot partition for menu entry! Continuing anyway...")

    else:
        logger.debug("AssembleGRUB2MenuEntry(): Menu Entry Boot Partition: "+MenuEntries[Menu][MenuEntryName]["Partition"]+"...")

    #Get the kernel options for this menuentry.
    logger.info("AssembleGRUB2MenuEntry(): Getting kernel options...")

    MenuEntries[Menu][MenuEntryName]["KernelOptions"] = ["Unknown"]

    for line in MenuEntries[Menu][MenuEntryName]["RawMenuEntryData"]:
        if "linux" in line:
            MenuEntries[Menu][MenuEntryName]["KernelOptions"] = line.split()[3:]

    #Check we got them.
    if MenuEntries[Menu][MenuEntryName]["KernelOptions"] == ["Unknown"]:
        logger.error("AssembleGRUB2MenuEntry(): Couldn't find kernel options for menu entry! Continuing anyway...")

    else:
        logger.debug("AssembleGRUB2MenuEntry(): Menu Entry Kernel Options: "+', '.join(MenuEntries[Menu][MenuEntryName]["KernelOptions"])+"...")

    return MenuEntries

def GetGRUB2Config(ConfigFilePath, GRUBEnvironmentFilePath, MenuEntries):
    """Get important bits of config from grub2 (MBR or UEFI)"""
    logger.info("GetGRUB2Config(): Getting config at "+ConfigFilePath+"...")

    #Set temporary vars
    Timeout = "Unknown"
    KernelOptions = "Unknown"
    DefaultOS = "Unknown"

    #Open the config file in read mode, so we can save the important bits of config.
    logger.info("GetGRUB2Config(): Getting config...")
    ConfigFile = open(ConfigFilePath, 'r')

    #Loop through each line in the file, paying attention only to the important ones.
    for line in ConfigFile:
        #Look for the timeout setting.
        if 'GRUB_TIMEOUT' in line and '=' in line:
            #Get only the numbers.
            Temp = line.split("=")[1].replace("\n", "")

            #Check this worked properly.
            if Temp.isdigit():
                #Great! We got it.
                logger.info("GetGRUB2Config(): Found bootloader timeout...")
                Timeout = int(Temp)

        #Look for kernel options used globally in all the boot options.
        elif 'GRUB_CMDLINE_LINUX' in line and '=' in line:
            #Split by ' or ", and check the result isn't an empty string in case there was nothing there.
            if "\'" in line:
                Temp = line.split("\'")[1]

            elif "\"" in line:
                Temp = line.split("\"")[1]

            if Temp != "":
                KernelOptions = Temp
                logger.info("GetGRUB2Config(): Found global kernel options...")

        #Look for default OS setting.
        elif "GRUB_DEFAULT" in line and "=" in line:
            #Setup.
            MatchByName = False
            MatchByID = False

            #If this is an integer or string that == "saved", we need to match it to GRUB's grub.cfg menuentries.
            logger.info("GetGRUB2Config(): Found default OS line....")
            GRUBDefault = line.split("=")[1].replace("\"", "").replace("\'", "").replace("\n", "")

            if GRUBDefault.isdigit() or ">" in GRUBDefault:
                #Match By ID.
                MatchByID = True

            elif GRUBDefault == "saved":
                #Find the corresponding GRUB menuentry, matching by name or ID.
                logger.info("GetGRUB2Config(): Looking for default OS in GRUB environment file...")
                GRUBEnvironmentFile = open(GRUBEnvironmentFilePath, "r")

                for Var in GRUBEnvironmentFile:
                    if "saved_entry=" in Var or "default=" in Var:
                        GRUBDefault = Var.split("=")[1].replace("\n", "")

                if GRUBDefault.isdigit() or ">" in GRUBDefault:
                    #Match by ID.
                    MatchByID = True

                else:
                    #Match by name.
                    MatchByName = True

            else:
                #Match by name.
                MatchByName = True

            if MatchByID:
                #Find the corresponding GRUB menuentry, matching by ID.
                logger.info("GetGRUB2Config(): Matching default OS by ID...")
                for Menu in MenuEntries.keys():
                    for OS in MenuEntries[Menu]["Order"]:
                        if MenuEntries[Menu][OS]["ID"] == GRUBDefault:
                            DefaultOS = OS
                            break

            if MatchByName:
                #Check in the menuentries list.
                logger.info("GetGRUB2Config(): Finding default OS by name...")
                Found = False

                for Menu in MenuEntries.keys():
                    for MenuEntry in MenuEntries[Menu]["Order"]:
                        if GRUBDefault == MenuEntry:
                            DefaultOS = GRUBDefault
                            Found = True

                if Found:
                    logger.info("GetGRUB2Config(): Found default OS by name...")

                else:
                    logger.warning("GetGRUB2Config(): Didn't find default OS by name, setting it to the 1st menu entry instead...")

                    #Find the 1st menu entry.
                    for Entry in MenuEntries["MainMenu"]["Order"]:
                        if MenuEntries["MainMenu"][Entry]["ID"] == 0:
                            DefaultOS = Entry
                            logger.info("GetGRUB2Config(): Set default OS to "+Entry+" instead. Continuing...")

            logger.info("GetGRUB2Config(): Done!")

    #Close the file.
    logger.info("GetGRUB2Config(): Done! Returning information...")
    ConfigFile.close()

    return (Timeout, KernelOptions, DefaultOS)

def ParseGRUBLEGACYMenuEntries(MenuEntriesFilePath):
    """Find and parse GRUB LEGACY menu entries."""
    logger.info("ParseGRUBLEGACYMenuEntries(): Finding and parsing menu entries...")

    #Open the menu entries file to find and save all the menu entries.
    MenuEntriesFile = open(MenuEntriesFilePath, "r")
    MenuEntriesFileContents = MenuEntriesFile.readlines()
    MenuEntriesFile.close()

    #Setup.
    MenuEntries = {}
    MenuEntries["MainMenu"] = {}
    MenuEntries["MainMenu"]["Order"] = []
    entry_counter = 0

    #Read each line in the file.
    for line in MenuEntriesFileContents:
        #Process all menu entries.
        if "title" in line and "#" not in line:
            logger.info("ParseGRUBLEGACYMenuEntries(): Found a menu entry. Assembling into a dictionary with AssembleGRUBLEGACYMenuEntry()...")
            MenuEntries = AssembleGRUBLEGACYMenuEntry(MenuEntries, MenuEntriesFileContents, line, entry_counter)
            entry_counter += 1
            logger.info("ParseGRUBLEGACYMenuEntries(): Done!")

    #Close the file.
    logger.info("ParseGRUBLEGACYMenuEntries(): Finished!")
    return MenuEntries

def AssembleGRUBLEGACYMenuEntry(MenuEntries, MenuEntriesFileContents, line, entry_counter):
    """Assemble a menu entry in the dictionary for GRUB LEGACY"""
    logger.info("AssembleGRUBLEGACYMenuEntry(): Preparing to get menu entry info...")
    MenuEntry = ' '.join(line.split("\t")[1:])

    #Make it work on Fedora.
    if MenuEntry == "":
        MenuEntry = ' '.join(line.split(" ")[1:])

    MenuEntries["MainMenu"]["Order"].append(MenuEntry)
    MenuEntries["MainMenu"][MenuEntry] = {}
    MenuEntries["MainMenu"][MenuEntry]["ID"] = unicode(entry_counter)

    MenuEntries["MainMenu"][MenuEntry]["RawMenuEntryData"] = []

    #Get the full contents of the menuentry (keep adding lines to the list until we find "title").
    logger.info("AssembleGRUBLEGACYMenuEntry(): Getting menu entry data...")
    for MenuEntryData in MenuEntriesFileContents[MenuEntriesFileContents.index(line)+1:]:
        MenuEntries["MainMenu"][MenuEntry]["RawMenuEntryData"].append(MenuEntryData)

        if "title" in MenuEntryData:
            #Remove the last line.
            MenuEntries["MainMenu"][MenuEntry]["RawMenuEntryData"].pop()
            break

    MenuEntries["MainMenu"][MenuEntry]["Partition"] = "Unknown"
    MenuEntries["MainMenu"][MenuEntry]["KernelOptions"] = ["Unknown"]

    logger.info("AssembleGRUBLEGACYMenuEntry(): Getting menu entry boot partition and kernel options...")

    for line in MenuEntries["MainMenu"][MenuEntry]["RawMenuEntryData"]:
        if "kernel" not in line:
            continue

        #Get the partition.
        try:
            Partition = line.split(" ")[1]

        except IndexError:
            continue

        #Make it work on Fedora.
        if "vmlinuz" in Partition:
            Partition = line.split(" ")[3]

        #If we have a UUID, convert it into a device node.
        if "UUID=" in Partition:
            UUID = Partition.split("=")[2]

            for disk in DiskInfo.keys():
                if DiskInfo[disk]["UUID"] == UUID:
                    MenuEntries["MainMenu"][MenuEntry]["Partition"] = disk

        else:
            MenuEntries["MainMenu"][MenuEntry]["Partition"] = Partition.split("=")[1]

        logger.info("AssembleGRUBLEGACYMenuEntry(): Found boot partition...")

        #Kernel Options.
        MenuEntries["MainMenu"][MenuEntry]["KernelOptions"] = line.split(" ")[2:]
        logger.info("AssembleGRUBLEGACYMenuEntry(): Found kernel options...")

    return MenuEntries

def GetGRUBLEGACYConfig(ConfigFilePath, MenuEntries):
    """Get important bits of config from grub-legacy"""
    logger.info("GetGRUBLEGACYConfig(): Getting config at "+ConfigFilePath+"...")

    #Set temporary vars
    Timeout, DefaultOS = ("Unknown", "Unknown")

    #Open the file in read mode, so we can save the important bits of config.
    ConfigFile = open(ConfigFilePath, 'r')

    for line in ConfigFile:
        #Look for the default setting.
        if "default" in line and "#" not in line:
            logger.info("GetGRUBLEGACYConfig(): Getting default OS...")

            #Handle different versions of GRUB-LEGACY.
            if "=" in line:
                GRUBDefault = line.split("=")[1].replace("\n", "")

            else:
                GRUBDefault = line.split()[1].replace("\n", "")

            if GRUBDefault.isdigit() == False:
                #Ignore it.
                logger.info("GetGRUBLEGACYConfig(): Default OS is not a digit (probably set to \"saved\"), ignoring it...")
                continue

            #Find the corresponding GRUB menuentry, matching by ID.
            logger.info("GetGRUB2Config(): Matching default OS by ID...")
            for Menu in MenuEntries.keys():
                for OS in MenuEntries[Menu]["Order"]:
                    if MenuEntries[Menu][OS]["ID"] == GRUBDefault:
                        DefaultOS = OS
                        break

        #Look for the timeout setting.
        if 'timeout' in line and 'sec' not in line and "#" not in line:
            #Found it!
            try:
                Timeout = line.split()[1].replace('\n', '')

            except IndexError:
                Timeout = line.split("=")[1].replace('\n', '')

            if Timeout.isdigit():
                #Great! We got it.
                logger.info("GetGRUBLEGACYConfig(): Found bootloader time out...")
                Timeout = int(Timeout)

            #Exit the loop to save time.
            break

    #Close the file.
    logger.info("GetGRUBLEGACYConfig(): Done! Returning Information...")
    ConfigFile.close()

    return Timeout, DefaultOS

def ParseLILOMenuEntries(MenuEntriesFilePath):
    """Find and parse LILO and ELILO menu entries."""
    logger.info("ParseLILOMenuEntries(): Finding and parsing menu entries...")

    #Open the menu entries file to find and save all the menu entries.
    MenuEntriesFile = open(MenuEntriesFilePath, "r")
    MenuEntriesFileContents = MenuEntriesFile.readlines()
    MenuEntries = {}
    MenuEntries["MainMenu"] = {}
    MenuEntries["MainMenu"]["Order"] = []
    entry_counter = 0

    #Read each line.
    for line in MenuEntriesFileContents:
        #Process all menu entries.
        if "image" in line and "#" not in line:
            logger.info("ParseLILOMenuEntries(): Found a menu entry. Assembling into a dictionary with AssembleLILOMenuEntry()...")
            MenuEntries = AssembleLILOMenuEntry(MenuEntries, MenuEntriesFileContents, line, entry_counter)
            entry_counter += 1
            logger.info("ParseLILOMenuEntries(): Done!")

    #Close the file.
    logger.info("ParseLILOMenuEntries(): Finished!")
    MenuEntriesFile.close()
    return MenuEntries

def AssembleLILOMenuEntry(MenuEntries, MenuEntriesFileContents, line, entry_counter):
    """Assemble a menu entry in the dictionary for LILO/ELILO"""
    logger.info("AssembleLILOMenuEntry(): Preparing to get menu entry info...")

    RawMenuEntryData = []

    #Get the full contents of the menuentry (keep adding lines to the list until we find another menu entry).
    logger.info("AssembleLILOMenuEntry(): Getting menu entry data...")

    for MenuEntryData in MenuEntriesFileContents[MenuEntriesFileContents.index(line):]:
        RawMenuEntryData.append(MenuEntryData)

        if "label" in MenuEntryData:
            MenuEntry = MenuEntryData.split("=")[1].replace("\n", "")

        if MenuEntryData != line and "image" in MenuEntryData.split() and "=" in MenuEntryData.split() and "#" not in MenuEntryData.split():
            #Remove the last line.
            RawMenuEntryData.pop()
            break

    MenuEntries["MainMenu"][MenuEntry] = {}
    MenuEntries["MainMenu"]["Order"].append(MenuEntry)
    MenuEntries["MainMenu"][MenuEntry]["RawMenuEntryData"] = RawMenuEntryData
    MenuEntries["MainMenu"][MenuEntry]["ID"] = unicode(entry_counter)
    MenuEntries["MainMenu"][MenuEntry]["Partition"] = "Unknown"
    MenuEntries["MainMenu"][MenuEntry]["KernelOptions"] = ["Unknown"]

    for line in MenuEntries["MainMenu"][MenuEntry]["RawMenuEntryData"]:
        if "root" in line:
            #Get the partition.
            Partition = '='.join(line.replace("\n", "").split("=")[1:])

            #If we get a UUID, convert it to a device node.
            if "UUID=" in Partition:
                UUID = Partition.split("=")[1].replace("\"", "")
                logger.info("AssembleLILOMenuEntry(): Found UUID "+UUID+". Finding device node...")

                for disk in DiskInfo.keys():
                    if DiskInfo[disk]["UUID"] == UUID:
                        MenuEntries["MainMenu"][MenuEntry]["Partition"] = disk
                        logger.info("AssembleLILOMenuEntry(): Found device node "+disk+". Continuing...")

            else:
                MenuEntries["MainMenu"][MenuEntry]["Partition"] = Partition

            logger.info("AssembleLILOMenuEntry(): Found boot partition...")

        elif "append" in line:
            #Get the kernel options.
            MenuEntries["MainMenu"][MenuEntry]["KernelOptions"] = line.replace("\n", "").split("=")[1].replace("\"", "").split()
            logger.info("AssembleLILOMenuEntry(): Found kernel options...")

    return MenuEntries

def GetLILOConfig(ConfigFilePath, OS):
    """Get important bits of config from lilo and elilo"""
    logger.info("GetLILOConfig(): Getting config at "+ConfigFilePath+"...")

    #Set temporary vars
    Timeout, KernelOptions, BootDisk, DefaultOS = ("Unknown", "Unknown", "Unknown", "Unknown")

    #Open the file in read mode, so we can save the important bits of config.
    ConfigFile = open(ConfigFilePath, 'r')

    #Loop through each line in the file, paying attention only to the important ones.
    for line in ConfigFile:
        #Look for the delay/timeout setting.
        if ('delay' in line or 'timeout' in line) and '=' in line and "#" not in line:
            #Save it, carefully avoiding errors.
            Timeout = line.split("=")[1].replace(" ","").replace("\n", "")

            if Timeout.isdigit():
                #Great! We got it.
                #However, because lilo and elilo save this in 10ths of a second, divide it by ten first.
                Timeout = int(Timeout)//10
                logger.info("GetLILOConfig(): Found bootloader timeout...")

        #Look for kernel options used globally in all the boot options.
        elif 'append' in line and '=' in line and "#" not in line and KernelOptions == "Unknown":
            #Found them! Save it to GlobalKernelOptions
            KernelOptions = ' '.join(line.split("=")[1:]).replace("\"", "").replace("\n", "")
            logger.info("GetLILOConfig(): Found global kernel options...")

        #Look for the 'boot' setting.
        elif 'boot' in line and '=' in line and '#' not in line and 'map' not in line:
            #Found it!
            Temp = line.split("=")[1].replace("\n", "")

            #Convert to a device node if we have an ID.
            if "by-id" in Temp:
                ID = Temp.split("/")[-1].replace("\n", "").replace(" ", "")

                for disk in DiskInfo.keys():
                    if DiskInfo[disk]["ID"] == ID:
                        Temp = disk
                        break

            #Check we got the device node in case we had an ID.
            if "by-id" not in Temp and "/dev/" in Temp:
                BootDisk = Temp
                logger.info("GetLILOConfig(): Found boot disk "+BootDisk+"...")

        #Look for the default OS setting.
        elif "default" in line and "=" in line and "#" not in line:
            #Found it.
            DefaultOS = line.split("=")[1].replace("\n", "")
            logger.info("GetLILOConfig(): Found default OS "+DefaultOS+"...")

    #Close the file.
    logger.info("GetLILOConfig(): Done! Returning information...")
    ConfigFile.close()

    #Find the 1st menu entry and use that if we couldn't find the default OS.
    if DefaultOS == "Unknown":
        for Entry in BootloaderInfo[OS]["MenuEntries"]["MainMenu"]["Order"]:
            if BootloaderInfo[OS]["MenuEntries"]["MainMenu"][Entry]["ID"] == 0:
                DefaultOS = Entry
                logger.info("GetGRUB2Config(): Set default OS to "+Entry+" instead. Continuing...")

    #Ignore ELILO's boot disk setting.
    if "/etc/lilo.conf" in ConfigFilePath:
        return (Timeout, KernelOptions, BootDisk, DefaultOS)

    else:
        logger.info("GetLILOConfig(): Ignoring ELILO's book disk setting, instead preferring the detected EFI partition for this OS...")
        return (Timeout, KernelOptions, DefaultOS)
