# Pipeline Cloud Database Connection
[![License: CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc-sa/4.0/)

This project demonstrates how to connect to a database service called Pipeline Cloud using Python. It includes two approaches: a vanilla connection using `pyodbc` and a more advanced connection using `SQLAlchemy`.

To utilise this connection method, you will require a 'headless user' (service account), that is linked with your primary Azure MFA user account. For more details on this process, you can speak with your Bonterra account manager. 

## Prerequisites

- Docker
- Docker Compose
- Poetry
- ODBC Driver 18 for SQL Server

## Why Use Poetry?

Poetry is a dependency management tool for Python that simplifies the process of managing project dependencies and virtual environments. Unlike `pip`, Poetry automatically creates and manages a virtual environment for your project, ensuring that dependencies are isolated and consistent across different environments. This makes it easier to maintain and share your project.

### Basic Poetry Commands

- **Install Poetry**: Follow the [official installation guide](https://python-poetry.org/docs/#installation) to install Poetry on your system.
- **Install Dependencies**: Run `poetry install` to install all dependencies specified in `pyproject.toml`.
- **Activate Virtual Environment**: Use `poetry shell` to activate the virtual environment.
- **Run a Script**: Use `poetry run python <script_name>.py` to run a script within the virtual environment.

## Environment Variables

To connect to the Pipeline Cloud database, you'll need to create a `.env` file in the root directory (the same level as `.env.example`). This file will store the necessary environment variables for your database connection. If you're using a Bonterra-hosted Azure SQL instance, you will receive emails from `NoReply_PipelineCloud@everyaction.com` containing the server name, database name, and a secret link to fetch your application ID, private/public key, and certificate thumbprint. Store the private key in a file named `pipelinecloud_privatenopass.pem` in the root directory.

**⚠️ Important :** If you are self-hosting Pipeline Cloud, these values should be provided by your database administrator / DevOps team. The information provided in this section specifically applies to the Bonterra-hosted scenario.

| Key                     | Sample Value                                      | Description                                      |
|-------------------------|---------------------------------------------------|--------------------------------------------------|
| `DATABASE_SERVER`       | `esv30ddbms001.database.windows.net` or `esv30pdbms002.database.windows.net` | The server address of the database. Verify the correct server in your Azure MFA user connection string (e.g., via DBeaver, Azure Data Studio). |
| `DATABASE_NAME`         | `Pipeline_*****`                                  | The name of the database. This value is typically provided in an email from `NoReply_PipelineCloud@everyaction.com` during the provisioning stage of your Pipeline Cloud instance. |
| `TENANT_ID`             | `798d7834-694a-41b4-b6cb-e5448f079f6b`            | The tenant ID for Azure authentication. This is usually a fixed value and you should use the sample value provided. |
| `APPLICATION_ID`        |            | The application ID for Azure authentication. Obtain this from the secret link provided in the email. This value is unique to your EveryAction Pipeline Cloud instance. |
| `CLIENT_CERT_PATH`      | `pipelinecloud_privatenopass.pem`                 | Path to the client certificate PEM file. Obtain your private key from the secret link provided by the EveryAction team. This value is unique to your EveryAction Azure MFA account.|
| `CLIENT_CERT_THUMBPRINT`|         | Thumbprint of the client certificate. This is provided in the secret link email and is used to verify the certificate. This value is unique to your EveryAction Azure MFA user account. |

### Important Notes:
- **Private Key File**: Ensure that `pipelinecloud_privatenopass.pem` is stored securely in the root directory and not within the `/pipelinecloud/` app directory.
- **Environment File Location**: The `.env` file should be located in the same directory as `.env.example` and the PEM file.



## Directory Structure

```
.
├── .env.example
├── pipelinecloud_privatenopass.pem
├── pyproject.toml
├── README.md
└── pipelinecloud
    ├── dbconnection_basic.py
    └── dbconnection_sqlalchemy.py
```

- **`.env.example`**: Template for environment variables.
- **`pipelinecloud_privatenopass.pem`**: Your private key file (store in the root directory).
- **`pipelinecloud/`**: Contains the Python scripts for database connection.


## Running the Application Locally

1. **Clone the Repository**: 
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. **Set Up Environment Variables**: 
   - Copy `.env.example` to `.env` and fill in your credentials.
   - Ensure `pipelinecloud_privatenopass.pem` is in the root directory.

3. **Install Dependencies**: 
   ```bash
   poetry install
   ```

4. **Run the Scripts Using Poetry**: 
   - **Precheck**: Verify that your environment variables and PEM file are set up correctly.
     ```bash
     poetry run precheck
     ```
   - **Basic Database Connection**: Run the basic connection script using `pyodbc`.
     ```bash
     poetry run connect-basic
     ```
   - **SQLAlchemy Database Connection**: Run the advanced connection script using `SQLAlchemy`.
     ```bash
     poetry run connect-sqlalchemy
     ```
   - **Run All**: Execute the precheck and both connection methods sequentially.
     ```bash
     poetry run full-check
     ```

5. **Run the Scripts Directly (Without Poetry)**:
   - **Precheck**: 
     ```bash
     python pipelinecloud/precheck.py
     ```
   - **Basic Database Connection**: 
     ```bash
     python pipelinecloud/dbconnection_basic.py
     ```
   - **SQLAlchemy Database Connection**: 
     ```bash
     python pipelinecloud/dbconnection_sqlalchemy.py
     ```

**Note**: When running scripts directly, ensure that your Python environment is set up correctly and all dependencies are installed. You may need to activate the virtual environment created by Poetry using `poetry shell`.


## Running the Application in Docker

Docker is a platform that allows you to package applications and their dependencies into a container, ensuring consistency across different environments. This setup helps verify a successful connection without being affected by your local environment. You can install Docker from the [official Docker website](https://www.docker.com/products/docker-desktop).

1. **Build and Run the Docker Container**:
   - First, ensure Docker is installed and running on your system.
   - Build and run the Docker container using Docker Compose:
     ```bash
     docker-compose up --build
     ```

   This command will build the Docker image and start the container, running the application with the default script.

2. **Switch Scripts**: 
   - By default, the application runs `dbconnection_basic.py`. To run `dbconnection_sqlalchemy.py`, modify the `CMD` in the `Dockerfile`:
     ```dockerfile
     # Change the CMD line to run the SQLAlchemy script
     CMD ["poetry", "run", "connect-sqlalchemy"]
     ```

3. **Naming the Docker Container**:
   - You can specify a name for your Docker container by adding the `--name` flag to the `docker-compose` command:
     ```bash
     docker-compose up --build --name pipelinecloud-app
     ```

## ODBC Driver 18 for SQL Server

- **Mac**: Install via Homebrew:
  ```bash
  brew tap microsoft/mssql-release https://github.com/Microsoft/homebrew-mssql-release
  brew update
  ACCEPT_EULA=Y brew install msodbcsql18
  ```

- **Windows**: Download and install from the [Microsoft ODBC Driver for SQL Server](https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server).

- **Docker**: The ODBC driver is included in the Docker image setup.

## Placeholder Function

Both scripts include a placeholder function for querying the database. Replace the example query with your specific SQL or SQLAlchemy query to fetch data and log it to the console.

## FAQ and Common Errors

### Environment Variable Not Set
Ensure all required environment variables are set in your `.env` file.

### ModuleNotFoundError
Activate the Poetry environment using `poetry shell` and ensure dependencies are installed with `poetry install`.

### ODBC Driver Not Found
Ensure ODBC Driver 18 is installed on your system. Refer to the installation instructions above.

### Connection Errors
Check your network settings and ensure the database server is accessible from your environment.

This repository provides a skeleton for connecting to the Pipeline Cloud service from EveryAction using Python. It is designed to be simple to run locally with your credentials to verify a connection can be made.


## License

This project is licensed under the Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License. For more details, see https://creativecommons.org/licenses/by-nc-sa/4.0/legalcode.