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

class Main(): #*** Refactor all of these ***
    def ManageBootloader(self, OS):
        """Manage the installation and removal of each bootloader.""" #*** Check each operation worked with a return value! ***
        if BootloaderInfo[OS]["Settings"]["Reinstall"] or BootloaderInfo[OS]["Settings"]["Update"]:
            BootloaderInfo[OS]["Settings"]["NewBootloader"] = BootloaderInfo[OS]["Bootloader"]

        if BootloaderInfo[OS]["Settings"]["Reinstall"] or BootloaderInfo[OS]["Settings"]["InstallNewBootloader"]:
            #First remove the old bootloader, then install the new one.
            logger.info("MainBootloaderTools(): Main().ManageBootloaders(): Calling MainBackendTools().RemoveOldBootloader()...")
            MainBackendTools.RemoveOldBootloader(OS)
            wx.CallAfter(ParentWindow.UpdateCurrentProgress, 33)

            logger.info("MainBootloaderTools(): Main().ManageBootloaders(): Calling MainBackendTools().InstallNewBootloader()...")
            BootloaderInstallSucceded = MainBackendTools.InstallNewBootloader(OS)

            if BootloaderInstallSucceded == False:
                #Bootloader installation failed for at least one OS! *** Clarify this message with better info ***
                logger.error("MainBootloaderTools(): Main().ManageBootloaders(): Failed to install new bootloader in at least one OS! Asking user whether to continue with configuration or not...")
                Result = DialogTools.ShowYesNoDlg(Message="Bootloader Installation failed for at least one OS! Please tell WxFixBoot what to do now. Click Yes to configure bootloaders anyway, and no to skip configuration.", Title="WxFixBoot - Configure Bootloader?", Buttons=("Configure Bootloaders Anyway", "Skip Bootloader Configuration"))

                if Result == False:
                    logger.warning("MainBootloaderTools(): Main().ManageBootloaders(): Configuring bootloaders anyway. Calling MainBackendTools().SetNewBootloaderConfig()...")

                else:
                    logger.warning("MainBootloaderTools(): Main().ManageBootloaders(): Not configuring bootloaders...")
                    return True

        wx.CallAfter(ParentWindow.UpdateCurrentProgress, 66)
        MainBackendTools.SetNewBootloaderConfig(OS)

        logger.info("MainBootloaderTools(): Main().ManageBootloaders(): Done!")
        wx.CallAfter(ParentWindow.UpdateCurrentProgress, 100)

    def ReinstallBootloader(self): #*** DEPRECATED ***
        """Reinstall/fix the bootloader."""
        logger.info("MainBootloaderTools: Main().ReinstallBootloader(): Preparing to reinstall the bootloader...")
        wx.CallAfter(ParentWindow.UpdateOutputBox, "\n###Preparing to reinstall the bootloader...###\n")

        if SystemInfo["DisableBootloaderOperations"]:
            #These operations have been disabled. Notify the user and skip them.
            logger.info("MainBootloaderTools: Main().ReinstallBootloader(): Cancelled because bootloader operations have been disabled, or the required information wasn't found...")
            DialogTools.ShowMsgDlg(Kind="warning", Message="Bootloader operations have been disabled, or the required information wasn't found! This operation will now be skipped. Click okay to continue.")
            wx.CallAfter(ParentWindow.UpdateCurrentProgress, 100)
            wx.CallAfter(ParentWindow.UpdateOutputBox, "\n###Bootloader Operations Disabled.###\n") 

        else:
            #Call self.ManageBootloaders to perform the reinstallation safely.
            logger.info("MainBootloaderTools: Main().ReinstallBootloader(): Reinstalling the Bootloader...")
            wx.CallAfter(ParentWindow.UpdateOutputBox, "\n###Reinstalling the Bootloader...###\n")
            self.ManageBootloaders() 
            logger.info("MainBootloaderTools: Main().ReinstallBootloader(): Done!")

    def UpdateBootloader(self): #*** DEPRECATED ***
        """Update bootloader menu and config"""
        logger.info("MainBootloaderTools: Main().UpdateBootloader(): Preparing to update the bootloader...")
        wx.CallAfter(ParentWindow.UpdateOutputBox, "\n###Preparing to update the bootloader...###\n")

        if SystemInfo["DisableBootloaderOperations"]:
            #These operations have been disabled. Notify the user and skip them. *** Note why they were disabled ***
            logger.info("MainBootloaderTools: Main().UpdateBootloader(): Cancelled because bootloader operations have been disabled, or the required information wasn't found...")
            DialogTools.ShowMsgDlg(Kind="warning", Message="Bootloader operations have been disabled, or the required information wasn't found! This operation will now be skipped. Click okay to continue.")
            wx.CallAfter(ParentWindow.UpdateCurrentProgress, 100)
            wx.CallAfter(ParentWindow.UpdateOutputBox, "\n###Bootloader Operations Disabled.###\n") 

        else:
            logger.info("MainBootloaderTools: Main().UpdateBootloader(): Updating the bootloader's config...")
            wx.CallAfter(ParentWindow.UpdateOutputBox, "\n###Preparing to update the bootloader's configuration...###\n")

            #Set the bootloaders new config.
            MainBackendTools.SetNewBootloaderConfig()
            wx.CallAfter(ParentWindow.UpdateCurrentProgress, 100)

            logger.info("MainBootloaderTools: Main().UpdateBootloader(): Done!")

    def ManageBootloaders(self): #*** DEPRECATED ***
        """Manage the installation and removal of bootloaders.""" #*** Check each operation worked with a return value! ***
        #First remove the old bootloader, then install the new one.
        logger.info("MainBootloaderTools(): Main().ManageBootloaders(): Calling MainBackendTools().RemoveOldBootloader()...")
        MainBackendTools.RemoveOldBootloader()
        wx.CallAfter(ParentWindow.UpdateCurrentProgress, 33)

        logger.info("MainBootloaderTools(): Main().ManageBootloaders(): Calling MainBackendTools().InstallNewBootloader()...")
        BootloaderInstallSucceded = MainBackendTools.InstallNewBootloader()

        if BootloaderInstallSucceded:
            logger.info("MainBootloaderTools(): Main().ManageBootloaders(): Installing new bootloader succeeded! Calling MainBackendTools().SetNewBootloaderConfig()...")
            wx.CallAfter(ParentWindow.UpdateCurrentProgress, 66)
            MainBackendTools.SetNewBootloaderConfig()

        else:
            #Bootloader installation failed for at least one OS! *** Clarify this message with better info ***
            logger.error("MainBootloaderTools(): Main().ManageBootloaders(): Failed to install new bootloader in at least one OS! Asking user whether to continue with configuration or not...")
            Result = DialogTools.ShowYesNoDlg(Message="Bootloader Installation failed for at least one OS! Please tell WxFixBoot what to do now. Click Yes to configure bootloaders anyway, and no to skip configuration.", Title="WxFixBoot - Configure Bootloader(s)?", Buttons=("Configure Bootloaders Anyway", "Skip Bootloader Configuration"))

            if Result:
                #Continue and configure bootloaders. Otherwise, do nothing.
                logger.warning("MainBootloaderTools(): Main().ManageBootloaders(): Configuring bootloaders anyway. Calling MainBackendTools().SetNewBootloaderConfig()...")
                wx.CallAfter(ParentWindow.UpdateCurrentProgress, 66)
                MainBackendTools.SetNewBootloaderConfig()

            else:
                logger.warning("MainBootloaderTools(): Main().ManageBootloaders(): Not configuring bootloaders...")

        logger.info("MainBootloaderTools(): Main().ManageBootloaders(): Done!")
        wx.CallAfter(ParentWindow.UpdateCurrentProgress, 100)
