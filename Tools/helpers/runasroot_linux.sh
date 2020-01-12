#!/bin/bash
# -*- coding: utf-8 -*-
# Executes generic privileged processes for Linux when requested for WxFixBoot.
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

#NB: Keep processes' stderr by redirecting it to stdout.

#This solution was found at https://stackoverflow.com/a/8723305.
#CC BY-SA 3.0 - https://creativecommons.org/licenses/by-sa/3.0/
#It allows us to run sh -c with this script by escaping arguments
#properly with quotes.
#Code snippet (unchanged):
#---
C=''

for i in "$@"; do 
    i="${i//\\/\\\\}"
    C="$C \"${i//\"/\\\"}\""
done

#---

#My code:

sh -c "$C" 2>&1

exit $?
