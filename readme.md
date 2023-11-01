This repo is for a Cura plugin I am working on for adding scale modelling scaling.
The problem:
3D models of miniatures imported can be in a variety of scales 1/72, 1/100, 1/700 etc. The issue comes when wanting to print something in a different scale. The maths is simple, set the scale of the model to be (current scale/desired scale). The issue is that Cura's built in scale tool doesnt allow for the use of division or multiplication within the text input fields so it would be neccessary to calculate whatever scale you need to apply separately and type it in.
This plugin tool is just to make the process simpler, just input the current scale, the scale you want it to be in and it will scale it for you.
It is based on the translate tool and still requires much more modification to make it look good
