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

