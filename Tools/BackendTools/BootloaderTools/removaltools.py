#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Bootloader Removal Tools in the Bootloader Tools Package in the Backend Tools package for WxFixBoot Version 1.1~pre1
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
    def RemoveOldBootloader(self): #*** Reduce code duplication if possible ***
        """Remove the currently installed bootloader."""
        logger.debug("BootloaderRemovalTools: Main().RemoveOldBootloader(): Preparing to remove old bootloaders...")
        wx.CallAfter(ParentWindow.UpdateCurrentOpText, Message="Removing old bootloaders...")
        wx.CallAfter(ParentWindow.UpdateCurrentProgress, 27)
        wx.CallAfter(ParentWindow.UpdateOutputBox, "\n###Removing old bootloaders...###\n")

        #Loop through each OS in OSsForBootloaderRemoval, and provide information to the function that will remove the bootloader.
        for OS in OSsForBootloaderRemoval:
            #For each OS that needs the bootloader removed, grab the partition, and the package manager.
            Partition = OS.split()[-5]
            PackageManager = OS.split()[-1]

            logger.info("BootloaderRemovalTools: Main().RemoveOldBootloader(): Removing "+Bootloader+" from OS: "+OS+"...")
            wx.CallAfter(ParentWindow.UpdateOutputBox, "\n###Removing the old bootloader from OS: "+OS+"...###\n")

            #Grab the architecture.
            Arch = OS.split()[-8]
            if Arch == "64-bit":
                Arch = "x86_64"

            else:
                Arch = "i686"
            
            #If we're not on a live disk, and the partition is AutoRootFS, let the remover function know that we aren't using chroot.
            if LiveDisk == False and Partition == AutoRootFS:
                if Bootloader == "GRUB-LEGACY":
                    retval = self.RemoveGRUBLEGACY(PackageManager=PackageManager, UseChroot=False, Arch=Arch)

                elif Bootloader == "GRUB2":
                    retval = self.RemoveGRUB2(PackageManager=PackageManager, UseChroot=False, Arch=Arch)

                elif Bootloader == "LILO":
                    retval = self.RemoveLILO(PackageManager=PackageManager, UseChroot=False, Arch=Arch) #*** Broken, not moved yet ***

                elif Bootloader == "GRUB-UEFI":
                    retval = self.RemoveGRUBUEFI(PackageManager=PackageManager, UseChroot=False, Arch=Arch) #*** Broken, not moved yet ***

                elif Bootloader == "ELILO":
                    retval = self.RemoveELILO(PackageManager=PackageManager, UseChroot=False, Arch=Arch) #*** Broken, not moved yet ***

            #Otherwise, setup the chroot and everything else first, and tell it we are using chroot, and pass the mountpoint to it.
            else:
                #Mount the partition using the global mount function.
                MountPoint = "/mnt"+Partition
                Retval = CoreTools().MountPartition(Partition=Partition, MountPoint=MountPoint)

                if Retval != 0:
                    logger.error("BootloaderRemovalTools: Main().RemoveOldBootloader(): Failed to remount "+Partition+"! Warn the user and skip this OS.")
                    DialogTools().ShowMsgDlg(Kind="error", Message="WxixBoot failed to mount the partition containing: "+OS+"! This OS will now be skipped.")

                else:
                    #Set up chroot.
                    CoreBackendTools().SetUpChroot(MountPoint=MountPoint)

                    #If there's a seperate /boot partition for this OS, make sure it's mounted.
                    CoreBackendTools().StartThreadProcess(['chroot', MountPoint, 'mount', '-av'], ShowOutput=False)

                    #Remove the bootloader.
                    if Bootloader == "GRUB-LEGACY":
                        retval = self.RemoveGRUBLEGACY(PackageManager=PackageManager, UseChroot=True, MountPoint=MountPoint, Arch=Arch)

                    elif Bootloader == "GRUB2":
                        retval = self.RemoveGRUB2(PackageManager=PackageManager, UseChroot=True, MountPoint=MountPoint, Arch=Arch)

                    elif Bootloader == "LILO":
                        retval = self.RemoveLILO(PackageManager=PackageManager, UseChroot=True, MountPoint=MountPoint, Arch=Arch) #*** Broken, not moved yet ***

                    elif Bootloader == "GRUB-UEFI":
                        retval = self.RemoveGRUBUEFI(PackageManager=PackageManager, UseChroot=True, MountPoint=MountPoint, Arch=Arch) #*** Broken, not moved yet ***

                    elif Bootloader == "ELILO":
                        retval = self.RemoveELILO(PackageManager=PackageManager, UseChroot=True, MountPoint=MountPoint, Arch=Arch) #*** Broken, not moved yet ***

                    #Tear down chroot.
                    CoreBackendTools().TearDownChroot(MountPoint=MountPoint)

            wx.CallAfter(ParentWindow.UpdateOutputBox, "\n###Finished removing the old bootloader from OS: "+OS+"...###\n")

            if retval != 0:
                #Something went wrong! Log it and notify the user.
                logger.error("BootloaderRemovalTools: Main().RemoveOldBootloader(): Failed to remove "+Bootloader+" from OS: "+OS+"! We'll continue anyway. Warn the user.")
                DialogTools().ShowMsgDlg(Kind="error", Message="WxFixBoot failed to remove "+Bootloader+" from: "+OS+"! This probably doesn't matter; when we install the new bootloader, it should take precedence over the old one anyway. Make sure you check that OS after WxFixBoot finishes its operations.")

            wx.CallAfter(ParentWindow.UpdateCurrentProgress, 27+(22/len(OSsForBootloaderRemoval)))

        #Log and notify the user that we're finished remving bootloaders.
        logger.info("BootloaderRemovalTools: Main().RemoveOldBootloader(): Finished removing bootloaders...")
        wx.CallAfter(ParentWindow.UpdateCurrentOpText, Message="Finished removing old bootloaders...")
        wx.CallAfter(ParentWindow.UpdateCurrentProgress, 50)
        DialogTools().ShowMsgDlg(Kind="info", Message="Finished removing old bootloaders! WxFixBoot will now install your new bootloader to: "+', '.join(OSsForBootloaderInstallation)+".")

    def RemoveGRUBLEGACY(self, PackageManager, UseChroot, Arch, MountPoint="None"): #*** Change when we switch to always using shell=True ***
        """Remove GRUB-LEGACY."""
        if PackageManager == "apt-get":
            if UseChroot == False:
                retval = CoreBackendTools().StartThreadProcess(['apt-get', 'remove', '-y', 'grub', 'grub-legacy-doc', 'grub-common'], ShowOutput=False)

            else:
                retval = CoreBackendTools().StartThreadProcess(['chroot', MountPoint, 'apt-get', 'remove', '-y', 'grub', 'grub-legacy-doc', 'grub-common'], ShowOutput=False)
        
        #Return the return value.
        return retval

    def RemoveGRUB2(self, PackageManager, UseChroot, Arch, MountPoint="None"): #*** Change when we switch to always using shell=True ***
        """Remove GRUB2."""
        if PackageManager == "apt-get":
            if UseChroot == False:
                retval = CoreBackendTools().StartThreadProcess(['apt-get', 'remove', '-y', 'grub-pc', 'grub-pc-bin', 'grub-common'])

            else:
                retval = CoreBackendTools().StartThreadProcess(['chroot', MountPoint, 'apt-get', 'remove', '-y', 'grub-pc', 'grub-pc-bin', 'grub-common'])
        
        #Return the return value.
        return retval
