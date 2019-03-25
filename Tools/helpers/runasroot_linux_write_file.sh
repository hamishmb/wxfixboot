#!/bin/bash
# -*- coding: utf-8 -*-
# Writes files with privileged permissions on Linux when requested for WxFixBoot.
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

#Clear the IFS variable to prevent read from stripping leading whitespace.
IFS=

#Read the first line of input.
first=true
read -r line < /dev/stdin
echo "$line"

#Keep reading and writing until we get EOF.
while [[ $line != "EOF" ]]
do
    if [[ "$first" = true ]]; then
        echo "$line" > $1
    else
        echo "$line" >> $1
    fi

    read -r line < /dev/stdin
    echo "$line"
    first=false
done

exit $?
