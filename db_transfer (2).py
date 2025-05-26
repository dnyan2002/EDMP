import mysql.connector
import requests
import logging
import json
import time
import traceback

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

API_URL = 'http://localhost:8000/api/pid-data/'  # Correct API endpoint

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'edmp_irms'
}

def check_internet():
    """Check if the internet is available."""
    try:
        requests.get("https://www.google.com", timeout=5)
        return True
    except requests.RequestException:
        return False

def store_pending_data(data):
    """Store unsent data in a local table for later retry."""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()
        query = "INSERT INTO pending_data (json_data) VALUES (%s)"
        cursor.execute(query, (json.dumps(data),))
        connection.commit()
        logger.info("Stored unsent data for retry.")
    except mysql.connector.Error as e:
        logger.error(f"Database error storing pending data: {e}")
    finally:
        cursor.close()
        connection.close()

def get_current_or_create_row():
    """Get the current row ID where data should be filled, or create a new row if needed."""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor(dictionary=True)
        
        # Get the latest row from pid_data
        cursor.execute("SELECT * FROM pid_data ORDER BY id DESC LIMIT 1")
        latest_row = cursor.fetchone()
        
        if latest_row is None:
            # No rows exist, create the first row
            cursor.execute("INSERT INTO pid_data () VALUES ()")
            connection.commit()
            return cursor.lastrowid
        
        return latest_row['id']
        
    except mysql.connector.Error as e:
        logger.error(f"Database error getting current row: {e}")
        return None
    finally:
        cursor.close()
        connection.close()

def check_if_column_filled(row_id, column_name):
    """Check if a specific column in a row already has a value (not NULL)."""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        query = f"SELECT {column_name} FROM pid_data WHERE id = %s"
        cursor.execute(query, (row_id,))
        result = cursor.fetchone()
        
        if result and result[0] is not None:
            return True  # Column has a value
        return False  # Column is NULL or empty
        
    except mysql.connector.Error as e:
        logger.error(f"Database error checking column: {e}")
        return False
    finally:
        cursor.close()
        connection.close()

def create_new_row():
    """Create a new empty row in pid_data and return its ID."""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        cursor.execute("INSERT INTO pid_data () VALUES ()")
        connection.commit()
        new_row_id = cursor.lastrowid
        logger.info(f"Created new row with ID: {new_row_id}")
        return new_row_id
        
    except mysql.connector.Error as e:
        logger.error(f"Database error creating new row: {e}")
        return None
    finally:
        cursor.close()
        connection.close()

def send_data_to_server_with_row_logic(data):
    """Send data to fill one row at a time based on the new logic."""
    try:
        # Get current row ID
        current_row_id = get_current_or_create_row()
        if current_row_id is None:
            logger.error("Could not get or create current row")
            return False
        
        # Check which columns can be filled in the current row
        columns_to_fill = {}
        need_new_row = False
        
        for field_name, field_value in data.items():
            if field_name == 'plant_id':  # Skip plant_id as it's not a column in pid_data
                continue
                
            if field_value is not None:  # Only process non-null values
                if not check_if_column_filled(current_row_id, field_name):
                    # Column is empty, can fill it
                    columns_to_fill[field_name] = field_value
                else:
                    # Column already has data, need a new row
                    need_new_row = True
                    break
        
        # If we need a new row because current row columns are filled
        if need_new_row:
            current_row_id = create_new_row()
            if current_row_id is None:
                logger.error("Could not create new row")
                return False
            
            # Reset columns_to_fill for the new row
            columns_to_fill = {}
            for field_name, field_value in data.items():
                if field_name != 'plant_id' and field_value is not None:
                    columns_to_fill[field_name] = field_value
        
        # Prepare the update payload
        if columns_to_fill:
            update_payload = {
                'id': current_row_id,
                **columns_to_fill
            }
            
            logger.info(f"Updating row {current_row_id} with payload: {json.dumps(update_payload, indent=4)}")
            
            # Send to API
            response = requests.put(f"{API_URL}{current_row_id}/", json=update_payload, 
                                  headers={'Content-Type': 'application/json'}, timeout=10)
            
            logger.info(f"API Response: {response.status_code}, Response Body: {response.text}")
            
            if response.status_code in [200, 201]:
                logger.info(f"Data successfully updated in row {current_row_id}")
                return True
            else:
                logger.warning(f"Failed to update data. Status: {response.status_code}")
                return False
        else:
            logger.info("No new data to fill in current row")
            return True
            
    except requests.RequestException as e:
        logger.error(f"Error sending data to server: {e}")
        return False

def retry_pending_data():
    """Retry sending previously failed data."""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor(dictionary=True)

        cursor.execute("SELECT id, json_data FROM pending_data")
        pending_rows = cursor.fetchall()

        for row in pending_rows:
            data = json.loads(row['json_data'])
            if send_data_to_server_with_row_logic(data):
                cursor.execute("DELETE FROM pending_data WHERE id = %s", (row['id'],))
                connection.commit()
                logger.info(f"Successfully retried and deleted pending entry ID {row['id']}.")

    except mysql.connector.Error as e:
        logger.error(f"Database error retrying pending data: {e}")
    finally:
        cursor.close()
        connection.close()

def get_field_mapping():
    """Fetch field mappings between local_data fields and pid_data fields."""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor(dictionary=True)

        cursor.execute("SELECT ip_address_id, field_name, field_description FROM field_link")
        field_mappings = cursor.fetchall()

        mapping = {}
        for row in field_mappings:
            ip_address = row['ip_address_id']
            if ip_address not in mapping:
                mapping[ip_address] = {}
            mapping[ip_address][row['field_name']] = row['field_description']
        
        return mapping

    except mysql.connector.Error as e:
        logger.error(f"Database error fetching field mappings: {e}")
        return {}

    finally:
        cursor.close()
        connection.close()

def process_and_send_data():
    """Main function to fetch local data and send it to the PID API with row-by-row logic."""
    field_mapping = get_field_mapping()  # Fetch the latest field mappings

    while True:
        if check_internet():
            retry_pending_data()  # Retry previously failed data first

            try:
                connection = mysql.connector.connect(**DB_CONFIG)
                cursor = connection.cursor(dictionary=True)

                cursor.execute("""
                    SELECT id, ip_address_id, plant_id_id, value1, value2, value3, value4, value5, value6
                    FROM local_data
                    WHERE created_at <= NOW() - INTERVAL 1 MINUTE
                """)
                data_rows = cursor.fetchall()
                
                if data_rows:
                    for row in data_rows:
                        ip_address = row["ip_address_id"]
                        mapped_fields = field_mapping.get(ip_address, {})  # Get the mapping for this IP

                        payload = {"plant_id": row["plant_id_id"]}

                        # Map local_data values to corresponding pid_data fields
                        for field, pid_field in mapped_fields.items():
                            if field in row:
                                payload[pid_field] = row[field]

                        if send_data_to_server_with_row_logic(payload):
                            cursor.execute("DELETE FROM local_data WHERE id = %s", (row["id"],))
                            connection.commit()
                            logger.info(f"Successfully processed and deleted local_data ID {row['id']}")
                        else:
                            store_pending_data(payload)

                else:
                    logger.info("No new local data to send.")

            except mysql.connector.Error as e:
                logger.error(f"Database error: {e}")
            finally:
                cursor.close()
                connection.close()

        else:
            logger.warning("Internet not available. Storing data for later.")

        time.sleep(60)  # Check every 1 minute

if __name__ == "__main__":
    process_and_send_data()