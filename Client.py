from socket import *

HOST = "172.21.12.32" # Host IP Address
PORT = 12345 # Host port number

clientSocket = socket(AF_INET, SOCK_DGRAM)  # Create UDP socket
clientSocket.sendto("Wagwan".encode(), (HOST, PORT))  # Message to register with the server
print("Client is online and waiting for alerts...")

try:
    while True:  
        Alert, serverAddress = clientSocket.recvfrom(2048) # Server message 
        print(Alert.decode()) # Printing server message

except KeyboardInterrupt:
    print("\nClient shutting down...")
finally:
    clientSocket.close()
