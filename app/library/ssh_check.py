import socket

def check_ssh_connexion (server, port) :
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)                       
    result = sock.connect_ex((server, port))
    if result == 0:
        return 1
    else:
        return 0