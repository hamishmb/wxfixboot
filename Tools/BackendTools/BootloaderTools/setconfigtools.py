#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Bootloader Configuration Setting Tools in the Bootloader Tools Package in the Backend Tools package for WxFixBoot Version 2.0~pre1
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
    def SetGRUB2Config(self, filetoopen): #*** Add logging stuff ***
        """Set GRUB2 config."""
        SetTimeout = False
        SetKOpts = False
        SetDefault = False

        #Open the file in read mode, so we can find the new config that needs setting. Also, use a list to temporarily store the modified lines.
        ConfigFile = open(filetoopen, 'r')
        NewFileContents = []

        #Loop through each line in the file, paying attention only to the important ones.
        for line in ConfigFile:
            #Look for the timeout setting.
            if 'GRUB_TIMEOUT' in line and '=' in line:
                #Found it! Set the value to the current value of BootloaderTimeout.
                SetTimeout = True
                head, sep, Temp = line.partition('=')
                Temp = unicode(BootloaderTimeout)

                #Reassemble the line.
                line = head+sep+Temp+"\n"

            #Look for kernel options setting.
            elif 'GRUB_CMDLINE_LINUX_DEFAULT' in line and '=' in line:
                #Found it! Set it to the options in KernelOptions, carefully making sure we aren't double-quoting it.
                SetKOpts = True
                head, sep, Temp = line.partition('=')

                #Reassemble the line.
                line = head+sep+"'"+KernelOptions+"'"+"\n"

            #Look for the "GRUB_DEFAULT" setting.
            elif "GRUB_DEFAULT" in line and '=' in line:
                #Found it. Set it to 'saved', so we can set the default bootloader.
                SetDefault = True
                head, sep, Temp = line.partition('=')
                Temp = "saved"

                #Reassemble the line.
                line = head+sep+Temp+"\n"

            #Comment out the GRUB_HIDDEN_TIMEOUT line.
            elif 'GRUB_HIDDEN_TIMEOUT' in line and 'GRUB_HIDDEN_TIMEOUT_QUIET' not in line and '=' in line and '#' not in line:
                line = "#"+line

            NewFileContents.append(line)

        #Check that everything was set. If not, write that config now.
        if SetTimeout == False:
            NewFileContents.append("GRUB_TIMEOUT="+unicode(BootloaderTimeout)+"\n")

        if SetKOpts == False:
            Temp = KernelOptions.replace('\"', '').replace("\'", "").replace("\n", "")
            NewFileContents.append("GRUB_CMDLINE_LINUX_DEFAULT='"+Temp+"'\n")

        if SetDefault == False:
            NewFileContents.append("GRUB_DEFAULT=saved")

        #Write the finished lines to the file.
        ConfigFile.close()
        ConfigFile = open(filetoopen, 'w')
        ConfigFile.write(''.join(NewFileContents))
        ConfigFile.close()

    def InstallGRUB2ToMBR(self, PackageManager, MountPoint): #*** Will need changing when we get rid of the Root Device concept ***
        """Install GRUB2 (BIOS version) into the MBR of the hard drive"""
        #Okay, we've modified the kernel options and the timeout. Now we need to install grub to the MBR.
        #Use --force to make sure grub installs itself, even on a GPT disk with no bios boot partition. *** Do we always want to do that? ***
        if MountPoint == "":
            if PackageManager == "apt-get":
                retval = CoreBackendTools().StartThreadProcess("grub-install --force "+RootDevice, Piping=True, ShowOutput=False)

        else:
            if PackageManager == "apt-get":
                retval = CoreBackendTools().StartThreadProcess("chroot "+MountPoint+" grub-install --force "+RootDevice, Piping=True, ShowOutput=False)

        #Return the return value.
        return retval

    def InstallGRUBUEFIToPartition(self, PackageManager, MountPoint, UEFISystemPartitionMountPoint, Arch): #*** Change the name to "InstallGRUB2ToEFIPartition" ***
        """Install GRUB2 (EFI/UEFI version) into the EFI/UEFI partition"""
        #Okay, we've modified the kernel options and the timeout. Now we need to install grub to the UEFI partition.
        if MountPoint == "":
            if PackageManager == "apt-get":
                retval = CoreBackendTools().StartThreadProcess("grub-install --efi-directory="+UEFISystemPartitionMountPoint+" --target="+Arch+"-efi", Piping=True, ShowOutput=False)

        else:
            if PackageManager == "apt-get":
                retval = CoreBackendTools().StartThreadProcess("chroot "+MountPoint+" grub-install --efi-directory="+UEFISystemPartitionMountPoint+" --target="+Arch+"-efi", Piping=True, ShowOutput=False)

        #Return the return value.
        return retval

    def UpdateGRUB2(self, PackageManager, MountPoint):
        """Run 'update-grub' to update GRUB2's (BIOS and EFI/UEFI) configuration and bootloader menu"""
        #Okay, we've modified the kernel options and the timeout. Now we need to install grub to the UEFI partition.
        if MountPoint == "":
            if PackageManager == "apt-get":
                retval = CoreBackendTools().StartThreadProcess("update-grub", Piping=True, ShowOutput=False)

        else:
            if PackageManager == "apt-get":
                retval = CoreBackendTools().StartThreadProcess("chroot "+MountPoint+" update-grub", Piping=True, ShowOutput=False)

        #Return the return value.
        return retval

    def SetGRUB2DefaultOS(self, OS, PackageManager, MountPoint): #*** Do logging stuff ***
        """Set GRUB2's (both BIOS and EFI/UEFI) default OS to boot"""
        #I couldn't find a reliable way of doing this automatically, so give the user a choice box instead. *** Do this before release of final v2.0, probably in the 1st or 2nd rc. Maybe use disk names and save grub's name for each one ***
        global DefaultOS

        #Make a list of OSs grub2 found (hopefully all of them).
        GrubConfigFilePath = "/boot/grub/grub.cfg"

        if MountPoint != "":
            GrubConfigFilePath = MountPoint+GrubConfigFilePath

        GrubMenuEntries = ""

        if PackageManager == "apt-get":
            GrubConfigFile = open("/boot/grub/grub.cfg", "r")
            GrubConfig = GrubCfgFile.read()
            GrubConfigFile.close()

        for Line in GrubConfig.split("\n"):
            if "menuentry " in Line:
                GrubMenuEntries += Line+"\n"

        if GrubMenuEntries == "":
            #Don't set the default OS.
            DialogTools().ShowMsgDlg(Kind="error", Message="WxFixBoot failed to set the default OS. This doesn't really matter. Click okay to continue.")

        else:
            #Now finally make the list of grub's OS names.
            GRUBOSNameList = []

            #Split with each newline character found in the returned string. *** Do this earlier ***
            GrubMenuEntriesList = GrubMenuEntries.split('\n')

            for OSName in GrubMenuEntriesList:
                #Get each OS name, removing all of the unneeeded characters. *** Can we use .split() instead? ***
                junk,sep,info = OSName.partition("'")
                info,sep,junk = info.partition("'")
                GRUBOSNameList.append(info)

            #Now ask the user to select the correct one.
            DefaultOS = DialogTools().ShowChoiceDlg(Message="Please select the OS you want to use as "+BootloaderToInstall+"'s Default OS. You are setting configuration for: "+OS, Title="WxFixBoot - Select Default OS", Choices=GRUBOSNameList)

            #Use the user's selection to set the default OS.
            if LiveDisk == False and MountPoint == "":
                #If the OS is AutoRootFS, and we're not on a live disk, do it differently.
                if PackageManager == "apt-get":
                    retval = CoreBackendTools().StartThreadProcess("grub-set-default "+DefaultOS, Piping=True, ShowOutput=False)

            else:
                if PackageManager == "apt-get":
                    retval = CoreBackendTools().StartThreadProcess("chroot "+MountPoint+" grub-set-default "+DefaultOS, Piping=True, ShowOutput=False)

            #Return the return value.
            return retval

    def SetLILOConfig(self, filetoopen, PackageManager, MountPoint): #*** Add logging stuff ***
        """Set LILO's config."""
        SetTimeout = False
        SetBootDevice = False

        #Open the file in read mode, so we can find the important bits of config to edit. Also, use a list to temporarily store the modified lines.
        ConfigFile = open(filetoopen, 'r')
        NewFileContents = []

        #Loop through each line in the file, paying attention only to the important ones.
        for line in ConfigFile:
            #Look for the timeout setting.
            if 'timeout' in line and '=' in line and '#' not in line:
                #Found it! Set it to our value.
                SetTimeout = True

                #Save it, carefully avoiding errors.
                head, sep, Temp = line.partition('=')
                Temp = unicode(BootloaderTimeout*10)

                #Reassemble the line.
                line = "timeout"+sep+Temp+"\n"

            #Look for the 'boot' setting.
            elif 'boot' in line and '=' in line and '#' not in line and 'map' not in line: 
                #Found it, seperate the line.
                SetBootDevice = True
                head, sep, Temp = line.partition('=')

                #Now let's find the ID of RootDevice.
                ID = CoreBackendTools().GetDeviceID(Device=RootDevice)
                if ID != "None":
                    #Good, we've got the ID.
                    #Set it to RootDevice's ID.                    
                    Temp = "/dev/disk/by-id/"+ID

                else:
                    #Not so good... We'll have to use the device name, which may change, especially if we're using chroot.
                    Temp = RootDevice

                #Reassemble the line.
                line = head+sep+Temp+"\n"

            NewFileContents.append(line)

        #Check that everything was set. If not, write that config now.
        if SetTimeout == False:
            NewFileContents.append("timeout="+unicode(BootloaderTimeout)+"\n")

        if SetBootDevice == False:
            #Now let's find the ID of RootDevice.
            ID = CoreBackendTools().GetDeviceID(Device=RootDevice)
            if ID != "None":
                #Good, we've got the ID.
                #Set it to RootDevice's ID.                    
                Temp = "/dev/disk/by-id/"+ID

            else:
                #Not so good... We'll have to use the device name, which may change, especially if we're using chroot.
                Temp = RootDevice

            NewFileContents.append("boot="+Temp+"\n")

        #Write the finished lines to the file.
        ConfigFile.close()
        ConfigFile = open(filetoopen, 'w')
        ConfigFile.write(''.join(NewFileContents))
        ConfigFile.close()

    def SetELILOConfig(self, filetoopen, PackageManager, MountPoint): #*** Add logging stuff ***
        """Set ELILO config."""
        SetTimeout = False
        SetUEFIPart = False

        #Open the file in read mode, so we can find the important bits of config to edit. Also, use a list to temporarily store the modified lines.
        ConfigFile = open(filetoopen, 'r')
        NewFileContents = []

        #Loop through each line in the file, paying attention only to the important ones.
        for line in ConfigFile:
            #Look for the delay setting.
            if 'delay' in line and '=' in line and '#' not in line:
                #Found it! Set it to our value.
                SetTimeout = True

                #Save it, carefully avoiding errors.
                head, sep, Temp = line.partition('=')
                Temp = unicode(BootloaderTimeout*10)

                #Reassemble the line.
                line = head+sep+Temp+"\n"

            #Look for the 'boot' setting.
            elif 'boot' in line and '=' in line and '#' not in line:
                #Found it, seperate the line.
                SetUEFIPart = True
                head, sep, Temp = line.partition('=')

                #Now let's find the ID of UEFISystemPartition.
                ID = CoreBackendTools().GetDeviceID(Device=UEFISystemPartition)

                if ID != "None":
                    #Good, we've got the ID.
                    #Set it to UEFISystemPartition's ID.                    
                    Temp = "/dev/disk/by-id/"+ID

                else:
                    #Not so good... We'll have to use the partition's name, which may change, especially if we're using chroot.
                    Temp = UEFISystemPartition

                #Reassemble the line.
                line = head+sep+Temp+"\n"

            #Get rid of any boot entries.
            elif 'image=' in line or '\t' in line:
                #Skip this line, and don't append it to the list.
                continue

            NewFileContents.append(line)

        #Check that everything was set. If not, write that config now.
        if SetTimeout == False:
            NewFileContents.append("delay="+unicode(BootloaderTimeout)+"\n")

        if SetUEFIPart == False:
            #Now let's find the ID of UEFISystemPartition.
            ID = CoreBackendTools().GetDeviceID(Device=UEFISystemPartition)
            if ID != "None":
                #Good, we've got the ID.
                #Set it to UEFISystemPartition's ID.                    
                Temp = "/dev/disk/by-id/"+ID

            else:
                #Not so good... We'll have to use the device name, which may change, especially if we're using chroot.
                Temp = UEFISystemPartition

            NewFileContents.append("boot="+Temp+"\n")

        #Write the finished lines to the file.
        ConfigFile.close()
        ConfigFile = open(filetoopen, 'w')
        ConfigFile.write(''.join(NewFileContents))
        ConfigFile.close()

    def MakeLILOOSEntries(self, filetoopen, PackageManager, MountPoint):
        """Make OS Entries in the bootloader menu for LILO and ELILO, and then the default OS""" #*** Maybe set default OS in a seperate function? ***
        #Okay, we've saved the kopts, timeout, and the boot device in the list.
        #Now we'll set the OS entries, and then the default OS.
        #Open the file, and add each entry to a temporary list, which will be written to the file later.
        ConfigFile = open(filetoopen, 'r')
        NewFileContents = []

        #First, make sure everything else comes first, because LILO and ELILO are picky with the placement of the image files (they must be at the end of the file).
        #We'll also make a placeholder for the default OS, so it comes before the image entries too.
        Temp = False
        for line in ConfigFile:
            if 'default' in line and '=' in line and '#' not in line:
                #The place holder already exists. Set a variable so we don't make one.
                Temp = True

            NewFileContents.append(line)

        #If there isn't a placeholder, make one now.
        if Temp == False:
            NewFileContents.append("default=setthis\n")

        #Make the OS entries.
        if BootloaderToInstall == "ELILO":
            NewFileContents.append("#################### ELILO per-image section ####################")

        #As we make these entries, we'll record which ones were actually made, as the user can cancel them if it looks like it won't work.
        CompletedEntriesList = []

        for OS in OSList:
            logger.info("BootloaderConfigSettingTools: Main().MakeLILOOSEntries(): Preparing to make an entry for: "+OS)

            #Names in LILO are not allowed to have spaces, so let's grab the names and remove the spaces from them.
            #If this OS is the currently running one, we'll need to access a different part of the element.
            if OS.split()[-5] == "OS)":
                OSName = ''.join(OS.split()[0:-6])

            else:
                OSName = ''.join(OS.split()[0:-4])

            #Remove all the spaces from the OS's name.
            OSName = OSName.replace(' ','')

            #Grab the OS's partition.
            Partition = OS.split()[-1]

            #Check that the name is no longer than 15 characters.
            if len(OSName) > 15:
                #The name is too long! Truncate it to 15 characters.
                logger.warning("BootloaderConfigSettingTools: Main().MakeLILOOSEntries(): Truncating OS Name: "+OSName+" to 15 characters...")
                OSName = OSName[0:15]

            #Now let's make the entries.
            logger.debug("BootloaderConfigSettingTools: Main().MakeLILOOSEntries(): Checking for /vmlinuz and /initrd.img...")

            if OS[-5] == "OS)": #*** When we use dictionaries we won't need to do this ***
                CurrentOS = True

            else:
                CurrentOS = False

            #Check that MountPoint/vmlinuz and MountPoint/initrd.img exist. (If this is the current OS, MountPoint = "", and so doesn't get in the way).
            if os.path.isfile(MountPoint+"/vmlinuz"):
                #Good, add this to the file. (It's local to the partition, so we don't need to include MountPoint in the path)
                logger.info("BootloaderConfigSettingTools: Main().MakeLILOOSEntries(): Found /vmlinuz! Adding it to the config file...")
                NewFileContents.append("\nimage=/vmlinuz\n")

            else:
                #Not so good... This probably means changing LILO's config each time we do a kernel update... Let's ask the user if we should still add it.
                logger.warning("BootloaderConfigSettingTools: Main().MakeLILOOSEntries(): Couldn't find /vmlinuz for: "+OS+"! Asking the user if we should search for vmlinuz and make an entry anyway...")

                Result = DialogTools().ShowYesNoDlg(Message="Warning: /vmlinuz (shortcut to the latest kernel) wasn't found for: "+OS+"! Your new bootloader will still work, but this might mean you'll have to manaully change its config file each time you update your kernel on this OS. You can do this with WxFixBoot, but that won't stop it from being annoying and introducing security risks if you forget. However, this OS will be unbootable if you don't add it to the boot menu. Do you want to add it to the boot menu anyway?", Title="WxFixBoot - Add OS to boot menu?")

                if Result == False:
                    #Okay, go back to the start of the loop.
                    logger.warning("BootloaderConfigSettingTools: Main().MakeLILOOSEntries(): Not making an entry for "+OS+"! Skipping this OS...")
                    continue

                else:
                    #Right, we'll have to hunt out the Kernel.
                    logger.warning("BootloaderConfigSettingTools: Main().MakeLILOOSEntries(): Okay, we'll make an entry for "+OS+" anyway. Now let's try and find the latest Kernel...")
                    Kernel = HelperBackendTools().FindLatestVersion(Directory=MountPoint+"/boot", Type="Kernel")

                    #Check if we found it.
                    if Kernel == "None":
                        #We didn't! Tell the user, and skip this OS.
                        logger.error("BootloaderConfigSettingTools: Main().MakeLILOOSEntries(): Couldn't find the latest kernel for "+OS+"! This OS will now be skipped!") 
                        DialogTools().ShowMsgDlg(Kind="error", Message="WxFixBoot couldn't find the latest kernel for this OS. This OS will now be skipped.")
                        continue

                    else:
                        #We did! Add it to the file. (It's local to the partition, so we don't need to include MountPoint in the path)
                        logger.info("BootloaderConfigSettingTools: Main().MakeLILOOSEntries(): Found the latest kernel at: "+Kernel+"! Adding it to the config file...")
                        NewFileContents.append("\nimage=/boot/"+Kernel+"\n")

            if os.path.isfile(MountPoint+"/initrd.img"):
                #Good, add this to the file. (It's local to the partition, so we don't need to include MountPoint in the path)
                logger.info("BootloaderConfigSettingTools: Main().MakeLILOOSEntries(): Found /initrd.img! Adding it to the config file...")
                NewFileContents.append("\tinitrd=/initrd.img\n")

            else:
                #Not so good... This probably means changing LILO's config each time we do a kernel update... Let's ask the user if we should still add it.
                logger.warning("BootloaderConfigSettingTools: Main().MakeLILOOSEntries(): Couldn't find /initrd.img for "+OS+"! Asking the user if we should search for initrd.img and make an entry anyway...")

                Result = DialogTools().ShowYesNoDlg(Message="Warning: /initrd.img (shortcut to the latest Initial Filesystem) wasn't found for: "+OS+"! Your new bootloader will still work, but this might mean you'll have to manaully change its config file each time you update your kernel on this OS. You can do this with WxFixBoot, but that won't stop it from being annoying and introducing security risks if you forget. Do you want to add it to the boot menu anyway?", Title="WxFixBoot - Add OS to boot menu?")

                if Result == False:
                    #Okay, delete the last entry, so we don't have an unconfigured image, and then go back to the start of the loop.
                    logger.warning("BootloaderConfigSettingTools: Main().MakeLILOOSEntries(): Not making an entry for "+OS+"! Deleting the unconfigured image, and skipping this OS...")
                    Temp = NewFileContents.pop()
                    continue

                else:
                    #Right, we'll have to hunt out the Initrd/Initramfs.
                    logger.warning("BootloaderConfigSettingTools: Main().MakeLILOOSEntries(): Okay, we'll make an entry for "+OS+" anyway. Now let's try and find the latest Initrd...")
                    Initrd = HelperBackendTools().FindLatestVersion(Directory=MountPoint+"/boot", Type="Initrd")

                    #Check if we found it.
                    if Initrd == "None":
                        #We didn't! Tell the user, delete the unconfigured image entry (logically there must be one), and skip this OS.
                        logger.error("BootloaderConfigSettingTools: Main().MakeLILOOSEntries(): Couldn't find the latest Initrd for "+OS+"! This OS will now be skipped, and the unconfigured image deleted!") 
                        DialogTools().ShowMsgDlg(Kind="error", Message="WxFixBoot couldn't find the latest initrd.img for this OS. This OS will now be skipped.")
                        Temp = NewFileContents.pop()
                        continue

                    else:
                        #We did! Add it to the file. (It's local to the partition, so we don't need to include MountPoint in the path)
                        logger.info("BootloaderConfigSettingTools: Main().MakeLILOOSEntries(): Found the latest Initrd at: "+Initrd+"! Adding it to the config file...")
                        NewFileContents.append("\tinitrd=/boot/"+Initrd+"\n")

            #Set the root device.
            #Use UUID's here if we can.
            UUID = CoreBackendTools().GetPartitionUUID(Partition)
            if UUID == "None":
                NewFileContents.append("\troot="+Partition+"\n")

            else:
                #If we're using ELILO, we have to do this differently.
                if BootloaderToInstall == "ELILO":
                    NewFileContents.append("\troot=UUID="+UUID+"\n")

                else:
                    NewFileContents.append("\troot=\"UUID="+UUID+"\"\n")

            #Set the label.
            NewFileContents.append("\tlabel="+OSName+"\n")

            #Set the kernel options.
            NewFileContents.append("\tappend=\""+KernelOptions+"\"\n")

            #Set one other necessary boot option.
            NewFileContents.append("\tread-only\n")

            #Add this OS to the Completed Entries List, because if we got this far it's done and added.
            CompletedEntriesList.append(OSName)

        #Now set the default OS.
        #First, write the semi-finished lines to the file.
        ConfigFile.close()
        ConfigFile = open(filetoopen, 'w')
        ConfigFile.write(''.join(NewFileContents))
        ConfigFile.close()

        #Open the file again, with the new files written.
        ConfigFile = open(filetoopen, 'r')
        NewFileContents = []

        #Get the OS name and truncate it if necessary.
        logger.info("BootloaderConfigSettingTools: Main().MakeLILOOSEntries(): Getting and truncating the default OS's name...")

        #If DefaultOS is the currently running one, we'll need to access a different part of the variable.
        if DefaultOS.split()[-5] == "OS)":
            OSName = ''.join(DefaultOS.split()[0:-6])

        else:
            OSName = ''.join(DefaultOS.split()[0:-4])

        #Remove all of the spaces.
        DefaultOSName = OSName.replace(' ','')

        #Check that the name is no longer than 15 characters.
        if len(DefaultOSName) > 15:
            #The name is too long! Truncate it to 15 characters.
            logger.warning("BootloaderConfigSettingTools: Main().MakeLILOOSEntries(): Truncating OS Name: "+DefaultOSName+" to 15 characters...")
            DefaultOSName = DefaultOSName[0:15]

        #Now, check if its entry was added to the file, and ask the user for a new one if it wasn't.
        if DefaultOSName not in CompletedEntriesList:
            logger.info("BootloaderConfigSettingTools: Main().MakeLILOOSEntries(): Default OS not in the Completed Entries List! Asking the user for a new one...")

            if len(CompletedEntriesList) <= 0:
                #Something went wrong here! No OSs appear to have been added to the list. Warn the user. *** How about being helpful and trying to fix it right now? :D ***
                logger.error("BootloaderConfigSettingTools: Main().MakeLILOOSEntries(): CompletedEntriesList is empty! This suggests that no OSs have been added to the list! Warn the user, and skip this part of the operation.")
                DialogTools().ShowMsgDlg(Kind="error", Message="No Operating Systems have had entries created for them! If you canceled creating the entries, please reboot WxFixBoot and select only the option 'Update Bootloader Config'. If you didn't do that, and WxFixBoot either couldn't create them, or you see this error with no previous warnings, you may have to create your own bootloader config. Don't worry, this isn't too difficult, and you can search for tutorials for this on the internet. If WxFixBoot couldn't create your entries, or you are seeing this message with no previous warnings, please also email me directly via my Launchpad page with the contents of /tmp/wxfixboot.log and I'll try to help you.")

            else:
                #Ask the user for a new default OS.
                DefaultOSName = DialogTools().ShowChoiceDlg(Message="The OS you previously selected as the default wasn't added to the boot menu. Please an new OS you want to use as "+Bootloader+"'s Default OS. You are setting configuration for: "+OS, Title="WxFixBoot - Select Default OS", Choices=CompletedEntriesList)
                logger.info("BootloaderConfigSettingTools: Main().MakeLILOOSEntries(): User selected new default OS: "+DefaultOSName+"...")

        #Make the entry for the default OS.
        logger.info("BootloaderConfigSettingTools: Main().MakeLILOOSEntries(): Setting default OS...")
        SetDefaultOS = False

        for line in ConfigFile:
            if 'default' in line and '=' in line and '#' not in line:
                #Get the LILO name for DefaultOS.
                SetDefaultOS = True

                #Set default to the name.
                line = "default="+DefaultOSName+"\n"

            NewFileContents.append(line)

        #Check that everything was set. If not, write that config now.
        if SetDefaultOS == False:
            NewFileContents.append("default="+DefaultOSName+"\n")

        #Write the finished lines to the file.
        ConfigFile.close()
        ConfigFile = open(filetoopen, 'w')
        ConfigFile.write(''.join(NewFileContents))
        ConfigFile.close()

    def InstallLILOToMBR(self, PackageManager, MountPoint): #*** Will need changing when we get rid of the Root Device concept ***
        """Install LILO to the MBR of RootDev."""
        if MountPoint == "":
            retval = CoreBackendTools().StartThreadProcess("lilo", Piping=True, ShowOutput=False)

        else:
            retval = CoreBackendTools().StartThreadProcess("chroot "+MountPoint+" lilo", Piping=True, ShowOutput=False)

        #Return the return value.
        return retval

    def InstallELILOToPartition(self, PackageManager, MountPoint, UEFISystemPartition):
        """Install ELILO to the EFI/UEFI Partition"""
        #Okay, we've modified the kernel options and the timeout. Now we need to install grub to the UEFI partition.
        if MountPoint == "":
            if PackageManager == "apt-get":
                retval = CoreBackendTools().StartThreadProcess("elilo -b "+UEFISystemPartition+" --efiboot", Piping=True, ShowOutput=False)

        else:
            if PackageManager == "apt-get":
                retval = CoreBackendTools().StartThreadProcess("chroot "+MountPoint+" elilo -b "+UEFISystemPartition+" --efiboot", Piping=True, ShowOutput=False)

        #Return the return value.
        return retval
