import socket
from datetime import datetime
from gpiozero import Button, PWMOutputDevice
import time

# Configuration Constants
SERVER_IP = "0.0.0.0"  # Listen on all interfaces
SERVER_PORT = 12345
BUTTON_PIN = 23
BUZZER_PIN = 18

# GPIO Setup with gpiozero
button = Button(BUTTON_PIN, pull_up=True, bounce_time=0.3)
buzzer = PWMOutputDevice(BUZZER_PIN, initial_value=0, frequency=1000)

def initialize_server():
    """Create and return a UDP server socket"""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((SERVER_IP, SERVER_PORT))
    print(f"Server ready and listening on {SERVER_IP}:{SERVER_PORT}")
    return server_socket

def handle_emergency(clients, server_socket):
    """Handle emergency button press event with passive buzzer"""
    # Create alert message
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    alert_message = f"Emergency detected at [{current_time}]\n"
    
    # Log alert
    with open("Alerts.txt", "a") as log_file:
        log_file.write(alert_message)
    print(alert_message)
    
    # Send alert to all clients
    for client in clients:
        server_socket.sendto(alert_message.encode(), client)
    
    # Sound the passive buzzer with different tones
    try:
        # Siren-like effect
        for _ in range(3):
            # Rising tone
            for freq in range(500, 2000, 50):
                buzzer.frequency = freq
                buzzer.value = 0.5  # 50% duty cycle
                time.sleep(0.01)
            
            # Falling tone
            for freq in range(2000, 500, -50):
                buzzer.frequency = freq
                buzzer.value = 0.5
                time.sleep(0.01)
            
        # Final alert tone
        buzzer.frequency = 1000
        buzzer.value = 0.5
        time.sleep(0.5)
        
    finally:
        buzzer.off()

def main():
    server_socket = initialize_server()
    clients = set()
    
    def on_button_press():
        """Callback for button press event"""
        handle_emergency(clients, server_socket)
    
    # Set up button press callback
    button.when_pressed = on_button_press
    
    try:
        while True:
            # Check for new client messages with timeout
            server_socket.settimeout(0.1)
            
            try:
                message, client_address = server_socket.recvfrom(2048)
                print(f"Received from {client_address}: {message.decode()}")
                
                # Acknowledge connection
                server_socket.sendto("You are connected".encode(), client_address)
                
                # Add new client to set
                if client_address not in clients:
                    clients.add(client_address)
                    print(f"New client connected: {client_address}")
            except socket.timeout:
                pass
                
    except KeyboardInterrupt:
        print("\nServer shutting down...")
    finally:
        buzzer.close()
        button.close()
        server_socket.close()
        print("Server closed and GPIO cleaned up")

if __name__ == "__main__":
    main()
