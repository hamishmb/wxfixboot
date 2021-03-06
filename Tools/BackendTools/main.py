#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Main Backend Tools in the BackendTools Package for WxFixBoot Version 2.0.3
# This file is part of WxFixBoot.
# Copyright (C) 2013-2018 Hamish McIntyre-Bhatty
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
    def ManageBootloader(self, OS):
        """Manage the installation and removal of each bootloader."""
        #Test the internet connection.
        wx.CallAfter(ParentWindow.UpdateCurrentOpText, Message="Checking the Internet Connection...")
        wx.CallAfter(ParentWindow.UpdateOutputBox, "\n###Checking the Internet Connection...###\n")

        EssentialBackendTools.CheckInternetConnection()

        wx.CallAfter(ParentWindow.UpdateCurrentOpText, Message="Finished checking the Internet Connection...")
        wx.CallAfter(ParentWindow.UpdateOutputBox, "\n###Finished checking the Internet Connection...###\n")

        #Don't do anything if bootloader operations have been disabled.
        if SystemInfo["DisableBootloaderOperations"]:
            logger.info("MainBackendTools(): Main().ManageBootloader(): Bootloader operations have been disabled, skipping this operation...")
            wx.CallAfter(ParentWindow.UpdateCurrentProgress, 100)
            wx.CallAfter(ParentWindow.UpdateOutputBox, "\n###Skipped bootloader operations for "+OS+"...###\n")
            return True

        if BootloaderInfo[OS]["Settings"]["Reinstall"] or BootloaderInfo[OS]["Settings"]["Update"]:
            BootloaderInfo[OS]["Settings"]["NewBootloader"] = BootloaderInfo[OS]["Bootloader"]

        #Create a list of functions to call.
        FunctionList = [self.SetNewBootloaderConfig]
        
        if BootloaderInfo[OS]["Settings"]["Reinstall"] or BootloaderInfo[OS]["Settings"]["InstallNewBootloader"]:
            #Add more stuff to the list.
            FunctionList = [self.RemoveOldBootloader, self.InstallNewBootloader, self.SetNewBootloaderConfig]

        #Safegaurd operations using a loop.
        for Function in FunctionList:
            logger.info("MainBackendTools(): Main().ManageBootloader(): Calling "+unicode(Function)+"...")

            Success = False

            #Allow the user to keep trying if stuff goes wrong.
            while Success == False:
                #Create some text.
                if Function == self.RemoveOldBootloader:
                    Operation = "remove"

                elif Function == self.InstallNewBootloader:
                    Operation = "install"

                else:
                    Operation = "configure"

                Success = Function(OS)

                #Warn user if an error occured.
                if Success == False:
                    logger.error("MainBackendTools(): Main().ManageBootloader(): Failed to "+Operation+" "+OS+"'s old bootloader! Asking user whether to try again or skip this OS...")

                    #Drop a leading 'e' for correct English.
                    if Operation[-1] == "e":
                        Operation = Operation[0:-1]

                    Result = DialogTools.ShowYesNoDlg(Message="An error occured while "+Operation+"ing "+OS+"'s bootloader! This operating system may currently be in an unbootable state. What do you want to do? Click Yes to try again, and click No to cancel bootloader operations for this OS.", Title="WxFixBoot - Error "+Operation+"ing Bootloader!", Buttons=("Try Again", "Skip Bootloader Operations For This OS"))

                    if Result:
                        logger.info("MainBackendTools(): Main().ManageBootloader(): Trying again and checking internet connection again...")
                        EssentialBackendTools.CheckInternetConnection()

                        #Don't do anything if bootloader operations have been disabled.
                        if SystemInfo["DisableBootloaderOperations"]:
                            logger.info("MainBackendTools(): Main().ManageBootloader(): Bootloader operations have been disabled, skipping this operation...")
                            wx.CallAfter(ParentWindow.UpdateCurrentProgress, 100)
                            wx.CallAfter(ParentWindow.UpdateOutputBox, "\n###Skipped bootloader operations for "+OS+"...###\n")
                            return True 

                    else:
                        logger.error("MainBackendTools(): Main().ManageBootloader(): Skipping the rest of the bootloader operations for "+OS+"! Other operations will continue as normal. Returning False...")
                        wx.CallAfter(ParentWindow.UpdateCurrentProgress, 100)
                        return False

        logger.info("MainBackendTools(): Main().ManageBootloader(): Done!")

    def RemoveOldBootloader(self, OS):
        """Remove the currently installed bootloader."""
        logger.info("MainBackendTools: Main().RemoveOldBootloader(): Removing "+BootloaderInfo[OS]["Bootloader"]+" from "+OS+"...")
        wx.CallAfter(ParentWindow.UpdateCurrentProgress, 27)
        wx.CallAfter(ParentWindow.UpdateCurrentOpText, Message="Removing "+BootloaderInfo[OS]["Bootloader"]+" from "+OS+"......")
        wx.CallAfter(ParentWindow.UpdateOutputBox, "\n###Removing "+BootloaderInfo[OS]["Bootloader"]+" from "+OS+"...###\n")
            
        #If this is the current OS, let the remover function know that we aren't using chroot.
        if OSInfo[OS]["IsCurrentOS"]:
            logger.debug("MainBackendTools: Main().RemoveOldBootloader(): Modifying current OS so not using chroot...")
            UseChroot, UnmountAfter, MountPoint = (False, False, "")

        else:
            logger.debug("MainBackendTools: Main().RemoveOldBootloader(): Using chroot to modify another OS...")
            UseChroot = True
            MountPoint = "/tmp/wxfixboot/mountpoints"+OSInfo[OS]["Partition"]

            #Check if the partition is mounted.
            UnmountAfter = not CoreTools.IsMounted(OSInfo[OS]["Partition"], MountPoint)

            if UnmountAfter:
                #Mount the partition using the global mount function.
                if CoreTools.MountPartition(Partition=OSInfo[OS]["Partition"], MountPoint=MountPoint) != 0:
                    logger.error("MainBackendTools: Main().RemoveOldBootloader(): Failed to mount "+OSInfo[OS]["Partition"]+"! Warning the user and giving up...")
                    DialogTools.ShowMsgDlg(Kind="error", Message="WxFixBoot failed to mount the partition containing "+OS+"! Giving up. You will be prompted to try again if you wish.")
                    return False

            #Set up chroot.
            if CoreTools.SetUpChroot(MountPoint) != 0:
                logger.error("MainBackendTools: Main().RemoveOldBootloader(): Failed to set up chroot at "+MountPoint+"! Giving up...")
                DialogTools.ShowMsgDlg(Kind="error", Message="WxFixBoot failed to set up a chroot for "+OS+"! Giving up. You will be prompted to try again if you wish.")
                return False

        #Mount a /boot partition if it exists.
        if OSInfo[OS]["BootPartition"] != "Unknown":
            if CoreTools.MountPartition(OSInfo[OS]["BootPartition"], MountPoint+"/boot") != 0:
                logger.error("MainBackendTools: Main().RemoveOldBootloader(): Failed to mount "+OS+"'s /boot partition! Skipping bootloader removal for this OS.")
                DialogTools.ShowMsgDlg(Kind="error", Message="WxFixBoot failed to mount the partition containing "+OS+"'s /boot partition! Giving up. You will be prompted to try again if you wish.")

                if not OSInfo[OS]["IsCurrentOS"]:
                    CoreTools.TearDownChroot(MountPoint)
                    CoreTools.Unmount(MountPoint)

                return False

        #Mount the UEFI partition at MountPoint/boot/efi, if it exists.
        if OSInfo[OS]["EFIPartition"] != "Unknown":
            if CoreTools.MountPartition(Partition=OSInfo[OS]["EFIPartition"], MountPoint=MountPoint+"/boot/efi") != 0:
                logger.error("MainBackendTools: Main().RemoveOldBootloader(): Failed to mount "+OSInfo[OS]["EFIPartition"]+"! to "+MountPoint+"/boot/efi! Aborting bootloader installation and warning user...")
                DialogTools.ShowMsgDlg(Kind="error", Message="WxfixBoot failed to mount the partition containing "+OS+"'s EFI partition! Giving up. You will be prompted to try again if you wish.")
                return False

        #Wait until no other application is using APT/YUM.
        #Let user know what's happening.
        wx.CallAfter(ParentWindow.UpdateCurrentProgress, 27)
        wx.CallAfter(ParentWindow.UpdateCurrentOpText, Message="Waiting until "+OS+"'s package manager is free.\nClose any open applications if this message persists...")
        wx.CallAfter(ParentWindow.UpdateOutputBox, "\n###Waiting until "+OS+"'s package manager is free...###\n")

        logger.debug("MainBackendTools: Main().RemoveOldBootloader(): Waiting until "+OS+"'s package manager is free...")
        HelperBackendTools.WaitUntilPackageManagerNotInUse(MountPoint=MountPoint, PackageManager=OSInfo[OS]["PackageManager"])

        wx.CallAfter(ParentWindow.UpdateCurrentProgress, 27)
        wx.CallAfter(ParentWindow.UpdateCurrentOpText, Message="Removing "+BootloaderInfo[OS]["Bootloader"]+" from "+OS+"...")
        wx.CallAfter(ParentWindow.UpdateOutputBox, "\n###Removing "+BootloaderInfo[OS]["Bootloader"]+" from "+OS+"...###\n")

        #Remove the bootloader.
        if BootloaderInfo[OS]["Bootloader"] == "GRUB2":
            logger.info("MainBackendTools: Main().RemoveOldBootloader(): Removing GRUB2...")

            if OSInfo[OS]["PackageManager"] == "apt-get":
                Cmd = "sh -c 'DEBIAN_FRONTEND=noninteractive apt-get purge -y grub-pc grub-pc-bin grub-common'"

            elif OSInfo[OS]["PackageManager"] == "yum":
                Cmd = "yum -y remove grub2"

        elif BootloaderInfo[OS]["Bootloader"] == "LILO":
            logger.info("MainBackendTools: Main().RemoveOldBootloader(): Removing LILO...")

            if OSInfo[OS]["PackageManager"] == "apt-get":
                Cmd = "sh -c 'DEBIAN_FRONTEND=noninteractive apt-get purge -y lilo'"

            elif OSInfo[OS]["PackageManager"] == "yum":
                Cmd = "echo 'ERROR: LILO not available on Fedora or derivatives. Continuing anyway...'"

        elif BootloaderInfo[OS]["Bootloader"] == "GRUB-UEFI":
            logger.info("MainBackendTools: Main().RemoveOldBootloader(): Removing GRUB-UEFI...")

            if OSInfo[OS]["PackageManager"] == "apt-get":
                Cmd = "sh -c 'DEBIAN_FRONTEND=noninteractive apt-get purge -y grub-efi grub-efi-amd64 grub-efi-amd64-bin grub-efi-ia32 grub-efi-ia32-bin grub-common grub2-common'"

            elif OSInfo[OS]["PackageManager"] == "yum":
                Cmd = "yum -y remove grub2-efi shim-x64"

        elif BootloaderInfo[OS]["Bootloader"] == "ELILO":
            logger.info("MainBackendTools: Main().RemoveOldBootloader(): Removing ELILO...")

            if OSInfo[OS]["PackageManager"] == "apt-get":
                Cmd = "sh -c 'DEBIAN_FRONTEND=noninteractive apt-get purge -y elilo'"

            elif OSInfo[OS]["PackageManager"] == "yum":
                Cmd = "echo 'ERROR: ELILO not available on Fedora or derivatives. Continuing anyway...'"

        else:
            #Bootloader is unknown, or grub-legacy. Just output a warning message.
            logger.warning("MainBackendTools: Main().RemoveOldBootloader(): Cannot remove GRUB-LEGACY / unknown bootloader! Continuing anyway...")

            Cmd = "echo 'WARNING: Cannot remove GRUB-LEGACY, or bootloader is unknown. Continuing anyway...'"

        if UseChroot:
            Cmd = "chroot "+MountPoint+" "+Cmd

        Retval = CoreTools.StartProcess(Cmd)

        if Retval != 0:
            logger.error("MainBackendTools: Main().RemoveOldBootloader(): Failed to remove "+BootloaderInfo[OS]["Bootloader"]+" from "+OS+"! Warning user...")
            DialogTools.ShowMsgDlg(Kind="error", Message="WxFixBoot failed to remove "+BootloaderInfo[OS]["Bootloader"]+" from "+OS+"!")
            return False

        #If there's a seperate EFI partition for this OS, make sure it's unmounted before removing the chroot.
        if OSInfo[OS]["EFIPartition"] != "Unknown":
            if CoreTools.Unmount(MountPoint+"/boot/efi") != 0:
                logger.error("MainBackendTools: Main().RemoveOldBootloader(): Failed to unmount "+MountPoint+"/boot/efi! This probably doesn't matter...")

        #Unmount a /boot partition if it exists.
        if OSInfo[OS]["BootPartition"] != "Unknown":
            if CoreTools.Unmount(MountPoint+"/boot") != 0:
                logger.error("MainBackendTools: Main().RemoveOldBootloader(): Failed to unmount "+OS+"'s /boot partition! Continuing anyway...")

        #Tear down chroot if needed.
        if UseChroot:
            if CoreTools.TearDownChroot(MountPoint=MountPoint) != 0:
                logger.error("MainBackendTools: Main().RemoveOldBootloader(): Failed to remove chroot at "+MountPoint+"! Attempting to continue anyway...")

        #Unmount partition if needed.
        if UnmountAfter:
            if CoreTools.Unmount(MountPoint) != 0:
                logger.error("MainBackendTools: Main().RemoveOldBootloader(): Couldn't unmount "+MountPoint+"! Continuing anyway...")

        wx.CallAfter(ParentWindow.UpdateOutputBox, "\n###Finished removing "+BootloaderInfo[OS]["Bootloader"]+" from "+OS+"...###\n")

        if Retval != 0:
            #Something went wrong! Log it and notify the user.
            logger.error("MainBackendTools: Main().RemoveOldBootloader(): Failed to remove "+BootloaderInfo[OS]["Bootloader"]+" from "+OS+"! We'll continue anyway. Warn the user.")
            DialogTools.ShowMsgDlg(Kind="error", Message="WxFixBoot failed to remove "+BootloaderInfo[OS]["Bootloader"]+" from "+OS+"! This probably doesn't matter; when we install the new bootloader, it should take precedence over the old one anyway. Make sure you check that "+OS+" boots correctly after WxFixBoot finishes its operations. Reinstalling the bootloader again afterwards is recommended.")

        #Log and notify the user that we're finished removing bootloaders.
        logger.info("MainBackendTools: Main().RemoveOldBootloader(): Finished removing "+BootloaderInfo[OS]["Bootloader"]+"...")
        wx.CallAfter(ParentWindow.UpdateCurrentOpText, Message="Finished removing "+BootloaderInfo[OS]["Bootloader"]+" from "+OS+"......")
        wx.CallAfter(ParentWindow.UpdateCurrentProgress, 50)
        DialogTools.ShowMsgDlg(Kind="info", Message="Finished removing "+BootloaderInfo[OS]["Bootloader"]+"! WxFixBoot will now install "+BootloaderInfo[OS]["Settings"]["NewBootloader"]+" to "+OS+".")
        return True

    def InstallNewBootloader(self, OS):
        """Install a new bootloader."""
        logger.info("MainBackendTools: Main().InstallNewBootloader(): Preparing to install "+BootloaderInfo[OS]["Settings"]["NewBootloader"]+" in "+OS+"...")
        wx.CallAfter(ParentWindow.UpdateCurrentProgress, 52)  
        wx.CallAfter(ParentWindow.UpdateOutputBox, "\n###Preparing to install "+BootloaderInfo[OS]["Settings"]["NewBootloader"]+" in "+OS+"...###\n")
        wx.CallAfter(ParentWindow.UpdateCurrentOpText, Message="Preparing to install "+BootloaderInfo[OS]["Settings"]["NewBootloader"]+" in "+OS+"...")

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
                    DialogTools.ShowMsgDlg(Kind="error", Message="WxFixBoot failed to mount the partition containing "+OS+"! Bootloader installation cannot continue! This may leave your system, or this OS, in an unbootable state. Please close any open programs, then try again when prompted.")
                    return False

            #Set up chroot.
            if CoreTools.SetUpChroot(MountPoint=MountPoint) != 0:
                logger.error("MainBackendTools: Main().InstallNewBootloader(): Failed to set up chroot at "+MountPoint+"! Warning user and giving up...")
                DialogTools.ShowMsgDlg(Kind="error", Message="WxFixBoot failed to set up a chroot for "+OS+"! Giving up. You will be prompted to try again if you wish.")
                return False

            #If there's a seperate /boot partition for this OS, make sure it's mounted.
            if OSInfo[OS]["BootPartition"] != "Unknown":
                if CoreTools.MountPartition(Partition=OSInfo[OS]["BootPartition"], MountPoint=MountPoint+"/boot") != 0:
                    logger.error("MainBackendTools: Main().RemoveOldBootloader(): Failed to mount "+OSInfo[OS]["BootPartition"]+"! Warn the user and skip this OS.") 
                    DialogTools.ShowMsgDlg(Kind="error", Message="WxFixBoot failed to mount the partition containing "+OS+"'s /boot partition! Giving up. You will be prompted to try again if you wish.")
                    return False

        #Update the package lists.
        if OSInfo[OS]["PackageManager"] == "apt-get":
            Cmd = "sh -c 'DEBIAN_FRONTEND=noninteractive apt-get update'"

        elif OSInfo[OS]["PackageManager"] == "yum":
            Cmd = "yum check-update"

        if UseChroot:
            Cmd = "chroot "+MountPoint+" "+Cmd

        if CoreTools.StartProcess(Cmd) not in (0,100):
            logger.error("MainBackendTools: Main().InstallNewBootloader(): Failed to Update the Package Information! Continuing anyway...")
            DialogTools.ShowMsgDlg(Kind="error", Message="WxfixBoot failed to update "+OS+"'s package information! Giving up. You will be prompted to try again if you wish.")
            return False

        wx.CallAfter(ParentWindow.UpdateCurrentOpText, Message="Installing "+BootloaderInfo[OS]["Settings"]["NewBootloader"]+" in "+OS+"...")
        wx.CallAfter(ParentWindow.UpdateCurrentProgress, 55)       
        wx.CallAfter(ParentWindow.UpdateOutputBox, "\n###Installing "+BootloaderInfo[OS]["Settings"]["NewBootloader"]+" in "+OS+"...###\n")

        #Install the bootloader.
        if BootloaderInfo[OS]["Settings"]["NewBootloader"] == "GRUB2":
            logger.info("MainBackendTools: Main().InstallNewBootloader(): Installing GRUB2...")

            if OSInfo[OS]["PackageManager"] == "apt-get":
                Cmd = "sh -c 'DEBIAN_FRONTEND=noninteractive apt-get install -y grub-pc os-prober'"

            elif OSInfo[OS]["PackageManager"] == "yum":
                Cmd = "yum -y install grub2"

        elif BootloaderInfo[OS]["Settings"]["NewBootloader"] == "LILO":
            logger.info("MainBackendTools: Main().InstallNewBootloader(): Installing LILO...")

            if OSInfo[OS]["PackageManager"] == "apt-get":
                Cmd = "sh -c 'DEBIAN_FRONTEND=noninteractive apt-get install -y lilo'"

            elif OSInfo[OS]["PackageManager"] == "yum":
                Cmd = "echo 'ERROR: LILO not available on Fedora or derivatives. Continuing anyway...'"

        elif BootloaderInfo[OS]["Settings"]["NewBootloader"] == "GRUB-UEFI":
            logger.info("MainBackendTools: Main().InstallNewBootloader(): Installing GRUB-UEFI...")

            #Mount the UEFI partition at MountPoint/boot/efi.
            if CoreTools.MountPartition(Partition=OSInfo[OS]["EFIPartition"], MountPoint=MountPoint+"/boot/efi") != 0:
                logger.error("MainBackendTools: Main().InstallNewBootloader(): Failed to mount "+OSInfo[OS]["EFIPartition"]+" to "+MountPoint+"/boot/efi! Aborting bootloader installation and warning user...")
                DialogTools.ShowMsgDlg(Kind="error", Message="WxfixBoot failed to mount the partition containing "+OS+"'s EFI partition! Giving up. You will be prompted to try again if you wish.")
                return False

            if OSInfo[OS]["PackageManager"] == "apt-get":
                Cmd = "sh -c 'DEBIAN_FRONTEND=noninteractive apt-get install -y grub-efi os-prober'"

            elif OSInfo[OS]["PackageManager"] == "yum":
                Cmd = "yum -y install grub2-efi-ia32 grub2-efi-x64 grub2-efi shim-x64 fwupd fwupdate-efi fwupdate-libs gnome-software PackageKit appstream-data comps-extras epiphany-runtime flatpak-libs fwupd-labels libsmbios ostree rpm-ostree-libs"

        elif BootloaderInfo[OS]["Settings"]["NewBootloader"] == "ELILO":
            logger.info("MainBackendTools: Main().InstallNewBootloader(): Installing ELILO...")

            #Unmount the UEFI Partition now, and update the mtab inside chroot (if using chroot).
            if CoreTools.Unmount(OSInfo[OS]["EFIPartition"]) != 0:
                logger.error("MainBackendTools: Main().InstallNewBootloader(): Failed to unmount the EFI partition! Giving up and warning user...")
                DialogTools.ShowMsgDlg(Message="Couldn't unmount "+OS+"'s EFI partition! Giving up. You will be prompted to try again if you wish.", Kind="error")
                return False

            if UseChroot:
                CoreTools.UpdateChrootMtab(MountPoint=MountPoint)

            if OSInfo[OS]["PackageManager"] == "apt-get":
                Cmd = "sh -c 'DEBIAN_FRONTEND=noninteractive apt-get install -y elilo'"

            elif OSInfo[OS]["PackageManager"] == "yum":
                Cmd = "echo 'ERROR: ELILO not available on Fedora or derivatives. Continuing anyway...'"

        if UseChroot:
            Cmd = "chroot "+MountPoint+" "+Cmd

        Retval = CoreTools.StartProcess(Cmd)

        if Retval != 0:
            logger.error("MainBackendTools: Main().InstallNewBootloader(): Failed to install new bootloader. Warn user...")
            DialogTools.ShowMsgDlg(Kind="error", Message="WxfixBoot failed to install "+OS+"'s new bootloader! Continuing anyway...")

        #If there's a seperate EFI partition for this OS, make sure it's unmounted before removing the chroot.
        if OSInfo[OS]["EFIPartition"] != "Unknown":
            if CoreTools.Unmount(MountPoint+"/boot/efi") != 0:
                logger.error("MainBackendTools: Main().InstallNewBootloader(): Failed to unmount "+MountPoint+"/boot/efi! This probably doesn't matter...")

        #If there's a seperate /boot partition for this OS, make sure it's unmounted before removing the chroot.
        if OSInfo[OS]["BootPartition"] != "Unknown":
            if CoreTools.Unmount(MountPoint+"/boot") != 0:
                logger.error("MainBackendTools: Main().InstallNewBootloader(): Failed to unmount "+MountPoint+"/boot! This probably doesn't matter...")

        if UseChroot:
            logger.debug("MainBackendTools: Main().InstallNewBootloader(): Removing chroot...")

            #Tear down chroot.
            if CoreTools.TearDownChroot(MountPoint=MountPoint) != 0:
                logger.error("MainBackendTools: Main().InstallNewBootloader(): Failed to remove chroot at "+MountPoint+"! Attempting to continue anyway...")

        if UnmountAfter:
            if CoreTools.Unmount(MountPoint) != 0:
                logger.error("MainBackendTools: Main().InstallNewBootloader(): Failed to unmount "+MountPoint+"! Continuing anyway...")

        if Retval != 0:
            #Something went wrong! Log it and notify the user.
            logger.error("MainBackendTools: Main().InstallNewBootloader(): Failed to install "+BootloaderInfo[OS]["Settings"]["NewBootloader"]+" in "+OS+"! This may mean the system (or this OS) is now unbootable! Warning the user and asking to try again.")
            DialogTools.ShowMsgDlg(Kind="error", Message="WxFixBoot failed to install "+BootloaderInfo[OS]["Settings"]["NewBootloader"]+" in "+OS+"! This may leave this OS, or your system, in an unbootable state. You will now be prompted to try again.")
            return False

        wx.CallAfter(ParentWindow.UpdateOutputBox, "\n###Finished installing "+BootloaderInfo[OS]["Settings"]["NewBootloader"]+" in "+OS+"...###\n")

        #Log and notify the user that we're finished installing the bootloader.
        logger.info("MainBackendTools: Main().InstallNewBootloader(): Finished installing "+BootloaderInfo[OS]["Settings"]["NewBootloader"]+"...")
        wx.CallAfter(ParentWindow.UpdateCurrentOpText, Message="Finish installing "+BootloaderInfo[OS]["Settings"]["NewBootloader"]+" in "+OS+"...")
        wx.CallAfter(ParentWindow.UpdateCurrentProgress, 75)
        return True

    def SetNewBootloaderConfig(self, OS):
        """Manage setting new bootloader config."""
        logger.info("MainBackendTools: Main().SetNewBootloaderConfig(): Setting "+BootloaderInfo[OS]["Settings"]["NewBootloader"]+"'s config for "+OS+"...")
        wx.CallAfter(ParentWindow.UpdateCurrentOpText, Message="Setting "+BootloaderInfo[OS]["Settings"]["NewBootloader"]+" config for "+OS+"...")
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
                    logger.warning("MainBackendTools: Main().SetNewBootloaderConfig(): Failed to mount "+OSInfo[OS]["Partition"]+"! Giving up...")
                    return False

            #Set up chroot.
            if CoreTools.SetUpChroot(MountPoint=MountPoint) != 0:
                logger.error("MainBackendTools: Main().SetNewBootloaderConfig(): Failed to set up chroot at "+MountPoint+"! Giving up...")
                DialogTools.ShowMsgDlg(Kind="error", Message="WxFixBoot failed to set up a chroot for "+OS+"! Giving up. You will be prompted to try again if you wish.")
                return False

            wx.CallAfter(ParentWindow.UpdateCurrentProgress, 81)

        #Mount a /boot partition if it exists.
        if OSInfo[OS]["BootPartition"] != "Unknown":
            if CoreTools.MountPartition(OSInfo[OS]["BootPartition"], MountPoint+"/boot") != 0:
                logger.error("MainBackendTools: Main().SetNewBootloaderConfig(): Failed to mount "+OS+"'s /boot partition! Skipping bootloader config setting for this OS.")

                if not OSInfo[OS]["IsCurrentOS"]:
                    CoreTools.TearDownChroot(MountPoint)
                    CoreTools.Unmount(MountPoint)

                return False

        #If there's a seperate EFI partition for this OS, make sure it's mounted.
        if OSInfo[OS]["EFIPartition"] != "Unknown":
            if CoreTools.MountPartition(Partition=OSInfo[OS]["EFIPartition"], MountPoint=MountPoint+"/boot/efi") != 0:
                logger.error("MainBackendTools: Main().RemoveOldBootloader(): Failed to mount "+OSInfo[OS]["EFIPartition"]+"! Warn the user and skip this OS.") 
                DialogTools.ShowMsgDlg(Kind="error", Message="WxFixBoot failed to mount the partition containing "+OS+"'s EFI partition! Giving up. You will be prompted to try again if you wish.")
                return False

        #On GRUB2, get the new menuentries so we can set the default OS.
        logger.info("MainBackendTools: Main().SetNewBootloaderConfig(): Reading GRUB2's menu entries to set default OS...")

        if BootloaderInfo[OS]["Settings"]["NewBootloader"] in ("GRUB2", "GRUB-UEFI"):
            #Update GRUB.
            logger.info("MainBackendTools: Main().SetNewBootloaderConfig(): Updating GRUB2 Configuration...")
            BootloaderConfigSettingTools.UpdateGRUB2(OS=OS, PackageManager=OSInfo[OS]["PackageManager"], UseChroot=UseChroot, MountPoint=MountPoint)

            BootloaderInfo[OS]["NewMenuEntries"] = BootloaderConfigObtainingTools.ParseGRUB2MenuData(MenuData="", MountPoint=MountPoint)[1]

        #Look for the configuration file, based on which SetConfig() function we're about to run.
        if BootloaderInfo[OS]["Settings"]["NewBootloader"] in ("GRUB2", "GRUB-UEFI"):
            #Check MountPoint/etc/default/grub exists.
            if os.path.isfile(MountPoint+"/etc/default/grub"):
                #It does, we'll run the function to set the config now.
                logger.info("MainBackendTools: Main().SetNewBootloaderConfig(): Setting GRUB2 Configuration...")
                BootloaderConfigSettingTools.SetGRUB2Config(OS=OS, filetoopen=MountPoint+"/etc/default/grub", BootloaderTimeout=BootloaderInfo[OS]["Settings"]["NewTimeout"], KernelOptions=BootloaderInfo[OS]["Settings"]["NewKernelOptions"])

            if BootloaderInfo[OS]["Settings"]["NewBootloader"] == "GRUB-UEFI":
                #Mount the UEFI partition at MountPoint/boot/efi.
                if CoreTools.MountPartition(Partition=OSInfo[OS]["EFIPartition"], MountPoint=MountPoint+"/boot/efi") != 0:
                    logger.error("MainBackendTools: Main().SetNewBootloaderConfig(): Couldn't mount EFI partition "+OSInfo[OS]["EFIPartition"]+" to install bootloader! Giving up and warning user...")
                    DialogTools.ShowMsgDlg(Kind="error", Message="WxFixBoot failed to mount "+OS+"'s EFI partition! You will now be promtped to give up or try again.")
                    return False

                #Now Install GRUB-UEFI to the UEFI Partition.
                logger.info("MainBackendTools: Main().SetNewBootloaderConfig(): Installing GRUB-UEFI to "+OSInfo[OS]["EFIPartition"]+"...")
                BootloaderConfigSettingTools.InstallGRUB2ToEFIPartition(PackageManager=OSInfo[OS]["PackageManager"], MountPoint=MountPoint, UseChroot=UseChroot, UEFISystemPartitionMountPoint="/boot/efi", Arch=OSInfo[OS]["Arch"])

            else:
                #Now Install GRUB2 to the MBR.
                logger.info("MainBackendTools: Main().SetNewBootloaderConfig(): Installing GRUB2 to "+DiskInfo[OSInfo[OS]["Partition"]]["HostDevice"]+"...")
                BootloaderConfigSettingTools.InstallGRUB2ToMBR(PackageManager=OSInfo[OS]["PackageManager"], UseChroot=UseChroot, MountPoint=MountPoint, Device=DiskInfo[OSInfo[OS]["Partition"]]["HostDevice"])

            #Update GRUB.
            logger.info("MainBackendTools: Main().SetNewBootloaderConfig(): Updating GRUB2 Configuration...")
            BootloaderConfigSettingTools.UpdateGRUB2(OS=OS, PackageManager=OSInfo[OS]["PackageManager"], UseChroot=UseChroot, MountPoint=MountPoint)

            if BootloaderInfo[OS]["Settings"]["NewBootloader"] == "GRUB-UEFI":
                #Make an entry in fstab for the UEFI Partition, if needed.
                HelperBackendTools.WriteFSTABEntryForUEFIPartition(OS=OS, MountPoint=MountPoint)

                #Copy and backup EFI files where needed.
                HelperBackendTools.BackupUEFIFiles(MountPoint=MountPoint)
                HelperBackendTools.ManageUEFIFiles(OS=OS, MountPoint=MountPoint)

            if BootloaderInfo[OS]["Settings"]["NewBootloader"] == "GRUB-UEFI" and OSInfo[OS]["PackageManager"] == "yum":
                #If we're switching to GRUB-UEFI from BIOS it can mess up GRUB2 and change the boot commands to linux and initrd instead of linuxefi and initrdefi, preventing boot.
                #Fix this. The next time GRUB is updated from within the OS it will fix itself.
                logger.info("MainBackendTools: Main().SetNewBootloaderConfig(): Fixing Fedora's GRUB2-UEFI config (when booted with BIOS, it can go wrong)...")
                logger.info("MainBackendTools: Main().SetNewBootloaderConfig(): Finding and opening GRUB config file...")

                #Find grub.cfg. (Ubuntu).
                if os.path.isdir(MountPoint+"/boot/grub"):
                    GRUBDir = MountPoint+"/boot/grub"

                #(Fedora, EFI)
                elif os.path.isdir(MountPoint+"/boot/efi/EFI/fedora"):
                    GRUBDir = MountPoint+"/boot/efi/EFI/fedora"

                #Correct the commands if needed.
                ConfigFile = open(GRUBDir+"/grub.cfg", "r")
                Config = ConfigFile.readlines()
                ConfigFile.close()

                NewConfig = []

                for Line in Config:
                    if "linux16" in Line and "/vmlinu" in Line:
                        NewConfig.append(Line.replace("linux16", "linuxefi"))

                    elif "linux" in Line and "linuxefi" not in Line and "/vmlinu" in Line:
                        NewConfig.append(Line.replace("linux", "linuxefi"))

                    elif "initrd16" in Line and ("/initrd" in Line or "/initramfs" in Line):
                        NewConfig.append(Line.replace("initrd16", "initrdefi"))

                    elif "initrd" in Line and "initrdefi" not in Line and ("/initrd" in Line or "/initramfs" in Line):
                        NewConfig.append(Line.replace("initrd", "initrdefi"))

                    else:
                        NewConfig.append(Line)

                #Write the fixed config.
                ConfigFile = open(GRUBDir+"/grub.cfg", "w")
                ConfigFile.write(''.join(NewConfig))
                ConfigFile.close()

                #Unmount the EFI partition.
                if CoreTools.Unmount(OSInfo[OS]["EFIPartition"]) != 0:
                    logger.error("MainBackendTools: Main().SetNewBootloaderConfig(): Couldn't unmount EFI partition! This probably won't matter, so we'll continue anyway...")

                logger.info("MainBackendTools: Main().SetNewBootloaderConfig(): Done!")

            elif BootloaderInfo[OS]["Settings"]["NewBootloader"] == "GRUB2" and OSInfo[OS]["PackageManager"] == "yum":
                #If we're switching to GRUB2 from UEFI it can mess up GRUB2 and change the boot commands to linuxefi and initrdefi instead of linux and initrd, preventing boot.
                #Fix this. The next time GRUB is updated from within the OS it will fix itself.
                logger.info("MainBackendTools: Main().SetNewBootloaderConfig(): Fixing Fedora's GRUB2-BIOS config (when booted with EFI, it can go wrong)...")
                logger.info("MainBackendTools: Main().SetNewBootloaderConfig(): Finding and opening GRUB config file...")

                #Find grub.cfg. (Ubuntu).
                if os.path.isdir(MountPoint+"/boot/grub"):
                    GRUBDir = MountPoint+"/boot/grub"

                #(Fedora, BIOS)
                elif os.path.isdir(MountPoint+"/boot/grub2"):
                    GRUBDir = MountPoint+"/boot/grub2"

                #Correct the commands if needed.
                ConfigFile = open(GRUBDir+"/grub.cfg", "r")
                Config = ConfigFile.readlines()
                ConfigFile.close()

                NewConfig = []

                for Line in Config:
                    NewConfig.append(Line.replace("linuxefi", "linux").replace("initrdefi", "initrd"))

                #Write the fixed config.
                ConfigFile = open(GRUBDir+"/grub.cfg", "w")
                ConfigFile.write(''.join(NewConfig))
                ConfigFile.close()

                logger.info("MainBackendTools: Main().SetNewBootloaderConfig(): Done!")
                
        elif BootloaderInfo[OS]["Settings"]["NewBootloader"] == "LILO":
            #Make LILO's config file.
            logger.info("MainBackendTools: Main().SetNewBootloaderConfig(): Making LILO's configuration file...")
            Cmd = "liloconfig -f"

            if UseChroot:
                Cmd = "chroot "+MountPoint+" "+Cmd

            if CoreTools.StartProcess(Cmd, ShowOutput=False) != 0:
                logger.error("MainBackendTools: Main().SetNewBootloaderConfig(): '"+Cmd+"' didn't run successfully! Attempting to continue anyway...")

            #Check the config file exists for lilo.
            if os.path.isfile(MountPoint+"/etc/lilo.conf"):
                #It does, we'll run the function to set the config now.
                logger.info("MainBackendTools: Main().SetNewBootloaderConfig(): Setting LILO Configuration...")
                BootloaderConfigSettingTools.SetLILOConfig(OS=OS, filetoopen=MountPoint+"/etc/lilo.conf")
    
                #Also, set the OS entries.
                logger.info("MainBackendTools: Main().SetNewBootloaderConfig(): Creating LILO OS Entries...")
                BootloaderConfigSettingTools.MakeLILOOSEntries(OS=OS, filetoopen=MountPoint+"/etc/lilo.conf", MountPoint=MountPoint, KernelOptions=BootloaderInfo[OS]["Settings"]["NewKernelOptions"])

            #Now Install LILO to the MBR.
            logger.info("MainBackendTools: Main().SetNewBootloaderConfig(): Installing LILO to the MBR...")
            BootloaderConfigSettingTools.InstallLILOToMBR(PackageManager=OSInfo[OS]["PackageManager"], UseChroot=UseChroot, MountPoint=MountPoint)

        elif BootloaderInfo[OS]["Settings"]["NewBootloader"] == "ELILO":
            #Unmount the UEFI Partition now, and update mtab in the chroot.
            #Pause for 0.5 secs.
            time.sleep(0.5)

            if CoreTools.Unmount(OSInfo[OS]["EFIPartition"]) != 0:
                logger.error("MainBackendTools: Main().SetNewBootloaderConfig(): Failed to unmount "+OS+"'s EFI partition! Waning user and prompting to try again...")
                DialogTools.ShowMsgDlg(Message="Couldn't unmount "+OS+"'s EFI partition! Giving up. You will be prompted to try again if you wish.", Kind="error")
                return False

            #Update chroot mtab if needed.
            if UseChroot:
                CoreTools.UpdateChrootMtab(MountPoint=MountPoint)

            #Make ELILO's config file.
            logger.info("MainBackendTools: Main().SetNewBootloaderConfig(): Making ELILO's configuration file...")

            Cmd = "elilo -b "+OSInfo[OS]["EFIPartition"]+" --autoconf"

            if UseChroot:
                Cmd = "chroot "+MountPoint+" "+Cmd

            if CoreTools.StartProcess(Cmd, ShowOutput=False) != 0:
                logger.error("MainBackendTools: Main().SetNewBootloaderConfig(): '"+Cmd+"' didn't run successfully! Attempting to continue anyway...")

            #Check elilo's config file exists.
            if os.path.isfile(MountPoint+"/etc/elilo.conf"):
                #It does, we'll run the function to set the config now.
                logger.info("MainBackendTools: Main().SetNewBootloaderConfig(): Setting ELILO Configuration...")
                BootloaderConfigSettingTools.SetLILOConfig(OS=OS, filetoopen=MountPoint+"/etc/elilo.conf")

                #Also, set the OS entries.
                logger.info("MainBackendTools: Main().SetNewBootloaderConfig(): Creating ELILO OS Entries...")
                BootloaderConfigSettingTools.MakeLILOOSEntries(OS=OS, filetoopen=MountPoint+"/etc/elilo.conf", MountPoint=MountPoint, KernelOptions=BootloaderInfo[OS]["Settings"]["NewKernelOptions"])

            #Now Install ELILO to the UEFI Partition.
            logger.info("MainBackendTools: Main().SetNewBootloaderConfig(): Installing ELILO to "+OSInfo[OS]["EFIPartition"]+"...")
            BootloaderConfigSettingTools.InstallELILOToPartition(OS=OS, PackageManager=OSInfo[OS]["PackageManager"], UseChroot=UseChroot, MountPoint=MountPoint)

            #Mount the UEFI partition at MountPoint/boot/efi.
            if CoreTools.MountPartition(Partition=OSInfo[OS]["EFIPartition"], MountPoint=MountPoint+"/boot/efi") != 0:
                logger.error("MainBackendTools: Main().SetNewBootloaderConfig(): Failed to mount EFI partition "+OSInfo[OS]["EFIPartition"]+"! Continuing anyway...")

            #Copy and backup UEFI files where needed.
            HelperBackendTools.BackupUEFIFiles(MountPoint=MountPoint)
            HelperBackendTools.ManageUEFIFiles(OS=OS, MountPoint=MountPoint)

            #Unmount the EFI partition.
            if CoreTools.Unmount(OSInfo[OS]["EFIPartition"]) != 0:
                logger.error("MainBackendTools: Main().SetNewBootloaderConfig(): Couldn't unmount EFI partition! This probably won't matter, so we'll continue anyway...")

        #If there's a seperate EFI partition for this OS, make sure it's unmounted before removing the chroot.
        if OSInfo[OS]["EFIPartition"] != "Unknown":
            if CoreTools.Unmount(MountPoint+"/boot/efi") != 0:
                logger.error("MainBackendTools: Main().SetNewBootloaderConfig(): Failed to unmount "+MountPoint+"/boot/efi! This probably doesn't matter...")

        #Unmount a /boot partition if it exists.
        if OSInfo[OS]["BootPartition"] != "Unknown":
            if CoreTools.Unmount(MountPoint+"/boot") != 0:
                logger.error("MainBackendTools: Main().SetNewBootloaderConfig(): Failed to unmount "+OS+"'s /boot partition! Continuing anyway...")

        #Tear down chroot if needed.
        if UseChroot:
            if CoreTools.TearDownChroot(MountPoint=MountPoint) != 0:
                logger.error("MainBackendTools: Main().SetNewBootloaderConfig(): Failed to remove chroot at "+MountPoint+"! Attempting to continue anyway...")
    
        #Unmount the partition if needed.
        if UnmountAfter:
            if CoreTools.Unmount(MountPoint) != 0:
                logger.error("MainBackendTools: Main().SetNewBootloaderConfig(): Failed to unmount "+MountPoint+"! Continuing anyway...")

        logger.debug("MainBackendTools: Main().SetNewBootloaderConfig(): Finished setting "+BootloaderInfo[OS]["Settings"]["NewBootloader"]+"'s config for "+OS+"...")
        wx.CallAfter(ParentWindow.UpdateOutputBox, "\n###Finished setting "+BootloaderInfo[OS]["Settings"]["NewBootloader"]+"'s config for "+OS+"...###\n")
        wx.CallAfter(ParentWindow.UpdateCurrentOpText, Message="Finished setting "+BootloaderInfo[OS]["Settings"]["NewBootloader"]+"'s config for "+OS+"!")
        wx.CallAfter(ParentWindow.UpdateCurrentProgress, 100)
        return True

#End main Class.
