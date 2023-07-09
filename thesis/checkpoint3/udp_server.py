import socket
import time

buffsize=1024
msgFserver="5.5 2.3 56.2"
serverPort=3333
serverIP='192.168.4.6'
bytestosend=msgFserver.encode('utf-8')
pisocket=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
pisocket.bind((serverIP, serverPort))

print('Server is up and listening...')

msg, address = pisocket.recvfrom(buffsize)
msg=msg.decode('utf-8') 
print(msg)
print('Client address', address[0])
pisocket.sendto(bytestosend, address)

while True:
    
    num1 = str(input())
    num2 = str(input())
    num3 = str(input())
    msg = num1 + ' ' + num2 + ' ' + num3
    msge = msg.encode('utf-8')
    pisocket.sendto(msge, address)
    if msg == "q q q":
        pisocket.close()
        break
    