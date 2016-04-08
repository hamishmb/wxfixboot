#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Bootloader Installation Tools in the Bootloader Tools Package in the Backend Tools package for WxFixBoot Version 2.0~pre1
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
    def UpdatePackageLists(self, PackageManager, UseChroot, MountPoint=None):
        """Update the package lists so the required packages can always be found."""
        if PackageManager == "apt-get":
            if UseChroot == False:
                retval = CoreTools.StartProcess("DEBIAN_FRONTEND=noninteractive apt-get update")

            else:
                retval = CoreTools.StartProcess("chroot "+MountPoint+" sh -c 'DEBIAN_FRONTEND=noninteractive apt-get update'")
        
        #Return the return value.
        return retval

    def InstallGRUB2(self, PackageManager, UseChroot, MountPoint=None):
        """Install GRUB2."""
        if PackageManager == "apt-get":
            if UseChroot == False:
                retval = CoreTools.StartProcess("DEBIAN_FRONTEND=noninteractive apt-get install -y grub-pc os-prober")

            else:
                retval = CoreTools.StartProcess("chroot "+MountPoint+" sh -c 'DEBIAN_FRONTEND=noninteractive apt-get install -y grub-pc os-prober'")
        
        #Return the return value.
        return retval

    def InstallLILO(self, PackageManager, UseChroot, MountPoint=None):
        """Install LILO."""
        if PackageManager == "apt-get":
            if UseChroot == False:
                retval = CoreTools.StartProcess("DEBIAN_FRONTEND=noninteractive apt-get install -y lilo")

            else:
                retval = CoreTools.StartProcess("chroot "+MountPoint+" sh -c 'DEBIAN_FRONTEND=noninteractive apt-get install -y lilo'")
        
        #Return the return value.
        return retval

    def InstallGRUBUEFI(self, PackageManager, UseChroot, MountPoint=None):
        """Install GRUB-UEFI."""
        if PackageManager == "apt-get":
            if UseChroot == False:
                retval = CoreTools.StartProcess("DEBIAN_FRONTEND=noninteractive apt-get install -y grub-efi os-prober")

            else:
                retval = CoreTools.StartProcess("chroot "+MountPoint+" sh -c 'DEBIAN_FRONTEND=noninteractive apt-get install -y grub-efi os-prober'")
        
        #Return the return value.
        return retval

    def InstallELILO(self, PackageManager, UseChroot, MountPoint=None):
        """Install ELILO."""
        if PackageManager == "apt-get":
            if UseChroot == False:
                retval = CoreTools.StartProcess("DEBIAN_FRONTEND=noninteractive apt-get install -y elilo")

            else:
                retval = CoreTools.StartProcess("chroot "+MountPoint+" sh -c 'DEBIAN_FRONTEND=noninteractive apt-get install -y elilo'")
        
        #Return the return value.
        return retval

