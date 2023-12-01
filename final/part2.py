from argparse import ArgumentParser
import sys
import os
import time
from datetime import datetime
from socket import *
import csv

def log_csv(server_ip, server_port, client_ip, client_port, url, status_line, content_length):
    with open('tasoodSocketOutput.csv', mode='a') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(["Client request served", "4-Tuple:", server_ip, server_port, client_ip, client_port,
                             "Requested URL", url, status_line, "Bytes sent:", content_length])

def log_text(response):
    status_line = response.split(b"\r\n")[0].decode()
    headers = response.decode().split("\r\n\r\n")[0]
    with open('tasoodHTTPResponses.txt', 'a') as file:
        file.write(f"{status_line}\n{headers}\n\n")


def getType(extension):
    if extension == ".html":
        return "text/html"
    elif extension == ".txt":
        return "text/plain"
    elif extension == ".jpg":
        return "image/jpeg"
    elif extension == ".png":
        return "image/png"
    elif extension == ".gif":
        return "image/gif"
    elif extension == ".csv":
        return "text/csv"
    elif extension == ".docx":
        return "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    elif extension == ".doc":
        return "application/msword"
    elif extension == ".zip":
        return "application/zip"
    else:
        return "text/html"
    
def http_response(path):

    content_length = 0
    if os.path.exists(path):
        with open(path, 'rb') as file:
            file_content = file.read()
        file.close
        content_length = os.path.getsize(path)
        last_modified = os.path.getmtime(path)
        last_modified = time.ctime(last_modified)
        extension = os.path.splitext(path)[1].lower()
        type = getType(extension)
        http_message = (
        f"HTTP/1.1 200 OK\r\n" 
        f"Content-Length: {content_length}\r\n" 
        f"Content-Type: {type}\r\n"
        f"Date: {datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')} \r\n"
        f"Last-Modified: {last_modified}\r\n"
        f"Connection: close\r\n"
        f"\r\n"
        )
        http_message = http_message.encode() + file_content + b"\r\n"
        #sys.stdout.write(http_message)
       
    else:
        http_message = (
            f"HTTP/1.1 404 Not Found\r\n"
            f"Date: {datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')}\r\n"
            f"Connection: close\r\n"
            f"\r\n"
            f"404 Not Found: File not found\r\n"
        )
    return http_message, content_length



parser = ArgumentParser()
parser.add_argument("-p", type=int, help= "Enter port number")
parser.add_argument("-d", type=str, help= "absolute path")

args = parser.parse_args()

port_num = args.p
dir_path = args.d

port_num = 8000
dir_path = "/Users/tanujsood/Desktop"

if port_num == 8000:
    #sys.stdout.write(f"{port_num} {dir_path}\n")
    serverSocket = socket(AF_INET, SOCK_STREAM)
    serverSocket.bind(("127.0.0.1", port_num))
    serverSocket.listen(1)
    socket_info = serverSocket.getsockname()
    socket_ip = socket_info[0]
    socket_port = socket_info[1]
    sys.stdout.write(f"Welcome socket created: {socket_ip}, {socket_port}\n")
    print(" ")
    while True:
        connectionSocket, addr = serverSocket.accept()
        sys.stdout.write(f"Connection socket created: {addr[0]}, {addr[1]}\n")
        sentence = connectionSocket.recv(1024).decode()
        sentence_split = sentence.split()
        if sentence_split[0] != "GET":
            error_response = (
            f"HTTP/1.1 501 Not Implemented\r\n\r\n"
            f"Date: {datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')}\r\n"
            f"Connection: close\r\n"
            f"\r\n"
            f"501 Not Implemented: The server does not support this functionality r\n"
            )
            connectionSocket.close()
            sys.stdout.write(f"Connection to {addr[0]}, {addr[1]} is now closed.")
        elif sentence_split[2] != "HTTP/1.1":
            error_response = (
            f"HTTP/1.1 505 HTTP Version Not Supported\r\n"
            f"Date: {datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')}\r\n"
            f"Connection: close\r\n"
            f"\r\n"
            f"505 HTTP Version Not Supported: The server only supports HTTP/1.1\r\n"
            )
            connectionSocket.close()
            sys.stdout.write(f"Connection to {addr[0]}, {addr[1]} is now closed.")
        else:
            path = os.path.join(dir_path, sentence_split[1].lstrip("/"))
            response, length = http_response(dir_path)
            connectionSocket.send(response)
            connectionSocket.close()
            log_csv(socket_ip, socket_port, addr[0], addr[1], sentence_split[1], response.split(b"\r\n")[0].decode(),
                        length)
            log_text(response)
            sys.stdout.write(f"Connection to {addr[0]}, {addr[1]} is now closed.")
            
elif port_num in range(0,1024):
    sys.stdout.write(f"Well-known port number {port_num} entered - could cause a conflict.\n")
    sys.stdout.write(f"{port_num} {dir_path}\n")
elif port_num in range(1024, 49152):
    sys.stdout.write(f"Registered port number {port_num} entered - could cause a conflict.\n")
    sys.stdout.write(f"{port_num} {dir_path}\n")
else:
    sys.stderr.write("Terminating program, port number is not allowed.\n")
    sys.exit(1)


