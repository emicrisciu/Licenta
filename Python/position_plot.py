import serial
import re
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, Arc
from matplotlib.animation import FuncAnimation
import time
import math

# Configurarea porturilor seriale
uwb_ser = serial.Serial('COM6', 115200)
mpu_ser = serial.Serial('COM3', 115200)

pos_pattern = r"POS:\[(-?\d+),(-?\d+),(-?\d+),(\d+)\]"
mpu_pattern = r"MPU:(-?\d+\.\d+),(-?\d+\.\d+),(-?\d+\.\d+),(-?\d+\.\d+),(-?\d+\.\d+),(-?\d+\.\d+)"

# Configurarea graficului 2D
fig, ax = plt.subplots()
x_data, y_data = [], []
sc = ax.scatter([], [], color='blue')  # Punctul de pe grafic

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

# Variabile pentru integrarea datelor provenite de la IMU
last_time = time.time()
last_pos_x = 0
last_pos_y = 0
imu_dx = 0
imu_dy = 0
dt = 0.05  # Pasul de timp în secunde

# Funcții pentru validarea zonelor specifice în care se află mingea
def is_valid_data(x, y, z, qf):
    return qf < 55 or not (0 <= z)

def is_goal_left(x, y, z, qf):
    return (-60 <= x <= 60) and (185 <= y <= 315)

def is_goal_right(x, y, z, qf):
    return (940 <= x <= 1060) and (185 <= y <= 315)

def is_out_up(x, y, z, qf):
    return (0 <= x <= 1000) and (500 <= y)

def is_out_down(x, y, z, qf):
    return (0 <= x <= 1000) and (0 >= y)

def is_corner_up_left(x, y, z, qf):
    return (-60 <= x <= 0) and (315 <= y <= 500)

def is_corner_down_left(x, y, z, qf):
    return (-60 <= x <= 0) and (0 <= y <= 185)

def is_corner_up_right(x, y, z, qf):
    return (1000 <= x <= 1060) and (315 <= y <= 500)

def is_corner_down_right(x, y, z, qf):
    return (1000 <= x <= 1060) and (0 <= y <= 185)

def is_corner_left(x, y, z, qf):
    return (-100 <= x <= -60) and (0 <= y <= 500)

def is_corner_right(x, y, z, qf):
    return (1060 <= x <= 1100) and (0 <= y <= 500)

def update(frame):
    global last_time, last_pos_x, last_pos_y, imu_dx, imu_dy, dt

    current_time = time.time()
    dt = current_time - last_time
    last_time = current_time

    # Citește datele de la portul serial (UWB)
    if uwb_ser.in_waiting:
        uwb_line = uwb_ser.readline().decode('utf-8').strip()
        uwb_match = re.search(pos_pattern, uwb_line)
        if uwb_match:
            try:
                # Extrage coordonatele tag-ului UWB (x, y)
                x = int(uwb_match.group(1))
                y = int(uwb_match.group(2))
                z = int(uwb_match.group(3))
                qf = int(uwb_match.group(4))
                
                if is_valid_data(x, y, z, qf):
                    # Folosește poziția tag-ului UWB ca referință
                    last_pos_x = x + imu_dx
                    last_pos_y = y + imu_dy
                    
                    # Resetează offset-urile
                    imu_dx, imu_dy = 0, 0
                    
                    # Stochează coordonatele noului punct validat
                    x_data.append(last_pos_x)
                    y_data.append(last_pos_y)
                    
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
                    
                    # Verifică dacă mingea a depășit anumite zone și marchează / evidențiază acest lucru
                    if is_goal_left(x, y, z, qf):
                        # print("G")
                        goal_zone_left.set_alpha(0.7)
                    else:
                        if is_goal_right(x, y, z, qf):
                            # print("G")
                            goal_zone_right.set_alpha(0.7)
                        else:
                            if is_corner_up_left(x, y, z, qf):
                                # print("P/C")
                                corner_zone_up_left.set_alpha(0.7)
                            else:
                                if is_corner_down_left(x, y, z, qf):
                                    # print("P/C")
                                    corner_zone_down_left.set_alpha(0.7)
                                else:
                                    if is_corner_up_right(x, y, z, qf):
                                        # print("P/C")
                                        corner_zone_up_right.set_alpha(0.7)
                                    else:
                                        if is_corner_down_right(x, y, z, qf):
                                            # print("P/C")
                                            corner_zone_down_right.set_alpha(0.7)
                                        else:
                                            if is_corner_left(x, y, z, qf):
                                                corner_zone_left.set_alpha(0.7)
                                            else:
                                                if is_corner_right(x, y, z, qf):
                                                    corner_zone_right.set_alpha(0.7)
                                                else:
                                                    if is_out_up(x, y, z, qf):
                                                        # print("M")
                                                        out_zone_up.set_alpha(0.7)
                                                    else:
                                                        if is_out_down(x, y, z, qf):
                                                            # print("M")
                                                            out_zone_down.set_alpha(0.7)
                            
                    # Limitează numărul de puncte ce sunt desenate pe grafic pentru a nu încărca memoria și desenul
                    if len(x_data) > 10:
                        x_data.pop(0)
                        y_data.pop(0)

                    # Se updatează plotul cu punctele procesate
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
                
                # Calculează deplasamentul folosind accelerația și timpul
                imu_dx += ax * dt**2 / 2  # Δx = 0.5 * ax * dt^2
                imu_dy += ay * dt**2 / 2  # Δy = 0.5 * ay * dt^2
                
            except ValueError as e:
                print(f"Parsing error: {e}")
                
    return sc

# Setează FuncAnimation pentru a actualiza în timp real graficul
ani = FuncAnimation(fig, update, interval=5, cache_frame_data=False)
plt.show()

# Închide conexiunile seriale
uwb_ser.close()
mpu_ser.close()
