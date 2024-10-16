import os
import logging
import pem
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# Set up logging to display debug information
logging.basicConfig(level=logging.INFO)

# Required environment variables
required_vars = {
    "DATABASE_SERVER": os.getenv("DATABASE_SERVER"),
    "DATABASE_NAME": os.getenv("DATABASE_NAME"),
    "TENANT_ID": os.getenv("TENANT_ID"),
    "APPLICATION_ID": os.getenv("APPLICATION_ID"),
    "CLIENT_CERT_PATH": os.getenv("CLIENT_CERT_PATH"),
    "CLIENT_CERT_THUMBPRINT": os.getenv("CLIENT_CERT_THUMBPRINT"),
}


def verify_env_vars():
    """
    Verify that all required environment variables are set.
    """
    missing_vars = [
        var_name for var_name, var_value in required_vars.items() if not var_value
    ]
    if missing_vars:
        logging.error(
            "The following environment variables are not set: %s",
            ", ".join(missing_vars),
        )
        return False
    logging.info("All required environment variables are set.")
    return True


def verify_pem_file():
    """
    Verify that the PEM file exists and contains a valid private key.
    """
    cert_path = required_vars["CLIENT_CERT_PATH"]
    if not os.path.exists(cert_path):
        logging.error("PEM file not found at path: %s", cert_path)
        return False

    try:
        certs = pem.parse_file(cert_path)
        if not certs:
            logging.error("PEM file is empty or invalid: %s", cert_path)
            return False

        # Check if the PEM file contains a valid private key
        private_key = certs[0]
        if "PRIVATE KEY" not in private_key.as_text():
            logging.error(
                "PEM file does not contain a valid private key: %s", cert_path
            )
            return False

        logging.info("PEM file contains a valid private key.")
        return True
    except Exception as e:
        logging.error("Error parsing PEM file: %s", e)
        return False


def run_precheck():
    """
    Run the precheck to verify environment variables and PEM file.
    """
    env_vars_ok = verify_env_vars()
    pem_file_ok = verify_pem_file()

    if env_vars_ok and pem_file_ok:
        logging.info("Setup verification successful.")
    else:
        logging.error("Setup verification failed. Please check the errors above.")


if __name__ == "__main__":
    run_precheck()
