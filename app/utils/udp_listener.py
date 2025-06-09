import socket
import threading

# Variable global para la última distancia recibida
_ultima_distancia = None
UDP_PORT = 5000

def get_ultima_distancia():
    return _ultima_distancia

def recibir_distancia():
    global _ultima_distancia
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('', UDP_PORT))

    while True:
        try:
            data, addr = sock.recvfrom(1024)
            mensaje = data.decode().strip()
            if mensaje:
                _ultima_distancia = mensaje.split()[1]
                #print(_ultima_distancia)
        except Exception as e:
            print(f"❌ Error al recibir UDP: {e}")

def iniciar_listener_udp():
    hilo = threading.Thread(target=recibir_distancia, daemon=True)
    hilo.start()
    print("🟢 Listener UDP de distancia iniciado")
