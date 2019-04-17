#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Core Tools in the Tools Package for WxFixBoot
# This file is part of WxFixBoot.
# Copyright (C) 2013-2019 Hamish McIntyre-Bhatty
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

"""
This module contains the "core tools" used in various parts of WxFixBoot.
"""

#Do future imports to prepare to support python 3. Use unicode strings rather than ASCII
#strings, as they fix potential problems.
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

#Import modules.
import subprocess
import sys
import time
import logging
import os
import shlex
import wx

#Import other modules.
from . import dialogtools as DialogTools

#Make unicode an alias for str in Python 3.
if sys.version_info[0] == 3:
    unicode = str #pylint: disable=redefined-builtin,invalid-name
    str = bytes #pylint: disable=redefined-builtin,invalid-name

#Set up logging.
logger = logging.getLogger(__name__)
logger.setLevel(logging.getLogger("WxFixBoot").getEffectiveLevel())

#Define global variables
STARTUP = None

def get_helper(cmd):
    """Figure out which helper script to use."""
    helper = "/usr/share/wxfixboot/Tools/helpers/runasroot_linux.sh"

    if "run_getdevinfo.py" in cmd:
        helper = "/usr/share/wxfixboot/Tools/helpers/runasroot_linux_getdevinfo.sh"

    elif "umount" in cmd or "kpartx -d" in cmd:
        helper = "/usr/share/wxfixboot/Tools/helpers/runasroot_linux_umount.sh"

    elif ("mount" in cmd or "kpartx -l" in cmd or "kpartx -a" in cmd or "lsblk" in cmd
          or "partprobe" in cmd):
        #Note: These are only used in the process of mounting files.
        helper = "/usr/share/wxfixboot/Tools/helpers/runasroot_linux_mount.sh"

    elif "pkexec /usr/share/wxfixboot/Tools/helpers/runasroot_linux_read_file.sh" in cmd:
        #No need to add a helper for this.
        return ""

    else:
        helper = "/usr/share/wxfixboot/Tools/helpers/runasroot_linux.sh"

    return "pkexec "+helper

def start_process(exec_cmds, show_output=True, return_output=False, testing=False, privileged=False):
    """Start a process given a string of commands to execute.
    show_output is boolean and specifies whether to show output in the outputbox (if exists) or
    not.

    return_output is boolean and specifies whether to return the output back to the caller or not.
    """

    #Save the command as it was passed, in case we need
    #to call recursively (pkexec auth failure/dismissal).
    origcmds = exec_cmds

    #If this is to be a privileged process, add the helper script to the cmdline.
    if privileged:
        helper = get_helper(exec_cmds)

        exec_cmds = helper+" "+exec_cmds

    #Make sure output is always in English.
    environ = dict(os.environ, LC_ALL="C")

    exec_cmds = shlex.split(exec_cmds)

    #Run the command(s).
    logger.debug("start_process(): Starting process: "+' '.join(exec_cmds))
    cmd = subprocess.Popen(exec_cmds, stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT, env=environ,
                           shell=False)

    #Use a simpler output reader on startup to improve performance.
    if STARTUP:
        line_list = read(cmd, testing=testing)

    else:
        line_list = read_and_send_output(cmd, show_output)

    #Save runcmd.returncode, as it tends to reset fairly quickly.
    ret_val = int(cmd.returncode)

    #Log this info in a debug message.
    logger.debug("start_process(): Process: "+' '.join(exec_cmds)
                 +": Return Value: "+unicode(ret_val)
                 + ", Output: \"\n\n"+'\n'.join(line_list)+"\"\n")

    #Handle these error codes if pkexec is being used.
    #When commands are not found, we get the same codes - potential for infinite recursion here... XXX
    if privileged and (ret_val in (126, 127)) and "pkexec" in exec_cmds and "chroot" not in exec_cmds \
        and "lsb_release" not in exec_cmds:
        #Try again, auth dismissed / bad password 3 times.
        #A lot of recursion is allowed (~1000 times), so this shouldn't be a problem.
        logger.debug("start_process(): Bad auth or dismissed by user. Trying again...")
        return start_process(exec_cmds=origcmds, show_output=show_output,
                             return_output=return_output, testing=testing,
                             privileged=privileged)

    if return_output is False:
        #Return the return code back to whichever function ran this process, so it can handle
        #any errors.
        return ret_val

    elif testing:
        #Return the return code, as well as the output (not joining on newlines).
        return (ret_val, ''.join(line_list))

    #Otherwise, just return the return code, as well as the output.
    return (ret_val, '\n'.join(line_list))

def read(cmd, testing=False):
    """
    Read the cmd's output char by char, but do as little processing as possible to improve
    startup performance
    """

    #Get ready to run the command(s). Read up to 100 empty "" characters after the process finishes
    #to make sure we get all the output.
    counter = 0
    line = str(b"")
    line_list = []

    while cmd.poll() is None or counter < 100:
        char = cmd.stdout.read(1)

        if char == b"":
            counter += 1
            continue

        line += char

        if char in (b"\n", b"\r"):
            #Interpret as Unicode and remove "NULL" characters.
            line = line.decode("UTF-8", errors="ignore").replace("\x00", "")

            if testing:
                line_list.append(line)

            else:
                line_list.append(line.replace("\n", "").replace("\r", ""))

            #Reset line.
            line = str(b"")

    #Catch it if there's not a newline at the end.
    if line != b"":
        #Interpret as Unicode and remove "NULL" characters.
        line = line.decode("UTF-8", errors="ignore").replace("\x00", "")

        if testing:
            line_list.append(line)

        else:
            line_list.append(line.replace("\n", "").replace("\r", ""))

    return line_list

def read_and_send_output(cmd, show_output):
    """Read the cmd's output char by char, and send the output to the output box"""
    #Get ready to run the command(s). Read up to 100 empty "" characters after the process finishes
    #to make sure we get all the output.
    counter = 0
    line = str(b"")
    line_list = []
    hold = False
    send_line = False

    while cmd.poll() is None or counter < 100:
        char = cmd.stdout.read(1)

        if char == b"":
            counter += 1
            continue

        line += char

        if hold:
            #Check if this char is \n.
            if char == b"\n":
                #Send the line as is but replace \r\n with \n.
                line = str(line.replace(b"\r\n", b"\n"))

            else:
                #Send the line as is.
                send_line = True

            hold = False

        if char in (b"\n", b"\x08") or send_line:
            #Interpret as Unicode and remove "NULL" characters.
            line = line.decode("UTF-8", errors="ignore").replace("\x00", "")

            wx.CallAfter(wx.GetApp().TopWindow.update_output_box, line, show_output)
            line_list.append(line.replace("\n", "").replace("\r", "").replace("\x08", ""))

            #Reset line.
            line = str(b"")
            send_line = False

        elif char == b"\r":
            #Take the next character too in case it's \n, so we can just handle \r\n as \n.
            hold = True

    #Catch it if there's not a newline at the end.
    if line != b"":
        #Interpret as Unicode and remove "NULL" characters.
        line = line.decode("UTF-8", errors="ignore").replace("\x00", "")

        wx.CallAfter(wx.GetApp().TopWindow.update_output_box, line, show_output)
        line_list.append(line.replace("\n", "").replace("\r", "").replace("\x08", ""))

    return line_list

def read_privileged_file(filename):
    """
    Uses start_process() and a helper script to read privileged files
    and returns the content as a string.
    """

    return start_process("pkexec /usr/share/wxfixboot/Tools/helpers/runasroot_linux_read_file.sh "+filename,
                         show_output=False, return_output=True, privileged=True)[1].split("\n")

def write_privileged_file(filename, file_contents):
    """
    Uses start_process() and a helper script to write privileged files.
    This is an inherent security risk, but is needed to write bootloader
    configuration. So, there is a hardcoded whitelist of files we're
    allowed to write to here to mitigate at least some of that risk.

    This isn't an exact match thing, because these files might be within
    mountpoints. We will nevertheless match as exactly as we can.

    A few different checks are done to ensure that we are allowed to
    modify this file, just in case the program does something weird.

    The helper script is run through polkit, for security.
    """

    allowed_files = \
    ["/etc/default/grub",
     "/boot/grub/grub.cfg",
     "/boot/grub2/grub.cfg",
     "/boot/efi/EFI/fedora/grub.cfg",
     "/etc/lilo.conf",
     "/etc/elilo.conf"]

    #Try to sanitize the filename argument as much as possible, as get as close a match
    #as we can.
    #There should never be spaces in this filename, or in the path.
    if " " in filename:
        logger.error("write_privileged_file(): File contains spaces, rejecting...")
        return 1

    #Check that this is in the list of allowed files.
    allowed = False

    #Only allow this file if it is in the list. NB: We're checking this way
    #because of mountpoints - we might not be modifying the root FS.
    for name in allowed_files:
        if name == filename:
            #We're modifying this on rootfs.
            allowed = True

        elif name in filename and "/tmp/wxfixboot/mountpoints" in filename:
            #We're modifying this on a different filesystem that wxfixboot mounted.
            allowed = True

    if not allowed:
        logger.error("write_privileged_file(): File not allowed, or in disallowed filesystem, "
                     + "rejecting...")
        return 1

    #Okay, we should be alright now.
    logger.info("write_privileged_file(): Writing to "+filename+", writing:\n\n"
                + file_contents+"\n\n...")

    #Start the process.
    cmd = subprocess.Popen("pkexec /usr/share/wxfixboot/Tools/helpers/runasroot_linux_write_file.sh "
                           + filename, stdin=subprocess.PIPE, shell=True)

    #Write the file contents to its stdin, plus EOF.
    cmd.stdin.write(file_contents.encode("UTF-8", errors="ignore")+str(b"\nEOF"))
    cmd.stdin.flush()
    cmd.stdin.close()

    #Wait for it to finish.
    while cmd.poll() is None:
        time.sleep(0.5)

    logger.info("write_privileged_file(): Done.")

    return 0

def is_mounted(partition, mount_point=None):
    """
    Checks if the given partition is mounted.
    partition is the given partition to check.
    If mount_point is specified, check if the partition is mounted there, rather than just if
    it's mounted.

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
    logger.info("get_partition_mounted_at(): Trying to get partition mounted at "+mount_point
                + "...")

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
        logger.info("mount_partition(): Preparing to mount "+partition+" at "+mount_point
                    + " with extra options "+options+"...")

    else:
        logger.info("mount_partition(): Preparing to mount "+partition+" at "+mount_point
                    + " with no extra options...")

    mount_info = start_process("mount -l", show_output=False, return_output=True)[1]

    #There is a partition mounted here. Check if our partition is already mounted in the right
    #place.
    if mount_point == get_mount_point_of(partition):
        #The correct partition is already mounted here.
        logger.debug("mount_partition(): partition: "+partition+" was already mounted at: "
                     + mount_point+". Continuing...")
        return 0

    elif mount_point in mount_info:
        #Something else is in the way. unmount that partition, and continue.
        logger.warning("mount_partition(): unmounting filesystem in the way at "+mount_point
                       + "...")

        ret_val = unmount(mount_point)

        if ret_val != 0:
            logger.error("mount_partition(): Couldn't unmount "+mount_point
                         +", preventing the mounting of "+partition+"! Skipping mount attempt.")
            return False

    #Create the dir if needed. TODO What if we don't have permission?
    if os.path.isdir(mount_point) is False:
        os.makedirs(mount_point)

    #Mount the device to the mount point.
    ret_val = start_process("mount "+options+" "+partition+" "+mount_point,
                            show_output=False, privileged=True)

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
    ret_val = start_process("mount -o remount,"+mode+" "+partition,
                            show_output=False, privileged=True)

    if ret_val == 0:
        logger.warning("remount_partition(): Successfully remounted partition!")

    else:
        logger.info("remount_partition(): Failed to remount partition!")

    #Return the return value
    return ret_val

def unmount(mount_point):
    """
    Unmounts the given mountpoint.
    mount_point is the mountpoint to unmount.
    mount_point can also be a partition name (for example /dev/sda1).
    """
    logger.debug("unmount(): Preparing to unmount "+mount_point)

    if mount_point not in start_process("mount -l", show_output=False, return_output=True)[1]:
        logger.info("unmount(): "+mount_point+" was not mounted. Continuing...")
        ret_val = 0

    else:
        logger.debug("unmount(): unmounting "+mount_point+"...")
        ret_val = start_process("umount "+mount_point, show_output=False, privileged=True)

        if ret_val == 0:
            logger.info("unmount(): Successfully unmounted "+mount_point+"!")

        else:
            logger.warning("unmount(): Failed to unmount "+mount_point+"!")

    #Return the return value
    return ret_val

def update_chroot_mtab(mount_point):
    """Update /etc/mtab inside a chroot, so the list of mounted filesystems is always right."""
    logger.debug("update_chroot_mtab(): Updating /etc/mtab for chroot at: "+mount_point+"...")

    retval = start_process("cp -vf /proc/self/mounts "+mount_point+"/etc/mtab",
                           show_output=False, privileged=True)

    if retval != 0:
        logger.warning("update_chroot_mtab(): Failed to run command: cp -vf /proc/self/mounts "
                       + mount_point+"/etc/mtab! Chroot may not set up properly! This *probably* "
                       + "doesn't matter, but in rare situations it could cause problems. If the "
                       + "chrooted OS is Fedora-based, this is normal because /etc/mtab is a "
                       + "symlink to /proc/self/mounts.")

    logger.debug("update_chroot_mtab(): Finished updating /etc/mtab for chroot at: "
                 + mount_point+".")

def setup_chroot(mount_point):
    """Set up a chroot for the given mountpoint."""
    logger.debug("setup_chroot(): Setting up chroot for mount_point: "+mount_point+"...")

    #Mount /dev, /dev/pts, /proc and /sys for the chroot.
    #We might also need internet access in chroot, so to do this first backup
    #mount_point/etc/resolv.conf to mount_point/etc/resolv.conf.bak (if it's a link, this
    #will also preserve it), then copy current system's /etc/resolv.conf (the contents, not
    #the link) to mount_point/etc/resolv.conf, enabling internet access.

    mount_list = ("/dev", "/dev/pts", "/proc", "/sys")

    for file_system in mount_list:
        if mount_partition(partition=file_system, mount_point=mount_point+file_system, options="--bind") != 0:
            logger.error("setup_chroot(): Failed to bind "+file_system+" to "+mount_point
                         + file_system+"! Chroot isn't set up properly! Attempting to continue "
                         + "anyway...")

    exec_list = ("mv -vf "+mount_point+"/etc/resolv.conf "+mount_point+"/etc/resolv.conf.bak",
                 "cp -fv /etc/resolv.conf "+mount_point+"/etc/resolv.conf")

    for exec_cmd in exec_list:
        ret_val = start_process(exec_cmd, show_output=False, return_output=True,
                                privileged=True)[0]

        if ret_val != 0:
            logger.error("setup_chroot(): Error: Failed to run command: '"+exec_cmd
                         + "'! Chroot may not be set up properly! On Fedora systems this probably "
                         + "doesn't matter. Continuing anyway...")

            #Ignore these errors, the only happen on Fedora and they don't really matter.
            ret_val = 0

    update_chroot_mtab(mount_point=mount_point)

    logger.debug("setup_chroot(): Finished setting up chroot for mount_point: "+mount_point+"...")
    return ret_val

def teardown_chroot(mount_point):
    """Remove a chroot at the given mountpoint."""
    logger.debug("teardown_chroot(): Removing chroot at mount_point: "+mount_point+"...")

    #unmount /dev/pts, /dev, /proc and /sys in the chroot.
    unmount_list = (mount_point+"/dev/pts", mount_point+"/dev", mount_point+"/proc",
                    mount_point+"/sys")

    for file_system in unmount_list:
        if unmount(file_system) != 0:
            logger.error("teardown_chroot(): Faied to unmount "+file_system
                         + "! Chroot isn't removed properly! Attempting to continue anyway...")

    #We'll also need to replace the mount_point/etc/resolv.conf with the backup file,
    #mount_point/etc/resolv.conf.bak.
    ret_val = start_process("mv -vf "+mount_point+"/etc/resolv.conf.bak "+mount_point
                            + "/etc/resolv.conf", show_output=False, privileged=True)

    if ret_val != 0:
        logger.error("teardown_chroot(): Failed to run command: 'mv -vf "+mount_point
                     + "/etc/resolv.conf.bak "+mount_point+"/etc/resolv.conf'! Return value was: "
                     + unicode(ret_val)+". Chroot may not be removed properly!")

    logger.debug("teardown_chroot(): Finished removing chroot at mount_point: "+mount_point+"...")
    return ret_val

def send_notification(msg):
    """Send a notification, created to reduce clutter in the rest of the code."""
    #Use notify-send.
    start_process(exec_cmds="notify-send 'WxFixBoot' '"+msg
                  +"' -i /usr/share/pixmaps/wxfixboot.png", return_output=False)

def emergency_exit(message):
    """Handle emergency exits. Warn the user, log, and exit to terminal with the given message"""
    logger.critical("emergency_exit(): Emergency exit has been triggered! Giving user message "
                    + "dialog and saving the logfile...")

    logger.critical("emergency_exit(): The error is: "+message)

    #Warn the user.
    DialogTools.show_msg_dlg(message="Emergency exit triggered.\n\n"+message
                             + "\n\nYou'll now be asked for a location to save the log file.\n"
                             + "If you email me at hamishmb@live.co.uk with the contents of that "
                             + "file I'll be happy to help you fix this problem.", kind="error")

    #Shut down the logger.
    logging.shutdown()

    #Save the log file.
    log_file = DialogTools.show_save_file_dlg(wildcard="Log Files|*.log")
    start_process("mv -v /tmp/wxfixboot.log "+log_file, show_output=False)

    #Exit.
    DialogTools.show_msg_dlg(message="Done. WxFixBoot will now exit.")
    wx.Exit()
    sys.stdout.write(message+"\n")
    os._exit(1) #TODO Is there a better alternative that will work from a thread?
