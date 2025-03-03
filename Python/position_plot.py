import serial
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, Arc
from matplotlib.animation import FuncAnimation
import time
import math
import numpy as np
import threading
from queue import Queue
import bluetooth

esp_addr = "A0:A3:B3:97:4B:62"  # Adresa MAC a lui ESP32

esp_socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)

esp_socket.connect((esp_addr, 1))   # Conectarea prin BLE la ESP32 (prin portul 1)

# Cozile ce vor conține datele venite prin BLE de la tag-ul UWB și de la IMU
uwb_data_queue = Queue()
mpu_data_queue = Queue()

# Folosim un lock pentru a bloca accesul la coadă din alt thread în timpul verificării numarului de elemente
lock = threading.Lock()

# Funcție ce șterge cele mai vechi n elemente din coada q
def delete_old_elements(q, n):
    for _ in range(n):
        if not q.empty():
            deleted = q.get()
            
# Funcție ce gestionează coada cu date de la tag-ul UWB            
def read_uwb_bluetooth():
    while True:
        data = esp_socket.recv(1024).decode('utf-8').strip()
        if data:
            print(data)
            if data[0] == "T":
                uwb_data_queue.put(data)
                with lock:
                    if uwb_data_queue.qsize() >= 20:
                        delete_old_elements(uwb_data_queue, 10)

# Funcție ce gestionează coada cu date de la senzorul IMU
def read_mpu_bluetooth():
    while True:
        data = esp_socket.recv(1024).decode('utf-8').strip()
        if data:
            print(data)
            if data[0] == "M":
                mpu_data_queue.put(data)
                with lock:
                    if mpu_data_queue.qsize() >= 20:
                        delete_old_elements(mpu_data_queue, 10)                            
                
fig, ax = plt.subplots()
x_data, y_data = [], []
goal_zone_left = None
goal_zone_right = None
out_zone_up = None
out_zone_down = None
corner_zone_up_left = None
corner_zone_down_left = None
corner_zone_up_right = None
corner_zone_down_right = None
corner_zone_left = None
corner_zone_right = None
above_goal_zone_left = None
above_goal_zone_right = None
sc = None
qf = 100    # Inițialiare variabilă globală factor de calitate

def draw_field():
    # Configurarea graficului 2D
    global ax, sc, goal_zone_left, goal_zone_right, out_zone_up, out_zone_down, corner_zone_up_left, corner_zone_down_left, corner_zone_up_right, corner_zone_down_right, corner_zone_left, corner_zone_right, above_goal_zone_left, above_goal_zone_right
    
    sc = ax.scatter([], [], color='blue')  # Punctul de pe grafic
    # line, = ax.plot([], [], 'bo', markersize=5)

    # def init():
    #     ax.set_xlim(-100, field_length + 100)  # Voi desena terenul mai lung decât în mod normal pentru a observa și zona din spatele porții
    #     ax.set_ylim(-50, field_width + 50) # Voi desena terenul mai lat decât în mod normal pentru a observa și zona auturilor
    #     return line,

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
 
# Implementarea filtrului complementar pentru a ajusta poziția și în funcție de datele citite de la IMU    
alpha = 0.9
dt = 0.1
x_est, y_est = 0, 0
vx, vy = 0, 0

def complementary_filter(pos_x, pos_y, acc_x, acc_y):
    global x_est, y_est, vx, vy
    
    vx = vx + acc_x * dt
    vy = vy + acc_y * dt
    
    x_est = alpha * pos_x + (1 - alpha) * (x_est + vx *dt)
    y_est = alpha * pos_y + (1 - alpha) * (y_est + vy *dt)
    
    return x_est, y_est

# Funcții pentru validarea zonelor specifice în care se află mingea
def is_valid_data(qf):
    return qf >= 1

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

uwb_z, uwb_x, uwb_y = 0, 0, 0 
acc_x, acc_y = 0, 0

# Funcție ce gestionează ce se întâmplă la fiecare frame ce se desenează
def update(frame):
    global P, qf, uwb_x, uwb_y, uwb_z, acc_x, acc_y
    
    z = None    # Poziția UWB implicită (inexistentă)
    u = np.zeros((2, 1))    # Intrarea IMU implicită (zero)

    # Citește datele de la portul serial (UWB)
    if not uwb_data_queue.empty():
        try:
            uwb_line = uwb_data_queue.get()
            coords = uwb_line.split()
            uwb_x = int(coords[1])
            uwb_y = int(coords[2])
            uwb_z = int(coords[3])
            qf = int(coords[4])
            z = np.array([uwb_x, uwb_y]).reshape((2, 1))
            
        except ValueError as e:
            print(f"Parsing error: {e}")
    
    # Citește datele de la portul serial (MPU)
    if not mpu_data_queue.empty():
        try:
            mpu_line = mpu_data_queue.get()
            imu_data = mpu_line.split(',')
            acc_x = float(imu_data[0].split(':')[1])
            acc_y = float(imu_data[1])
            u = np.array([acc_x, acc_y]).reshape((2, 1))
            
        except ValueError as e:
            print(f"Parsing error: {e}")
    
    # Aplică filtrul complementar
    uwb_x, uwb_y = complementary_filter(uwb_x, uwb_y, acc_x, acc_y)
    
    if (uwb_x and uwb_y):
        if is_valid_data(qf):
            # Adaugă poziția estimată la grafic
            x_data.append(uwb_x)  # Poziția estimată X
            y_data.append(uwb_y)  # Poziția estimată Y
            
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
            
            # print(f"x = {x}, y = {y}, z = {uwb_z}")
            
            # Verifică dacă mingea a depășit anumite zone și marchează / evidențiază acest lucru
            if is_above_goal_left(uwb_x, uwb_y, uwb_z):
                # print("PP")   # peste poartă
                above_goal_zone_left.set_alpha(0.7)
            else:
                if is_above_goal_right(uwb_x, uwb_y, uwb_z):
                    # print("PP")
                    above_goal_zone_right.set_alpha(0.7)
                else:
                    if is_goal_left(uwb_x, uwb_y):
                        # print("G")
                        goal_zone_left.set_alpha(0.7)
                    else:
                        if is_goal_right(uwb_x, uwb_y):
                            # print("G")
                            goal_zone_right.set_alpha(0.7)
                        else:
                            if is_corner_up_left(uwb_x, uwb_y):
                                # print("P/C")
                                corner_zone_up_left.set_alpha(0.7)
                            else:
                                if is_corner_down_left(uwb_x, uwb_y):
                                    # print("P/C")
                                    corner_zone_down_left.set_alpha(0.7)
                                else:
                                    if is_corner_up_right(uwb_x, uwb_y):
                                        # print("P/C")
                                        corner_zone_up_right.set_alpha(0.7)
                                    else:
                                        if is_corner_down_right(uwb_x, uwb_y):
                                            # print("P/C")
                                            corner_zone_down_right.set_alpha(0.7)
                                        else:
                                            if is_corner_left(uwb_x, uwb_y):
                                                corner_zone_left.set_alpha(0.7)
                                            else:
                                                if is_corner_right(uwb_x, uwb_y):
                                                    corner_zone_right.set_alpha(0.7)
                                                else:
                                                    if is_out_up(uwb_x, uwb_y):
                                                        # print("M")
                                                        out_zone_up.set_alpha(0.7)
                                                    else:
                                                        if is_out_down(uwb_x, uwb_y):
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

ani = None
def animation():
    global ani
    # Setează FuncAnimation pentru a actualiza în timp real graficul
    ani = FuncAnimation(fig, update, interval=100, cache_frame_data=False)

# Se pornesc thread-urile
threading.Thread(target=draw_field, daemon=True).start()
threading.Thread(target=read_uwb_bluetooth, daemon=True).start()
threading.Thread(target=read_mpu_bluetooth, daemon=True).start()
threading.Thread(target=animation, daemon=True).start()

plt.show()

# Închide toate conexiunile
esp_socket.close()