import socket
from datetime import datetime
from gpiozero import Button, PWMOutputDevice
import time


IP = "0.0.0.0"  #for all interfaces
PORT = 12345
BUTTON_PIN = 23
BUZZER_PIN = 18

# Button and Buzzer Setup with gpiozero
button = Button(BUTTON_PIN, pull_up=True, bounce_time=0.3)
buzzer = PWMOutputDevice(BUZZER_PIN, initial_value=0, frequency=1000)


#Creating the server using a udp soccket
def Create_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((IP, PORT))
    print(f"Server ready and listening on {IP}:{PORT}")
    return server_socket

#Function to sound the buzzer, write to the log and notify all clients on the server
def Emergency(clients, server_socket, buzzer):

    # Create an alert message with the current time
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    alert_message = f"Emergency detected at [{current_time}]\n"
    
    # Log the alert to a file
    with open("Alerts.txt", "a") as log:
        log.write(alert_message)
    print(alert_message)
    
    # Sending an alert to all the clients on the server
    for client in clients:
        server_socket.sendto(alert_message.encode(), client)
    
    # Switching on the buzzer and making it sound like a siren
    try:
        # Siren sound
        for _ in range(3):
            
            for freq in range(500, 2000, 50):
                buzzer.frequency = freq
                buzzer.value = 0.5  
                time.sleep(0.01)
            
            for freq in range(2000, 500, -50):
                buzzer.frequency = freq
                buzzer.value = 0.5
                time.sleep(0.01)
        
    finally:
        buzzer.off()


def main():
    server_socket = Create_server()
    clients = set()

    # Check if button is pressed and calls the function emergency
    def on_button_press():
        Emergency(clients, server_socket, buzzer)
    button.when_pressed = on_button_press
    
    
    try:
        while True:
            # Stops recvfrom blocking the main loop
            server_socket.settimeout(0.1)
            
            try:
                # Allowing for the recieving of messages and then sending a response to the message
                message, client_address = server_socket.recvfrom(2048)
                print(f"Received from {client_address}: {message.decode()}")
                
                server_socket.sendto("You are connected. Wagwan!!!".encode(), client_address)
                
                # Add new client to the set
                if client_address not in clients:
                    clients.add(client_address)
                    print(f"New client connected: {client_address}")
            except socket.timeout:
                pass
    finally:
        buzzer.close()
        button.close()
        server_socket.close()

if __name__ == "__main__":
    main()
