import serial
import re
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, Arc
from matplotlib.animation import FuncAnimation
import time
import math
import numpy as np
import threading
from queue import Queue
import bluetooth
import socket

SOCKET_PORT = 5000

# Configurarea porturilor seriale
# uwb_ser = serial.Serial('COM6', 115200)
# mpu_ser = serial.Serial('COM3', 115200)

uwb_addr = "C0:59:C9:08:D6:4B" # insert tag MAC address here
mpu_addr = "A0:A3:B3:97:4B:62"

#uwb_socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
mpu_socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)

#uwb_socket.connect((uwb_addr, 1)) # ask chatgpt about this line here
mpu_socket.connect((mpu_addr, 1))

pos_pattern = r"POS:\[(-?\d+),(-?\d+),(-?\d+),(\d+)\]"
mpu_pattern = r"MPU:(-?\d+\.\d+),(-?\d+\.\d+),(-?\d+\.\d+),(-?\d+\.\d+),(-?\d+\.\d+),(-?\d+\.\d+)"

uwb_data_queue = Queue()
mpu_data_queue = Queue()

#client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#client_socket.connect(('localhost', SOCKET_PORT))

def read_socket():    
    while True:
        data = client_socket.recv(1024).decode('utf-8').strip
        if data:
            uwb_data_queue.put(data)
            print(data)
    

#def read_uwb_serial():
 #   while True:
  #      if uwb_ser.in_waiting:
   #         line = uwb_ser.readline().decode('utf-8').strip()
    #        uwb_data_queue.put(line)
    
def read_uwb_bluetooth():
    while True:
        data = uwb_socket.recv(1024).decode('utf-8').strip()
        uwb_data_queue.put(data)

# def read_mpu_serial():
#     while True:
#         if mpu_ser.in_waiting:
#             line = mpu_ser.readline().decode('utf-8').strip()
#             mpu_data_queue.put(line)
            
def read_mpu_bluetooth():
    while True:
        data = mpu_socket.recv(1024).decode('utf-8').strip()
        print(data)
        mpu_data_queue.put(data)
        uwb_data_queue.put(data)            
            
# Start thread-uri
#threading.Thread(target=read_uwb_bluetooth, daemon=True).start()
threading.Thread(target=read_mpu_bluetooth, daemon=True).start()
#threading.Thread(target=read_socket, daemon=True).start()

# Configurarea graficului 2D
fig, ax = plt.subplots()
x_data, y_data = [], []
sc = ax.scatter([], [], color='blue')  # Punctul de pe grafic
# line, = ax.plot([], [], 'bo', markersize=5)

# def init():
#     ax.set_xlim(-100, field_length + 100)  # Voi desena terenul mai lung decât în mod normal pentru a observa și zona din spatele porții
#     ax.set_ylim(-50, field_width + 50) # Voi desena terenul mai lat decât în mod normal pentru a observa și zona auturilor
#     return line,

qf = 100    # Inițialiare variabilă globală factor de calitate

# Dimensiunile terenului
field_length = 1000  # Lungimea terenului
field_width = 500  # Lățimea terenului
goal_depth = 120  # Adâncimea zonei potențialului gol (> adâncimea porții)
goal_width = 130  # Lățimea zonei potențialului gol (> lățimea porții)
goal_y_start = 185  # Startul zonei de gol pe axa Y

# Setarea limitelor graficului
ax.set_xlim(-100, field_length + 100)  # Voi desena terenul mai lung decât în mod normal pentru a observa și zona din spatele porții
ax.set_ylim(-50, field_width + 50) # Voi desena terenul mai lat decât în mod normal pentru a observa și zona auturilor
ax.set_title('Teren de fotbal cu poziția mingii în timp real')
ax.set_xlabel('X (mm)')
ax.set_ylabel('Y (mm)')

# Adăugarea liniilor / marginilor terenului
ax.plot([0, 0], [0, field_width], color='black')  # Linia porții stânga
ax.plot([field_length, field_length], [0, field_width], color='black')  # Linia porții dreapta
ax.plot([0, field_length], [0, 0], color='black')  # Linia de jos
ax.plot([0, field_length], [field_width, field_width], color='black')  # Linia de sus
ax.plot([field_length / 2, field_length / 2], [0, field_width], color='black')  # Linia de mijloc

# Desenarea contururilor porților
# Poarta stângă
ax.plot([-45, 0], [200, 200], color='black', linewidth=0.8)
ax.plot([-45, -45], [200, 300], color='black', linewidth=0.8)
ax.plot([-45, 0], [300, 300], color='black', linewidth=0.8)
# Poarta dreaptă
ax.plot([field_length, field_length + 45], [200, 200], color='black', linewidth=0.8)
ax.plot([field_length + 45, field_length + 45], [200, 300], color='black', linewidth=0.8)
ax.plot([field_length, field_length + 45], [300, 300], color='black', linewidth=0.8)

# Cercul de la centrul terenului
center_circle = Circle((field_length / 2, field_width / 2), 75, edgecolor='black', facecolor='none', linestyle='-')
ax.add_patch(center_circle)

# Punctul de la centrul terenului
ax.scatter([field_length / 2], [field_width / 2], color='black')

# Careurile mari "de 16 metri"
penalty_area_left = Rectangle((0, 100), 160, 300, edgecolor='black', facecolor='none')
penalty_area_right = Rectangle((840, 100), 160, 300, edgecolor='black', facecolor='none')
ax.add_patch(penalty_area_left)
ax.add_patch(penalty_area_right)

# Careurile mici "de 6 metri"
goal_area_left = Rectangle((0, 185), 60, 130, edgecolor='black', facecolor='none')
goal_area_right = Rectangle((940, 185), 60, 130, edgecolor='black', facecolor='none')
ax.add_patch(goal_area_left)
ax.add_patch(goal_area_right)

# Punctele pentru penalty-uri
ax.scatter([110], [250], color='black')
ax.scatter([890], [250], color='black')

# Semicercurile din dreptul careurilor
penalty_arc_left = Arc((115, 250), 146, 146, angle=0, theta1=308, theta2=52, edgecolor='black')
penalty_arc_right = Arc((885, 250), 146, 146, angle=0, theta1=128, theta2=232, edgecolor='black')
ax.add_patch(penalty_arc_left)
ax.add_patch(penalty_arc_right)

# Zonele corespunzătoare unui potențial gol
goal_zone_left = Rectangle((-60, goal_y_start), goal_depth, goal_width, color='green', alpha=0.2)   # Am considerat o zonă mare cât 2 careuri mici lipite
goal_zone_right = Rectangle((940, goal_y_start), goal_depth, goal_width, color='green', alpha=0.2)
ax.add_patch(goal_zone_left)
ax.add_patch(goal_zone_right)

# Zonele auturilor de margine
out_zone_up = Rectangle((0, 500), 1000, 50, color='red', alpha=0.2)
out_zone_down = Rectangle((0, -50), 1000, 50, color='red', alpha=0.2)
ax.add_patch(out_zone_up)
ax.add_patch(out_zone_down)

# Zonele auturilor de poartă / cornerelor
corner_zone_up_left = Rectangle((-60, 315), 60, 185, color='orange', alpha=0.2)
corner_zone_down_left = Rectangle((-60, 0), 60, 185, color='orange', alpha=0.2)
corner_zone_left = Rectangle((-100, 0), 40, 500, color='orange', alpha=0.2) # Zona care cuprinde și spatele porții din stânga
corner_zone_up_right = Rectangle((1000, 315), 60, 185, color='orange', alpha=0.2)
corner_zone_down_right = Rectangle((1000, 0), 60, 185, color='orange', alpha=0.2)
corner_zone_right = Rectangle((1060, 0), 40, 500, color='orange', alpha=0.2)    # Zona care cuprinde și spatele porții din dreapta
ax.add_patch(corner_zone_up_left)
ax.add_patch(corner_zone_down_left)
ax.add_patch(corner_zone_left)
ax.add_patch(corner_zone_up_right)
ax.add_patch(corner_zone_down_right)
ax.add_patch(corner_zone_right)

# Zone care se suprapun cu porțile dar corespund zonelor de deasupra porților (ținem cont de coordonata Z)
above_goal_zone_left = Rectangle((-60, 185), 60, 130, color='orange', alpha=0.2)
above_goal_zone_right = Rectangle((1000, 185), 60, 130, color='orange', alpha=0.2)
ax.add_patch(above_goal_zone_left)
ax.add_patch(above_goal_zone_right)

# Filtru Kalman
dt = 0.05   # Pasul de timp (50 ms între măsurători)
A = np.array([[1, 0, dt, 0],
              [0, 1, 0, dt],
              [0, 0, 1, 0],
              [0, 0, 0, 1]])
B = np.array([[0.5 * dt**2, 0],
              [0, 0.5 * dt**2],
              [dt, 0],
              [0, dt]])
H = np.array([[1, 0, 0, 0],
              [0, 1, 0, 0]])
x = np.zeros((4, 1))  # Starea inițială: [x, y, vx, vy]
P = np.eye(4) * 500  # Matricea de covarianță a erorii
Q = np.eye(4) * 0.1  # Zgomotul procesului
R = np.eye(2) * 10   # Zgomotul măsurătorilor

def kalman_filter(x, P, z, u):
    # Predict
    x_pred = A @ x + B @ u
    P_pred = A @ P @ A.T + Q
    
    # Update
    y = z - H @ x_pred  # Inovația
    S = H @ P_pred @ H.T + R    # Covarianța inovației
    K = P_pred @ H.T @ np.linalg.inv(S) # Câștigul Kalman
    
    x_updated = x_pred + K @ y
    P_updated = (np.eye(4) - K @ H) @ P_pred
    
    return x_updated, P_updated

# Funcții pentru validarea zonelor specifice în care se află mingea
def is_valid_data(qf):
    return qf >= 50

def is_goal_left(x, y):
    return (-60 <= x <= 60) and (185 <= y <= 315)

def is_goal_right(x, y):
    return (940 <= x <= 1060) and (185 <= y <= 315)

def is_out_up(x, y):
    return (0 <= x <= 1000) and (500 <= y)

def is_out_down(x, y):
    return (0 <= x <= 1000) and (0 >= y)

def is_corner_up_left(x, y):
    return (-60 <= x <= 0) and (315 <= y <= 500)

def is_corner_down_left(x, y):
    return (-60 <= x <= 0) and (0 <= y <= 185)

def is_corner_up_right(x, y):
    return (1000 <= x <= 1060) and (315 <= y <= 500)

def is_corner_down_right(x, y):
    return (1000 <= x <= 1060) and (0 <= y <= 185)

def is_corner_left(x, y):
    return (-100 <= x <= -60) and (0 <= y <= 500)

def is_corner_right(x, y):
    return (1060 <= x <= 1100) and (0 <= y <= 500)

def is_above_goal_left(x, y, z):
    return (-60 <= x <= 0) and (185 <= y <= 315) and (z >= 250)

def is_above_goal_right(x, y, z):
    return (1000 <= x <= 1060) and (185 <= y <= 315) and (z >= 250)

uwb_z = 0

def update(frame):
    global x, P, qf, uwb_z
    
    z = None    # Poziția UWB implicită (inexistentă)
    u = np.zeros((2, 1))    # Intrarea IMU implicită (zero)

    # Citește datele de la portul serial (UWB)
    if not uwb_data_queue.empty():
        uwb_line = uwb_data_queue.get()
        uwb_match = re.search(pos_pattern, uwb_line)
        if uwb_match:
            try:
                # Extrage coordonatele tag-ului UWB (x, y)
                uwb_x = int(uwb_match.group(1))
                uwb_y = int(uwb_match.group(2))
                uwb_z = int(uwb_match.group(3))
                qf = int(uwb_match.group(4))
                #print(f"x = {uwb_x}, y = {uwb_y}, z = {uwb_z}, qf = {qf}")
                z = np.array([uwb_x, uwb_y]).reshape((2, 1))
                
            except ValueError as e:
                print(f"Parsing error: {e}")
    
    # Citește datele de la portul serial (MPU)
    if not mpu_data_queue.empty():
        mpu_line = mpu_data_queue.get()
        mpu_match = re.search(mpu_pattern, mpu_line)
        if mpu_match:
            try:
                ax = float(mpu_match.group(1))  # Accel X
                ay = float(mpu_match.group(2))  # Accel Y
                #print(f"ax = {ax}, ay = {ay}")
                u = np.array([ax, ay]).reshape((2, 1))
                
            except ValueError as e:
                print(f"Parsing error: {e}")
                
    # Aplică filtrul Kalman
    if z is not None:
        x, P = kalman_filter(x, P, z, u)
        
    if is_valid_data(qf):
        # Adaugă poziția estimată la grafic
        x_data.append(x[0, 0])  # Poziția estimată X
        y_data.append(x[1, 0])  # Poziția estimată Y
        
        # Resetează transparența tuturor zonelor de interes
        goal_zone_left.set_alpha(0.2)
        goal_zone_right.set_alpha(0.2)
        out_zone_up.set_alpha(0.2)
        out_zone_down.set_alpha(0.2)
        corner_zone_up_left.set_alpha(0.2)
        corner_zone_down_left.set_alpha(0.2)
        corner_zone_up_right.set_alpha(0.2)
        corner_zone_down_right.set_alpha(0.2)
        corner_zone_left.set_alpha(0.2)
        corner_zone_right.set_alpha(0.2)
        above_goal_zone_left.set_alpha(0.2)
        above_goal_zone_right.set_alpha(0.2)
        
        # print(f"x = {x[0, 0]}, y = {x[1, 0]}, z = {uwb_z}")
        
        # Verifică dacă mingea a depășit anumite zone și marchează / evidențiază acest lucru
        if is_above_goal_left(x[0, 0], x[1, 0], uwb_z):
            # print("PP")   # peste poartă
            above_goal_zone_left.set_alpha(0.7)
        else:
            if is_above_goal_right(x[0, 0], x[1, 0], uwb_z):
                # print("PP")
                above_goal_zone_right.set_alpha(0.7)
            else:
                if is_goal_left(x[0, 0], x[1, 0]):
                    # print("G")
                    goal_zone_left.set_alpha(0.7)
                else:
                    if is_goal_right(x[0, 0], x[1, 0]):
                        # print("G")
                        goal_zone_right.set_alpha(0.7)
                    else:
                        if is_corner_up_left(x[0, 0], x[1, 0]):
                            # print("P/C")
                            corner_zone_up_left.set_alpha(0.7)
                        else:
                            if is_corner_down_left(x[0, 0], x[1, 0]):
                                # print("P/C")
                                corner_zone_down_left.set_alpha(0.7)
                            else:
                                if is_corner_up_right(x[0, 0], x[1, 0]):
                                    # print("P/C")
                                    corner_zone_up_right.set_alpha(0.7)
                                else:
                                    if is_corner_down_right(x[0, 0], x[1, 0]):
                                        # print("P/C")
                                        corner_zone_down_right.set_alpha(0.7)
                                    else:
                                        if is_corner_left(x[0, 0], x[1, 0]):
                                            corner_zone_left.set_alpha(0.7)
                                        else:
                                            if is_corner_right(x[0, 0], x[1, 0]):
                                                corner_zone_right.set_alpha(0.7)
                                            else:
                                                if is_out_up(x[0, 0], x[1, 0]):
                                                    # print("M")
                                                    out_zone_up.set_alpha(0.7)
                                                else:
                                                    if is_out_down(x[0, 0], x[1, 0]):
                                                        # print("M")
                                                        out_zone_down.set_alpha(0.7)
                
        # Limitează numărul de puncte ce sunt desenate pe grafic pentru a nu încărca memoria și desenul
        if len(x_data) > 10:
            x_data.pop(0)
            y_data.pop(0)

        # Se updatează plotul cu punctele procesate
        sc.set_offsets(list(zip(x_data, y_data)))
        # line.set_xdata(x_data)
        # line.set_ydata(y_data)
         
    #return line,
    return sc

# Setează FuncAnimation pentru a actualiza în timp real graficul
ani = FuncAnimation(fig, update, interval=5, cache_frame_data=False)
plt.show()

# Închide conexiunile seriale
#uwb_ser.close()
# mpu_ser.close()
uwb_socket.close()
mpu_socket.close()
#client_socket.close()