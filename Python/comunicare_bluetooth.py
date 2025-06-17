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
coada_date_tag_uwb = deque(maxlen=20)
coada_date_imu = deque(maxlen=20)
socket_esp = None

# Zona funcțiilor folosite pentru asigurarea comunicării prin Bluetooth între modulele RaspberryPi și ESP32

def seteaza_conexiune_bluetooth(adresa_mac_esp):
    """
    Funcție ce inițializează conexiunea Bluetooth cu un modul a cărui adresă MAC este furnizată ca parametru
    """
    global socket_esp
    try:
        socket_esp = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        socket_esp.connect((adresa_mac_esp, 1))   # Ne conectăm la ESP32 pe baza adresei sale MAC, pe portul 1
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
                elif data == 'ANCORA':
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
    Funcție ce verifică starea conexiunii Bluetooth și semnalează nevoia de oprire a programului dacă aceasta este întreruptă
    """
    global termina_program, socket_esp
    while not termina_program:
        try:
            if socket_esp is None:
                raise ConnectionError("Nu exista socket ESP!")

			# Trimite un caracter neutru
            socket_esp.send(b'\n')
            time.sleep(2)  # Verifică la fiecare 2 secunde
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