import mysql.connector
import requests
import logging
import traceback
import time
import uuid
import platform

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data_transfer.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def generate_device_id():
    """
    Generate a unique device identifier
    """
    try:
        system_info = f"{platform.node()}_{platform.system()}_{platform.release()}"
        return str(uuid.uuid5(uuid.NAMESPACE_DNS, system_info))
    except Exception as e:
        logger.error(f"Error generating device ID: {e}")
        return str(uuid.uuid4())

def transfer_local_data_to_pid_data(api_url):
    """
    Transfer data from local database to PID data via API
    """
    # Database connection parameters
    db_config = {
        'host': 'localhost',  # Replace with your local database host
        'user': 'root',       # Replace with your database username
        'password': '',        # Replace with your database password
        'database': 'edmp_irms'  # Replace with your local database name
    }

    try:
        # Establish database connection
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)

        # Fetch local data
        cursor.execute("""
            SELECT id, ip_address_id, plant_id_id, value1, value2, value3, 
                   value4, value5, value6 
            FROM local_data
        """)
        local_data_rows = cursor.fetchall()

        if not local_data_rows:
            logger.info("No data found in local_data table")
            return

        # Fetch field links to map local data to pid_data fields
        cursor.execute("""
            SELECT fl.field_name, c.ip_address, c.id as connection_id
            FROM field_link fl
            JOIN connection c ON fl.ip_address_id = c.id
        """)
        field_links = cursor.fetchall()

        # Process each local data row
        for local_row in local_data_rows:
            # Prepare data for API
            api_data = {
                'device_id': generate_device_id(),
                'ip_address': local_row['ip_address'],
                'plant_id': local_row['plant_id']
            }

            # Values from local data
            local_values = [
                local_row['value1'], local_row['value2'], local_row['value3'],
                local_row['value4'], local_row['value5'], local_row['value6']
            ]

            # Map local values to PID data fields
            for i, link in enumerate(field_links):
                if i < len(local_values):
                    api_data[link['field_name']] = local_values[i]

            # Send data to API
            try:
                response = requests.post(
                    api_url, 
                    json=api_data,
                    headers={
                        'Content-Type': 'application/json',
                        'User-Agent': f'LocalDataTransfer/1.0 (Device:{api_data["device_id"]})'
                    },
                    timeout=10
                )

                # Log response and handle success/failure
                if response.status_code == 201:
                    logger.info(f"Successfully sent data for IP {local_row['ip_address']}")
                    
                    # Optionally, delete the processed row from local database
                    # Uncomment if you want to remove processed entries
                    # cursor.execute("DELETE FROM local_data WHERE id = %s", (local_row['id'],))
                    # connection.commit()
                else:
                    logger.warning(f"Failed to send data. Status: {response.status_code}")
                    logger.warning(f"Response: {response.text}")

            except requests.RequestException as e:
                logger.error(f"API Request Error: {e}")
                logger.error(traceback.format_exc())

    except mysql.connector.Error as db_error:
        logger.error(f"Database Error: {db_error}")
        logger.error(traceback.format_exc())

    except Exception as e:
        logger.error(f"Unexpected Error: {e}")
        logger.error(traceback.format_exc())

    finally:
        # Ensure connections are closed
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals() and connection.is_connected():
            connection.close()

def main():
    # API endpoint for PID data
    API_URL = 'http://localhost:8000/api/local-data/'
    
    logger.info("Local Data Transfer Application Started")
    logger.info(f"Target API Endpoint: {API_URL}")

    # Continuous data transfer with error resilience
    while True:
        try:
            transfer_local_data_to_pid_data(API_URL)
        except Exception as e:
            logger.critical(f"Critical error in main loop: {e}")
        
        # Wait before next transfer (adjust as needed)
        sleep_time = 60  # 1 minutes
        logger.info(f"Waiting {sleep_time} seconds before next data transfer")
        time.sleep(sleep_time)

if __name__ == "__main__":
    main()