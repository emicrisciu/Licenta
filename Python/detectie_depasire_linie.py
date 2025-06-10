"""
Acest fișier conține codul destinat algoritmului de detecție a depășirii liniilor terenului de către mingea de fotbal
"""

# Zona importării bibliotecilor

import teren_fotbal
import math

# Inițializarea dicționarului ce cuprinde marginile terenului
margini_teren = {
    "margine_stanga": [(0, 0), (0, teren_fotbal.latime_teren)],
    "margine_dreapta": [(teren_fotbal.lungime_teren, 0), (teren_fotbal.lungime_teren, teren_fotbal.latime_teren)],
    "margine_inferioara": [(0, 0), (teren_fotbal.lungime_teren, 0)],
    "margine_superioara": [(0, teren_fotbal.latime_teren), (teren_fotbal.lungime_teren, teren_fotbal.latime_teren)]
}

# Zona funcțiilor ce implementează algoritmul de detecție a depășirii liniilor

def verifica_intersectie_segmente(p1, p2, p3, p4):
    """
    Funcție ce determină dacă două segmente de dreaptă se intersectează
    """
    def verifica_sens_opus_acelor_de_ceasornic(A, B, C):
        """
        Funcție ce determină sensul invers al acelor de ceasornic pe care îl determină punctele extreme ale segmentelor
        """
        return (C[1]-A[1]) * (B[0]-A[0]) > (B[1]-A[1]) * (C[0]-A[0])
    
    return (verifica_sens_opus_acelor_de_ceasornic(p1, p3, p4) != verifica_sens_opus_acelor_de_ceasornic(p2, p3, p4) and 
            verifica_sens_opus_acelor_de_ceasornic(p1, p2, p3) != verifica_sens_opus_acelor_de_ceasornic(p1, p2, p4))

def calculeaza_punct_de_intersectie(p1, p2, p3, p4):
    """
    Funcție ce identifică punctul în care se intersectează două segmente
    """
    x1, y1 = p1
    x2, y2 = p2
    x3, y3 = p3
    x4, y4 = p4
    
    # linia 1 scrisă ca a1x + b1y = c1
    a1 = y2 - y1
    b1 = x1 - x2
    c1 = a1*x1 + b1*y1
    
    # linia 2 scrisă ca a2x + b2y = c2
    a2 = y4 - y3
    b2 = x3 - x4
    c2 = a2*x3 + b2*y3
    
    determinant = a1*b2 - a2*b1
    
    if determinant == 0:
        return None  # Liniile sunt paralele
    else:
        x = (b2*c1 - b1*c2)/determinant
        y = (a1*c2 - a2*c1)/determinant
        return (x, y)

def detecteaza_depasirea_liniei(pozitie_curenta, pozitie_anterioara, coordonata_z, dt):
    """
    Funcție ce cuprinde algoritmul de detecție a depășirii liniilor
    """
    mesaj = ""
	# Se verifică dacă mingea depășește vreo margine
    for denumire_margine, puncte_margine in margini_teren.items():
        p3, p4 = puncte_margine
        
        if verifica_intersectie_segmente(pozitie_anterioara, pozitie_curenta, p3, p4):
			# În cazul detecției unei depășiri, se calculează punctul exact prin care mingea a depășit terenul
            punct_de_intersectie = calculeaza_punct_de_intersectie(pozitie_anterioara, pozitie_curenta, p3, p4)
            
			# Determinarea direcției mingii (înăuntru/afară)
            zona_curenta = teren_fotbal.detecteaza_zona(pozitie_curenta[0], pozitie_curenta[1], coordonata_z)
            zona_anterioara = teren_fotbal.detecteaza_zona(pozitie_anterioara[0], pozitie_anterioara[1], coordonata_z)
	
            if zona_anterioara == "teren" and zona_curenta != "teren":
                directie = "afara"
                if zona_curenta in ["peste_poarta_stanga", "peste_poarta_dreapta"]:
                    mesaj = "Mingea a trecut peste poarta!"
                elif zona_curenta in ["poarta_stanga", "poarta_dreapta"]:
                    mesaj = "Gol detectat!"
                else:
                    mesaj = "Mingea a iesit din teren in "
                    if zona_curenta in ["aut_margine_superioara", "aut_margine_inferioara"]:
                        mesaj += "aut de margine!"
                    else:
                        mesaj += "aut de poarta / corner!"
            elif zona_anterioara != "teren" and zona_curenta == "teren":
                directie = "inauntru"
                mesaj = "Mingea a intrat in teren din zona "
                if zona_anterioara in ["peste_poarta_stanga", "peste_poarta_dreapta", "poarta_stanga", "poarta_dreapta"]:
                    mesaj += "portii!"
                elif zona_anterioara in ["aut_margine_superioara", "aut_margine_inferioara"]:
                    mesaj += "autului de margine!"
                else:
                    mesaj += "autului de poarta / cornerului!"
            else:
                directie = "neclara"
            
			# Se calculează viteza cu care mingea a depășit linia
            dx = pozitie_curenta[0] - pozitie_anterioara[0]
            dy = pozitie_curenta[1] - pozitie_anterioara[1]
            viteza = math.sqrt(dx**2 + dy**2) / dt
            
            return {
                "margine": denumire_margine,
                "punct_de_intersectie": punct_de_intersectie,
                "directie": directie,
                "viteza": viteza/1000,
                "mesaj": mesaj
            }
    
    return None
    
# def detecteaza_gol(coordonata_z, punct_de_intersectie, crossing_direction): # TO BE DELETED!
#     return coordonata_z <= 500 and crossing_direction == "afara" and (start_poarta_axa_y <= punct_de_intersectie[1] <= start_poarta_axa_y + latime_poarta)
    
def calculeaza_distanta_punct_dreapta(punct, linie):
	"""
	Funcție ce calculează distanța de la un punct la o dreaptă
	"""
	x0, y0 = punct
	(x1, y1), (x2, y2) = linie

	# Check if the linie points are the same (not a valid linie)
	if (x1, y1) == (x2, y2):
		# Calculate distance to the punct on the linie
		return ((x0 - x1)**2 + (y0 - y1)**2)**0.5

	# Calculate the distance using the formula:
	# d = |Ax0 + By0 + C| / sqrt(A^2 + B^2)
	# where Ax + By + C = 0 is the linie equation

	A = y2 - y1
	B = x1 - x2
	C = x2*y1 - x1*y2

	numarator = abs(A*x0 + B*y0 + C)
	numitor = (A**2 + B**2)**0.5

	return numarator / numitor