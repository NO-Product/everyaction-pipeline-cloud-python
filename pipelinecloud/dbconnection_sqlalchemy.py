from msal import ConfidentialClientApplication
import os
import logging
import jwt
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import urllib
import pem
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# Configuration values for authentication and database connection
AUTHORITY_HOST_URI = "https://login.microsoftonline.com"
TENANT = os.getenv("TENANT_ID")
RESOURCE_URI = "https://database.windows.net/"
APPLICATION_ID = os.getenv("APPLICATION_ID")
CLIENT_CERT_THUMBPRINT = os.getenv("CLIENT_CERT_THUMBPRINT")
CERT_FILE = os.getenv("CLIENT_CERT_PATH")
SQL_SERVER = os.getenv("DATABASE_SERVER")
DATABASE = os.getenv("DATABASE_NAME")

# Check for missing environment variables
required_vars = {
    "TENANT_ID": TENANT,
    "APPLICATION_ID": APPLICATION_ID,
    "CLIENT_CERT_THUMBPRINT": CLIENT_CERT_THUMBPRINT,
    "CLIENT_CERT_PATH": CERT_FILE,
    "DATABASE_SERVER": SQL_SERVER,
    "DATABASE_NAME": DATABASE,
}

for var_name, var_value in required_vars.items():
    if not var_value:
        raise EnvironmentError(f"Environment variable {var_name} is not set.")

# Set up logging to display debug information
logging.basicConfig(level=logging.DEBUG)


def authenticate_client_cert():
    """
    Authenticates the application using a service principal with a certificate.

    Returns:
        dict: A dictionary containing the authentication result, including the access token.

    Raises:
        Exception: If the token acquisition fails.
    """
    authority_uri = AUTHORITY_HOST_URI + "/" + TENANT

    # Parse the PEM file to extract the client certificate
    certs = pem.parse_file(CERT_FILE)
    client_cert = str(certs[0])

    # Initialize the MSAL ConfidentialClientApplication with the client certificate
    app = ConfidentialClientApplication(
        client_id=APPLICATION_ID,
        authority=authority_uri,
        client_credential={
            "private_key": client_cert,
            "thumbprint": CLIENT_CERT_THUMBPRINT,
        },
    )

    # Acquire an access token for the specified resource
    result = app.acquire_token_for_client(scopes=[RESOURCE_URI + "/.default"])

    if "access_token" in result:
        logging.debug("Token acquired: %s", result)
        return result
    else:
        logging.error("Failed to acquire token: %s", result.get("error_description"))
        raise Exception("Failed to acquire token")


def get_sqlalchemy_engine(token):
    """
    Create a SQLAlchemy engine using the Azure AD token.
    """
    # Construct the connection string with the token
    connection_string = (
        f"Driver={{ODBC Driver 18 for SQL Server}};"
        f"Server={SQL_SERVER};"
        f"Database={DATABASE};"
        "Authentication=ActiveDirectoryAccessToken;"
        f"AccessToken={token}"
    )

    # URL encode the connection string
    encoded_connection_string = urllib.parse.quote_plus(connection_string)

    # Log the encoded connection string for debugging
    logging.debug("Encoded connection string: %s", encoded_connection_string)

    # Create the SQLAlchemy engine
    engine = create_engine(
        f"mssql+pyodbc:///?odbc_connect={encoded_connection_string}", echo=True
    )
    return engine


def connect_to_database():
    """
    Connect to the database using SQLAlchemy and the access token obtained from Azure AD.
    """
    # Obtain the authentication dictionary containing the access token
    authDict = authenticate_client_cert()

    # Log the available keys in the authentication dictionary
    logging.debug("Available keys in authDict: %s", authDict.keys())

    # Log the access token and its expiration information
    logging.debug("Access Token: %s", authDict["access_token"])
    logging.debug("Your Token Will Expire on: %s", authDict["expires_in"])
    logging.debug("Your Token Expires in: %s", authDict["expires_in"])

    # Decode the JWT access token to inspect its claims
    try:
        decoded_token = jwt.decode(
            authDict["access_token"], options={"verify_signature": False}
        )
        logging.debug("Decoded Token Claims: %s", decoded_token)
    except Exception as e:
        logging.error("Error decoding token: %s", e)

    # Use SQLAlchemy to connect and query
    try:
        engine = get_sqlalchemy_engine(authDict["access_token"])
        Session = sessionmaker(bind=engine)
        session = Session()

        # Call the placeholder function to interact with the database
        interact_with_database(session)

    except Exception as e:
        logging.error("Error connecting to SQL Server with SQLAlchemy: %s", e)


def interact_with_database(session):
    """
    Placeholder function to interact with the database.
    Fetches a list of tables as an example.
    """
    try:
        # Example query to fetch a list of tables
        result = session.execute(
            text(
                "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE';"
            )
        )
        tables = result.fetchall()
        logging.info("Tables in the database:")
        for table in tables:
            logging.info(table[0])

        # Additional example queries (commented out)
        # result = session.execute(text("SELECT COUNT(*) FROM some_table;"))
        # count = result.fetchone()
        # logging.info("Number of rows in some_table: %s", count[0])

        # result = session.execute(text("SELECT TOP 10 * FROM some_table;"))
        # rows = result.fetchall()
        # for row in rows:
        #     logging.info(row)

    except Exception as e:
        logging.error("Error executing query: %s", e)


if __name__ == "__main__":
    connect_to_database()
