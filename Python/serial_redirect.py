import serial
import threading

# Configurare porturi seriale
COM6_PORT = 'COM6'  # Portul tag-ului UWB
COM3_PORT = 'COM3'  # Portul ESP32
BAUD_RATE = 115200    # Viteza de comunicare pentru ambele porturi

def forward_data(source, destination):
    """
    Funcție care citește date de pe un port serial și le trimite către altul.
    """
    while True:
        try:
            if source.in_waiting > 0:  # Dacă există date disponibile pe port
                data = source.readline().decode('utf-8').strip()  # Citește datele disponibile, linie cu linie
                if data:
                    destination.write((data + '\n').encode('utf-8'))  # Trimite datele către portul de destinație
                # print(data)
        except Exception as e:
            print(f"Eroare în redirecționare: {e}")
            break

def main():
    try:
        # Deschidere conexiuni seriale
        com6 = serial.Serial(COM6_PORT, BAUD_RATE, timeout=1)
        com3 = serial.Serial(COM3_PORT, BAUD_RATE, timeout=1)
        print(f"Conexiuni deschise: {COM6_PORT} -> {COM3_PORT}")

        # Thread pentru redirecționarea datelor
        thread = threading.Thread(target=forward_data, args=(com6, com3))

        thread.start()

        # Așteaptă finalizarea thread-ului (scriptul rulează pe termen lung)
        thread.join()

    except Exception as e:
        print(f"Eroare la configurarea porturilor seriale: {e}")
    finally:
        # Închide porturile seriale la ieșire
        try:
            if com6.is_open:
                com6.close()
            if com3.is_open:
                com3.close()
        except:
            pass
        print("Porturile seriale au fost închise.")

if __name__ == "__main__":
    main()
