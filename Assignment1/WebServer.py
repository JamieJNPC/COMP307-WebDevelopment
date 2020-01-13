import socket
import sys


def receive(client_connection):
    request_data = b''
    while True:
        request_data += client_connection.recv(4098)
        if b'\r\n\r\n' in request_data:
            break

    parts = request_data.split(b'\r\n\r\n', 1)
    header = parts[0]
    body = parts[1]

    if b'Content-Length' in header:
        headers = header.split(b'\r\n')
        for head in headers:
            if head.startswith(b'Content-Length'):
                blen = int(head.split(b' ')[1])
                break
    else:
        blen = 0

    while len(body) < blen:
        body += client_connection.recv(4098)
    """print(header.decode("utf-8", "replace"), flush=True)
    print("")
    print(body.decode("utf-8", "replace"), flush=True)"""

    return header.decode("utf-8", "replace"), body.decode("utf-8", "replace")


if len(sys.argv) != 4:
    quit("Incorrect parameters")

host, port, root_path = sys.argv[1], sys.argv[2], sys.argv[3]
listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
listen_socket.bind((host, int(port)))
listen_socket.listen(1)
print("Serving HTTP on port " + port)
while True:
    client_connection, client_address = listen_socket.accept()
    header, body = receive(client_connection)
    path = root_path + str(header).split(' ')[1]
    if "jpg" in path:
        http_response = """\
HTTP/1.1 200 OK
Content-Type: images/jpeg;


        """
        http_response = http_response.replace("\n", "\r\n")
        http_response = http_response.encode(encoding='UTF-8')
    elif "png" in path:
        http_response = """\
HTTP/1.1 200 OK
Content-Type: images/png;


                """
        http_response = http_response.replace("\n", "\r\n")
        http_response = http_response.encode(encoding='UTF-8')
    elif "html" in path:
        http_response = """\
HTTP/1.1 200 OK
Content-Type: text/html;


                """
        http_response = http_response.replace("\n", "\r\n")
        http_response = http_response.encode(encoding='UTF-8')

    try:
        with open(path, 'rb') as file:
            http_response += file.read()
    except:
        http_response = """\
HTTP/1.1 404 OK
Content-Type: text/html

404 File Not Found
        """
        http_response = http_response.replace("\n", "\r\n")
        http_response = http_response.encode(encoding='UTF-8')
    if "Firefox" in header:
        http_response = """\
HTTP/1.1 403 OK
Content-Type: text/html

Firefox poses a security risk. Please use another browser to access this server
                """
        http_response = http_response.replace("\n", "\r\n")
        http_response = http_response.encode(encoding='UTF-8')
    client_connection.sendall(http_response)
    client_connection.close()
