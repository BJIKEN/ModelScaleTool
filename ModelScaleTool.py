# Copyright (c) 2019 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

import time
from typing import cast, List, Optional, Union

from PyQt5.QtCore import Qt, QTimer

from UM.Event import Event, MouseEvent, KeyEvent
from UM.Math.Float import Float
from UM.Math.Plane import Plane
from UM.Math.Vector import Vector
from UM.Operations.GroupedOperation import GroupedOperation
from UM.Operations.TranslateOperation import TranslateOperation
from UM.Scene.SceneNodeSettings import SceneNodeSettings
from UM.Scene.Selection import Selection
from UM.Scene.ToolHandle import ToolHandle
from UM.Tool import Tool
from UM.Logger import Logger #Adding messages to the log.

try:
    from . import ModelScaleToolHandle
except (ImportError, SystemError):
    import TranslateToolHandle  # type: ignore  # This fixes the tests not being able to import.


DIMENSION_TOLERANCE = 0.0001  # Tolerance value used for comparing dimensions from the UI.
DIRECTION_TOLERANCE = 0.0001  # Used to check if you're perpendicular on some axis


class ModelScaleTool(Tool):
    """Provides the tool to move meshes and groups.

    The tool exposes a ToolHint to show the distance of the current operation.
    """
    
    def __init__(self) -> None:
        super().__init__()

        self._handle = ModelScaleToolHandle.ModelScaleToolHandle() #type: ModelScaleToolHandle.ModelScaleToolHandle #Because for some reason MyPy thinks this variable contains Optional[ToolHandle].
        self._enabled_axis = [ToolHandle.XAxis, ToolHandle.YAxis, ToolHandle.ZAxis]

        self._grid_snap = False
        self._grid_size = 10
        self._moved = False

        self._shortcut_key = Qt.Key_T

        self._distance_update_time = None #type: Optional[float]
        self._distance = None #type: Optional[Vector]

        self.setExposedProperties("ToolHint",
                                  "X", "Y", "Z",
                                  SceneNodeSettings.LockPosition)

        self._update_selection_center_timer = QTimer()
        self._update_selection_center_timer.setInterval(50)
        self._update_selection_center_timer.setSingleShot(True)
        self._update_selection_center_timer.timeout.connect(self.propertyChanged.emit)

        # Ensure that the properties (X, Y & Z) are updated whenever the selection center is changed.
        Selection.selectionCenterChanged.connect(self._onSelectionCenterChanged)

        # CURA-5966 Make sure to render whenever objects get selected/deselected.
        Selection.selectionChanged.connect(self.propertyChanged)

    def _onSelectionCenterChanged(self):
        self._update_selection_center_timer.start()

    def getX(self) -> float:
        """Get the x-location of the selection bounding box center.

        :return: X location in mm.
        """
        '''
        if Selection.hasSelection():
            return float(Selection.getBoundingBox().center.x)
        '''
        return 6.0

    def getY(self) -> float:
        """Get the y-location of the selection bounding box center.

        :return: Y location in mm.
        
        if Selection.hasSelection():
            # Note; The switching of z & y is intentional. We display z as up for the user,
            # But store the data in openGL space.
            return float(Selection.getBoundingBox().center.z)
        """
        
        return 1.0

    def getZ(self) -> float:
        """Get the z-location of the selection bounding box bottom

        The bottom is used as opposed to the center, because the biggest use
        case is to push the selection into the build plate.
        :return: Z location in mm.
        
        # We want to display based on the bottom instead of the actual coordinate.
        if Selection.hasSelection():
            # Note; The switching of z & y is intentional. We display z as up for the user,
            # But store the data in openGL space.
            return float(Selection.getBoundingBox().bottom)
        """
        return 1.0

    @staticmethod
    def _parseFloat(str_value: str) -> float:
        try:
            parsed_value = float(str_value)
        except ValueError:
            parsed_value = float(0)
        return parsed_value


        
    def setModelScale(self, y: str) -> None:
        splitInput =  y.split("/")
        parsed_Desired = abs(self._parseFloat(splitInput[0]))#take absolute value so dont have to worry about accidental negatives
        parsed_Start = abs(self._parseFloat(splitInput[1]))
        bounding_box = Selection.getBoundingBox()

        if (parsed_Desired * parsed_Start)!=0: # Multiply both values together to make sure neither are 0
            selected_nodes = self._getSelectedObjectsWithoutSelectedAncestors()
            if len(selected_nodes) > 1:
                op = GroupedOperation()
                # add functionality for more than one object at a time
            else:
                for selected_node in selected_nodes:
                    SCALE_FACTOR = (parsed_Start)/(parsed_Desired)
                    selected_node.scale(Vector(SCALE_FACTOR,SCALE_FACTOR,SCALE_FACTOR))
                    #OUTSTR = "SCALE_FACTOR is: "+ str(SCALE_FACTOR)+ " by factoring start: "+str(START_SCALE)+" and desired:" +str(DESIRED_SCALE)
                    #Logger.log("i", OUTSTR)
            
            self._controller.toolOperationStopped.emit(self)

    def setEnabledAxis(self, axis: List[int]) -> None:
        """Set which axis/axes are enabled for the current translate operation

        :param axis: List of axes (expressed as ToolHandle enum).
        """

        self._enabled_axis = axis
        self._handle.setEnabledAxis(axis)

    def setLockPosition(self, value: bool) -> None:
        """Set lock setting to the object. This setting will be used to prevent

        model movement on the build plate.
        :param value: The setting state.
        """
        for selected_node in self._getSelectedObjectsWithoutSelectedAncestors():
            selected_node.setSetting(SceneNodeSettings.LockPosition, str(value))

    def getLockPosition(self) -> Union[str, bool]:
        total_size = Selection.getCount()
        false_state_counter = 0
        true_state_counter = 0
        if not Selection.hasSelection():
            return False

        for selected_node in self._getSelectedObjectsWithoutSelectedAncestors():
            if selected_node.getSetting(SceneNodeSettings.LockPosition, "False") != "False":
                true_state_counter += 1
            else:
                false_state_counter += 1

        if total_size == false_state_counter:  # No locked positions
            return False
        elif total_size == true_state_counter:  # All selected objects are locked
            return True
        else:
            return "partially"  # At least one, but not all are locked

    def event(self, event: Event) -> bool:
        """Handle mouse and keyboard events.

        :param event: The event to handle.
        :return: Whether this event has been caught by this tool (True) or should
        be passed on (False).
        """
        super().event(event)

        # Make sure the displayed values are updated if the bounding box of the selected mesh(es) changes
        if event.type == Event.ToolActivateEvent:
            for node in self._getSelectedObjectsWithoutSelectedAncestors():
                node.boundingBoxChanged.connect(self.propertyChanged)

        if event.type == Event.ToolDeactivateEvent:
            for node in self._getSelectedObjectsWithoutSelectedAncestors():
                node.boundingBoxChanged.disconnect(self.propertyChanged)

        if event.type == Event.KeyPressEvent and cast(KeyEvent, event).key == KeyEvent.ShiftKey:
            return False

        

        return False

    def getToolHint(self) -> Optional[str]:
        """Return a formatted distance of the current translate operation.

        :return: Fully formatted string showing the distance by which the
        mesh(es) are dragged.
        """
        return "%.2f mm" % self._distance.length() if self._distance else None
