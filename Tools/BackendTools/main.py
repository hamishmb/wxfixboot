#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Main Backend Tools in the BackendTools Package for WxFixBoot Version 2.0~pre1
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

#Begin Main Class.
class Main():
    def GetOldBootloaderConfig(self): #*** Check this works ***
        """Get the old bootloader's config before removing it, so we can reuse it (if possible) with the new one."""
        logger.debug("MainBackendTools: Main().GetOldBootloaderConfig(): Preparing to get bootloader config...")
        wx.CallAfter(ParentWindow.UpdateCurrentOpText, Message="Preparing to get bootloader config...")
        wx.CallAfter(ParentWindow.UpdateCurrentProgress, 2)
        wx.CallAfter(ParentWindow.UpdateOutputBox, "\n###Preparing to get old bootloader config...###\n")

        #Define global vars
        global BootloaderTimeout
        global KernelOptions

        #Use two lists for global kernel options and timeouts, so if they differ for each instance of the bootloader (assuming there is more than one), we can ask the user which is best, or go with WxFixBoot's default (timeout=10, kopts="quiet splash nomodeset")
        KernelOptsList = []
        TimeoutsList = []

        wx.CallAfter(ParentWindow.UpdateCurrentOpText, Message="Getting old bootloader config...")
        wx.CallAfter(ParentWindow.UpdateOutputBox, "\n###Getting old bootloader config...###\n")

        #Loop through each OS in OSsForBootloaderRemoval, and provide information to the function that gets the configuration.
        logger.info("MainBackendTools: Main().GetOldBootloaderConfig(): Looking for configuration in OSs marked for bootloader removal...")
        for OS in OSsForBootloaderRemoval:
            #Grab the OS's partition.
            Partition = OS.split()[-5]
            logger.debug("MainBackendTools: Main().GetOldBootloaderConfig(): Looking for config in OS: "+OS+"...")

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
                    logger.warning("MainBackendTools: Main().GetOldBootloaderConfig(): Failed to mount "+Partiton+"! Ignoring this partition...")
                    continue

            #Look for the configuration file, based on which GetConfig() function we're about to run.
            if Bootloader == "GRUB-LEGACY" and os.path.isfile(MountPoint+"/boot/grub/menu.lst"):
                logger.info("MainBackendTools: Main().GetOldBootloaderConfig(): Found GRUB-LEGACY config file. Getting bootloader's timeout...")
                timeout = BootloaderConfigObtainingTools().GetGRUBLEGACYConfig(filetoopen=MountPoint+"/boot/grub/menu.lst")
                    
            elif Bootloader in ('GRUB2', 'GRUB-UEFI') and os.path.isfile(MountPoint+"/etc/default/grub"):
                logger.info("MainBackendTools: Main().GetOldBootloaderConfig(): Found GRUB2 (BIOS and UEFI) config file. Getting bootloader's timeout and kernel options...")
                timeout, kopts = BootloaderConfigObtainingTools().GetGRUB2Config(filetoopen=MountPoint+"/etc/default/grub")

            elif Bootloader == "LILO" and os.path.isfile(MountPoint+"/etc/lilo.conf"):
                logger.info("MainBackendTools: Main().GetOldBootloaderConfig(): Found LILO config file. Getting bootloader's timeout and kernel options...")
                timeout, kopts = BootloaderConfigObtainingTools().GetLILOConfig(filetoopen=MountPoint+"/etc/lilo.conf")

            elif Bootloader == "ELILO" and os.path.isfile(MountPoint+"/etc/elilo.conf"):
                logger.info("MainBackendTools: Main().GetOldBootloaderConfig(): Found ELILO config file. Getting bootloader's timeout and kernel options...")
                timeout, kopts = BootloaderConfigObtainingTools().GetLILOConfig(filetoopen=MountPoint+"/etc/elilo.conf")

            #Unmount the partition, if needed.
            if MountPoint != "":
                CoreTools().Unmount(MountPoint) #*** Check it worked! ***

            #Now we have the config, let's add it to the list, if it's unique. This will also catch the NameError exception created if the bootloader's config file wasn't found. 
            #First do timeout.
            if timeout != "" and timeout not in TimeoutsList:
                TimeoutsList.append(timeout)

            if kopts != "" and kopts not in KernelOptsList:
                KernelOptsList.append(kopts)

            wx.CallAfter(ParentWindow.UpdateCurrentProgress, 2+(14//len(OSsForBootloaderRemoval)))

        #We're finished getting the config.
        logger.info("MainBackendTools: Main().GetOldBootloaderConfig(): Finished looking for configuration in OSs marked for bootloader removal.")
        wx.CallAfter(ParentWindow.UpdateCurrentOpText, Message="Determining configuration to use...")
        wx.CallAfter(ParentWindow.UpdateCurrentProgress, 14)

        #Now let's check how many options there are in each of these lists, and run different code accordingly.
        #First TimeoutsList, but only if we aren't using a preset value for BootloaderTimeout.
        logger.info("MainBackendTools: Main().GetOldBootloaderConfig(): Determining config to use...")
        if BootloaderTimeout == -1:
            if len(TimeoutsList) == 0:
                #No timeout was found!
                Temp = DialogTools().ShowTextEntryDlg(Message="WxFixBoot couldn't find the currently installed bootloader's timeout value. Please enter a value, or use WxFixBoot's default (10).", Title="WxFixBoot - Enter timeout value")
                BootloaderTimeout = int(Temp)
                logger.info("MainBackendTools: Main().GetOldBootloaderConfig(): Using user's bootloader timeout value: "+unicode(BootloaderTimeout))

            elif len(TimeoutsList) == 1:
                #As there is one, do what the user said, and set it directly.
                BootloaderTimeout = int(TimeoutsList[0])
                logger.info("MainBackendTools: Main().GetOldBootloaderConfig(): Using only bootloader timeout value found: "+unicode(BootloaderTimeout))

            else:
                #Ask the user which timeout to use, as there are more than one.
                TimeoutsList.append("WxFixBoot's Default (10)")
                Result = DialogTools().ShowChoiceDlg(Message="WxFixBoot found multiple timeout settings. Please select the one you want.", Title="WxFixBoot -- Select Timeout Setting", Choices=TimeoutsList)

                #Save it.
                if Result == "WxFixBoot's Default (10)":
                    BootloaderTimeout = 10
                    logger.info("MainBackendTools: Main().GetOldBootloaderConfig(): Using WxFixBoot's default bootloader timeout value: 10")

                else:
                    BootloaderTimeout = int(Result)
                    logger.info("MainBackendTools: Main().GetOldBootloaderConfig(): Using user chosen bootloader timeout value: "+unicode(BootloaderTimeout))

        wx.CallAfter(ParentWindow.UpdateCurrentProgress, 21)

        #Now do the kernel options.
        if len(KernelOptsList) == 0:
            #No kernel options were found!
            #Ask the user to use WxFixBoot's default, or do manual config.
            Result = DialogTools().ShowYesNoDlg(Message="WxFixBoot couldn't find the current bootloader's default kernel options. Do you want to use WxFixBoot's default options? You should click yes and use the defaults, which are almost always fine. However, if you know exactly what you're doing, you can click no, and modify them yourself.", Title="WxFixBoot - Use Default Kernel Options?")

            if Result:
                KernelOptions = "quiet splash nomodeset"
                logger.info("MainBackendTools: Main().GetOldBootloaderConfig(): Using WxFixBoot's default kernel options: 'quiet splash nomodeset'")

            else:
                #Ask the user for the kernel options to use.
                Result = DialogTools().ShowTextEntryDlg(Message="Please enter the kernel options you want to use. WxFixBoot's default kernel options are: 'quiet splash nomodeset'. If you've changed your mind, type these instead.", Title="WxFixBoot - Enter Kernel Options")

                KernelOptions = Result
                logger.info("MainBackendTools: Main().GetOldBootloaderConfig(): Using user defined kernel options: '"+KernelOptions+"'")

        elif len(KernelOptsList) == 1:
            #Use the single set of options found.
            KernelOptions = KernelOptsList[0]
            logger.info("MainBackendTools: Main().GetOldBootloaderConfig(): Using only kernel options found: "+KernelOptions)

        else:
            #Ask the user which timeout to use, as there are more than one.
            KernelOptsList.append("WxFixBoot's Default ('quiet splash nomodeset')")
            Result = DialogTools().ShowChoiceDlg(Message="WxFixBoot found multiple kernel options. Please select the one you want.", Title="WxFixBoot -- Select Kernel Options", Choices=KernelOptsList)

            #Save it.
            if Result == "WxFixBoot's Default ('quiet splash nomodeset')":
                KernelOptions = "quiet splash nomodeset"
                logger.info("MainBackendTools: Main().GetOldBootloaderConfig(): Using WxFixBoot's default kernel options: 'quiet splash nomodeset'")

            else:
                KernelOptions = Result
                logger.warning("MainBackendTools: Main().GetOldBootloaderConfig(): Using user entered kernel options: "+KernelOptions)

        wx.CallAfter(ParentWindow.UpdateCurrentProgress, 25)

    def RemoveOldBootloader(self): #*** Handle return values *** *** Check this works ***
        """Remove the currently installed bootloader."""
        logger.debug("MainBackendTools: Main().RemoveOldBootloader(): Preparing to remove old bootloaders...")
        wx.CallAfter(ParentWindow.UpdateCurrentOpText, Message="Removing old bootloaders...")
        wx.CallAfter(ParentWindow.UpdateCurrentProgress, 27)
        wx.CallAfter(ParentWindow.UpdateOutputBox, "\n###Removing old bootloaders...###\n")

        #Loop through each OS in OSsForBootloaderRemoval, and provide information to the function that will remove the bootloader.
        for OS in OSsForBootloaderRemoval:
            #For each OS that needs the bootloader removed, grab the partition, and the package manager.
            Partition = OS.split()[-5]
            PackageManager = OS.split()[-1]

            logger.info("MainBackendTools: Main().RemoveOldBootloader(): Removing "+Bootloader+" from OS: "+OS+"...")
            wx.CallAfter(ParentWindow.UpdateOutputBox, "\n###Removing the old bootloader from OS: "+OS+"...###\n")

            #Grab the architecture. *** Change this soon ***
            Arch = OS.split()[-8]
            if Arch == "64-bit":
                Arch = "x86_64"

            else:
                Arch = "i686"
            
            #If we're not on a live disk, and the partition is AutoRootFS, let the remover function know that we aren't using chroot.
            if LiveDisk == False and Partition == AutoRootFS:
                logger.debug("MainBackendTools: Main().RemoveOldBootloader(): Modifying current OS so not using chroot...")
                UseChroot = False
                MountPoint = None

            else:
                logger.debug("MainBackendTools: Main().RemoveOldBootloader(): Using chroot to modify another OS...")
                UseChroot = True

                #Mount the partition using the global mount function. *** Note: Do we need to unmount it afterwards? Maybe check if it's mounted first, and do if needed *** 
                MountPoint = "/mnt"+Partition
                Retval = CoreTools().MountPartition(Partition=Partition, MountPoint=MountPoint)

                if Retval != 0:
                    logger.error("MainBackendTools: Main().RemoveOldBootloader(): Failed to remount "+Partition+"! Warn the user and skip this OS.")
                    DialogTools().ShowMsgDlg(Kind="error", Message="WxixBoot failed to mount the partition containing: "+OS+"! This OS will now be skipped.")
                    continue

                #Set up chroot.
                CoreBackendTools().SetUpChroot(MountPoint=MountPoint)

                #If there's a seperate /boot partition for this OS, make sure it's mounted. *** Read this OS's FSTAB instead of hoping that this works, cos then we can use the global mount function to do this *** *** this might mount other stuff and interfere too ***
                CoreBackendTools().StartThreadProcess("chroot "+MountPoint+" mount -av", Piping=True, ShowOutput=False)

            #Remove the bootloader.
            if Bootloader == "GRUB-LEGACY":
                logger.info("MainBackendTools: Main().RemoveOldBootloader(): Removing GRUB-LEGACY...")
                retval = BootloaderRemovalTools().RemoveGRUBLEGACY(PackageManager=PackageManager, UseChroot=UseChroot, MountPoint=MountPoint, Arch=Arch)

            elif Bootloader == "GRUB2":
                logger.info("MainBackendTools: Main().RemoveOldBootloader(): Removing GRUB2...")
                retval = BootloaderRemovalTools().RemoveGRUB2(PackageManager=PackageManager, UseChroot=UseChroot, MountPoint=MountPoint, Arch=Arch)

            elif Bootloader == "LILO":
                logger.info("MainBackendTools: Main().RemoveOldBootloader(): Removing LILO...")
                retval = BootloaderRemovalTools().RemoveLILO(PackageManager=PackageManager, UseChroot=UseChroot, MountPoint=MountPoint, Arch=Arch)

            elif Bootloader == "GRUB-UEFI":
                logger.info("MainBackendTools: Main().RemoveOldBootloader(): Removing GRUB-UEFI...")
                retval = BootloaderRemovalTools().RemoveGRUBUEFI(PackageManager=PackageManager, UseChroot=UseChroot, MountPoint=MountPoint, Arch=Arch)

            elif Bootloader == "ELILO":
                logger.info("MainBackendTools: Main().RemoveOldBootloader(): Removing ELILO...")
                retval = BootloaderRemovalTools().RemoveELILO(PackageManager=PackageManager, UseChroot=UseChroot, MountPoint=MountPoint, Arch=Arch)

            #Tear down chroot if needed.
            if UseChroot:
                CoreBackendTools().TearDownChroot(MountPoint=MountPoint)

            wx.CallAfter(ParentWindow.UpdateOutputBox, "\n###Finished removing the old bootloader from OS: "+OS+"...###\n")

            if retval != 0:
                #Something went wrong! Log it and notify the user.
                logger.error("MainBackendTools: Main().RemoveOldBootloader(): Failed to remove "+Bootloader+" from OS: "+OS+"! We'll continue anyway. Warn the user.")
                DialogTools().ShowMsgDlg(Kind="error", Message="WxFixBoot failed to remove "+Bootloader+" from: "+OS+"! This probably doesn't matter; when we install the new bootloader, it should take precedence over the old one anyway. Make sure you check that OS after WxFixBoot finishes its operations.")

            wx.CallAfter(ParentWindow.UpdateCurrentProgress, 27+(22//len(OSsForBootloaderRemoval)))

        #Log and notify the user that we're finished remving bootloaders.
        logger.info("MainBackendTools: Main().RemoveOldBootloader(): Finished removing bootloaders...")
        wx.CallAfter(ParentWindow.UpdateCurrentOpText, Message="Finished removing old bootloaders...")
        wx.CallAfter(ParentWindow.UpdateCurrentProgress, 50)
        DialogTools().ShowMsgDlg(Kind="info", Message="Finished removing old bootloaders! WxFixBoot will now install your new bootloader to: "+', '.join(OSsForBootloaderInstallation)+".")

    def InstallNewBootloader(self): #*** Check this works ***
        """Install a new bootloader."""
        wx.CallAfter(ParentWindow.UpdateCurrentProgress, 52)  
        BootloaderInstallSucceded = True     

        #Loop through OSsForBootloaderInstallation, and provide information to the function that will install the bootloader.
        for OS in OSsForBootloaderInstallation:
            #For each OS that needs the new bootloader installed, grab the partition, and the package manager.
            Partition = OS.split()[-5]
            PackageManager = OS.split()[-1]

            logger.info("MainBackendTools: Main().InstallNewBootloader(): Preparing to install the new bootloader ("+BootloaderToInstall+") in OS: "+OS+"...")
            wx.CallAfter(ParentWindow.UpdateOutputBox, "\n###Preparing to install "+BootloaderToInstall+" in OS: "+OS+"...###\n")
            wx.CallAfter(ParentWindow.UpdateCurrentOpText, Message="Preparing to install the new bootloader(s)...")

            #If we're not on a live disk, and the partition is AutoRootFS, let the installer functions know that we aren't using chroot.
            if LiveDisk == False and Partition == AutoRootFS:
                logger.debug("MainBackendTools: Main().InstallNewBootloader(): Modifying current OS so not using chroot...")
                UseChroot = False
                MountPoint = ""

            #Otherwise, setup the chroot and everything else first, and tell them we are using chroot, and pass the mountpoint to them.
            else:
                logger.debug("MainBackendTools: Main().InstallNewBootloader(): Using chroot to modify another OS...")
                UseChroot = True
                MountPoint = "/mnt"+Partition
                Retval = CoreTools().MountPartition(Partition=Partition, MountPoint=MountPoint)

                if Retval != 0:
                    logger.error("MainBackendTools: Main().InstallNewBootloader(): Failed to mount "+Partition+"! Warn the user and skip this OS.")
                    DialogTools().ShowMsgDlg(Kind="error", Message="WxFixBoot failed to mount the partition containing: "+OS+"! Bootloader installation cannot continue! This may leave your system, or this OS, in an unbootable state. It is recommended to do a Bad Sector check, and then try again.") #*** Is this good advice? Try to determine the cause of the problem ***
                    continue

                #Set up chroot.
                CoreBackendTools().SetUpChroot(MountPoint=MountPoint)

                #If there's a seperate /boot partition for this OS, make sure it's mounted.
                CoreBackendTools().StartThreadProcess("chroot "+MountPoint+" mount -av", Piping=True, ShowOutput=False) #*** Read this OS's FSTAB instead of hoping that this works, cos then we can use the global mount function to do this ***

            #Update the package lists.
            retval = BootloaderInstallationTools().UpdatePackageLists(PackageManager=PackageManager, UseChroot=UseChroot) #*** This ignores this return value! ***

            wx.CallAfter(ParentWindow.UpdateCurrentOpText, Message="Installing the new bootloader(s)...")
            wx.CallAfter(ParentWindow.UpdateCurrentProgress, 55)       
            wx.CallAfter(ParentWindow.UpdateOutputBox, "\n###Installing the new bootloader in OS: "+OS+"...###\n")

            #Install the bootloader.
            if BootloaderToInstall == "GRUB2":
                logger.info("MainBackendTools: Main().InstallNewBootloader(): Installing GRUB2...")
                retval = BootloaderInstallationTools().InstallGRUB2(PackageManager=PackageManager, UseChroot=UseChroot, MountPoint=MountPoint)

            elif BootloaderToInstall == "LILO":
                logger.info("MainBackendTools: Main().InstallNewBootloader(): Installing LILO...")
                retval = BootloaderInstallationTools().InstallLILO(PackageManager=PackageManager, UseChroot=UseChroot, MountPoint=MountPoint)

            elif BootloaderToInstall == "GRUB-UEFI":
                logger.info("MainBackendTools: Main().InstallNewBootloader(): Installing GRUB-UEFI...")
                #Mount the UEFI partition at MountPoint/boot/efi.
                #Unmount it first though, in case it's already mounted. *** Alternately check where it's mounted and leave it if it's okay ***
                CoreTools().Unmount(UEFISystemPartition) #*** Check it worked! ***
                CoreTools().MountPartition(Partition=UEFISystemPartition, MountPoint=MountPoint+"/boot/efi") #*** Check it worked! ***
                retval = BootloaderInstallationTools().InstallGRUBUEFI(PackageManager=PackageManager, UseChroot=UseChroot, MountPoint=MountPoint)

            elif BootloaderToInstall == "ELILO":
                logger.info("MainBackendTools: Main().InstallNewBootloader(): Installing ELILO...")
                #Unmount the UEFI Partition now, and update the mtab inside chroot.
                CoreTools().Unmount(UEFISystemPartition) #*** Check it worked! ***

                if UseChroot:
                    CoreBackendTools().UpdateChrootMtab(MountPoint=MountPoint)

                retval = BootloaderInstallationTools().InstallELILO(PackageManager=PackageManager, UseChroot=UseChroot, MountPoint=MountPoint)

            #If there's a seperate /boot partition for this OS, make sure it's unmounted before removing the chroot.
            CoreTools().Unmount(MountPoint+"/boot") #*** Check it worked *** *** Test that this works *** *** Why not check if there is one first? ***

            if UseChroot:
                logger.debug("MainBackendTools: Main().InstallNewBootloader(): Removing chroot...")
                #Tear down chroot.
                CoreBackendTools().TearDownChroot(MountPoint=MountPoint)

            if retval != 0:
                #Something went wrong! Log it and notify the user.
                BootloaderInstallSucceded = False
                logger.error("MainBackendTools: Main().InstallNewBootloader(): Failed to install "+BootloaderToInstall+" in OS: "+OS+"! This may mean the system (or this OS) is now unbootable! We'll continue anyway. Warn the user.")
                DialogTools().ShowMsgDlg(Kind="error", Message="WxFixBoot failed to install "+BootloaderToInstall+" in: "+OS+"! This may leave this OS, or your system, in an unbootable state. It is recommended to do a Bad Sector check, unplug any non-essential devices, and then try again.") #*** Maybe ask to try again right now ***

            wx.CallAfter(ParentWindow.UpdateOutputBox, "\n###Finished installing "+BootloaderToInstall+" in OS: "+OS+"...###\n")

        #Log and notify the user that we're finished removing bootloaders.
        logger.info("MainBackendTools: Main().InstallNewBootloader(): Finished Installing bootloaders...")
        wx.CallAfter(ParentWindow.UpdateCurrentOpText, Message="Finished Installing bootloaders...")
        wx.CallAfter(ParentWindow.UpdateCurrentProgress, 75)
        return BootloaderInstallSucceded #*** Keep the results for each OS here, and note which one(s) failed! ***

    def SetNewBootloaderConfig(self): #*** Reduce duplication and maybe move to MainBackendTools? ***
        """Manage setting new bootloader config."""
        logger.debug("MainBackendTools: Main().SetNewBootloaderConfig(): Preparing to set bootloader config in OS(s): "+', '.join(OSsForBootloaderInstallation)+"...")
        wx.CallAfter(ParentWindow.UpdateCurrentOpText, Message="Preparing to set the new bootloaders' config...")
        wx.CallAfter(ParentWindow.UpdateCurrentProgress, 77)

        #Loop through OSsForBootloaderInstallation, and provide information to the function that will set the bootloaders' config.
        for OS in OSsForBootloaderInstallation:
            #For each OS that needs the new bootloader configured, grab the partition, and the package manager.
            logger.info("MainBackendTools: Main().SetNewBootloaderConfig(): Setting the new bootloader config for OS: "+OS+"...")

            #Grab the OS's partition and package manager.
            Partition = OS.split()[-5]
            PackageManager = OS.split()[-1]

            wx.CallAfter(ParentWindow.UpdateOutputBox, "\n###Preparing to set the new bootloaders' config for OS: "+OS+"...###\n")

            #Grab the architecture.
            Arch = OS.split()[-8]
            if Arch == "64-bit":
                Arch = "x86_64"

            else:
                Arch = "i686"

            wx.CallAfter(ParentWindow.UpdateCurrentOpText, Message="Setting the new bootloader's config...")
            wx.CallAfter(ParentWindow.UpdateCurrentProgress, 79)
            wx.CallAfter(ParentWindow.UpdateOutputBox, "\n###Setting the new bootloader's config for OS: "+OS+"...###\n")

            #Check if the Partition is AutoRootFS, if we're not on a live disk.
            if LiveDisk == False and Partition == AutoRootFS:
                #If so, make sure this will work for this OS too, and avoid setting mountpoint, so the config instructions below look in the right place for the config files.
                MountPoint = ""

            else:
                #If not, set mountpoint to the actual mountpoint.
                MountPoint = "/mnt"+Partition

                #Mount the partition.
                Retval = CoreTools().MountPartition(Partition=Partition, MountPoint=MountPoint)

                if Retval != 0:
                    #Ignore this partition.
                    logger.warning("MainBackendTools: Main().SetNewBootloaderConfig(): Failed to mount "+Partition+"! Ignoring this partition...")
                    continue

                else:
                    #Set up chroot.
                    CoreBackendTools().SetUpChroot(MountPoint=MountPoint)

                wx.CallAfter(ParentWindow.UpdateCurrentProgress, 81)

            #Look for the configuration file, based on which SetConfig() function we're about to run.
            if BootloaderToInstall == "GRUB2":
                #Check MountPoint/etc/default/grub exists. *** What do we do if it doesn't? Maybe have a template to put there ***
                if os.path.isfile(MountPoint+"/etc/default/grub"):
                    #It does, we'll run the function to set the config now.
                    logger.info("MainBackendTools: Main().SetNewBootloaderConfig(): Setting GRUB2-BIOS Configuration...")
                    BootloaderConfigSettingTools().SetGRUB2Config(filetoopen=MountPoint+"/etc/default/grub")

                #Now Install GRUB2 to the MBR.
                logger.info("MainBackendTools: Main().SetNewBootloaderConfig(): Installing GRUB2 to MBR...")
                BootloaderConfigSettingTools().InstallGRUB2ToMBR(PackageManager=PackageManager, MountPoint=MountPoint)

                #Update GRUB.
                logger.info("MainBackendTools: Main().SetNewBootloaderConfig(): Updating GRUB2 Configuration...")
                BootloaderConfigSettingTools().UpdateGRUB2(PackageManager=PackageManager, MountPoint=MountPoint)

                #Set the default OS.
                logger.info("MainBackendTools: Main().SetNewBootloaderConfig(): Setting GRUB2 Default OS...")
                BootloaderConfigSettingTools().SetGRUB2DefaultOS(OS=OS, PackageManager=PackageManager, MountPoint=MountPoint)

            elif BootloaderToInstall == "GRUB-UEFI":
                #Check MountPoint/etc/default/grub exists. *** What do we do if it doesn't? Maybe have a template to put there ***
                if os.path.isfile(MountPoint+"/etc/default/grub"):
                    #It does, we'll run the function to set the config now.
                    logger.info("MainBackendTools: Main().SetNewBootloaderConfig(): Setting GRUB2-UEFI Configuration...")
                    BootloaderConfigSettingTools().SetGRUB2Config(filetoopen=MountPoint+"/etc/default/grub")

                #Mount the UEFI partition at MountPoint/boot/efi.
                CoreTools().MountPartition(Partition=UEFISystemPartition, MountPoint=MountPoint+"/boot/efi") #*** Check it worked! ***

                #Now Install GRUB-UEFI to the UEFI Partition.
                logger.info("MainBackendTools: Main().SetNewBootloaderConfig(): Installing GRUB2 to UEFISystemPartition...")
                BootloaderConfigSettingTools().InstallGRUBUEFIToPartition(PackageManager=PackageManager, MountPoint=MountPoint, UEFISystemPartitionMountPoint=MountPoint+"/boot/efi", Arch=Arch)

                #Update GRUB.
                logger.info("MainBackendTools: Main().SetNewBootloaderConfig(): Updating GRUB2 Configuration...")
                BootloaderConfigSettingTools().UpdateGRUB2(PackageManager=PackageManager, MountPoint=MountPoint)

                #Make an entry in fstab for the UEFI Partition, if needed.
                HelperBackendTools().WriteFSTABEntryForUEFIPartition(MountPoint=MountPoint, UEFISystemPartition=UEFISystemPartition)

                #Copy and backup EFI files where needed.
                HelperBackendTools().BackupUEFIFiles(MountPoint=MountPoint)
                HelperBackendTools().CopyUEFIFiles(MountPoint=MountPoint)

                #Set the default OS.
                logger.info("MainBackendTools: Main().SetNewBootloaderConfig(): Setting GRUB2 Default OS...")
                BootloaderConfigSettingTools().SetGRUB2DefaultOS(OS=OS, PackageManager=PackageManager, MountPoint=MountPoint)

            elif BootloaderToInstall == "LILO":
                #Make LILO's config file.
                logger.info("MainBackendTools: Main().SetNewBootloaderConfig(): Making LILO's configuration file...")
                if MountPoint == "":
                    CoreBackendTools().StartThreadProcess("liloconfig -f", Piping=True, ShowOutput=False)

                else:
                    CoreBackendTools().StartThreadProcess("chroot "+MountPoint+" liloconfig -f", Piping=True, ShowOutput=False)

                #Check the config file exists for lilo. *** What do we do if it doesn't? Check the last command ran successfully ***
                if os.path.isfile(MountPoint+"/etc/lilo.conf"):
                    #It does, we'll run the function to set the config now.
                    logger.info("MainBackendTools: Main().SetNewBootloaderConfig(): Setting LILO Configuration...")
                    BootloaderConfigSettingTools().SetLILOConfig(filetoopen=MountPoint+"/etc/lilo.conf", PackageManager=PackageManager, MountPoint=MountPoint)
    
                    #Also, set the OS entries.
                    logger.info("MainBackendTools: Main().SetNewBootloaderConfig(): Creating LILO OS Entries...")
                    BootloaderConfigSettingTools().MakeLILOOSEntries(filetoopen=MountPoint+"/etc/lilo.conf", PackageManager=PackageManager, MountPoint=MountPoint)

                #Now Install LILO to the MBR.
                logger.info("MainBackendTools: Main().SetNewBootloaderConfig(): Installing LILO to the MBR...")
                BootloaderConfigSettingTools().InstallLILOToMBR(PackageManager=PackageManager, MountPoint=MountPoint)

            elif BootloaderToInstall == "ELILO":
                #Unmount the UEFI Partition now, and update mtab in the chroot.
                CoreTools().Unmount(UEFISystemPartition) #*** Check it worked! ***
                CoreBackendTools().UpdateChrootMtab(MountPoint=MountPoint)

                #Make ELILO's config file.
                logger.info("MainBackendTools: Main().SetNewBootloaderConfig(): Making ELILO's configuration file...")
                if MountPoint == "":
                    CoreBackendTools().StartThreadProcess("elilo -b "+UEFISystemPartition+" --autoconf", Piping=True, ShowOutput=False)

                else:
                    CoreBackendTools().StartThreadProcess("chroot "+MountPoint+" elilo -b "+UEFISystemPartition+" --autoconf", Piping=True, ShowOutput=False)

                #Check elilo's config file exists. *** What do we do if it doesn't? Check the last command ran successfully ***
                if os.path.isfile(MountPoint+"/etc/elilo.conf"):
                    #It does, we'll run the function to set the config now.
                    logger.info("MainBackendTools: Main().SetNewBootloaderConfig(): Setting ELILO Configuration...")
                    BootloaderConfigSettingTools().SetELILOConfig(filetoopen=MountPoint+"/etc/elilo.conf", PackageManager=PackageManager, MountPoint=MountPoint)

                    #Also, set the OS entries.
                    logger.info("MainBackendTools: Main().SetNewBootloaderConfig(): Creating ELILO OS Entries...")
                    BootloaderConfigSettingTools().MakeLILOOSEntries(filetoopen=MountPoint+"/etc/elilo.conf", PackageManager=PackageManager, MountPoint=MountPoint)

                #Now Install ELILO to the UEFI Partition.
                logger.info("MainBackendTools: Main().SetNewBootloaderConfig(): Installing ELILO to UEFISystemPartition...")
                BootloaderConfigSettingTools().InstallELILOToPartition(PackageManager=PackageManager, MountPoint=MountPoint, UEFISystemPartitionMountPoint=MountPoint+"/boot/efi", Arch=Arch)

                #Mount the UEFI partition at MountPoint/boot/efi.
                CoreTools().MountPartition(Partition=UEFISystemPartition, MountPoint=MountPoint+"/boot/efi") #*** Check it worked! ***

                #Copy and backup UEFI files where needed.
                HelperBackendTools().BackupUEFIFiles(MountPoint=MountPoint)
                HelperBackendTools().CopyUEFIFiles(MountPoint=MountPoint)

            #Unmount the partition, if needed.
            if MountPoint != "":
                #Tear down chroot.
                CoreBackendTools().TearDownChroot(MountPoint=MountPoint)
                CoreTools().Unmount(MountPoint) #*** Check it worked! ***

            wx.CallAfter(ParentWindow.UpdateOutputBox, "\n###Finished setting the new bootloader's config for OS: "+OS+"...###\n")

        logger.debug("MainBackendTools: Main().SetNewBootloaderConfig(): Finished setting bootloader config.")
        wx.CallAfter(ParentWindow.UpdateCurrentOpText, Message="Finished setting the new bootloader's config!")
        wx.CallAfter(ParentWindow.UpdateCurrentProgress, 100)

#End main Class.
