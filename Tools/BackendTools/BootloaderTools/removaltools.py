#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Bootloader Removal Tools in the Bootloader Tools Package in the Backend Tools package for WxFixBoot Version 2.0~pre1
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
    def RemoveGRUBLEGACY(self, PackageManager, UseChroot, MountPoint=None):
        """Remove GRUB-LEGACY."""
        if PackageManager == "apt-get":
            if UseChroot == False:
                retval = CoreBackendTools().StartThreadProcess("apt-get remove -y grub grub-legacy-doc grub-common", Piping=True, ShowOutput=False)

            else:
                retval = CoreBackendTools().StartThreadProcess("chroot "+MountPoint+" apt-get remove -y grub grub-legacy-doc grub-common", Piping=True, ShowOutput=False)
        
        #Return the return value.
        return retval

    def RemoveGRUB2(self, PackageManager, UseChroot, MountPoint=None):
        """Remove GRUB2."""
        if PackageManager == "apt-get":
            if UseChroot == False:
                retval = CoreBackendTools().StartThreadProcess("apt-get remove -y grub-pc grub-pc-bin grub-common", Piping=True, ShowOutput=False)

            else:
                retval = CoreBackendTools().StartThreadProcess("chroot "+MountPoint+" apt-get remove -y grub-pc grub-pc-bin grub-common", Piping=True, ShowOutput=False)
        
        #Return the return value.
        return retval

    def RemoveLILO(self, PackageManager, UseChroot, MountPoint=None):
        """Remove lilo."""
        if PackageManager == "apt-get":
            if UseChroot == False:
                retval = CoreBackendTools().StartThreadProcess("apt-get remove -y lilo", Piping=True, ShowOutput=False)

            else:
                retval = CoreBackendTools().StartThreadProcess("chroot "+MountPoint+" apt-get remove -y lilo", Piping=True, ShowOutput=False)
        
        #Return the return value.
        return retval

    def RemoveGRUBUEFI(self, PackageManager, UseChroot, MountPoint=None):
        """Remove GRUB-UEFI."""
        if PackageManager == "apt-get":
            if UseChroot == False:
                retval = CoreBackendTools().StartThreadProcess("apt-get remove -y grub-efi grub-efi-amd64 grub-efi-amd64-bin grub-efi-ia32 grub-efi-ia32-bin grub-common grub2-common", Piping=True, ShowOutput=False)

            else:
                retval = CoreBackendTools().StartThreadProcess("chroot "+MountPoint+" apt-get remove -y grub-efi grub-efi-amd64 grub-efi-amd64-bin grub-efi-ia32 grub-efi-ia32-bin grub-common grub2-common", Piping=True, ShowOutput=False)
        
        #Return the return value.
        return retval

    def RemoveELILO(self, PackageManager, UseChroot, MountPoint=None):
        """Remove ELILO."""
        if PackageManager == "apt-get":
            if UseChroot == False:
                retval = CoreBackendTools().StartThreadProcess("apt-get remove -y elilo", Piping=True, ShowOutput=False)

            else:
                retval = CoreBackendTools().StartThreadProcess("chroot "+MountPoint+" apt-get remove -y elilo", Piping=True, ShowOutput=False)
        
        #Return the return value.
        return retval

