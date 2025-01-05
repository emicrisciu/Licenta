import serial
import threading
import socket

# Configurare porturi seriale
COM6_PORT = 'COM6'  # Portul tag-ului UWB
COM3_PORT = 'COM3'  # Portul ESP32
BAUD_RATE = 115200    # Viteza de comunicare pentru ambele porturi
#SOCKET_PORT = 5000

def forward_data(source, destination):
    """
    Funcție care citește date de pe un port serial și le trimite către altul.
    """
    while True:
        try:
            if source.in_waiting > 0:  # Dacă există date disponibile pe port
                data = source.readline().decode('utf-8').strip()  # Citește datele disponibile
                if data:
                    destination.write((data + '\n').encode('utf-8'))  # Trimite datele către portul de destinație
                    #destination.sendall((data + '\n').encode('utf-8'))  # Trimite datele către portul de destinație
                print(data)
        except Exception as e:
            print(f"Eroare în redirecționare: {e}")
            break

def main():
    try:
        # Deschidere conexiuni seriale
        com6 = serial.Serial(COM6_PORT, BAUD_RATE, timeout=1)
        com3 = serial.Serial(COM3_PORT, BAUD_RATE, timeout=1)
        print(f"Conexiuni deschise: {COM6_PORT} -> {COM3_PORT}")
        
        # # Configurare socket server
        # server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # server_socket.bind(('localhost', SOCKET_PORT))
        # server_socket.listen(1)
        # print(f"Socket server ascultă pe portul {SOCKET_PORT}")
        
        #  # Așteptă conexiune de la alt script
        # client_socket, addr = server_socket.accept()
        # print(f"Client conectat de la: {addr}")

        # Thread-uri pentru redirecționare bidirecțională
        thread1 = threading.Thread(target=forward_data, args=(com6, com3))
        #thread2 = threading.Thread(target=forward_data, args=(com3, com6))

        thread1.start()
        #thread2.start()

        # Așteaptă finalizarea thread-urilor (de obicei, acest script rulează pe termen lung)
        thread1.join()
        #thread2.join()

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
