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

def send_data_to_server(data):
    """Send data to the PID API server."""
    try:
        logger.info(f"Sending payload: {json.dumps(data, indent=4)}")  # Debugging log
        response = requests.post(API_URL, json=data, headers={'Content-Type': 'application/json'}, timeout=10)
        logger.info(f"API Response: {response.status_code}, Response Body: {response.text}")  # Log response

        if response.status_code == 201:
            logger.info("Data sent successfully to PID API.")
            return True
        else:
            logger.warning(f"Failed to send data. Status: {response.status_code}")
            return False
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
            if send_data_to_server(data):
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
    """Main function to fetch local data and send it to the PID API."""
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

                        if send_data_to_server(payload):
                            cursor.execute("DELETE FROM local_data WHERE id = %s", (row["id"],))
                            connection.commit()
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
