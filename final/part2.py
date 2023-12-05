from argparse import ArgumentParser
import sys
import os
import time
from datetime import datetime
from socket import *
import csv
import errno

def log_csv(server_ip, server_port, client_ip, client_port, url, status_line, content_length):
    with open('tasoodSocketOutput.csv', mode='a') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(["Client request served", "4-Tuple:", server_ip, server_port, client_ip, client_port,
                             "Requested URL", "."+url, status_line, "Bytes sent:", content_length])

def log_text(headers):
    with open('tasoodHTTPResponses.txt', 'a') as file:
        file.write("{}\n".format(headers))


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
        file.close()
        content_length = os.path.getsize(path)
        last_modified = os.path.getmtime(path)
        last_modified = time.ctime(last_modified)
        extension = os.path.splitext(path)[1].lower()
        type = getType(extension)
        headers = (
        "HTTP/1.1 200 OK\r\n"
        "Content-Length: {}\r\n" 
        "Content-Type: {}\r\n"
        "Date: {} \r\n"
        "Last-Modified: {}\r\n"
        "Connection: close\r\n"
        "\r\n"
        ).format(content_length,type,datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT'),last_modified)
        http_message = headers.encode() + file_content + b"\r\n"
        #sys.stdout.write(http_message)
       
    else:
        headers = (
            "HTTP/1.1 404 Not Found\r\n"
            "Date: {}\r\n"
            "\r\n"
        ).format(datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT'))
        http_message = headers.encode()
    return http_message, content_length, headers



parser = ArgumentParser()
parser.add_argument("-p", type=int, help= "Enter port number")
parser.add_argument("-d", type=str, help= "absolute path")

args = parser.parse_args()

port_num = args.p
dir_path = args.d

#port_num = 8000
#dir_path = "/Users/tanujsood/Desktop"

if port_num == 80:
    #sys.stdout.write(f"{port_num} {dir_path}\n")
    bind_success = False
    while not bind_success:
        try:
            serverSocket = socket(AF_INET, SOCK_STREAM)
            serverSocket.bind(("127.0.0.1", port_num))
            bind_success = True
        except OSError as e:
            if e.errno == errno.EADDRINUSE:
                print(f"Port {port_num} is already in use. Retrying in 5 seconds...")
                time.sleep(5)
            else:
                print(f"Fatal error: {e}")
                sys.exit(1)
    serverSocket.listen(1)
    socket_info = serverSocket.getsockname()
    socket_ip = socket_info[0]
    socket_port = socket_info[1]
    sys.stdout.write("Welcome socket created: {}, {}\n".format(socket_ip,socket_port))
    while True:
        #sys.stdout.write("here1: {}, {}\n".format(socket_ip,socket_port))
        connectionSocket, addr = serverSocket.accept()
        sys.stdout.write("Connection socket created: {}, {}\n".format(addr[0],addr[1]))
        sentence = connectionSocket.recv(1024).decode()
        sentence_split = sentence.split()
        if len(sentence_split)<2 or sentence_split[0] != "GET":
            #sys.stdout.write("here2: {}, {}\n".format(socket_ip,socket_port))
            error_response = (
            "HTTP/1.1 501 Not Implemented\r\n"
            "Date: {}\r\n"
            "\r\n"
            ).format(datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT'))
            error_response = error_response.encode()
            connectionSocket.send(error_response)
            connectionSocket.close()
            sys.stdout.write("Connection to {}, {} is now closed.\n".format(addr[0],addr[1]))
        elif len(sentence_split)<3 or sentence_split[2] != "HTTP/1.1":
            #sys.stdout.write("here3: {}, {}\n".format(socket_ip,socket_port))
            error_response = (
            "HTTP/1.1 505 HTTP Version Not Supported\r\n"
            "Date: {}\r\n"
            "\r\n"
            ).format(datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT'))
            error_response = error_response.encode()
            connectionSocket.send(error_response)
            connectionSocket.close()
            sys.stdout.write("Connection to {}, {} is now closed.\n".format(addr[0]),addr[1])
        else:
            #sys.stdout.write("here4: {}, {}\n".format(socket_ip,socket_port))
            path = os.path.join(dir_path, sentence_split[1].lstrip("/"))
            response, length, heads = http_response(path)
            connectionSocket.send(response)
            connectionSocket.close()
            sys.stdout.write("Connection to {}, {} is now closed.\n".format(addr[0],addr[1]))
            log_csv(socket_ip, socket_port, addr[0], addr[1], sentence_split[1], heads.split("\r\n")[0],length)
            log_text(heads)
            
elif port_num in range(0,1024):
    sys.stdout.write("Well-known port number {} entered - could cause a conflict.\n".format(port_num))
    sys.stdout.write("{} {}\n".format(port_num,dir_path))
elif port_num in range(1024, 49152):
    sys.stdout.write("Registered port number {} entered - could cause a conflict.\n".format(port_num))
    sys.stdout.write("{} {}\n".format(port_num,dir_path))
else:
    sys.stderr.write("Terminating program, port number is not allowed.\n")
    sys.exit(1)
