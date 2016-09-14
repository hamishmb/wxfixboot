#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Bootloader Configuration Obtaining Tools in the Startup Tools Package for WxFixBoot Version 2.0~rc1
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

class Main(): #*** Refactor all of these ***
    def FindGRUB(self, OSPartition, GRUBVersion): #*** Test this thoroughly ***
        """Find GRUB for the given OS."""
        logger.info("BootloaderConfigObtainingTools: Main().FindGRUB(): Looking for "+GRUBVersion+"...")

        #Do some setup.
        LikelyGRUBInstallDisks = (DiskInfo[OSPartition]["HostDevice"], OSPartition)

        logger.info("BootloaderConfigObtainingTools: Main().FindGRUB(): Looking in "+', '.join(LikelyGRUBInstallDisks)+"...")

        #Look for the right string for each boot loader. *** Test this ***
        if GRUBVersion == "GRUB2":
            LookFor = ("ZRr=", "TCPAf")

        else:
            LookFor = ("ZRrI", "")

        for Disk in LikelyGRUBInstallDisks:
            logger.info("BootloaderConfigObtainingTools: Main().FindGRUB(): "+DiskInfo[Disk]["Name"]+" "+', '.join(DiskInfo[Disk]["BootRecordStrings"]))

            for Line in DiskInfo[Disk]["BootRecordStrings"]:
                #Check that we have the right version of GRUB, and double check that GRUB is present.
                if Line in LookFor and "GRUB" in DiskInfo[Disk]["BootRecordStrings"]:
                    logger.info("BootloaderConfigObtainingTools: Main().FindGRUB(): Found "+GRUBVersion+" on "+Disk+"...")
                    logger.info("BootloaderConfigObtainingTools: Main().FindGRUB(): Done!")
                    return Disk

        logger.info("BootloaderConfigObtainingTools: Main().FindGRUB(): Didn't find "+GRUBVersion+" on any likely disks...")
        return "Unknown"

    def ParseGRUB2MenuData(self, MenuData="", MountPoint="", MenuEntries={}, MenuName="MainMenu", MenuIDs={}, MenuID=""):
        """Find and parse GRUB2 (EFI and BIOS) menu entries in the given line list"""
        if MenuData != "":
            logger.info("BootloaderConfigObtainingTools: Main().ParseGRUB2MenuData(): Finding and parsing menu entries in given menu data...")
            GRUBDir = ""

        else:
            logger.info("BootloaderConfigObtainingTools: Main().ParseGRUB2MenuData(): Finding and opening GRUB config file...")

            #Find grub.cfg. (Ubuntu).
            if os.path.isdir(MountPoint+"/boot/grub"):
                GRUBDir = MountPoint+"/boot/grub"

            #(Fedora, BIOS)
            elif os.path.isdir(MountPoint+"/boot/grub2"):
                GRUBDir = MountPoint+"/boot/grub2"

            #(Fedora, EFI)
            if os.path.isfile(GRUBDir+"/grub.cfg") == False and os.path.isdir(MountPoint+"/boot/efi/EFI/fedora"):
                GRUBDir = MountPoint+"/boot/efi/EFI/fedora"

            #Process menu entries, and pass the entire contents of the menu entries file to the parser.
            MenuEntriesFile = open(GRUBDir+"/grub.cfg", "r")
            MenuData = MenuEntriesFile.readlines()
            MenuEntriesFile.close()

            logger.info("BootloaderConfigObtainingTools: Main().ParseGRUB2MenuData(): Finding and parsing menu entries in "+GRUBDir+"/grub.cfg...")

        logger.debug("BootloaderConfigObtainingTools: Main().ParseGRUB2MenuData(): Parsing menu data for menu: "+MenuName+"...")

        MenuEntries[MenuName] = {}
        MenuEntries[MenuName]["Order"] = []
        MenuIDs[MenuName] = {}
        MenuIDs[MenuName]["ID"] = MenuID
        
        EntryCounter = 0
        SkipUntil = 0
        LineCounter = 0

        #Read each line.
        for Line in MenuData:
            LineCounter += 1

            #Skip some lines if needed.
            if LineCounter < SkipUntil:
                continue

            #Parse any menu entries we find.
            if "menuentry " in Line:
                logger.info("BootloaderConfigObtainingTools: Main().ParseGRUB2MenuData(): Found a menu entry. Assembling into a dictionary with self.AssembleGRUB2MenuEntry()...")
                MenuEntries = self.AssembleGRUB2MenuEntry(MenuEntries, MenuIDs, MenuData, MenuName, Line, EntryCounter)
                logger.info("BootloaderConfigObtainingTools: Main().ParseGRUB2MenuData(): Done!")

                #Increment the entry counter.
                EntryCounter += 1

            #Handle submenus correctly.
            elif "submenu " in Line:
                logger.info("BootloaderConfigObtainingTools: Main().ParseGRUB2MenuData(): Found submenu...")
                #Get the submenu's name, create a sub-dictionary for it, save its ID, and change the Value of "MenuName" to the submenu's name.
                #Keep compatibility with older versions of GRUB2.
                try:
                    SubMenuName = Line.split("'")[1].replace("\"", "").replace("\'", "")

                except IndexError:
                    SubMenuName = Line.split("\"")[1].replace("\"", "").replace("\'", "")

                #Get the entire contents of the submenu.
                logger.info("BootloaderConfigObtainingTools: Main().ParseGRUB2MenuData(): Getting the entire text content of the submenu...")
                BracketCount = 0
                SubMenuData = []

                for SubMenuDataLine in MenuData[MenuData.index(Line):]:
                    #Don't add the first line to the SubMenuData to avoid an endless recursive call.
                    if "submenu " not in SubMenuDataLine:
                        SubMenuData.append(SubMenuDataLine)

                    if "{" in SubMenuDataLine:
                        BracketCount += 1

                    elif "}" in SubMenuDataLine:
                        BracketCount -= 1

                    if BracketCount == 0:
                        break

                logger.info("BootloaderConfigObtainingTools: Main().ParseGRUB2MenuData(): Done! Processing any menu entries in the submenu with recursive call...")

                #Call this function again with the contents of the submenu, and some arguments so everything works correctly.
                MenuEntries, MenuIDs = self.ParseGRUB2MenuData(SubMenuData, MountPoint=MountPoint, MenuEntries=MenuEntries, MenuName=SubMenuName, MenuIDs=MenuIDs, MenuID=unicode(EntryCounter)+">")[1:]

                logger.info("BootloaderConfigObtainingTools: Main().ParseGRUB2MenuData(): Done! Jumping past the submenu data to avoid duplicating menu entries...")

                #Increment the entry counter.
                EntryCounter += 1

                #Skip the submenu data, and set "Menu" back to "MainMenu" again so entries are added correctly.
                SkipUntil = LineCounter+len(SubMenuData)

        logger.info("BootloaderConfigObtainingTools: Main().ParseGRUB2MenuData(): Finished!")
        return GRUBDir, MenuEntries, MenuIDs

    def AssembleGRUB2MenuEntry(self, MenuEntries, MenuIDs, MenuEntriesFileContents, Menu, Line, EntryCounter):
        """Assemble a menu entry in the dictionary for GRUB2 (BIOS and UEFI)"""
        logger.info("BootloaderConfigObtainingTools: Main().AssembleGRUB2MenuEntry(): Preparing to get menu entry info...")

        #Get the menu entry name.
        if "\'" in Line:
            MenuEntryName = Line.split("\'")[1]

        else:
            MenuEntryName = Line.split("\"")[1]

        logger.debug("BootloaderConfigObtainingTools: Main().AssembleGRUB2MenuEntry(): Menu Entry name: "+MenuEntryName+"...")

        #Get the menu entry ID.
        MenuEntries[Menu]["Order"].append(MenuEntryName)
        MenuEntries[Menu][MenuEntryName] = {}
        MenuEntries[Menu][MenuEntryName]["ID"] = MenuIDs[Menu]["ID"]+unicode(EntryCounter)

        logger.debug("BootloaderConfigObtainingTools: Main().AssembleGRUB2MenuEntry(): Menu Entry ID: "+MenuEntries[Menu][MenuEntryName]["ID"]+"...")

        #Get the full contents of the menuentry (keep adding lines to the list until we find a "}").
        logger.info("BootloaderConfigObtainingTools: Main().AssembleGRUB2MenuEntry(): Getting menu entry data...")

        MenuEntries[Menu][MenuEntryName]["RawMenuEntryData"] = []

        for MenuEntryData in MenuEntriesFileContents[MenuEntriesFileContents.index(Line):]:
            MenuEntries[Menu][MenuEntryName]["RawMenuEntryData"].append(MenuEntryData)

            if MenuEntryData.split()[-1] == "}":
                break

        #Get boot partition.
        logger.info("BootloaderConfigObtainingTools: Main().AssembleGRUB2MenuEntry(): Getting menu entry's boot partition with entry name...")

        #Try multiple methods to get this info.
        MenuEntries[Menu][MenuEntryName]["Partition"] = "Unknown"

        #Try to get it from the menu entry name (older GRUB2 versions).
        try:
            #Remove the brackets, split with " ", and grab the last element in the resulting list, which is hopefully the partition name e.g. /dev/sdc.
            MenuEntries[Menu][MenuEntryName]["Partition"] = MenuEntryName.replace(")", "").split(" (")[1].split(" ")[-1]

        except IndexError: pass

        #If this fails, try finding the UUID in the menu-entry data and converting that to a device name. *** Check this works ***
        if MenuEntries[Menu][MenuEntryName]["Partition"] == "Unknown" or "/dev/" not in MenuEntries[Menu][MenuEntryName]["Partition"]:
            logger.info("BootloaderConfigObtainingTools: Main().AssembleGRUB2MenuEntry(): Getting menu entry's boot partition with UUID...")
            UUID = ""

            for EachLine in MenuEntries[Menu][MenuEntryName]["RawMenuEntryData"]:
                if "search " in EachLine:
                    UUID = EachLine.split()[-1]
                    logger.info("BootloaderConfigObtainingTools: Main().AssembleGRUB2MenuEntry(): Found UUID...")
                    break

            if UUID != "":
                #Convert to device name if possible.
                logger.info("BootloaderConfigObtainingTools: Main().AssembleGRUB2MenuEntry(): Matching UUID to disk...")
                for Disk in DiskInfo.keys():
                    if DiskInfo[Disk]["UUID"] == UUID:
                        MenuEntries[Menu][MenuEntryName]["Partition"] = Disk

        #If THAT fails, try to use the "set root=" line to find the device name. *** Check this works right ***
        if MenuEntries[Menu][MenuEntryName]["Partition"] == "Unknown" or "/dev/" not in MenuEntries[Menu][MenuEntryName]["Partition"]:
            logger.info("BootloaderConfigObtainingTools: Main().AssembleGRUB2MenuEntry(): Getting menu entry's boot partition with GRUB2's 'set root=' line...")
            RootLine = ""

            for EachLine in MenuEntries[Menu][MenuEntryName]["RawMenuEntryData"]:
                if "set root" in EachLine:
                    RootLine = EachLine
                    logger.info("BootloaderConfigObtainingTools: Main().AssembleGRUB2MenuEntry(): Found GRUB2's 'set root=' line...")
                    break

            if RootLine != "":
                #Get the numbers used in this line.
                logger.info("BootloaderConfigObtainingTools: Main().AssembleGRUB2MenuEntry(): Finding GRUB device name numbers...")
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
            logger.error("BootloaderConfigObtainingTools: Main().AssembleGRUB2MenuEntry(): Couldn't find boot partition for menu entry! Continuing anyway...")

        else:
            logger.debug("BootloaderConfigObtainingTools: Main().AssembleGRUB2MenuEntry(): Menu Entry Boot Partition: "+MenuEntries[Menu][MenuEntryName]["Partition"]+"...")

        #Get the kernel options for this menuentry.
        logger.info("BootloaderConfigObtainingTools: Main().AssembleGRUB2MenuEntry(): Getting kernel options...")

        MenuEntries[Menu][MenuEntryName]["KernelOptions"] = ["Unknown"]

        for Line in MenuEntries[Menu][MenuEntryName]["RawMenuEntryData"]:
            if "linux" in Line:
                MenuEntries[Menu][MenuEntryName]["KernelOptions"] = Line.split()[3:]

        #Check we got them.
        if MenuEntries[Menu][MenuEntryName]["KernelOptions"] == ["Unknown"]:
            logger.error("BootloaderConfigObtainingTools: Main().AssembleGRUB2MenuEntry(): Couldn't find kernel options for menu entry! Continuing anyway...")

        else:
            logger.debug("BootloaderConfigObtainingTools: Main().AssembleGRUB2MenuEntry(): Menu Entry Kernel Options: "+', '.join(MenuEntries[Menu][MenuEntryName]["KernelOptions"])+"...")

        return MenuEntries

    def GetGRUB2Config(self, ConfigFilePath, GRUBEnvironmentFilePath, MenuEntries):
        """Get important bits of config from grub2 (MBR or UEFI)"""
        logger.info("BootloaderConfigObtainingTools: Main().GetGRUB2Config(): Getting config at "+ConfigFilePath+"...")

        #Set temporary vars
        Timeout = "Unknown"
        KernelOptions = "Unknown"
        DefaultOS = "Unknown"

        #Open the config file in read mode, so we can save the important bits of config.
        logger.info("BootloaderConfigObtainingTools: Main().GetGRUB2Config(): Getting config...")
        ConfigFile = open(ConfigFilePath, 'r')

        #Loop through each line in the file, paying attention only to the important ones.
        for Line in ConfigFile:
            #Look for the timeout setting.
            if 'GRUB_TIMEOUT' in Line and '=' in Line:
                #Get only the numbers.
                Temp = Line.split("=")[1].replace("\n", "")

                #Check this worked properly.
                if Temp.isdigit():
                    #Great! We got it.
                    logger.info("BootloaderConfigObtainingTools: Main().GetGRUB2Config(): Found bootloader timeout...")
                    Timeout = int(Temp)

            #Look for kernel options used globally in all the boot options.
            elif 'GRUB_CMDLINE_LINUX' in Line and '=' in Line:
                #Split by ' or ", and check the result isn't an empty string in case there was nothing there.
                if "\'" in Line:
                    Temp = Line.split("\'")[1]

                elif "\"" in Line:
                    Temp = Line.split("\"")[1]

                if Temp != "":
                    KernelOptions = Temp
                    logger.info("BootloaderConfigObtainingTools: Main().GetGRUB2Config(): Found global kernel options...")

            #Look for default OS setting.
            elif "GRUB_DEFAULT" in Line and "=" in Line:
                #Setup.
                MatchByName = False
                MatchByID = False

                #If this is an integer or string that == "saved", we need to match it to GRUB's grub.cfg menuentries.
                logger.info("BootloaderConfigObtainingTools: Main().GetGRUB2Config(): Found default OS line....")
                GRUBDefault = Line.split("=")[1].replace("\"", "").replace("\'", "").replace("\n", "")

                if GRUBDefault.isdigit() or ">" in GRUBDefault:
                    #Match By ID.
                    MatchByID = True

                elif GRUBDefault == "saved":
                    #Find the corresponding GRUB menuentry, matching by name or ID.
                    logger.info("BootloaderConfigObtainingTools: Main().GetGRUB2Config(): Looking for default OS in GRUB environment file...")
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
                    logger.info("BootloaderConfigObtainingTools: Main().GetGRUB2Config(): Matching default OS by ID...")
                    for Menu in MenuEntries.keys():
                        for OS in MenuEntries[Menu]["Order"]:
                            if MenuEntries[Menu][OS]["ID"] == GRUBDefault:
                                DefaultOS = OS
                                break

                if MatchByName:
                    #Check in the menuentries list.
                    logger.info("BootloaderConfigObtainingTools: Main().GetGRUB2Config(): Finding default OS by name...")
                    Found = False

                    for Menu in MenuEntries.keys():
                        for MenuEntry in MenuEntries[Menu]["Order"]:
                            if GRUBDefault == MenuEntry:
                                DefaultOS = GRUBDefault
                                Found = True

                    if Found:
                        logger.info("BootloaderConfigObtainingTools: Main().GetGRUB2Config(): Found default OS by name...")

                    else:
                        logger.warning("BootloaderConfigObtainingTools: Main().GetGRUB2Config(): Didn't find default OS by name, setting it to the 1st menu entry instead...")

                        #Find the 1st menu entry.
                        for Entry in MenuEntries["MainMenu"]["Order"]:
                            if MenuEntries["MainMenu"][Entry]["ID"] == 0:
                                DefaultOS = Entry
                                logger.info("BootloaderConfigObtainingTools: Main().GetGRUB2Config(): Set default OS to "+Entry+" instead. Continuing...")

                logger.info("BootloaderConfigObtainingTools: Main().GetGRUB2Config(): Done!")

        #Close the file.
        logger.info("BootloaderConfigObtainingTools: Main().GetGRUB2Config(): Done! Returning information...")
        ConfigFile.close()

        return (Timeout, KernelOptions, DefaultOS)

    def ParseGRUBLEGACYMenuEntries(self, MenuEntriesFilePath): #*** Test this ***
        """Find and parse GRUB LEGACY menu entries."""
        logger.info("BootloaderConfigObtainingTools: Main().ParseGRUBLEGACYMenuEntries(): Finding and parsing menu entries...")

        #Open the menu entries file to find and save all the menu entries.
        MenuEntriesFile = open(MenuEntriesFilePath, "r")
        MenuEntriesFileContents = MenuEntriesFile.readlines()
        MenuEntries = {}
        Menu = "MainMenu"
        MenuEntries[Menu] = {}
        MenuEntries[Menu]["Order"] = []
        MenuIDs = {}
        MenuIDs[Menu] = {}
        MenuIDs[Menu]["ID"] = ""
        MenuData = {}
        MenuData[Menu] = {}
        MenuData[Menu]["EntryCounter"] = 0
        SkipUntil = 0
        LineCounter = 0

        #Read each line in the file.
        for Line in MenuEntriesFileContents:
            LineCounter += 1

            #Process all menu entries.
            if "title " in Line:
                logger.info("BootloaderConfigObtainingTools: Main().ParseGRUBLEGACYMenuEntries(): Found a menu entry. Assembling into a dictionary with self.AssembleGRUBLEGACYMenuEntry()...")
                MenuEntries, MenuData[Menu]["EntryCounter"] = self.AssembleGRUBLEGACYMenuEntry(MenuEntries, MenuIDs, MenuEntriesFileContents, Menu, Line, MenuData[Menu]["EntryCounter"])
                logger.info("BootloaderConfigObtainingTools: Main().ParseGRUBLEGACYMenuEntries(): Done!")

        #Close the file.
        logger.info("BootloaderConfigObtainingTools: Main().ParseGRUBLEGACYMenuEntries(): Finished!")
        MenuEntriesFile.close()
        return MenuEntries, MenuIDs

    def AssembleGRUBLEGACYMenuEntry(self, MenuEntries, MenuIDs, MenuEntriesFileContents, Menu, Line, EntryCounter): #*** Refactor ***
        """Assemble a menu entry in the dictionary for GRUB LEGACY"""
        logger.info("BootloaderConfigObtainingTools: Main().AssembleGRUBLEGACYMenuEntry(): Preparing to get menu entry info...")
        MenuEntry = ' '.join(Line.split()[1:])

        MenuEntries[Menu]["Order"].append(MenuEntry)
        MenuEntries[Menu][MenuEntry] = {}
        MenuEntries[Menu][MenuEntry]["ID"] = MenuIDs[Menu]["ID"]+unicode(EntryCounter)

        MenuEntries[Menu][MenuEntry]["RawMenuEntryData"] = []

        #Get the full contents of the menuentry (keep adding lines to the list until we find "title").
        logger.info("BootloaderConfigObtainingTools: Main().AssembleGRUBLEGACYMenuEntry(): Getting menu entry data...")
        for MenuEntryData in MenuEntriesFileContents[MenuEntriesFileContents.index(Line):]:
            MenuEntries[Menu][MenuEntry]["RawMenuEntryData"].append(MenuEntryData)

            if "title" in MenuEntryData:
                #Remove the last line.
                MenuEntries[Menu][MenuEntry]["RawMenuEntryData"].pop()
                break

        MenuEntries[Menu][MenuEntry]["Partition"] = "Unknown"
        MenuEntries[Menu][MenuEntry]["KernelOptions"] = ["Unknown"]

        logger.info("BootloaderConfigObtainingTools: Main().AssembleGRUBLEGACYMenuEntry(): Getting menu entry boot partition and kernel options...")
        try:
            for Line in MenuEntries[Menu][MenuEntry]["RawMenuEntryData"]:
                if "kernel" in Line:
                    #Get the partition.
                    Temp = Line.split()[2]

                    #If we have a UUID, convert it into a device node.
                    if "UUID=" in Temp:
                        UUID = Temp.split("=")[3]

                        for Disk in DiskInfo.keys():
                            if DiskInfo[Disk]["UUID"] == Temp:
                                MenuEntries[Menu][MenuEntry]["Partition"] = DiskInfo[Disk]["UUID"]

                    else:
                        MenuEntries[Menu][MenuEntry]["Partition"] = Temp

                    logger.info("BootloaderConfigObtainingTools: Main().AssembleGRUBLEGACYMenuEntry(): Found boot partition...")
                    logger.info("BootloaderConfigObtainingTools: Main().AssembleGRUBLEGACYMenuEntry(): Found kernel options...")
                    MenuEntries[Menu][MenuEntry]["KernelOptions"] = Line.split()[3:]

        except IndexError:
            pass

        EntryCounter += 1

        return MenuEntries, EntryCounter

    def GetGRUBLEGACYConfig(self, ConfigFilePath):
        """Get important bits of config from grub-legacy"""
        logger.info("BootloaderConfigObtainingTools: Main().GetGRUBLEGACYConfig(): Getting config at "+ConfigFilePath+"...")

        #In this case, the only useful info is the timeout, so just get this.
        #Set temporary vars
        Timeout = "Unknown"

        #Open the file in read mode, so we can save the important bits of config.
        ConfigFile = open(ConfigFilePath, 'r')

        #Look for the timeout setting.
        for Line in ConfigFile:
            if 'timeout' in Line and 'sec' not in Line:
                #Found it!
                Timeout = Line.split()[1].replace('\n', '')

                if Timeout.isdigit():
                    #Great! We got it.
                    logger.info("BootloaderConfigObtainingTools: Main().GetGRUBLEGACYConfig(): Found bootloader time out...")
                    Timeout = int(Timeout)

                #Exit the loop to save time.
                break

        #Close the file.
        logger.info("BootloaderConfigObtainingTools: Main().GetGRUBLEGACYConfig(): Done! Returning Information...")
        ConfigFile.close()

        return Timeout

    def ParseLILOMenuEntries(self, MenuEntriesFilePath):
        """Find and parse LILO and ELILO menu entries."""
        logger.info("BootloaderConfigObtainingTools: Main().ParseLILOMenuEntries(): Finding and parsing menu entries...")

        #Open the menu entries file to find and save all the menu entries.
        MenuEntriesFile = open(MenuEntriesFilePath, "r")
        MenuEntriesFileContents = MenuEntriesFile.readlines()
        MenuEntries = {}
        Menu = "MainMenu"
        MenuEntries[Menu] = {}
        MenuEntries[Menu]["Order"] = []
        MenuIDs = {}
        MenuIDs[Menu] = {}
        MenuIDs[Menu]["ID"] = ""
        MenuData = {}
        MenuData[Menu] = {}
        MenuData[Menu]["EntryCounter"] = 0
        SkipUntil = 0
        LineCounter = 0

        #Read each line.
        for Line in MenuEntriesFileContents:
            LineCounter += 1

            #Process all menu entries.
            if "image" in Line and "#" not in Line:
                logger.info("BootloaderConfigObtainingTools: Main().ParseLILOMenuEntries(): Found a menu entry. Assembling into a dictionary with self.AssembleLILOMenuEntry()...")
                MenuEntries, MenuData[Menu]["EntryCounter"] = self.AssembleLILOMenuEntry(MenuEntries, MenuIDs, MenuEntriesFileContents, Menu, Line, MenuData[Menu]["EntryCounter"])
                logger.info("BootloaderConfigObtainingTools: Main().ParseLILOMenuEntries(): Done!")

        #Close the file.
        logger.info("BootloaderConfigObtainingTools: Main().ParseLILOMenuEntries(): Finished!")
        MenuEntriesFile.close()
        return MenuEntries, MenuIDs

    def AssembleLILOMenuEntry(self, MenuEntries, MenuIDs, MenuEntriesFileContents, Menu, Line, EntryCounter): #*** Refactor ***
        """Assemble a menu entry in the dictionary for LILO/ELILO"""
        logger.info("BootloaderConfigObtainingTools: Main().AssembleLILOMenuEntry(): Preparing to get menu entry info...")

        RawMenuEntryData = []

        #Get the full contents of the menuentry (keep adding lines to the list until we find another menu entry).
        logger.info("BootloaderConfigObtainingTools: Main().AssembleLILOMenuEntry(): Getting menu entry data...")
        for MenuEntryData in MenuEntriesFileContents[MenuEntriesFileContents.index(Line):]:
            RawMenuEntryData.append(MenuEntryData)

            if "label" in MenuEntryData:
                MenuEntry = MenuEntryData.split("=")[1].replace("\n", "")

            if MenuEntryData != Line and "image" in MenuEntryData.split() and "=" in MenuEntryData.split() and "#" not in MenuEntryData.split():
                #Remove the last line.
                RawMenuEntryData.pop()
                break

        MenuEntries[Menu][MenuEntry] = {}
        MenuEntries[Menu]["Order"].append(MenuEntry)
        MenuEntries[Menu][MenuEntry]["RawMenuEntryData"] = RawMenuEntryData
        MenuEntries[Menu][MenuEntry]["ID"] = MenuIDs[Menu]["ID"]+unicode(EntryCounter)
        MenuEntries[Menu][MenuEntry]["Partition"] = "Unknown"
        MenuEntries[Menu][MenuEntry]["KernelOptions"] = ["Unknown"]

        try:
            for Line in MenuEntries[Menu][MenuEntry]["RawMenuEntryData"]:
                if "root" in Line:
                    #Get the partition.
                    Temp = '='.join(Line.split("=")[1:])

                    #If we get a UUID, convert it to a device node.
                    if "UUID=" in Temp:
                        UUID = Temp.split("=")[1].replace("\"", "").replace("\n", "")
                        logger.info("BootloaderConfigObtainingTools: Main().AssembleLILOMenuEntry(): Found UUID "+UUID+". Finding device node...")

                        for Disk in DiskInfo.keys():
                            if DiskInfo[Disk]["UUID"] == UUID:
                                MenuEntries[Menu][MenuEntry]["Partition"] = Disk
                                logger.info("BootloaderConfigObtainingTools: Main().AssembleLILOMenuEntry(): Found device node "+Disk+". Continuing...")

                    else:
                        MenuEntries[Menu][MenuEntry]["Partition"] = Temp

                    logger.info("BootloaderConfigObtainingTools: Main().AssembleLILOMenuEntry(): Found boot partition...")

                elif "append" in Line:
                    #Get the kernel options.
                    logger.info("BootloaderConfigObtainingTools: Main().AssembleLILOMenuEntry(): Found kernel options...")
                    MenuEntries[Menu][MenuEntry]["KernelOptions"] = Line.split("=")[1].replace("\"", "").split()

        except IndexError:
            pass

        EntryCounter += 1

        return MenuEntries, EntryCounter

    def GetLILOConfig(self, ConfigFilePath, OS):
        """Get important bits of config from lilo and elilo"""
        logger.info("BootloaderConfigObtainingTools: Main().GetLILOConfig(): Getting config at "+ConfigFilePath+"...")

        #Set temporary vars
        Timeout = "Unknown"
        KernelOptions = "Unknown"
        BootDisk = "Unknown"
        DefaultOS = "Unknown"

        #Open the file in read mode, so we can save the important bits of config.
        ConfigFile = open(ConfigFilePath, 'r')

        #Loop through each line in the file, paying attention only to the important ones.
        for Line in ConfigFile:
            #Look for the delay/timeout setting.
            if ('delay' in Line or 'timeout' in Line) and '=' in Line and "#" not in Line:
                #Save it, carefully avoiding errors.
                Timeout = Line.split("=")[1].replace(" ","").replace("\n", "")

                if Timeout.isdigit():
                    #Great! We got it.
                    #However, because lilo and elilo save this in 10ths of a second, divide it by ten first.
                    Timeout = int(Timeout)//10
                    logger.info("BootloaderConfigObtainingTools: Main().GetLILOConfig(): Found bootloader timeout...")

            #Look for kernel options used globally in all the boot options.
            elif 'append' in Line and '=' in Line and "#" not in Line:
                #Found them! Save it to GlobalKernelOptions
                KernelOptions = ' '.join(Line.split("=")[1:]).replace("\"", "").replace("\n", "")
                logger.info("BootloaderConfigObtainingTools: Main().GetLILOConfig(): Found global kernel options...")

            #Look for the 'boot' setting.
            elif 'boot' in Line and '=' in Line and '#' not in Line and 'map' not in Line:
                #Found it!
                Temp = Line.split("=")[1].replace("\n", "")

                #Convert to a device node if we have an ID.
                if "by-id" in Temp:
                    ID = Temp.split("/")[-1].replace("\n", "").replace(" ", "")
                    for Disk in DiskInfo.keys():
                        if DiskInfo[Disk]["ID"] == ID:
                            Temp = Disk
                            break

                #Check we got the device node in case we had an ID.
                if "by-id" not in Temp and "/dev/" in Temp:
                    BootDisk = Temp
                    logger.info("BootloaderConfigObtainingTools: Main().GetLILOConfig(): Found boot disk "+BootDisk+"...")

            #Look for the default OS setting.
            elif "default" in Line and "=" in Line and "#" not in Line:
                #Found it.
                DefaultOS = Line.split("=")[1].replace("\n", "")
                logger.info("BootloaderConfigObtainingTools: Main().GetLILOConfig(): Found default OS "+DefaultOS+"...")

        #Close the file.
        logger.info("BootloaderConfigObtainingTools: Main().GetLILOConfig(): Done! Returning information...")
        ConfigFile.close()

        #Find the 1st menu entry and use that if we couldn't find the default OS.
        if DefaultOS == "Unknown":
            for Entry in BootloaderInfo[OS]["MenuEntries"]["MainMenu"]["Order"]:
                if BootloaderInfo[OS]["MenuEntries"]["MainMenu"][Entry]["ID"] == 0:
                    DefaultOS = Entry
                    logger.info("BootloaderConfigObtainingTools: Main().GetGRUB2Config(): Set default OS to "+Entry+" instead. Continuing...")

        #Ignore ELILO's boot disk setting.
        if "/etc/lilo.conf" in ConfigFilePath:
            return (Timeout, KernelOptions, BootDisk, DefaultOS)

        else:
            logger.info("BootloaderConfigObtainingTools: Main().GetLILOConfig(): Ignoring ELILO's book disk setting, instead preferring the detected EFI partition for this OS...")
            return (Timeout, KernelOptions, DefaultOS)
