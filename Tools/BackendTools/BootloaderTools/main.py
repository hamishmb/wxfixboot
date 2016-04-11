#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Main Bootloader Tools in the Bootloader Tools Package in the Backend Tools package for WxFixBoot Version 2.0~pre1
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
    def PrepareForBootloaderInstallation(self):
        """Run checks, gather information, and prepare for bootloader operations.""" #*** Make this more customisable *** 
        #First, check the Internet connection.
        DisableBootloaderOperations = EssentialBackendTools.CheckInternetConnection()

        #*** Temporarily define these as global until switch to dictionaries ***
        global OSsForBootloaderRemoval
        global OSsForBootloaderInstallation

        if DisableBootloaderOperations:
            #Disable bootloader operations.
            OSsForBootloaderRemoval = []
            OSsForBootloaderInstallation = []
            wx.CallAfter(ParentWindow.UpdateOutputBox, "\n###Bootloader Operations Disabled.###\n") 

        else:
            #Determine all the package managers on the system, including all OSs and the OS running, but not the live disk (if there is one). #*** Move this to startuptools ***
            logger.debug("MainBootloaderTools: Main().PrepareForBootloaderInstallation(): Determining package managers for all Linux OSs...")
            wx.CallAfter(ParentWindow.UpdateCurrentOpText, Message="Preparing for bootloader operations...")
            wx.CallAfter(ParentWindow.UpdateCurrentProgress, 10)
            wx.CallAfter(ParentWindow.UpdateOutputBox,"\n###Preparing for bootloader operations...###\n")

            OSListWithPackageManagers = []
        
            #Use OSInfo to find all partitions with Linux OSs on them.
            Keys = OSInfo.keys()
            Keys.sort()

            #Start of for loop.
            for OS in Keys:
                #Get the partition that each OS is on.
                Partition = OSInfo[OS]["Partition"]

                #If not on a live disk, and this OS is the one running, skip some stuff.
                if SystemInfo["IsLiveDisk"] == False and Partition == AutoRootFS:
                    #Find the package manager on this partition, if one exists.
                    #This is the RootFS, so don't use chroot in the given command lists.
                    APT = HelperBackendTools.LookForAPTOnPartition(APTExecCmds="which apt-get")

                    #Add the OS and its package manager to the list, if there is one. *** Add this to OSInfo when moved to startup tools ***
                    if APT:
                       logger.info("MainBootloaderTools: Main().PrepareForBootloaderInstallation(): Found possible package management candidate: "+OS+" with Package Manager apt-get")
                       OSListWithPackageManagers.append(OS+" (Current OS) "+OSInfo[OS]["Arch"]+" on partition "+Partition+" with Package Manager apt-get")
                            
                    #Skip the rest of the for loop.
                    continue

                #Mount the partition.
                Retval = CoreTools.MountPartition(Partition=Partition, MountPoint="/mnt"+Partition)

                #Check if anything went wrong.
                if Retval != 0:
                    #Ignore this partition.
                    logger.warning("MainBootloaderTools: Main().PrepareForBootloaderInstallation(): Failed to mount "+Partition+"! Ignoring this partition...")

                else:
                    #Find the package manager on this partition, if one exists.
                    #This isn't the RootFS, so use chroot in the given command lists.
                    APT = HelperBackendTools.LookForAPTOnPartition(APTExecCmds="chroot /mnt"+Partition+" which apt-get")

                    #Add the OS and its package manager to the list, if there is one.
                    if APT:
                        logger.info("MainBootloaderTools: Main().PrepareForBootloaderInstallation(): Found possible package management candidate: "+OS+" with Package Manager apt-get")
                        OSListWithPackageManagers.append(OS+" "+OSInfo[OS]["Arch"]+" on partition "+Partition+" with Package Manager apt-get")

            wx.CallAfter(ParentWindow.UpdateCurrentProgress, 70)

            #Check if there are any candidates for bootloader installation/removal. Hopefully there are!
            if OSListWithPackageManagers == []:
                #Oh dear... There aren't.
                logger.error("MainBootloaderTools: Main().PrepareForBootloaderInstallation(): Couldn't find an OS with APT! Will have to disable some operations!")
                DialogTools.ShowMsgDlg(Kind="error", Message="No supported package managers could be found on any of your operating systems! At the moment, APT is supported, which covers most Linux Operating Systems. WxFixBoot will have to skip all operations that require a package manager, such as installing, removing and reinstalling the bootloader. In a later release WxFixBoot will likely support another package manager, such as Slackware's system. If you think you do have an OS with a supported package manager, please report a bug or email me directly via my Launchpad page, so I can try to help. In the meantime, you can probably follow some online instructions for your operating system.")

                #Set these to "None", so the packagemanager-dependant code can skip itself.
                OSsForBootloaderRemoval = []
                OSsForBootloaderInstallation = []

                #Update Current Operation Text.
                wx.CallAfter(ParentWindow.UpdateCurrentProgress, 100)

            else:
                #Very good! There is at least one candidate.
                logger.info("MainBootloaderTools: Main().PrepareForBootloaderInstallation(): Found at least one candidate for installing and removing bootloaders! Continuing...")

                #Also, we need to find which OS(es) installed the bootloader (or have it installed currently), and ask the user which OS to install the bootloader with.
                OSsForBootloaderRemoval = HelperBackendTools.FindBootloaderRemovalOSs(OSListWithPackageManagers, AutoRootFS, Bootloader)
                logger.info("MainBootloaderTools: Main().PrepareForBootloaderInstallation(): List of OSs to have the bootloader removed: "+', '.join(OSsForBootloaderRemoval)+"...")

                #Update Current Operation Text.
                wx.CallAfter(ParentWindow.UpdateCurrentProgress, 85)
                OSsForBootloaderInstallation = HelperBackendTools.AskUserForBootloaderInstallationOSs(OSListWithPackageManagers, UpdateBootloader, ReinstallBootloader, OSsForBootloaderRemoval)
                wx.CallAfter(ParentWindow.UpdateCurrentProgress, 100)

            wx.CallAfter(ParentWindow.UpdateOutputBox, "\n###Done!###\n") 

    def ReinstallBootloader(self):
        """Reinstall/fix the bootloader."""
        #*** Temporarily define this as global until switch to dictionaries ***
        global DisableBootloaderOperations
        DisableBootloaderOperations = False

        logger.info("MainBootloaderTools: Main().ReinstallBootloader(): Preparing to reinstall the bootloader...")
        wx.CallAfter(ParentWindow.UpdateOutputBox, "\n###Preparing to reinstall the bootloader...###\n")

        if OSsForBootloaderInstallation in (["None,FSCKProblems"], []):
            #These operations have been disabled. Notify the user and skip them.
            logger.info("MainBootloaderTools: Main().ReinstallBootloader(): Cancelled because bootloader operations have been disabled, or the required information wasn't found...")
            DialogTools.ShowMsgDlg(Kind="warning", Message="Bootloader operations have been disabled, or the required information wasn't found! This operation will now be skipped. Click okay to continue.")
            wx.CallAfter(ParentWindow.UpdateCurrentProgress, 100)
            wx.CallAfter(ParentWindow.UpdateOutputBox, "\n###Bootloader Operations Disabled.###\n") 
            DisableBootloaderOperations = True

        else:
            #Set BootloaderToInstall as the current bootloader to allow this to work properly.
            global BootloaderToInstall
            BootloaderToInstall = Bootloader

            #Call self.ManageBootloaders to perform the reinstallation safely.
            logger.info("MainBootloaderTools: Main().ReinstallBootloader(): Reinstalling the Bootloader...")
            wx.CallAfter(ParentWindow.UpdateOutputBox, "\n###Reinstalling the Bootloader...###\n")
            self.ManageBootloaders() 
            logger.info("MainBootloaderTools: Main().ReinstallBootloader(): Done!")

    def UpdateBootloader(self):
        """Update bootloader menu and config"""
        global DisableBootloaderOperations
        DisableBootloaderOperations = False
        logger.info("MainBootloaderTools: Main().UpdateBootloader(): Preparing to update the bootloader...")
        wx.CallAfter(ParentWindow.UpdateOutputBox, "\n###Preparing to update the bootloader...###\n")

        if OSsForBootloaderInstallation in (["None,FSCKProblems"], []):
            #These operations have been disabled. Notify the user and skip them.
            logger.info("MainBootloaderTools: Main().UpdateBootloader(): Cancelled because bootloader operations have been disabled, or the required information wasn't found...")
            DialogTools.ShowMsgDlg(Kind="warning", Message="Bootloader operations have been disabled, or the required information wasn't found! This operation will now be skipped. Click okay to continue.")
            wx.CallAfter(ParentWindow.UpdateCurrentProgress, 100)
            wx.CallAfter(ParentWindow.UpdateOutputBox, "\n###Bootloader Operations Disabled.###\n") 
            DisableBootloaderOperations = True

        else:
            #Set BootloaderToInstall as the current bootloader to allow this to work properly. *** Doesn't work because it needs to be set to tools.BackendTools.main.BootloaderToInstall ***
            global BootloaderToInstall
            BootloaderToInstall = Bootloader
            logger.info("MainBootloaderTools: Main().UpdateBootloader(): Updating the bootloader's config...")
            wx.CallAfter(ParentWindow.UpdateOutputBox, "\n###Preparing to update the bootloader's configuration...###\n")

            #Get the bootloader's config.
            MainBackendTools.GetOldBootloaderConfig()
            wx.CallAfter(ParentWindow.UpdateCurrentProgress, 50)

            #Set the bootloaders new config.
            MainBackendTools.SetNewBootloaderConfig()
            wx.CallAfter(ParentWindow.UpdateCurrentProgress, 100)

            logger.info("MainBootloaderTools: Main().UpdateBootloader(): Done!")

    def ManageBootloaders(self):
        """Manage the installation and removal of bootloaders.""" #*** Check each operation worked with a return value! ***
        #First remove the old bootloader, then install the new one.
        logger.info("MainBootloaderTools(): Main().ManageBootloaders(): Calling MainBackendTools().GetOldBootloaderConfig()...")
        MainBackendTools.GetOldBootloaderConfig()
        wx.CallAfter(ParentWindow.UpdateCurrentProgress, 25)

        logger.info("MainBootloaderTools(): Main().ManageBootloaders(): Calling MainBackendTools().RemoveOldBootloader()...")
        MainBackendTools.RemoveOldBootloader()
        wx.CallAfter(ParentWindow.UpdateCurrentProgress, 50)

        logger.info("MainBootloaderTools(): Main().ManageBootloaders(): Calling MainBackendTools().InstallNewBootloader()...")
        BootloaderInstallSucceded = MainBackendTools().InstallNewBootloader()

        if BootloaderInstallSucceded:
            logger.info("MainBootloaderTools(): Main().ManageBootloaders(): Installing new bootloader succeeded! Calling MainBackendTools().SetNewBootloaderConfig()...")
            wx.CallAfter(ParentWindow.UpdateCurrentProgress, 75)
            MainBackendTools.SetNewBootloaderConfig()

        else:
            #Bootloader installation failed for at least one OS! *** Clarify this message with better info ***
            logger.error("MainBootloaderTools(): Main().ManageBootloaders(): Failed to install new bootloader in at least one OS! Asking user whether to continue with configuration or not...")
            Result = DialogTools.ShowYesNoDlg(Message="Bootloader Installation failed for at least one OS! Do you want to continue and configure the new bootloader(s), or skip the rest of the bootloader operations? You probably want to configure the bootloader anyway.", Title="WxFixBoot - Configure Bootloader(s)?")

            if Result:
                #Continue and configure bootloaders. Otherwise, do nothing.
                logger.warning("MainBootloaderTools(): Main().ManageBootloaders(): Configuring bootloaders anyway. Calling MainBackendTools().SetNewBootloaderConfig()...")
                wx.CallAfter(ParentWindow.UpdateCurrentProgress, 75)
                MainBackendTools.SetNewBootloaderConfig()

            else:
                logger.warning("MainBootloaderTools(): Main().ManageBootloaders(): Not configuring bootloaders...")

        logger.info("MainBootloaderTools(): Main().ManageBootloaders(): Done!")
        wx.CallAfter(ParentWindow.UpdateCurrentProgress, 100)
