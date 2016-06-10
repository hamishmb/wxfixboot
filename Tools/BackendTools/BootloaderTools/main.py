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
    def ManageBootloader(self, OS): #*** Move to MainBackendTools? ***
        """Manage the installation and removal of each bootloader.""" #*** Check each operation worked with a return value! ***
        if BootloaderInfo[OS]["Settings"]["Reinstall"] or BootloaderInfo[OS]["Settings"]["Update"]:
            BootloaderInfo[OS]["Settings"]["NewBootloader"] = BootloaderInfo[OS]["Bootloader"]

        if BootloaderInfo[OS]["Settings"]["Reinstall"] or BootloaderInfo[OS]["Settings"]["InstallNewBootloader"]:
            #First remove the old bootloader, then install the new one.
            logger.info("MainBootloaderTools(): Main().ManageBootloader(): Calling MainBackendTools().RemoveOldBootloader()...")
            MainBackendTools.RemoveOldBootloader(OS)
            wx.CallAfter(ParentWindow.UpdateCurrentProgress, 33)

            logger.info("MainBootloaderTools(): Main().ManageBootloader(): Calling MainBackendTools().InstallNewBootloader()...")
            BootloaderInstallSucceded = MainBackendTools.InstallNewBootloader(OS)

            if BootloaderInstallSucceded == False:
                #Bootloader installation failed for at least one OS! *** Clarify this message with better info ***
                logger.error("MainBootloaderTools(): Main().ManageBootloader(): Failed to install new bootloader in at least one OS! Asking user whether to continue with configuration or not...")
                Result = DialogTools.ShowYesNoDlg(Message="Bootloader Installation failed for at least one OS! Please tell WxFixBoot what to do now. Click Yes to configure bootloaders anyway, and no to skip configuration.", Title="WxFixBoot - Configure Bootloader?", Buttons=("Configure Bootloaders Anyway", "Skip Bootloader Configuration"))

                if Result == False:
                    logger.warning("MainBootloaderTools(): Main().ManageBootloader(): Configuring bootloaders anyway. Calling MainBackendTools().SetNewBootloaderConfig()...")

                else:
                    logger.warning("MainBootloaderTools(): Main().ManageBootloader(): Not configuring bootloaders...")
                    return True

        wx.CallAfter(ParentWindow.UpdateCurrentProgress, 66)
        MainBackendTools.SetNewBootloaderConfig(OS)

        logger.info("MainBootloaderTools(): Main().ManageBootloader(): Done!")
        wx.CallAfter(ParentWindow.UpdateCurrentProgress, 100)
