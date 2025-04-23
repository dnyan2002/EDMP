import socket
import threading
import json
from threading import Thread
from database_communication import DatabaseCommunication

class GreetingServer(Thread):
    def __init__(self, port):
        super().__init__()
        self.status = False
        self.port = port
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            # Set a reasonable socket timeout
            self.server_socket.settimeout(1.0)  # 1 second timeout for accept()
            self.server_socket.bind(('', port))
            self.server_socket.listen(5)
            self.database_communication = DatabaseCommunication()
            self.status = True  # Keep the server running
            self.clients = {}   # Dictionary to track connected clients
            self.lock = threading.Lock()
            print(f"✅ Server initialized on port {port}")
        except Exception as e:
            print(f"❌ Server initialization error on port {port}: {e}")
    
    def handle_client(self, client_socket, addr):
        """Handles communication with a connected client for IOT data collection."""
        print(f"✅ Connection established with IOT device at {addr}")
        
        with self.lock:
            self.clients[addr] = client_socket

        # Configure socket for better IOT communication
        try:
            # Set a timeout for receiving data (IOT devices might send infrequently)
            client_socket.settimeout(60)  # 60 second timeout
        except Exception as e:
            print(f"⚠️ Error configuring socket for {addr}: {e}")

        # Update connection status
        self.database_communication.update_server_conn_error1(0)

        while self.status:
            try:
                raw_data = client_socket.recv(1024)
                if not raw_data:  # Check if connection was closed
                    print(f"⚠️ IOT device at {addr} disconnected - connection closed")
                    break
                    
                print(f"📩 Raw data received from IOT device at {addr}: {raw_data!r}")
                
                # Process the received data
                try:
                    # Try to decode as string first
                    client_message = raw_data.decode('utf-8', errors='replace').strip()
                    print(f"📩 Decoded message from IOT device at {addr}: {client_message}")
                    
                    # Try to parse as JSON if it looks like JSON data
                    if client_message.startswith('{') and client_message.endswith('}'):
                        try:
                            data_dict = json.loads(client_message)
                            print(f"📊 Parsed JSON data: {data_dict}")
                            
                            # Process the JSON data
                            plant_id = self.database_communication.get_plant_id(addr[0])
                            self.database_communication.insert_into_database(data_dict, addr[0], plant_id)
                            
                        except json.JSONDecodeError as je:
                            print(f"⚠️ Invalid JSON format from {addr}: {je}")
                            # Try to handle it as a regular message
                            plant_id = self.database_communication.get_plant_id(addr[0])
                            self.database_communication.insert_into_database(client_message, addr[0], plant_id)
                    else:
                        # Handle as regular message (not JSON)
                        if client_message and client_message != "keepalive":
                            plant_id = self.database_communication.get_plant_id(addr[0])
                            self.database_communication.insert_into_database(client_message, addr[0], plant_id)
                            
                except UnicodeDecodeError as e:
                    print(f"⚠️ Cannot decode data from {addr} as text: {e}")
                    # Handle binary data from IOT device if needed
                    continue

                # Skip empty messages but keep connection
                if not client_message:
                    print(f"⚠️ Empty message from {addr} but connection maintained")
                    continue

                # Skip keepalive messages
                if client_message == "keepalive":
                    print(f"🔄 Received keepalive from {addr}")
                    continue

                # Send acknowledgment back to the IOT device
                try:
                    response = "ACK"
                    client_socket.sendall(response.encode())
                except socket.error as e:
                    print(f"⚠️ Failed to send response to {addr}: {e}")
                    break

            except socket.timeout:
                # Just a timeout, the connection might still be good
                print(f"⏱️ Timeout waiting for data from {addr}, but connection maintained")
                # Send a keepalive message to check if connection is still alive
                try:
                    client_socket.sendall(b"keepalive")
                    print(f"✅ Keepalive sent to {addr}")
                except socket.error as e:
                    print(f"⚠️ Connection lost with {addr} during keepalive: {e}")
                    break
                continue
                
            except socket.error as e:
                print(f"⚠️ Connection lost with {addr}: {e}")
                break
            except Exception as e:
                print(f"⚠️ General error handling client {addr}: {e}")
                # Continue the loop to maintain connection despite errors
                continue

        print(f"🔴 Closing connection with {addr}")
        try:
            client_socket.close()
        except Exception as e:
            print(f"⚠️ Error closing socket for {addr}: {e}")
        
        with self.lock:
            if addr in self.clients:
                del self.clients[addr]
                
        # Update connection status
        self.database_communication.update_server_conn_error1(1)

    def run(self):
        """Main server loop to accept and handle IOT device connections."""
        print(f"🚀 IOT Server is running on port {self.port} and waiting for connections...")

        while self.status:
            try:
                try:
                    client_socket, addr = self.server_socket.accept()
                    print(f"⚡ New connection from {addr}")
                    client_thread = threading.Thread(target=self.handle_client, args=(client_socket, addr), daemon=True)
                    client_thread.name = f"IOT-Handler-{addr[0]}:{addr[1]}"
                    client_thread.start()
                except socket.timeout:
                    # No new connections, just continue the loop
                    continue
            except Exception as e:
                if self.status:  # Only print error if server is still supposed to be running
                    print(f"⚠️ Error accepting connection: {e}")
            
            # Short sleep to prevent tight loop
            import time
            time.sleep(0.1)