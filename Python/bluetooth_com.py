"""
Acest fișier conține codul destinat asigurării comunicării prin tehnologia fără fir Bluetooth
"""

# Zona importării bibliotecilor

import bluetooth
import matplotlib.pyplot as plt
import time
import sys
from collections import deque
import tkinter as tk

# Zona inițializării variabilelor globale
termina_program = False
coada_date_tag_uwb = deque(maxlen=10) # size?
coada_date_imu = deque(maxlen=10)
socket_esp = None #bluetooth.BluetoothSocket(bluetooth.RFCOMM)

# Zona funcțiilor folosite pentru asigurarea comunicării prin Bluetooth între modulele RaspberryPi și ESP32

def seteaza_conexiune_bluetooth(adresa_mac_esp):
    """
    Funcție ce inițializează conexiunea Bluetooth cu un modul a cărui adresă MAC este furnizată ca parametru
    """
    global socket_esp
    try:
        socket_esp = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        socket_esp.connect((adresa_mac_esp, 1))   # Connect to ESP32 via BLE (port 1)
        print("Conexiunea Bluetooth cu ESP32 s-a efectuat cu succes!")
    except bluetooth.BluetoothError as e:
        print(f"Eroare la conexiunea Bluetooth: {e}")
        socket_esp = None

def citeste_prin_bluetooth():
    """
    Funcție ce citește date prin Bluetooth și le plasează în cozile potrivite în funcție de forma mesajului citit
    """
    global termina_program, socket_esp
    while not termina_program:
        try:
            data = socket_esp.recv(1024).decode('utf-8').strip()
            if data:
                print(f"Date citite prin Bluetooth: {data}")
                if data[0] == 'T':
                    coada_date_tag_uwb.append(data)
                elif data[0] == 'M':
                    coada_date_imu.append(data)
                elif data == 'ANCHOR':
                    print("Verifica configuratia ancorelor!")
                    termina_program = True
                    plt.close('all')
                    sys.exit(0)
        except bluetooth.BluetoothError as e:
            print(f"Eroare la citirea datelor prin Bluetooth: {e}")
            time.sleep(1)
            
def afiseaza_notificare(mesaj):
    """
    Funcție ce creează o notificare de tip pop-up pe ecran, pentru a-i comunica utilizatorului un eveniment legat de depășirea unei linii din terenul de fotbal de către minge
    """
    popup = tk.Tk()
    popup.title("Notificare")
    popup.geometry("500x100")
    label = tk.Label(popup, text=mesaj, font=("Arial", 12))
    label.pack(pady=20)

    popup.after(1000, popup.destroy)
    popup.mainloop()
            
def verifica_conexiune_bluetooth():
    """
    Funcție ce verifică starea conexiunii Bluetooth - DE ACTUALIZAT! DEOCAMDATĂ SE VERIFICĂ DOAR DACĂ CONEXIUNEA A PORNIT, NU ȘI DACĂ SE STINGE PE PARCURS!
    """
    global termina_program, socket_esp
    while not termina_program:
        try:
            if socket_esp is None:
                raise ConnectionError("Nu exista socket ESP!")

			# Trimite un semnal inofensiv sau verifică cu recv non-blocking
            socket_esp.send(b'\n')  # trimite ceva neutru, gen newline
            time.sleep(2)  # verifică la fiecare 2 secunde
        except (OSError, ConnectionError) as e:
            print(f"[ERROR] Conexiunea Bluetooth a eșuat: {e}")
            termina_program = True
            try:
                socket_esp.close()
            except:
                pass
            time.sleep(1)
            afiseaza_notificare("Bluetooth deconectat sau indisponibil!")
            plt.close('all')
            break

def verifica_intervalul_de_valori(x, y, min_x, max_x, min_y, max_y):
    """
    Funcție ce verifică dacă poziția curentă a mingii se află în limitele machetei - DE VĂZUT DACĂ RĂMÂNE AICI SAU ÎN FIȘIERUL PRINCIPAL!
    """
    if x < min_x:
        x = min_x
    elif x > max_x:
        x = max_x
    
    if y < min_y:
        y = min_y
    elif y > max_y:
        y = max_y
    
    return x, y