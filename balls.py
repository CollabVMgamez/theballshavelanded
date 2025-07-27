import socket
import threading
import time

HOST = '0.0.0.0'   # Listen on all interfaces
PORT = 6969        # You know what it is

balls = r"""
         ______
      .-'      '-.
    .'            '.
   /                \
  ;                  ;
  |   O        O     |
  ;    \______/      ;
   \                /
    '.            .'
      '-.______.–'
        /      \
       |        |
     _/|________|\_
    (__)        (__)

     THE BALLS
       HAVE
      LANDED
"""

def handle_client(conn, addr):
    print(f"[+] {addr} connected.")
    try:
        while True:
            conn.sendall((balls + "\n").encode())
            time.sleep(1)
    except:
        print(f"[-] {addr} disconnected.")
    finally:
        conn.close()

def start():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"[*] Listening on port {PORT}...")
        while True:
            conn, addr = s.accept()
            client_thread = threading.Thread(target=handle_client, args=(conn, addr))
            client_thread.start()

if __name__ == "__main__":
    start()
