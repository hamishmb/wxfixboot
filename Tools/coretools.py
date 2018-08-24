#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Core Tools in the Tools Package for WxFixBoot Version 3.0.0
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

# pylint: disable=logging-not-lazy
#
# Reason (logging-not-lazy): This is a more readable way of logging.

#Do future imports to prepare to support python 3. Use unicode strings rather than ASCII strings, as they fix potential problems.
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

#Import modules.
import subprocess
import sys
import logging
import os
import wx

#Import other modules.
from . import dialogtools as DialogTools

#Set up logging. FIXME Set logger level as specified on cmdline.
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def start_process(exec_cmds, show_output=True, return_output=False, testing=False):
    """Start a process given a string of commands to execute.
    show_output is boolean and specifies whether to show output in the outputbox (if exists) or not.
    return_output is boolean and specifies whether to return the output back to the caller or not.
    """
    #Make sure output is always in English.
    exec_cmds = "LC_ALL=C "+exec_cmds

    #Run the command(s).
    logger.debug("start_process(): Starting process: "+exec_cmds)
    cmd = subprocess.Popen(exec_cmds, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)

    #Use a simpler output reader on startup to improve performance.
    if Startup:
        line_list = read(cmd, testing=testing)

    else:
        line_list = read_and_send_output(cmd, show_output)

    #Save runcmd.returncode, as it tends to reset fairly quickly.
    ret_val = int(cmd.returncode)

    #Log this info in a debug message.
    logger.debug("start_process(): Process: "+exec_cmds+": Return Value: "+unicode(ret_val)+", Output: \"\n\n"+'\n'.join(line_list)+"\"\n")

    if return_output is False:
        #Return the return code back to whichever function ran this process, so it can handle any errors.
        return ret_val

    elif testing:
        #Return the return code, as well as the output (not joining on newlines).
        return (ret_val, ''.join(line_list))

    #Otherwise, just return the return code, as well as the output.
    return (ret_val, '\n'.join(line_list))

def read(cmd, testing=False):
    """Read the cmd's output char by char, but do as little processing as possible to improve startup performance"""
    #Get ready to run the command(s). Read up to 100 empty "" characters after the process finishes to make sure we get all the output.
    counter = 0
    line = str("")
    line_list = []

    while cmd.poll() is None or counter < 100:
        char = cmd.stdout.read(1)

        if char == "":
            counter += 1
            continue

        line += char

        if char in ("\n", "\r"):
            #Interpret as Unicode and remove "NULL" characters.
            line = line.decode("UTF-8", errors="replace").replace("\x00", "")

            if testing:
                line_list.append(line)

            else:
                line_list.append(line.replace("\n", "").replace("\r", ""))

            #Reset line.
            line = str("")

    return line_list

def read_and_send_output(cmd, show_output):
    """Read the cmd's output char by char, and send the output to the output box"""
    #Get ready to run the command(s). Read up to 100 empty "" characters after the process finishes to make sure we get all the output.
    counter = 0
    line = str("")
    line_list = []
    hold = False
    send_line = False

    while cmd.poll() is None or counter < 100:
        char = cmd.stdout.read(1)

        if char == "":
            counter += 1
            continue

        line += char

        if hold:
            #Check if this char is \n.
            if char == "\n":
                #Send the line as is but replace \r\n with \n.
                line = str(line.replace("\r\n", "\n"))

            else:
                #Send the line as is.
                send_line = True

            hold = False

        if char in ("\n", "\x08") or send_line:
            #Interpret as Unicode and remove "NULL" characters.
            line = line.decode("UTF-8", errors="replace").replace("\x00", "")

            wx.CallAfter(ParentWindow.UpdateOutputBox, line, show_output)
            line_list.append(line.replace("\n", "").replace("\r", "").replace("\x08", ""))

            #Reset line.
            line = str("")
            send_line = False

        elif char == "\r":
            #Take the next character too in case it's \n, so we can just handle \r\n as \n.
            hold = True

    return line_list

def is_mounted(partition, mount_point=None):
    """Checks if the given partition is mounted.
    partition is the given partition to check.
    If mount_point is specified, check if the partition is mounted there, rather than just if it's mounted.
    Return boolean True/False.
    """
    if mount_point is None:
        logger.debug("is_mounted(): Checking if "+partition+" is mounted...")
        mount_info = start_process("mount -l", show_output=False, return_output=True)[1]

        mounted = False

        for line in mount_info.split("\n"):
            if line.split()[0] == partition:
                mounted = True

    else:
        #Check where it's mounted to.
        logger.debug("is_mounted(): Checking if "+partition+" is mounted at "+mount_point+"...")

        mounted = False

        if get_mount_point_of(partition) == mount_point:
            mounted = True

    if mounted:
        logger.debug("is_mounted(): It is. Returning True...")
        return True

    #else return false.
    logger.debug("is_mounted(): It isn't. Returning False...")
    return False

def get_partition_mounted_at(mount_point):
    """Returns the partition mounted at the given mountpoint, if any.
    Otherwise, return None"""
    logger.info("get_partition_mounted_at(): Trying to get partition mounted at "+mount_point+"...")

    mount_info = start_process("mount -l", show_output=False, return_output=True)[1]
    partition = None

    for line in mount_info.split("\n"):
        split_line = line.split()

        if mount_point == split_line[2]:
            partition = split_line[0]

    if partition != None:
        logger.info("get_partition_mounted_at(): Found it! partition is "+partition+"...")

    else:
        logger.info("get_partition_mounted_at(): Didn't find it...")

    return partition

def get_mount_point_of(partition):
    """Returns the mountpoint of the given partition, if any.
    Otherwise, return None"""
    logger.info("get_mount_point_of(): Trying to get mount point of partition "+partition+"...")

    mount_info = start_process("mount -l", show_output=False, return_output=True)[1]
    mount_point = None

    for line in mount_info.split("\n"):
        split_line = line.split()

        if partition == split_line[0]:
            mount_point = split_line[2]

    if mount_point != None:
        logger.info("get_mount_point_of(): Found it! mount_point is "+mount_point+"...")

    else:
        logger.info("get_mount_point_of(): Didn't find it...")

    return mount_point

def mount_partition(partition, mount_point, options=""):
    """Mounts the given partition.
    partition is the partition to mount.
    mount_point is where you want to mount the partition.
    options is non-mandatory and contains whatever options you want to pass to the mount command.
    The default value for options is an empty string.
    """
    if options != "":
        logger.info("mount_partition(): Preparing to mount "+partition+" at "+mount_point+" with extra options "+options+"...")

    else:
        logger.info("mount_partition(): Preparing to mount "+partition+" at "+mount_point+" with no extra options...")

    mount_info = start_process("mount -l", show_output=False, return_output=True)[1]

    #There is a partition mounted here. Check if our partition is already mounted in the right place.
    if mount_point == get_mount_point_of(partition):
        #The correct partition is already mounted here.
        logger.debug("mount_partition(): partition: "+partition+" was already mounted at: "+mount_point+". Continuing...")
        return 0

    elif mount_point in mount_info:
        #Something else is in the way. unmount that partition, and continue.
        logger.warning("mount_partition(): unmounting filesystem in the way at "+mount_point+"...")
        ret_val = unmount(mount_point)

        if ret_val != 0:
            logger.error("mount_partition(): Couldn't unmount "+mount_point+", preventing the mounting of "+partition+"! Skipping mount attempt.")
            return False

    #Create the dir if needed.
    if os.path.isdir(mount_point) is False:
        os.makedirs(mount_point)

    #Mount the device to the mount point.
    ret_val = start_process("mount "+options+" "+partition+" "+mount_point, show_output=False)

    if ret_val == 0:
        logger.debug("mount_partition(): Successfully mounted partition!")

    else:
        logger.warning("mount_partition(): Failed to mount partition!")

    return ret_val

def remount_partition(partition, mode="rw"):
    """Remounts the given partition.
    partition is the partition to remount.
    mode is non-mandatory and is either rw or ro for read-write or read-only respectively.
    The default value for mode is rw.
    """
    logger.debug("remount_partition(): Remounting "+partition+" as "+mode+"...")
    ret_val = start_process("mount -o remount,"+mode+" "+partition, show_output=False)

    if ret_val == 0:
        logger.warning("remount_partition(): Successfully remounted partition!")

    else:
        logger.info("remount_partition(): Failed to remount partition!")

    #Return the return value
    return ret_val

def unmount(mount_point):
    """unmounts the given mountpoint.
    mount_point is the mountpoint to unmount.
    mount_point can also be a partition name (for example /dev/sda1).
    """
    logger.debug("unmount(): Preparing to unmount "+mount_point)

    if mount_point not in start_process("mount -l", show_output=False, return_output=True)[1]:
        logger.info("unmount(): "+mount_point+" was not mounted. Continuing...")
        ret_val = 0

    else:
        logger.debug("unmount(): unmounting "+mount_point+"...")
        ret_val = start_process("umount "+mount_point, show_output=False)

        if ret_val == 0:
            logger.info("unmount(): Successfully unmounted "+mount_point+"!")

        else:
            logger.warning("unmount(): Failed to unmount "+mount_point+"!")

    #Return the return value
    return ret_val

def update_chroot_mtab(mount_point):
    """Update /etc/mtab inside a chroot, so the list of mounted filesystems is always right."""
    logger.debug("update_chroot_mtab(): Updating /etc/mtab for chroot at: "+mount_point+"...")

    retval = start_process("cp -vf /proc/self/mounts "+mount_point+"/etc/mtab", show_output=False)

    if retval != 0:
        logger.warning("update_chroot_mtab(): Failed to run command: cp -vf /proc/self/mounts "+mount_point+"/etc/mtab! Chroot may not set up properly! This *probably* doesn't matter, but in rare situations it could cause problems. If the chrooted OS is Fedora-based, this is normal because /etc/mtab is a symlink to /proc/self/mounts.")

    logger.debug("update_chroot_mtab(): Finished updating /etc/mtab for chroot at: "+mount_point+".")

def setup_chroot(mount_point):
    """Set up a chroot for the given mountpoint."""
    logger.debug("setup_chroot(): Setting up chroot for mount_point: "+mount_point+"...")

    #Mount /dev, /dev/pts, /proc and /sys for the chroot.
    #We might also need internet access in chroot, so to do this first backup mount_point/etc/resolv.conf to mount_point/etc/resolv.conf.bak (if it's a link, this will also preserve it),
    #then copy current system's /etc/resolv.conf (the contents, not the link) to mount_point/etc/resolv.conf, enabling internet access.

    mount_list = ("/dev", "/dev/pts", "/proc", "/sys")

    for file_system in mount_list:
        if mount_partition(partition=file_system, mount_point=mount_point+file_system, options="--bind") != 0:
            logger.error("setup_chroot(): Failed to bind "+file_system+" to "+mount_point+file_system+"! Chroot isn't set up properly! Attempting to continue anyway...")

    exec_list = ("mv -vf "+mount_point+"/etc/resolv.conf "+mount_point+"/etc/resolv.conf.bak", "cp -fv /etc/resolv.conf "+mount_point+"/etc/resolv.conf")

    for exec_cmd in exec_list:
        ret_val = start_process(exec_cmd, show_output=False, return_output=True)[0]

        if ret_val != 0:
            logger.error("setup_chroot(): Error: Failed to run command: '"+exec_cmd+"'! Chroot may not be set up properly! On Fedora systems this probably doesn't matter. Continuing anyway...")
            #Ignore these errors, the only happen on Fedora and they don't really matter.
            ret_val = 0

    update_chroot_mtab(mount_point=mount_point)

    logger.debug("setup_chroot(): Finished setting up chroot for mount_point: "+mount_point+"...")
    return ret_val

def teardown_chroot(mount_point):
    """Remove a chroot at the given mountpoint."""
    logger.debug("teardown_chroot(): Removing chroot at mount_point: "+mount_point+"...")

    #unmount /dev/pts, /dev, /proc and /sys in the chroot.
    unmount_list = (mount_point+"/dev/pts", mount_point+"/dev", mount_point+"/proc", mount_point+"/sys")

    for file_system in unmount_list:
        if unmount(file_system) != 0:
            logger.error("teardown_chroot(): Faied to unmount "+file_system+"! Chroot isn't removed properly! Attempting to continue anyway...")

    #We'll also need to replace the mount_point/etc/resolv.conf with the backup file, mount_point/etc/resolv.conf.bak.
    ret_val = start_process("mv -vf "+mount_point+"/etc/resolv.conf.bak "+mount_point+"/etc/resolv.conf", show_output=False)

    if ret_val != 0:
        logger.error("teardown_chroot(): Failed to run command: 'mv -vf "+mount_point+"/etc/resolv.conf.bak "+mount_point+"/etc/resolv.conf'! Return value was: "+unicode(ret_val)+". Chroot may not be removed properly!")

    logger.debug("teardown_chroot(): Finished removing chroot at mount_point: "+mount_point+"...")
    return ret_val

def emergency_exit(message):
    """Handle emergency exits. Warn the user, log, and exit to terminal with the given message"""
    logger.critical("emergency_exit(): Emergency exit has been triggered! Giving user message dialog and saving the logfile...")
    logger.critical("emergency_exit(): The error is: "+message)

    #Warn the user.
    DialogTools.show_msg_dlg(message="Emergency exit triggered.\n\n"+message+"\n\nYou'll now be asked for a location to save the log file.\nIf you email me at hamishmb@live.co.uk with the contents of that file I'll be happy to help you fix this problem.", kind="error")

    #Shut down the logger.
    logging.shutdown()

    #Save the log file.
    log_file = DialogTools.show_save_file_dlg(wildcard="Log Files|*.log")
    start_process("mv -v /tmp/wxfixboot.log "+log_file, show_output=False)

    #If we're using wayland, remove the workaround we have to use to make this work.
    #XXX Fix for running on Wayland until we get policy kit stuff done.
    try:
        subprocess.check_call("xhost -si:localuser:root", shell=True)

    except subprocess.CalledProcessError:
        pass

    #Exit.
    DialogTools.show_msg_dlg(message="Done. WxFixBoot will now exit.")
    wx.Exit()
    sys.stdout.write(message+"\n")
    os._exit(1) #TODO Is there a better alternative that will work from a thread?
