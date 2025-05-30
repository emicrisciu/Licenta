import bluetooth
import matplotlib.pyplot as plt
import time
import sys
from collections import deque
import tkinter as tk

# Variabile globale - explain
terminate_program = False
uwb_data_queue = deque(maxlen=10) # size?
mpu_data_queue = deque(maxlen=10)
esp_socket = None #bluetooth.BluetoothSocket(bluetooth.RFCOMM)

def set_bluetooth(esp_addr):
	global esp_socket
	try:
		esp_socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
		esp_socket.connect((esp_addr, 1))   # Connect to ESP32 via BLE (port 1)
		print("Successfully connected to ESP32")
	except bluetooth.BluetoothError as e:
		print(f"Bluetooth connection error: {e}")
		esp_socket = None
		#exit(1)

def read_esp_bluetooth():
    global terminate_program, esp_socket
    while not terminate_program:
        try:
            data = esp_socket.recv(1024).decode('utf-8').strip()
            if data:
                print(f"Data read through BLE: {data}")
                if data[0] == 'T':
                    uwb_data_queue.append(data)
                elif data[0] == 'M':
                    mpu_data_queue.append(data)
                elif data == 'ANCHOR':
                    print("Check Anchors Config")
                    terminate_program = True
                    plt.close('all')
                    sys.exit(0)
        except bluetooth.BluetoothError as e:
            print(f"Bluetooth error reading UWB data: {e}")
            time.sleep(1)
            
def show_popup(message):
	popup = tk.Tk()
	popup.title("Notificare")
	popup.geometry("500x100")
	label = tk.Label(popup, text=message, font=("Arial", 12))
	label.pack(pady=20)
	
	popup.after(1000, popup.destroy)
	popup.mainloop()
            
def bluetooth_health_check():
	global terminate_program, esp_socket
	while not terminate_program:
		try:
			if esp_socket is None:
				raise ConnectionError("ESP socket is None")

			# Trimite un semnal inofensiv sau verifică cu recv non-blocking
			esp_socket.send(b'\n')  # trimite ceva neutru, gen newline
			time.sleep(2)  # verifică la fiecare 2 secunde
		except (OSError, ConnectionError) as e:
			print(f"[ERROR] Conexiunea Bluetooth a eșuat: {e}")
			terminate_program = True
			try:
				esp_socket.close()
			except:
				pass
			time.sleep(1)
			show_popup("Bluetooth deconectat sau indisponibil!")
			plt.close('all')
			break

def range_check(x, y, min_x, max_x, min_y, max_y):
    # Apply a hard limit - heavily weight positions toward the valid range
    if x < min_x:
        x = min_x
    elif x > max_x:
        x = max_x
    
    if y < min_y:
        y = min_y
    elif y > max_y:
        y = max_y
    
    return x, y