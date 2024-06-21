import psycopg2
import os
import time
import json
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from dotenv import load_dotenv

load_dotenv()

# DB Configuration  --------------------------------
db_config = {
    'user': os.environ.get('DB_USER'),
    'password': os.environ.get('DB_PSW'),
    'host': os.environ.get('DB_HOST'),
    'database': os.environ.get('DB'),
}

# Google Sheets API setup -------------------------------
SCOPES = [os.environ.get('SCOPES')]
CLIENT_SECRET_FILE = os.environ.get('CLIENT_SECRET_FILE')
SPREADSHEET_ID = os.environ.get('SPREADSHEET_ID')
RANGE_NAME = os.environ.get('RANGE_NAME')
TOKEN_JSON_FILE = os.environ.get('TOKEN_JSON_FILE')

def create_table():
    try:
        connection = psycopg2.connect(**db_config)
        cursor = connection.cursor()
        create_table_query = '''
        CREATE TABLE IF NOT EXISTS person_data (
            Name VARCHAR(50) NOT NULL,
            Age INTEGER NOT NULL,
            YOB INTEGER NOT NULL,
            UNIQUE(Name, Age, YOB)
        ); '''
        cursor.execute(create_table_query)
        connection.commit()
    except psycopg2.Error as e:
        print(f"Error creating table: {e}")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def read_json(file_path):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
        return data
    except Exception as e:
        print(f"Error reading JSON file {file_path}: {e}")
        return None
    

def get_service():
    creds = None
    try:
        if os.path.exists(TOKEN_JSON_FILE):
            i = read_json(TOKEN_JSON_FILE)
            json_data = json.loads(i)
            creds = Credentials.from_authorized_user_info(json_data, SCOPES)
        # If there are no (valid) credentials available, let the user log in --------------------------------
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    CLIENT_SECRET_FILE, SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials in a json file ---------------------------
            with open(TOKEN_JSON_FILE, 'w') as token:
                json.dump(creds.to_json(), token)
    except Exception as e:
        print(f"Error obtaining credentials: {e}")

    try:
        service = build('sheets', 'v4', credentials=creds)
        return service
    except Exception as e:
        print(f"Error creating Google Sheets service: {e}")
        return None

def fetch_data(service):
    try:
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
        values = result.get('values', [])
        return values
    except Exception as e:
        print(f"Error fetching data from Google Sheets: {e}")
        return []

def get_existing_data(cursor):
    try:
        cursor.execute("SELECT * FROM person_data")
        existing_data = cursor.fetchall()
        return existing_data
    except psycopg2.Error as e:
        print(f"Error fetching existing data from database: {e}")
        return []

def update_database(data):
    try:
        connection = psycopg2.connect(**db_config)
        cursor = connection.cursor()

        existing_data = get_existing_data(cursor)
        existing_data_set = {tuple(row) for row in existing_data}

        insert_query = "INSERT INTO person_data (name, age, yob) VALUES (%s, %s, %s) ON CONFLICT (Name, Age, YOB) DO NOTHING"
        for row in data:
            if tuple(row) not in existing_data_set:
                try:
                    cursor.execute(insert_query, tuple(row))
                except Exception as e:
                    print(f"Error updating for tuple: {tuple(row)}, error: {e}")
                    pass

        connection.commit()
    except psycopg2.Error as e:
        print(f"Error connecting to the database: {e}")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
            
def main():
    service = get_service()
    if not service:
        print("Failed to create Google Sheets service. Exiting.")
        return

    previous_data = None
    create_table()
    
    while True:
        data = fetch_data(service)
        if data:
            # Skip the header row --------------------------------
            data = data[1:]
            if data != previous_data:
                print("Data updated. Transferring to database...")
                update_database(data)
                previous_data = data
            else:
                print("No updates detected.")
        else:
            print("Failed to fetch data. Retrying...")
        
        time.sleep(30)

if __name__ == '__main__':
    main()