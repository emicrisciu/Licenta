# Zona importării bibliotecilor - unele din ele trebuie eliminate!

import serial
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, Arc
from matplotlib.animation import FuncAnimation
import sys
import time
import math
import numpy as np
import threading
from queue import Queue
import bluetooth
from collections import deque
from scipy.signal import savgol_filter
import football_field
import bluetooth_com
import line_crossing

# Zona variabilelor globale - explicatii pt fiecare!

bluetooth_com.terminate_program = False
outlier_count = 0
outlier_threshold = 2
outlier_position = None
outlier_flag = False
mean_flag = False
mean_threshold = 3
mean_count = 0
line_crossing_buffer = deque(maxlen=5)  # Buffer to track potential line crossings
line_crossing_confidence = 0  # Confidence level that a line crossing occurred
line_crossing_threshold = 3  # Number of consistent readings needed
last_zone = "field"  # Track the previous zone
crossing_cooldown = 0  # Prevent rapid successive crossing detections
crossing_cooldown_time = 10  # Frames to wait before detecting another crossing
# Buffer for smoothing position data
position_buffer = deque(maxlen=20)
last_time = time.time()
uwb_x, uwb_y, uwb_z, qf, acc_x, acc_y, acc_z = football_field.field_length/2, football_field.field_width/2, 0, 0, 0, 0, 0
x_data, y_data = [], []
processed_position = {"x": football_field.field_length/2, "y": football_field.field_width/2}
processed_lock = threading.Lock()
vx, vy = 0, 0
x_est, y_est = 0, 0
dt = 0

# Setarea conexiunii Bluetooth

esp_addr = "A0:A3:B3:97:4B:62"  # Adresa MAC a ESP32
bluetooth_com.set_bluetooth(esp_addr)

# Zona funcțiilor folosite în timpul procesării datelor

def complementary_filter(pos_x, pos_y, acc_x, acc_y, dt):
	"""
	Filtrul complementar ce implică folosirea accelerației pentru rafinarea poziției
	"""
	global x_est, y_est, vx, vy
	alpha = 0.9
    
	# Update velocity with acceleration
	vx = vx + acc_x * dt
	vy = vy + acc_y * dt
    
	# Update position estimate
	x_est = alpha * pos_x + (1 - alpha) * (x_est + vx * dt)
	y_est = alpha * pos_y + (1 - alpha) * (y_est + vy * dt)
    
	return x_est, y_est

# Funcție ce verifică dacă poziția curentă a mingii se află în limitele machetei
	
def range_check(x, y, min_x, max_x, min_y, max_y):
    # Apply a hard limit - heavily weight positions toward the valid range
    if x < min_x:
        x = min_x
    elif x > max_x:
        x = max_x
    
    if y < min_y:
        y = min_y
    elif y > max_y:
        y = max_y
    
    return x, y
    
def distance(x, y):
	return math.sqrt((x[0] - y[0])**2 + (x[1] - y[1])**2)

def processing_loop():
	global uwb_x, uwb_y, uwb_z, qf, acc_x, acc_y, mean_count, mean_flag, position_buffer, dt
	last_time = time.time()
	while not bluetooth_com.terminate_program:
		
		if bluetooth_com.uwb_data_queue:
			try:
				coords = bluetooth_com.uwb_data_queue.popleft().split()
				uwb_x = int(coords[1])
				uwb_y = int(coords[2])
				uwb_z = int(coords[3])
				qf = int(coords[4])
			except ValueError as e:
				print(f"Parsing error: {e}")
				
		if bluetooth_com.mpu_data_queue:
			try:
				imu_data = bluetooth_com.mpu_data_queue.popleft().split(',')
				acc_x = float(imu_data[0].split(':')[1])
				acc_y = float(imu_data[1])
				acc_z = float(imu_data[2])
			except ValueError as e:
				print(f"Parsing error: {e}")
		
		# Apply filtering and update position
		if uwb_x is not None and uwb_y is not None:
			if qf > 30:
				new_pos = (uwb_x, uwb_y)
			else:
				current_time = time.time()
				dt = current_time - last_time
				#print(f"dt = {dt}")
				last_time = current_time
				new_pos = complementary_filter(uwb_x, uwb_y, acc_x, acc_y, dt)
				
			# print(f"pos before range check: {new_pos}")
			
			new_pos = range_check(new_pos[0], new_pos[1], -football_field.border, football_field.field_length + football_field.border, -football_field.border, football_field.field_width + football_field.border)
			
			with processed_lock:
				position_buffer.append((new_pos[0], new_pos[1]))
				
			if len(position_buffer) > 1 and distance(position_buffer[-1], position_buffer[-2]) < 100:
				mean_count += 1
				if mean_count > 2:
					mean_flag = True
			else:
				mean_count = 0
				mean_flag = False
				
			if mean_flag and len(position_buffer) > mean_count - 1:
				sum_x = sum(pos[0] for pos in list(position_buffer)[-mean_count:])
				sum_y = sum(pos[1] for pos in list(position_buffer)[-mean_count:])
				avg_point = (sum_x / mean_count, sum_y / mean_count)
				with processed_lock:
					position_buffer.append(avg_point) #poate fi problema pt ca tot introduc valori medii in buffer, poate lasam doar partea de afisat sa ia in considerare media!
				
			if len(position_buffer) > 2:
				crossing_info = line_crossing.detect_line_crossing(position_buffer[-1], position_buffer[-2], uwb_z, dt)
				if crossing_info:
					print(f"\n\nLine crossed: {crossing_info['boundary']}")
					print(f"Direction: {crossing_info['direction']}")
					print(f"Position: ({crossing_info['crossing_point'][0]:.2f}, {crossing_info['crossing_point'][1]:.2f})")
					print(f"Velocity: {crossing_info['velocity']:.2f} m/s")
					bluetooth_com.show_popup(crossing_info['message'])
			
			#print(f"pos after range check: {processed_position}")
			
			# for boundary_name, boundary_points in field_boundaries.items():
				# p1, p2 = boundary_points
				# boundary_line = (p1, p2)
				# if distance_from_point_to_line(new_pos, boundary_line) < 200:
					# print(f"\n\nDANGEROUS! - {boundary_name}\n\n")
					# set a flag that indicates that the ball is near a field boundary or jump directly to line crossing check
					
			# Handle line crossing detection
			# crossing_info = detect_line_crossing(new_pos)
			# if crossing_info:
				# print(f"\n\nLine crossed: {crossing_info['boundary']}")
				# print(f"Direction: {crossing_info['direction']}")
				# print(f"Position: ({crossing_info['crossing_point'][0]:.2f}, {crossing_info['crossing_point'][1]:.2f})")
				# print(f"Velocity: {crossing_info['velocity']:.2f} m/s")
				
				# if detect_goal(local_uwb_z, crossing_info['crossing_point'], crossing_info['direction']):
					# print("GOAAAAAAAAAAAAAAAAAAAAAAAAAAL!!!")
					# for zone_patch in zone_patches.values():
						# zone_patch.set_alpha(1)
				
				# Here you could add code to trigger actions based on the crossing
				# For example, sending a signal, playing a sound, etc.
			# Handle outliers
			# ~ if position_buffer and is_outlier(new_pos, position_buffer[-1]):
				# ~ if outlier_count == 0:
					# ~ outlier_position = new_pos
					# ~ outlier_count += 1
					# ~ mean_count = 0
					# ~ mean_flag = False
				# ~ else:
					# ~ if math.sqrt((new_pos[0] - outlier_position[0])**2 + (new_pos[1] - outlier_position[1])**2) < 200:
						# ~ outlier_count += 1
						# ~ if outlier_count >= outlier_threshold:
							# ~ outlier_count = 0
							# ~ outlier_position = None
							# ~ interp_x, interp_y = complementary_filter(local_uwb_x, local_uwb_y, local_acc_x, local_acc_y, dt)
							# ~ position_buffer.append((interp_x, interp_y))
					# ~ else:
						# ~ outlier_position = new_pos
						# ~ outlier_count = 1
						# ~ interp_x, interp_y = complementary_filter(local_uwb_x, local_uwb_y, local_acc_x, local_acc_y, dt)
						# ~ position_buffer.append((interp_x, interp_y))
			# ~ else:
				# ~ # Normal position update with complementary filter
				# ~ x_est, y_est = complementary_filter(local_uwb_x, local_uwb_y, local_acc_x, local_acc_y, dt)
				
				# ~ # Check if position is relatively stable
				# ~ if position_buffer and math.sqrt((x_est - position_buffer[-1][0])**2 + (y_est - position_buffer[-1][1])**2) < 100:
					# ~ mean_count += 1
					# ~ if mean_count >= mean_threshold:
						# ~ mean_flag = True
				# ~ else:
					# ~ mean_count = 0
					# ~ mean_flag = False
						
				# ~ position_buffer.append((x_est, y_est))
				
			# ~ position_buffer.append((local_uwb_x, local_uwb_y))
			
			# ~ if len(position_buffer) >= 5:
				# ~ interp_x, interp_y = qf_weighted_savgol_filter(local_qf)
				# ~ print("\n\n\n\nSMOOOOOTH\n\n\n\n")
			# ~ else:
				# ~ interp_x, interp_y = local_uwb_x, local_uwb_y
			
				# ~ # Apply moving average when ball is stable
				# ~ if len(position_buffer) >= 3 and mean_flag:
					# ~ sum_x = sum(pos[0] for pos in position_buffer)
					# ~ sum_y = sum(pos[1] for pos in position_buffer)
					# ~ avg_x = sum_x / len(position_buffer)
					# ~ avg_y = sum_y / len(position_buffer)
					# ~ interp_x, interp_y = avg_x, avg_y
				# ~ else:
					# ~ interp_x, interp_y = x_est, y_est
					
			# ~ interp_x, interp_y = enhanced_position_filter(local_uwb_x, local_uwb_y, local_qf)
			# ~ interp_x, interp_y = local_uwb_x, local_uwb_y

def update(frame):
	global processed_lock, position_buffer, uwb_z
	
	if position_buffer:
		with processed_lock:
			x, y = position_buffer.popleft()
			#print(f"Position inside update function: {x}, {y}")
				
		if x is not None and y is not None:
			x_data.append(x)
			y_data.append(y)
			
			if len(x_data) > 10:
				x_data.pop(0)
				y_data.pop(0)
				
			football_field.sc.set_offsets(list(zip(x_data, y_data)))
			
			# Reset transparency of all zones
			for zone_patch in football_field.zone_patches.values():
				zone_patch.set_alpha(0.2)
				
			# Detect which zone the ball is in and highlight it
			zone = football_field.detect_zone(x, y, uwb_z)
			if zone in football_field.zone_patches:
				football_field.zone_patches[zone].set_alpha(0.7)
			
			elements_to_update = [football_field.sc]
			for zone_name, zone_patch in football_field.zone_patches.items():
				elements_to_update.append(zone_patch)
				
			return tuple(elements_to_update)
		
	return tuple()
	# start_time = time.time()
	# global last_time, uwb_x, uwb_y, uwb_z, qf, acc_x, acc_y, acc_z
	# #global qf, x_est, y_est, uwb_x, uwb_y, uwb_z, acc_x, acc_y, last_time, interp_x, interp_y, dt, terminate_program
	# #global outlier_count, outlier_position, mean_flag, mean_count
	# #global last_zone, line_crossing_confidence, crossing_cooldown
    
	# if bluetooth_com.terminate_program:
		# return tuple()
    
	# current_time = time.time()
	# dt = current_time - last_time
	# print(f"dt = {dt}")
	# last_time = current_time

	# # with lock:
		# # local_uwb_x = uwb_x
		# # local_uwb_y = uwb_y
		# # local_uwb_z = uwb_z
		# # local_qf = qf
		# # local_acc_x = acc_x
		# # local_acc_y = acc_y
        
	
	# end_time = time.time()
    
	# elements_to_update = [football_field.sc]
	# # for zone_name, zone_patch in football_field.zone_patches.items():
		# # elements_to_update.append(zone_patch) BIG PROBLEM TO SOLVE

	# print(f"Frame processing time: {end_time - start_time:.4f} seconds")
	# print(f"Returned artists: {elements_to_update}")
	# return tuple(elements_to_update)


# def update1(frame):
	# football_field.sc.set_offsets([[0, 0]])
	# return (football_field.sc,)

def test_function():
	from simulator import simulate_trajectory
	trajectory = simulate_trajectory()
	for x, y, z, qf in trajectory:
		bluetooth_com.uwb_data_queue.append(f"T {x} {y} {z} {qf}")
		time.sleep(0.1)


# Main execution
def main(test_mode=False):
	#global terminate_program
	try:
		football_field.draw_field()
		
		if not test_mode:
		
			bluetooth_check_thread = threading.Thread(target=bluetooth_com.bluetooth_health_check, daemon=True)
			bluetooth_check_thread.start()
			
			# Start thread for data handling
			data_reading_thread = threading.Thread(target=bluetooth_com.read_esp_bluetooth, daemon=True)
			data_reading_thread.start()
			
		else:
			
			test_thread = threading.Thread(target=test_function, daemon=True)
			test_thread.start()
		
		processing_thread = threading.Thread(target=processing_loop, daemon=True)
		processing_thread.start()
		
		# Create animation
		ani = FuncAnimation(football_field.fig, update, interval=20, cache_frame_data=False, blit=True)
		
		# Display plot
		plt.show()
		
	except KeyboardInterrupt:
		print("Program terminated by user")
		bluetooth_com.terminate_program = True
	finally:
		bluetooth_com.terminate_program = True
		# Close all connections
		if bluetooth_com.esp_socket is not None:
			bluetooth_com.esp_socket.close()
			print("Bluetooth connection closed")
		exit(1)

if __name__ == "__main__":
    main(test_mode=False)