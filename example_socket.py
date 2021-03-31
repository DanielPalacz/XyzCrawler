import socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
s.connect(("example.com", 80))
s.send(b"GET / HTTP/1.1\nHost: example.com\n\r\r")
s.recv(1024)
s.fileno()
