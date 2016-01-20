# This code is part of the checkmate project.
# Copyright (C) 2014-2016 The checkmate project contributors
#
# This program is free software under the terms of the GNU GPL, either
# version 3 of the License, or (at your option) any later version.

import random

import PyTango


def create_component_device(device_name, component_name):
        server_name = component_name
        db = PyTango.Database()
        comp = PyTango.DbDevInfo()
        comp._class = "DServer"
        comp.server = "component/" + server_name
        comp.name = "dserver/component/" + server_name
        db.add_device(comp)

        dev_info = PyTango.DbDevInfo()
        dev_info._class = device_name
        dev_info.server = "component/" + server_name
        dev_info.name = "sys/component/" + component_name
        db.add_device(dev_info)
        return server_name

