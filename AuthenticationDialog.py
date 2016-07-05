#!/usr/bin/env python
# -*- coding: utf-8 -*- 
# Authentication Dialog for WxFixboot Version 2.0~pre2
# This file is part of WxFixboot.
# Copyright (C) 2013-2016 Hamish McIntyre-Bhatty
# WxFixboot is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License version 3 or,
# at your option, any later version.
#
# WxFixboot is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with WxFixboot.  If not, see <http://www.gnu.org/licenses/>.

#Do future imports to prepare to support python 3. Use unicode strings rather than ASCII strings, as they fix potential problems.
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

#Import other modules
import wx
import wx.animate
import time
import subprocess
import os
import sys

#Begin Authentication Window.
class AuthWindow(wx.Frame):  
    def __init__(self):
        """Inititalize AuthWindow"""
        wx.Frame.__init__(self, None, title="WxFixboot - Authenticate", size=(600,400), style=(wx.DEFAULT_FRAME_STYLE | wx.STAY_ON_TOP) ^ (wx.RESIZE_BORDER | wx.MINIMIZE_BOX))
        self.AuthPanel = wx.Panel(self)

        #Set the frame's icon.
        global AppIcon
        AppIcon = wx.Icon("/usr/share/wxfixboot/images/Logo.png", wx.BITMAP_TYPE_PNG)
        wx.Frame.SetIcon(self, AppIcon)

        self.CreateText()
        self.CreateButtons()
        self.CreateOtherWidgets()
        self.SetupSizers()
        self.BindEvents()

        #Call Layout() on self.AuthPanel() to ensure it displays properly.
        self.AuthPanel.Layout()

        #Give the password field focus, so the user can start typing immediately.
        self.PasswordField.SetFocus()

    def CreateText(self):
        """Create all text for AuthenticationWindow"""
        self.TitleText = wx.StaticText(self.AuthPanel, -1, "Authentication is required to run WxFixboot.")
        self.BodyText = wx.StaticText(self.AuthPanel, -1, "WxFixboot requires privileges to run.\nPlease enter your password to grant permission.")
        self.PasswordText = wx.StaticText(self.AuthPanel, -1, "Password:")

        Font = self.TitleText.GetFont()
        Font.SetWeight(wx.BOLD)
        self.TitleText.SetFont(Font) 
        self.PasswordText.SetFont(Font)

    def CreateButtons(self):
        """Create all buttons for AuthenticationWindow"""
        self.CancelButton = wx.Button(self.AuthPanel, -1, "Cancel")
        self.AuthButton = wx.Button(self.AuthPanel, -1, "Authenticate")

    def CreateOtherWidgets(self):
        """Create all other widgets for AuthenticationWindow"""
        #Create the image.
        img = wx.Image("/usr/share/wxfixboot/images/Logo.png", wx.BITMAP_TYPE_PNG)
        self.Image = wx.StaticBitmap(self.AuthPanel, -1, wx.BitmapFromImage(img))

        #Create the password field.
        self.PasswordField = wx.TextCtrl(self.AuthPanel, -1, "", style=wx.TE_PASSWORD|wx.TE_PROCESS_ENTER)
        self.PasswordField.SetBackgroundColour((255,255,255))

        #Create the throbber.
        self.Busy = wx.animate.Animation("/usr/share/wxfixboot/images/Throbber.gif")
        self.GreenPulse = wx.animate.Animation("/usr/share/wxfixboot/images/GreenPulse.gif")
        self.RedPulse = wx.animate.Animation("/usr/share/wxfixboot/images/RedPulse.gif")

        self.Throbber = wx.animate.AnimationCtrl(self.AuthPanel, -1, self.GreenPulse)
        self.Throbber.SetUseWindowBackgroundColour(True)
        self.Throbber.SetInactiveBitmap(wx.Bitmap("/usr/share/wxfixboot/images/ThrobberRest.png", wx.BITMAP_TYPE_PNG))
        self.Throbber.SetClientSize(wx.Size(30,30))

    def SetupSizers(self):
        """Setup sizers for AuthWindow"""
        #Make the main boxsizer.
        MainSizer = wx.BoxSizer(wx.VERTICAL)

        #Make the top sizer.
        TopSizer = wx.BoxSizer(wx.HORIZONTAL)

        #Make the top text sizer.
        TopTextSizer = wx.BoxSizer(wx.VERTICAL)

        #Add items to the top text sizer.
        TopTextSizer.Add(self.TitleText, 0, wx.ALIGN_LEFT)
        TopTextSizer.Add(self.BodyText, 0, wx.TOP|wx.ALIGN_LEFT, 10)

        #Add items to the top sizer.
        TopSizer.Add(self.Image, 0, wx.LEFT|wx.ALIGN_CENTER, 18)
        TopSizer.Add(TopTextSizer, 1, wx.LEFT|wx.ALIGN_CENTER, 29)

        #Make the password sizer.
        PasswordSizer = wx.BoxSizer(wx.HORIZONTAL)

        #Add items to the password sizer.
        PasswordSizer.Add(self.PasswordText, 0, wx.LEFT|wx.ALIGN_CENTER, 12)
        PasswordSizer.Add(self.PasswordField, 1, wx.LEFT|wx.ALIGN_CENTER, 22)
        PasswordSizer.Add(self.Throbber, 0, wx.LEFT|wx.ALIGN_CENTER|wx.FIXED_MINSIZE, 10)

        #Make the button sizer.
        ButtonSizer = wx.BoxSizer(wx.HORIZONTAL)

        #Add items to the button sizer.
        ButtonSizer.Add(self.CancelButton, 0, wx.ALIGN_CENTER|wx.EXPAND)
        ButtonSizer.Add(self.AuthButton, 1, wx.LEFT|wx.ALIGN_CENTER|wx.EXPAND, 10)

        #Add items to the main sizer.
        MainSizer.Add(TopSizer, 0, wx.ALL|wx.ALIGN_CENTER|wx.EXPAND, 10)
        MainSizer.Add(PasswordSizer, 0, wx.BOTTOM|wx.LEFT|wx.RIGHT|wx.ALIGN_CENTER|wx.EXPAND, 10)
        MainSizer.Add(ButtonSizer, 1, wx.BOTTOM|wx.LEFT|wx.RIGHT|wx.ALIGN_CENTER|wx.EXPAND, 10)

        #Get the sizer set up for the frame.
        self.AuthPanel.SetSizer(MainSizer)
        MainSizer.SetSizeHints(self)

    def BindEvents(self):
        """Bind all events for AuthenticationWindow"""
        self.Bind(wx.EVT_TEXT_ENTER, self.OnAuth, self.PasswordField)
        self.Bind(wx.EVT_BUTTON, self.OnAuth, self.AuthButton)
        self.Bind(wx.EVT_BUTTON, self.OnExit, self.CancelButton)

    def OnAuth(self, Event=None):
        """Check the password is correct, then either warn the user or call self.StartWxFixBoot()"""
        #Remove any cached credentials, so we don't create a security problem, or say the password is right when it isn't.
        subprocess.Popen("sudo -k", shell=True).wait()

        #Check the password is right.
        Password = self.PasswordField.GetLineText(0)
        Cmd = subprocess.Popen("LC_ALL=C sudo -S echo 'Authentication Succeeded'", stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)

        #Send the password to sudo through stdin, to avoid showing the user's password in the system/activity monitor.
        Cmd.stdin.write(Password+"\n")
        Cmd.stdin.close()

        self.Throbber.SetAnimation(self.Busy)
        self.Throbber.Play()

        while Cmd.poll() == None:
            wx.Yield()
            time.sleep(0.04)

        Output = Cmd.stdout.read()

        if "Authentication Succeeded" in Output:
            #Set the password field colour to green.
            self.PasswordField.SetBackgroundColour((192,255,192))

            #Play the green pulse for one second.
            self.Throbber.SetAnimation(self.GreenPulse)
            self.Throbber.Play()
            wx.CallLater(1000, self.Throbber.Stop)
            wx.CallLater(1100, self.StartWxFixBoot, Password)

        else:
            #Shake the window
            XPos, YPos = self.GetPosition()
            Count = 0

            while Count <= 6:
                if Count in (0,2,4,6):
                    XPos -= 10
                else:
                    XPos += 10

                time.sleep(0.02)
                self.SetPosition((XPos, YPos))
                wx.Yield()
                Count += 1

            #Set the password field colour to pink, and select its text.
            self.PasswordField.SetBackgroundColour((255,192,192))
            self.PasswordField.SetSelection(0,-1)
            self.PasswordField.SetFocus()

            #Play the red pulse for one second.
            self.Throbber.SetAnimation(self.RedPulse)
            self.Throbber.Play()
            wx.CallLater(1000, self.Throbber.Stop)

    def StartWxFixBoot(self, Password):
        """Start WxFixBoot and exit"""
        Cmd = subprocess.Popen("sudo -SH /usr/share/wxfixboot/WxFixBoot.py", stdin=subprocess.PIPE, stdout=sys.stdout, stderr=subprocess.PIPE, shell=True)

        #Send the password to sudo through stdin, to avoid showing the user's password in the system/activity monitor.
        Cmd.stdin.write(Password+"\n")
        Cmd.stdin.close()

        #Remove any cached credentials, so we don't create a security problem.
        subprocess.Popen("sudo -k", shell=True).wait()

        #Overwrite the password with a string of nonsense characters before deleting it, so the password cannot be read from memory when this script closes.
        Password = "ABCDEFGHIJKLMNOPQRSTUVWXYZ123456789!£$%^&*()_+"
        del Password
        self.OnExit()

    def OnExit(self, Event=None):
        """Close AuthWindow() and exit"""
        time.sleep(10)
        self.Destroy()

#End Authentication Window.
if __name__ == "__main__":
    app = wx.App(False)
    MainFrame = AuthWindow()
    MainFrame.Show()
    app.MainLoop()
