import socket
import threading
import time
import os
import sys
from datetime import datetime
from database_communication import DatabaseCommunication
from greeting_server import GreetingServer

class MainSocketClass:
    counter = 0
    status = 0  # status of production started or stop
    status1 = 0  # status of production for testing filters
    previous_status = 0
    db = DatabaseCommunication()
    port1 = db.get_com_port1()  # port for greeting server 1
    print("asdfghjk",type(port1))
    
    result_value = 0
    
    folder_path = "D:\\Softwares\\logs"
    output_file = os.path.join(folder_path, "PLCLog.txt")
    formatter = "%Y-%m-%d %H:%M:%S"
    

    # Get Iot Ip address from database
    
    server_name1 = db.get_plc_ip1()  # port for greeting server 9
    
    # Persistent connection sockets
    client_socket1 = None
    
    
    
    # Connection status flags
    connection_active1 = False
    
    
    # Reconnection timers
    last_reconnect_attempt1 = 0

    reconnect_interval = 60  # Seconds between reconnection attempts
    keepalive_interval = 30  # Seconds between keepalive messages

    last_keepalive1 = 0
    
    
    # Flags to track if initial command has been sent
    initial_command_sent1 = False

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
        db_conn = DatabaseCommunication()
        """Send keepalive packet to maintain connection"""
        current_time = time.time()
        
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
            
            finally:
                db_conn.close()
        
        #-----------------------------------------------------------------------------
                
        return False
    
    #############################################################################################
    
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
        
        finally:
            db_conn.close()

    

    #############################################################################################
    
    # @classmethod
    # def send_query(cls):
    #     print("Executing send_query method")

    #     cls.status = cls.db_com.check_status()
    #     print(f"Production status fetched: {cls.status}")

    #     cls.server_name1 = cls.db_com.get_plc_ip1()
    #     cls.server_name2 = cls.db_com.get_plc_ip2()

    #     cls.port1 = cls.db_com.get_com_port1()
    #     cls.port2 = cls.db_com.get_com_port2()

    #     print(f"Server 1 IP: {cls.server_name1}, Port: {cls.port1}")
    #     print(f"Server 2 IP: {cls.server_name2}, Port: {cls.port2}")

    #     print("Production started")
    #     cls.previous_status = cls.status
    #     if cls.status == 1:
    #         cls.db_com.truncate_table()
    #         print("Truncated table successfully")
    #     return

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

                #-----------------------------------------------------
            
            except Exception as e:
                print(f"❌ Error in connection monitor: {e}")
                
            time.sleep(10)  # Check connection status more frequently

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

        # Initialize DatabaseCommunication
        try:
            cls.db_com = DatabaseCommunication()
            if cls.db_com is None:
                raise ValueError("DatabaseCommunication failed to initialize. Exiting service_main.")
            print("✅ DatabaseCommunication initialized successfully")
        except Exception as e:
            print(f"❌ Error initializing DatabaseCommunication: {e}")
            return  # Exit if database initialization fails

        try:
            # Initialize GreetingServer instances
            print(f"🔹 Initializing GreetingServers on ports {cls.port1}...")

            cls.g = GreetingServer(cls.port1)   # IOT_Device - 1
            
            # Start both servers in separate threads
            print("🔹 Starting server threads")
            t1 = threading.Thread(target=cls.g.start, daemon=True)
            
            t1.name = "GreetingServer-1"
            
            
            # Start connection monitor thread
            print("🔹 Starting connection monitor")
            t_monitor = threading.Thread(target=cls.connection_monitor, daemon=True)
            t_monitor.name = "Connection-Monitor"
            t_monitor.start()

            t1.start()

            print("✅ Servers started successfully")

            # Main loop with reduced frequency
            while True:
                time.sleep(5)  # Reasonable polling interval
                #cls.send_query()

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