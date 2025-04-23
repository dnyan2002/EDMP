import socket
import threading
from threading import Thread
from database_communication import DatabaseCommunication

class GreetingServer7(Thread): #
    def __init__(self, port):
        super().__init__()
        self.status = False
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #<----
            self.server_socket.bind(('', port))
            self.server_socket.listen(5)
            self.database_communication = DatabaseCommunication()
            self.status = True  # Keep the server running
            self.clients = {}   # Dictionary to track connected clients
            self.lock = threading.Lock()
            
        except Exception as e:
            print(f"❌ Server initialization error: {e}")
    
    def handle_client(self, client_socket, addr):
        """Handles communication with a connected client without forcing reconnections."""
        print(f"✅ Connection established with 8th : {addr}") #
        
        with self.lock:
            self.clients[addr] = client_socket

        while self.status:
            try:
                raw_data = client_socket.recv(1024)
                if not raw_data:  # Check if connection was closed
                    print(f"⚠️ Client 8th : {addr} disconnected - connection closed") #
                    break
                    
                print(f"📩 Raw data received from 8th : {addr}: {raw_data!r}") #
                try:
                    client_message = raw_data.decode().strip()
                    print(f"📩 Decoded message from 8th :{addr}: {client_message}") #
                except UnicodeDecodeError as e:
                    print(f"⚠️ Cannot decode data from 8th : {addr}: {e}") #
                    print(f"⚠️ Attempting to process as binary data")
                    # Handle binary data if needed
                    continue

                if not client_message:
                    print(f"⚠️ Client 8th : {addr} sent empty message but connection maintained") #
                    continue  # Continue instead of breaking on empty message

                print(f"📩 Received from 8th :{addr}: {client_message}") #

                # Process and store data
                # for update connection if IOT is On

                self.database_communication.update_server_conn_error8(0) #
                plant_id = self.database_communication.get_plant_id(addr)

                self.database_communication.insert_into_database(client_message, addr, plant_id)

                try:
                    response = f"Server received: {client_message}"
                    client_socket.sendall(response.encode())
                except socket.error as e:
                    print(f"⚠️ Failed to send response to 8th : {addr}: {e}") #
                    break

            except socket.timeout:
                # Just a timeout, the connection might still be good
                print(f"⏱️ Timeout waiting for data from 8th :{addr}, but connection maintained.") #
                # Send a keepalive message to check if connection is still alive
                try:
                    client_socket.sendall(b"keepalive")
                    print(f"✅ Keepalive sent to 8th : {addr}") #
                except socket.error as e:
                    print(f"⚠️ Connection lost with 8th : {addr} during keepalive: {e}") #
                    break
                continue
                
            except socket.error as e:
                print(f"⚠️ Connection lost with 8th : {addr}: {e}") #
                break

        print(f"🔴 Closing connection with 8th : {addr}") #
        try:
            client_socket.close()
        except Exception as e:
            print(f"⚠️ Error closing socket for 8th : {addr}: {e}") #
        
        with self.lock:
            if addr in self.clients:
                del self.clients[addr]
                
        # Update connection status
        self.database_communication.update_server_conn_error8(1) #

    def run(self):
        """Main server loop to accept and handle clients in separate threads."""
        print("🚀 8th Server is running and waiting for connections...") #

        while self.status:
            try:
                try:
                    client_socket, addr = self.server_socket.accept()
                    client_thread = threading.Thread(target=self.handle_client, args=(client_socket, addr), daemon=True)
                    client_thread.name = f"Handler-{addr[0]}:{addr[1]}"
                    client_thread.start()
                except socket.timeout:
                    # No new connections, just continue the loop
                    continue
            except Exception as e:
                if self.status:  # Only print error if server is still supposed to be running
                    print(f"⚠️ Error accepting connection: {e}")

    # def stop_server(self):
    #     """Stops the server and closes all client connections."""
    #     self.status = False
        
    #     # Close all client connections
    #     with self.lock:
    #         for addr, client_socket in self.clients.items():
    #             try:
    #                 print(f"🔴 Closing connection with {addr} during server shutdown")
    #                 client_socket.close()
    #             except Exception as e:
    #                 print(f"⚠️ Error closing socket for {addr}: {e}")
    #         self.clients.clear()
        
    #     # Close the server socket
    #     try:
    #         self.server_socket.close()
    #     except Exception as e:
    #         print(f"⚠️ Error closing server socket: {e}")
            
    #     print("🔴 Server stopped.")