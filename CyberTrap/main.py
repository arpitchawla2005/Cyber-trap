import socket
import threading
import requests
from datetime import datetime
import csv
import os

HOST = '0.0.0.0'
PORT = 2222
LOG_FILE = "honeypot_logs.csv"

# Get location of IP address
def get_location(ip):
    try:
        data = requests.get(f"http://ip-api.com/json/{ip}").json()
        return data.get('city', 'Unknown'), data.get('country', 'Unknown')
    except:
        return "Unknown", "Unknown"

# Log username and password into a CSV file
def log_attempt(ip, username, password):
    city, country = get_location(ip)
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    file_exists = os.path.isfile(LOG_FILE)

    try:
        with open(LOG_FILE, "a", newline='') as csvfile:
            writer = csv.writer(csvfile)
            if not file_exists:
                writer.writerow(["Timestamp", "IP", "City", "Country", "Username", "Password"])
            writer.writerow([timestamp, ip, city, country, username, password])
        print(f"[LOGGED] {timestamp} | {ip} | {city}, {country} | {username} | {password}")
    except Exception as e:
        print(f"[ERROR] Could not log attempt: {e}")

# Receive a line from client
def receive_line(sock):
    data = b""
    while not data.endswith(b"\n"):
        chunk = sock.recv(1)
        if not chunk:
            break
        data += chunk
    return data.decode(errors="ignore").strip()

# Handle incoming connection
def handle_client(client_socket, client_address):
    try:
        ip = client_address[0]
        print(f"[+] New connection from {ip}")

        client_socket.sendall(b"Welcome to SSH Service\r\nUsername: ")
        username = receive_line(client_socket)

        client_socket.sendall(b"Password: ")
        password = receive_line(client_socket)

        log_attempt(ip, username, password)

        client_socket.sendall(b"Access Denied. Goodbye!\r\n")
    except Exception as e:
        print(f"[ERROR] {e}")
    finally:
        client_socket.close()

# Start the honeypot server
def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(5)
    print(f"[*] Honeypot listening on {HOST}:{PORT} ...")

    while True:
        client, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(client, addr))
        thread.start()

if __name__ == "__main__":
    start_server()
