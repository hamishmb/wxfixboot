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

    def RemoveLILO(self, PackageManager, UseChroot, Arch, MountPoint="None"): #*** Change when we switch to always using shell=True ***
        """Remove lilo."""
        if PackageManager == "apt-get":
            if UseChroot == False:
                retval = CoreBackendTools().StartThreadProcess(['apt-get', 'remove', '-y', 'lilo'])

            else:
                retval = CoreBackendTools().StartThreadProcess(['chroot', MountPoint, 'apt-get', 'remove', '-y', 'lilo'])
        
        #Return the return value.
        return retval

    def RemoveGRUBUEFI(self, PackageManager, UseChroot, Arch, MountPoint="None"): #*** Change when we switch to always using shell=True ***
        """Remove GRUB-UEFI."""
        if PackageManager == "apt-get":
            if UseChroot == False:
                retval = CoreBackendTools().StartThreadProcess(['apt-get', 'remove', '-y', 'grub-efi', 'grub-efi-amd64', 'grub-efi-amd64-bin', 'grub-efi-ia32', 'grub-efi-ia32-bin', 'grub-common', 'grub2-common'])

            else:
                retval = CoreBackendTools().StartThreadProcess(['chroot', MountPoint, 'apt-get', 'remove', '-y', 'grub-efi', 'grub-efi-amd64', 'grub-efi-amd64-bin', 'grub-efi-ia32', 'grub-efi-ia32-bin', 'grub-common', 'grub2-common'])
        
        #Return the return value.
        return retval

    def RemoveELILO(self, PackageManager, UseChroot, Arch, MountPoint="None"): #*** Change when we switch to always using shell=True ***
        """Remove ELILO."""
        if PackageManager == "apt-get":
            if UseChroot == False:
                retval = CoreBackendTools().StartThreadProcess(['apt-get', 'remove', '-y', 'elilo'])

            else:
                retval = CoreBackendTools().StartThreadProcess(['chroot', MountPoint, 'apt-get', 'remove', '-y', 'elilo'])
        
        #Return the return value.
        return retval

