# Google Sheets to PostgreSQL Synchronization

This project synchronizes data from a Google Sheets document to a PostgreSQL database. It periodically checks for updates in the Google Sheets document and inserts new data into the PostgreSQL database.

## Prerequisites

Before running the script, ensure you have the following:

- Python 3.x installed
- PostgreSQL installed and running
- Google Sheets API credentials
- `psycopg2`, `google-auth`, `google-auth-oauthlib`, `google-auth-httplib2`, `google-api-python-client`, `python-dotenv` packages installed

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/google-sheets-to-postgresql.git
cd google-sheets-to-postgresql
```

2. Install the required packages:

```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory with the following environment variables:

```env
DB_USER=your_db_user
DB_PSW=your_db_password
DB_HOST=your_db_host
DB=your_db_name
SCOPES=https://www.googleapis.com/auth/spreadsheets.readonly
CLIENT_SECRET_FILE=path_to_your_client_secret.json
SPREADSHEET_ID=your_spreadsheet_id
RANGE_NAME=Sheet1!A1:C
TOKEN_JSON_FILE=token.json
```

## Configuration

Ensure your PostgreSQL database is configured correctly. The script uses the following configuration:

Replace the placeholder values in the `.env`, `token.json`, `client_secret.json` file with your actual auth credentials. Database details, and Google Sheets API details.

## Usage

1. Run the script:

```bash
python pipeline.py
```

The script performs the following major steps:

1. **Database Table Creation**: Creates a table named `person_data` if it does not exist.
2. **Google Sheets API Authentication**: Authenticates using the provided credentials and token file. If no credentials are found, takes the user to browser window for creating credentials.
3. **Data Fetching**: Fetches data from the specified Google Sheets document.
4. **Database Update**: Inserts new data into the PostgreSQL database if there are any updates.

## Code Overview

### Database Configuration

The database configuration is loaded from environment variables in .env file.

### Google Sheets API Setup

The Google Sheets API is set up using the provided credentials and scopes:

```python
SCOPES = [os.environ.get('SCOPES')]
CLIENT_SECRET_FILE = os.environ.get('CLIENT_SECRET_FILE')
SPREADSHEET_ID = os.environ.get('SPREADSHEET_ID')
RANGE_NAME = os.environ.get('RANGE_NAME')
TOKEN_JSON_FILE = os.environ.get('TOKEN_JSON_FILE')
```

### Table Creation

Creates the `person_data` table if it does not exist:

```python
def create_table():
    ...
```

### Reading JSON

Reads data from a JSON file:

```python
def read_json(file_path):
    ...
```

### Google Sheets Service

Gets the Google Sheets service:

```python
def get_service():
    ...
```

### Fetching Data

Fetches data from Google Sheets:

```python
def fetch_data(service):
    ...
```

### Database Update

Updates the PostgreSQL database with new data:

```python
def update_database(data):
    ...
```

### Main Function

The main function coordinates the workflow:

```python
def main():
    ...
```

## Acknowledgements

This project uses the following libraries:

- `psycopg2`
- `google-auth`
- `google-auth-oauthlib`
- `google-auth-httplib2`
- `google-api-python-client`
- `python-dotenv`