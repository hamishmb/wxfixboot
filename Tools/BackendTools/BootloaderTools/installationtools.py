#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Bootloader Installation Tools in the Bootloader Tools Package in the Backend Tools package for WxFixBoot Version 1.1~pre1
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
    def InstallNewBootloader(self): #*** Reduce code duplication ***
        """Install a new bootloader."""
        #Install the new bootloader on the chosen OS.
        wx.CallAfter(ParentWindow.UpdateCurrentOpText, Message="Preparing to install the new bootloader(s)...") #*** Does this need to be here? ***
        wx.CallAfter(ParentWindow.UpdateCurrentProgress, 52)  
        BootloaderInstallSucceded = True     

        #Loop through OSsForBootloaderInstallation, and provide information to the function that will install the bootloader.
        for OS in OSsForBootloaderInstallation:
            #For each OS that needs the new bootloader installed, grab the partition, and the package manager.
            Partition = OS.split()[-5]
            PackageManager = OS.split()[-1]

            logger.info("BootloaderInstallationTools: Main().InstallNewBootloader(): Preparing to install the new bootloader "+BootloaderToInstall+" in OS: "+OS+"...")
            wx.CallAfter(ParentWindow.UpdateOutputBox, "\n###Preparing to install the new bootloader in OS: "+OS+"...###\n") #*** Show the new bootloader here ***
            wx.CallAfter(ParentWindow.UpdateCurrentOpText, Message="Preparing to install the new bootloader(s)...")

            #Grab the architecture.
            Arch = OS.split()[-8]
            if Arch == "64-bit":
                Arch = "x86_64"
            else:
                Arch = "i686"

            #If we're not on a live disk, and the partition is AutoRootFS, let the installer function know that we aren't using chroot.
            if LiveDisk == False and Partition == AutoRootFS:
                #Update the package lists.
                retval = self.UpdatePackageLists(PackageManager=PackageManager, UseChroot=False)

                wx.CallAfter(ParentWindow.UpdateCurrentOpText, Message="Installing the new bootloader(s)...")
                wx.CallAfter(ParentWindow.UpdateCurrentProgress, 55)       
                wx.CallAfter(ParentWindow.UpdateOutputBox, "\n###Installing the new bootloader in OS: "+OS+"...###\n")

                if BootloaderToInstall == "GRUB2":
                    retval = self.InstallGRUB2(PackageManager=PackageManager, UseChroot=False, Arch=Arch)

                elif BootloaderToInstall == "LILO":
                    retval = self.InstallLILO(PackageManager=PackageManager, UseChroot=False, Arch=Arch)

                elif BootloaderToInstall == "GRUB-UEFI":
                    #Mount the UEFI partition at /boot/efi.
                    #Unmount it first though, in case it's already mounted.
                    CoreTools().Unmount(UEFISystemPartition) #*** Check it worked! ***
                    CoreTools().MountPartition(Partition=UEFISystemPartition, MountPoint="/boot/efi") #*** Check this worked! ***

                    retval = self.InstallGRUBUEFI(PackageManager=PackageManager, UseChroot=False, Arch=Arch)

                elif BootloaderToInstall == "ELILO":
                    #Unmount the UEFI Partition now.
                    CoreTools().Unmount(UEFISystemPartition) #*** Check it worked! ***

                    retval = self.InstallELILO(PackageManager=PackageManager, UseChroot=False, Arch=Arch)

            #Otherwise, setup the chroot and everything else first, and tell it we are using chroot, and pass the mountpoint to it.
            else:
                #Mount the partition using the global mount function.
                MountPoint = "/mnt"+Partition
                Retval = CoreTools().MountPartition(Partition=Partition, MountPoint=MountPoint)

                if Retval != 0:
                    logger.error("BootloaderInstallationTools: Main().InstallNewBootloader(): Failed to remount "+Partition+"! Warn the user and skip this OS.")
                    DialogTools().ShowMsgDlg(Kind="error", Message="WxFixBoot failed to mount the partition containing: "+OS+"! Bootloader installation cannot continue! This may leave your system, or this OS, in an unbootable state. It is recommended to do a Bad Sector check, and then try again.")

                else:
                    #Set up chroot.
                    CoreBackendTools().SetUpChroot(MountPoint=MountPoint)

                    #If there's a seperate /boot partition for this OS, make sure it's mounted.
                    CoreBackendTools().StartThreadProcess(['chroot', MountPoint, 'mount', '-av'], ShowOutput=False)

                    #Update the package lists.
                    retval = self.UpdatePackageLists(PackageManager=PackageManager, UseChroot=True, MountPoint=MountPoint)

                    wx.CallAfter(ParentWindow.UpdateCurrentOpText, Message="Installing the new bootloader(s)...")
                    wx.CallAfter(ParentWindow.UpdateCurrentProgress, 55)       
                    wx.CallAfter(ParentWindow.UpdateOutputBox, "\n###Installing the new bootloader in OS: "+OS+"...###\n")

                    #Install the bootloader.
                    if BootloaderToInstall == "GRUB2":
                        retval = self.InstallGRUB2(PackageManager=PackageManager, UseChroot=True, MountPoint=MountPoint, Arch=Arch)

                    elif BootloaderToInstall == "LILO":
                        retval = self.InstallLILO(PackageManager=PackageManager, UseChroot=True, MountPoint=MountPoint, Arch=Arch)

                    elif BootloaderToInstall == "GRUB-UEFI":
                        #Mount the UEFI partition at MountPoint/boot/efi.
                        #Unmount it first though, in case it's already mounted. *** Alternately check where it's mounted and leave it if it's okay ***
                        CoreTools().Unmount(UEFISystemPartition) #*** Check it worked! ***
                        CoreTools().MountPartition(Partition=UEFISystemPartition, MountPoint=MountPoint+"/boot/efi") #*** Check it worked! ***
                        retval = self.InstallGRUBUEFI(PackageManager=PackageManager, UseChroot=True, MountPoint=MountPoint, Arch=Arch)

                    elif BootloaderToInstall == "ELILO":
                        #Unmount the UEFI Partition now, and update the mtab inside chroot.
                        CoreTools().Unmount(UEFISystemPartition) #*** Check it worked! ***
                        CoreBackendTools().UpdateChrootMtab(MountPoint=MountPoint)

                        retval = self.InstallELILO(PackageManager=PackageManager, UseChroot=True, MountPoint=MountPoint, Arch=Arch)

                    #If there's a seperate /boot partition for this OS, make sure it's unmounted before removing the chroot. *** No need to use chroot for this, do normally using safer global unmount function and update MTAB ***
                    CoreBackendTools().StartThreadProcess(['chroot', MountPoint, 'umount', '/boot'], ShowOutput=False)

                    #Tear down chroot.
                    CoreBackendTools().TearDownChroot(MountPoint=MountPoint)

            if retval != 0:
                #Something went wrong! Log it and notify the user.
                BootloaderInstallSucceded = False
                logger.error("BootloaderInstallationTools: Main().InstallNewBootloader(): Failed to install "+BootloaderToInstall+" in OS: "+OS+"! This may mean the system (or this OS) is now unbootable! We'll continue anyway. Warn the user.")
                DialogTools().ShowMsgDlg(Kind="error", Message="WxFixBoot failed to install "+BootloaderToInstall+" in: "+OS+"! This may leave this OS, or your system, in an unbootable state. It is recommended to do a Bad Sector check, unplug any non-essential devices, and then try again.") #*** Maybe ask to try again right now ***

            wx.CallAfter(ParentWindow.UpdateOutputBox, "\n###Finished installing the new bootloader in OS: "+OS+"...###\n") #*** Show the name of the new bootloader here ***

        #Log and notify the user that we're finished removing bootloaders.
        logger.info("BootloaderInstallationTools: Main().InstallNewBootloader(): Finished Installing bootloaders...")
        wx.CallAfter(ParentWindow.UpdateCurrentOpText, Message="Finished Installing bootloaders...")
        wx.CallAfter(ParentWindow.UpdateCurrentProgress, 75)
        return BootloaderInstallSucceded

    def UpdatePackageLists(self, PackageManager, UseChroot, MountPoint="None"): #*** Change when we switch to always using shell=True ***
        """Update the package lists so the required packages can always be found."""
        if PackageManager == "apt-get":
            if UseChroot == False:
                retval = CoreBackendTools().StartThreadProcess("DEBIAN_FRONTEND=noninteractive apt-get update", Piping=True)

            else:
                retval = CoreBackendTools().StartThreadProcess("chroot "+MountPoint+" sh -c 'DEBIAN_FRONTEND=noninteractive apt-get update'", Piping=True)
        
        #Return the return value.
        return retval

    def InstallGRUB2(self, PackageManager, UseChroot, Arch, MountPoint="None"): #*** Change when we switch to always using shell=True ***
        """Install GRUB2."""
        if PackageManager == "apt-get":
            if UseChroot == False:
                retval = CoreBackendTools().StartThreadProcess("DEBIAN_FRONTEND=noninteractive apt-get install -y grub-pc os-prober", Piping=True)

            else:
                retval = CoreBackendTools().StartThreadProcess("chroot "+MountPoint+" sh -c 'DEBIAN_FRONTEND=noninteractive apt-get install -y grub-pc os-prober'", Piping=True)
        
        #Return the return value.
        return retval

    def InstallLILO(self, PackageManager, UseChroot, Arch, MountPoint="None"): #*** Change when we switch to always using shell=True ***
        """Install LILO."""
        if PackageManager == "apt-get":
            if UseChroot == False:
                retval = CoreBackendTools().StartThreadProcess("DEBIAN_FRONTEND=noninteractive apt-get install -y lilo", Piping=True)

            else:
                retval = CoreBackendTools().StartThreadProcess("chroot "+MountPoint+" sh -c 'DEBIAN_FRONTEND=noninteractive apt-get install -y lilo'", Piping=True)
        
        #Return the return value.
        return retval

    def InstallGRUBUEFI(self, PackageManager, UseChroot, Arch, MountPoint="None"): #*** Change when we switch to always using shell=True ***
        """Install GRUB-UEFI."""
        if PackageManager == "apt-get":
            if UseChroot == False:
                retval = CoreBackendTools().StartThreadProcess("DEBIAN_FRONTEND=noninteractive apt-get install -y grub-efi os-prober", Piping=True)

            else:
                retval = CoreBackendTools().StartThreadProcess("chroot "+MountPoint+" sh -c 'DEBIAN_FRONTEND=noninteractive apt-get install -y grub-efi os-prober'", Piping=True)
        
        #Return the return value.
        return retval

   def InstallELILO(self, PackageManager, UseChroot, Arch, MountPoint="None"): #*** Change when we switch to always using shell=True ***
        """Install ELILO."""
        if PackageManager == "apt-get":
            if UseChroot == False:
                retval = CoreBackendTools().StartThreadProcess("DEBIAN_FRONTEND=noninteractive apt-get install -y elilo", Piping=True)

            else:
                retval = CoreBackendTools().StartThreadProcess("chroot "+MountPoint+" sh -c 'DEBIAN_FRONTEND=noninteractive apt-get install -y elilo'", Piping=True)
        
        #Return the return value.
        return retval

