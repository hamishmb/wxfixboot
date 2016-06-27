#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Main Backend Tools in the BackendTools Package for WxFixBoot Version 2.0~pre2
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
    def RemoveOldBootloader(self, OS): #*** Handle return values better, and return them *** *** Give more information to user when there are errors ***
        """Remove the currently installed bootloader."""
        logger.info("MainBackendTools: Main().RemoveOldBootloader(): Removing "+BootloaderInfo[OS]["Bootloader"]+" from "+OS+"...")
        wx.CallAfter(ParentWindow.UpdateCurrentProgress, 27)
        wx.CallAfter(ParentWindow.UpdateCurrentOpText, Message="Removing "+BootloaderInfo[OS]["Bootloader"]+" from "+OS+"......")
        wx.CallAfter(ParentWindow.UpdateOutputBox, "\n###Removing "+BootloaderInfo[OS]["Bootloader"]+" from "+OS+"...###\n")
            
        #If this is the current OS, let the remover function know that we aren't using chroot.
        if OSInfo[OS]["IsCurrentOS"]:
            logger.debug("MainBackendTools: Main().RemoveOldBootloader(): Modifying current OS so not using chroot...")
            UseChroot, UnmountAfter, MountPoint = (False, False, None)

        else:
            logger.debug("MainBackendTools: Main().RemoveOldBootloader(): Using chroot to modify another OS...")
            UseChroot = True
            MountPoint = "/tmp/wxfixboot/mountpoints"+OSInfo[OS]["Partition"]

            #Check if the partition is mounted.
            UnmountAfter = not CoreTools.IsMounted(OSInfo[OS]["Partition"], MountPoint)

            if UnmountAfter:
                #Mount the partition using the global mount function.
                if CoreTools.MountPartition(Partition=OSInfo[OS]["Partition"], MountPoint=MountPoint) != 0:
                    logger.error("MainBackendTools: Main().RemoveOldBootloader(): Failed to mount "+OSInfo[OS]["Partition"]+"! Warn the user and skip this OS.") #*** Shall we remove it from all bootloader operations? *** *** Ask the user to try again? ***
                    DialogTools.ShowMsgDlg(Kind="error", Message="WxFixBoot failed to mount the partition containing "+OS+"! This OS will now be skipped.")
                    return False #*** Not handled at the moment ***

            #Set up chroot.
            if CoreTools.SetUpChroot(MountPoint) != 0:
                logger.error("MainBackendTools: Main().RemoveOldBootloader(): Failed to set up chroot at "+MountPoint+"! Attempting to continue anyway...") #*** What should we do here? ***

            #If there's a seperate /boot partition for this OS, make sure it's mounted.
            if OSInfo[OS]["BootPartition"] != "Unknown":
                if CoreTools.MountPartition(Partition=OSInfo[OS]["BootPartition"], MountPoint=MountPoint+"/boot") != 0:
                    logger.error("MainBackendTools: Main().RemoveOldBootloader(): Failed to mount "+OSInfo[OS]["Partition"]+"! Warn the user and skip this OS.") #*** Shall we remove it from all bootloader operations? *** *** Ask the user to try again? ***
                    DialogTools.ShowMsgDlg(Kind="error", Message="WxFixBoot failed to mount the partition containing "+OS+"'s /boot partition! This OS will now be skipped.")
                    return False #*** Not handled at the moment ***

        #Remove the bootloader. *** Test all these ***
        if BootloaderInfo[OS]["Bootloader"] == "GRUB-LEGACY":
            logger.info("MainBackendTools: Main().RemoveOldBootloader(): Removing GRUB-LEGACY...") #*** Test this ***

            if OSInfo[OS]["PackageManager"] == "apt-get":
                Cmd = "sh -c 'DEBIAN_FRONTEND=noninteractive apt-get purge -y grub grub-legacy-doc grub-common'"

        elif BootloaderInfo[OS]["Bootloader"] == "GRUB2":
            logger.info("MainBackendTools: Main().RemoveOldBootloader(): Removing GRUB2...")

            if OSInfo[OS]["PackageManager"] == "apt-get":
                Cmd = "sh -c 'DEBIAN_FRONTEND=noninteractive 'apt-get purge -y grub-pc grub-pc-bin grub-common'"

        elif BootloaderInfo[OS]["Bootloader"] == "LILO":
            logger.info("MainBackendTools: Main().RemoveOldBootloader(): Removing LILO...")

            if OSInfo[OS]["PackageManager"] == "apt-get":
                Cmd = "sh -c 'DEBIAN_FRONTEND=noninteractive 'apt-get purge -y lilo'"

        elif BootloaderInfo[OS]["Bootloader"] == "GRUB-UEFI":
            logger.info("MainBackendTools: Main().RemoveOldBootloader(): Removing GRUB-UEFI...")

            if OSInfo[OS]["PackageManager"] == "apt-get":
                Cmd = "sh -c 'DEBIAN_FRONTEND=noninteractive 'apt-get purge -y grub-efi grub-efi-amd64 grub-efi-amd64-bin grub-efi-ia32 grub-efi-ia32-bin grub-common grub2-common'"

        elif BootloaderInfo[OS]["Bootloader"] == "ELILO":
            logger.info("MainBackendTools: Main().RemoveOldBootloader(): Removing ELILO...")

            if OSInfo[OS]["PackageManager"] == "apt-get":
                Cmd = "sh -c 'DEBIAN_FRONTEND=noninteractive 'apt-get purge -y elilo'"

        if UseChroot:
            Cmd = "chroot "+MountPoint+" "+Cmd

        Retval = CoreTools.StartProcess(Cmd)

        if Retval != 0:
            logger.error("MainBackendTools: Main().RemoveOldBootloader(): Failed to remove "+BootloaderInfo[OS]["Bootloader"]+" from "+OS+"! Warning user...")
            DialogTools.ShowMsgDlg(Kind="error", Message="WxFixBoot failed to remove "+BootloaderInfo[OS]["Bootloader"]+" from "+OS+"! This OS will now be skipped.") #*** Shall we remove it from all bootloader operations? *** *** Ask the user to try again? ***

        #Tear down chroot if needed.
        if UseChroot:
            if CoreTools.TearDownChroot(MountPoint=MountPoint) != 0:
                logger.error("MainBackendTools: Main().RemoveOldBootloader(): Failed to remove chroot at "+MountPoint+"! Attempting to continue anyway...") #*** What should we do here? ***

        #Unmount partition if needed.
        if UnmountAfter:
            if CoreTools.Unmount(MountPoint) != 0:
                logger.error("MainBackendTools: Main().RemoveOldBootloader(): Couldn't unmount "+MountPoint+"! Continuing anyway...")

        wx.CallAfter(ParentWindow.UpdateOutputBox, "\n###Finished removing "+BootloaderInfo[OS]["Bootloader"]+" from "+OS+"...###\n")

        if Retval != 0:
            #Something went wrong! Log it and notify the user.
            logger.error("MainBackendTools: Main().RemoveOldBootloader(): Failed to remove "+BootloaderInfo[OS]["Bootloader"]+" from "+OS+"! We'll continue anyway. Warn the user.")
            DialogTools.ShowMsgDlg(Kind="error", Message="WxFixBoot failed to remove "+BootloaderInfo[OS]["Bootloader"]+" from "+OS+"! This probably doesn't matter; when we install the new bootloader, it should take precedence over the old one anyway. Make sure you check that "+OS+" after WxFixBoot finishes its operations.")

        #Log and notify the user that we're finished removing bootloaders.
        logger.info("MainBackendTools: Main().RemoveOldBootloader(): Finished removing "+BootloaderInfo[OS]["Bootloader"]+"...")
        wx.CallAfter(ParentWindow.UpdateCurrentOpText, Message="Finished removing "+BootloaderInfo[OS]["Bootloader"]+"...")
        wx.CallAfter(ParentWindow.UpdateCurrentProgress, 50)
        DialogTools.ShowMsgDlg(Kind="info", Message="Finished removing "+BootloaderInfo[OS]["Bootloader"]+"! WxFixBoot will now install "+BootloaderInfo[OS]["Settings"]["NewBootloader"]+" to "+OS+".")

    def InstallNewBootloader(self, OS): #*** Give more info to user when there are errors ***
        """Install a new bootloader."""
        logger.info("MainBackendTools: Main().InstallNewBootloader(): Preparing to install "+BootloaderInfo[OS]["Settings"]["NewBootloader"]+" in "+OS+"...")
        wx.CallAfter(ParentWindow.UpdateCurrentProgress, 52)  
        wx.CallAfter(ParentWindow.UpdateOutputBox, "\n###Preparing to install "+BootloaderInfo[OS]["Settings"]["NewBootloader"]+" in "+OS+"...###\n")
        wx.CallAfter(ParentWindow.UpdateCurrentOpText, Message="Preparing to install "+BootloaderInfo[OS]["Settings"]["NewBootloader"]+" in "+OS+"...")

        BootloaderInstallSucceded = True #*** Get rid of this? ***

        #If this is the current OS, let the installer functions know that we aren't using chroot.
        if OSInfo[OS]["IsCurrentOS"]:
            logger.debug("MainBackendTools: Main().InstallNewBootloader(): Modifying current OS so not using chroot...")
            UseChroot, UnmountAfter, MountPoint = (False, False, "")

        #Otherwise, setup the chroot and everything else first, and tell them we are using chroot, and pass the mountpoint to them.
        else:
            logger.debug("MainBackendTools: Main().InstallNewBootloader(): Using chroot to modify another OS...")
            UseChroot = True
            MountPoint = "/tmp/wxfixboot/mountpoints"+OSInfo[OS]["Partition"]

            #Check if the partition is mounted.
            UnmountAfter = not CoreTools.IsMounted(OSInfo[OS]["Partition"], MountPoint)

            if UnmountAfter:
                if CoreTools.MountPartition(Partition=OSInfo[OS]["Partition"], MountPoint=MountPoint) != 0:
                    logger.error("MainBackendTools: Main().InstallNewBootloader(): Failed to mount "+OSInfo[OS]["Partition"]+"! Warn the user and skip this OS.")
                    DialogTools.ShowMsgDlg(Kind="error", Message="WxFixBoot failed to mount the partition containing "+OS+"! Bootloader installation cannot continue! This may leave your system, or this OS, in an unbootable state. It is recommended to do a Bad Sector check, and then try again.") #*** Is this good advice? Try to determine the cause of the problem ***
                    return False #*** Not handled yet ***

            #Set up chroot.
            if CoreTools.SetUpChroot(MountPoint=MountPoint) != 0:
                logger.error("MainBackendTools: Main().InstallNewBootloader(): Failed to set up chroot at "+MountPoint+"! Attempting to continue anyway...") #*** What should we do here? ***

            #If there's a seperate /boot partition for this OS, make sure it's mounted.
            if OSInfo[OS]["BootPartition"] != "Unknown":
                if CoreTools.MountPartition(Partition=OSInfo[OS]["BootPartition"], MountPoint=MountPoint+"/boot") != 0:
                    logger.error("MainBackendTools: Main().RemoveOldBootloader(): Failed to mount "+OSInfo[OS]["BootPartition"]+"! Warn the user and skip this OS.") #*** Shall we remove it from all bootloader operations? *** *** Ask the user to try again? ***
                    DialogTools.ShowMsgDlg(Kind="error", Message="WxFixBoot failed to mount the partition containing "+OS+"'s /boot partition! This OS will now be skipped.")
                    return False #*** Not handled at the moment ***

        #Update the package lists.
        if OSInfo[OS]["PackageManager"] == "apt-get":
            Cmd = "sh -c 'DEBIAN_FRONTEND=noninteractive apt-get update'"

        if UseChroot:
            Cmd = "chroot "+MountPoint+" "+Cmd

        if CoreTools.StartProcess(Cmd) != 0:
            logger.error("MainBackendTools: Main().InstallNewBootloader(): Failed to Update the Package Information! Continuing anyway...") #*** Stop here? Check Internet Connection Again? ***
    
        wx.CallAfter(ParentWindow.UpdateCurrentOpText, Message="Installing "+BootloaderInfo[OS]["Settings"]["NewBootloader"]+" in "+OS+"...")
        wx.CallAfter(ParentWindow.UpdateCurrentProgress, 55)       
        wx.CallAfter(ParentWindow.UpdateOutputBox, "\n###Installing "+BootloaderInfo[OS]["Settings"]["NewBootloader"]+" in "+OS+"...###\n")

        #Install the bootloader.
        if BootloaderInfo[OS]["Settings"]["NewBootloader"] == "GRUB2":
            logger.info("MainBackendTools: Main().InstallNewBootloader(): Installing GRUB2...")

            if OSInfo[OS]["PackageManager"] == "apt-get":
                Cmd = "sh -c 'DEBIAN_FRONTEND=noninteractive apt-get install -y grub-pc os-prober'"

        elif BootloaderInfo[OS]["Settings"]["NewBootloader"] == "LILO":
            logger.info("MainBackendTools: Main().InstallNewBootloader(): Installing LILO...")

            if OSInfo[OS]["PackageManager"] == "apt-get":
                Cmd = "sh -c 'DEBIAN_FRONTEND=noninteractive apt-get install -y lilo'"

        elif BootloaderInfo[OS]["Settings"]["NewBootloader"] == "GRUB-UEFI":
            logger.info("MainBackendTools: Main().InstallNewBootloader(): Installing GRUB-UEFI...")

            #Mount the UEFI partition at MountPoint/boot/efi.
            if CoreTools.MountPartition(Partition=BootloaderInfo[OS]["BootDisk"], MountPoint=MountPoint+"/boot/efi") != 0:
                logger.error("MainBackendTools: Main().InstallNewBootloader(): Failed to mount "+BootloaderInfo[OS]["BootDisk"]+"! to "+MountPoint+"/boot/efi! Aborting bootloader installation and warning user...")
                DialogTools.ShowMsgDlg(Kind="error", Message="WxfixBoot failed to mount the partition containing "+OS+"'s EFI partition! This OS will now be skipped.")
                return False #*** Not handled at the moment ***

            if OSInfo[OS]["PackageManager"] == "apt-get":
                Cmd = "sh -c 'DEBIAN_FRONTEND=noninteractive apt-get install -y grub-efi os-prober'"

        elif BootloaderInfo[OS]["Settings"]["NewBootloader"] == "ELILO":
            logger.info("MainBackendTools: Main().InstallNewBootloader(): Installing ELILO...")
            #Unmount the UEFI Partition now, and update the mtab inside chroot (if using chroot).
            if CoreTools.Unmount(BootloaderInfo[OS]["BootDisk"]) != 0:
                logger.error("MainBackendTools: Main().InstallNewBootloader(): Failed to unmount the EFI partition! If installing ELILO fails this might be the reason. Continuing anyway...") #*** Installation won't work if unmounting failed! ***

            if UseChroot:
                CoreTools.UpdateChrootMtab(MountPoint=MountPoint)

            if OSInfo[OS]["PackageManager"] == "apt-get":
                Cmd = "sh -c 'DEBIAN_FRONTEND=noninteractive apt-get install -y elilo'"

        if UseChroot:
            Cmd = "chroot "+MountPoint+" "+Cmd

        Retval = CoreTools.StartProcess(Cmd)

        if Retval != 0:
            logger.error("MainBackendTools: Main().InstallNewBootloader(): Failed to uninstall old bootloader. Warn user...")
            DialogTools.ShowMsgDlg(Kind="error", Message="WxfixBoot failed to uninstall "+OS+"'s old bootloader! Continuing anyway...")

        #If there's a seperate /boot partition for this OS, make sure it's unmounted before removing the chroot.
        if OSInfo[OS]["BootPartition"] != "Unknown":
            if CoreTools.Unmount(MountPoint+"/boot") != 0:
                logger.error("MainBackendTools: Main().InstallNewBootloader(): Failed to unmount "+MountPoint+"/boot! This probably doesn't matter...") #*** What should we do here? ***

        if UseChroot:
            logger.debug("MainBackendTools: Main().InstallNewBootloader(): Removing chroot...")

            #Tear down chroot.
            if CoreTools.TearDownChroot(MountPoint=MountPoint) != 0:
                logger.error("MainBackendTools: Main().InstallNewBootloader(): Failed to remove chroot at "+MountPoint+"! Attempting to continue anyway...") #*** What should we do here? ***

        if UnmountAfter:
            if CoreTools.Unmount(MountPoint) != 0:
                logger.error("MainBackendTools: Main().InstallNewBootloader(): Failed to unmount "+MountPoint+"! Continuing anyway...")

        if Retval != 0:
            #Something went wrong! Log it and notify the user.
            BootloaderInstallSucceded = False
            logger.error("MainBackendTools: Main().InstallNewBootloader(): Failed to install "+BootloaderInfo[OS]["Settings"]["NewBootloader"]+" in "+OS+"! This may mean the system (or this OS) is now unbootable! We'll continue anyway. Warn the user.")
            DialogTools.ShowMsgDlg(Kind="error", Message="WxFixBoot failed to install "+BootloaderInfo[OS]["Settings"]["NewBootloader"]+" in "+OS+"! This may leave this OS, or your system, in an unbootable state. It is recommended to do a Bad Sector check, unplug any non-essential devices, and then try again.") #*** Maybe ask to try again right now ***

        wx.CallAfter(ParentWindow.UpdateOutputBox, "\n###Finished installing "+BootloaderInfo[OS]["Settings"]["NewBootloader"]+" in "+OS+"...###\n")

        #Log and notify the user that we're finished installing the bootloader.
        logger.info("MainBackendTools: Main().InstallNewBootloader(): Finished installing "+BootloaderInfo[OS]["Settings"]["NewBootloader"]+"...")
        wx.CallAfter(ParentWindow.UpdateCurrentOpText, Message="Finished installing "+BootloaderInfo[OS]["Settings"]["NewBootloader"]+"...")
        wx.CallAfter(ParentWindow.UpdateCurrentProgress, 75)
        return BootloaderInstallSucceded

    def SetNewBootloaderConfig(self, OS): #*** Use UseChroot in child functions? *** *** Only set e.g. Timeout and Kernel Options if they are being changed ***
        """Manage setting new bootloader config."""
        logger.info("MainBackendTools: Main().SetNewBootloaderConfig(): Setting "+BootloaderInfo[OS]["Settings"]["NewBootloader"]+"'s config for "+OS+"...")
        wx.CallAfter(ParentWindow.UpdateCurrentOpText, Message="Setting "+BootloaderInfo[OS]["Settings"]["NewBootloader"]+" config...")
        wx.CallAfter(ParentWindow.UpdateCurrentProgress, 79)
        wx.CallAfter(ParentWindow.UpdateOutputBox, "\n###Setting "+BootloaderInfo[OS]["Settings"]["NewBootloader"]+"'s config for "+OS+"...###\n")

        #If this is the current OS, let the config functions know that we aren't using chroot.
        if OSInfo[OS]["IsCurrentOS"]:
            logger.debug("MainBackendTools: Main().SetNewBootloaderConfig(): We're modifying the current OS...")
            #If so, make sure this will work for this OS too, and avoid setting mountpoint, so the config instructions below look in the right place for the config files.
            UseChroot, UnmountAfter, MountPoint = (False, False, "")

        else:
            logger.debug("MainBackendTools: Main().SetNewBootloaderConfig(): We're modifying another OS...")
            UseChroot = True
            MountPoint = "/tmp/wxfixboot/mountpoints"+OSInfo[OS]["Partition"]

            #Check if the partition is mounted.
            UnmountAfter = not CoreTools.IsMounted(OSInfo[OS]["Partition"], MountPoint)

            if UnmountAfter:
                #Mount the partition.
                if CoreTools.MountPartition(Partition=OSInfo[OS]["Partition"], MountPoint=MountPoint) != 0:
                    #Ignore this partition.
                    logger.warning("MainBackendTools: Main().SetNewBootloaderConfig(): Failed to mount "+OSInfo[OS]["Partition"]+"! Ignoring this partition...")
                    return False #*** Not handled yet ***

            #Set up chroot.
            if CoreTools.SetUpChroot(MountPoint=MountPoint) != 0:
                logger.error("MainBackendTools: Main().SetNewBootloaderConfig(): Failed to set up chroot at "+MountPoint+"! Attempting to continue anyway...") #*** What should we do here? ***

            wx.CallAfter(ParentWindow.UpdateCurrentProgress, 81)

        #Look for the configuration file, based on which SetConfig() function we're about to run.
        if BootloaderInfo[OS]["Settings"]["NewBootloader"] == "GRUB2":
            #Check MountPoint/etc/default/grub exists. *** What do we do if it doesn't? Maybe have a template to put there ***
            if os.path.isfile(MountPoint+"/etc/default/grub"):
                #It does, we'll run the function to set the config now.
                logger.info("MainBackendTools: Main().SetNewBootloaderConfig(): Setting GRUB2-BIOS Configuration...")
                BootloaderConfigSettingTools.SetGRUB2Config(filetoopen=MountPoint+"/etc/default/grub", BootloaderTimeout=BootloaderInfo[OS]["Settings"]["NewTimeout"], KernelOptions=BootloaderInfo[OS]["Settings"]["NewKernelOptions"])

            #Now Install GRUB2 to the MBR. *** Is this necessary when updating it? ***
            logger.info("MainBackendTools: Main().SetNewBootloaderConfig(): Installing GRUB2 to "+DiskInfo[OSInfo[OS]["Partition"]]["HostDevice"]+"...")
            BootloaderConfigSettingTools.InstallGRUB2ToMBR(PackageManager=OSInfo[OS]["PackageManager"], MountPoint=MountPoint, Device=DiskInfo[OSInfo[OS]["Partition"]]["HostDevice"])

            #Update GRUB.
            logger.info("MainBackendTools: Main().SetNewBootloaderConfig(): Updating GRUB2 Configuration...")
            BootloaderConfigSettingTools.UpdateGRUB2(PackageManager=OSInfo[OS]["PackageManager"], MountPoint=MountPoint)

            #Set the default OS.
            logger.info("MainBackendTools: Main().SetNewBootloaderConfig(): Setting GRUB2 Default OS...")
            BootloaderConfigSettingTools.SetGRUB2DefaultOS(OS=OS, MountPoint=MountPoint)

        elif BootloaderInfo[OS]["Settings"]["NewBootloader"] == "GRUB-UEFI":
            #Check MountPoint/etc/default/grub exists. *** What do we do if it doesn't? Maybe have a template to put there ***
            if os.path.isfile(MountPoint+"/etc/default/grub"):
                #It does, we'll run the function to set the config now.
                logger.info("MainBackendTools: Main().SetNewBootloaderConfig(): Setting GRUB2-UEFI Configuration...")
                BootloaderConfigSettingTools.SetGRUB2Config(filetoopen=MountPoint+"/etc/default/grub", BootloaderTimeout=BootloaderInfo[OS]["Settings"]["NewTimeout"], KernelOptions=BootloaderInfo[OS]["Settings"]["NewKernelOptions"])

            #Mount the UEFI partition at MountPoint/boot/efi.
            if CoreTools.MountPartition(Partition=BootloaderInfo[OS]["BootDisk"], MountPoint=MountPoint+"/boot/efi") != 0:
                logger.error("MainBackendTools: Main().SetNewBootloaderConfig(): Couldn't mount EFI partition "+BootloaderInfo[OS]["BootDisk"]+" to install bootloader! *** TODO: Cancel bootloader operations *** Continuing for now...")

            #Now Install GRUB-UEFI to the UEFI Partition. *** Is this necessary when updating it? ***
            logger.info("MainBackendTools: Main().SetNewBootloaderConfig(): Installing GRUB2 to "+BootloaderInfo[OS]["BootDisk"]+"...")
            BootloaderConfigSettingTools.InstallGRUBUEFIToPartition(PackageManager=OSInfo[OS]["PackageManager"], MountPoint=MountPoint, UEFISystemPartitionMountPoint=MountPoint+"/boot/efi", Arch=OSInfo[OS]["Arch"])

            #Update GRUB.
            logger.info("MainBackendTools: Main().SetNewBootloaderConfig(): Updating GRUB2 Configuration...")
            BootloaderConfigSettingTools.UpdateGRUB2(PackageManager=OSInfo[OS]["PackageManager"], MountPoint=MountPoint)

            #Make an entry in fstab for the UEFI Partition, if needed.
            HelperBackendTools.WriteFSTABEntryForUEFIPartition(MountPoint=MountPoint)

            #Copy and backup EFI files where needed.
            HelperBackendTools.BackupUEFIFiles(MountPoint=MountPoint)
            HelperBackendTools.CopyUEFIFiles(OS=OS, MountPoint=MountPoint)

            #Set the default OS.
            logger.info("MainBackendTools: Main().SetNewBootloaderConfig(): Setting GRUB2 Default OS...")
            BootloaderConfigSettingTools.SetGRUB2DefaultOS(OS=OS, MountPoint=MountPoint)

            #Unmount the EFI partition.
            if CoreTools.Unmount(BootloaderInfo[OS]["BootDisk"]) != 0: #*** Warn user? ***
                logger.error("MainBackendTools: Main().SetNewBootloaderConfig(): Couldn't unmount EFI partition! This probably won't matter, so we'll continue anyway...")

        elif BootloaderInfo[OS]["Settings"]["NewBootloader"] == "LILO":
            #Make LILO's config file.
            logger.info("MainBackendTools: Main().SetNewBootloaderConfig(): Making LILO's configuration file...")
            Cmd = "liloconfig -f"

            if UseChroot:
                Cmd = "chroot "+MountPoint+" "+Cmd

            if CoreTools.StartProcess(Cmd, ShowOutput=False) != 0:
                logger.error("MainBackendTools: Main().SetNewBootloaderConfig(): '"+Cmd+"' didn't run successfully! Attempting to continue anyway...") #*** What do we do here? ***

            #Check the config file exists for lilo. *** What do we do if it doesn't? Have a template one to put there? ***
            if os.path.isfile(MountPoint+"/etc/lilo.conf"):
                #It does, we'll run the function to set the config now.
                logger.info("MainBackendTools: Main().SetNewBootloaderConfig(): Setting LILO Configuration...")
                BootloaderConfigSettingTools.SetLILOConfig(filetoopen=MountPoint+"/etc/lilo.conf", PackageManager=OSInfo[OS]["PackageManager"], MountPoint=MountPoint, BootloaderTimeout=BootloaderInfo[OS]["Settings"]["NewTimeout"], BootDevice=DiskInfo[OSInfo[OS]["Partition"]]["HostDevice"])
    
                #Also, set the OS entries.
                logger.info("MainBackendTools: Main().SetNewBootloaderConfig(): Creating LILO OS Entries...")
                BootloaderConfigSettingTools.MakeLILOOSEntries(OS=OS, filetoopen=MountPoint+"/etc/lilo.conf", PackageManager=OSInfo[OS]["PackageManager"], MountPoint=MountPoint, KernelOptions=BootloaderInfo[OS]["Settings"]["NewKernelOptions"])

            #Now Install LILO to the MBR.
            logger.info("MainBackendTools: Main().SetNewBootloaderConfig(): Installing LILO to the MBR...")
            BootloaderConfigSettingTools.InstallLILOToMBR(PackageManager=OSInfo[OS]["PackageManager"], MountPoint=MountPoint)

        elif BootloaderInfo[OS]["Settings"]["NewBootloader"] == "ELILO":
            #Unmount the UEFI Partition now, and update mtab in the chroot.
            if CoreTools.Unmount(BootloaderInfo[OS]["BootDisk"]) != 0:
                logger.error("MainBackendTools: Main().SetNewBootloaderConfig(): Failed to unmount EFI partition "+BootloaderInfo[OS]["BootDisk"]+"! Continuing anyway...") #*** Installation will fail if this happens! ***

            #Update chroot mtab if needed.
            if UseChroot:
                CoreTools.UpdateChrootMtab(MountPoint=MountPoint)

            #Make ELILO's config file.
            logger.info("MainBackendTools: Main().SetNewBootloaderConfig(): Making ELILO's configuration file...")

            Cmd = "elilo -b "+BootloaderInfo[OS]["BootDisk"]+" --autoconf"

            if UseChroot:
                Cmd = "chroot "+MountPoint+" "+Cmd

            if CoreTools.StartProcess(Cmd, ShowOutput=False) != 0:
                logger.error("MainBackendTools: Main().SetNewBootloaderConfig(): '"+Cmd+"' didn't run successfully! Attempting to continue anyway...")

            #Check elilo's config file exists. *** What do we do if it doesn't? Have a template to put there? ***
            if os.path.isfile(MountPoint+"/etc/elilo.conf"):
                #It does, we'll run the function to set the config now.
                logger.info("MainBackendTools: Main().SetNewBootloaderConfig(): Setting ELILO Configuration...")
                BootloaderConfigSettingTools.SetELILOConfig(filetoopen=MountPoint+"/etc/elilo.conf", PackageManager=OSInfo[OS]["PackageManager"], MountPoint=MountPoint, BootloaderTimeout=BootloaderInfo[OS]["Settings"]["NewTimeout"])

                #Also, set the OS entries.
                logger.info("MainBackendTools: Main().SetNewBootloaderConfig(): Creating ELILO OS Entries...")
                BootloaderConfigSettingTools.MakeLILOOSEntries(filetoopen=MountPoint+"/etc/elilo.conf", PackageManager=OSInfo[OS]["PackageManager"], MountPoint=MountPoint, KernelOptions=BootloaderInfo[OS]["Settings"]["NewKernelOptions"])

            #Now Install ELILO to the UEFI Partition.
            logger.info("MainBackendTools: Main().SetNewBootloaderConfig(): Installing ELILO to "+BootloaderInfo[OS]["BootDisk"]+"...")
            BootloaderConfigSettingTools.InstallELILOToPartition(PackageManager=OSInfo[OS]["PackageManager"], MountPoint=MountPoint)

            #Mount the UEFI partition at MountPoint/boot/efi.
            if CoreTools.MountPartition(Partition=BootloaderInfo[OS]["BootDisk"], MountPoint=MountPoint+"/boot/efi") != 0:
                logger.error("MainBackendTools: Main().SetNewBootloaderConfig(): Failed to mount EFI partition "+BootloaderInfo[OS]["BootDisk"]+"! Continuing anyway...")

            #Copy and backup UEFI files where needed.
            HelperBackendTools.BackupUEFIFiles(MountPoint=MountPoint)
            HelperBackendTools.CopyUEFIFiles(OS=OS, MountPoint=MountPoint)

            #Unmount the EFI partition.
            if CoreTools.Unmount(BootloaderInfo[OS]["BootDisk"]) != 0: #*** Warn user? ***
                logger.error("MainBackendTools: Main().SetNewBootloaderConfig(): Couldn't unmount EFI partition! This probably won't matter, so we'll continue anyway...")

        #Tear down chroot if needed.
        if UseChroot:
            if CoreTools.TearDownChroot(MountPoint=MountPoint) != 0:
                logger.error("MainBackendTools: Main().SetNewBootloaderConfig(): Failed to remove chroot at "+MountPoint+"! Attempting to continue anyway...") #*** What should we do here? ***

        #Unmount the partition if needed.
        if UnmountAfter:
            if CoreTools.Unmount(MountPoint) != 0:
                logger.error("MainBackendTools: Main().SetNewBootloaderConfig(): Failed to unmount "+MountPoint+"! Continuing anyway...")

        logger.debug("MainBackendTools: Main().SetNewBootloaderConfig(): Finished setting "+BootloaderInfo[OS]["Settings"]["NewBootloader"]+"'s config for "+OS+"...")
        wx.CallAfter(ParentWindow.UpdateOutputBox, "\n###Finished setting "+BootloaderInfo[OS]["Settings"]["NewBootloader"]+"'s config for "+OS+"...###\n")
        wx.CallAfter(ParentWindow.UpdateCurrentOpText, Message="Finished setting "+BootloaderInfo[OS]["Settings"]["NewBootloader"]+"'s config!")
        wx.CallAfter(ParentWindow.UpdateCurrentProgress, 100)

#End main Class.
