# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from . import ModelScaleTool

from UM.i18n import i18nCatalog
i18n_catalog = i18nCatalog("uranium")

def getMetaData():
    return {
        "tool": {
            "name": i18n_catalog.i18nc("@action:button", "Scale Model"),
            "description": i18n_catalog.i18nc("@info:tooltip", "Scale the model"),
            "icon": "ModelScale_icon",
            "tool_panel": "ModelScaleTool.qml",
            "weight": 19 # set to random high value to make sure tool appears at bottom of toolbar
        }
    }

def register(app):
    return { "tool": ModelScaleTool.ModelScaleTool() }
