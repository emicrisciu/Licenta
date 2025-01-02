import serial
import re
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, Arc
from matplotlib.animation import FuncAnimation
import time
import numpy as np

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

# Setarea limitelor graficului
ax.set_xlim(-100, field_length + 100)
ax.set_ylim(-50, field_width + 50)
ax.set_title('Teren de fotbal cu poziția mingii în timp real')
ax.set_xlabel('X (mm)')
ax.set_ylabel('Y (mm)')

# Linie centrală, porți și careuri
ax.plot([0, 0], [0, field_width], color='black')  # Linia porții stânga
ax.plot([field_length, field_length], [0, field_width], color='black')  # Linia porții dreapta
ax.plot([0, field_length], [0, 0], color='black')  # Linia de jos
ax.plot([0, field_length], [field_width, field_width], color='black')  # Linia de sus
ax.plot([field_length / 2, field_length / 2], [0, field_width], color='black')  # Linia de mijloc

# Filtru Kalman
dt = 0.05  # Pasul de timp (50 ms între măsurători)
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
    y = z - (H @ x_pred)  # Inovația
    S = H @ P_pred @ H.T + R  # Covarianța inovației
    K = P_pred @ H.T @ np.linalg.inv(S)  # Câștigul Kalman

    x_updated = x_pred + K @ y
    P_updated = (np.eye(4) - K @ H) @ P_pred

    return x_updated, P_updated

# Funcția de actualizare pentru animație
def update(frame):
    global x, P
    
    z = None  # Poziția UWB implicită (inexistentă)
    u = np.zeros((2, 1))  # Intrarea IMU implicită (zero)

    # Citește datele UWB
    if uwb_ser.in_waiting:
        uwb_line = uwb_ser.readline().decode('utf-8').strip()
        uwb_match = re.search(pos_pattern, uwb_line)
        if uwb_match:
            uwb_x = int(uwb_match.group(1))
            uwb_y = int(uwb_match.group(2))
            z = np.array([uwb_x, uwb_y]).reshape((2, 1))
        else:
            z = None  # Dacă nu sunt date valide UWB

    # Citește datele IMU
    if mpu_ser.in_waiting:
        mpu_line = mpu_ser.readline().decode('utf-8').strip()
        mpu_match = re.search(mpu_pattern, mpu_line)
        if mpu_match:
            ax = float(mpu_match.group(1))  # Accelerație X
            ay = float(mpu_match.group(2))  # Accelerație Y
            u = np.array([ax, ay]).reshape((2, 1))
        else:
            u = np.zeros((2, 1))  # Dacă nu sunt date valide IMU
    else:
        u = np.zeros((2, 1))  # Dacă nu există date disponibile în buffer

    # Aplică filtrul Kalman
    if z is not None:
        x, P = kalman_filter(x, P, z, u)

    # Adaugă poziția estimată la grafic
    x_data.append(x[0, 0])  # Poziția estimată X
    y_data.append(x[1, 0])  # Poziția estimată Y

    # Limitează numărul de puncte afișate
    if len(x_data) > 20:
        x_data.pop(0)
        y_data.pop(0)

    # Actualizează graficul
    sc.set_offsets(list(zip(x_data, y_data)))
    return sc

# Setează animația
ani = FuncAnimation(fig, update, interval=5, cache_frame_data=False)
plt.show()

# Închide conexiunile seriale la închiderea aplicației
uwb_ser.close()
mpu_ser.close()
