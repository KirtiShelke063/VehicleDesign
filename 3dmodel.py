import trimesh
import numpy as np
from pathlib import Path

# Load STL files
real_dc_motor = trimesh.load("DCMotor.stl")
real_dc_motor.apply_scale(0.01)

real_esp8266 = trimesh.load("esp8266.stl")
real_esp8266.apply_scale(0.01)
real_esp8266.visual.face_colors = [0, 100, 200, 255]  # Blue PCB color for ESP8266
real_esp8266.apply_translation([0.4, 0.6, 0.25])  # Adjusted for swapped dimensions

# Load ESP32-CAM from STL file
esp32_cam = trimesh.load("ESP32-CAM.stl")
esp32_cam.apply_scale(0.01)
esp32_cam.visual.face_colors = [192, 192, 192, 255]  # Silver color for camera
# Rotate 90 degrees around Z-axis to face horizontally, then rotate around X-axis to make it vertical
esp32_cam.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2, [0, 0, 1]))  # 90 degree horizontal shift
esp32_cam.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2, [1, 0, 0]))  # Make it vertical
esp32_cam.apply_transform(trimesh.transformations.rotation_matrix(np.pi, [0, 1, 0]))  # Make it upside down
esp32_cam.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2, [0, 0, 1]))  # Additional 90 degree horizontal flip
esp32_cam.apply_translation([0.0, 1.3, 0.3])  # Adjusted to front of vehicle with swapped dimensions

pantograf_mesh = trimesh.load("Pantograf.stl")
pantograf_mesh.apply_scale(0.025)  # Increased scale from 0.01 to 0.025
pantograf_mesh.visual.face_colors = [255, 215, 0, 255]
pantograf_mesh.apply_translation([0, 0, 0.55])  # Lowered from 0.7 to 0.55 to attach with servo

servo_mesh = trimesh.load("servo.stl")
servo_mesh.apply_scale(0.01)
servo_mesh.visual.face_colors = [0, 0, 255, 255]
servo_mesh.apply_translation([0, 0, 0.45])  # Positioned to connect with pantograph base

# Create a connecting joint between servo and pantograph
servo_pantograph_joint = trimesh.creation.cylinder(radius=0.05, height=0.05)  # Reduced height for closer connection
servo_pantograph_joint.visual.face_colors = [100, 100, 100, 255]
servo_pantograph_joint.apply_translation([0, 0, 0.52])  # Adjusted position for closer connection

# Chassis with swapped dimensions - length as width and width as length
chassis = trimesh.creation.box(extents=[1.2, 2.5, 0.3])  # Swapped from [2.5, 1.2, 0.3]
chassis.visual.face_colors = [20, 20, 20, 255]  # Shiny black matte color (very dark gray for matte effect)
chassis.apply_translation([0, 0, 0.15])

# Create vertical wheels using STL file
def create_vertical_wheel():
    wheel = trimesh.load("Tyres-30_full.stl")
    wheel.apply_scale(0.005)  # Compress the size significantly from large STL
    wheel.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2, [1, 0, 0]))  # Rotate around X-axis for vertical orientation
    # Removed color assignment to keep original tire color from STL
    return wheel

# Adjust wheel positions for the new chassis dimensions (swapped X and Y)
wheel_positions = [
    [0.5, 1.0, -0.1], [0.5, -1.0, -0.1],
    [-0.5, 1.0, -0.1], [-0.5, -1.0, -0.1]
]

wheels_and_motors = []
for pos in wheel_positions:
    wheel = create_vertical_wheel().copy().apply_translation(pos)
    
    # Position motors on the inner side of wheels, facing horizontally like real vehicles
    motor = real_dc_motor.copy()
    motor.visual.face_colors = [192, 192, 192, 255]  # Silver color for motors
    # Rotate motor 90 degrees around Y-axis to face horizontally
    motor.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2, [0, 1, 0]))
    
    # For left side motors, rotate additional 180 degrees to face the correct direction
    if pos[0] < 0:  # Left side wheels
        motor.apply_transform(trimesh.transformations.rotation_matrix(np.pi, [0, 0, 1]))
    
    # Position on the inner side of wheel (offset inward toward vehicle center)
    side_offset = 0.2  # Distance from wheel center to side face
    motor_x_offset = -side_offset if pos[0] > 0 else side_offset  # Inward toward center
    motor_pos = [pos[0] + motor_x_offset, pos[1], pos[2]]  # Same height as wheel center
    motor.apply_translation(motor_pos)
    
    wheels_and_motors.extend([wheel, motor])

# Load motor driver from GLB file
motor_driver_scene = trimesh.load("L298N motor driver.glb")

# Handle GLB scene properly
if hasattr(motor_driver_scene, 'to_geometry'):
    motor_driver = motor_driver_scene.to_geometry()
else:
    motor_driver = motor_driver_scene

motor_driver.apply_scale(0.5)  # Expanded from 0.01 to 1.0 (100x larger)
motor_driver.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2, [1, 0, 0]))  # Make it horizontal to surface
motor_driver.apply_translation([0, -0.6, 0.31])  # Moved up from 0.25 to 0.35 to sit above surface

# Combine all components using regular concatenation
vehicle_model = trimesh.util.concatenate([
    chassis, pantograf_mesh, servo_mesh, servo_pantograph_joint,
    real_esp8266, esp32_cam, motor_driver
] + wheels_and_motors)

# Export the final model
vehicle_model.export("final_engineering_vehicle.glb")
print("Exported to final_engineering_vehicle.glb")
