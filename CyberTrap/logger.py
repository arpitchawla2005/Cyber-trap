from datetime import datetime
import os

def log_attempt(ip, username, password):
    log_file = "log.txt"
    try:
        with open(log_file, "a") as f:
            f.write(f"{datetime.now()} - IP: {ip}, Username: {username}, Password: {password}\n")
        print(f"[LOGGED] {ip} | {username=} | {password=}")
    except Exception as e:
        print(f"[ERROR] Failed to write log: {e}")
