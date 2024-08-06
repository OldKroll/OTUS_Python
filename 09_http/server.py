import json
import os
import socket
import threading

HOST = "localhost"
PORT = 8081
DOCUMENT_ROOT = "./www"  # root folder for static files


class Response:
    def __init__(self) -> None:
        self.headers = {"Content-Type": "text/html; charset=utf-8"}
        self.code = "200 OK"
        self.body = ""

    def dump(self) -> bytes:
        headers = ""
        for k, v in self.headers.items():
            headers += f"{k}: {v}\r\n"
        resp = f"""\r\nHTTP/1.1 {self.code}\r\n{headers}\r\n{self.body}\r\n"""
        return resp.encode("utf-8")


def handle_request(client_socket: socket.socket, addr):
    response = Response()
    try:
        request = client_socket.recv(1024).decode("utf-8").split("\r\n")
        print(f"\nRecieved data from {addr}:")
        print(request)

        general_header = request[0].split(" ")
        method = general_header[0]
        path = general_header[1]

        if method in ["GET", "HEAD"] and path == "/index.html":
            with open(f"{DOCUMENT_ROOT}/index.html", "r", encoding="utf-8") as f:
                response.body = f.read()
        else:
            response.code = "404 Not Found"

    except Exception as e:
        print(e)
        response.code = "500 Internal Server Error"

    finally:
        client_socket.sendall(response.dump())
        client_socket.close()
        exit(0)


def start_server():
    s_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s_tcp.bind((HOST, PORT))
    s_tcp.listen(15)
    print(f"Server listen at http://{HOST}:{PORT}")
    while True:
        client_socket, addr = s_tcp.accept()
        client_handler = threading.Thread(
            target=handle_request, args=(client_socket, addr)
        )
        client_handler.start()


if __name__ == "__main__":
    try:
        start_server()
    except KeyboardInterrupt:
        print("Server stopped by Ctrl+C")
        exit(0)
