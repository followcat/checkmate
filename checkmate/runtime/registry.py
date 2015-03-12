# This code is part of the checkmate project.
# Copyright (C) 2013 The checkmate project contributors
# 
# This program is free software under the terms of the GNU GPL, either
# version 3 of the License, or (at your option) any later version.

import zope.component.globalregistry


class RuntimeGlobalRegistry(zope.component.globalregistry.BaseGlobalComponents):
    """
    """

global_registry = RuntimeGlobalRegistry()

