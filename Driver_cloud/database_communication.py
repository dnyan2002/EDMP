import mysql.connector
import time
import json
from datetime import datetime
from mysql.connector import Error, pooling

class DatabaseCommunication:
    formatter = "%Y-%m-%d %H:%M:%S"
    
    def __init__(self):
        print(f"[DEBUG] Initializing DatabaseCommunication at {datetime.now().strftime(self.formatter)}")
        self.con = None
        self.cursor = None
        try:
            self.connect_to_database()
            self.start_connection_monitor()
        except Exception as e:
            print(f"[ERROR] Database initialization failed: {e}")
    
    def connect_to_database(self):
        """Establish a connection to the database"""
        try:
            print("[DEBUG] Attempting to connect to MySQL database")
            self.con = mysql.connector.connect(
                host="localhost",
                database="edmp_irms",
                user="root",
                password="",
                autocommit=False,  # We'll handle transactions explicitly
                pool_name="edmp_pool",
                pool_size=5,
                pool_reset_session=True
            )
            print("[DEBUG] MySQL connection successful")
            return True
        except Exception as e:
            print(f"[ERROR] Database connection failed: {e}")
            self.con = None
            return False
    
    def ensure_connection(self):
        """Ensures the database connection is active before executing queries."""
        if self.con is None or not self.con.is_connected():
            print("[WARNING] Database connection is None or lost. Attempting reconnection...")
            return self.connect_to_database()
        return True
    
    def execute_query(self, query, params=None, fetch=False, commit=False):
        """Execute a query with proper connection verification and error handling"""
        result = None
        cursor = None
        
        if not self.ensure_connection():
            print("[ERROR] Failed to ensure database connection")
            return None
            
        try:
            cursor = self.con.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
                
            if fetch:
                result = cursor.fetchall() if fetch == 'all' else cursor.fetchone()
            
            if commit:
                self.con.commit()
                
            return result
        except Error as e:
            print(f"[ERROR] Query execution failed: {e}")
            if e.errno == 1062:  # Duplicate entry error
                print("[WARNING] Duplicate entry detected, skipping.")
            else:
                self.log_error_details(e)
            
            # Rollback in case of error
            try:
                if self.con and self.con.is_connected():
                    self.con.rollback()
            except:
                pass
                
            return None
        finally:
            if cursor:
                cursor.close()
    
    def log_error_details(self, e):
        print(f"[ERROR] Detailed error log: {type(e).__name__} - {str(e)}")
        # Additional error logging implementation if needed
    
    def close_connection(self, connection):
        try:
            if connection and connection.is_connected():
                connection.close()
                print("[DEBUG] Database connection closed successfully")
        except Error as e:
            print(f"[ERROR] Failed to close database connection: {e}")
    
    def close_statement(self, cursor):
        try:
            if cursor:
                cursor.close()
                print("[DEBUG] Database cursor closed successfully")
        except Error as e:
            print(f"[ERROR] Failed to close database cursor: {e}")
    
    def check_status(self):
        """Check the current production status from database"""
        try:
            result = self.execute_query("SELECT status FROM production_status WHERE id = 1", fetch=True)
            if result:
                return result[0]
            return 0  # Default status if no result
        except Exception as e:
            print(f"[ERROR] Failed to check production status: {e}")
            return 0  # Default status on error
    
    def truncate_table(self):
        """Truncate the local_data table when production starts"""
        try:
            self.execute_query("TRUNCATE TABLE local_data", commit=True)
            print("[DEBUG] Successfully truncated local_data table")
            return True
        except Exception as e:
            print(f"[ERROR] Failed to truncate local_data table: {e}")
            return False
    
    # COM port and IP address retrieval methods remain the same...
    
    def get_com_port1(self):  
        print("[DEBUG] Getting COM port 1")  
        com_port = 9090  # Default value  

        try:                                  
            result = self.execute_query("SELECT port_no FROM connection WHERE machine_name = 'Machine1'", fetch=True)  

            if result:  # Ensure result is not None or empty  
                com_port = int(result[0])  # Extract integer from tuple  

        except Exception as e:          
            print(f"[ERROR] Failed to fetch COM port 1: {e}")  

        return com_port  # Return as an integer

    def get_plc_ip1(self): # Get IP address from Database 
        print("[DEBUG] Getting PLC IP 1")
        com_ip = "192.168.1.19"  # Default value
        try:
                                
            result = self.execute_query("SELECT ip_address FROM connection WHERE machine_name = 'Machine1'", fetch=True)  

            if result:  # Ensure result is not None or empty  
                com_ip = str(result[0])  # Extract integer from tuple  
                print("IP address type :", type(com_ip))
                
        except Exception as e:
            print(f"[ERROR] Failed to fetch COM port IP-1: {e}")
        
        return com_ip
    
    def update_server_conn_error1(self, status):  # for update connection if IOT is On
        print(f"[DEBUG] Updating server connection error 1 status: {status}")
        try:  
            self.execute_query("UPDATE connection SET status = %s WHERE machine_name = 'Machine1'", (status,), commit=True)
            print(f"[DEBUG] Successfully updated connection status to {status}")
        except Exception as e:
            print(f"[ERROR] Failed to update connection status: {e}")

    def close_result_set(self, result_set):
        pass

    def get_com_port1(self):  
        print("[DEBUG] Getting COM port 1")  
        com_port = 5050  # Default value  

        try:                                  
            result = self.execute_query("SELECT port_no FROM connection WHERE machine_name = 'Machine1'", fetch=True)  

            if result:  # Ensure result is not None or empty  
                com_port = int(result[0])  # Extract integer from tuple  

        except Exception as e:          
            print(f"[ERROR] Failed to fetch COM port 1: {e}")  

        return com_port  # Return as an integer  

    def get_com_port2(self):  
        print("[DEBUG] Getting COM port 2")  
        com_port = 9090  # Default value  

        try:                                  
            result = self.execute_query("SELECT port_no FROM connection WHERE machine_name = 'Machine2'", fetch=True)  

            if result:  # Ensure result is not None or empty  
                com_port = int(result[0])  # Extract integer from tuple  

        except Exception as e:          
            print(f"[ERROR] Failed to fetch COM port 2: {e}")  

        return com_port  # Return as an integer  

    def get_com_port3(self):  
        print("[DEBUG] Getting COM port 3")  
        com_port = 9090  # Default value  

        try:                                  
            result = self.execute_query("SELECT port_no FROM connection WHERE machine_name = 'Machine3'", fetch=True)  

            if result:  # Ensure result is not None or empty  
                com_port = int(result[0])  # Extract integer from tuple  

        except Exception as e:          
            print(f"[ERROR] Failed to fetch COM port 3: {e}")  

        return com_port  # Return as an integer  

    def get_com_port4(self):  
        print("[DEBUG] Getting COM port 4")  
        com_port = 9090  # Default value  

        try:                                  
            result = self.execute_query("SELECT port_no FROM connection WHERE machine_name = 'Machine4'", fetch=True)  

            if result:  # Ensure result is not None or empty  
                com_port = int(result[0])  # Extract integer from tuple  

        except Exception as e:          
            print(f"[ERROR] Failed to fetch COM port 4: {e}")  

        return com_port  # Return as an integer  

    def get_com_port5(self):
        print("[DEBUG] Getting COM port 5")  
        com_port = 9090  # Default value  

        try:                                  
            result = self.execute_query("SELECT port_no FROM connection WHERE machine_name = 'Machine5'", fetch=True)  

            if result:  # Ensure result is not None or empty  
                com_port = int(result[0])  # Extract integer from tuple  

        except Exception as e:          
            print(f"[ERROR] Failed to fetch COM port 5: {e}")  

        return com_port  # Return as an integer  

    def get_com_port6(self):
        print("[DEBUG] Getting COM port 6")  
        com_port = 9090  # Default value  

        try:                                  
            result = self.execute_query("SELECT port_no FROM connection WHERE machine_name = 'Machine6'", fetch=True)  

            if result:  # Ensure result is not None or empty  
                com_port = int(result[0])  # Extract integer from tuple  

        except Exception as e:          
            print(f"[ERROR] Failed to fetch COM port 6: {e}")  

        return com_port
    
    def get_com_port7(self):
        print("[DEBUG] Getting COM port 7")  
        com_port = 9090  # Default value  

        try:                                  
            result = self.execute_query("SELECT port_no FROM connection WHERE machine_name = 'Machine7'", fetch=True)  

            if result:  # Ensure result is not None or empty  
                com_port = int(result[0])  # Extract integer from tuple  

        except Exception as e:          
            print(f"[ERROR] Failed to fetch COM port 7: {e}")  

        return com_port  # Return as an integer 

    def get_com_port8(self):
        print("[DEBUG] Getting COM port 8")  
        com_port = 9090  # Default value  

        try:                                  
            result = self.execute_query("SELECT port_no FROM connection WHERE machine_name = 'Machine8'", fetch=True)  

            if result:  # Ensure result is not None or empty  
                com_port = int(result[0])  # Extract integer from tuple  

        except Exception as e:          
            print(f"[ERROR] Failed to fetch COM port 8: {e}")  

        return com_port  # Return as an integer  

    def get_com_port9(self):
        print("[DEBUG] Getting COM port 9")  
        com_port = 9090  # Default value  

        try:                                  
            result = self.execute_query("SELECT port_no FROM connection WHERE machine_name = 'Machine9'", fetch=True)  

            if result:  # Ensure result is not None or empty  
                com_port = int(result[0])  # Extract integer from tuple  

        except Exception as e:          
            print(f"[ERROR] Failed to fetch COM port 9: {e}")  

        return com_port  # Return as an integer  

    def get_plc_ip1(self): # Get IP address from Database 
        print("[DEBUG] Getting PLC IP 1")
        com_ip = "192.168.1.20"  # Default value
        try:
                                
            result = self.execute_query("SELECT ip_address FROM connection WHERE machine_name = 'Machine1'", fetch=True)  

            if result:  # Ensure result is not None or empty  
                com_ip = str(result[0])  # Extract integer from tuple  
                print("IP address type :", type(com_ip))
                
        except Exception as e:
            print(f"[ERROR] Failed to fetch COM port IP-1: {e}")
        
        return com_ip

    def get_plc_ip2(self): # Get IP address from Database 
        print("[DEBUG] Getting PLC IP 2")
        com_ip = "192.168.1.31"  # Default value
        try:
                                
            result = self.execute_query("SELECT ip_address FROM connection WHERE machine_name = 'Machine2'", fetch=True)  

            if result:  # Ensure result is not None or empty  
                com_ip = str(result[0])  # Extract integer from tuple  
                print("IP address type :", type(com_ip))
                
        except Exception as e:
            print(f"[ERROR] Failed to fetch COM port IP-2: {e}")
        
        return com_ip

    def get_plc_ip3(self): # Get IP address from Database 
        print("[DEBUG] Getting PLC IP 3")
        com_ip = "192.168.1.19"  # Default value
        try:
                                
            result = self.execute_query("SELECT ip_address FROM connection WHERE machine_name = 'Machine3'", fetch=True)  

            if result:  # Ensure result is not None or empty  
                com_ip = str(result[0])  # Extract integer from tuple  
                print("IP address type :", type(com_ip))
                
        except Exception as e:
            print(f"[ERROR] Failed to fetch COM port IP-3: {e}")
        
        return com_ip

    def get_plc_ip4(self): # Get IP address from Database 
        print("[DEBUG] Getting PLC IP 4")
        com_ip = "192.168.1.19"  # Default value
        try:
                                
            result = self.execute_query("SELECT ip_address FROM connection WHERE machine_name = 'Machine4'", fetch=True)  

            if result:  # Ensure result is not None or empty  
                com_ip = str(result[0])  # Extract integer from tuple  
                print("IP address type :", type(com_ip))
                
        except Exception as e:
            print(f"[ERROR] Failed to fetch COM port IP-4: {e}")
        
        return com_ip

    def get_plc_ip5(self): # Get IP address from Database 
        print("[DEBUG] Getting PLC IP 5")
        com_ip = "192.168.1.19"  # Default value
        try:
                                
            result = self.execute_query("SELECT ip_address FROM connection WHERE machine_name = 'Machine5'", fetch=True)  

            if result:  # Ensure result is not None or empty  
                com_ip = str(result[0])  # Extract integer from tuple  
                print("IP address type :", type(com_ip))
                
        except Exception as e:
            print(f"[ERROR] Failed to fetch COM port IP-5: {e}")
        
        return com_ip

    def get_plc_ip6(self): # Get IP address from Database 
        print("[DEBUG] Getting PLC IP 6")
        com_ip = "192.168.1.19"  # Default value
        try:
                                
            result = self.execute_query("SELECT ip_address FROM connection WHERE machine_name = 'Machine6'", fetch=True)  

            if result:  # Ensure result is not None or empty  
                com_ip = str(result[0])  # Extract integer from tuple  
                print("IP address type :", type(com_ip))
                
        except Exception as e:
            print(f"[ERROR] Failed to fetch COM port IP-6: {e}")
        
        return com_ip

    def get_plc_ip7(self): # Get IP address from Database 
        print("[DEBUG] Getting PLC IP 7")
        com_ip = "192.168.1.19"  # Default value
        try:
                   
            result = self.execute_query("SELECT ip_address FROM connection WHERE machine_name = 'Machine7'", fetch=True)  

            if result:  # Ensure result is not None or empty  
                com_ip = str(result[0])  # Extract integer from tuple  
                print("IP address type :", type(com_ip))
                
        except Exception as e:
            print(f"[ERROR] Failed to fetch COM port IP-7: {e}")
        
        return com_ip

    def get_plc_ip8(self): # Get IP address from Database 
        print("[DEBUG] Getting PLC IP 8")
        com_ip = "192.168.1.19"  # Default value
        try:                
            result = self.execute_query("SELECT ip_address FROM connection WHERE machine_name = 'Machine8'", fetch=True)  

            if result:  # Ensure result is not None or empty  
                com_ip = str(result[0])  # Extract integer from tuple  
                print("IP address type :", type(com_ip))
                
        except Exception as e:
            print(f"[ERROR] Failed to fetch COM port IP-8: {e}")
        
        return com_ip

    def get_plc_ip9(self): # Get IP address from Database 
        print("[DEBUG] Getting PLC IP 9")
        com_ip = "192.168.1.19"  # Default value
        try:
                                
            result = self.execute_query("SELECT ip_address FROM connection WHERE machine_name = 'Machine9'", fetch=True)  

            if result:  # Ensure result is not None or empty  
                com_ip = str(result[0])  # Extract integer from tuple  
                print("IP address type :", type(com_ip))
                
        except Exception as e:
            print(f"[ERROR] Failed to fetch COM port IP-8: {e}")
        
        return com_ip

    def update_server_conn_error2(self, status):  # for update connection if IOT is On
        print(f"[DEBUG] Updating server connection error 2 status: {status}")  
        self.execute_query("UPDATE connection SET status = %s WHERE machine_name = 'Machine2'",(status,), commit=True)

    def update_server_conn_error3(self, status):  # for update connection if IOT is On
        print(f"[DEBUG] Updating server connection error 3 status: {status}")  
        self.execute_query("UPDATE connection SET status = %s WHERE machine_name = 'Machine3'",(status,), commit=True)

    def update_server_conn_error4(self, status):  # for update connection if IOT is On
        print(f"[DEBUG] Updating server connection error 4 status: {status}")  
        self.execute_query("UPDATE connection SET status = %s WHERE machine_name = 'Machine4'",(status,), commit=True)

    def update_server_conn_error5(self, status):  # for update connection if IOT is On
        print(f"[DEBUG] Updating server connection error 5 status: {status}")  
        self.execute_query("UPDATE connection SET status = %s WHERE machine_name = 'Machine5'",(status,), commit=True)

    def update_server_conn_error6(self, status):  # for update connection if IOT is On
        print(f"[DEBUG] Updating server connection error 6 status: {status}")  
        self.execute_query("UPDATE connection SET status = %s WHERE machine_name = 'Machine6'",(status,), commit=True)

    def update_server_conn_error7(self, status):  # for update connection if IOT is On
        print(f"[DEBUG] Updating server connection error 7 status: {status}")  
        self.execute_query("UPDATE connection SET status = %s WHERE machine_name = 'Machine7'",(status,), commit=True)

    def update_server_conn_error8(self, status):  # for update connection if IOT is On
        print(f"[DEBUG] Updating server connection error 8 status: {status}")  
        self.execute_query("UPDATE connection SET status = %s WHERE machine_name = 'Machine8'",(status,), commit=True)
    
    def update_server_conn_error9(self, status):  # for update connection if IOT is On
        print(f"[DEBUG] Updating server connection error 9 status: {status}")  
        self.execute_query("UPDATE connection SET status = %s WHERE machine_name = 'Machine9'",(status,), commit=True)
    
    def get_plant_id(self, ip_addr):
        print(f"[DEBUG] Getting Machine ID for IP: {ip_addr}")

        plant_id = None  # Initialize plant_id to avoid referencing an undefined variable  

        query = "SELECT plant_id_id FROM connection WHERE ip_address = %s"  
        result = self.execute_query(query, (ip_addr,), fetch=True)  

        if result:  # Ensure result is not None or empty  
            plant_id = int(result[0])  # Extract integer from tuple
            print(f"[DEBUG] Found plant_id: {plant_id} for IP: {ip_addr}")
        else:
            print(f"[WARNING] No plant_id found for IP: {ip_addr}") 

        return plant_id

    import json
    from datetime import datetime

    def insert_into_database(self, key_value_pair, ip_addr, plant_id):
        """Insert data into the database with dynamic key-value pairs."""
        print("1. Inserting into database...")

        print(f"2. Key value pair: {key_value_pair}, IP address: {ip_addr}, Plant ID: {plant_id}")
        print("3. Types of input dictionary:", type(key_value_pair))

        # Extract IP address from tuple if needed
        print("qwertyuiopasdfghjklzxcvbnm",ip_addr)
        if isinstance(ip_addr, tuple):  
            ip_addr = ip_addr[0]
        print("4. Processed IP Address:", ip_addr)

        # ✅ Fix the JSON format issue
        if isinstance(key_value_pair, str):
            try:
                # Ensure `key_value_pair` is a valid JSON string
                key_value_pair = key_value_pair.replace("}{", "},{")  # Fix concatenated JSON issue
                key_value_pair = "[" + key_value_pair + "]"  # Convert to list format
                key_value_pair = json.loads(key_value_pair)[0]  # Extract first valid JSON object
            except json.JSONDecodeError as e:
                print(f"[ERROR] Invalid JSON format: {e}")
                return False

        print("5. Data dictionary:", key_value_pair)

        if not self.ensure_connection():
            print("[ERROR] Failed to ensure database connection")
            return False

        values = list(key_value_pair.values())
        print("6. Extracted values:", values)

    
        # ✅ Fetch IP Address ID from `connection` table
        try:
            query = "SELECT id FROM connection WHERE ip_address = %s"
            result = self.execute_query(query, (ip_addr,), fetch=True)

            if result:
                ip_address_id = result[0]  # Extract ID from tuple
                print("7. Fetched ip_address_id:", ip_address_id)
            else:
                print("[ERROR] No matching record found in 'connection' table for IP:", ip_addr)
                return False

        except Exception as e:
            print(f"[ERROR] Failed to fetch IP address ID: {e}")
            return False

        print("8. IP address ID:", ip_address_id)

        # ✅ Check and Fix `plant_id`
        if plant_id is None:
            try:
                plant_query = "SELECT plant_id_id FROM connection LIMIT 1"  # Modify as per your DB
                plant_result = self.execute_query(plant_query, fetch=True)
                if plant_result:
                    plant_id = plant_result[0]
                    print("9. Fetched default plant_id:", plant_id)
                else:
                    print("[ERROR] No valid `plant_id` found!")
                    return False
            except Exception as e:
                print(f"[ERROR] Failed to fetch `plant_id`: {e}")
                return False

        print("10. Final Plant ID:", plant_id)

        # Get current timestamp
        current_dt_tm = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        print("11. Current Date Time:", current_dt_tm)

        # ✅ Insert Data into `local_data` table
        try:
            insert_query = """
                INSERT INTO local_data 
                (value1, value2, value3, value4, value5, value6, value7, value8, ip_address_id, plant_id_id, created_at) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            self.execute_query(
                insert_query, 
                (values[0], values[1], values[2], values[3], values[4], values[5], values[6], values[7], ip_address_id, plant_id, current_dt_tm), 
                commit=True
            )

            print("[DEBUG] Successfully inserted data ✅")
            return True
        except Exception as e:
            print(f"[ERROR] Failed to insert data: {e}")
            self.log_error_details(e)
            return False
        

    def start_connection_monitor(self):
        """Start a thread to monitor and maintain the database connection"""
        import threading
        
        def monitor_connection():
            while True:
                if not self.ensure_connection():
                    print("[WARNING] Lost database connection. Attempting to reconnect...")
                else:
                    # Perform a simple query to keep the connection alive
                    try:
                        self.execute_query("SELECT 1", fetch=True)
                    except:
                        pass
                time.sleep(30)  # Check every 30 seconds
        
        monitor_thread = threading.Thread(target=monitor_connection, daemon=True)
        monitor_thread.name = "DB-Connection-Monitor"
        monitor_thread.start()
        print("[DEBUG] Database connection monitoring thread started")
    
    def close(self):
        """Close all database resources properly"""
        if self.con and self.con.is_connected():
            try:
                if self.cursor:
                    self.cursor.close()
                self.con.close()
                print("[DEBUG] Database resources closed properly")
            except Error as e:
                print(f"[ERROR] Error while closing database resources: {e}")

def __init__(self):
    print(f"[DEBUG] Initializing DatabaseCommunication at {datetime.now().strftime(self.formatter)}")
    self.con = None
    self.cursor = None
    try:
        self.connect_to_database()
        self.start_connection_monitor()  # Start the connection monitor
    except Exception as e:
        print(f"[ERROR] Database initialization failed: {e}")
