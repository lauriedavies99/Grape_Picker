# Grape_Picker #
Grape Picker for final year university project

# Vision System
Python used for the vision system with a realsense D435i stereo camera.
Requires pyrealsense2, numpy, opencv and math packages.
Vision system uses chroma key and depth perception to identify bunches of grapes and calculate a percentage certainty of the object being a grape.

# End Effector
Consists of a gripping and cutting mechanism so that the bunch can be picked without being dropped.
Used two Dynamixel xl330-m288-t servo motors along with a small gearbox to increase the torque for the cutting arm.
Requires the Dynalixelshield package.
