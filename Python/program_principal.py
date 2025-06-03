# Zona importării bibliotecilor - unele din ele trebuie eliminate!

import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, Arc
from matplotlib.animation import FuncAnimation
import time
import math
import threading
from collections import deque
import teren_fotbal
import comunicare_bluetooth
import detectie_depasire_linie

# Zona variabilelor globale

semafor = threading.Lock()                                                                                                  # Semafor folosit pentru accesarea datelor procesate din multiple fire de execuție
uwb_x, uwb_y, uwb_z, factor_calitate, acc_x, acc_y, acc_z = teren_fotbal.lungime_teren/2, teren_fotbal.latime_teren/2, 0, 0, 0, 0, 0     # Variabile ce sunt utilizate în funcția de procesare și care rețin valorile coordonatelor și a accelerațiilor pe toate axele
x_data, y_data = [], []                                                                                                     # Liste ce sunt folosite la actualizarea graficului și ce rețin coordonatele în plan ce trebuie desenate
coada_coordonate = deque(maxlen=20)                                                                                         # Buffer circular ce stochează coordonatele mingii, din înregistrări consecutive
timp_anterior = time.time()                                                                                                 # Variabilă ce memorează timpul, folosită în calculul lui dt pentru determinarea diferiților parametrii
adresa_mac_esp = "A0:A3:B3:97:4B:62"                                                                                        # Adresa MAC a ESP32
fanion_activare_medie = False                                                                                               # Fanion de tip boolean care indică aplicarea mediei aritmetice în procesarea pozițiilor consecutive relativ apropiate
prag_medie = 3                                                                                                              # Prag ce reprezintă numărul minim de înregistrări consecutive apropiate ca distanță
contor_medie = 0                                                                                                            # Contor ce numără pozițiile consecutive apropiate între ele
vx, vy = 0, 0                                                                                                               # Variabile ce reprezintă viteze utilizate în implementarea filtrului complementar
x_estimat, y_estimat = 0, 0                                                                                                 # Variabile ce stochează rezultatul apicării filtrului complementar
dt = 0                                                                                                                      # Diferența de timp dintre două măsurători consecutive, folosită în calculul vitezei și a poziției estimate

# Zona funcțiilor folosite în timpul procesării datelor

def filtru_complementar(pos_x, pos_y, acc_x, acc_y, dt):
	"""
	Filtrul complementar ce implică folosirea accelerației pentru rafinarea poziției
	"""
	global x_estimat, y_estimat, vx, vy
	alpha = 0.9 # Ponderea pe care o au coordonatele măsurate în calculul coordonatelor estimate prin filtrul complementar
    
	# Calculul vitezei în funcție de accelerația măsurată
	vx = vx + acc_x * dt
	vy = vy + acc_y * dt
    
	# Calculul coordonatelor estimate în funcție de cele măsurate și de viteză
	x_estimat = alpha * pos_x + (1 - alpha) * (x_estimat + vx * dt)
	y_estimat = alpha * pos_y + (1 - alpha) * (y_estimat + vy * dt)
    
	return x_estimat, y_estimat
	
def verifica_intervalul_de_valori(x, y, min_x, max_x, min_y, max_y):
    """
    Funcție ce verifică dacă poziția curentă a mingii se află în limitele machetei
    """
    # Se limitează valorile ce sunt măsurate pentru coordonate, astfel ca ele să fie vizibile în marginile graficului
    if x < min_x:
        x = min_x
    elif x > max_x:
        x = max_x
    
    if y < min_y:
        y = min_y
    elif y > max_y:
        y = max_y
    
    return x, y
    
def calculeaza_distanta_dintre_puncte(x, y):
    """
    Funcție ce calculează distanța dintre două puncte
    """
    return math.sqrt((x[0] - y[0])**2 + (x[1] - y[1])**2)

def proceseaza_date():
    """
    Funcție ce conține întreaga procesare a datelor și ce rulează într-un fir separat de execuție
    
    Această funcție preia datele curente din cele două cozi ce sunt completate prin conexiunea Bluetooth, le prelucrează și le pune într-o coadă ce va fi citită
    de către firul de execuție responsabil cu actualizarea în timp real a graficului reprezentând terenul de fotbal
    """
    global uwb_x, uwb_y, uwb_z, factor_calitate, acc_x, acc_y, contor_medie, fanion_activare_medie, coada_coordonate, dt
    timp_anterior = time.time()
    while not comunicare_bluetooth.termina_program:
		
        # Se încearcă citirea datelor ce populează cozile aferente coordonatelor și accelerațiilor
        if comunicare_bluetooth.coada_date_tag_uwb:
            try:
                coordonate = comunicare_bluetooth.coada_date_tag_uwb.popleft().split()
                uwb_x = int(coordonate[1])
                uwb_y = int(coordonate[2])
                uwb_z = int(coordonate[3])
                factor_calitate = int(coordonate[4])
            except ValueError as e:
                print(f"Eroare la parcurgerea datelor despre coordonate: {e}")
				
        if comunicare_bluetooth.coada_date_imu:
            try:
                acceleratii = comunicare_bluetooth.coada_date_imu.popleft().split(',')
                acc_x = float(acceleratii[0].split(':')[1])
                acc_y = float(acceleratii[1])
                acc_z = float(acceleratii[2])
            except ValueError as e:
                print(f"Eroare la parcurgerea datelor despre acceleratie: {e}")
		
		# Dacă am citit cu succes coordonatele mingii, continuăm cu aplicarea filtrului complementar și cu verificarea mai multor scenarii
        if uwb_x is not None and uwb_y is not None:
            # Dacă factorul de calitate este mulțumitor, sunt preluate datele primite direct de la senzor, fără prelucrare
            if factor_calitate > 30:
                pozitie_noua = (uwb_x, uwb_y)
            # Se aplică filtrul complementar doar dacă factorul de calitate este nesatisfăcător
            else:
                timp_curent = time.time()
                dt = timp_curent - timp_anterior # ?? scoate afara dt-ul din if-else
                timp_anterior = timp_curent
                pozitie_noua = filtru_complementar(uwb_x, uwb_y, acc_x, acc_y, dt)
			
            # După ce am decis care e poziția mai apropiată de realitate, verificăm să se afle în limitele graficului, din motive mai mult estetice
            pozitie_noua = verifica_intervalul_de_valori(pozitie_noua[0], pozitie_noua[1], -teren_fotbal.margine_teren, teren_fotbal.lungime_teren + teren_fotbal.margine_teren, -teren_fotbal.margine_teren, teren_fotbal.latime_teren + teren_fotbal.margine_teren)
			
            # Se lipesc noile date la coada ce stochează coordonate, folosind un semafor, deoarece aceasta e accesată din mai multe fire de execuție
            with semafor:
                coada_coordonate.append((pozitie_noua[0], pozitie_noua[1]))
				
            # Ne punem problema aplicării unei medii aritmetice asupra coordonatelor pentru cazul când minim 3 măsurători consecutive sunt apropiate între ele
            if len(coada_coordonate) > 1 and calculeaza_distanta_dintre_puncte(coada_coordonate[-1], coada_coordonate[-2]) < 100:
                contor_medie += 1
                if contor_medie > prag_medie:
                    fanion_activare_medie = True
            else:
                contor_medie = 0
                fanion_activare_medie = False
			
            # Dacă ne aflăm în cazul în care se aplică media aritmetică, verificăm dacă avem suficiente elemente în coadă și punem noua înregistrare rezultată în coadă
            if fanion_activare_medie and len(coada_coordonate) > contor_medie - 1:
                suma_x = sum(pozitie[0] for pozitie in list(coada_coordonate)[-contor_medie:])
                suma_y = sum(pozitie[1] for pozitie in list(coada_coordonate)[-contor_medie:])
                punct_medie = (suma_x / contor_medie, suma_y / contor_medie)
                with semafor:
                    coada_coordonate.append(punct_medie) #poate fi problema pt ca tot introduc valori medii in buffer, poate lasam doar partea de afisat sa ia in considerare media!
				
            # Dacă avem cel puțin două măsurători ne putem pune deja problema depășirii liniilor terenului
            if len(coada_coordonate) > 2:
                # Se verifică dacă segmentul realizat de cele mai recente două înregistrări se intersectează cu una dintre marginile terenului
                informatii_depasire_linie = detectie_depasire_linie.detecteaza_depasirea_liniei(coada_coordonate[-1], coada_coordonate[-2], uwb_z, dt)
                # Dacă s-a detectat o depășire, afișăm câteva date relevante despre locul prin care a avut loc "tăierea" liniei
                if informatii_depasire_linie:
                    print(f"\n\nLinia ce a fost depasita: {informatii_depasire_linie['margine']}")
                    print(f"Directia: {informatii_depasire_linie['directie']}")
                    print(f"Punctul prin care a fost depasita linia: ({informatii_depasire_linie['punct_de_intersectie'][0]:.2f}, {informatii_depasire_linie['punct_de_intersectie'][1]:.2f})")
                    print(f"Viteza: {informatii_depasire_linie['viteza']:.2f} m/s")
                    comunicare_bluetooth.afiseaza_notificare(informatii_depasire_linie['mesaj'])
			
			#print(f"pozitie after range check: {processed_position}")
			
			# for boundary_name, boundary_points in margini_teren.items():
				# p1, p2 = boundary_points
				# boundary_line = (p1, p2)
				# if calculeaza_distanta_punct_dreapta(pozitie_noua, boundary_line) < 200:
					# print(f"\n\nDANGEROUS! - {boundary_name}\n\n")
					# set a flag that indicates that the ball is near a field boundary or jump directly to line crossing check
					
			# Handle line crossing detection
			# informatii_depasire_linie = detecteaza_depasirea_liniei(pozitie_noua)
			# if informatii_depasire_linie:
				# print(f"\n\nLine crossed: {informatii_depasire_linie['boundary']}")
				# print(f"Direction: {informatii_depasire_linie['direction']}")
				# print(f"Position: ({informatii_depasire_linie['crossing_point'][0]:.2f}, {informatii_depasire_linie['crossing_point'][1]:.2f})")
				# print(f"Velocity: {informatii_depasire_linie['velocity']:.2f} m/s")
				
				# if detecteaza_gol(local_uwb_z, informatii_depasire_linie['crossing_point'], informatii_depasire_linie['direction']):
					# print("GOAAAAAAAAAAAAAAAAAAAAAAAAAAL!!!")
					# for zona in zone_teren.values():
						# zona.set_alpha(1)
				
				# Here you could add code to trigger actions based on the crossing
				# For example, sending a signal, playing a sound, etc.
			# Handle outliers
			# ~ if coada_coordonate and is_outlier(pozitie_noua, coada_coordonate[-1]):
				# ~ if outlier_count == 0:
					# ~ outlier_position = pozitie_noua
					# ~ outlier_count += 1
					# ~ contor_medie = 0
					# ~ fanion_activare_medie = False
				# ~ else:
					# ~ if math.sqrt((pozitie_noua[0] - outlier_position[0])**2 + (pozitie_noua[1] - outlier_position[1])**2) < 200:
						# ~ outlier_count += 1
						# ~ if outlier_count >= outlier_threshold:
							# ~ outlier_count = 0
							# ~ outlier_position = None
							# ~ interp_x, interp_y = filtru_complementar(local_uwb_x, local_uwb_y, local_acc_x, local_acc_y, dt)
							# ~ coada_coordonate.append((interp_x, interp_y))
					# ~ else:
						# ~ outlier_position = pozitie_noua
						# ~ outlier_count = 1
						# ~ interp_x, interp_y = filtru_complementar(local_uwb_x, local_uwb_y, local_acc_x, local_acc_y, dt)
						# ~ coada_coordonate.append((interp_x, interp_y))
			# ~ else:
				# ~ # Normal position actualizeaza with complementary filter
				# ~ x_estimat, y_estimat = filtru_complementar(local_uwb_x, local_uwb_y, local_acc_x, local_acc_y, dt)
				
				# ~ # Check if position is relatively stable
				# ~ if coada_coordonate and math.sqrt((x_estimat - coada_coordonate[-1][0])**2 + (y_estimat - coada_coordonate[-1][1])**2) < 100:
					# ~ contor_medie += 1
					# ~ if contor_medie >= prag_medie:
						# ~ fanion_activare_medie = True
				# ~ else:
					# ~ contor_medie = 0
					# ~ fanion_activare_medie = False
						
				# ~ coada_coordonate.append((x_estimat, y_estimat))
				
			# ~ coada_coordonate.append((local_uwb_x, local_uwb_y))
			
			# ~ if len(coada_coordonate) >= 5:
				# ~ interp_x, interp_y = qf_weighted_savgol_filter(local_qf)
				# ~ print("\n\n\n\nSMOOOOOTH\n\n\n\n")
			# ~ else:
				# ~ interp_x, interp_y = local_uwb_x, local_uwb_y
			
				# ~ # Apply moving average when ball is stable
				# ~ if len(coada_coordonate) >= 3 and fanion_activare_medie:
					# ~ suma_x = sum(pozitie[0] for pozitie in coada_coordonate)
					# ~ suma_y = sum(pozitie[1] for pozitie in coada_coordonate)
					# ~ avg_x = suma_x / len(coada_coordonate)
					# ~ avg_y = suma_y / len(coada_coordonate)
					# ~ interp_x, interp_y = avg_x, avg_y
				# ~ else:
					# ~ interp_x, interp_y = x_estimat, y_estimat
					
			# ~ interp_x, interp_y = enhanced_position_filter(local_uwb_x, local_uwb_y, local_qf)
			# ~ interp_x, interp_y = local_uwb_x, local_uwb_y

def actualizeaza(cadru):
    """
    Funcție ce va rula într-un fir de execuție separat și este responsabilă cu citirea datelor din coada ce se completează cu date procesate și cu actualizarea graficului afișat pe ecran
    """
    global semafor, coada_coordonate, uwb_z
	
    # Dacă avem elemente în coada ce stochează coordonate, continuăm cu afișarea acestora pe grafic
    if coada_coordonate:
        # Citim primul element din coadă
        with semafor:
            x, y = coada_coordonate.popleft()
			
        if x is not None and y is not None:
            x_data.append(x)
            y_data.append(y)
            
            # Limităm numărul de puncte ce apar simultan pe ecran la 10, pentru eficientizarea programului
            if len(x_data) > 10:
                x_data.pop(0)
                y_data.pop(0)
			
            # Se actualizează punctele de pe grafic
            teren_fotbal.sc.set_offsets(list(zip(x_data, y_data)))
			
			# Se resetează intensitatea culorilor fiecărei zonă
            for zona in teren_fotbal.zone_teren.values():
                zona.set_alpha(0.2)
				
			# Se detectează zona în care se află mingea și se evidențiază, crescând intensitatea culorii
            zona = teren_fotbal.detecteaza_zona(x, y, uwb_z)
            if zona in teren_fotbal.zone_teren:
                teren_fotbal.zone_teren[zona].set_alpha(0.7)
			
            # Se împachetează elementele ce sunt actualizate de către funcția de animație într-un format suportat de aceasta
            elemente_de_actualizat = [teren_fotbal.sc]
            for nume_zona, zona in teren_fotbal.zone_teren.items():
                elemente_de_actualizat.append(zona)
				
            return tuple(elemente_de_actualizat)
	
    return tuple()
	# start_time = time.time()
	# global timp_anterior, uwb_x, uwb_y, uwb_z, factor_calitate, acc_x, acc_y, acc_z
	# #global factor_calitate, x_estimat, y_estimat, uwb_x, uwb_y, uwb_z, acc_x, acc_y, timp_anterior, interp_x, interp_y, dt, termina_program
	# #global outlier_count, outlier_position, fanion_activare_medie, contor_medie
	# #global last_zone, detectie_depasire_linie_confidence, crossing_cooldown
    
	# if comunicare_bluetooth.termina_program:
		# return tuple()
    
	# timp_curent = time.time()
	# dt = timp_curent - timp_anterior
	# print(f"dt = {dt}")
	# timp_anterior = timp_curent

	# # with lock:
		# # local_uwb_x = uwb_x
		# # local_uwb_y = uwb_y
		# # local_uwb_z = uwb_z
		# # local_qf = factor_calitate
		# # local_acc_x = acc_x
		# # local_acc_y = acc_y
        
	
	# end_time = time.time()
    
	# elemente_de_actualizat = [teren_fotbal.sc]
	# # for nume_zona, zona in teren_fotbal.zone_teren.items():
		# # elemente_de_actualizat.append(zona) BIG PROBLEM TO SOLVE

	# print(f"cadru processing time: {end_time - start_time:.4f} seconds")
	# print(f"Returned artists: {elemente_de_actualizat}")
	# return tuple(elemente_de_actualizat)


# def update1(cadru):
	# teren_fotbal.sc.set_offsets([[0, 0]])
	# return (teren_fotbal.sc,)

def functie_de_test():
    """
    Funcție ce va rula într-un fir de execuție separat și ce simulează o traiectorie a mingii definită manual, pentru a fi utilizată în modul de testare 
    """
    from simulator import simuleaza_traiectoria
    traiectorie = simuleaza_traiectoria()
    for x, y, z, factor_calitate in traiectorie:
        comunicare_bluetooth.coada_date_tag_uwb.append(f"T {x} {y} {z} {factor_calitate}")
        time.sleep(0.1)


# Main execution
def main(mod_test=False):
    """
    Funcția principală a sistemului în care se creează și se pornesc firele paralele de execuție 
    """
	#global termina_program
    try:
        # Setarea conexiunii Bluetooth
        comunicare_bluetooth.seteaza_conexiune_bluetooth(adresa_mac_esp)
        teren_fotbal.deseneaza_teren()
		
        # Dacă nu este activat modul de test, atunci programul decurge normal și sunt pornite firele de execuție ce se ocupă de conexiunea Bluetooth și citirea datelor
        if not mod_test:
            fir_executie_verificare_bluetooth = threading.Thread(target=comunicare_bluetooth.verifica_conexiune_bluetooth, daemon=True)
            fir_executie_verificare_bluetooth.start()
			
			# Start thread for data handling
            fir_executie_citire_date = threading.Thread(target=comunicare_bluetooth.citeste_prin_bluetooth, daemon=True)
            fir_executie_citire_date.start()
		
        # Dacă este activat modul de test, atunci programul pornește un fir de execuție pentru simularea unei traiectorii
        else:
            fir_executie_testare = threading.Thread(target=functie_de_test, daemon=True)
            fir_executie_testare.start()
		
        # Firul de exeucție ce se ocupă cu procesarea datelor trebuie pornit în orice caz
        fir_executie_procesare = threading.Thread(target=proceseaza_date, daemon=True)
        fir_executie_procesare.start()
		
		# Se creează animația în timp real a terenului de fotbal 2D
        ani = FuncAnimation(teren_fotbal.fig, actualizeaza, interval=20, cache_frame_data=False, blit=True)
		
		# Se afișează graficul
        plt.show()
		
    except KeyboardInterrupt:
        print("Programul a fost oprit de către utilizator!")
        comunicare_bluetooth.termina_program = True
    finally:
        comunicare_bluetooth.termina_program = True
        if comunicare_bluetooth.socket_esp is not None:
            comunicare_bluetooth.socket_esp.close()
            print("Conexiunea Bluetooth a fost închisă!")
        exit(1)

if __name__ == "__main__":
    main(mod_test=False)