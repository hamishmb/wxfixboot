#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Bootloader Configuration Obtaining Tools in the Bootloader Tools Package in the Backend Tools package for WxFixBoot Version 2.0~pre1
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

class Main(): #*** Refactor all of these *** *** Doesn't seem to find bootloader time out *** *** Sometimes doesn't find kernel options ***
    def GetGRUBLEGACYConfig(self, ConfigFilePath): #*** Add logging messages *** *** Can we get kernel options here? ***
        """Get important bits of config from grub-legacy"""
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
                    Timeout = int(Timeout)

                #Exit the loop to save time.
                break

        #Close the file.
        ConfigFile.close()

        return Timeout

    def FindGRUB(self, OSPartition, GRUBVersion): #*** Add logging messages *** *** Test this thoroughly ***
        """Find GRUB for the given OS."""
        #Do some setup.
        LikelyGRUBInstallDisks = (DiskInfo[OSPartition]["HostDisk"], OSPartition)
        FoundGRUB = False
        FoundRightVersion = False

        #Look for the right string for each boot loader.
        if GRUBVersion == "GRUB2":
            LookFor = "ZRr="

        else:
            LookFor = "ZRrI"

        for Disk in LikelyGRUBInstallDisks:
            for Line in DiskInfo[Disk]["BootRecordStrings"]:
                #Check that we have the right version of GRUB, and double check that GRUB is present.
                if LookFor in Line:
                    FoundRightVersion = True

                elif "GRUB" in Line:
                    FoundGRUB = True
                    BootDisk = Disk

                #Break out of the loop if possible to save time.
                if FoundRightVersion and FoundGRUB:
                    break

            #Break out of the loop if possbile to save time.
            if FoundRightVersion and FoundGRUB:
                break

        if FoundRightVersion and FoundGRUB:
            return BootDisk

        else:
            return "Unknown"

    def GetGRUB2Config(self, ConfigFilePath): #*** Add logging messages ***
        """Get important bits of config from grub2 (MBR or UEFI)"""
        #Set temporary vars
        Timeout = "Unknown"
        KernelOptions = "Unknown"

        #Open the file in read mode, so we can save the important bits of config.
        ConfigFile = open(ConfigFilePath, 'r')

        #Loop through each line in the file, paying attention only to the important ones.
        for Line in ConfigFile:
            #Look for the timeout setting.
            if 'GRUB_TIMEOUT' in Line and '=' in Line:
                #Found it! Save it, carefully avoiding errors.
                Timeout = Line.split("=")[1]

                if Timeout.isdigit():
                    #Great! We got it.
                    Timeout = int(Timeout)

            #Look for kernel options used globally in all the boot options.
            elif 'GRUB_CMDLINE_LINUX_DEFAULT' in Line and '=' in Line:
                #Found them! Save them.
                KernelOptions = Line.split("=")[1].replace("\'", "")

        #Close the file.
        ConfigFile.close()

        return (Timeout, KernelOptions)

    def GuessGRUBBootDevice(self, OSName):
        """Make an educated guess as to where grub is installed to for each OS"""
        pass

    def GetLILOConfig(self, ConfigFilePath): #*** Add logging messages ***
        """Get important bits of config from lilo and elilo"""
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

            #Look for kernel options used globally in all the boot options. *** Doesn't seem to work ***
            elif 'append' in Line and '=' in Line:
                #Found them! Save it to GlobalKernelOptions
                KernelOptions = ' '.join(Line.split("=")[1:]).replace("\"", "")

            #Look for the 'boot' setting. *** Test this ***
            elif 'boot' in Line and '=' in Line and '#' not in Line and 'map' not in Line:
                #Found it!
                Temp = Line.split("=")[1]

                #Convert to a device node if we have an ID.
                if "by-id" in Temp:
                    ID = Temp.split("/")[-1]

                    for Disk in DiskInfo.keys():
                        if DiskInfo[Disk]["ID"] == ID:
                            Temp = Disk
                            break

                #Check we got the device node in case we had an ID.
                if "/dev/" in Temp:
                    BootDisk = Temp

        #Close the file.
        ConfigFile.close()

        #Ignore ELILO's boot disk setting. *** Change later? ***
        if "/etc/lilo.conf" in ConfigFilePath:
            return (Timeout, KernelOptions, BootDisk)

        else:
            return (Timeout, KernelOptions)
