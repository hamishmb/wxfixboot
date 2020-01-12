#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# CoreTools test functions for WxFixBoot
# This file is part of WxFixBoot.
# Copyright (C) 2013-2020 Hamish McIntyre-Bhatty
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

#If you're wondering why this is here, it's so that there are some known good/sane functions
#to aid testing the real ones. These are needed to manipulate system state so we can create
#various situations to test the real functions against.

#Do future imports to prepare to support python 3. Use unicode strings rather than ASCII
#strings, as they fix potential problems.
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

#Import modules.
import time
import os
import subprocess

def start_process(command, return_output=False):
    """Start a given process, and return output and return value if needed"""
    runcmd = subprocess.Popen("LC_ALL=C "+command, stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT, shell=True)

    while runcmd.poll() is None:
        time.sleep(0.25)

    #Save runcmd.stdout.readlines, and runcmd.returncode, as they tend to reset fairly quickly.
    #Handle unicode properly.
    output = []

    for line in runcmd.stdout.readlines():
        output.append(line.decode("UTF-8", errors="ignore"))

    retval = int(runcmd.returncode)

    if return_output is False:
        #Return the return code back to whichever function ran this process, so it can handle
        #any errors.
        return retval

    #Otherwise, return the return code, as well as the output.
    return retval, ''.join(output)

def is_mounted(partition, mount_point=None):
    """Checks if the given partition is mounted.
    partition is the given partition to check.
    If mount_point is specified, check if the partition is mounted there, rather than just if
    it's mounted.
    Return boolean True/False.
    """

    if mount_point is None:
        mount_info = start_process("mount", return_output=True)[1]

        mounted = False

        #Linux fix: Accept any mountpoint when called with just one argument.
        for line in mount_info.split("\n"):
            if line:
                if line.split()[0] == partition or line.split()[2] == partition:
                    mounted = True
                    break

    else:
        #Check where it's mounted to.
        mounted = False

        if get_mount_point_of(partition) == mount_point:
            mounted = True

    return mounted

def get_mount_point_of(partition):
    """Returns the mountpoint of the given partition, if any.
    Otherwise, return None"""
    mount_info = start_process("mount", return_output=True)[1]
    mount_point = None

    for line in mount_info.split("\n"):
        split_line = line.split()

        if split_line:
            if partition == split_line[0]:
                mount_point = split_line[2]
                break

    return mount_point

def mount_partition(partition, mount_point, options=""):
    """
    Mounts the given partition.
    partition is the partition to mount.
    mount_point is where you want to mount the partition.
    options is non-mandatory and contains whatever options you want to pass to the mount command.
    The default value for options is an empty string.
    """

    mount_info = start_process("mount", return_output=True)[1]

    #There is a partition mounted here. Check if our partition is already mounted in the
    #right place.
    if mount_point == get_mount_point_of(partition):
        #The correct partition is already mounted here.
        return 0

    elif mount_point in mount_info:
        #Something else is in the way. Unmount that partition, and continue.
        if unmount_disk(mount_point) != 0:
            return False

    #Create the dir if needed.
    if os.path.isdir(mount_point) is False:
        os.makedirs(mount_point)

    #Mount the device to the mount point.
    retval = start_process("mount "+options+" "+partition+" "+mount_point)

    return retval

def unmount_disk(disk):
    """Unmount the given disk"""
    #Check if it is mounted.
    if is_mounted(disk) is False:
        #The disk isn't mounted.
        #Set retval to 0.
        retval = 0

    else:
        #The disk is mounted.
        #Unmount it.
        retval = start_process(command="umount "+disk, return_output=False)

    #Return the return value
    return retval
