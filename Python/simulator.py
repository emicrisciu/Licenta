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
    z = 200
    qf = 50

    trajectory = []

    for step in range(50):
        x = int(start_x + step * 2)
        y = int(start_y + step * 2) #math.sin(step / 5) * 400)
        trajectory.append((x, y, z, qf))
        time.sleep(0.1)
    
    for step in range(50):
        x = start_x + 880 + step * 3
        y = 600
        trajectory.append((x, y, z, qf))
        time.sleep(0.1)
        
    for step in range(50):
        x = 900
        y = start_y + 550 + step *3
        trajectory.append((x, y, z, qf))
        time.sleep(0.1)
        
    for step in range(10):
        x -= 100
        trajectory.append((x, y, z, qf))
        time.sleep(0.5)
        
    for step in range(10):
        y -= 100
        trajectory.append((x, y, z, qf))
        time.sleep(0.5)
        
    return trajectory