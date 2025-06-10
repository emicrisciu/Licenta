"""
Acest fișier conține codul dedicat desenării graficului 2D asociat terenului de fotbal
"""

# Zona importării bibliotecilor

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, Arc

# Zona inițializării variabilelor globale și a elementelor ce constituie desenul

fig, ax = plt.subplots(figsize=(16, 9)) # Figura va avea raportul 16:9, potrivit pentru majoritatea ecranelor
# Mai jos sunt inițializate zonele terenului, vizibile global
poarta_stanga = None
poarta_dreapta = None
aut_margine_superioara = None
aut_margine_inferioara = None
aut_de_poarta_stanga_sus = None
aut_de_poarta_stanga_jos = None
aut_de_poarta_dreapta_sus = None
aut_de_poarta_dreapta_jos = None
aut_de_poarta_stanga = None
aut_de_poarta_dreapta = None
peste_poarta_stanga = None
peste_poarta_dreapta = None
sc = ax.scatter([], [])
# Mai jos sunt inițializate variabilele globale reprezentând dimensiunile machetei, toate fiind măsurate în mm
lungime_teren = 1800 
latime_teren = 1200   
goal_depth = 150 
start_poarta_axa_y = 350
latime_poarta = 500
latime_careu_mare = 297
start_careu_mare_axa_y = 223
latime_careu_mic = 99
punct_penalty = 197
raza_cercuri = 163
margine_teren = 200
# Mai jos este dicționarul ce va conține perechi de tip denumire - zonă pentru toate zonele terenului
zone_teren = {}

# Zona funcțiilor folosite în timpul desenării terenului de fotbal

def deseneaza_teren():
    """
    Funcția ce se ocupă cu crearea și desenarea tuturor liniilor și zonelor ce alcătuiesc un teren de fotbal
    """
    
    # Variabilele globale ce sunt folosite în interiorul acestei funcții
    global ax, sc, poarta_stanga, poarta_dreapta, aut_margine_superioara, aut_margine_inferioara
    global aut_de_poarta_stanga_sus, aut_de_poarta_stanga_jos, aut_de_poarta_dreapta_sus, aut_de_poarta_dreapta_jos
    global aut_de_poarta_stanga, aut_de_poarta_dreapta, peste_poarta_stanga, peste_poarta_dreapta
    global lungime_teren, latime_teren, goal_depth, latime_poarta, start_poarta_axa_y, start_poarta_axa_y, latime_careu_mare, latime_careu_mic

    # Mingea va fi desenată ca un punct pe grafic
    sc = ax.scatter([], [], color='blue', s=50)

    # Setarea limitelor graficului
    ax.set_xlim(-margine_teren, lungime_teren + margine_teren)
    ax.set_ylim(-margine_teren, latime_teren + margine_teren)
    ax.set_title('Poziția în timp real a mingii pe terenul de fotbal')
    ax.set_xlabel('X (mm)')
    ax.set_ylabel('Y (mm)')

    # Desenarea marginilor terenului de fotbal
    ax.plot([0, 0], [0, latime_teren], color='black')  # Left goal line
    ax.plot([lungime_teren, lungime_teren], [0, latime_teren], color='black')  # Right goal line
    ax.plot([0, lungime_teren], [0, 0], color='black')  # Bottom line
    ax.plot([0, lungime_teren], [latime_teren, latime_teren], color='black')  # Top line
    ax.plot([lungime_teren / 2, lungime_teren / 2], [0, latime_teren], color='black')  # Middle line

    # Desenarea porților
    # Poarta stângă
    ax.plot([-goal_depth, 0], [start_poarta_axa_y, start_poarta_axa_y], color='grey', linewidth=1.2)
    ax.plot([-goal_depth, -goal_depth], [start_poarta_axa_y, latime_teren - start_poarta_axa_y], color='grey', linewidth=1.2)
    ax.plot([-goal_depth, 0], [latime_teren - start_poarta_axa_y, latime_teren - start_poarta_axa_y], color='grey', linewidth=1.2)
    # Poarta dreaptă
    ax.plot([lungime_teren, lungime_teren + goal_depth], [start_poarta_axa_y, start_poarta_axa_y], color='grey', linewidth=1.2)
    ax.plot([lungime_teren + goal_depth, lungime_teren + goal_depth], [start_poarta_axa_y, latime_teren - start_poarta_axa_y], color='grey', linewidth=1.2)
    ax.plot([lungime_teren, lungime_teren + goal_depth], [latime_teren - start_poarta_axa_y, latime_teren - start_poarta_axa_y], color='grey', linewidth=1.2)

    # Cercul de la centrul terenului
    center_circle = Circle((lungime_teren / 2, latime_teren / 2), raza_cercuri, edgecolor='black', facecolor='none', linestyle='-')
    ax.add_patch(center_circle)

    # Punctul din centrul terenului
    ax.scatter([lungime_teren / 2], [latime_teren / 2], color='black')

    # Careurile mari
    penalty_area_left = Rectangle((0, start_careu_mare_axa_y), latime_careu_mare, latime_teren - 2 * start_careu_mare_axa_y, edgecolor='black', facecolor='none')
    penalty_area_right = Rectangle((lungime_teren - latime_careu_mare, start_careu_mare_axa_y), latime_careu_mare, latime_teren - 2 * start_careu_mare_axa_y, edgecolor='black', facecolor='none')
    ax.add_patch(penalty_area_left)
    ax.add_patch(penalty_area_right)

    # Careurile mici
    goal_area_left = Rectangle((0, start_poarta_axa_y), latime_careu_mic, latime_poarta, edgecolor='black', facecolor='none')
    goal_area_right = Rectangle((lungime_teren - latime_careu_mic, start_poarta_axa_y), latime_careu_mic, latime_poarta, edgecolor='black', facecolor='none')
    ax.add_patch(goal_area_left)
    ax.add_patch(goal_area_right)

    # Punctele pentru loviturile de la 11 metri
    ax.scatter([punct_penalty], [latime_teren / 2], color='black')
    ax.scatter([lungime_teren - punct_penalty], [latime_teren / 2], color='black')

    # Semicercurile din dreptul careurilor mari
    penalty_arc_left = Arc((punct_penalty, latime_teren / 2), 2 * raza_cercuri, 320, angle=0, theta1=308, theta2=52, edgecolor='black')
    penalty_arc_right = Arc((lungime_teren - punct_penalty, latime_teren / 2), 2 * raza_cercuri, 320, angle=0, theta1=128, theta2=232, edgecolor='black')
    ax.add_patch(penalty_arc_left)
    ax.add_patch(penalty_arc_right)

    # Zonele în care considerăm că s-a marcat un gol
    poarta_stanga = Rectangle((-goal_depth, start_poarta_axa_y), goal_depth, latime_poarta, color='green', alpha=0.2)
    poarta_dreapta = Rectangle((lungime_teren, start_poarta_axa_y), goal_depth, latime_poarta, color='green', alpha=0.2)
    ax.add_patch(poarta_stanga)
    zone_teren["poarta_stanga"] = poarta_stanga
    ax.add_patch(poarta_dreapta)
    zone_teren["poarta_dreapta"] = poarta_dreapta

    # Zonele de aut de margine, din partea superioară, respectiv inferioară a terenului
    aut_margine_superioara = Rectangle((-margine_teren, latime_teren), lungime_teren + 2 * margine_teren, margine_teren, color='red', alpha=0.2)
    aut_margine_inferioara = Rectangle((-margine_teren, -margine_teren), lungime_teren + 2 * margine_teren, margine_teren, color='red', alpha=0.2)
    ax.add_patch(aut_margine_superioara)
    zone_teren["aut_margine_superioara"] = aut_margine_superioara
    ax.add_patch(aut_margine_inferioara)
    zone_teren["aut_margine_inferioara"] = aut_margine_inferioara

    # Zonele de corner / aut de poartă
    aut_de_poarta_stanga_sus = Rectangle((-goal_depth, start_poarta_axa_y + latime_poarta), goal_depth, start_poarta_axa_y, color='orange', alpha=0.2)
    aut_de_poarta_stanga_jos = Rectangle((-goal_depth, 0), goal_depth, start_poarta_axa_y, color='orange', alpha=0.2)
    aut_de_poarta_stanga = Rectangle((-margine_teren, 0), margine_teren - goal_depth, latime_teren, color='orange', alpha=0.2)
    aut_de_poarta_dreapta_sus = Rectangle((lungime_teren, start_poarta_axa_y + latime_poarta), goal_depth, start_poarta_axa_y, color='orange', alpha=0.2)
    aut_de_poarta_dreapta_jos = Rectangle((lungime_teren, 0), goal_depth, start_poarta_axa_y, color='orange', alpha=0.2)
    aut_de_poarta_dreapta = Rectangle((lungime_teren + goal_depth, 0), margine_teren - goal_depth, latime_teren, color='orange', alpha=0.2)
    ax.add_patch(aut_de_poarta_stanga_sus)
    zone_teren["aut_de_poarta_stanga_sus"] = aut_de_poarta_stanga_sus
    ax.add_patch(aut_de_poarta_stanga_jos)
    zone_teren["aut_de_poarta_stanga_jos"] = aut_de_poarta_stanga_jos
    ax.add_patch(aut_de_poarta_stanga)
    zone_teren["aut_de_poarta_stanga"] = aut_de_poarta_stanga
    ax.add_patch(aut_de_poarta_dreapta_sus)
    zone_teren["aut_de_poarta_dreapta_sus"] = aut_de_poarta_dreapta_sus
    ax.add_patch(aut_de_poarta_dreapta_jos)
    zone_teren["aut_de_poarta_dreapta_jos"] = aut_de_poarta_dreapta_jos
    ax.add_patch(aut_de_poarta_dreapta)
    zone_teren["aut_de_poarta_dreapta"] = aut_de_poarta_dreapta

    # Zonele ce indică faptul că mingea a trecut peste poartă. Ele se suprapun cu zonele de gol
    peste_poarta_stanga = Rectangle((-goal_depth, start_poarta_axa_y), goal_depth, latime_poarta, color='orange', alpha=0.2)
    peste_poarta_dreapta = Rectangle((lungime_teren, start_poarta_axa_y), goal_depth, latime_poarta, color='orange', alpha=0.2)
    ax.add_patch(peste_poarta_stanga)
    zone_teren["peste_poarta_stanga"] = peste_poarta_stanga
    ax.add_patch(peste_poarta_dreapta)
    zone_teren["peste_poarta_dreapta"] = peste_poarta_dreapta

def detecteaza_zona(x, y, z):
    """
    Funcție ce determină zona în care se află mingea la momentul curent, folosită pentru a evidenția zona în cauză în funcția ce actualizează desenul
    """
    if (-goal_depth <= x <= 0) and (start_poarta_axa_y <= y <= start_poarta_axa_y + latime_poarta) and (z >= 250):
        return "peste_poarta_stanga"
    elif (lungime_teren <= x <= lungime_teren + goal_depth) and (start_poarta_axa_y <= y <= start_poarta_axa_y + latime_poarta) and (z >= 250):
        return "peste_poarta_dreapta"
    if (-goal_depth <= x <= 0) and (start_poarta_axa_y <= y <= start_poarta_axa_y + latime_poarta):
        return "poarta_stanga"
    elif (lungime_teren <= x <= lungime_teren + goal_depth) and (start_poarta_axa_y <= y <= start_poarta_axa_y + latime_poarta):
        return "poarta_dreapta"
    elif (-margine_teren <= x <= lungime_teren + margine_teren) and (y > latime_teren):
        return "aut_margine_superioara"
    elif (-margine_teren <= x <= lungime_teren + margine_teren) and (y < 0):
        return "aut_margine_inferioara"
    elif (-goal_depth <= x <= 0) and (start_poarta_axa_y + latime_poarta <= y <= latime_teren):
        return "aut_de_poarta_stanga_sus"
    elif (-goal_depth <= x <= 0) and (0 <= y <= start_poarta_axa_y):
        return "aut_de_poarta_stanga_jos"
    elif (lungime_teren <= x <= lungime_teren + goal_depth) and (start_poarta_axa_y + latime_poarta <= y <= latime_teren):
        return "aut_de_poarta_dreapta_sus"
    elif (lungime_teren <= x <= lungime_teren + goal_depth) and (0 <= y <= start_poarta_axa_y):
        return "aut_de_poarta_dreapta_jos"
    elif (-margine_teren <= x <= -goal_depth) and (0 <= y <= latime_teren):
        return "aut_de_poarta_stanga"
    elif (lungime_teren + goal_depth <= x <= lungime_teren + margine_teren) and (0 <= y <= latime_teren):
        return "aut_de_poarta_dreapta"
    else:
        return "teren"