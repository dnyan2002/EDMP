import socket
import threading
import time
import os
import sys
from datetime import datetime
from database_communication import DatabaseCommunication
from greeting_server import GreetingServer
from greeting_server1 import GreetingServer1

class MainSocketClass:
    folder_path = "D:\\Softwares\\logs"
    output_file = os.path.join(folder_path, "PLCLog.txt")
    formatter = "%Y-%m-%d %H:%M:%S"
    
    # Initialize class variables for socket management
    db_com = None
    status = 0
    previous_status = 0
    
    # Socket connection variables for device 1
    server_name1 = "127.0.0.1"
    port1 = 9090
    client_socket1 = None
    connection_active1 = False
    initial_command_sent1 = False
    last_keepalive1 = 0
    last_reconnect_attempt1 = 0
    
    # Socket connection variables for device 2
    server_name2 = "127.0.0.1"
    port2 = 9090
    client_socket2 = None
    connection_active2 = False
    initial_command_sent2 = False
    last_keepalive2 = 0
    last_reconnect_attempt2 = 0
    
    # Timing settings
    reconnect_interval = 30  # Seconds to wait between reconnection attempts
    keepalive_interval = 60  # Seconds to wait between keepalive messages

    @staticmethod
    def write_file(path, input_text):
        print(f"Writing to file: {path}")
        append = True
        try:
            if os.path.exists(path):
                size = os.path.getsize(path)
                if size > 500000:
                    append = False
        except Exception as e1:
            print(f"File check error: {e1}")
            current_time = datetime.now().strftime(MainSocketClass.formatter)
            MainSocketClass.write_file(MainSocketClass.output_file, current_time)
            MainSocketClass.write_file(MainSocketClass.output_file, str(e1) + "\n\n")
        
        try:
            mode = 'a' if append else 'w'
            with open(path, mode) as file:
                file.write(input_text)
        except Exception as e:
            print(f"Exception occurred while writing: {e}")

    @classmethod
    def send_keepalive(cls, socket_num):
        """Send keepalive packet to maintain connection"""
        db_conn = DatabaseCommunication()
        current_time = time.time()
        
        try:
            if socket_num == 1:
                if not cls.connection_active1 or not cls.client_socket1:
                    return False
                    
                if current_time - cls.last_keepalive1 < cls.keepalive_interval:
                    return True  # Not time for keepalive yet
                    
                cls.last_keepalive1 = current_time
                
                try:
                    # Send simple keepalive message
                    cls.client_socket1.sendall(b"keepalive")
                    print(f"✅ Keepalive sent to server 1")
                    return True
                except socket.error as e:
                    print(f"❌ Keepalive failed to server 1: {e}")
                    cls.connection_active1 = False
                    db_conn.update_server_conn_error1(1)
                    return False
                
            elif socket_num == 2:
                if not cls.connection_active2 or not cls.client_socket2:
                    return False
                    
                if current_time - cls.last_keepalive2 < cls.keepalive_interval:
                    return True  # Not time for keepalive yet
                    
                cls.last_keepalive2 = current_time
                
                try:
                    # Send simple keepalive message
                    cls.client_socket2.sendall(b"keepalive")
                    print(f"✅ Keepalive sent to server 2")
                    return True
                except socket.error as e:
                    print(f"❌ Keepalive failed to server 2: {e}")
                    cls.connection_active2 = False
                    db_conn.update_server_conn_error2(1)
                    return False
        except Exception as e:
            print(f"❌ General error in send_keepalive: {e}")
            return False
        finally:
            db_conn.close()
                
        return False

    @classmethod
    def establish_connection1(cls):
        """Establish a persistent connection to server 1 if not already connected"""
        db_conn = DatabaseCommunication()
        if cls.client_socket1 and cls.connection_active1:
            return True
            
        current_time = time.time()
        if current_time - cls.last_reconnect_attempt1 < cls.reconnect_interval:
            return False  # Don't attempt reconnection too frequently
            
        cls.last_reconnect_attempt1 = current_time
        
        try:
            print(f"🔹 Establishing connection to {cls.server_name1}:{cls.port1}")
            if cls.client_socket1:
                try:
                    cls.client_socket1.close()
                except:
                    pass
                    
            cls.client_socket1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            cls.client_socket1.settimeout(10)  # 10 second timeout for connection
            cls.client_socket1.connect((cls.server_name1, cls.port1))
            # Configure socket keep-alive
            cls.client_socket1.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            # Set TCP keepalive parameters if platform supports them
            if hasattr(socket, "TCP_KEEPIDLE") and hasattr(socket, "TCP_KEEPINTVL") and hasattr(socket, "TCP_KEEPCNT"):
                cls.client_socket1.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 60)  # Start sending after 60s
                cls.client_socket1.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 10)  # Send every 10s
                cls.client_socket1.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 6)    # Up to 6 times
            
            cls.client_socket1.settimeout(None)  # Remove timeout after connection
            
            cls.connection_active1 = True
            cls.initial_command_sent1 = False  # Reset initial command flag
            cls.last_keepalive1 = time.time()
            db_conn.update_server_conn_error1(0)
            print(f"✅ Connected to {cls.server_name1}:{cls.port1}")
            return True
            
        except socket.error as e:
            print(f"❌ Socket error on connection to server 1: {e}")
            cls.connection_active1 = False
            db_conn.update_server_conn_error1(1)
            return False
        except Exception as e:
            print(f"❌ General error connecting to server 1: {e}")
            cls.connection_active1 = False
            db_conn.update_server_conn_error1(1)
            return False
        finally:
            db_conn.close()

    @classmethod
    def establish_connection2(cls):
        """Establish a persistent connection to server 2 if not already connected"""
        db_conn = DatabaseCommunication()
        if cls.connection_active2:
            return True
            
        current_time = time.time()
        if current_time - cls.last_reconnect_attempt2 < cls.reconnect_interval:
            return False  # Don't attempt reconnection too frequently
            
        cls.last_reconnect_attempt2 = current_time
        
        try:
            print(f"🔹 Establishing connection to {cls.server_name2}:{cls.port2}")
            if cls.client_socket2:
                try:
                    cls.client_socket2.close()
                except:
                    pass
                    
            cls.client_socket2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            cls.client_socket2.settimeout(10)  # 10 second timeout for connection
            cls.client_socket2.connect((cls.server_name2, cls.port2))
            # Configure socket keep-alive
            cls.client_socket2.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            # Set TCP keepalive parameters if platform supports them
            if hasattr(socket, "TCP_KEEPIDLE") and hasattr(socket, "TCP_KEEPINTVL") and hasattr(socket, "TCP_KEEPCNT"):
                cls.client_socket2.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 60)  # Start sending after 60s
                cls.client_socket2.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 10)  # Send every 10s
                cls.client_socket2.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 6)    # Up to 6 times
            
            cls.client_socket2.settimeout(None)  # Remove timeout after connection
            
            cls.connection_active2 = True
            cls.initial_command_sent2 = False  # Reset initial command flag
            cls.last_keepalive2 = time.time()
            db_conn.update_server_conn_error2(0)
            print(f"✅ Connected to {cls.server_name2}:{cls.port2}")
            return True
            
        except socket.error as e:
            print(f"❌ Socket error on connection to server 2: {e}")
            cls.connection_active2 = False
            db_conn.update_server_conn_error2(1)
            return False
        except Exception as e:
            print(f"❌ General error connecting to server 2: {e}")
            cls.connection_active2 = False
            db_conn.update_server_conn_error2(1)
            return False
        finally:
            db_conn.close()

    @classmethod
    def send_query(cls):
        print("Executing send_query method")
        try:
            # Add check if db_com is initialized
            if cls.db_com is None:
                print("❌ Database connection not initialized")
                return

            # Get server addresses and ports from database
            cls.server_name1 = cls.db_com.get_plc_ip1()
            cls.server_name2 = cls.db_com.get_plc_ip2()

            cls.port1 = cls.db_com.get_com_port1()
            cls.port2 = cls.db_com.get_com_port2()

            print(f"Server 1 IP: {cls.server_name1}, Port: {cls.port1}")
            print(f"Server 2 IP: {cls.server_name2}, Port: {cls.port2}")

        except Exception as e:
            print(f"❌ Error in send_query: {e}")
            cls.write_file(cls.output_file, f"Error in send_query: {str(e)}\n\n")

    @classmethod
    def connection_monitor(cls):
        """Periodically check and attempt to reconnect if connections are lost"""
        while True:
            try:
                # Check and attempt to reconnect if needed
                if not cls.connection_active1:
                    cls.establish_connection1()
                else:
                    # Send keepalive to maintain connection
                    cls.send_keepalive(1)
                    
                if not cls.connection_active2:
                    cls.establish_connection2()
                else:
                    # Send keepalive to maintain connection
                    cls.send_keepalive(2)
                    
            except Exception as e:
                print(f"❌ Error in connection monitor: {e}")
                cls.write_file(cls.output_file, f"Error in connection monitor: {str(e)}\n\n")
                
            time.sleep(10)

    @classmethod
    def service_main(cls):
        print("🔹 Starting service_main...")

        # Check and create logs directory if it doesn't exist
        if not os.path.exists(cls.folder_path):
            try:
                os.makedirs(cls.folder_path)
                print(f"✅ Created logs directory: {cls.folder_path}")
            except Exception as e:
                print(f"❌ Error creating logs directory: {e}")
                cls.write_file(cls.output_file, f"Error creating logs directory: {str(e)}\n\n")

        # Initialize DatabaseCommunication
        try:
            cls.db_com = DatabaseCommunication()
            if cls.db_com is None:
                raise ValueError("DatabaseCommunication failed to initialize. Exiting service_main.")
            print("✅ DatabaseCommunication initialized successfully")
        except Exception as e:
            print(f"❌ Error initializing DatabaseCommunication: {e}")
            cls.write_file(cls.output_file, f"Error initializing DatabaseCommunication: {str(e)}\n\n")
            return  # Exit if database initialization fails

        try:
            # Get initial PLC IP and port configurations from database
            cls.server_name1 = cls.db_com.get_plc_ip1()
            cls.server_name2 = cls.db_com.get_plc_ip2()
            cls.port1 = cls.db_com.get_com_port1()
            cls.port2 = cls.db_com.get_com_port2()
            
            print(f"Initial config - Server 1: {cls.server_name1}:{cls.port1}")
            print(f"Initial config - Server 2: {cls.server_name2}:{cls.port2}")

            # Initialize GreetingServer instances
            print(f"🔹 Initializing GreetingServers on ports {cls.port1} and {cls.port2}...")

            cls.g = GreetingServer(cls.port1)
            cls.g1 = GreetingServer1(cls.port2)

            # Start both servers in separate threads
            print("🔹 Starting server threads")
            t1 = threading.Thread(target=cls.g.run, daemon=True)
            t2 = threading.Thread(target=cls.g1.run, daemon=True)
            
            t1.name = "GreetingServer1"
            t2.name = "GreetingServer2"
            
            # Start connection monitor thread
            print("🔹 Starting connection monitor")
            t_monitor = threading.Thread(target=cls.connection_monitor, daemon=True)
            t_monitor.name = "Connection-Monitor"
            t_monitor.start()

            t1.start()
            t2.start()

            print("✅ Servers started successfully")

            # Main loop with reduced frequency
            while True:
                try:
                    time.sleep(5)  # Reasonable polling interval
                    cls.send_query()
                except Exception as e:
                    print(f"❌ Error in main loop: {e}")
                    cls.write_file(cls.output_file, f"Error in main loop: {str(e)}\n\n")

        except Exception as e:
            print(f"❌ Error in service_main: {e}")
            cls.write_file(cls.output_file, f"Error in service_main: {str(e)}\n\n")

def main():
    print("Starting main function")
    try:
        MainSocketClass.service_main()
    except Exception as e:
        print(f"Main function error: {e}")
        MainSocketClass.write_file(MainSocketClass.output_file, str(e) + "\n\n")

if __name__ == "__main__":
    main()