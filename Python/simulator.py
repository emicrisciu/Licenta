import time
import math
import random

def simuleaza_traiectoria():
    """
    Generează o traiectorie simplă cu evenimente interesante.
    Returnează o listă de tuple (x, y, z, timestamp)
    """
    start_x = 900
    start_y = 600
    z = 200  # înălțimea mingii, 20 cm
    qf = 50

    trajectory = []

    # Minge pe teren -> spre poartă dreapta
    for step in range(50):
        x = int(start_x + step * 2)
        y = int(start_y + step * 2) #math.sin(step / 5) * 400)
        trajectory.append((x, y, z, qf))
        time.sleep(0.1)

    # Iese din teren - simulate "gol"
    for step in range(10):
        x += 100
        trajectory.append((x, y, z, qf))
        time.sleep(0.1)
        
    for step in range(50):
        x -= 50
        trajectory.append((x, y, z, qf))
        time.sleep(0.1)
        
    for step in range(10):
        x = 900
        y -= 100
        trajectory.append((x, y, z, qf))
        time.sleep(0.1)

    return trajectory