#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Bootloader Configuration Obtaining Tools in the Bootloader Tools Package in the Backend Tools package for WxFixBoot Version 1.1~pre1
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

class Main(): #*** Refactor and test all of these ***
    def GetGRUBLEGACYConfig(self, filetoopen): #*** Add logging messages ***
        """Get important bits of config from grub-legacy before removing it."""
        #In this case, the only useful info is the timeout, so just get this.
        #Set temporary vars
        Timeout = ""

        #Open the file in read mode, so we can save the important bits of config.
        infile = open(filetoopen, 'r')

        #Look for the timeout setting.
        for line in infile:
            if 'timeout' in line and 'sec' not in line:
                #Found it! Save it to BootloaderTimeout, but only if BootloaderTimeout = -1 (we aren't changing the timeout). #*** Otherwise, don't bother looking for it and speed this up! ***
                if BootloaderTimeout == -1:
                    Temp = line.split()[1].replace('\n', '')
                    if Temp.isdigit():
                        #Great! We got it.
                        Timeout = int(Temp)

                    #Exit the loop to save time.
                    break

        #Close the file.
        infile.close()

        return Timeout

    def GetGRUB2Config(self, filetoopen): #*** Add logging messages ***
        """Get important bits of config from grub2 (MBR or UEFI) before removing it."""
        #Set temporary vars
        Timeout = ""
        Kopts = ""

        #Open the file in read mode, so we can save the important bits of config.
        infile = open(filetoopen, 'r')

        #Loop through each line in the file, paying attention only to the important ones. *** Can we use .split("=") instead? ***
        for line in infile:
            #Look for the timeout setting.
            if 'GRUB_TIMEOUT' in line and '=' in line:
                #Found it! Save it to BootloaderTimeout, but only if BootloaderTimeout = -1 (we aren't changing the timeout).
                if BootloaderTimeout == -1: #*** If we check this earlier it'll save CPU time ***
                    #Save it, carefully avoiding errors.
                    junk, sep, Temp = line.partition('=')
                    Temp = Temp.replace(' ','').replace('\n', '').replace("\'", "")
                    if Temp.isdigit():
                        #Great! We got it.
                        Timeout = int(Temp)

            #Look for kernel options used globally in all the boot options.
            elif 'GRUB_CMDLINE_LINUX_DEFAULT' in line and '=' in line:
                #Found them! Save it to GlobalKernelOptions
                junk, sep, Temp = line.partition('=')
                Kopts = Temp.replace('\"', '').replace("\'", "").replace("\n", "")

        #Close the file.
        infile.close()

        #Return these values to self.RemoveOldBootloader()
        return (Timeout, Kopts)

    def GetLILOConfig(self, filetoopen): #*** Add logging messages ***
        """Get important bits of config from lilo before removing it."""
        #Set temporary vars
        Timeout = ""
        Kopts = ""

        #Open the file in read mode, so we can save the important bits of config.
        infile = open(filetoopen, 'r')

        #Loop through each line in the file, paying attention only to the important ones.
        for line in infile:
            #Look for the delay/timeout setting.
            if ('delay' in line or 'timeout' in line) and '=' in line:
                #Found it! Save it to BootloaderTimeout, but only if BootloaderTimeout = -1 (we aren't changing the timeout). *** Can we use .split("=") instead? ***
                if BootloaderTimeout == -1: #*** If we check this earlier it'll save CPU time ***
                    #Save it, carefully avoiding errors.
                    junk, sep, Temp = line.partition('=')
                    Temp = Temp.replace(' ','').replace('\n', '')
                    if Temp.isdigit():
                        #Great! We got it.
                        #However, because lilo and elilo save this in 10ths of a second, divide it by ten first.
                        Timeout = int(Temp)/10

            #Look for kernel options used globally in all the boot options.
            elif 'append' in line and '=' in line:
                #Found them! Save it to GlobalKernelOptions
                junk, sep, Temp = line.partition('=')
                Kopts = Temp.replace('\"', '').replace("\'", "").replace("\n", "")

        #Close the file.
        infile.close()

        #Return these values to self.RemoveOldBootloader()
        return (Timeout, Kopts)

