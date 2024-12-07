import serial
import re
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Configurarea portului serial
ser = serial.Serial('COM6', 115200)  # Înlocuiește cu portul corect și viteza ta de transmisie

pos_pattern = r"POS:\[(\d+),(\d+),(\d+),(\d+)\]"

# Configurarea graficului 2D
fig, ax = plt.subplots()
x_data, y_data = [], []
sc = ax.scatter([], [], color='blue')  # Punctul de pe grafic

ax.set_xlim(0, 1000)  # Setează limitele axei X
ax.set_ylim(0, 500)  # Setează limitele axei Y
ax.set_title('Poziția Tag-ului în timp real')
ax.set_xlabel('X (mm)')
ax.set_ylabel('Y (mm)')

def is_valid_data(x, y, z, qf):
    if qf < 60:
        return False
    if not (0 <= z):
        return False
    return True

def update(frame):
    # Citește datele de la portul serial (presupunând că sunt în format X,Y,Z)
    line = ser.readline().decode('utf-8').strip()
    match = re.search(pos_pattern, line)
    if match:
        try:
            # Extrage coordonatele X și Y
            x = int(match.group(1))
            y = int(match.group(2))
            z = int(match.group(3))
            qf = int(match.group(4))
            # print(f"Tag Position: X={x}, Y={y}, Z={z}, QF={qf}")
            
            if is_valid_data(x, y, z, qf):
                x_data.append(x)
                y_data.append(y)
                
                # Limiteaza punctele de pe grafic 
                if len(x_data) > 100:
                    x_data.pop(0)
                    y_data.pop(0)

                # Actualizează graficul
                sc.set_offsets(list(zip(x_data, y_data)))
        except ValueError as e:
            print(f"Parsing error: {e}")
    return sc

ani = FuncAnimation(fig, update, interval=100, cache_frame_data=False)
plt.show()

ser.close()