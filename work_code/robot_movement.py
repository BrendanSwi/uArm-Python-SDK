import sys
import time
import math

sys.path.append ('..')

from uarm.wrapper import SwiftAPI
from uarm.utils.log import logger

logger.setLevel(logger.VERBOSE)

# Setting a link between uArm and the kernel
swift = SwiftAPI (port = "COM5", callback_thread_pool_size = 1)

# Check to see if device connected
device_info = swift.get_device_info()
print (device_info)

# Send robot back to home
# Default position is [200, 0, 150]
swift.reset()

# Wait for robot to get back position
time.sleep (1)

# Getting robot's current position
current_position = swift.get_position()

## Basic Movement
# Defining Z-axis range and step size
z_start = 150
z_end = 100
step_size = 10

# Moving the robot arm up and down along the z-axis
print ("Moving arm up and down the z-axis...")
for z in range (z_start, z_end - 1, -step_size):
    swift.set_position(x = current_position[0], y = current_position[1], z = z) 
    time.sleep(0.5)

for z in range (z_end, z_start + 1, step_size):
    swift.set_position(x = current_position[0], y = current_position[1], z = z)
    time.sleep(0.5)

# Defining X-axis range and step size
x_start = 200
x_end = 150
step_size = 10

# Moving the robot arm left and right along the x-axis
print ("Moving arm left and right the x-axis...")
for x in range (x_start, x_end - 1, -step_size):
    swift.set_position(x = x, y = current_position[1], z = current_position[2]) 
    time.sleep(0.5)

for x in range (x_end, x_start + 1, step_size):
    swift.set_position(x = x, y = current_position[1], z = current_position[2])
    time.sleep(0.5)

## Moving In a Square
square_coordinates = [
    (200, 50, 150),
    (250, 50, 150),
    (250, 100, 150),
    (200, 100, 150),
    (200, 50, 150)
]

# Moving through each point
for point in square_coordinates:
    swift.set_position(x = point[0], y = point[1], z = point[2], wait = False)
    time.sleep(1)

## Moving In a Circle
center_x, center_y, z = 200, 0, 150
radius = 50
steps = 180

# Moving through each point
for angle in range(0, 360, 360 // steps):
    x = round(center_x + radius * math.cos(math.radians(angle)), 2)
    y = round(center_y + radius * math.sin(math.radians(angle)), 2)
    swift.set_position(x=x, y=y, z=z, wait=False)
    time.sleep(0.02)

# Return to home
swift.reset()

# Disconnect from Robot
swift.disconnect()