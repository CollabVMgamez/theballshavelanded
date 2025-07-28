import socket
import threading
import time
import argparse
import logging

# ASCII art payload
def get_balls():
    return r"""
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

# Client handler
def handle_client(conn, addr, log_enabled):
    if log_enabled:
        logging.info(f"Connection from {addr[0]}:{addr[1]}")
    try:
        # Peek at incoming data to detect HTTP GET
        data = conn.recv(1024, socket.MSG_PEEK)
        if data.startswith(b"GET "):
            # Respond with HTML page
            balls_html = get_balls().replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
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
                conn.sendall((get_balls() + "\n").encode())
                time.sleep(1)
    except Exception:
        pass
    finally:
        conn.close()

# Main server
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ASCII Balls TCP Server with optional logging and HTML support.")
    parser.add_argument(
        "--no-log", dest="log", action="store_false", help="Disable logging of client connections"
    )
    parser.add_argument(
        "--port", type=int, default=6969, help="Port to listen on (default: 6969)"
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
            thread = threading.Thread(target=handle_client, args=(conn, addr, args.log), daemon=True)
            thread.start()
