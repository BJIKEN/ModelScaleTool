// Copyright (c) 2016 Ultimaker B.V.
// Uranium is released under the terms of the LGPLv3 or higher.

import QtQuick 2.2
import QtQuick.Controls 1.2

import UM 1.1 as UM

Item
{
    id: base
    width: childrenRect.width
    height: childrenRect.height
    UM.I18nCatalog { id: catalog; name: "uranium"}

    property string xText
    property string yText
    property string zText
    property string lockPosition

    //Rounds a floating point number to 4 decimals. This prevents floating
    //point rounding errors.
    //
    //input:    The number to round.
    //decimals: The number of decimals (digits after the radix) to round to.
    //return:   The rounded number.
    function roundFloat(input, decimals)
    {
        //First convert to fixed-point notation to round the number to 4 decimals and not introduce new floating point errors.
        //Then convert to a string (is implicit). The fixed-point notation will be something like "3.200".
        //Then remove any trailing zeroes and the radix.
        var output = "";
        if (input !== undefined)
        {
            output = input.toFixed(decimals).replace(/\.?0*$/, ""); //Match on periods, if any ( \.? ), followed by any number of zeros ( 0* ), then the end of string ( $ ).
        }
        if (output == "-0")
        {
            output = "0";
        }
        return output;
    }

    function selectTextInTextfield(selected_item){
        selected_item.selectAll()
        selected_item.focus = true
    }

    Grid
    {
        id: textfields;

        anchors.leftMargin: UM.Theme.getSize("default_margin").width;
        anchors.top: parent.top;

        columns: 2;
        flow: Grid.TopToBottom;
        spacing: Math.round(UM.Theme.getSize("default_margin").width / 2);

        Label
        {
            height: UM.Theme.getSize("setting_control").height;
            text: "Starting Scale 1:";
            font: UM.Theme.getFont("default");
            color: UM.Theme.getColor("default");
            verticalAlignment: Text.AlignVCenter;
            renderType: Text.NativeRendering
            width: Math.ceil(contentWidth) //Make sure that the grid cells have an integer width.
        }

        Label
        {
            height: UM.Theme.getSize("setting_control").height;
            text: "Desired Scale 1:";
            font: UM.Theme.getFont("default");
            color: UM.Theme.getColor("default"); // This is intentional. The internal axis are switched.
            verticalAlignment: Text.AlignVCenter;
            renderType: Text.NativeRendering
            width: Math.ceil(contentWidth) //Make sure that the grid cells have an integer width.
        }


        TextField
        {
            id: xTextField
            width: UM.Theme.getSize("setting_control").width;
            height: UM.Theme.getSize("setting_control").height;
            style: UM.Theme.styles.text_field;
            text: xText
            validator: DoubleValidator
            {
                decimals: 5
                locale: "en_US"
            }

            onEditingFinished:
            {
                
            }
            onActiveFocusChanged:
            {
                if(!activeFocus && text =="")
                {
                    xText = 0.1; // Yeaaah i know. We need to change it to something else so we can force it to 0
                    xText = 0;
                }
            }
            Keys.onBacktabPressed: selectTextInTextfield(zTextField)
            Keys.onTabPressed: selectTextInTextfield(yTextField)
        }
        TextField
        {
            id: yTextField
            width: UM.Theme.getSize("setting_control").width;
            height: UM.Theme.getSize("setting_control").height;
            style: UM.Theme.styles.text_field;
            text: yText
            validator: DoubleValidator
            {
                decimals: 4
                locale: "en_US"
            }

            onEditingFinished:
            {
               
            }

            onActiveFocusChanged:
            {
                if(!activeFocus && text =="")
                {
                    yText = 0.1; // Yeaaah i know. We need to change it to something else so we can force it to 0
                    yText = 0;
                }
            }
            Keys.onBacktabPressed: selectTextInTextfield(xTextField)
            //Keys.onTabPressed: selectTextInTextfield(zTextField) How do we make it select a button?
        }
        
    }

    Button
    {
        id: applyModelScale

        anchors.top: textfields.bottom
        anchors.topMargin: UM.Theme.getSize("default_margin").height;
        anchors.left: textfields.left
        anchors.leftMargin: UM.Theme.getSize("default_margin").width

        //: Reset Rotation tool button
	text: "Convert Model Scale"
        style: UM.Theme.styles.toolbox_action_button
        z: 2

        onClicked: {
		var yTextValue = yTextField.text.replace(",", ".") // User convenience. We use dots for decimal values
		var xTextValue = xTextField.text.replace(",", ".")
		var combinedText = yTextValue.concat("/",xTextValue)
                UM.ActiveTool.setProperty("ModelScale", combinedText);
	}
    }

    // We have to use indirect bindings, as the values can be changed from the outside, which could cause breaks
    // (for instance, a value would be set, but it would be impossible to change it).
    // Doing it indirectly does not break these.
    Binding
    {
        target: base
        property: "xText"
        value: base.roundFloat(UM.ActiveTool.properties.getValue("X"), 4)
    }

    Binding
    {
        target: base
        property: "yText"
        value: base.roundFloat(UM.ActiveTool.properties.getValue("Y"), 4)
    }



    //Binding
   // {
   //     target: base
   //     property: "applyModelScale"
  //      value: UM.ActiveTool.properties.getValue("LockPosition")
 //   }
}
