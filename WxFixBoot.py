#!/usr/bin/env python
# -*- coding: utf-8 -*-
# WxFixBoot Version 3.0.0
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

#Do future imports to continue python 2 support.
#Use unicode strings rather than ASCII strings, as they fix potential problems.
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

#Import other modulesS
import traceback
import threading
import subprocess
import sys
import getopt
import logging
import os
import shutil
import time
import plistlib

import wx
import wx.html
import wx.lib.statbmp
import wx.lib.stattext

#Compatibility with wxPython 4.
if int(wx.version()[0]) >= 4:
    import wx.adv
    from wx.adv import AboutDialogInfo as wxAboutDialogInfo #pylint: disable=no-name-in-module
    from wx.adv import AboutBox as wxAboutBox #pylint: disable=no-name-in-module

else:
    from wx import AboutDialogInfo as wxAboutDialogInfo #pylint: disable=no-name-in-module
    from wx import AboutBox as wxAboutBox #pylint: disable=no-name-in-module

import getdevinfo
import getdevinfo.linux

#Make unicode an alias for str in Python 3.
if sys.version_info[0] == 3:
    #Disable cos necessary to keep supporting python 2.
    unicode = str #pylint: disable=redefined-builtin,invalid-name

    #Plist hack for Python 3.
    plistlib.readPlistFromString = plistlib.loads #pylint: disable=no-member
    plistlib.writePlist = plistlib.dump #pylint: disable=no-member

#Define the version number and the release date as global variables.
VERSION = "3.0.0"
RELEASEDATE = "18/9/2018"

#Define other global variables.
SESSION_ENDING = False
CLASSIC_WXPYTHON = int(wx.version()[0]) < 4
APPICON = None
OUTPUT_LOG = None
OPERATIONS = None
NUMBER_OF_OPERATIONS = None
STOP_PROGRESSTEXT_HANDLER_THREAD = None

def usage():
    print("\nUsage: WxFixBoot.py [OPTION]\n")
    print("       -h, --help:                   Show this help message")
    print("       -q, --quiet:                  Show only warning, error and critical messages in the log file. Very unhelpful for debugging, and not recommended.")
    print("       -v, --verbose:                Enable logging of info messages, as well as warnings, errors and critical errors.")
    print("                                     Not the best for debugging, but acceptable if there is little disk space.")
    print("       -d, --debug:                  Log lots of boring debug messages, as well as information, warnings, errors and critical errors. Usually used for diagnostic purposes.")
    print("                                     The default, as it's very helpful if problems are encountered, and the user needs help\n")
    print("WxFixBoot "+VERSION+" is released under the GNU GPL Version 3")
    print("Copyright (C) Hamish McIntyre-Bhatty 2013-2018")

#If this isn't running as root, relaunch.
if not os.geteuid() == 0:
    subprocess.Popen(["/usr/share/wxfixboot/AuthenticationDialog.py"])
    sys.exit("\nSorry, WxFixBoot must be run with root privileges. "
             + "\nRestarting as Root...")

#Set up according to cmdline options.
try:
    OPTIONS = getopt.getopt(sys.argv[1:], "hqvd", ("help", "quiet", "verbose", "debug"))[0]

except getopt.GetoptError as err:
    #Invalid option. Show the help message and then exit.
    #Show the error.
    print(unicode(err))
    usage()
    sys.exit(2)

#Set up logging.
logger = logging.getLogger('WxFixBoot '+VERSION)
logging.basicConfig(filename='/tmp/wxfixboot.log',
                    format='%(asctime)s - %(name)s - %(levelname)s: %(message)s',
                    datefmt='%d/%m/%Y %I:%M:%S %p')

logger.setLevel(logging.DEBUG)

#Set restarting to false.
RESTARTING = False

#Determine the option(s) given, and change the level of logging based on cmdline options.
for OPTION, ARGUMENT in OPTIONS:
    if OPTION in ("-q", "--quiet"):
        logger.setLevel(logging.WARNING)

    elif OPTION in ("-v", "--verbose"):
        logger.setLevel(logging.INFO)

    elif OPTION in ("-d", "--debug"):
        logger.setLevel(logging.DEBUG)

    elif OPTION in ("-h", "--help"):
        usage()
        sys.exit()

    else:
        assert False, "unhandled option"

#Import custom-made modules
import Tools
from Tools.dictionaries import *
import Tools.coretools as CoreTools
import Tools.dialogtools as DialogTools
import Tools.StartupTools.main as MainStartupTools
import Tools.BackendTools.essentials as EssentialBackendTools
import Tools.BackendTools.main as MainBackendTools

import SystemInfoNoteBookSharedFunctions as NoteBookSharedFunctions

#Begin Disk Information Handler thread.
class GetDiskInformation(threading.Thread): #TODO Is this needed?
    def __init__(self):
        """Initialize and start the thread."""
        self.parent_window = wx.GetApp().TopWindow
        threading.Thread.__init__(self)
        self.start()

    def run(self):
        """Get Disk Information and return it as a list with embedded lists"""
        #Use a module I've written to collect data about connected Disks, and return it.
        wx.CallAfter(self.parent_window.ReceiveDiskInfo, getdevinfo.getdevinfo.get_info())

#End Disk Information Handler thread.
#Begin Starter Class
class WxFixBoot(wx.App):
    def OnInit(self): #pylint: disable=invalid-name
        """Starts InitialWindow()"""
        InitialWindow().Show()
        return True

#End Starter Class
#Begin Initialization Panel.
class InitialPanel(wx.Panel):
    def __init__(self, parent):
        """Initialises the panel"""
        wx.Panel.__init__(self, parent=parent)
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
        self.frame = parent
        self.Bind(wx.EVT_PAINT, self.on_erase_background)

    def on_erase_background(self, event): #pylint: disable=unused-argument
        """Redraw the background image when needed"""
        _dc = wx.ClientDC(self)

        if CLASSIC_WXPYTHON:
            _dc.SetClippingRect(self.GetUpdateRegion().GetBox())

        else:
            _dc.SetClippingRegion(self.GetUpdateRegion().GetBox())

        _dc.Clear()
        splash = wx.Bitmap("/usr/share/wxfixboot/images/splash.png")
        _dc.DrawBitmap(splash, 0, 0)

#End Initialization Panel.
#Begin Initialization Frame.
class InitialWindow(wx.Frame):
    def __init__(self):
        """Initialises InitialWindow"""
        wx.Frame.__init__(self, parent=None, title="WxFixBoot",
                          size=(600, 420), style=wx.SIMPLE_BORDER)

        self.panel = InitialPanel(self)
        self.SetClientSize(wx.Size(600, 420))

        if RESTARTING is False:
            print("WxFixBoot Version "+VERSION+" Starting...")
            logger.info("WxFixBoot Version "+VERSION+" Starting...")

        else:
            print("WxFixBoot Version "+VERSION+" Restarting...")
            logger.info("WxFixBoot Version "+VERSION+" Restarting...")

        logger.info("Release date: "+RELEASEDATE)
        logger.info("Running on Python version: "+unicode(sys.version_info)+"...")
        logger.info("Running on wxPython version: "+wx.version()+"...")

        #Set the frame's icon.
        global APPICON
        APPICON = wx.Icon("/usr/share/wxfixboot/images/logo.png", wx.BITMAP_TYPE_PNG)
        wx.Frame.SetIcon(self, APPICON)

        #Create the progress bar and text.
        self.create_progress_bar_and_text()

        #Setup sizers.
        self.setup_sizers()

        #Start the Initalization Thread, which performs all necessary startup
        #scripts and checks, and let it know this is the first start.
        logger.debug("Starting InitThread()...")

        ProgressTextHandlerThread()
        InitThread()

    def create_progress_bar_and_text(self):
        """Create a progressbar and some progress text"""
        self.progress_bar = wx.Gauge(self.panel, -1, 100)
        self.progress_bar.SetBezelFace(3)
        self.progress_bar.SetShadowWidth(3)
        self.progress_bar.SetValue(0)
        self.progress_bar.Show()

        #Create the progress text.
        self.progress_text = wx.StaticText(self.panel, -1, "Initialising...")

    def setup_sizers(self):
        """Setup sizers for InitialWindow"""
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add((50, 50), 10, wx.EXPAND)
        main_sizer.Add(self.progress_text, 1, wx.CENTER|wx.BOTTOM|wx.LEFT|wx.RIGHT, 10)
        main_sizer.Add(self.progress_bar, 1, wx.BOTTOM|wx.LEFT|wx.RIGHT|wx.EXPAND, 10)

        #Get the sizer set up for the frame.
        self.panel.SetSizer(main_sizer)
        main_sizer.SetMinSize(wx.Size(600, 420))
        main_sizer.SetSizeHints(self)

    def update_progress_bar(self, value):
        """Update the progress bar with the given value"""
        self.progress_bar.SetValue(int(value))

        if int(value) == 100:
            global STOP_PROGRESSTEXT_HANDLER_THREAD
            STOP_PROGRESSTEXT_HANDLER_THREAD = True
            self.finished_startup()

    def update_progress_text(self, message):
        """Call the text handler thread to distract the user"""
        self.progress_text.SetLabel(message)
        self.panel.Layout()

    def set_progress_text(self, message):
        """Update the progress text with the given string"""
        self.progress_text.SetLabel(message)
        self.panel.Layout()

    def finished_startup(self, event=None): #pylint: disable=unused-argument
        """Starts MainWindow, called when StartupScripts are finished"""
        logger.info("Closing Initial Window and Starting Main Window...")

        #Show the user some important information
        dlg = wx.MessageDialog(self.panel, "Please make sure you have a working "
                               + "internet connection before performing any "
                               + "bootloader operations. Thank you.",
                               "WxFixBoot - Information",
                               style=wx.OK | wx.ICON_INFORMATION,
                               pos=wx.DefaultPosition)

        dlg.ShowModal()
        dlg.Destroy()

        main_gui = MainWindow()
        APP.SetTopWindow(main_gui)
        self.Destroy()

        #Start MainFrame.
        main_gui.Show(True)

#End Initialization Frame.
#Begin Progress Text Handler Thread.
class ProgressTextHandlerThread(threading.Thread):
    def __init__(self):
        """Start the Thread"""
        threading.Thread.__init__(self)
        self.parent_window = wx.GetApp().TopWindow

        global STOP_PROGRESSTEXT_HANDLER_THREAD
        STOP_PROGRESSTEXT_HANDLER_THREAD = False

        self.start()

    def run(self):
        """Distract the user with some text effects on the Initial Window.
        For 10 seconds of the same message, make dots build up to 3 dots and back after the text.
        After 10 seconds of same message, state that WxFixBoot is still starting up,
        and to be patient."""

        half_second_counter = 0
        message = ""

        while True:
            if STOP_PROGRESSTEXT_HANDLER_THREAD:
                break

            if half_second_counter == 20:
                message = message.replace(".", "")+". This may take a few minutes. Please be patient."
                wx.CallAfter(self.parent_window.set_progress_text, message)
                time.sleep(0.5)
                half_second_counter += 1

            else:
                last_message = message

                message = self.parent_window.progress_text.GetLabel()

                if message == last_message:
                    half_second_counter += 1

                else:
                    half_second_counter == 0

                if message[-3:] == "...":
                    message = message[0:-3]

                message = message+"."
                wx.CallAfter(self.parent_window.set_progress_text, message)
                time.sleep(0.5)

#End Progress Text Handler Thread.
#Begin Initialization Thread.
class InitThread(threading.Thread):
    def __init__(self):
        """Start the thread."""
        #Initialize the thread.
        threading.Thread.__init__(self)
        self.parent_window = wx.GetApp().TopWindow

        #Start the thread.
        self.start()

    def run(self):
        """Handle errors in the main thread code"""
        logger.debug("InitThread(): Starting...")

        #Handle any unexpected errors.
        try:
            self.main_code()

        except Exception:
            logger.critical("Unexpected error \n\n"
                            + unicode(traceback.format_exc())
                            + "\n\n while starting WxFixBoot. "
                            + "Warning user and exiting.")

            CoreTools.emergency_exit("There was an unexpected error: \n\n"
                                     + unicode(traceback.format_exc())
                                     + "\n\nWhile starting up!")

    def main_code(self):
        """Create the temporary mount point folder and set some default settings."""
        global SYSTEM_INFO
        global SETTINGS
        global DISK_INFO
        global OS_INFO

        #Let CoreTools know we're starting up.
        Tools.coretools.startup = True

        #Set variables used for checking whether bootloader operations have been disabled.
        SYSTEM_INFO["DisableBootloaderOperations"] = False
        SYSTEM_INFO["DisableBootloaderOperationsBecause"] = []

        #Initialise a variable for later.
        SYSTEM_INFO["PreviousOSChoice"] = ""

        #Set initial settings for MainWindow.
        SETTINGS["QuickFSCheck"] = False
        SETTINGS["BadSectorCheck"] = False
        SETTINGS["FullVerbosity"] = False
        SETTINGS["MakeSystemSummary"] = True
        SETTINGS["SaveOutput"] = True

        #Remove the temporary directory if it exists.
        if os.path.isdir("/tmp/wxfixboot/mountpoints"):
            #Check nothing is using it.
            if "/tmp/wxfixboot/mountpoints" in CoreTools.start_process("mount", return_output=True)[1]:
                CoreTools.emergency_exit("There are mounted filesystems in "
                                         + "/tmp/wxfixboot/mountpoints, WxFixBoot's temporary "
                                         + "mountpoints directory! Please unmount any filesystems "
                                         + "there and try again.") #FIXME Handle this automatically if possible.

            shutil.rmtree("/tmp/wxfixboot/mountpoints")

        os.makedirs("/tmp/wxfixboot/mountpoints")

        #Check for dependencies
        logger.info("InitThread(): Checking For Dependencies...")
        wx.CallAfter(self.parent_window.update_progress_text, "Checking For Dependencies...")
        MainStartupTools.check_depends()
        wx.CallAfter(self.parent_window.update_progress_bar, "2")
        logger.info("InitThread(): Done Checking For Dependencies!")

        #Check if we're on a Live Disk.
        logger.info("InitThread(): Checking For Live Disk...")
        wx.CallAfter(self.parent_window.update_progress_text, "Checking For Live Disk...")
        MainStartupTools.check_for_live_disk()
        wx.CallAfter(self.parent_window.update_progress_bar, "4")
        logger.info("InitThread(): Done Checking For Live Disk!")

        #Unmount all filesystems, to avoid any data corruption.
        logger.info("InitThread(): Unmounting Filesystems...")
        wx.CallAfter(self.parent_window.update_progress_text, "Unmounting Filesystems...")
        MainStartupTools.unmount_all_filesystems()
        wx.CallAfter(self.parent_window.update_progress_bar, "5")
        logger.info("InitThread(): Done Unmounting Filsystems!")

        #Check filesystems.
        logger.info("InitThread(): Checking Filesystems...")
        wx.CallAfter(self.parent_window.update_progress_text, "Checking Filesystems...")
        MainStartupTools.check_filesystems()
        wx.CallAfter(self.parent_window.update_progress_bar, "15")
        logger.info("InitThread(): Filesystems Checked!")

        #Get device info.
        logger.info("InitThread(): Getting Device Information...")
        wx.CallAfter(self.parent_window.update_progress_text, "Getting Device Information...")

        DISK_INFO.update(getdevinfo.getdevinfo.get_info())

        wx.CallAfter(self.parent_window.update_progress_bar, "60")
        logger.info("InitThread(): Finished Getting Device Information...")

        #Mount all filesystems.
        logger.info("InitThread(): Mounting Core Filesystems...")
        wx.CallAfter(self.parent_window.update_progress_text, "Mounting Core Filesystems...")
        MainStartupTools.mount_core_filesystems()
        wx.CallAfter(self.parent_window.update_progress_bar, "63")
        logger.info("InitThread(): Done Mounting Core Filsystems!")

        #Get a list of OSs.
        logger.info("InitThread(): Finding OSs...")
        wx.CallAfter(self.parent_window.update_progress_text, "Finding Operating Systems...")

        TEMP_OS_INFO, TEMP_SYSTEM_INFO = MainStartupTools.get_oss()
        OS_INFO.update(TEMP_OS_INFO)
        SYSTEM_INFO.update(TEMP_SYSTEM_INFO)

        wx.CallAfter(self.parent_window.update_progress_bar, "65")
        logger.info("InitThread(): Done Finding OSs...")

        #Get the firmware type.
        logger.info("InitThread(): Determining Firmware Type...")
        wx.CallAfter(self.parent_window.update_progress_text, "Determining Firmware Type...")
        MainStartupTools.get_firmware_type()
        wx.CallAfter(self.parent_window.update_progress_bar, "70")
        logger.info("InitThread(): Determined Firmware Type as: "+SYSTEM_INFO["FirmwareType"])

        #New bootloader info getting function.
        logger.info("InitThread(): Finding all Bootloaders and getting their settings...")
        wx.CallAfter(self.parent_window.update_progress_text, "Finding Bootloaders...")
        MainStartupTools.get_bootloaders()
        wx.CallAfter(self.parent_window.update_progress_bar, "80")
        logger.info("InitThread(): Done!")

        #Check if any modifyable Linux installations were found.
        if not SYSTEM_INFO["ModifyableOSs"]:
            logger.critical("InitThread(): No modifyable Linux installations found! If you think "
                            + "this is incorrect, please file a bug or ask a question on "
                            + "WxFixBoot's launchpad page. Exiting...")

            #Exit.
            CoreTools.emergency_exit("You don't appear to have any modifyable Linux installations "
                                     + "on your hard disks. If you think this is incorrect, "
                                     + "please file a bug or ask a question on WxFixBoot's "
                                     + "launchpad page.") #FIXME Link.

        #Perform final check.
        logger.info("InitThread(): Doing Final Check for error situations...")
        wx.CallAfter(self.parent_window.update_progress_text, "Checking Everything...")
        MainStartupTools.final_check()
        wx.CallAfter(self.parent_window.update_progress_bar, "100")
        logger.info("InitThread(): Done Final Check!")

        #Let CoreTools know we're finished starting up.
        Tools.coretools.startup = False

        wx.CallAfter(self.parent_window.update_progress_text, "Finished! Starting GUI...")
        logger.info("InitThread(): Finished Determining Settings. Exiting InitThread()...")

#End Initalization Thread.
#Begin Main Window
class MainWindow(wx.Frame):
    def __init__(self):
        """Initialise MainWindow"""
        wx.Frame.__init__(self, None, title="WxFixBoot", size=(400, 300),
                          style=wx.DEFAULT_FRAME_STYLE)

        self.panel = wx.Panel(self)
        self.SetClientSize(wx.Size(400, 300))

        #Set the frame's icon.
        wx.Frame.SetIcon(self, APPICON)

        #Create a Statusbar in the bottom of the window and set the text.
        self.make_status_bar()

        #Add text.
        self.create_text()

        #Create some buttons
        self.create_buttons()

        #Create some checkboxes
        self.create_checkboxes()

        #Create the menus.
        self.create_menus()

        #Set up checkboxes
        self.refresh_main_window()

        #Setup Sizers.
        self.setup_sizers()

        #Bind all events.
        self.bind_events()

        logger.debug("MainWindow().__init__(): Started. Waiting for events...")

    def make_status_bar(self):
        """Create the status bar"""
        self.statusbar = self.CreateStatusBar()
        self.StatusBar.SetFieldsCount(2)
        self.StatusBar.SetStatusWidths([-1, 150])
        self.StatusBar.SetStatusText("Ready.", 0)
        self.StatusBar.SetStatusText("v"+VERSION+" ("+RELEASEDATE+")", 1)

    def create_text(self):
        """Create the text"""
        self.settings_text = wx.StaticText(self.panel, -1,
                                           "Please set the basic settings here first.")

        self.welcome_text = wx.StaticText(self.panel, -1, "Welcome to WxFixBoot!")

        #Add an image.
        img = wx.Image("/usr/share/pixmaps/wxfixboot.png", wx.BITMAP_TYPE_PNG)

        if CLASSIC_WXPYTHON:
            self.logo = wx.StaticBitmap(self.panel, -1, wx.BitmapFromImage(img))

        else:
            self.logo = wx.StaticBitmap(self.panel, -1, wx.Bitmap(img))

    def create_buttons(self):
        """Create the buttons"""
        self.about_button = wx.Button(self.panel, wx.ID_ANY, "About")
        self.exit_button = wx.Button(self.panel, wx.ID_ANY, "Quit")
        self.bootloader_options_button = wx.Button(self.panel, -1, "Bootloader Options")
        self.apply_operations_button = wx.Button(self.panel, wx.ID_ANY, "Apply All Operations")

    def create_checkboxes(self):
        """Create the checkboxes"""
        self.bad_sector_check_check_box = wx.CheckBox(self.panel, -1,
                                                      "Check All File Systems (thorough)")

        self.check_filesystems_check_box = wx.CheckBox(self.panel, -1,
                                                       "Check All File Systems (quick)")

        self.fullverbose_checkbox = wx.CheckBox(self.panel, -1, "Show diagnostic terminal output")
        self.make_summary_check_box = wx.CheckBox(self.panel, -1, "Save System Report To File")
        self.log_output_checkbox = wx.CheckBox(self.panel, -1, "Save terminal output in Report")

    def create_menus(self):
        """Create the menus"""
        filemenu = wx.Menu()
        viewmenu = wx.Menu()
        editmenu = wx.Menu()
        helpmenu = wx.Menu() 
   
        #Adding Menu Items.
        self.menu_about = helpmenu.Append(wx.ID_ABOUT, "&About", "Information about this program")
        self.menu_exit = filemenu.Append(wx.ID_EXIT, "&Exit", "Terminate this program")
        self.menu_systeminfo = viewmenu.Append(wx.ID_ANY, "&System Information", "Information about all detected disks, OSs, and Bootloaders")
        self.menu_privacy_policy = viewmenu.Append(wx.ID_ANY, "&Privacy Policy",
                                                   "View WxFixBoot's privacy policy")

        self.menu_bootloader_options = editmenu.Append(wx.ID_PREFERENCES, "&Bootloader Options", "All Bootloader Options used to modify/fix your system")

        #Creating the menubar.
        menubar = wx.MenuBar()

        #Adding menus to the MenuBar
        menubar.Append(filemenu, "&File")
        menubar.Append(editmenu, "&Edit")
        menubar.Append(viewmenu, "&View")
        menubar.Append(helpmenu, "&Help")

        #Adding the MenuBar to the Frame content.
        self.SetMenuBar(menubar)

    def on_checkbox(self, event=None): #pylint: disable=unused-argument
        """
        Called when one of the checkboxes is checked/unchecked,
        to make sure the options stay valid
        """

        logger.debug("MainWindow().on_checkbox(): Checkboxes have been changed. "
                     + "Making sure options are valid and don't conflict...")

        #Bad Sector Check Choicebox
        if self.bad_sector_check_check_box.IsChecked():
            self.check_filesystems_check_box.Disable()

        else:
            self.check_filesystems_check_box.Enable()

        #Quick Disk Check Choicebox
        if self.check_filesystems_check_box.IsChecked():
            self.bad_sector_check_check_box.Disable()

        else:
            self.bad_sector_check_check_box.Enable()

        #Log output, and Make Summary checkboxes.
        if self.make_summary_check_box.IsChecked():
            self.log_output_checkbox.Enable()
            self.log_output_checkbox.SetValue(True)

        else:
            self.log_output_checkbox.SetValue(False)
            self.log_output_checkbox.Disable()

        logger.debug("MainWindow().on_checkbox(): Done. Calling self.save_main_options()...")
        self.save_main_options()

    def bootloader_options(self, event=None): #pylint: disable=unused-argument
        """Show the Bootloader Options Window"""
        #Safeguard program reliability (and continuity) by saving the settings first.
        logger.debug("MainWindow().bootloader_options(): Calling self.save_main_options()...")
        self.save_main_options()

        #Open the Bootloader Options window
        logger.debug("MainWindow().bootloader_options(): Starting Bootloader Settings Window...")
        self.Hide()
        BootloaderOptionsWindow().Show()

    def system_info(self, event=None): #pylint: disable=unused-argument
        """Start SystemInfoWindow"""
        logger.debug("MainWindow().system_info(): Starting System Info Window...")
        SystemInfoWindow().Show()

    def show_privacypolicy(self, event=None): #pylint: disable=unused-argument
        """Show PrivPolWindow"""
        PrivPolWindow().Show()

    def progress_window(self, event=None): #pylint: disable=unused-argument
        """Starts Progress Window"""
        logger.debug("MainWindow().progress_window(): Starting Progress Window...")
        self.save_main_options()
        progress_frame = ProgressWindow()
        APP.SetTopWindow(progress_frame)
        progress_frame.Show(True)
        self.Destroy()

    def refresh_main_window(self):
        """Refresh the main window to reflect changes in the options, or after a restart."""
        logger.debug("MainWindow().refresh_main_window(): Refreshing MainWindow...")

        self.check_filesystems_check_box.SetValue(SETTINGS["QuickFSCheck"])
        self.bad_sector_check_check_box.SetValue(SETTINGS["BadSectorCheck"])
        self.fullverbose_checkbox.SetValue(SETTINGS["FullVerbosity"])
        self.make_summary_check_box.SetValue(SETTINGS["MakeSystemSummary"])
        self.log_output_checkbox.SetValue(SETTINGS["SaveOutput"])

        #Enable and Disable Checkboxes as necessary
        self.on_checkbox()

        #Reveal MainWindow
        self.Show()

    def on_about(self, event=None): #pylint: disable=unused-argument
        """Shows the About Box"""
        logger.debug("MainWindow().on_about(): Showing About Box...")
        aboutbox = wxAboutDialogInfo()
        aboutbox.Name = "WxFixBoot"
        aboutbox.SetIcon(APPICON)
        aboutbox.Version = VERSION
        aboutbox.Copyright = "(C) 2013-2018 Hamish McIntyre-Bhatty"
        aboutbox.Description = "Utility to fix the bootloader on a\ncomputer quickly " \
                               + "\n\nPython version "+sys.version.split()[0] \
                               + "\nwxPython version " + wx.version()

        aboutbox.WebSite = ("https://www.hamishmb.com", "My Website")
        aboutbox.Developers = ["Hamish McIntyre-Bhatty"]
        aboutbox.Artists = ["Bhuna https://www.instagram.com/bhuna42/",
                            "Holly McIntyre-Bhatty (Old Artwork)"]

        aboutbox.License = "WxFixBoot is free software: you can redistribute it and/or modify it\nunder the terms of the GNU General Public License version 3 or,\nat your option, any later version.\n\nWxFixBoot is distributed in the hope that it will be useful,\nbut WITHOUT ANY WARRANTY; without even the implied warranty of\nMERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the\nGNU General Public License for more details.\n\nYou should have received a copy of the GNU General Public License\nalong with WxFixBoot.  If not, see <http://www.gnu.org/licenses/>."

        #Show the AboutBox.
        wxAboutBox(aboutbox)

    def setup_sizers(self):
        """Setup sizers for MainWindow"""
        #Create the main sizer.
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        #Create the check box and Logo sizer.
        checkbox_and_logo_sizer = wx.BoxSizer(wx.HORIZONTAL)

        #Create the check box sizer.
        checkbox_sizer = wx.BoxSizer(wx.VERTICAL)

        #Create the bottom button sizer.
        bottom_button_sizer = wx.BoxSizer(wx.HORIZONTAL)

        #Add items to the check box sizer.
        checkbox_sizer.Add(self.bad_sector_check_check_box, 1, wx.BOTTOM, 10)
        checkbox_sizer.Add(self.check_filesystems_check_box, 1, wx.BOTTOM, 10)
        checkbox_sizer.Add(self.fullverbose_checkbox, 1, wx.BOTTOM, 10)
        checkbox_sizer.Add(self.make_summary_check_box, 1, wx.BOTTOM, 10)
        checkbox_sizer.Add(self.log_output_checkbox, 1, wx.BOTTOM, 10)

        #Add items to the check box and logo sizer.
        checkbox_and_logo_sizer.Add(checkbox_sizer, 2, wx.RIGHT, 10)
        checkbox_and_logo_sizer.Add(self.logo, 1, wx.TOP|wx.LEFT|wx.ALIGN_RIGHT, 10)

        #Add items to the bottom button sizer.
        bottom_button_sizer.Add(self.about_button, 1, wx.RIGHT|wx.EXPAND, 10)
        bottom_button_sizer.Add(self.bootloader_options_button, 2, wx.RIGHT|wx.EXPAND, 10)
        bottom_button_sizer.Add(self.exit_button, 1, wx.EXPAND)

        #Add items to the main sizer.
        main_sizer.Add(self.welcome_text, 10, wx.TOP|wx.BOTTOM|wx.CENTER, 10)
        main_sizer.Add(self.settings_text, 10, wx.BOTTOM|wx.CENTER, 10)
        main_sizer.Add(checkbox_and_logo_sizer, 36, wx.BOTTOM|wx.LEFT|wx.RIGHT|wx.EXPAND, 5)
        main_sizer.Add(self.apply_operations_button, 10, wx.BOTTOM|wx.CENTER, 10)
        main_sizer.Add(bottom_button_sizer, 10, wx.BOTTOM|wx.LEFT|wx.RIGHT|wx.EXPAND, 10)

        #Get the sizer set up for the frame.
        self.panel.SetSizer(main_sizer)
        main_sizer.SetMinSize(wx.Size(400, 300))
        main_sizer.SetSizeHints(self)

    def bind_events(self): 
        """Bind all mainwindow events"""
        self.Bind(wx.EVT_MENU, self.on_about, self.menu_about)
        self.Bind(wx.EVT_MENU, self.on_exit, self.menu_exit)
        self.Bind(wx.EVT_CLOSE, self.on_exit)
        self.Bind(wx.EVT_BUTTON, self.on_about, self.about_button)
        self.Bind(wx.EVT_BUTTON, self.on_exit, self.exit_button)
        self.Bind(wx.EVT_MENU, self.system_info, self.menu_systeminfo)
        self.Bind(wx.EVT_MENU, self.show_privacypolicy, self.menu_privacy_policy)
        self.Bind(wx.EVT_MENU, self.bootloader_options, self.menu_bootloader_options)
        self.Bind(wx.EVT_BUTTON, self.bootloader_options, self.bootloader_options_button)
        self.Bind(wx.EVT_BUTTON, self.progress_window, self.apply_operations_button)

        #Checkboxes on the main window.
        self.Bind(wx.EVT_CHECKBOX, self.on_checkbox, self.check_filesystems_check_box)
        self.Bind(wx.EVT_CHECKBOX, self.on_checkbox, self.bad_sector_check_check_box)
        self.Bind(wx.EVT_CHECKBOX, self.on_checkbox, self.make_summary_check_box)

    def save_main_options(self):
        """Save all options"""
        logger.debug("MainWindow().save_main_options(): Saving Options on MainWindow...")

        #Bad Sector Check Choicebox
        if self.bad_sector_check_check_box.IsChecked():
            self.check_filesystems_check_box.Disable()
            SETTINGS["BadSectorCheck"] = True

        else:
            self.check_filesystems_check_box.Enable()
            SETTINGS["BadSectorCheck"] = False

        #Quick Disk Check Choicebox
        if self.check_filesystems_check_box.IsChecked():
            self.bad_sector_check_check_box.Disable()
            SETTINGS["QuickFSCheck"] = True

        else:
            self.bad_sector_check_check_box.Enable()
            SETTINGS["QuickFSCheck"] = False

        #Diagnostic output checkbox.
        SETTINGS["FullVerbosity"] = self.fullverbose_checkbox.IsChecked()

        #System Summary checkBox
        SETTINGS["MakeSystemSummary"] = self.make_summary_check_box.IsChecked()

        #Save output checkbox.
        SETTINGS["SaveOutput"] = self.log_output_checkbox.IsChecked()

        logger.debug("MainWindow().save_main_options(): MainWindow options saved! "
                     + "Counting operations to do...")

        self.count_operations()

    def count_operations(self):
        """Count the number of operations to do. Called by self.MainMainOpts()"""
        global NUMBER_OF_OPERATIONS
        global OPERATIONS

        #List to contain operations (and their functions) to run.
        OPERATIONS = []

        #Run a series of if statements to determine what operations to do,
        #which order to do them in, and the total number to do.
        #Do essential processes first.
        if SETTINGS["QuickFSCheck"]:
            OPERATIONS.append((EssentialBackendTools.filesystem_check, "Quick",
                               Tools.BackendTools.main.manage_bootloader))

            logger.info("MainWindow().count_operations(): Added EssentialBackendTools.filesystem_check to OPERATIONS...")

        if SETTINGS["BadSectorCheck"]:
            OPERATIONS.append((EssentialBackendTools.filesystem_check, "Thorough",
                               Tools.BackendTools.main.manage_bootloader))

            logger.info("MainWindow().count_operations(): Added EssentialBackendTools.filesystem_check to OPERATIONS...")

        #Now do other processes.
        for _os in BOOTLOADER_INFO:
            if BOOTLOADER_INFO[_os]["Settings"]["ChangeThisOS"]:
                OPERATIONS.append((MainBackendTools.manage_bootloader, _os))
                logger.info("MainWindow().count_operations(): Added (MainBackendTools."
                            +"manage_bootloader, "+_os+") to OPERATIONS...")

        NUMBER_OF_OPERATIONS = len(OPERATIONS)

        #Log gathered operations to do, and the number (verbose mode, default).
        logger.info("MainWindow().count_operations(): Number of operations: "
                    + unicode(NUMBER_OF_OPERATIONS))

        if NUMBER_OF_OPERATIONS == 0:
            logger.info("MainWindow().count_operations(): No operations to do. "
                        + "Disabling self.apply_operations_button...")
            self.apply_operations_button.SetLabel("No Operations Enabled")
            self.apply_operations_button.Disable()

        else:
            logger.info("MainWindow().count_operations(): There are operations to do. "
                        + "Enabling self.apply_operations_button...")
            self.apply_operations_button.SetLabel("Apply All Operations")
            self.apply_operations_button.Enable()

    def on_exit(self, event=None): #pylint: disable=unused-argument
        """Shut down."""
        logger.info("MainWindow().on_exit(): Double-checking the exit attempt with the user...")
        dlg = wx.MessageDialog(self.panel, 'Are you sure you want to exit?',
                               'WxFixBoot - Question!', wx.YES_NO | wx.ICON_QUESTION)

        answer = dlg.ShowModal()
        dlg.Destroy()

        if answer == wx.ID_YES:
            #Run the exit sequence
            logger.info("MainWindow().on_exit(): Exiting...")

            #Shutdown the logger.
            logging.shutdown()

            #Prompt user to save the log file.
            dlg = wx.MessageDialog(self.panel, "Do you want to keep WxFixBoot's log file? "
                                   + "For privacy reasons, WxFixBoot will delete its log file "
                                   + "when closing. If you want to save it, which is helpful "
                                   + "for debugging if something went wrong, click yes, and "
                                   + "otherwise click no.", "WxFixBoot - Question",
                                   style=wx.YES_NO | wx.ICON_QUESTION, pos=wx.DefaultPosition)

            answer = dlg.ShowModal()
            dlg.Destroy()

            if answer == wx.ID_YES:
                #Ask the user where to save it.
                dlg = wx.FileDialog(self.panel, "Save log file to...", defaultDir="/home",
                                    wildcard="Log Files (*.log)|*.log",
                                    style=wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT)

                answer = dlg.ShowModal()
                _file = dlg.GetPath()
                dlg.Destroy()

                if answer == wx.ID_OK:
                    #Copy it to the specified path, using a one-liner, and don't bother
                    #handling any errors, because this is run as root.
                    CoreTools.start_process("cp /tmp/wxfixboot.log "+_file)

                    dlg = wx.MessageDialog(self.panel, 'Done! WxFixBoot will now exit.',
                                           'WxFixBoot - Information', wx.OK | wx.ICON_INFORMATION)
                    dlg.ShowModal()
                    dlg.Destroy()

                else:
                    dlg = wx.MessageDialog(self.panel, "Okay, WxFixBoot will now exit without "
                                           + "saving the log file.", 'WxFixBoot - Information',
                                           wx.OK | wx.ICON_INFORMATION)

                    dlg.ShowModal()
                    dlg.Destroy()

            else:
                dlg = wx.MessageDialog(self.panel, "Okay, WxFixBoot will now exit without "
                                       + "saving the log file.", 'WxFixBoot - Information',
                                       wx.OK | wx.ICON_INFORMATION)

                dlg.ShowModal()
                dlg.Destroy()

            #Delete the log file, and don't bother handling any errors, because this is run as root. FIXME It won't be soon, and not smart anyway.
            os.remove('/tmp/wxfixboot.log')

            #If we're using wayland, remove the workaround we have to use to make this work.
            #XXX Fix for running on Wayland until we get policy kit stuff done.
            try:
                subprocess.check_call("xhost -si:localuser:root", shell=True)
            except subprocess.CalledProcessError:
                pass

            self.Destroy()

#End Main window
#Begin System Info Page 1.
class SystemInfoPage1(wx.Panel):
    def __init__(self, notebook, systeminfo_window):
        """Initialise SystemInfoPage1"""
        self.parent_window = notebook

        wx.Panel.__init__(self, self.parent_window)

        self.systeminfo_window = systeminfo_window
        self.list_ctrl = None

        logger.debug("SystemInfoPage1().__init__(): Creating widgets...")
        self.title = "Here are all the detected disks on your computer"
        NoteBookSharedFunctions.create_widgets(self)

        logger.debug("SystemInfoPage1().__init__(): Setting up sizers...")
        NoteBookSharedFunctions.setup_sizers(self)

        logger.debug("SystemInfoPage1().__init__(): Binding events...")
        NoteBookSharedFunctions.bind_events(self)

        logger.debug("SystemInfoPage1().__init__(): Updating list ctrl with Disk info...")
        NoteBookSharedFunctions.update_list_ctrl(self, headings=["Name", "Type", "Vendor",
                                                                 "Product", "Capacity",
                                                                 "Description"],
                                                 dictionary=DISK_INFO)

    def on_size(self, event=None): #pylint: disable=unused-argument
        """Auto resize the ListCtrl columns"""
        width = self.list_ctrl.GetClientSize()[0]

        self.list_ctrl.SetColumnWidth(0, int(width * 0.15))
        self.list_ctrl.SetColumnWidth(1, int(width * 0.1))
        self.list_ctrl.SetColumnWidth(2, int(width * 0.1))
        self.list_ctrl.SetColumnWidth(3, int(width * 0.3))
        self.list_ctrl.SetColumnWidth(4, int(width * 0.15))
        self.list_ctrl.SetColumnWidth(5, int(width * 0.2))

        if event != None:
            event.Skip()

#End System Info Page 1
#Begin System Info Page 2.
class SystemInfoPage2(wx.Panel):
    def __init__(self, notebook, systeminfo_window):
        """Initialise SystemInfoPage2"""
        self.parent_window = notebook

        wx.Panel.__init__(self, self.parent_window)
        self.systeminfo_window = systeminfo_window
        self.list_ctrl = None

        logger.debug("SystemInfoPage2().__init__(): Creating widgets...")
        self.title = "Here are all the detected disks on your computer"
        NoteBookSharedFunctions.create_widgets(self)

        logger.debug("SystemInfoPage2().__init__(): Setting up sizers...")
        NoteBookSharedFunctions.setup_sizers(self)

        logger.debug("SystemInfoPage2().__init__(): Binding events...")
        NoteBookSharedFunctions.bind_events(self)

        logger.debug("SystemInfoPage2().__init__(): Updating list ctrl with Disk info...")
        NoteBookSharedFunctions.update_list_ctrl(self, headings=["Name", "Type", "Partitions",
                                                                 "Flags", "Partitioning",
                                                                 "FileSystem"],
                                                 dictionary=DISK_INFO)

    def on_size(self, event=None): #pylint: disable=unused-argument
        """Auto resize the ListCtrl columns"""
        width = self.list_ctrl.GetClientSize()[0]

        self.list_ctrl.SetColumnWidth(0, int(width * 0.15))
        self.list_ctrl.SetColumnWidth(1, int(width * 0.1))
        self.list_ctrl.SetColumnWidth(2, int(width * 0.25))
        self.list_ctrl.SetColumnWidth(3, int(width * 0.3))
        self.list_ctrl.SetColumnWidth(4, int(width * 0.1))
        self.list_ctrl.SetColumnWidth(5, int(width * 0.1))

        if event != None:
            event.Skip()

#End System Info Page 2
#Begin System Info Page 3.
class SystemInfoPage3(wx.Panel):
    def __init__(self, notebook, systeminfo_window):
        """Initialise SystemInfoPage3"""
        self.parent_window = notebook
        wx.Panel.__init__(self, self.parent_window)
        self.systeminfo_window = systeminfo_window
        self.list_ctrl = None

        logger.debug("SystemInfoPage3().__init__(): Creating widgets...")
        self.title = "Here are all the detected disks on your computer"
        NoteBookSharedFunctions.create_widgets(self)

        logger.debug("SystemInfoPage3().__init__(): Setting up sizers...")
        NoteBookSharedFunctions.setup_sizers(self)

        logger.debug("SystemInfoPage3().__init__(): Binding events...")
        NoteBookSharedFunctions.bind_events(self)

        logger.debug("SystemInfoPage3().__init__(): Updating list ctrl with Disk info...")
        NoteBookSharedFunctions.update_list_ctrl(self, headings=["Name", "Type", "ID", "UUID"],
                                                 dictionary=DISK_INFO)

    def on_size(self, event=None): #pylint: disable=unused-argument
        """Auto resize the ListCtrl columns"""
        width = self.list_ctrl.GetClientSize()[0]

        self.list_ctrl.SetColumnWidth(0, int(width * 0.15))
        self.list_ctrl.SetColumnWidth(1, int(width * 0.15))
        self.list_ctrl.SetColumnWidth(2, int(width * 0.35))
        self.list_ctrl.SetColumnWidth(3, int(width * 0.35))

        if event != None:
            event.Skip()

#End System Info Page 3
#Begin System Info Page 4.
class SystemInfoPage4(wx.Panel):
    def __init__(self, notebook, systeminfo_window):
        """Initialise SystemInfoPage4"""
        self.parent_window = notebook
        wx.Panel.__init__(self, self.parent_window)
        self.systeminfo_window = systeminfo_window
        self.list_ctrl = None

        logger.debug("SystemInfoPage4().__init__(): Creating widgets...")
        self.title = "Here are all the operating systems WxFixBoot detected on your computer"
        NoteBookSharedFunctions.create_widgets(self)

        logger.debug("SystemInfoPage4().__init__(): Setting up sizers...")
        NoteBookSharedFunctions.setup_sizers(self)

        logger.debug("SystemInfoPage4().__init__(): Binding events...")
        NoteBookSharedFunctions.bind_events(self)

        logger.debug("SystemInfoPage4().__init__(): Updating list ctrl with OS Info...")
        NoteBookSharedFunctions.update_list_ctrl(self, headings=["Name", "IsCurrentOS",
                                                                 "Arch", "Partition",
                                                                 "PackageManager"],
                                                 dictionary=OS_INFO)

    def on_size(self, event=None): #pylint: disable=unused-argument
        """Auto resize the ListCtrl columns"""
        width = self.list_ctrl.GetClientSize()[0]

        self.list_ctrl.SetColumnWidth(0, int(width * 0.4))
        self.list_ctrl.SetColumnWidth(1, int(width * 0.1))
        self.list_ctrl.SetColumnWidth(2, int(width * 0.1))
        self.list_ctrl.SetColumnWidth(3, int(width * 0.2))
        self.list_ctrl.SetColumnWidth(4, int(width * 0.2))

        if event != None:
            event.Skip()

#End System Info Page 4
#Begin System Info Page 5.
class SystemInfoPage5(wx.Panel):
    def __init__(self, notebook, systeminfo_window):
        """Initialise SystemInfoPage5"""
        self.parent_window = notebook
        wx.Panel.__init__(self, self.parent_window)
        self.systeminfo_window = systeminfo_window
        self.list_ctrl = None

        logger.debug("SystemInfoPage5().__init__(): Creating widgets...")
        self.title = "Here are all the bootloaders WxFixBoot detected on your computer"
        NoteBookSharedFunctions.create_widgets(self)

        logger.debug("SystemInfoPage5().__init__(): Setting up sizers...")
        NoteBookSharedFunctions.setup_sizers(self)

        logger.debug("SystemInfoPage5().__init__(): Binding events...")
        NoteBookSharedFunctions.bind_events(self)

        logger.debug("SystemInfoPage5().__init__(): Updating list ctrl with Bootloader Info...")
        NoteBookSharedFunctions.update_list_ctrl(self, headings=["OSName", "Bootloader",
                                                                 "BootDisk", "DefaultOS"],
                                                 dictionary=BOOTLOADER_INFO)

    def on_size(self, event=None): #pylint: disable=unused-argument
        """Auto resize the ListCtrl columns"""
        width = self.list_ctrl.GetClientSize()[0]

        self.list_ctrl.SetColumnWidth(0, int(width * 0.4))
        self.list_ctrl.SetColumnWidth(1, int(width * 0.1))
        self.list_ctrl.SetColumnWidth(2, int(width * 0.1))
        self.list_ctrl.SetColumnWidth(3, int(width * 0.4))

        if event != None:
            event.Skip()

#End System Info Page 5
#Begin System Info Page 6.
class SystemInfoPage6(wx.Panel):
    def __init__(self, notebook, systeminfo_window):
        """Initialise SystemInfoPage6"""
        self.parent_window = notebook
        wx.Panel.__init__(self, self.parent_window)
        self.systeminfo_window = systeminfo_window
        self.list_ctrl = None

        logger.debug("SystemInfoPage6().__init__(): Creating widgets...")
        self.title = "Here are all the bootloaders WxFixBoot detected on your computer"
        NoteBookSharedFunctions.create_widgets(self)

        logger.debug("SystemInfoPage6().__init__(): Setting up sizers...")
        NoteBookSharedFunctions.setup_sizers(self)

        logger.debug("SystemInfoPage6().__init__(): Binding events...")
        NoteBookSharedFunctions.bind_events(self)

        logger.debug("SystemInfoPage6().__init__(): Updating list ctrl with Bootloader Info...")
        NoteBookSharedFunctions.update_list_ctrl(self, headings=["OSName", "Timeout",
                                                                 "GlobalKernelOptions",
                                                                 "IsModifyable", "Comments"],
                                                 dictionary=BOOTLOADER_INFO)

    def on_size(self, event=None): #pylint: disable=unused-argument
        """Auto resize the ListCtrl columns"""
        width = self.list_ctrl.GetClientSize()[0]

        self.list_ctrl.SetColumnWidth(0, int(width * 0.4))
        self.list_ctrl.SetColumnWidth(1, int(width * 0.1))
        self.list_ctrl.SetColumnWidth(2, int(width * 0.2))
        self.list_ctrl.SetColumnWidth(3, int(width * 0.1))
        self.list_ctrl.SetColumnWidth(4, int(width * 0.2))

        if event != None:
            event.Skip()

#End System Info Page 6
#Begin System Info Window
class SystemInfoWindow(wx.Frame):
    def __init__(self):
        """Initialize SystemInfoWindow"""
        wx.Frame.__init__(self, wx.GetApp().TopWindow, title="WxFixBoot - System Information",
                          size=(780, 310), style=wx.DEFAULT_FRAME_STYLE)

        self.panel = wx.Panel(self)
        self.SetClientSize(wx.Size(780, 310))
        self.parent_window = wx.GetApp().TopWindow
        wx.Frame.SetIcon(self, APPICON)

        #Set up the notebook and the pages.
        self.notebook = wx.Notebook(self.panel)
        page1 = SystemInfoPage1(self.notebook, self)
        page2 = SystemInfoPage2(self.notebook, self)
        page3 = SystemInfoPage3(self.notebook, self)
        page4 = SystemInfoPage4(self.notebook, self)
        page5 = SystemInfoPage5(self.notebook, self)
        page6 = SystemInfoPage6(self.notebook, self)

        self.notebook.AddPage(page1, "Disk Info 1")
        self.notebook.AddPage(page2, "Disk Info 2")
        self.notebook.AddPage(page3, "Disk Info 3")
        self.notebook.AddPage(page4, "OS Info")
        self.notebook.AddPage(page5, "Bootloader Info 1")
        self.notebook.AddPage(page6, "Bootloader Info 2")

        #Set up the sizer.
        main_sizer = wx.BoxSizer()
        main_sizer.Add(self.notebook, 1, wx.EXPAND)
        self.panel.SetSizer(main_sizer)
        main_sizer.SetMinSize(wx.Size(780, 310))
        main_sizer.SetSizeHints(self)

        self.bind_events()

        #Call Layout() on self.panel() to ensure it displays properly.
        self.panel.Layout()

        logger.info("SystemInfoWindow().__init__(): Ready. Waiting for events...")

    def bind_events(self):
        """Bind all events for SystemInfoWindow"""
        self.Bind(wx.EVT_CLOSE, self.on_exit)

    def on_exit(self, event=None): #pylint: disable=unused-argument
        """Exit SystemInfoWindow"""
        logger.info("SystemInfoWindow().on_exit(): Closing SystemInfoWindow...")
        self.Destroy()

#End System Info Window
#Begin Privacy Policy Window.
class PrivPolWindow(wx.Frame):
    def __init__(self):
        """Initialize PrivPolWindow"""
        wx.Frame.__init__(self, parent=wx.GetApp().TopWindow, title="WxFixBoot - Privacy Policy",
                          size=(750, 400), style=wx.DEFAULT_FRAME_STYLE)

        self.panel = wx.Panel(self)
        self.SetClientSize(wx.Size(750, 400))
        self.parent_window = wx.GetApp().TopWindow
        wx.Frame.SetIcon(self, APPICON)

        logger.debug("PrivPolWindow().__init__(): Creating button...")
        self.create_button()

        logger.debug("PrivPolWindow().__init__(): Loading page...")
        self.load_page()

        logger.debug("PrivPolWindow().__init__(): Setting up sizers...")
        self.setup_sizers()

        logger.debug("PrivPolWindow().__init__(): Binding Events...")
        self.bind_events()

        #Call Layout() on self.panel() to ensure it displays properly.
        self.panel.Layout()

        logger.debug("PrivPolWindow().__init__(): Ready. Waiting for events...")

    def create_button(self):
        """Create the close buton."""
        self.close_button = wx.Button(self.panel, -1, "Close")

    def load_page(self):
        """Load the privacy policy web page (locally stored)"""
        _file = open("/usr/share/wxfixboot/other/privacypolicy.html", "r")
        text = _file.read()
        _file.close()

        self.html = wx.html.HtmlWindow(self.panel)
        self.html.SetPage(text)

    def setup_sizers(self):
        """Set up sizers for PrivPolWindow"""
        #Make a boxsizer.
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        #Add each object to the main sizer.
        main_sizer.Add(self.html, 1, wx.EXPAND|wx.ALL, 10)
        main_sizer.Add(self.close_button, 0, wx.BOTTOM|wx.CENTER, 10)

        #Get the sizer set up for the frame.
        self.panel.SetSizer(main_sizer)
        main_sizer.SetMinSize(wx.Size(750, 400))
        main_sizer.SetSizeHints(self)

    def bind_events(self):
        """Bind events so we can close this window."""
        self.Bind(wx.EVT_BUTTON, self.on_close, self.close_button)
        self.Bind(wx.EVT_CLOSE, self.on_close)

    def on_close(self, event=None): #pylint: disable=unused-argument
        """Close PrivPolWindow"""
        self.Destroy()

#End Privacy Policy Window.
#Begin Bootloader Options Window.
class BootloaderOptionsWindow(wx.Frame):
    def __init__(self):
        """Initialise bootloader options window"""
        wx.Frame.__init__(self, parent=wx.GetApp().TopWindow,
                          title="WxFixBoot - Bootloader Options", size=(400, 200),
                          style=wx.DEFAULT_FRAME_STYLE)

        self.panel = wx.Panel(self)
        self.SetClientSize(wx.Size(800, 800))
        self.parent_window = wx.GetApp().TopWindow
        wx.Frame.SetIcon(self, APPICON)

        #Set up the previous OS choice.
        if SYSTEM_INFO["PreviousOSChoice"] == "":
            SYSTEM_INFO["PreviousOSChoice"] = SYSTEM_INFO["ModifyableOSs"][0]

        self.create_text()
        self.create_choiceboxes()
        self.create_checkboxes()
        self.create_buttons()
        self.create_other_widgets()
        self.setup_sizers()
        self.bind_events()

        self.on_advanced_options()
        self.on_osinfo()

        wx.CallLater(500, self.on_oschoice_change, startup=True)

        #Let user know they can specify a timeout of 0 seconds to hide the boot menu,
        #if they have only 1 (detected) OS.
        if len(OS_INFO) == 1:
            wx.CallLater(500, self.display_timeoutinfo_message)

        logger.debug("BootloaderOptionsWindow().__init__(): Bootloader Options Window Started.")

    def display_timeoutinfo_message(self):
        """Displays an informational message to the user if they only have 1 detected OS."""
        dlg = wx.MessageDialog(self.panel, "WxFixBoot only detected one Operating System on "
                               + "your computer. You can hide your boot menu entirely, if you "
                               + "wish, by selecting a bootloader timeout of 0 seconds.",
                               "WxFixBoot - Information", style=wx.OK | wx.ICON_INFORMATION)

        dlg.ShowModal()
        dlg.Destroy()

    def create_text(self):
        """Create the text"""
        self.title_text = wx.StaticText(self.panel, -1, "Select each OS you want to modify")
        self.os_info_text = wx.lib.stattext.GenStaticText(self.panel, -1, "OS Info")

        #Basic Options.
        self.basic_options_text = wx.lib.stattext.GenStaticText(self.panel, -1, "Basic Options")
        self.new_timeout_text = wx.StaticText(self.panel, -1, "New timeout (in seconds):")
        self.defaultos_text = wx.StaticText(self.panel, -1, "Default OS to boot:")

        #Advanced Options.
        self.advanced_options_text = wx.lib.stattext.GenStaticText(self.panel, -1,
                                                                   "Advanced Options")

        self.new_kerneloptions_text = wx.StaticText(self.panel, -1, "New kernel options:")
        self.backup_bootloader_text = wx.StaticText(self.panel, -1, "Backup to:")
        self.restore_bootloader_text = wx.StaticText(self.panel, -1, "Restore from:")

    def create_choiceboxes(self):
        """Create the choice boxes"""
        self.os_choice = wx.Choice(self.panel, -1, choices=SYSTEM_INFO["ModifyableOSs"])
        self.os_choice.SetStringSelection(SYSTEM_INFO["PreviousOSChoice"])

        #Basic Options.
        self.defaultos_choice = wx.Choice(self.panel, -1, choices=list(OS_INFO.keys()))

        #Advanced Options.
        self.new_bootloader_choice = wx.Choice(self.panel, -1, choices=[])
        self.backup_bootloader_choice = wx.Choice(self.panel, -1, choices=["-- Please Select --",
                                                                           "Specify File Path..."])

        self.restore_bootloader_choice = wx.Choice(self.panel, -1,
                                                   choices=["-- Please Select --",
                                                            "Specify File Path..."])

    def create_checkboxes(self):
        """Create the check boxes"""
        #Basic Options.
        self.reinstall_bootloader_checkbox = wx.CheckBox(self.panel, -1, "")
        self.update_bootloader_checkbox = wx.CheckBox(self.panel, -1, "")
        self.keep_bootloader_timeout_checkbox = wx.CheckBox(self.panel, -1, "")

        #Advanced Options.
        self.keep_kerneloptions_checkbox = wx.CheckBox(self.panel, -1, "")
        self.install_new_bootloader_checkbox = wx.CheckBox(self.panel, -1,
                                                           "Install a New Bootloader")

        self.backup_bootloader_checkbox = wx.CheckBox(self.panel, -1,
                                                      "Backup this OS's bootloader config")

        self.restore_bootloader_checkbox = wx.CheckBox(self.panel, -1,
                                                       "Restore this OS's bootloader config")

    def create_buttons(self):
        """Create the buttons"""
        self.system_info_button = wx.Button(self.panel, -1, "View More Details")
        self.revert_os_changes_button = wx.Button(self.panel, -1, "Revert Changes for this OS")
        self.save_button = wx.Button(self.panel, -1, "Save All Changes And Close")

    def create_other_widgets(self):
        """Create all other widgets"""
        #Bootloader timeout spinner.
        self.bootloader_timeout_spinner = wx.SpinCtrl(self.panel, -1, "")
        self.bootloader_timeout_spinner.SetRange(0, 100)

        #Arrows.
        img1 = wx.Image("/usr/share/wxfixboot/images/ArrowDown.png", wx.BITMAP_TYPE_PNG)
        img2 = wx.Image("/usr/share/wxfixboot/images/ArrowRight.png", wx.BITMAP_TYPE_PNG)

        if CLASSIC_WXPYTHON:
            self.down_arrow_image = wx.BitmapFromImage(img1)
            self.right_arrow_image = wx.BitmapFromImage(img2)

        else:
            self.down_arrow_image = wx.Bitmap(img1)
            self.right_arrow_image = wx.Bitmap(img2)

        self.arrow1 = wx.lib.statbmp.GenStaticBitmap(self.panel, -1, self.down_arrow_image)
        self.arrow2 = wx.lib.statbmp.GenStaticBitmap(self.panel, -1, self.down_arrow_image)
        self.arrow3 = wx.lib.statbmp.GenStaticBitmap(self.panel, -1, self.down_arrow_image)

        #List Ctrl.
        self.list_ctrl = wx.ListCtrl(self.panel, -1,
                                     style=wx.LC_REPORT|wx.BORDER_SUNKEN|wx.LC_VRULES)

        NoteBookSharedFunctions.update_list_ctrl(self, headings=["Name", "IsCurrentOS", "Arch",
                                                                 "Partition", "PackageManager"],
                                                 dictionary=OS_INFO)

        #Text ctrl.
        self.new_kerneloptions_textctrl = wx.TextCtrl(self.panel, -1, "")

    def on_size(self, event=None): #pylint: disable=unused-argument
        """Auto resize the ListCtrl columns"""
        width = self.list_ctrl.GetClientSize()[0]

        self.list_ctrl.SetColumnWidth(0, int(width * 0.4))
        self.list_ctrl.SetColumnWidth(1, int(width * 0.1))
        self.list_ctrl.SetColumnWidth(2, int(width * 0.1))
        self.list_ctrl.SetColumnWidth(3, int(width * 0.2))
        self.list_ctrl.SetColumnWidth(4, int(width * 0.2))

        if event != None:
            event.Skip()

    def setup_sizers(self):
        """Setup the sizers"""
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)

        osinfo_sizer = wx.BoxSizer(wx.HORIZONTAL)

        #Add items to osinfo_sizer.
        osinfo_sizer.Add((5, 5), 1, wx.RIGHT|wx.ALIGN_CENTER, 5)
        osinfo_sizer.Add(self.os_info_text, 0, wx.RIGHT|wx.LEFT|wx.ALIGN_CENTER, 5)
        osinfo_sizer.Add(self.arrow1, 0, wx.RIGHT|wx.LEFT|wx.ALIGN_CENTER, 5)
        osinfo_sizer.Add((5, 5), 1, wx.LEFT|wx.ALIGN_CENTER, 5)

        basic_options_sizer = wx.BoxSizer(wx.HORIZONTAL)

        #Add items to basic_options_sizer.
        basic_options_sizer.Add((5, 5), 1, wx.RIGHT|wx.ALIGN_CENTER, 5)
        basic_options_sizer.Add(self.basic_options_text, 0, wx.RIGHT|wx.LEFT|wx.ALIGN_CENTER, 5)
        basic_options_sizer.Add(self.arrow2, 0, wx.RIGHT|wx.LEFT|wx.ALIGN_CENTER, 5)
        basic_options_sizer.Add((5, 5), 1, wx.LEFT|wx.ALIGN_CENTER, 5)

        self.fix_and_update_bootloader_sizer = wx.BoxSizer(wx.HORIZONTAL)

        #Add items to fix_and_update_bootloader_sizer.
        self.fix_and_update_bootloader_sizer.Add(self.reinstall_bootloader_checkbox, 1,
                                                 wx.RIGHT|wx.ALIGN_CENTER, 5)

        self.fix_and_update_bootloader_sizer.Add(self.update_bootloader_checkbox, 1,
                                                 wx.LEFT|wx.ALIGN_CENTER, 5)

        self.timeout_sizer = wx.BoxSizer(wx.HORIZONTAL)

        #Add items to timeout_sizer.
        self.timeout_sizer.Add(self.keep_bootloader_timeout_checkbox, 3,
                               wx.RIGHT|wx.ALIGN_CENTER, 5)

        self.timeout_sizer.Add((5, 5), 1, wx.RIGHT|wx.LEFT, 5)
        self.timeout_sizer.Add(self.new_timeout_text, 2, wx.RIGHT|wx.LEFT|wx.ALIGN_CENTER, 5)
        self.timeout_sizer.Add(self.bootloader_timeout_spinner, 3, wx.LEFT|wx.ALIGN_CENTER, 5)

        self.defaultos_sizer = wx.BoxSizer(wx.HORIZONTAL)

        #Add items to defaultos_sizer.
        self.defaultos_sizer.Add(self.defaultos_text, 1, wx.RIGHT|wx.ALIGN_CENTER, 5)
        self.defaultos_sizer.Add(self.defaultos_choice, 1, wx.LEFT|wx.ALIGN_CENTER, 5)

        advanced_options_sizer = wx.BoxSizer(wx.HORIZONTAL)

        #Add items to advanced_options_sizer.
        advanced_options_sizer.Add((5, 5), 1, wx.RIGHT|wx.ALIGN_CENTER, 5)
        advanced_options_sizer.Add(self.advanced_options_text, 0,
                                   wx.RIGHT|wx.LEFT|wx.ALIGN_CENTER, 5)

        advanced_options_sizer.Add(self.arrow3, 0, wx.RIGHT|wx.LEFT|wx.ALIGN_CENTER, 5)
        advanced_options_sizer.Add((5, 5), 1, wx.LEFT|wx.ALIGN_CENTER, 5)

        self.kernel_options_sizer = wx.BoxSizer(wx.HORIZONTAL)

        #Add items to kernel_options_sizer.
        self.kernel_options_sizer.Add(self.keep_kerneloptions_checkbox, 2,
                                      wx.RIGHT|wx.ALIGN_CENTER, 5)

        self.kernel_options_sizer.Add(self.new_kerneloptions_text, 1,
                                      wx.RIGHT|wx.LEFT|wx.ALIGN_CENTER, 5)

        self.kernel_options_sizer.Add(self.new_kerneloptions_textctrl, 2,
                                      wx.LEFT|wx.ALIGN_CENTER, 5)

        self.install_new_bootloader_sizer = wx.BoxSizer(wx.HORIZONTAL)

        #Add items to install_new_bootloader_sizer.
        self.install_new_bootloader_sizer.Add(self.install_new_bootloader_checkbox, 2,
                                              wx.RIGHT|wx.ALIGN_CENTER, 5)

        self.install_new_bootloader_sizer.Add((5, 5), 1, wx.RIGHT|wx.LEFT|wx.ALIGN_CENTER, 5)
        self.install_new_bootloader_sizer.Add(self.new_bootloader_choice, 2,
                                              wx.LEFT|wx.ALIGN_CENTER, 5)

        self.backup_bootloader_sizer = wx.BoxSizer(wx.HORIZONTAL)

        #Add items to backup_bootloader_sizer.
        self.backup_bootloader_sizer.Add(self.backup_bootloader_checkbox, 2,
                                         wx.RIGHT|wx.ALIGN_CENTER, 5)

        self.backup_bootloader_sizer.Add(self.backup_bootloader_text, 1,
                                         wx.RIGHT|wx.LEFT|wx.ALIGN_CENTER, 5)

        self.backup_bootloader_sizer.Add(self.backup_bootloader_choice, 2,
                                         wx.LEFT|wx.ALIGN_CENTER, 5)

        self.restore_bootloader_sizer = wx.BoxSizer(wx.HORIZONTAL)

        #Add items to restore_bootloader_sizer.
        self.restore_bootloader_sizer.Add(self.restore_bootloader_checkbox, 2,
                                          wx.RIGHT|wx.ALIGN_CENTER, 5)

        self.restore_bootloader_sizer.Add(self.restore_bootloader_text, 1,
                                          wx.RIGHT|wx.LEFT|wx.ALIGN_CENTER, 5)

        self.restore_bootloader_sizer.Add(self.restore_bootloader_choice, 2,
                                          wx.LEFT|wx.ALIGN_CENTER, 5)

        bottom_button_sizer = wx.BoxSizer(wx.HORIZONTAL)

        #Add items to bottom_button_sizer.
        bottom_button_sizer.Add(self.revert_os_changes_button, 1, wx.RIGHT|wx.ALIGN_CENTER, 5)
        bottom_button_sizer.Add(self.save_button, 1, wx.LEFT|wx.ALIGN_CENTER, 5)

        #Add items to main_sizer.
        self.main_sizer.Add(self.title_text, 1, wx.ALL|wx.CENTER, 10)
        self.main_sizer.Add(self.os_choice, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        self.main_sizer.Add(wx.StaticLine(self.panel), 0, wx.ALL|wx.EXPAND, 10)
        self.main_sizer.Add(osinfo_sizer, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        self.main_sizer.Add(self.list_ctrl, 5, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        self.main_sizer.Add(self.system_info_button, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        self.main_sizer.Add(wx.StaticLine(self.panel), 0, wx.ALL|wx.EXPAND, 10)
        self.main_sizer.Add(basic_options_sizer, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        self.main_sizer.Add(self.fix_and_update_bootloader_sizer, 1,
                            wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)

        self.main_sizer.Add(self.timeout_sizer, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        self.main_sizer.Add(self.defaultos_sizer, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        self.main_sizer.Add(wx.StaticLine(self.panel), 0, wx.ALL|wx.EXPAND, 10)
        self.main_sizer.Add(advanced_options_sizer, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        self.main_sizer.Add(self.kernel_options_sizer, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        self.main_sizer.Add(self.install_new_bootloader_sizer, 1,
                            wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)

        self.main_sizer.Add(self.backup_bootloader_sizer, 1,
                            wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)

        self.main_sizer.Add(self.restore_bootloader_sizer, 1,
                            wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)

        self.main_sizer.Add(wx.StaticLine(self.panel), 0, wx.ALL|wx.EXPAND, 10)
        self.main_sizer.Add(bottom_button_sizer, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)

        #Get the sizer set up for the frame.
        self.panel.SetSizer(self.main_sizer)
        self.main_sizer.SetMinSize(wx.Size(749, 673)) #TODO Why this weird size?

    def bind_events(self):
        """Bind all events for BootloaderOptionsWindow"""
        self.Bind(wx.EVT_CLOSE, self.on_close)
        self.Bind(wx.EVT_SIZE, self.on_size)

        #Text.
        self.os_info_text.Bind(wx.EVT_LEFT_DOWN, self.on_osinfo)
        self.basic_options_text.Bind(wx.EVT_LEFT_DOWN, self.on_basic_options)
        self.advanced_options_text.Bind(wx.EVT_LEFT_DOWN, self.on_advanced_options)

        #Images.
        self.arrow1.Bind(wx.EVT_LEFT_DOWN, self.on_osinfo)
        self.arrow2.Bind(wx.EVT_LEFT_DOWN, self.on_basic_options)
        self.arrow3.Bind(wx.EVT_LEFT_DOWN, self.on_advanced_options)

        #Checkboxes.
        self.Bind(wx.EVT_CHECKBOX, self.on_timeout_checkbox, self.keep_bootloader_timeout_checkbox)
        self.Bind(wx.EVT_CHECKBOX, self.on_update_or_reinstall_checkbox,
                  self.reinstall_bootloader_checkbox)

        self.Bind(wx.EVT_CHECKBOX, self.on_update_or_reinstall_checkbox,
                  self.update_bootloader_checkbox)

        self.Bind(wx.EVT_CHECKBOX, self.on_install_new_bootloader_checkbox,
                  self.install_new_bootloader_checkbox)

        self.Bind(wx.EVT_CHECKBOX, self.on_backup_bootloader_checkbox,
                  self.backup_bootloader_checkbox)

        self.Bind(wx.EVT_CHECKBOX, self.on_restore_bootloader_checkbox,
                  self.restore_bootloader_checkbox)

        self.Bind(wx.EVT_CHECKBOX, self.on_kerneloptions_checkbox,
                  self.keep_kerneloptions_checkbox)

        #Buttons.
        self.Bind(wx.EVT_BUTTON, self.on_close, self.save_button)
        self.Bind(wx.EVT_BUTTON, self.system_info, self.system_info_button)
        self.Bind(wx.EVT_BUTTON, self.load_settings, self.revert_os_changes_button)

        #Choiceboxes.
        self.Bind(wx.EVT_CHOICE, self.on_oschoice_change, self.os_choice)
        self.Bind(wx.EVT_CHOICE, self.on_restore_bootloader_choice, self.restore_bootloader_choice)
        self.Bind(wx.EVT_CHOICE, self.on_backup_bootloader_choice, self.backup_bootloader_choice)
        self.Bind(wx.EVT_CHOICE, self.on_new_bootloader_choice, self.new_bootloader_choice)

    def system_info(self, event=None): #pylint: disable=unused-argument
        """Start SystemInfoWindow"""
        logger.debug("BootloaderOptionsWindow().system_info(): Starting System Info Window...")
        SystemInfoWindow().Show()

    def load_settings(self, event=None): #pylint: disable=unused-argument
        """Load all settings for this OS into the checkboxes and choice boxes"""
        _os = self.os_choice.GetStringSelection()

        logger.debug("BootloaderOptionsWindow().load_settings(): Loading settings for "+_os+"...")
        self.reinstall_bootloader_checkbox.SetValue(BOOTLOADER_INFO[_os]["Settings"]["Reinstall"])
        self.update_bootloader_checkbox.SetValue(BOOTLOADER_INFO[_os]["Settings"]["Update"])
        self.keep_bootloader_timeout_checkbox.SetValue(BOOTLOADER_INFO[_os]["Settings"]["KeepExistingTimeout"])
        self.bootloader_timeout_spinner.SetValue(BOOTLOADER_INFO[_os]["Settings"]["NewTimeout"])
        self.keep_kerneloptions_checkbox.SetValue(BOOTLOADER_INFO[_os]["Settings"]["KeepExistingKernelOptions"])
        self.new_kerneloptions_textctrl.SetValue(BOOTLOADER_INFO[_os]["Settings"]["NewKernelOptions"])
        self.defaultos_choice.SetStringSelection(BOOTLOADER_INFO[_os]["Settings"]["DefaultOS"])
        self.install_new_bootloader_checkbox.SetValue(BOOTLOADER_INFO[_os]["Settings"]["InstallNewBootloader"])
        self.new_bootloader_choice.SetStringSelection(BOOTLOADER_INFO[_os]["Settings"]["NewBootloader"])
        self.backup_bootloader_checkbox.SetValue(BOOTLOADER_INFO[_os]["Settings"]["BackupBootloader"])
        self.backup_bootloader_choice.SetStringSelection(BOOTLOADER_INFO[_os]["Settings"]["BootloaderBackupTarget"])
        self.restore_bootloader_checkbox.SetValue(BOOTLOADER_INFO[_os]["Settings"]["RestoreBootloader"])
        self.restore_bootloader_choice.SetStringSelection(BOOTLOADER_INFO[_os]["Settings"]["BootloaderRestoreSource"])
        self.on_timeout_checkbox()
        self.set_gui_state()

        #Don't allow the user to attempt to modify or remove GRUB-LEGACY.
        if BOOTLOADER_INFO[self.os_choice.GetStringSelection()]["Bootloader"] in ("GRUB-LEGACY", "Unknown"):
            self.reinstall_bootloader_checkbox.Disable()
            self.update_bootloader_checkbox.Disable()

        #Don't allow the user to replace grub-legacy.
        if BOOTLOADER_INFO[self.os_choice.GetStringSelection()]["Bootloader"] == "GRUB-LEGACY":
            self.install_new_bootloader_checkbox.Disable()

    def set_gui_state(self, event=None): #pylint: disable=unused-argument
        """Set all the GUI element's states (enabled/disabled) for this OS"""
        _os = self.os_choice.GetStringSelection()

        logger.debug("BootloaderOptionsWindow().set_gui_state(): Setting GUI state for "+_os+"...")
        self.reinstall_bootloader_checkbox.Enable(BOOTLOADER_INFO[_os]["GUIState"]["ReinstallCheckBoxState"])
        self.update_bootloader_checkbox.Enable(BOOTLOADER_INFO[_os]["GUIState"]["UpdateCheckBoxState"])
        self.keep_bootloader_timeout_checkbox.Enable(BOOTLOADER_INFO[_os]["GUIState"]["KeepExistingTimeoutCheckBoxState"])
        self.bootloader_timeout_spinner.Enable(BOOTLOADER_INFO[_os]["GUIState"]["NewTimeoutSpinnerState"])
        self.keep_kerneloptions_checkbox.Enable(BOOTLOADER_INFO[_os]["GUIState"]["KeepExistingKernelOptionsCheckBoxState"])
        self.new_kerneloptions_textctrl.Enable(BOOTLOADER_INFO[_os]["GUIState"]["NewKernelOptionsTextCtrlState"])
        self.defaultos_choice.Enable(BOOTLOADER_INFO[_os]["GUIState"]["DefaultOSChoiceState"])
        self.install_new_bootloader_checkbox.Enable(BOOTLOADER_INFO[_os]["GUIState"]["InstallNewBootloaderCheckBoxState"])
        self.new_bootloader_choice.Enable(BOOTLOADER_INFO[_os]["GUIState"]["NewBootloaderChoiceState"])
        self.backup_bootloader_checkbox.Enable(BOOTLOADER_INFO[_os]["GUIState"]["BackupBootloaderCheckBoxState"])
        self.backup_bootloader_choice.Enable(BOOTLOADER_INFO[_os]["GUIState"]["BackupBootloaderChoiceState"])
        self.restore_bootloader_checkbox.Enable(BOOTLOADER_INFO[_os]["GUIState"]["RestoreBootloaderCheckBoxState"])
        self.restore_bootloader_choice.Enable(BOOTLOADER_INFO[_os]["GUIState"]["RestoreBootloaderChoiceState"])

    def set_text_labels(self):
        """Set text labels for GUI elements"""
        _os = self.os_choice.GetStringSelection()

        logger.debug("BootloaderOptionsWindow().set_text_labels(): "
                     + "Setting text labels for "+_os+"...")

        self.keep_kerneloptions_checkbox.SetLabel("Keep "+BOOTLOADER_INFO[_os]["Bootloader"]
                                                  + "'s existing kernel options")

        self.install_new_bootloader_checkbox.SetLabel("Replace "+BOOTLOADER_INFO[_os]["Bootloader"]
                                                      + " with:")

        self.reinstall_bootloader_checkbox.SetLabel("Fix/Reinstall "
                                                    + BOOTLOADER_INFO[_os]["Bootloader"])

        self.update_bootloader_checkbox.SetLabel("Update "+BOOTLOADER_INFO[_os]["Bootloader"]
                                                 + "'s Config")

        self.keep_bootloader_timeout_checkbox.SetLabel("Keep "+BOOTLOADER_INFO[_os]["Bootloader"]
                                                       + "'s existing menu timeout")

        self.revert_os_changes_button.SetLabel("Revert Changes for "+_os)

    def on_oschoice_change(self, event=None, startup=False): #pylint: disable=unused-argument
        """Save and load new GUI settings and states in accordance with the OS choice change"""
        logger.debug("BootloaderOptionsWindow().on_oschoice_change(): OS choice has changed. "
                     + "Saving and then loading settings...")

        #Save settings when selecting a new choice, but not when this is called
        #when the window is first opened.
        if startup is False:
            self.save_settings(_os=SYSTEM_INFO["PreviousOSChoice"])
            self.save_gui_state(_os=SYSTEM_INFO["PreviousOSChoice"])
            SYSTEM_INFO["PreviousOSChoice"] = self.os_choice.GetStringSelection()

        #Set up new_bootloader_choice.
        choices = BOOTLOADER_INFO[self.os_choice.GetStringSelection()]["AvailableBootloaders"]

        if OS_INFO[self.os_choice.GetStringSelection()]["EFIPartition"] == "Unknown":
            #Remove GRUB-UEFI and ELILO if they are available for install.
            if "GRUB-UEFI" in choices:
                choices.remove("GRUB-UEFI")

            if "ELILO" in choices:
                choices.remove("ELILO")

            dlg = wx.MessageDialog(self.panel, "This OS has no UEFI partition, so you will be "
                                   + "unable to select a UEFI bootloader to install.",
                                   "WxFixBoot - Information", style=wx.OK | wx.ICON_INFORMATION,
                                   pos=wx.DefaultPosition)

            dlg.ShowModal()
            dlg.Destroy()

        #Remove the current bootloader from the choices (if it's in there).
        if BOOTLOADER_INFO[self.os_choice.GetStringSelection()]["Bootloader"] in choices:
            choices.remove(BOOTLOADER_INFO[self.os_choice.GetStringSelection()]["Bootloader"])

        #Set the choices.
        self.new_bootloader_choice.SetItems(["-- Please Select --"]+choices)
        self.new_bootloader_choice.SetStringSelection("-- Please Select --")

        self.load_settings()
        self.set_text_labels()

        #Don't allow the user to attempt to modify or remove GRUB-LEGACY.
        if BOOTLOADER_INFO[self.os_choice.GetStringSelection()]["Bootloader"] in ("GRUB-LEGACY", "Unknown"):
            self.reinstall_bootloader_checkbox.Disable()
            self.update_bootloader_checkbox.Disable()

        #Don't allow the user to replace grub-legacy.
        if BOOTLOADER_INFO[self.os_choice.GetStringSelection()]["Bootloader"] == "GRUB-LEGACY":
            self.install_new_bootloader_checkbox.Disable()

        #Warn the user not to do bootloader operations if the current bootloader is an
        #EFI bootloader, but we couldn't find the OS's EFI partition.
        if (BOOTLOADER_INFO[self.os_choice.GetStringSelection()]["Bootloader"] in ("GRUB-UEFI", "ELILO")) and (OS_INFO[self.os_choice.GetStringSelection()]["EFIPartition"] == "Unknown"):
            dlg = wx.MessageDialog(self.panel, "This OS has no UEFI partition, but you have a "
                                   + "UEFI bootloader installed! Please don't do any bootloader "
                                   + "operations on this operating system, or you may encounter "
                                   + "errors.", "WxFixBoot - Warning",
                                   style=wx.OK | wx.ICON_WARNING, pos=wx.DefaultPosition)

            dlg.ShowModal()
            dlg.Destroy()

        #Warn the user if we don't know what the bootloader is.
        if BOOTLOADER_INFO[self.os_choice.GetStringSelection()]["Bootloader"] == "Unknown":
            dlg = wx.MessageDialog(self.panel, "Couldn't determine the bootloader for this OS! "
                                   + "It may be not fully installed or removed. If you want to "
                                   + "fix this, please open the advanced options pulldown and "
                                   + "replace the bootloader with one of the selections there.", "WxFixBoot - Warning", style=wx.OK | wx.ICON_WARNING, pos=wx.DefaultPosition)
            dlg.ShowModal()
            dlg.Destroy()

        #Make sure the window displays properly.
        self.main_sizer.SetSizeHints(self)

    def on_osinfo(self, event=None): #pylint: disable=unused-argument
        """Hide/Show the OS info, and rotate the arrow"""
        if self.list_ctrl.IsShown():
            logger.debug("BootloaderOptionsWindow().on_osinfo(): Hiding OS Info...")
            self.arrow1.SetBitmap(self.right_arrow_image)

            self.main_sizer.Detach(self.list_ctrl)
            self.main_sizer.Detach(self.system_info_button)
            self.list_ctrl.Hide()
            self.system_info_button.Hide()

        else:
            logger.debug("BootloaderOptionsWindow().on_osinfo(): Showing OS Info...")
            self.arrow1.SetBitmap(self.down_arrow_image)

            self.main_sizer.Insert(4, self.list_ctrl, 5, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
            self.main_sizer.Insert(5, self.system_info_button, 1,
                                   wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)

            self.list_ctrl.Show()
            self.system_info_button.Show()

        #Make sure the window is displayed properly.
        self.main_sizer.SetSizeHints(self)
        self.panel.Layout()

    def on_basic_options(self, event=None): #pylint: disable=unused-argument
        """Hide/Show the basic options, and rotate the arrow"""
        if self.reinstall_bootloader_checkbox.IsShown():
            logger.debug("BootloaderOptionsWindow().on_basic_options(): Hiding Basic Options...")

            #Refuse to collapse this section if Advanced Settings are shown.
            if self.install_new_bootloader_checkbox.IsShown():
                logger.debug("BootloaderOptionsWindow().on_basic_options(): Cancelling because Advanced Options are shown...")
                return True

            self.arrow2.SetBitmap(self.right_arrow_image)

            self.main_sizer.Detach(self.fix_and_update_bootloader_sizer)
            self.main_sizer.Detach(self.timeout_sizer)
            self.main_sizer.Detach(self.defaultos_sizer)

            self.reinstall_bootloader_checkbox.Hide()
            self.update_bootloader_checkbox.Hide()
            self.keep_bootloader_timeout_checkbox.Hide()
            self.new_timeout_text.Hide()
            self.bootloader_timeout_spinner.Hide()
            self.defaultos_text.Hide()
            self.defaultos_choice.Hide()

        else:
            logger.debug("BootloaderOptionsWindow().on_basic_options(): Showing Basic Options...")
            self.arrow2.SetBitmap(self.down_arrow_image)

            #Find the first index to re-add items in main_sizer.
            if self.list_ctrl.IsShown():
                first_number = 8

            else:
                first_number = 6

            self.main_sizer.Insert(first_number, self.fix_and_update_bootloader_sizer,
                                   1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)

            self.main_sizer.Insert(first_number+1, self.timeout_sizer, 1,
                                   wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)

            self.main_sizer.Insert(first_number+2, self.defaultos_sizer, 1,
                                   wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)

            self.reinstall_bootloader_checkbox.Show()
            self.update_bootloader_checkbox.Show()
            self.keep_bootloader_timeout_checkbox.Show()
            self.new_timeout_text.Show()
            self.bootloader_timeout_spinner.Show()
            self.defaultos_text.Show()
            self.defaultos_choice.Show()

        #Make sure the window displays properly.
        self.main_sizer.SetSizeHints(self)
        self.panel.Layout()

    def on_advanced_options(self, event=None): #pylint: disable=unused-argument
        """Show/Hide the advanced options, and rotate the arrow"""
        if self.install_new_bootloader_checkbox.IsShown():
            logger.debug("BootloaderOptionsWindow().on_advanced_options(): Hiding Advanced Options...")
            self.arrow3.SetBitmap(self.right_arrow_image)

            self.main_sizer.Detach(self.kernel_options_sizer)
            self.main_sizer.Detach(self.install_new_bootloader_sizer)
            self.main_sizer.Detach(self.backup_bootloader_sizer)
            self.main_sizer.Detach(self.restore_bootloader_sizer)

            self.keep_kerneloptions_checkbox.Hide()
            self.new_kerneloptions_text.Hide()
            self.new_kerneloptions_textctrl.Hide()
            self.install_new_bootloader_checkbox.Hide()
            self.new_bootloader_choice.Hide()
            self.backup_bootloader_checkbox.Hide()
            self.backup_bootloader_text.Hide()
            self.backup_bootloader_choice.Hide()
            self.restore_bootloader_checkbox.Hide()
            self.restore_bootloader_text.Hide()
            self.restore_bootloader_choice.Hide()

        else:
            logger.debug("BootloaderOptionsWindow().on_advanced_options(): Showing Advanced Options...")

            #If Basic Options are hidden, show them.
            if self.reinstall_bootloader_checkbox.IsShown() is False:
                logger.debug("BootloaderOptionsWindow().on_advanced_options(): Showing Basic Options first...")
                self.on_basic_options()

            self.arrow3.SetBitmap(self.down_arrow_image)

            if self.list_ctrl.IsShown():
                first_number = 13

            else:
                first_number = 11

            self.main_sizer.Insert(first_number, self.kernel_options_sizer, 1,
                                   wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
            self.main_sizer.Insert(first_number+1, self.install_new_bootloader_sizer,
                                  1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)

            self.main_sizer.Insert(first_number+2, self.backup_bootloader_sizer,
                                   1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)

            self.main_sizer.Insert(first_number+3, self.restore_bootloader_sizer,
                                   1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)

            self.keep_kerneloptions_checkbox.Show()
            self.new_kerneloptions_text.Show()
            self.new_kerneloptions_textctrl.Show()
            self.install_new_bootloader_checkbox.Show()
            self.new_bootloader_choice.Show()
            self.backup_bootloader_checkbox.Show()
            self.backup_bootloader_text.Show()
            self.backup_bootloader_choice.Show()
            self.restore_bootloader_checkbox.Show()
            self.restore_bootloader_text.Show()
            self.restore_bootloader_choice.Show()

        #Make sure the window displays properly.
        self.main_sizer.SetSizeHints(self)
        self.panel.Layout()

    def on_backup_bootloader_choice(self, event=None): #pylint: disable=unused-argument
        """Allow the user to select a config file to backup the bootloader to"""
        logger.debug("BootloaderOptionsWindow().on_backup_bootloader_choice(): Selecting bootloader config backup file...")

        _file = self.backup_bootloader_choice.GetStringSelection()

        #Determine what to do here.
        if _file == "Specify File Path...":
            dlg = wx.FileDialog(self.panel, "Select Backup File...",
                                defaultDir="/home",
                                wildcard="All Files/Devices (*)|*|WxFixBoot Bootloader Config Backup (.wxfbc)|*.wxfbc",
                                style=wx.FD_SAVE)

            if dlg.ShowModal() == wx.ID_OK:
                _file = dlg.GetPath()
                logger.debug("BootloaderOptionsWindow().on_backup_bootloader_choice(): File is "+_file+"...")
                logger.debug("BootloaderOptionsWindow().on_backup_bootloader_choice(): Saving config to "+_file+"...")
                plistlib.writePlist(BOOTLOADER_INFO[self.os_choice.GetStringSelection()], _file) #pylint: disable=deprecated-method
                logger.debug("BootloaderOptionsWindow().on_backup_bootloader_choice(): Finished saving config to "+_file+"...")

                #Let the user know we were successful.
                msg_dlg = wx.MessageDialog(self.panel, "Finished backing up config to "+_file+"!",
                                           "Config Backup Successful", wx.OK | wx.ICON_INFORMATION,
                                           pos=wx.DefaultPosition)

                msg_dlg.ShowModal()
                msg_dlg.Destroy()

                #Reset the choicebox and checkbox.
                self.backup_bootloader_choice.SetStringSelection("-- Please Select --")
                self.backup_bootloader_checkbox.SetValue(0)
                self.on_backup_bootloader_checkbox()

            else:
                #Reset choice box.
                self.backup_bootloader_choice.SetStringSelection("-- Please Select --")

            dlg.Destroy()

    def on_restore_bootloader_choice(self, event=None): #pylint: disable=unused-argument
        """Allow the user to select a config file to restore the bootloader from"""
        logger.debug("BootloaderOptionsWindow().on_restore_bootloader_choice(): Selecting bootloader config backup file...")

        _file = self.restore_bootloader_choice.GetStringSelection()

        #Determine what to do here.
        if _file == "Specify File Path...":
            dlg = wx.FileDialog(self.panel, "Select Backup File...",
                                defaultDir="/home",
                                wildcard="All Files/Devices (*)|*|WxFixBoot Bootloader Config Backup (.wxfbc)|*.wxfbc",
                                style=wx.FD_OPEN)

            if dlg.ShowModal() == wx.ID_OK:
                _file = dlg.GetPath()
                logger.debug("BootloaderOptionsWindow().on_restore_bootloader_choice(): Loading config from "+_file+"...")

                try:
                    self.setup_for_restoring_bootloader(plistlib.readPlistFromString(_file))

                except Exception:
                    #Error!
                    logger.error("BootloaderOptionsWindow().on_restore_bootloader_choice(): Error when loading config! Warning user and reloading previous settings...")

                    #Let the user know about the error.
                    msg_dlg = wx.MessageDialog(self.panel,
                                               "Couldn't load config from "+_file+"! Are you sure you selected the right file? WxFixBoot will revert back to the previous settings now.",
                                               "Config Load Failed!", wx.OK | wx.ICON_ERROR,
                                               pos=wx.DefaultPosition)

                    msg_dlg.ShowModal()
                    msg_dlg.Destroy()

                    #Reload previous settings.
                    self.on_oschoice_change()

                else:
                    logger.debug("BootloaderOptionsWindow().on_restore_bootloader_choice(): Successfully loaded config from "+_file+"...")

                    #Let the user know we were successful.
                    msg_dlg = wx.MessageDialog(self.panel,
                                               "The bootloader configuration was successfully loaded. Please review the changes in this window, and then continue if you are satisfied.",
                                               "WxFixBoot - Information",
                                               style=wx.OK | wx.ICON_INFORMATION,
                                               pos=wx.DefaultPosition)

                    msg_dlg.ShowModal()
                    msg_dlg.Destroy()

                    #Reset the choicebox and checkbox.
                    self.restore_bootloader_choice.SetStringSelection("-- Please Select --")
                    self.restore_bootloader_checkbox.SetValue(0)

            else:
                #Reset choice box.
                self.restore_bootloader_choice.SetStringSelection("-- Please Select --")

            dlg.Destroy()

    def setup_for_restoring_bootloader(self, config):
        """Setup the window to use the configuration from the chosen bootloader config backup file"""
        _os = self.os_choice.GetStringSelection()

        #Check this is the right config for this OS.
        if config["OSName"] != _os:
            dlg = wx.MessageDialog(self.panel, "This config file is config for "+config["OSName"]
                                   + ", not "+_os+", the current OS. Please change the selected "
                                   + "OS, or select the correct config file for this OS.",
                                   "WxFixBoot - Error", style=wx.OK | wx.ICON_ERROR,
                                   pos=wx.DefaultPosition)

            dlg.ShowModal()
            dlg.Destroy()
            return True

        #Check the bootloader in the config file can be installed in this OS.
        if self.new_bootloader_choice.FindString(config["Bootloader"]) == -1 and config["Bootloader"] != BOOTLOADER_INFO[_os]["Bootloader"]:
            dlg = wx.MessageDialog(self.panel, "The bootloader installed at the time the config "
                                   + "was backed up cannot be installed in this OS. Most likely, "
                                   + "the config file has been tampered with or has corrupted.",
                                   "WxFixBoot - Error", style=wx.OK | wx.ICON_ERROR,
                                   pos=wx.DefaultPosition)

            dlg.ShowModal()
            dlg.Destroy()
            return True

        #Disable the restore config checkbox.
        self.restore_bootloader_choice.SetStringSelection("-- Please Select --")
        self.restore_bootloader_checkbox.SetValue(0)
        self.on_restore_bootloader_checkbox()

        #Determine if the current bootloader is the same as the backed up one. 
        if config["Bootloader"] == BOOTLOADER_INFO[_os]["Bootloader"] and config["Bootloader"] not in ("GRUB-LEGACY", "Unknown"):
            #Set up to reinstall the current bootloader.
            self.reinstall_bootloader_checkbox.Enable()
            self.reinstall_bootloader_checkbox.SetValue(1)
            self.on_update_or_reinstall_checkbox()

        elif config["Bootloader"] != "GRUB-LEGACY" and BOOTLOADER_INFO[_os]["Bootloader"] not in ("GRUB-LEGACY", "Unknown"):
            #Set up to replace the current bootloader with the old one.
            self.install_new_bootloader_checkbox.Enable()
            self.install_new_bootloader_checkbox.SetValue(1)
            self.new_bootloader_choice.SetStringSelection(config["Bootloader"])
            self.on_install_new_bootloader_checkbox()

        else:
            #Don't allow the user to attempt to switch back to GRUB-LEGACY, or replace it. TODO Can this be done a better way?
            raise RuntimeError

        #Use kernel options used when the backup was taken.
        self.keep_kerneloptions_checkbox.SetValue(0)
        self.on_kerneloptions_checkbox()
        self.new_kerneloptions_textctrl.SetValue(config["GlobalKernelOptions"])

        #Use timeout used when the backup was taken.
        self.keep_bootloader_timeout_checkbox.SetValue(0)
        self.on_timeout_checkbox()
        self.bootloader_timeout_spinner.SetValue(config["Timeout"])

        #Use default OS used when the backup was taken.
        if config["DefaultOS"] in OS_INFO.keys():
            self.defaultos_choice.SetStringSelection(config["DefaultOS"])

        else:
            dlg = wx.MessageDialog(self.panel, "This default OS used when this config was backed "
                                   + "up was not detected by WxFixBoot. Instead, "+_os+" will be "
                                   + "used, or you can make a custom selection.",
                                   "WxFixBoot - Information", wx.OK | wx.ICON_INFORMATION)

            dlg.ShowModal()
            dlg.Destroy()
            self.defaultos_choice.SetStringSelection(_os)

        logger.debug("BootloaderOptionsWindow().setup_for_restoring_bootloader(): Finished loading config from file...")

    def on_update_or_reinstall_checkbox(self, event=None): #pylint: disable=unused-argument
        """Enable/Disable options, based on the value of the update/reinstall checkboxes."""
        logger.debug("BootloaderOptionsWindow().on_update_or_reinstall_checkbox(): Enabling and Disabling options as needed...")
 
        if self.reinstall_bootloader_checkbox.IsChecked():
            self.update_bootloader_checkbox.Disable()
            self.keep_bootloader_timeout_checkbox.Enable()
            self.keep_bootloader_timeout_checkbox.SetValue(1)
            self.keep_kerneloptions_checkbox.Enable()
            self.keep_kerneloptions_checkbox.SetValue(1)
            self.defaultos_choice.Enable()
            self.install_new_bootloader_checkbox.SetValue(0)
            self.install_new_bootloader_checkbox.Disable()
            self.new_bootloader_choice.Disable()
            self.restore_bootloader_checkbox.Disable()
            self.restore_bootloader_choice.Disable()

        elif self.update_bootloader_checkbox.IsChecked():
            self.reinstall_bootloader_checkbox.Disable()
            self.keep_bootloader_timeout_checkbox.Enable()
            self.keep_bootloader_timeout_checkbox.SetValue(1)
            self.keep_kerneloptions_checkbox.Enable()
            self.keep_kerneloptions_checkbox.SetValue(1)
            self.defaultos_choice.Enable()
            self.install_new_bootloader_checkbox.SetValue(0)
            self.install_new_bootloader_checkbox.Disable()
            self.new_bootloader_choice.Disable()
            self.restore_bootloader_checkbox.Disable()
            self.restore_bootloader_choice.Disable()

        else:
            self.reinstall_bootloader_checkbox.Enable()
            self.update_bootloader_checkbox.Enable()
            self.keep_bootloader_timeout_checkbox.SetValue(0)
            self.keep_bootloader_timeout_checkbox.Disable()
            self.keep_kerneloptions_checkbox.SetValue(0)
            self.keep_kerneloptions_checkbox.Disable()
            self.bootloader_timeout_spinner.Disable()
            self.new_kerneloptions_textctrl.Disable()
            self.defaultos_choice.Disable()
            self.install_new_bootloader_checkbox.Enable()
            self.new_bootloader_choice.Disable()
            self.restore_bootloader_checkbox.Enable()
            self.restore_bootloader_choice.Disable()

    def on_kerneloptions_checkbox(self, event=None): #pylint: disable=unused-argument
        """Enable/Disable the kernel options text ctrl, based on the value of the kernel options checkbox."""
        logger.debug("BootloaderOptionsWindow().on_kerneloptions_checkbox(): Enabling and Disabling options as needed...")

        if self.keep_kerneloptions_checkbox.IsChecked():
            self.new_kerneloptions_textctrl.SetValue(BOOTLOADER_INFO[self.os_choice.GetStringSelection()]["Settings"]["NewKernelOptions"])
            self.new_kerneloptions_textctrl.Disable()

        else:
            self.new_kerneloptions_textctrl.Enable()

    def on_timeout_checkbox(self, event=None): #pylint: disable=unused-argument
        """Enable/Disable the bootloader timeout spinner, based on the value of the timeout checkbox."""
        logger.debug("BootloaderOptionsWindow().on_timeout_checkbox(): Enabling and Disabling options s needed...")

        if self.keep_bootloader_timeout_checkbox.IsChecked():
            self.bootloader_timeout_spinner.SetValue(BOOTLOADER_INFO[self.os_choice.GetStringSelection()]["Settings"]["NewTimeout"])
            self.bootloader_timeout_spinner.Disable()

        else:
            self.bootloader_timeout_spinner.Enable()

    def on_backup_bootloader_checkbox(self, event=None): #pylint: disable=unused-argument
        """Enable/Disable the bootloader timeout spinner, based on the value of the timeout checkbox."""
        logger.debug("BootloaderOptionsWindow().on_backup_bootloader_checkbox(): Enabling and Disabling options as needed...")

        if self.backup_bootloader_checkbox.IsChecked():
            self.backup_bootloader_choice.Enable()

        else:
            self.backup_bootloader_choice.Disable()

    def on_restore_bootloader_checkbox(self, event=None): #pylint: disable=unused-argument
        """Enable/Disable options, based on the value of the timeout checkbox."""
        logger.debug("BootloaderOptionsWindow(). Enabling and disabling options as needed...")

        if self.restore_bootloader_checkbox.IsChecked():
            self.restore_bootloader_choice.Enable()
            self.reinstall_bootloader_checkbox.Disable()
            self.update_bootloader_checkbox.Disable()
            self.install_new_bootloader_checkbox.Disable()
            self.new_bootloader_choice.Disable()

        else:
            self.restore_bootloader_choice.Disable()
            self.reinstall_bootloader_checkbox.Enable()
            self.update_bootloader_checkbox.Enable()
            self.install_new_bootloader_checkbox.Enable()
            self.new_bootloader_choice.Disable()

        #Don't allow the user to attempt to modify GRUB-LEGACY.
        if BOOTLOADER_INFO[self.os_choice.GetStringSelection()]["Bootloader"] in ("GRUB-LEGACY", "Unknown"):
            self.reinstall_bootloader_checkbox.Disable()
            self.update_bootloader_checkbox.Disable()

        #Don't allow replacing grub-legacy.
        if BOOTLOADER_INFO[self.os_choice.GetStringSelection()]["Bootloader"] == "GRUB-LEGACY":
            self.install_new_bootloader_checkbox.Disable()

    def on_install_new_bootloader_checkbox(self, event=None): #pylint: disable=unused-argument
        """Enable/Disable options, based on the value of the new bootloader checkbox."""
        logger.debug("BootloaderOptionsWindow().on_install_new_bootloader_checkbox(): Enabling and disabling options as needed...")

        if self.install_new_bootloader_checkbox.IsChecked():
            self.new_bootloader_choice.Enable()
            self.reinstall_bootloader_checkbox.Disable()
            self.update_bootloader_checkbox.Disable()
            self.keep_bootloader_timeout_checkbox.Enable()
            self.keep_bootloader_timeout_checkbox.SetValue(1)
            self.keep_kerneloptions_checkbox.Enable()
            self.keep_kerneloptions_checkbox.SetValue(1)
            self.defaultos_choice.Enable()
            self.restore_bootloader_checkbox.Disable()
            self.restore_bootloader_choice.Disable()

        else:
            self.new_bootloader_choice.Disable()
            self.new_bootloader_choice.SetStringSelection("-- Please Select --")
            self.reinstall_bootloader_checkbox.Enable()
            self.update_bootloader_checkbox.Enable()
            self.keep_bootloader_timeout_checkbox.SetValue(0)
            self.keep_bootloader_timeout_checkbox.Disable()
            self.keep_kerneloptions_checkbox.SetValue(0)
            self.keep_kerneloptions_checkbox.Disable()
            self.bootloader_timeout_spinner.Disable()
            self.new_kerneloptions_textctrl.Disable()
            self.defaultos_choice.Disable()
            self.restore_bootloader_checkbox.Enable()
            self.restore_bootloader_choice.Disable()

        #Don't allow the user to attempt to modify GRUB-LEGACY.
        if BOOTLOADER_INFO[self.os_choice.GetStringSelection()]["Bootloader"] in ("GRUB-LEGACY", "Unknown"):
            self.reinstall_bootloader_checkbox.Disable()
            self.update_bootloader_checkbox.Disable()

        #Don't allow replacing grub-legacy.
        if BOOTLOADER_INFO[self.os_choice.GetStringSelection()]["Bootloader"] == "GRUB-LEGACY":
            self.install_new_bootloader_checkbox.Disable()

    def on_new_bootloader_choice(self, event=None): #pylint: disable=unused-argument
        """Warn user about LILO's/ELILO's rubbish multi OS support if needed""" #TODO Offer to disable?
        if len(SYSTEM_INFO["ModifyableOSs"]) > 1 and self.new_bootloader_choice.GetStringSelection() in ("LILO", "ELILO"):
            dlg = wx.MessageDialog(self.panel, "Installing "
                                   + self.new_bootloader_choice.GetStringSelection()
                                   + " is discouraged because you have more than one Linux OS "
                                   + "installed, and this bootloader has poor support for booting "
                                   + "multiple Linux OSs. Click okay to continue.",
                                   "WxFixBoot - Warning", wx.OK | wx.ICON_WARNING)

            dlg.ShowModal()
            dlg.Destroy()

    def save_settings(self, event=None, _os=None): #pylint: disable=unused-argument
        """Save all settings for this OS from the checkboxes and choice boxes"""
        logger.debug("BootloaderOptionsWindow().save_settings(): Saving settings for "+_os+"...")

        #Check that the settings are valid.
        if self.install_new_bootloader_checkbox.IsChecked() and self.new_bootloader_choice.GetStringSelection() == "-- Please Select --":
            logger.warning("BootloaderOptionsWindow().save_settings(): Aborting saving settings because bootloader is being replaced, but its replacement is unspecified...")
            dlg = wx.MessageDialog(self.panel, "If you're going to replace "
                                   + BOOTLOADER_INFO[_os]["Bootloader"]+", you must select a new "
                                   + "bootloader to replace it with!", "WxFixBoot - Warning",
                                   wx.OK | wx.ICON_WARNING)

            dlg.ShowModal()
            dlg.Destroy()
            raise RuntimeError

        BOOTLOADER_INFO[_os]["Settings"]["Reinstall"] = self.reinstall_bootloader_checkbox.GetValue()
        BOOTLOADER_INFO[_os]["Settings"]["Update"] = self.update_bootloader_checkbox.GetValue()
        BOOTLOADER_INFO[_os]["Settings"]["KeepExistingTimeout"] = self.keep_bootloader_timeout_checkbox.GetValue()
        BOOTLOADER_INFO[_os]["Settings"]["NewTimeout"] = self.bootloader_timeout_spinner.GetValue()
        BOOTLOADER_INFO[_os]["Settings"]["KeepExistingKernelOptions"] = self.keep_kerneloptions_checkbox.GetValue()
        BOOTLOADER_INFO[_os]["Settings"]["NewKernelOptions"] = self.new_kerneloptions_textctrl.GetValue()
        BOOTLOADER_INFO[_os]["Settings"]["DefaultOS"] = self.defaultos_choice.GetStringSelection()
        BOOTLOADER_INFO[_os]["Settings"]["DefaultBootDevice"] = BOOTLOADER_INFO[BOOTLOADER_INFO[_os]["Settings"]["DefaultOS"]]["DefaultBootDevice"]
        BOOTLOADER_INFO[_os]["Settings"]["InstallNewBootloader"] = self.install_new_bootloader_checkbox.GetValue()
        BOOTLOADER_INFO[_os]["Settings"]["NewBootloader"] = self.new_bootloader_choice.GetStringSelection()
        BOOTLOADER_INFO[_os]["Settings"]["BackupBootloader"] = self.backup_bootloader_checkbox.GetValue()
        BOOTLOADER_INFO[_os]["Settings"]["BootloaderBackupTarget"] = self.backup_bootloader_choice.GetStringSelection()
        BOOTLOADER_INFO[_os]["Settings"]["RestoreBootloader"] = self.restore_bootloader_checkbox.GetValue()
        BOOTLOADER_INFO[_os]["Settings"]["BootloaderRestoreSource"] = self.restore_bootloader_choice.GetStringSelection()

        if BOOTLOADER_INFO[_os]["Settings"]["Reinstall"] or BOOTLOADER_INFO[_os]["Settings"]["Update"] or BOOTLOADER_INFO[_os]["Settings"]["InstallNewBootloader"] or BOOTLOADER_INFO[_os]["Settings"]["RestoreBootloader"]:
            logger.debug("BootloaderOptionsWindow().save_settings(): "+_os+" is being modified...")
            BOOTLOADER_INFO[_os]["Settings"]["ChangeThisOS"] = True

        else:
            logger.debug("BootloaderOptionsWindow().save_settings(): "+_os+" is not being modified...")
            BOOTLOADER_INFO[_os]["Settings"]["ChangeThisOS"] = False

    def save_gui_state(self, event=None, _os=None): #pylint: disable=unused-argument
        """Save all the GUI element's states (enabled/disabled) for this _os"""
        logger.debug("BootloaderOptionsWindow().save_gui_state(): Saving GUI state for "+_os+"...")
        BOOTLOADER_INFO[_os]["GUIState"]["ReinstallCheckBoxState"] = self.reinstall_bootloader_checkbox.IsEnabled()
        BOOTLOADER_INFO[_os]["GUIState"]["UpdateCheckBoxState"] = self.update_bootloader_checkbox.IsEnabled()
        BOOTLOADER_INFO[_os]["GUIState"]["KeepExistingTimeoutCheckBoxState"] = self.keep_bootloader_timeout_checkbox.IsEnabled()
        BOOTLOADER_INFO[_os]["GUIState"]["NewTimeoutSpinnerState"] = self.bootloader_timeout_spinner.IsEnabled()
        BOOTLOADER_INFO[_os]["GUIState"]["KeepExistingKernelOptionsCheckBoxState"] = self.keep_kerneloptions_checkbox.IsEnabled()
        BOOTLOADER_INFO[_os]["GUIState"]["NewKernelOptionsTextCtrlState"] = self.new_kerneloptions_textctrl.IsEnabled()
        BOOTLOADER_INFO[_os]["GUIState"]["DefaultOSChoiceState"] = self.defaultos_choice.IsEnabled()
        BOOTLOADER_INFO[_os]["GUIState"]["InstallNewBootloaderCheckBoxState"] = self.install_new_bootloader_checkbox.IsEnabled()
        BOOTLOADER_INFO[_os]["GUIState"]["NewBootloaderChoiceState"] = self.new_bootloader_choice.IsEnabled()
        BOOTLOADER_INFO[_os]["GUIState"]["BackupBootloaderCheckBoxState"] = self.backup_bootloader_checkbox.IsEnabled()
        BOOTLOADER_INFO[_os]["GUIState"]["BackupBootloaderChoiceState"] = self.backup_bootloader_choice.IsEnabled()
        BOOTLOADER_INFO[_os]["GUIState"]["RestoreBootloaderCheckBoxState"] = self.restore_bootloader_checkbox.IsEnabled()
        BOOTLOADER_INFO[_os]["GUIState"]["RestoreBootloaderChoiceState"] = self.restore_bootloader_choice.IsEnabled()

    def on_close(self, event=None): #pylint: disable=unused-argument
        """Save settings and GUI state, and then close BootloaderOptionsWindow"""
        logger.debug("BootloaderOptionsWindow().on_close(): Closing BootloaderOptionsWindow...")
        self.save_settings(_os=self.os_choice.GetStringSelection())
        self.save_gui_state(_os=self.os_choice.GetStringSelection())

        #Send a message to MainWindow so it can refresh.
        wx.CallAfter(self.parent_window.refresh_main_window)

        self.Destroy()

#End New Bootloader Options Window.
#Begin Progress Window
class ProgressWindow(wx.Frame):
    def __init__(self):
        """Initialse Progress Window"""
        wx.Frame.__init__(self, parent=None, title="WxFixBoot - Operations Progress",
                          size=(500, 300), style=wx.CAPTION|wx.MINIMIZE|wx.RESIZE_BORDER)

        self.panel = wx.Panel(self)
        self.SetClientSize(wx.Size(500, 300))
        wx.Frame.SetIcon(self, APPICON)

        self.create_text()
        self.create_buttons()
        self.create_progressbars()

        #Create the output box and log.
        self.output_box = wx.TextCtrl(self.panel, -1, "", size=(480, 240),
                                      style=wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_WORDWRAP)

        self.output_box.SetBackgroundColour((0, 0, 0))
        self.output_box.SetDefaultStyle(wx.TextAttr(wx.WHITE))

        global OUTPUT_LOG
        OUTPUT_LOG = []

        #Setup the rest of the window.
        self.setup_sizers()
        self.bind_events()

        #Make sure the panel displays properly.
        self.panel.Layout()

        logger.debug("ProgressWindow().__init__(): Progress Window Started.")
        logger.debug("ProgressWindow().__init__(): Starting Backend Thread...")

        self.running_operations = True

        BackendThread(self)

    def create_text(self):
        """Create the Text"""
        self.performing_operations_text = wx.StaticText(self.panel, -1, "WxFixBoot is performing operations... Please wait.")
        self.current_operating_heading_text = wx.StaticText(self.panel, -1, "Current Operation:")
        self.current_operating_text = wx.StaticText(self.panel, -1, "Initializating...")
        self.current_operation_progress_text = wx.StaticText(self.panel, -1, "Current Operation Progress:")
        self.overall_progress_text = wx.StaticText(self.panel, -1, "Overall Progress:")

    def create_buttons(self):
        """Create buttons."""
        self.show_output_button = wx.ToggleButton(self.panel, -1, "Show Terminal Output")
        self.restart_button = wx.Button(self.panel, -1, "Restart WxFixBoot")
        self.exit_button = wx.Button(self.panel, -1, "Exit")
        self.restart_button.Disable()
        self.exit_button.Disable()

    def create_progressbars(self):
        """Create both progress bars"""
        #Create the progress bar for the current operation.
        self.current_operation_progress_bar = wx.Gauge(self.panel, -1, 100)
        self.current_operation_progress_bar.SetBezelFace(3)
        self.current_operation_progress_bar.SetShadowWidth(3)
        self.current_operation_progress_bar.SetValue(0)
        self.current_operation_progress_bar.Show()

        #Create the progress bar for overall progress.
        self.overall_progress_bar = wx.Gauge(self.panel, -1, 100)
        self.overall_progress_bar.SetBezelFace(3)
        self.overall_progress_bar.SetShadowWidth(3)
        self.overall_progress_bar.SetValue(0)
        self.overall_progress_bar.Show()

    def setup_sizers(self):
        """Setup sizers for Progress Window"""
        #Create the Main Sizer.
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)

        #Create the first button sizer.
        button_sizer_1 = wx.BoxSizer(wx.HORIZONTAL)

        #Create the second button sizer.
        button_sizer_2 = wx.BoxSizer(wx.HORIZONTAL)

        #Add items to the first button sizer.
        button_sizer_1.Add(self.restart_button, 1, wx.RIGHT, 5)
        button_sizer_1.Add((5,5), 1, wx.LEFT|wx.RIGHT, 5)
        button_sizer_1.Add(self.show_output_button, 1, wx.LEFT|wx.RIGHT, 5)

        #Add items to the second button sizer.
        button_sizer_2.Add((5,5), 1, wx.RIGHT, 5)
        button_sizer_2.Add(self.exit_button, 1, wx.LEFT|wx.RIGHT, 5)
        button_sizer_2.Add((5,5), 1, wx.LEFT|wx.RIGHT, 5)

        #Add items to the main sizer.
        self.main_sizer.Add(self.performing_operations_text, 0, wx.ALL|wx.ALIGN_CENTER, 10)
        self.main_sizer.Add(self.current_operating_heading_text, 0,
                            wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.ALIGN_CENTER, 10)

        self.main_sizer.Add(self.current_operating_text, 0,
                            wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.ALIGN_CENTER, 10)

        self.main_sizer.Add(self.current_operation_progress_text, 0,
                            wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.ALIGN_CENTER, 10)

        self.main_sizer.Add(self.current_operation_progress_bar, 0,
                            wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)

        self.main_sizer.Add(self.overall_progress_text, 0,
                            wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.ALIGN_CENTER, 10)

        self.main_sizer.Add(self.overall_progress_bar, 0, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        self.main_sizer.Add(button_sizer_1, 0, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        self.main_sizer.Add(self.output_box, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        self.main_sizer.Add(button_sizer_2, 0, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)

        self.show_output()

        #Get the sizer set up for the frame.
        self.panel.SetSizer(self.main_sizer)
        self.main_sizer.SetMinSize(wx.Size(500, 300))
        self.main_sizer.SetSizeHints(self)

    def bind_events(self):
        """Bind events for Progress Window"""
        self.Bind(wx.EVT_TOGGLEBUTTON, self.show_output, self.show_output_button)
        self.Bind(wx.EVT_BUTTON, self.restart_wxfixboot, self.restart_button)
        self.Bind(wx.EVT_QUERY_END_SESSION, self.session_ending)
        self.Bind(wx.EVT_BUTTON, self.on_exit, self.exit_button)
        self.Bind(wx.EVT_CLOSE, self.on_exit)

        #Prevent focus on Output Box.
        self.output_box.Bind(wx.EVT_SET_FOCUS, self.focus_on_output_button)

    def focus_on_output_button(self, event=None): #pylint: disable=unused-argument
        """Focus on the show output button instead of the TextCtrl, and reset the insertion point back after 30 milliseconds, preventing the user from changing the insertion point and messing the formatting up."""
        #Just a slightly hacky way of trying to make sure the user can't change the insertion
        #point! Works unless you start doing silly stuff like tapping on the output box
        #constantly :)
        self.show_output_button.SetFocus()
        insertion_point = self.output_box.GetInsertionPoint()
        wx.CallLater(30, self.output_box.SetInsertionPoint, insertion_point)

    def show_output(self, event=None): #pylint: disable=unused-argument
        """Show and Hide the output box in ProgressWindow()"""
        logger.debug("ProgressWindow().show_output() was Toggled to position: "+unicode(self.show_output_button.GetValue())+", where True = Depressed and vice versa.")
        if self.show_output_button.GetValue():
            #Remove the empty space.
            self.main_sizer.Detach(8)

            #Show the output box.
            self.main_sizer.Insert(8, self.output_box, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
            self.output_box.Show()

        else:
            #Hide the output box.
            self.main_sizer.Detach(self.output_box)
            self.output_box.Hide()

            #Insert some empty space.
            self.main_sizer.Insert(8, (1,1), 1, wx.EXPAND)

        #Call Layout() on self.panel() to ensure it displays properly.
        self.panel.Layout()
        self.main_sizer.SetSizeHints(self)

    def carriagereturn(self):
        """Handles carriage returns in output"""
        #Go back until the last newline character, and overwrite anything in the way on the next
        #write. Get the current insertion point.
        current_insertion_point = self.output_box.GetInsertionPoint()

        #Get the text up to the current insertion point.
        text = self.output_box.GetRange(0, current_insertion_point)

        #Find the last newline char in the text.
        newline_nos = []
        counter = 0
        for char in text:
            if char == "\n":
                newline_nos.append(counter)

            counter += 1

        if newline_nos != []:
            last_newline = newline_nos[-1]

        else:
            #Hacky bit to make the new insertion point 0 :)
            last_newline = -1

        #Set the insertion point to just after that newline, unless we're already there, and in
        #that case set the insertion point just after the previous newline.
        new_insertion_point = last_newline + 1

        self.output_box.SetInsertionPoint(new_insertion_point)

    def backspace(self):
        """Handles backspaces in output"""
        #Move the insertion point 1 char to the left.
        self.output_box.SetInsertionPoint(self.output_box.GetInsertionPoint()-1)

    def update_output_box(self, line, show_output=True):
        """Update the output box, and add lines to the list"""
        #Add the line to the output log.
        global OUTPUT_LOG
        OUTPUT_LOG.append(line)

        if show_output or SETTINGS["FullVerbosity"]:
            temp_line = ""

            for char in line:
                if char != "\r" and char != "\x08":
                    temp_line += char

                    if char == "\n":
                        self.add_line_to_output_box(temp_line, _type="None")
                        temp_line = ""

                else:
                    if char == "\r":
                        _type = "CR"

                    elif char == "\x08":
                        _type = "BKSP"

                    self.add_line_to_output_box(temp_line, _type)
                    temp_line = ""

    def add_line_to_output_box(self, line, _type):
        insertion_point = self.output_box.GetInsertionPoint()

        self.output_box.Replace(insertion_point, insertion_point+len(line), line)

        if _type == "CR":
            self.carriagereturn()

        elif _type == "BKSP":
            self.backspace()

    def update_current_progress(self,msg):
        """Update the progress of the current progress progress bar"""
        #Called at various points during operation code.
        self.current_operation_progress_bar.SetValue(int(msg))

        if self.current_operation_progress_bar.GetValue() == 100:
            self.update_total_progress()

            #Stop this resetting when all operations are complete.
            if self.overall_progress_bar.GetValue() != 100:
                self.current_operation_progress_bar.SetValue(0)

    def update_total_progress(self):
        """Update the progress of the overall progress progress bar"""
        #This is called when self.current_operation_progress_bar reaches 100 (aka full).
        if self.overall_progress_bar.GetValue() < 100:
            self.overall_progress_bar.SetValue(self.overall_progress_bar.GetValue()
                                               +(100//NUMBER_OF_OPERATIONS))

    def update_current_operation_text(self, message):
        """Keep the current operations status text up to date."""
        self.current_operating_text.SetLabel(message)
        self.panel.Layout()

    def backend_thread_finished(self):
        """Called when the BackendThread is finished, enables self.restart_button and self.exit_button"""
        self.running_operations = False
        self.restart_button.Enable()
        self.exit_button.Enable()

    def restart_wxfixboot(self, event=None): #pylint: disable=unused-argument
        """Restart WxFixBoot"""
        logger.debug("ProgressWindow().restart_wxfixboot(): Restarting WxFixBoot...")
        logger.debug("ProgressWindow().restart_wxfixboot(): Checking no filesystems are mounted in the temporary directory, and unmounting them if they are...")

        if os.path.exists("/tmp/wxfixboot/mountpoints/dev"):
            for _dir in os.listdir("/tmp/wxfixboot/mountpoints/dev"):
                #Call CoreTools.unmount() on each directory to make sure that nothing is mounted
                #there after this point.
                if CoreTools.unmount("/tmp/wxfixboot/mountpoints/dev/"+_dir) != 0:
                    #If we errored try removing chroot and trying again.
                    logger.warning("ProgressWindow().restart_wxfixboot(): Failed to unmount /tmp/wxfixboot/mountpoints/dev/"+_dir+"! Trying to remove chroot first then trying again...")
                    CoreTools.teardown_chroot("/tmp/wxfixboot/mountpoints/dev/"+_dir)

                    if CoreTools.unmount("/tmp/wxfixboot/mountpoints/dev/"+_dir) != 0:
                        logger.error("ProgressWindow().restart_wxfixboot(): Couldn't unmount /tmp/wxfixboot/mountpoints/dev/"+_dir+"! Giving up, warning user, and aborting restart...")
                        dlg = wx.MessageDialog(self.panel, "Couldn't restart WxFixBoot because "
                                               + "there are mounted filesystems in the temporary "
                                               + "directory! Please try restarting your system "
                                               + "and then try again.", "WxFixBoot - Error!",
                                               wx.OK | wx.ICON_ERROR)

                        dlg.ShowModal()
                        dlg.Destroy()
                        return False

        self.Hide()

        global RESTARTING
        RESTARTING = True

        #Make sure any pending output box events are processed now, to avoid errors later.
        wx.Yield()

        #Destroy ProgressWindow.                
        self.Destroy()

        InitialWindow().Show()

    def session_ending(self, event): #pylint: disable=unused-argument
        """Attempt to veto e.g. a shutdown/logout event if recovering data."""
        #Check if we can veto the shutdown.
        logger.warning("ProgressWindow().session_ending(): Attempting to veto system shutdown / logoff...")

        if event.CanVeto() and self.running_operations:
            #Veto the shutdown and warn the user.
            event.Veto(True)
            logger.info("ProgressWindow().session_ending(): Vetoed system shutdown / logoff...")
            dlg = wx.MessageDialog(self.panel, "You can't shutdown or logoff while recovering "
                                   + "data!", "WxFixBoot - Error!", wx.OK | wx.ICON_ERROR)

            dlg.ShowModal()
            dlg.Destroy()

        else:
            #Set SESSION_ENDING to True, call on_exit.
            logger.critical("ProgressWindow().session_ending(): Cannot veto system shutdown / logoff! Cleaning up...")
            global SESSION_ENDING
            SESSION_ENDING = True
            self.on_exit()

    def on_exit(self, event=None): #pylint: disable=unused-argument
        """Exits the programs, and sorts out log file saving/deleting stuff"""
        #Check if the session is ending.
        if SESSION_ENDING:
            #Delete the log file and exit ASAP.
            logging.shutdown()
            os.remove("/tmp/wxfixboot.log")
            self.Destroy()

        dlg = wx.MessageDialog(self.panel, 'Are you sure you want to exit?',
                               'WxFixBoot - Question!', wx.YES_NO | wx.ICON_QUESTION)

        answer = dlg.ShowModal()
        dlg.Destroy()

        if answer == wx.ID_YES:
            #Run the exit sequence
            logger.info("ProgressWindow().on_exit(): Exiting...")

            #Shutdown the logger.
            logging.shutdown()

            #Prompt user to save the log file.
            dlg = wx.MessageDialog(self.panel, "Do you want to keep WxFixBoot's log file? For "
                                   + "privacy reasons, WxFixBoot will delete its log file when "
                                   + "closing. If you want to save it, which is helpful for "
                                   + "debugging if something went wrong, click yes, and otherwise "
                                   + "click no.", "WxFixBoot - Question",
                                   style=wx.YES_NO | wx.ICON_QUESTION, pos=wx.DefaultPosition)

            answer = dlg.ShowModal()
            dlg.Destroy()

            if answer == wx.ID_YES:
                #Ask the user where to save it.
                dlg = wx.FileDialog(self.panel, "Save log file to...", defaultDir="/home",
                                    wildcard="Log Files (*.log)|*.log",
                                    style=wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT)

                answer = dlg.ShowModal()
                _file = dlg.GetPath()
                dlg.Destroy()

                if answer == wx.ID_OK:
                    #Copy it to the specified path, using a one-liner, and don't bother handling
                    #any errors, because this is run as root. FIXME Bad idea.
                    CoreTools.start_process("cp /tmp/wxfixboot.log "+_file)

                    dlg = wx.MessageDialog(self.panel, 'Done! WxFixBoot will now exit.',
                                           'WxFixBoot - Information', wx.OK | wx.ICON_INFORMATION)
                    dlg.ShowModal()
                    dlg.Destroy()

                else:
                    dlg = wx.MessageDialog(self.panel, "Okay, WxFixBoot will now exit without "
                                           + "saving the log file.", 'WxFixBoot - Information',
                                           wx.OK | wx.ICON_INFORMATION)

                    dlg.ShowModal()
                    dlg.Destroy()

            else:
                dlg = wx.MessageDialog(self.panel, "Okay, WxFixBoot will now exit without saving "
                                       + "the log file.", 'WxFixBoot - Information',
                                       wx.OK | wx.ICON_INFORMATION)

                dlg.ShowModal()
                dlg.Destroy()

            #Delete the log file, and don't bother handling any errors, because this is run as root.
            os.remove('/tmp/wxfixboot.log')

            self.Destroy()

#End Progress Window
#Begin Backend Thread
class BackendThread(threading.Thread):
    def __init__(self, parent_window):
        """Initialize BackendThread"""
        #Set up the backend tools.
        self.parent_window = parent_window

        #Start the main part of this thread.
        threading.Thread.__init__(self)
        self.start()

    def run(self):
        """Do setup, and call self.start_operations()"""
        #Log the BackendThread start event (in debug mode).
        logger.debug("BackendThread().run(): Started. Calling self.start_operations()...")

        #Handle any unexpected errors.
        try:
            self.start_operations()

        except Exception:
            logger.critical("Unexpected error \n\n"+unicode(traceback.format_exc())+"\n\n while running operations. Warning user and exiting.")
            CoreTools.emergency_exit("There was an unexpected error:\n\n"+unicode(traceback.format_exc())+"\n\nWhile running operations!")

    def start_operations(self):
        """Start doing operations."""
        logger.debug("BackendThread().start_operations(): Running operations...")

        DialogTools.show_msg_dlg(kind="info", message="Please stay within sight of the system, "
                                 + "as operations are not fully automated and you may be asked "
                                 + "the occasional queston, or be shown warnings. You may see "
                                 + "the occasional file manager dialog pop up as well, so feel "
                                 + "free to either close them or ignore them.")

        #Make the list of operations avalable so bootloader operations can be disabled if
        #necessary.
        Tools.BackendTools.helpers.OPERATIONS = OPERATIONS

        #Run functions to do operations.
        for function in OPERATIONS:
            #Run the function.
            if not isinstance(function, tuple):
                function()

            else:
                function[0](*function[1:])

        if SETTINGS["MakeSystemSummary"]:
            self.generate_system_report()

        if SYSTEM_INFO["DisableBootloaderOperations"]:
            DialogTools.show_msg_dlg(kind="warning", message="Bootloader Operations were "
                                     + "disabled. This is because "
                                     + SYSTEM_INFO["DisableBootloaderOperationsBecause"]
                                     + ". Click okay to continue.")

        logger.info("BackendThread().start_operations(): Finished Operation Running Code.")

        wx.CallAfter(self.parent_window.update_current_operation_text, message="Finished!")

        #Change the dialog's message if needed.
        dialog_message = "Your operations are all done! Thank you for using WxFixBoot."

        for function in OPERATIONS:
            if isinstance(function, tuple):
                if MainBackendTools.manage_bootloader in function:
                    dialog_message += " You performed bootloader operations on at least one OS, "
                    dialog_message += "so please now reboot your system."
                    break

        DialogTools.show_msg_dlg(kind="info", message=dialog_message)

        wx.CallAfter(self.parent_window.backend_thread_finished)

    def generate_system_report(self):
        """Create a system report, containing various information helpful for debugging and fixing problems. It's pretty much like a bootinfo summary."""
        DialogTools.show_msg_dlg(kind="info", message="WxFixBoot will now create your system "
                                 + "report. Click okay to continue.")

        #Ask the user where to save the file.
        report_file = DialogTools.show_save_file_dlg(title="WxFixBoot - Select System Report File",
                                                     wildcard="Text Files|*.txt|Log Files|*.log|All Files/Devices (*)|*")

        #Write everything directly to the file.
        report_list = open(report_file, 'w')
        report_list.write("This system report was created with WxFixBoot version "+VERSION
                          + ". It can be used to diagnose problems with your system, and can help "
                          + "if you wish to make a support request.\n\n")

        #Do Firmware Information.
        report_list.write("\n##########Firmware Information##########\n")
        report_list.write("Detected firmware type: "+SYSTEM_INFO["FirmwareType"]+"\n")

        #Do Disk Information
        report_list.write("\n##########Disk Information##########\n")
        disk_list = list(DISK_INFO.keys())
        disk_list.sort()

        report_list.write("All Disks: "+', '.join(disk_list)+"\n\n")
        report_list.write("Per Disk Info:\n")

        for disk in disk_list:
            report_list.write("\tName: "+disk+"\n")
            report_list.write("\t\tType: "+DISK_INFO[disk]["Type"]+"\n")
            report_list.write("\t\tHost Device: "+DISK_INFO[disk]["HostDevice"]+"\n")
            report_list.write("\t\tPartitions: "+', '.join(DISK_INFO[disk]["Partitions"])+"\n")
            report_list.write("\t\tVendor: "+DISK_INFO[disk]["Vendor"]+"\n")
            report_list.write("\t\tProduct: "+DISK_INFO[disk]["Product"]+"\n")
            report_list.write("\t\tRaw Capacity: "+DISK_INFO[disk]["RawCapacity"]+"\n")
            report_list.write("\t\tHuman-readable Capacity: "+DISK_INFO[disk]["Capacity"]+"\n")
            report_list.write("\t\tDescription: "+DISK_INFO[disk]["Description"]+"\n")
            report_list.write("\t\tFlags: "+', '.join(DISK_INFO[disk]["Flags"])+"\n")
            report_list.write("\t\tPartitioning: "+DISK_INFO[disk]["Partitioning"]+"\n")
            report_list.write("\t\tFilesystem: "+DISK_INFO[disk]["FileSystem"]+"\n")
            report_list.write("\t\tUUID: "+DISK_INFO[disk]["UUID"]+"\n")
            report_list.write("\t\tID: "+DISK_INFO[disk]["ID"]+"\n")
            #report_list.write("\t\tBoot Record Strings: "+unicode(b', '.join(DISK_INFO[disk]["BootRecordStrings"]))+"\n\n") FIXME disabled until GetDevInfo 1.0.4 is out w/ final fix for this. 

        #Do OS Information.
        report_list.write("\n##########OS Information##########\n")
        os_list = list(OS_INFO.keys())
        os_list.sort()

        report_list.write("Detected Operating Systems: "+', '.join(OS_INFO.keys())+"\n")
        report_list.write("Modifyable Operating Systems: "+', '.join(SYSTEM_INFO["ModifyableOSs"])
                          + "\n")

        report_list.write("Currently running OS architecture: "+SYSTEM_INFO["CurrentOSArch"]+"\n")
        report_list.write("Currently running OS is on Live Disk: "
                          + unicode(SYSTEM_INFO["IsLiveDisk"])+"\n")

        if SYSTEM_INFO["IsLiveDisk"]:
            report_list.write("Currently running OS is Parted Magic: "
                              + unicode(SYSTEM_INFO["OnPartedMagic"])+"\n")

        report_list.write("Per OS Info:\n")

        for _os in os_list:
            report_list.write("\tOS Name: "+_os+"\n")
            report_list.write("\t\tIs Current OS: "+unicode(OS_INFO[_os]["IsCurrentOS"])+"\n")
            report_list.write("\t\tArchitecture: "+OS_INFO[_os]["Arch"]+"\n")
            report_list.write("\t\tInstalled On: "+OS_INFO[_os]["Partition"]+"\n")
            report_list.write("\t\tPackage Manager: "+OS_INFO[_os]["PackageManager"]+"\n")
            report_list.write("\t\tBoot Partition: "+OS_INFO[_os]["BootPartition"]+"\n")
            report_list.write("\t\tEFI Partition: "+OS_INFO[_os]["EFIPartition"]+"\n")
            report_list.write("\t\tContents of /etc/fstab:\n\t\t\t"
                              + '\n\t\t\t'.join(OS_INFO[_os]["RawFSTabInfo"])+"\n\n")

        #Do Bootloader information
        report_list.write("\n##########Bootloader Information##########\n")

        report_list.write("Disabled Bootloader Operations: "
                          + unicode(SYSTEM_INFO["DisableBootloaderOperations"])+"\n")

        if SYSTEM_INFO["DisableBootloaderOperations"]:
            report_list.write("Bootloader operations have been disabled. The operations that were "
                              + "going to be done are still detailed below,\n")

            report_list.write("but they weren't actually done.\n")
            report_list.write("Bootloader Operations were disabled because: "
                              + SYSTEM_INFO["DisableBootloaderOperationsBecause"]+"\n\n")

        bootloader_oss = list(BOOTLOADER_INFO.keys())
        bootloader_oss.sort()

        for _os in bootloader_oss:
            report_list.write("\tControlling OS: "+_os+"\n")
            report_list.write("\tBootloader (at time of startup): "
                              + BOOTLOADER_INFO[_os]["Bootloader"]+"\n")

            report_list.write("\tBootloaders that can be installed: "
                              + ', '.join(BOOTLOADER_INFO[_os]["AvailableBootloaders"])+"\n")

            report_list.write("\t\tBootloader Timeout: "
                              + unicode(BOOTLOADER_INFO[_os]["Timeout"])+"\n")

            report_list.write("\t\tGlobal Kernel Options: "
                              + BOOTLOADER_INFO[_os]["GlobalKernelOptions"]+"\n")

            report_list.write("\t\tBootloader-Specific Default _os: "
                              + BOOTLOADER_INFO[_os]["BLSpecificDefaultOS"]+"\n")

            report_list.write("\t\tDefault OS: "
                              + BOOTLOADER_INFO[_os]["DefaultOS"]+"\n")

            report_list.write("\t\tInstalled on: "
                              + BOOTLOADER_INFO[_os]["BootDisk"]+"\n")

            report_list.write("\t\tCan be modified: "
                              + unicode(BOOTLOADER_INFO[_os]["IsModifyable"])+"\n")

            report_list.write("\t\tReason for modifyability: "
                              + BOOTLOADER_INFO[_os]["Comments"]+"\n")

            report_list.write("\t\tBootloader was modified: "
                              + unicode(BOOTLOADER_INFO[_os]["Settings"]["ChangeThisOS"])+"\n\n")

            if BOOTLOADER_INFO[_os]["Settings"]["ChangeThisOS"]:
                report_list.write("\t\t\tBootloader was reinstalled: "
                                  + unicode(BOOTLOADER_INFO[_os]["Settings"]["Reinstall"])+"\n")

                report_list.write("\t\t\tBootloader was updated: "
                                  + unicode(BOOTLOADER_INFO[_os]["Settings"]["Update"])+"\n")

                report_list.write("\t\t\tBootloader was replaced with another bootloader: "
                                  + unicode(BOOTLOADER_INFO[_os]["Settings"]["InstallNewBootloader"])+"\n\n")

                if BOOTLOADER_INFO[_os]["Settings"]["Reinstall"] or BOOTLOADER_INFO[_os]["Settings"]["Update"] or BOOTLOADER_INFO[_os]["Settings"]["InstallNewBootloader"]:
                    report_list.write("\t\t\tNew Bootloader: "
                                      + BOOTLOADER_INFO[_os]["Settings"]["NewBootloader"]+"\n")

                    report_list.write("\t\t\tKept Existing Bootloader Timeout: "
                                      + unicode(BOOTLOADER_INFO[_os]["Settings"]["KeepExistingTimeout"])+"\n")

                    if BOOTLOADER_INFO[_os]["Settings"]["KeepExistingTimeout"] is False:
                        report_list.write("\t\t\tNew Bootloader Timeout: "
                                          + unicode(BOOTLOADER_INFO[_os]["Settings"]["NewTimeout"])+"\n")

                    report_list.write("\t\t\tKept Existing Kernel Options: "
                                      + unicode(BOOTLOADER_INFO[_os]["Settings"]["KeepExistingKernelOptions"])+"\n")

                    if BOOTLOADER_INFO[_os]["Settings"]["KeepExistingKernelOptions"] is False:
                        report_list.write("\t\t\tNew Kernel Options: "
                                          + BOOTLOADER_INFO[_os]["Settings"]["NewKernelOptions"]+"\n")

                    report_list.write("\t\t\tNew Default OS: "
                                      +BOOTLOADER_INFO[_os]["Settings"]["DefaultOS"]+"\n\n")


        #Do WxFixBoot's settings.
        report_list.write("\n##########Other WxFixBoot Settings##########\n")
        report_list.write("Do Quick Filesystem Check: "+unicode(SETTINGS["QuickFSCheck"])+"\n")
        report_list.write("Do Bad Sector Check: "+unicode(SETTINGS["BadSectorCheck"])+"\n")
        report_list.write("Show Diagnostic Terminal Output: "
                          + unicode(SETTINGS["FullVerbosity"])+"\n")

        report_list.write("Save System Report To File: "+unicode(SETTINGS["MakeSystemSummary"])+"\n")

        if SETTINGS["MakeSystemSummary"]:
            report_list.write("\n\tSave Terminal Output in Report: "
                              + unicode(SETTINGS["SaveOutput"])+"\n")

            report_list.write("\tSystem Report Target File: "+report_file+"\n\n")

        report_list.write("Number of operations to do: "+unicode(NUMBER_OF_OPERATIONS)+"\n")

        #Save terminal output.
        if SETTINGS["SaveOutput"]:
            report_list.write("\n##########Terminal Output##########\n")

            for line in OUTPUT_LOG:
                report_list.write(line)

            report_list.write("\n")

        #Save Log File.
        report_list.write("\n##########WxFixBoot's Log File##########\n")

        logfile = open("/tmp/wxfixboot.log", "r")

        for line in logfile:
            report_list.write(line)

        logfile.close()

        report_list.write("\n\n")
        report_list.write("\n##########End Of System Report##########\n")
        report_list.close()
 
#End Backend Thread
APP = WxFixBoot(False)
APP.MainLoop()
