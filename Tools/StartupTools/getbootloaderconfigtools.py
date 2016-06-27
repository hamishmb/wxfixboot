#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Bootloader Configuration Obtaining Tools in the Bootloader Tools Package in the Backend Tools package for WxFixBoot Version 2.0~pre2
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

        #Look for the right string for each boot loader.
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

        logger.info("BootloaderConfigObtainingTools: Main().FindGRUB(): Didn't find "+GRUBVersion+"...")
        return "Unknown"

    def ParseGRUB2MenuEntries(self, MenuEntriesFilePath): #*** Reduce duplication, perhaps with a recursive call ***
        """Find and parse GRUB2 (EFI and BIOS) menu entries."""
        logger.info("BootloaderConfigObtainingTools: Main().ParseGRUB2MenuEntries(): Finding and parsing menu entries...")

        #Open the menu entries file to find and save all the menu entries.
        MenuEntriesFile = open(MenuEntriesFilePath, "r")
        MenuEntriesFileContents = MenuEntriesFile.readlines()
        MenuEntries = {}
        Menu = "MainMenu"
        MenuEntries[Menu] = {}
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

            #Skip some lines if needed.
            if LineCounter < SkipUntil:
                continue

            #Parse any menu entries we find.
            if "menuentry " in Line:
                logger.info("BootloaderConfigObtainingTools: Main().ParseGRUB2MenuEntries(): Found a menu entry. Assembling into a dictionary with self.AssembleGRUB2MenuEntry()...")
                MenuEntries, MenuData[Menu]["EntryCounter"] = self.AssembleGRUB2MenuEntry(MenuEntries, MenuIDs, MenuEntriesFileContents, Menu, Line, MenuData[Menu]["EntryCounter"])
                logger.info("BootloaderConfigObtainingTools: Main().ParseGRUB2MenuEntries(): Done!")

            #Handle submenus correctly.
            elif "submenu " in Line:
                logger.info("BootloaderConfigObtainingTools: Main().ParseGRUB2MenuEntries(): Found submenu...")
                #Get the submenu, create a sub-dictionary for it, save its ID, and change the Value of "Menu" to the submenu's name.
                SubMenu = ' '.join(Line.split(" ")[1:-1]).replace("\"", "")
                MenuEntries[SubMenu] = {}
                MenuIDs[SubMenu] = {}
                MenuIDs[SubMenu]["ID"] = unicode(MenuData[Menu]["EntryCounter"])+">"
                MenuData[Menu]["EntryCounter"] += 1
                Menu = SubMenu

                #Get the entire contents of the submenu.
                logger.info("BootloaderConfigObtainingTools: Main().ParseGRUB2MenuEntries(): Getting the entire text content of the submenu...")
                BracketCount = 0
                MenuData[Menu] = {}
                MenuData[Menu]["EntryCounter"] = 0
                MenuData[Menu]["RawMenuData"] = []

                for SubMenuData in MenuEntriesFileContents[MenuEntriesFileContents.index(Line):]:
                    MenuData[Menu]["RawMenuData"].append(SubMenuData)

                    if "{" in SubMenuData:
                        BracketCount += 1

                    elif "}" in SubMenuData:
                        BracketCount -= 1

                    if BracketCount == 0:
                        break

                logger.info("BootloaderConfigObtainingTools: Main().ParseGRUB2MenuEntries(): Done! Processing any menu entries in the submenu...")

                #Process any menu entries in the submenu.
                for SubLine in MenuData[Menu]["RawMenuData"]:
                    if "menuentry " in SubLine:
                        MenuEntries, MenuData[Menu]["EntryCounter"] = self.AssembleGRUB2MenuEntry(MenuEntries, MenuIDs, MenuEntriesFileContents, Menu, SubLine, MenuData[Menu]["EntryCounter"])

                logger.info("BootloaderConfigObtainingTools: Main().ParseGRUB2MenuEntries(): Done! Jumping past the submenu data to avoid duplicating menu entries...")
                #Skip the submenu data, and set "Menu" back to "MainMenu" again so entries are added correctly.
                SkipUntil = LineCounter+len(MenuData[Menu]["RawMenuData"])

                Menu = "MainMenu"

        #Close the file.
        logger.info("BootloaderConfigObtainingTools: Main().ParseGRUB2MenuEntries(): Finished!")
        MenuEntriesFile.close()
        return MenuEntries, MenuIDs

    def AssembleGRUB2MenuEntry(self, MenuEntries, MenuIDs, MenuEntriesFileContents, Menu, Line, EntryCounter):
        """Assemble a menu entry in the dictionary for GRUB2 (BIOS and UEFI)"""
        logger.info("BootloaderConfigObtainingTools: Main().AssembleGRUB2MenuEntry(): Preparing to get menu entry info...")
        print(Line)
        MenuEntry = Line.split("\'")[1]
        Temp = MenuEntry.replace(")", "").split(" (")

        MenuEntries[Menu][MenuEntry] = {}
        MenuEntries[Menu][MenuEntry]["ID"] = MenuIDs[Menu]["ID"]+unicode(EntryCounter)

        logger.info("BootloaderConfigObtainingTools: Main().AssembleGRUB2MenuEntry(): Getting menu entry's boot partition...")

        try:
            MenuEntries[Menu][MenuEntry]["Partition"] = Temp[1].split(" ")[-1]

        except IndexError:
            MenuEntries[Menu][MenuEntry]["Partition"] = "Unknown"

        MenuEntries[Menu][MenuEntry]["RawMenuEntryData"] = []

        #Get the full contents of the menuentry (keep adding lines to the list until we find a "}").
        logger.info("BootloaderConfigObtainingTools: Main().AssembleGRUB2MenuEntry(): Getting menu entry data...")

        for MenuEntryData in MenuEntriesFileContents[MenuEntriesFileContents.index(Line):]:
            MenuEntries[Menu][MenuEntry]["RawMenuEntryData"].append(MenuEntryData)

            if MenuEntryData.split()[-1] == "}":
                break

        logger.info("BootloaderConfigObtainingTools: Main().AssembleGRUB2MenuEntry(): Getting kernel options...")
        MenuEntries[Menu][MenuEntry]["KernelOptions"] = ["Unknown"]

        for Line in MenuEntries[Menu][MenuEntry]["RawMenuEntryData"]:
            if "linux" in Line:
                MenuEntries[Menu][MenuEntry]["KernelOptions"] = Line.split()[3:]

        EntryCounter += 1

        return MenuEntries, EntryCounter

    def GetGRUB2Config(self, ConfigFilePath, GRUBEnvironmentFilePath, MenuEntries): #*** Refactor, and reduce duplication  ***
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
                #Found it! Save it, carefully avoiding errors.
                Timeout = Line.split("=")[1].replace("\n", "")

                if Timeout.isdigit():
                    #Great! We got it.
                    logger.info("BootloaderConfigObtainingTools: Main().GetGRUB2Config(): Found bootloader timeout...")
                    Timeout = int(Timeout)

            #Look for kernel options used globally in all the boot options.
            elif 'GRUB_CMDLINE_LINUX' in Line and '=' in Line:
                #Found them! Save them.
                Temp = '='.join(Line.split("=")[1:]).replace("\'", "").replace("\n", "")

                if Temp != "\"\"":
                    KernelOptions = Temp

                    logger.info("BootloaderConfigObtainingTools: Main().GetGRUB2Config(): Found global kernel options...")

            #Look for default os setting,
            elif "GRUB_DEFAULT" in Line and "=" in Line:
                #If this is an integer or string that == "saved", we need to match it to GRUB's grub.cfg menuentries.
                logger.info("BootloaderConfigObtainingTools: Main().GetGRUB2Config(): Found default OS line....")
                Temp = Line.split("=")[1].replace("\"", "").replace("\'", "").replace("\n", "")

                if Temp.isdigit() or ">" in Temp:
                    #Find the corresponding GRUB menuentry, matching by ID. *** What if we don't get a match? ***
                    logger.info("BootloaderConfigObtainingTools: Main().GetGRUB2Config(): Finding default OS by index...")
                    for Menu in MenuEntries.keys():
                        for OS in MenuEntries[Menu].keys():
                            if MenuEntries[Menu][OS]["ID"] == Temp:
                                DefaultOS = OS
                                break

                elif Temp == "saved":
                    #Find the corresponding GRUB menuentry, matching by name or ID.
                    logger.info("BootloaderConfigObtainingTools: Main().GetGRUB2Config(): Finding default OS in GRUB environment file...")
                    GRUBEnvironmentFile = open(GRUBEnvironmentFilePath, "r")

                    for Var in GRUBEnvironmentFile:
                        if "saved_entry=" in Var or "default=" in Var:
                            DefaultOS = Var.split("=")[1].replace("\n", "")

                    if DefaultOS.isdigit() or ">" in DefaultOS:
                        #Find the corresponding GRUB menuentry, matching by ID. *** What if we don't get a match? ***
                        logger.info("BootloaderConfigObtainingTools: Main().GetGRUB2Config(): Finding default OS by index...")
                        for Menu in MenuEntries.keys():
                            for OS in MenuEntries[Menu].keys():
                                if MenuEntries[Menu][OS]["ID"] == DefaultOS:
                                    DefaultOS = OS
                                    break

                    else:
                        #Check it is in the menuentries list.
                        logger.info("BootloaderConfigObtainingTools: Main().GetGRUB2Config(): Finding default OS by name...")
                        Found = False

                        for Menu in MenuEntries.keys():
                            for MenuEntry in MenuEntries[Menu].keys():
                                if DefaultOS == MenuEntry:
                                    Found = True

                        if not Found:
                            logger.warning("BootloaderConfigObtainingTools: Main().GetGRUB2Config(): Didn't find default OS by name...")
                            DefaultOS = "Unknown"

                        else:
                            logger.info("BootloaderConfigObtainingTools: Main().GetGRUB2Config(): Found default OS by name...")

                else:
                    #Check it is in the menuentries list.
                    logger.info("BootloaderConfigObtainingTools: Main().GetGRUB2Config(): Finding default OS by name...")
                    Found = False

                    for Menu in MenuEntries.keys():
                        for MenuEntry in MenuEntries[Menu].keys():
                            if DefaultOS == MenuEntry:
                                Found = True

                    if Found:
                        logger.info("BootloaderConfigObtainingTools: Main().GetGRUB2Config(): Found default OS by name...")
                        DefaultOS = Temp

                    else:
                        logger.warning("BootloaderConfigObtainingTools: Main().GetGRUB2Config(): Didn't find default OS by name...")

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

    def AssembleGRUBLEGACYMenuEntry(self, MenuEntries, MenuIDs, MenuEntriesFileContents, Menu, Line, EntryCounter):
        """Assemble a menu entry in the dictionary for GRUB LEGACY"""
        logger.info("BootloaderConfigObtainingTools: Main().AssembleGRUBLEGACYMenuEntry(): Preparing to get menu entry info...")
        MenuEntry = ' '.join(Line.split()[1:])

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
                MenuEntry = MenuEntryData.split("=")[1]

            if "image" in MenuEntryData.split() and "=" in MenuEntryData.split() and "#" not in MenuEntryData.split():
                #Remove the last line.
                RawMenuEntryData.pop()
                break

        MenuEntries[Menu][MenuEntry] = {}
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
                        UUID = Temp.split("=")[1].replace("\"", "")

                        for Disk in DiskInfo.keys():
                            if DiskInfo[Disk]["UUID"] == Temp:
                                MenuEntries[Menu][MenuEntry]["Partition"] = DiskInfo[Disk]["UUID"]

                    else:
                        MenuEntries[Menu][MenuEntry]["Partition"] = Temp

                    logger.info("BootloaderConfigObtainingTools: Main().AssembleLILOMenuEntry(): Found boot partition...")

                elif "append" in Line:
                    #Get the kernel options.
                    logger.info("BootloaderConfigObtainingTools: Main().AssembleLILOMenuEntry(): Found kernel options...")
                    MenuEntries[Menu][MenuEntry]["KernelOptions"] = Line.split("=")[1].replace("\"", "")

        except IndexError:
            pass

        EntryCounter += 1

        return MenuEntries, EntryCounter

    def GetLILOConfig(self, ConfigFilePath):
        """Get important bits of config from lilo and elilo"""
        logger.info("BootloaderConfigObtainingTools: Main().GetLILOConfig(): Getting config at "+ConfigFilePath+"...")

        #Set temporary vars
        Timeout = "Unknown"
        KernelOptions = "Unknown"
        BootDisk = "Unknown"

        #Open the file in read mode, so we can save the important bits of config.
        ConfigFile = open(ConfigFilePath, 'r')

        #Loop through each line in the file, paying attention only to the important ones.
        for Line in ConfigFile:
            #Look for the delay/timeout setting.
            if ('delay' in Line or 'timeout' in Line) and '=' in Line:
                #Save it, carefully avoiding errors.
                Timeout = Line.split("=")[1].replace(" ","")

                if Timeout.isdigit():
                    #Great! We got it.
                    #However, because lilo and elilo save this in 10ths of a second, divide it by ten first.
                    Timeout = int(Timeout)//10
                    logger.info("BootloaderConfigObtainingTools: Main().GetLILOConfig(): Found bootloader timeout...")

            #Look for kernel options used globally in all the boot options.
            elif 'append' in Line and '=' in Line:
                #Found them! Save it to GlobalKernelOptions
                KernelOptions = ' '.join(Line.split("=")[1:]).replace("\"", "")
                logger.info("BootloaderConfigObtainingTools: Main().GetLILOConfig(): Found global kernel options...")

            #Look for the 'boot' setting.
            elif 'boot' in Line and '=' in Line and '#' not in Line and 'map' not in Line:
                #Found it!
                Temp = Line.split("=")[1]

                #Convert to a device node if we have an ID.
                if "by-id" in Temp:
                    ID = Temp.split("/")[-1].replace("\n", "").replace(" ", "")
                    for Disk in DiskInfo.keys():
                        if DiskInfo[Disk]["ID"] == ID:
                            Temp = Disk
                            break

                #Check we got the device node in case we had an ID.
                if "by-id" not in Temp:
                    BootDisk = Temp
                    logger.info("BootloaderConfigObtainingTools: Main().GetLILOConfig(): Found boot disk "+BootDisk+"...")

            #Look for the default OS setting.
            elif "default" in Line and "=" in Line and "#" not in Line:
                #Found it.
                DefaultOS = Line.split("=")[1]
                logger.info("BootloaderConfigObtainingTools: Main().GetLILOConfig(): Found default OS "+DefaultOS+"...")

        #Close the file.
        logger.info("BootloaderConfigObtainingTools: Main().GetLILOConfig(): Done! Returning information...")
        ConfigFile.close()

        #Ignore ELILO's boot disk setting.
        if "/etc/lilo.conf" in ConfigFilePath:
            return (Timeout, KernelOptions, BootDisk, DefaultOS)

        else:
            logger.info("BootloaderConfigObtainingTools: Main().GetLILOConfig(): Ignoring ELILO's book disk setting, instead preferring the detected EFI partition for this OS...")
            return (Timeout, KernelOptions, DefaultOS)
