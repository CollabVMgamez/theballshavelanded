import socket
import threading
import time
import argparse
import logging
import os

# Default ASCII art
DEFAULT_ART = r"""
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

# Load custom ASCII from file if provided
def get_balls(ascii_file=None):
    if ascii_file:
        print(f"[INFO] Attempting to load ASCII art from: {ascii_file}")
        if not os.path.exists(ascii_file):
            print(f"[ERROR] File not found: {ascii_file}")
            return f"[ERROR LOADING ASCII FILE: File does not exist]"
        try:
            with open(ascii_file, 'r', encoding='utf-8') as f:
                content = f.read()
                print(f"[INFO] Loaded {len(content)} characters from ASCII file.")
                return content
        except Exception as e:
            print(f"[ERROR] Failed to read ASCII file: {e}")
            return f"[ERROR LOADING ASCII FILE: {e}]"
    return DEFAULT_ART

# Client handler
def handle_client(conn, addr, log_enabled, ascii_file):
    if log_enabled:
        logging.info(f"Connection from {addr[0]}:{addr[1]}")
    try:
        conn.settimeout(1.0)  # avoid hanging on recv
        try:
            data = conn.recv(1024, socket.MSG_PEEK)
        except socket.timeout:
            data = b''

        balls = get_balls(ascii_file)
        if data.startswith(b"GET "):
            # Respond with HTML page
            balls_html = balls.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            html_body = f"<html><head><meta http-equiv=\"refresh\" content=\"1\"></head><body><pre>{balls_html}</pre></body></html>"
            response = (
                "HTTP/1.1 200 OK\r\n"
                "Content-Type: text/html; charset=utf-8\r\n"
                "Connection: close\r\n"
                f"Content-Length: {len(html_body)}\r\n"
                "\r\n"
                + html_body
            )
            conn.sendall(response.encode())
        else:
            # Raw TCP spam
            while True:
                conn.sendall((balls + "\n").encode())
                time.sleep(1)
    except Exception as e:
        print(f"[ERROR] Client error: {e}")
    finally:
        conn.close()

# Main server
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ASCII Balls TCP Server with optional logging, custom ASCII, and HTML support.")
    parser.add_argument(
        "--no-log", dest="log", action="store_false", help="Disable logging of client connections"
    )
    parser.add_argument(
        "--port", type=int, default=6969, help="Port to listen on (default: 6969)"
    )
    parser.add_argument(
        "--ascii", type=str, default=None, help="Path to a custom ASCII text file"
    )
    args = parser.parse_args()

    # Configure logging
    if args.log:
        logging.basicConfig(filename="connections.log", level=logging.INFO,
                            format="%(asctime)s %(message)s")
    else:
        logging.basicConfig(level=logging.CRITICAL)  # suppress info logs

    HOST = '0.0.0.0'
    PORT = args.port

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen()
        print(f"[*] Listening on {HOST}:{PORT} (logging={'on' if args.log else 'off'})...")
        while True:
            conn, addr = s.accept()
            thread = threading.Thread(target=handle_client, args=(conn, addr, args.log, args.ascii), daemon=True)
            thread.start()

