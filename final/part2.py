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
        file.write("{}\n{}\n".format(status_line,headers))


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
        "HTTP/1.1 200 OK\r\n"
        "Content-Length: {}\r\n" 
        "Content-Type: {}\r\n"
        "Date: {} \r\n"
        "Last-Modified: {}\r\n"
        "Connection: close\r\n"
        "\r\n"
        ).format(content_length,type,datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT'),last_modified)
        http_message = http_message.encode() + file_content + b"\r\n"
        #sys.stdout.write(http_message)
       
    else:
        http_message = (
            "HTTP/1.1 404 Not Found\r\n"
            "Date: {}\r\n"
            "Connection: close\r\n"
            "\r\n"
            "404 Not Found: File not found\r\n"
        ).format(datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT'))
    return http_message.encode(), content_length



parser = ArgumentParser()
parser.add_argument("-p", type=int, help= "Enter port number")
parser.add_argument("-d", type=str, help= "absolute path")

args = parser.parse_args()

port_num = args.p
dir_path = args.d

port_num = 8000
#dir_path = "/Users/tanujsood/Desktop"

if port_num == 8000:
    #sys.stdout.write(f"{port_num} {dir_path}\n")
    serverSocket = socket(AF_INET, SOCK_STREAM)
    serverSocket.bind(("127.0.0.1", port_num))
    serverSocket.listen(1)
    socket_info = serverSocket.getsockname()
    socket_ip = socket_info[0]
    socket_port = socket_info[1]
    sys.stdout.write("Welcome socket created: {}, {}\n".format(socket_ip,socket_port))
    while True:
        connectionSocket, addr = serverSocket.accept()
        sys.stdout.write("Connection socket created: {}, {}\n".format(addr[0],addr[1]))
        sentence = connectionSocket.recv(1024).decode()
        sentence_split = sentence.split()
        if sentence_split[0] != "GET":
            error_response = (
            "HTTP/1.1 501 Not Implemented\r\n\r\n"
            "Date: {}\r\n"
            "Connection: close\r\n"
            "\r\n"
            "501 Not Implemented: The server does not support this functionality r\n"
            ).format(datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT'))
            connectionSocket.close()
            sys.stdout.write("Connection to {}, {} is now closed.\n".format(addr[0],addr[1]))
        elif sentence_split[2] != "HTTP/1.1":
            error_response = (
            "HTTP/1.1 505 HTTP Version Not Supported\r\n"
            "Date: {}\r\n"
            "Connection: close\r\n"
            "\r\n"
            "505 HTTP Version Not Supported: The server only supports HTTP/1.1\r\n"
            ).format(datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT'))
            connectionSocket.close()
            sys.stdout.write("Connection to {}, {} is now closed.\n".format(addr[0]),addr[1])
        else:
            path = os.path.join(dir_path, sentence_split[1].lstrip("/"))
            response, length = http_response(path)
            connectionSocket.send(response)
            connectionSocket.close()
            sys.stdout.write("Connection to {}, {} is now closed.\n".format(addr[0],addr[1]))
            log_csv(socket_ip, socket_port, addr[0], addr[1], sentence_split[1], response.split(b"\r\n")[0].decode(),
                        length)
            log_text(response)
            
elif port_num in range(0,1024):
    sys.stdout.write("Well-known port number {} entered - could cause a conflict.\n".format(port_num))
    sys.stdout.write("{} {}\n".format(port_num,dir_path))
elif port_num in range(1024, 49152):
    sys.stdout.write("Registered port number {} entered - could cause a conflict.\n".format(port_num))
    sys.stdout.write("{} {}\n".format(port_num,dir_path))
else:
    sys.stderr.write("Terminating program, port number is not allowed.\n")
    sys.exit(1)
