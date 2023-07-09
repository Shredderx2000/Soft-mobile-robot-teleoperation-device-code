import socket

def send_data(data, host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    byte_data = data.encode()
    

    try:
        sock.sendto(byte_data, (host, port))
        print("Success")
    except socket.error as e:
        print("error: ", str(e))
    finally:
        sock.close()

intLi = "6 7 8 9"
server_host = '192.168.15.117'
server_port = 25000

send_data(intLi, server_host, server_port)