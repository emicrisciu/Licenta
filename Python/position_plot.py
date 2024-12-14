import serial
import re
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import time
import math

# Configurarea porturilor seriale
uwb_ser = serial.Serial('COM6', 115200)
mpu_ser = serial.Serial('COM3', 115200)

pos_pattern = r"POS:\[(\d+),(\d+),(\d+),(\d+)\]"
mpu_pattern = r"MPU:(-?\d+\.\d+),(-?\d+\.\d+),(-?\d+\.\d+),(-?\d+\.\d+),(-?\d+\.\d+),(-?\d+\.\d+)"

# Configurarea graficului 2D
fig, ax = plt.subplots()
x_data, y_data = [], []
sc = ax.scatter([], [], color='blue')  # Punctul de pe grafic

ax.set_xlim(0, 1000)  # Setează limitele axei X
ax.set_ylim(0, 500)  # Setează limitele axei Y
ax.set_title('Poziția Tag-ului în timp real')
ax.set_xlabel('X (mm)')
ax.set_ylabel('Y (mm)')

# Variables for IMU integration
last_time = time.time()
last_pos_x = 0
last_pos_y = 0
last_acc_x = 0
last_acc_y = 0
angle_x = 0
angle_y = 0
dt = 0.05  # Time step in seconds (adjust as needed)

def is_valid_data(x, y, z, qf):
    if qf < 50 or not (0 <= z):
        return False
    return True

def is_goal(x, y, z, qf):
    if ((-100 <= x <= 100) or (900 <= x <= 1100)) and (150 <= y <= 350):
        return True
    return False

def update(frame):
    global last_time, last_pos_x, last_pos_y, angle_x, angle_y, dt, last_acc_x, last_acc_y

    current_time = time.time()
    dt = current_time - last_time
    last_time = current_time

    # Citește datele de la portul serial (UWB)
    if uwb_ser.in_waiting:
        uwb_line = uwb_ser.readline().decode('utf-8').strip()
        uwb_match = re.search(pos_pattern, uwb_line)
        if uwb_match:
            try:
                # Extract UWB position coordinates (x, y)
                x = int(uwb_match.group(1))
                y = int(uwb_match.group(2))
                z = int(uwb_match.group(3))
                qf = int(uwb_match.group(4))
                
                if is_valid_data(x, y, z, qf):
                    # Use UWB position as reference
                    last_pos_x = x
                    last_pos_y = y
                    
                    # Store the UWB coordinates
                    x_data.append(last_pos_x)
                    y_data.append(last_pos_y)
                    
                    if is_goal(x, y, z, qf):
                        print("G")
                    else:
                        if not (0 <= x <= 1000):
                            print("P/C")
                        if not (0 <= y <= 500):
                            print("M")
                    
                    # Limit the number of points plotted
                    if len(x_data) > 10:
                        x_data.pop(0)
                        y_data.pop(0)

                    # Update the scatter plot with UWB data
                    sc.set_offsets(list(zip(x_data, y_data)))
                
            except ValueError as e:
                print(f"Parsing error: {e}")
    
    # Citește datele de la portul serial (MPU)
    if mpu_ser.in_waiting:
        mpu_line = mpu_ser.readline().decode('utf-8').strip()
        mpu_match = re.search(mpu_pattern, mpu_line)
        if mpu_match:
            try:
                ax = float(mpu_match.group(1))  # Accel X
                ay = float(mpu_match.group(2))  # Accel Y
                az = float(mpu_match.group(3))  # Accel Z
                
                # Use the IMU to adjust the orientation (angle)
                # Example: Basic sensor fusion to adjust the position
                angle_x += ax * dt  # Integrate to get orientation changes (simple method)
                angle_y += ay * dt

                # Refine UWB position based on accelerometer data
                last_pos_x += ax * dt  # Adjust position based on accelerometer
                last_pos_y += ay * dt

                # Store the refined position from IMU adjustment
                x_data.append(last_pos_x)
                y_data.append(last_pos_y)
                
                # Limit the number of points plotted
                if len(x_data) > 10:
                    x_data.pop(0)
                    y_data.pop(0)

                # Update the scatter plot
                sc.set_offsets(list(zip(x_data, y_data)))
                
            except ValueError as e:
                print(f"Parsing error: {e}")
                
    return sc

# Setup FuncAnimation
ani = FuncAnimation(fig, update, interval=50, cache_frame_data=False)
plt.show()

# Close serial connections
uwb_ser.close()
mpu_ser.close()
