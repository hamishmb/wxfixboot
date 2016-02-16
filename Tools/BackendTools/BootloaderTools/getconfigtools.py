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
class Main(): #*** Refactor and test all of these ***
    def GetOldBootloaderConfig(self): #*** Add more logging messages ***
        """Get the old bootloader's config before removing it, so we can reuse it (if possible) with the new one."""
        logger.debug("GetBootloaderConfigTools: Main().GetOldBootloaderConfig(): Preparing to get bootloader config...")
        wx.CallAfter(ParentWindow.UpdateCurrentOpText, Message="Preparing to get bootloader config...")
        wx.CallAfter(ParentWindow.UpdateCurrentProgress, 2)
        wx.CallAfter(ParentWindow.UpdateOutputBox, "\n###Preparing to get old bootloader config...###\n")

        #Define global vars
        global BootloaderTimeout
        global KernelOptions

        #Use two lists for global kernel options and timeouts, so if they differ for each instance of the bootloader (assuming there is more than one), we can ask the user which is best, or go with WxFixBoot's default (timeout=10, kopts="quiet splash nomodeset")
        KernelOptsList = []
        TimeoutsList = []

        #Set two temporary vars.
        timeout = ""
        kopts = ""

        wx.CallAfter(ParentWindow.UpdateCurrentOpText, Message="Getting old bootloader config...")
        wx.CallAfter(ParentWindow.UpdateOutputBox, "\n###Getting old bootloader config...###\n")

        #Loop through each OS in OSsForBootloaderRemoval, and provide information to the function that gets the configuration.
        logger.info("GetBootloaderConfigTools: Main().GetOldBootloaderConfig(): Looking for configuration in OSs marked for bootloader removal...")
        for OS in OSsForBootloaderRemoval:
            #Grab the OS's partition.
            Partition = OS.split()[-5]
            logger.debug("GetBootloaderConfigTools: Main().GetOldBootloaderConfig(): Looking for config in OS: "+OS+"...")

            #Check if the Partition is AutoRootFS, if we're not on a live disk.
            if LiveDisk == False and Partition == AutoRootFS:
                #If so, make sure this will work for this OS too, and avoid setting mountpoint, so the config instructions below look in the right place for the config files.
                MountPoint = ""

            else:
                #If not, set mountpoint to the actual mountpoint.
                MountPoint = "/mnt"+Partition

                #Mount the partition.
                Retval = CoreTools().MountPartition(Partition=Partition, MountPoint=MountPoint)

                #Check if anything went wrong.
                if Retval != 0:
                    #Ignore this partition.
                    logger.warning("GetBootloaderConfigTools: Main().GetOldBootloaderConfig(): Failed to mount "+Partiton+"! Ignoring this partition...")
                    continue

            #Look for the configuration file, based on which GetConfig() function we're about to run.
            if Bootloader == "GRUB-LEGACY":
                #Check MountPoint/boot/grub/menu.lst exists.
                if os.path.isfile(MountPoint+"/boot/grub/menu.lst"):
                    #It does, we'll run the function to find the config now.
                    timeout = self.GetGRUBLEGACYConfig(filetoopen=MountPoint+"/boot/grub/menu.lst")
                    
            elif Bootloader in ('GRUB2', 'GRUB-UEFI'):
                #Check MountPoint/etc/default/grub exists, which should be for either GRUB2 or GRUB-UEFI.
                if os.path.isfile(MountPoint+"/etc/default/grub"):
                    #It does, we'll run the function to find the config now.
                    Temp = self.GetGRUB2Config(filetoopen=MountPoint+"/etc/default/grub")
                    timeout = Temp[0]
                    kopts = Temp[1]

            elif Bootloader in ('LILO', 'ELILO'):
                #Check the config file exists for both lilo and elilo.
                if Bootloader == "LILO" and os.path.isfile(MountPoint+"/etc/lilo.conf"):
                    #It does, we'll run the function to find the config now.
                    Temp = self.GetLILOConfig(filetoopen=MountPoint+"/etc/lilo.conf") #*** Broken, not moved yet. ***
                    timeout = Temp[0]
                    kopts = Temp[1]

                elif Bootloader == "ELILO" and os.path.isfile(MountPoint+"/etc/elilo.conf"):
                    #It does, we'll run the function to find the config now.
                    Temp = self.GetLILOConfig(filetoopen=MountPoint+"/etc/elilo.conf") #*** Broken, not moved yet. ***
                    timeout = Temp[0]
                    kopts = Temp[1]

            #Unmount the partition, if needed.
            if MountPoint != "":
                CoreTools().Unmount(MountPoint) #*** Check it worked! ***

            #Now we have the config, let's add it to the list, if it's unique. This will also catch the NameError exception created if the bootloader's config file wasn't found. 
            #First do timeout.
            if timeout != "":
                try:
                    TimeoutsList.index(timeout)

                except ValueError:
                    #It's unique.
                    TimeoutsList.append(timeout)

                except NameError: pass

            if kopts != "":
                #Now kopts.
                try:
                    KernelOptsList.index(kopts)

                except ValueError:
                    #It's unique.
                    KernelOptsList.append(kopts)

                except NameError: pass

            wx.CallAfter(self.ParentWindow.UpdateCurrentProgress, 2+(14/len(OSsForBootloaderRemoval)))

        #We're finished getting the config.
        logger.info("GetBootloaderConfigTools: Main().GetOldBootloaderConfig(): Finished looking for configuration in OSs marked for bootloader removal.")
        wx.CallAfter(ParentWindow.UpdateCurrentOpText, Message="Determining configuration to use...")
        wx.CallAfter(ParentWindow.UpdateCurrentProgress, 14)

        #Now let's check how many options there are in each of these lists, and run different code accordingly.
        #First TimeoutsList, but only if we aren't using a preset value for BootloaderTimeout.
        if BootloaderTimeout == -1:
            if len(TimeoutsList) == 0:
                #No timeout was found!
                Temp = DialogTools().ShowTextEntryDlg(Message="WxFixBoot couldn't find the currently installed bootloader's timeout value. Please enter a value, or use WxFixBoot's default (10).", Title="WxFixBoot - Enter timeout value")
                BootloaderTimeout = int(Temp)
                logger.info("GetBootloaderConfigTools: Main().GetOldBootloaderConfig(): Using user's bootloader timeout value: "+unicode(BootloaderTimeout))

            elif len(TimeoutsList) == 1:
                #As there is one, do what the user said, and set it directly.
                BootloaderTimeout = int(TimeoutsList[0])
                logger.info("GetBootloaderConfigTools: Main().GetOldBootloaderConfig(): Using only bootloader timeout value found: "+unicode(BootloaderTimeout))

            else:
                #Ask the user which timeout to use, as there are more than one.
                TimeoutsList.append("WxFixBoot's Default (10)")
                Result = DialogTools().ShowChoiceDlg(Message="WxFixBoot found multiple timeout settings. Please select the one you want.", Title="WxFixBoot -- Select Timeout Setting", Choices=TimeoutsList)

                #Save it.
                if Result == "WxFixBoot's Default (10)":
                    BootloaderTimeout = 10
                    logger.info("GetBootloaderConfigTools: Main().GetOldBootloaderConfig(): Using WxFixBoot's default bootloader timeout value: 10")

                else:
                    BootloaderTimeout = int(Result)
                    logger.info("GetBootloaderConfigTools: Main().GetOldBootloaderConfig(): Using user chosen bootloader timeout value: "+unicode(BootloaderTimeout))

        wx.CallAfter(ParentWindow.UpdateCurrentProgress, 21)

        #Now do the kernel options.
        if len(KernelOptsList) == 0:
            #No kernel options were found!
            #Ask the user to use WxFixBoot's default, or do manual config.
            Result = DialogTools().ShowYesNoDlg(Message="WxFixBoot couldn't find the current bootloader's default kernel options. Do you want to use WxFixBoot's default options? You should click yes and use the defaults, which are almost always fine. However, if you know exactly what you're doing, you can click no, and modify them yourself.", Title="WxFixBoot - Use Default Kernel Options?")

            if Result:
                KernelOptions = "quiet splash nomodeset"
                logger.info("GetBootloaderConfigTools: Main().GetOldBootloaderConfig(): Using WxFixBoot's default kernel options: 'quiet splash nomodeset'")

            else:
                #Ask the user for the kernel options to use.
                Result = DialogTools().ShowTextEntryDlg(Message="Please enter the kernel options you want to use. WxFixBoot's default kernel options are: 'quiet splash nomodeset'. If you've changed your mind, type these instead.", Title="WxFixBoot - Enter Kernel Options")

                KernelOptions = Result
                logger.info("GetBootloaderConfigTools: Main().GetOldBootloaderConfig(): Using user defined kernel options: '"+KernelOptions+"'")

        elif len(KernelOptsList) == 1:
            #Use the single set of options found.
            KernelOptions = KernelOptsList[0]
            logger.info("GetBootloaderConfigTools: Main().GetOldBootloaderConfig(): Using only kernel options found: "+KernelOptions)

        else:
            #Ask the user which timeout to use, as there are more than one.
            KernelOptsList.append("WxFixBoot's Default ('quiet splash nomodeset')")
            Result = DialogTools().ShowChoiceDlg(Message="WxFixBoot found multiple kernel options. Please select the one you want.", Title="WxFixBoot -- Select Kernel Options", Choices=KernelOptsList)

            #Save it.
            if Result == "WxFixBoot's Default ('quiet splash nomodeset')":
                KernelOptions = "quiet splash nomodeset"
                logger.info("GetBootloaderConfigTools: Main().GetOldBootloaderConfig(): Using WxFixBoot's default kernel options: 'quiet splash nomodeset'")

            else:
                KernelOptions = Result
                logger.warning("GetBootloaderConfigTools: Main().GetOldBootloaderConfig(): Using user entered kernel options: "+KernelOptions)

        wx.CallAfter(ParentWindow.UpdateCurrentProgress, 25)

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
                if BootloaderTimeout == -1:
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
