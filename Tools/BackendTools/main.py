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

#Begin Main Class. *** Make these use BootloaderInfo dictionary to get config for each bootloader ***
class Main():
    def RemoveOldBootloader(self): #*** Handle return values better, and return them ***
        """Remove the currently installed bootloader."""
        logger.debug("MainBackendTools: Main().RemoveOldBootloader(): Preparing to remove old bootloaders...")
        wx.CallAfter(ParentWindow.UpdateCurrentOpText, Message="Removing old bootloaders...")
        wx.CallAfter(ParentWindow.UpdateCurrentProgress, 27)
        wx.CallAfter(ParentWindow.UpdateOutputBox, "\n###Removing old bootloaders...###\n")

        #Loop through each OS in SystemInfo["OSsForBootloaderRemoval"], and provide information to the function that will remove the bootloader.
        for OS in SystemInfo["OSsForBootloaderRemoval"]:
            #For each OS that needs the bootloader removed, grab the partition, and the package manager.
            Partition = OSInfo[OS]["Partition"]
            PackageManager = OSInfo[OS]["PackageManager"]

            logger.info("MainBackendTools: Main().RemoveOldBootloader(): Removing "+SystemInfo["Bootloader"]+" from OS: "+OS+"...")
            wx.CallAfter(ParentWindow.UpdateOutputBox, "\n###Removing the old bootloader from OS: "+OS+"...###\n")
            
            #If we're not on a live disk, and the partition is RootFS, let the remover function know that we aren't using chroot.
            if SystemInfo["IsLiveDisk"] == False and Partition == SystemInfo["RootFS"]:
                logger.debug("MainBackendTools: Main().RemoveOldBootloader(): Modifying current OS so not using chroot...")
                UseChroot = False
                UnmountAfter = False
                MountPoint = None

            else:
                logger.debug("MainBackendTools: Main().RemoveOldBootloader(): Using chroot to modify another OS...")
                UseChroot = True
                MountPoint = "/mnt"+Partition

                #Check if the partition is mounted.
                if CoreTools.IsMounted(Partition, MountPoint):
                    UnmountAfter = False

                else:
                    UnmountAfter = True

                    #Mount the partition using the global mount function.
                    Retval = CoreTools.MountPartition(Partition=Partition, MountPoint=MountPoint)

                    if Retval != 0:
                        logger.error("MainBackendTools: Main().RemoveOldBootloader(): Failed to mount "+Partition+"! Warn the user and skip this OS.") #*** Shall we remove it from all bootloader operations? *** *** Ask the user to try again? ***
                        DialogTools.ShowMsgDlg(Kind="error", Message="WxixBoot failed to mount the partition containing: "+OS+"! This OS will now be skipped.")
                        continue

                #Set up chroot.
                Retval = CoreTools.SetUpChroot(MountPoint)

                if Retval != 0:
                    logger.error("MainBackendTools: Main().RemoveOldBootloader(): Failed to set up chroot at "+MountPoint+"! Attempting to continue anyway...") #*** What should we do here? ***

                #If there's a seperate /boot partition for this OS, make sure it's mounted. *** Read this OS's FSTAB instead of hoping that this works, cos then we can use the global mount function to do this *** *** this might mount other stuff and interfere too ***
                CoreTools.StartProcess("chroot "+MountPoint+" mount -av", ShowOutput=False)

            #Remove the bootloader.
            if SystemInfo["Bootloader"] == "GRUB-LEGACY":
                logger.info("MainBackendTools: Main().RemoveOldBootloader(): Removing GRUB-LEGACY...")
                retval = BootloaderRemovalTools.RemoveGRUBLEGACY(PackageManager=PackageManager, UseChroot=UseChroot, MountPoint=MountPoint)

            elif SystemInfo["Bootloader"] == "GRUB2":
                logger.info("MainBackendTools: Main().RemoveOldBootloader(): Removing GRUB2...")
                retval = BootloaderRemovalTools.RemoveGRUB2(PackageManager=PackageManager, UseChroot=UseChroot, MountPoint=MountPoint)

            elif SystemInfo["Bootloader"] == "LILO":
                logger.info("MainBackendTools: Main().RemoveOldBootloader(): Removing LILO...")
                retval = BootloaderRemovalTools.RemoveLILO(PackageManager=PackageManager, UseChroot=UseChroot, MountPoint=MountPoint)

            elif SystemInfo["Bootloader"] == "GRUB-UEFI":
                logger.info("MainBackendTools: Main().RemoveOldBootloader(): Removing GRUB-UEFI...")
                retval = BootloaderRemovalTools.RemoveGRUBUEFI(PackageManager=PackageManager, UseChroot=UseChroot, MountPoint=MountPoint)

            elif SystemInfo["Bootloader"] == "ELILO":
                logger.info("MainBackendTools: Main().RemoveOldBootloader(): Removing ELILO...")
                retval = BootloaderRemovalTools.RemoveELILO(PackageManager=PackageManager, UseChroot=UseChroot, MountPoint=MountPoint)

            #Tear down chroot if needed.
            if UseChroot:
                Retval = CoreTools.TearDownChroot(MountPoint=MountPoint)

                if Retval != 0:
                    logger.error("MainBackendTools: Main().RemoveOldBootloader(): Failed to remove chroot at "+MountPoint+"! Attempting to continue anyway...") #*** What should we do here? ***

            #Unmount partition if needed.
            if UnmountAfter:
                UnmountRetval = CoreTools.Unmount(MountPoint)

                if UnmountRetval != 0:
                    logger.error("MainBackendTools: Main().RemoveOldBootloader(): Couldn't unmount "+MountPoint+"! Continuing anyway...")

            wx.CallAfter(ParentWindow.UpdateOutputBox, "\n###Finished removing the old bootloader from OS: "+OS+"...###\n")

            if retval != 0:
                #Something went wrong! Log it and notify the user.
                logger.error("MainBackendTools: Main().RemoveOldBootloader(): Failed to remove "+SystemInfo["Bootloader"]+" from OS: "+OS+"! We'll continue anyway. Warn the user.")
                DialogTools.ShowMsgDlg(Kind="error", Message="WxFixBoot failed to remove "+SystemInfo["Bootloader"]+" from: "+OS+"! This probably doesn't matter; when we install the new bootloader, it should take precedence over the old one anyway. Make sure you check that OS after WxFixBoot finishes its operations.")

            wx.CallAfter(ParentWindow.UpdateCurrentProgress, 27+(22//len(SystemInfo["OSsForBootloaderRemoval"])))

        #Log and notify the user that we're finished removing bootloaders.
        logger.info("MainBackendTools: Main().RemoveOldBootloader(): Finished removing bootloaders...")
        wx.CallAfter(ParentWindow.UpdateCurrentOpText, Message="Finished removing old bootloaders...")
        wx.CallAfter(ParentWindow.UpdateCurrentProgress, 50)
        DialogTools.ShowMsgDlg(Kind="info", Message="Finished removing old bootloaders! WxFixBoot will now install your new bootloader to: "+', '.join(SystemInfo["OSsForBootloaderInstallation"])+".")

    def InstallNewBootloader(self):
        """Install a new bootloader."""
        wx.CallAfter(ParentWindow.UpdateCurrentProgress, 52)  
        BootloaderInstallSucceded = True     

        #Loop through SystemInfo["OSsForBootloaderInstallation"], and provide information to the function that will install the bootloader.
        for OS in SystemInfo["OSsForBootloaderInstallation"]:
            #For each OS that needs the new bootloader installed, grab the partition, and the package manager.
            Partition = OSInfo[OS]["Partition"]
            PackageManager = OSInfo[OS]["PackageManager"]

            logger.info("MainBackendTools: Main().InstallNewBootloader(): Preparing to install the new bootloader ("+SystemInfo["BootloaderToInstall"]+") in OS: "+OS+"...")
            wx.CallAfter(ParentWindow.UpdateOutputBox, "\n###Preparing to install "+SystemInfo["BootloaderToInstall"]+" in OS: "+OS+"...###\n")
            wx.CallAfter(ParentWindow.UpdateCurrentOpText, Message="Preparing to install the new bootloader(s)...")

            #If we're not on a live disk, and the partition is RootFS, let the installer functions know that we aren't using chroot.
            if SystemInfo["IsLiveDisk"] == False and Partition == SystemInfo["RootFS"]:
                logger.debug("MainBackendTools: Main().InstallNewBootloader(): Modifying current OS so not using chroot...")
                UseChroot = False
                UnmountAfter = False
                MountPoint = "/"

            #Otherwise, setup the chroot and everything else first, and tell them we are using chroot, and pass the mountpoint to them.
            else:
                logger.debug("MainBackendTools: Main().InstallNewBootloader(): Using chroot to modify another OS...")
                UseChroot = True
                MountPoint = "/mnt"+Partition

                #Check if the partition is mounted.
                if CoreTools.IsMounted(Partition, MountPoint):
                    UnmountAfter = False

                else:
                    UnmountAfter = True

                    Retval = CoreTools.MountPartition(Partition=Partition, MountPoint=MountPoint)

                    if Retval != 0:
                        logger.error("MainBackendTools: Main().InstallNewBootloader(): Failed to mount "+Partition+"! Warn the user and skip this OS.")
                        DialogTools.ShowMsgDlg(Kind="error", Message="WxFixBoot failed to mount the partition containing: "+OS+"! Bootloader installation cannot continue! This may leave your system, or this OS, in an unbootable state. It is recommended to do a Bad Sector check, and then try again.") #*** Is this good advice? Try to determine the cause of the problem ***
                        continue

                #Set up chroot.
                Retval = CoreTools.SetUpChroot(MountPoint=MountPoint)

                if Retval != 0:
                    logger.error("MainBackendTools: Main().InstallNewBootloader(): Failed to set up chroot at "+MountPoint+"! Attempting to continue anyway...") #*** What should we do here? ***

                #If there's a seperate /boot partition for this OS, make sure it's mounted.
                CoreTools.StartProcess("chroot "+MountPoint+" mount -av", ShowOutput=False) #*** Read this OS's FSTAB instead of hoping that this works, cos then we can use the global mount function to do this ***

            #Update the package lists.
            if BootloaderInstallationTools.UpdatePackageLists(PackageManager=PackageManager, UseChroot=UseChroot, MountPoint=MountPoint) != 0:
                logger.error("MainBackendTools: Main().InstallNewBootloader(): Failed to Update the Package Information! Continuing anyway...")
    
            wx.CallAfter(ParentWindow.UpdateCurrentOpText, Message="Installing the new bootloader(s)...")
            wx.CallAfter(ParentWindow.UpdateCurrentProgress, 55)       
            wx.CallAfter(ParentWindow.UpdateOutputBox, "\n###Installing the new bootloader in OS: "+OS+"...###\n")

            #Install the bootloader.
            if SystemInfo["BootloaderToInstall"] == "GRUB2":
                logger.info("MainBackendTools: Main().InstallNewBootloader(): Installing GRUB2...")
                retval = BootloaderInstallationTools.InstallGRUB2(PackageManager=PackageManager, UseChroot=UseChroot, MountPoint=MountPoint)

            elif SystemInfo["BootloaderToInstall"] == "LILO":
                logger.info("MainBackendTools: Main().InstallNewBootloader(): Installing LILO...")
                retval = BootloaderInstallationTools.InstallLILO(PackageManager=PackageManager, UseChroot=UseChroot, MountPoint=MountPoint)

            elif SystemInfo["BootloaderToInstall"] == "GRUB-UEFI":
                logger.info("MainBackendTools: Main().InstallNewBootloader(): Installing GRUB-UEFI...")
                #Mount the UEFI partition at MountPoint/boot/efi.
                #Unmount it first though, in case it's already mounted. *** Alternately, check where it's mounted and leave it if it's okay ***
                if CoreTools.Unmount(SystemInfo["UEFISystemPartition"]) != 0:
                    logger.error("MainBackendTools: Main().InstallNewBootloader(): Failed to unmount "+SystemInfo["UEFISystemPartition"]+"! This probably doesn't matter...")

                if CoreTools.MountPartition(Partition=SystemInfo["UEFISystemPartition"], MountPoint=MountPoint+"/boot/efi") != 0:
                    logger.error("MainBackendTools: Main().InstallNewBootloader(): Failed to mount "+SystemInfo["UEFISystemPartition"]+"! to "+MountPoint+"/boot/efi! *** TODO: Abort bootloader installation. *** For now, continue anyway...")

                retval = BootloaderInstallationTools.InstallGRUBUEFI(PackageManager=PackageManager, UseChroot=UseChroot, MountPoint=MountPoint)

            elif SystemInfo["BootloaderToInstall"] == "ELILO":
                logger.info("MainBackendTools: Main().InstallNewBootloader(): Installing ELILO...")
                #Unmount the UEFI Partition now, and update the mtab inside chroot (if using chroot).
                if CoreTools.Unmount(SystemInfo["UEFISystemPartition"]) != 0:
                    logger.error("MainBackendTools: Main().InstallNewBootloader(): Failed to unmount the EFI partition! If installing ELILO fails this might be the reason. Continuing anyway...") #*** Installation won't work if unmounting failed! ***

                if UseChroot:
                    CoreTools.UpdateChrootMtab(MountPoint=MountPoint)

                retval = BootloaderInstallationTools.InstallELILO(PackageManager=PackageManager, UseChroot=UseChroot, MountPoint=MountPoint)

            #If there's a seperate /boot partition for this OS, make sure it's unmounted before removing the chroot.
            if CoreTools.Unmount(MountPoint+"/boot") != 0:
                logger.error("MainBackendTools: Main().InstallNewBootloader(): Failed to unmount "+MountPoint+"/boot! *** TODO: Check if there is a /boot partition first ***. This probably doesn't matter...") #*** Why not check if there is one first? ***

            if UseChroot:
                logger.debug("MainBackendTools: Main().InstallNewBootloader(): Removing chroot...")
                #Tear down chroot.
                Retval = CoreTools.TearDownChroot(MountPoint=MountPoint)

                if Retval != 0:
                    logger.error("MainBackendTools: Main().InstallNewBootloader(): Failed to remove chroot at "+MountPoint+"! Attempting to continue anyway...") #*** What should we do here? ***

            if UnmountAfter:
                if CoreTools.Unmount(MountPoint) != 0:
                    logger.error("MainBackendTools: Main().InstallNewBootloader(): Failed to unmount "+MountPoint+"! Continuing anyway...")

            if retval != 0:
                #Something went wrong! Log it and notify the user.
                BootloaderInstallSucceded = False
                logger.error("MainBackendTools: Main().InstallNewBootloader(): Failed to install "+SystemInfo["BootloaderToInstall"]+" in OS: "+OS+"! This may mean the system (or this OS) is now unbootable! We'll continue anyway. Warn the user.")
                DialogTools.ShowMsgDlg(Kind="error", Message="WxFixBoot failed to install "+SystemInfo["BootloaderToInstall"]+" in: "+OS+"! This may leave this OS, or your system, in an unbootable state. It is recommended to do a Bad Sector check, unplug any non-essential devices, and then try again.") #*** Maybe ask to try again right now ***

            wx.CallAfter(ParentWindow.UpdateOutputBox, "\n###Finished installing "+SystemInfo["BootloaderToInstall"]+" in OS: "+OS+"...###\n")

        #Log and notify the user that we're finished removing bootloaders.
        logger.info("MainBackendTools: Main().InstallNewBootloader(): Finished Installing bootloaders...")
        wx.CallAfter(ParentWindow.UpdateCurrentOpText, Message="Finished Installing bootloaders...")
        wx.CallAfter(ParentWindow.UpdateCurrentProgress, 75)
        return BootloaderInstallSucceded #*** Keep the results for each OS here, and note which one(s) failed! ***

    def SetNewBootloaderConfig(self): #*** Use UseChroot here for readability? ***
        """Manage setting new bootloader config."""
        logger.debug("MainBackendTools: Main().SetNewBootloaderConfig(): Preparing to set bootloader config in OS(s): "+', '.join(SystemInfo["OSsForBootloaderInstallation"])+"...")
        wx.CallAfter(ParentWindow.UpdateCurrentOpText, Message="Preparing to set the new bootloaders' config...")
        wx.CallAfter(ParentWindow.UpdateCurrentProgress, 77)

        #Loop through SystemInfo["OSsForBootloaderInstallation"], and provide information to the function that will set the bootloaders' config.
        for OS in SystemInfo["OSsForBootloaderInstallation"]:
            #For each OS that needs the new bootloader configured, grab the partition, and the package manager.
            logger.info("MainBackendTools: Main().SetNewBootloaderConfig(): Setting the new bootloader config for OS: "+OS+"...")

            #Grab the OS's partition and package manager.
            Partition = OSInfo[OS]["Partition"]
            PackageManager = OSInfo[OS]["PackageManager"]

            wx.CallAfter(ParentWindow.UpdateOutputBox, "\n###Preparing to set the new bootloaders' config for OS: "+OS+"...###\n")

            #Grab the architecture.
            Arch = OSInfo[OS]["Arch"]

            wx.CallAfter(ParentWindow.UpdateCurrentOpText, Message="Setting the new bootloader's config...")
            wx.CallAfter(ParentWindow.UpdateCurrentProgress, 79)
            wx.CallAfter(ParentWindow.UpdateOutputBox, "\n###Setting the new bootloader's config for OS: "+OS+"...###\n")

            #Check if the Partition is RootFS, if we're not on a live disk.
            if SystemInfo["IsLiveDisk"] == False and Partition == SystemInfo["RootFS"]:
                logger.debug("MainBackendTools: Main().SetNewBootloaderConfig(): We're modifying the current OS...")
                #If so, make sure this will work for this OS too, and avoid setting mountpoint, so the config instructions below look in the right place for the config files.
                MountPoint = ""
                UnmountPartitionAfter = False

            else:
                logger.debug("MainBackendTools: Main().SetNewBootloaderConfig(): We're modifying another OS...")
                #If not, set mountpoint to the actual mountpoint.
                MountPoint = "/mnt"+Partition

                #Check if the partition is mounted.
                if CoreTools.IsMounted(Partition, MountPoint):
                    UnmountPartitionAfter = False

                else:
                    UnmountPartitionAfter = True

                    #Mount the partition.
                    Retval = CoreTools.MountPartition(Partition=Partition, MountPoint=MountPoint)

                    if Retval != 0:
                        #Ignore this partition.
                        logger.warning("MainBackendTools: Main().SetNewBootloaderConfig(): Failed to mount "+Partition+"! Ignoring this partition...")
                        continue

                #Set up chroot.
                Retval = CoreTools.SetUpChroot(MountPoint=MountPoint)
                if Retval != 0:
                    logger.error("MainBackendTools: Main().SetNewBootloaderConfig(): Failed to set up chroot at "+MountPoint+"! Attempting to continue anyway...") #*** What should we do here? ***

                wx.CallAfter(ParentWindow.UpdateCurrentProgress, 81)

            #Look for the configuration file, based on which SetConfig() function we're about to run.
            if SystemInfo["BootloaderToInstall"] == "GRUB2":
                #Check MountPoint/etc/default/grub exists. *** What do we do if it doesn't? Maybe have a template to put there ***
                if os.path.isfile(MountPoint+"/etc/default/grub"):
                    #It does, we'll run the function to set the config now.
                    logger.info("MainBackendTools: Main().SetNewBootloaderConfig(): Setting GRUB2-BIOS Configuration...")
                    BootloaderConfigSettingTools.SetGRUB2Config(filetoopen=MountPoint+"/etc/default/grub")

                #Now Install GRUB2 to the MBR. *** Is this necessary when updating it? ***
                logger.info("MainBackendTools: Main().SetNewBootloaderConfig(): Installing GRUB2 to MBR...")
                BootloaderConfigSettingTools.InstallGRUB2ToMBR(PackageManager=PackageManager, MountPoint=MountPoint)

                #Update GRUB.
                logger.info("MainBackendTools: Main().SetNewBootloaderConfig(): Updating GRUB2 Configuration...")
                BootloaderConfigSettingTools.UpdateGRUB2(PackageManager=PackageManager, MountPoint=MountPoint)

                #Set the default OS.
                logger.info("MainBackendTools: Main().SetNewBootloaderConfig(): Setting GRUB2 Default OS...")
                BootloaderConfigSettingTools.SetGRUB2DefaultOS(OS=OS, MountPoint=MountPoint)

            elif SystemInfo["BootloaderToInstall"] == "GRUB-UEFI":
                #Check MountPoint/etc/default/grub exists. *** What do we do if it doesn't? Maybe have a template to put there ***
                if os.path.isfile(MountPoint+"/etc/default/grub"):
                    #It does, we'll run the function to set the config now.
                    logger.info("MainBackendTools: Main().SetNewBootloaderConfig(): Setting GRUB2-UEFI Configuration...")
                    BootloaderConfigSettingTools.SetGRUB2Config(filetoopen=MountPoint+"/etc/default/grub")

                #Mount the UEFI partition at MountPoint/boot/efi.
                if CoreTools.MountPartition(Partition=SystemInfo["UEFISystemPartition"], MountPoint=MountPoint+"/boot/efi") != 0:
                    logger.error("MainBackendTools: Main().SetNewBootloaderConfig(): Couldn't mount EFI partition "+SystemInfo["UEFISystemPartition"]+" to install bootloader! *** TODO: Cancel bootloader operations *** Continuing for now...")

                #Now Install GRUB-UEFI to the UEFI Partition. *** Is this necessary when updating it? ***
                logger.info("MainBackendTools: Main().SetNewBootloaderConfig(): Installing GRUB2 to "+SystemInfo["UEFISystemPartition"]+"...")
                BootloaderConfigSettingTools.InstallGRUBUEFIToPartition(PackageManager=PackageManager, MountPoint=MountPoint, UEFISystemPartitionMountPoint=MountPoint+"/boot/efi", Arch=Arch)

                #Update GRUB.
                logger.info("MainBackendTools: Main().SetNewBootloaderConfig(): Updating GRUB2 Configuration...")
                BootloaderConfigSettingTools.UpdateGRUB2(PackageManager=PackageManager, MountPoint=MountPoint)

                #Make an entry in fstab for the UEFI Partition, if needed.
                HelperBackendTools.WriteFSTABEntryForUEFIPartition(MountPoint=MountPoint)

                #Copy and backup EFI files where needed.
                HelperBackendTools.BackupUEFIFiles(MountPoint=MountPoint)
                HelperBackendTools.CopyUEFIFiles(MountPoint=MountPoint)

                #Set the default OS.
                logger.info("MainBackendTools: Main().SetNewBootloaderConfig(): Setting GRUB2 Default OS...")
                BootloaderConfigSettingTools.SetGRUB2DefaultOS(OS=OS, MountPoint=MountPoint)

            elif SystemInfo["BootloaderToInstall"] == "LILO":
                #Make LILO's config file.
                logger.info("MainBackendTools: Main().SetNewBootloaderConfig(): Making LILO's configuration file...")

                if MountPoint == "":
                    Retval = CoreTools.StartProcess("liloconfig -f", ShowOutput=False)

                else:
                    Retval = CoreTools.StartProcess("chroot "+MountPoint+" liloconfig -f", ShowOutput=False)

                if Retval != 0:
                    logger.error("MainBackendTools: Main().SetNewBootloaderConfig(): liloconfig didn't run successfully! Attempting to continue anyway...")

                #Check the config file exists for lilo. *** What do we do if it doesn't? Have a template one to put there? ***
                if os.path.isfile(MountPoint+"/etc/lilo.conf"):
                    #It does, we'll run the function to set the config now.
                    logger.info("MainBackendTools: Main().SetNewBootloaderConfig(): Setting LILO Configuration...")
                    BootloaderConfigSettingTools.SetLILOConfig(filetoopen=MountPoint+"/etc/lilo.conf", PackageManager=PackageManager, MountPoint=MountPoint)
    
                    #Also, set the OS entries.
                    logger.info("MainBackendTools: Main().SetNewBootloaderConfig(): Creating LILO OS Entries...")
                    BootloaderConfigSettingTools.MakeLILOOSEntries(filetoopen=MountPoint+"/etc/lilo.conf", PackageManager=PackageManager, MountPoint=MountPoint)

                #Now Install LILO to the MBR.
                logger.info("MainBackendTools: Main().SetNewBootloaderConfig(): Installing LILO to the MBR...")
                BootloaderConfigSettingTools.InstallLILOToMBR(PackageManager=PackageManager, MountPoint=MountPoint)

            elif SystemInfo["BootloaderToInstall"] == "ELILO":
                #Unmount the UEFI Partition now, and update mtab in the chroot.
                if CoreTools.Unmount(SystemInfo["UEFISystemPartition"]) != 0:
                    logger.error("MainBackendTools: Main().SetNewBootloaderConfig(): Failed to unmount EFI partition "+SystemInfo["UEFISystemPartition"]+"! Continuing anyway...") #*** Installation will fail if this happens! ***

                CoreTools.UpdateChrootMtab(MountPoint=MountPoint)

                #Make ELILO's config file.
                logger.info("MainBackendTools: Main().SetNewBootloaderConfig(): Making ELILO's configuration file...")

                if MountPoint == "":
                    Retval = CoreTools.StartProcess("elilo -b "+SystemInfo["UEFISystemPartition"]+" --autoconf", ShowOutput=False)

                else:
                    Retval = CoreTools.StartProcess("chroot "+MountPoint+" elilo -b "+SystemInfo["UEFISystemPartition"]+" --autoconf", ShowOutput=False)

                if Retval != 0:
                    logger.error("MainBackendTools: Main().SetNewBootloaderConfig(): elilo -b "+SystemInfo["UEFISystemPartition"]+" didn't run successfully! Attempting to continue anyway...")
                #Check elilo's config file exists. *** What do we do if it doesn't? Have a template to put there? ***
                if os.path.isfile(MountPoint+"/etc/elilo.conf"):
                    #It does, we'll run the function to set the config now.
                    logger.info("MainBackendTools: Main().SetNewBootloaderConfig(): Setting ELILO Configuration...")
                    BootloaderConfigSettingTools.SetELILOConfig(filetoopen=MountPoint+"/etc/elilo.conf", PackageManager=PackageManager, MountPoint=MountPoint)

                    #Also, set the OS entries.
                    logger.info("MainBackendTools: Main().SetNewBootloaderConfig(): Creating ELILO OS Entries...")
                    BootloaderConfigSettingTools.MakeLILOOSEntries(filetoopen=MountPoint+"/etc/elilo.conf", PackageManager=PackageManager, MountPoint=MountPoint)

                #Now Install ELILO to the UEFI Partition.
                logger.info("MainBackendTools: Main().SetNewBootloaderConfig(): Installing ELILO to "+SystemInfo["UEFISystemPartition"]+"...")
                BootloaderConfigSettingTools.InstallELILOToPartition(PackageManager=PackageManager, MountPoint=MountPoint)

                #Mount the UEFI partition at MountPoint/boot/efi.
                if CoreTools.MountPartition(Partition=SystemInfo["UEFISystemPartition"], MountPoint=MountPoint+"/boot/efi") != 0:
                    logger.error("MainBackendTools: Main().SetNewBootloaderConfig(): Failed to mount EFI partition "+SystemInfo["UEFISystemPartition"]+"! Continuing anyway...")

                #Copy and backup UEFI files where needed.
                HelperBackendTools.BackupUEFIFiles(MountPoint=MountPoint)
                HelperBackendTools.CopyUEFIFiles(MountPoint=MountPoint)

            #Tear down chroot if needed.
            if MountPoint != "":
                Retval = CoreTools.TearDownChroot(MountPoint=MountPoint)

                if Retval != 0:
                    logger.error("MainBackendTools: Main().SetNewBootloaderConfig(): Failed to remove chroot at "+MountPoint+"! Attempting to continue anyway...") #*** What should we do here? ***

            #Unmount the partition if needed.
            if UnmountPartitionAfter:
                if CoreTools.Unmount(MountPoint) != 0:
                    logger.error("MainBackendTools: Main().SetNewBootloaderConfig(): Failed to unmount "+MountPoint+"! Continuing anyway...")

            wx.CallAfter(ParentWindow.UpdateOutputBox, "\n###Finished setting the new bootloader's config for OS: "+OS+"...###\n")

        logger.debug("MainBackendTools: Main().SetNewBootloaderConfig(): Finished setting bootloader config.")
        wx.CallAfter(ParentWindow.UpdateCurrentOpText, Message="Finished setting the new bootloader's config!")
        wx.CallAfter(ParentWindow.UpdateCurrentProgress, 100)

#End main Class.
