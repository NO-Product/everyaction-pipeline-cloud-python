import logging
from pipelinecloud.precheck import run_precheck
from pipelinecloud.dbconnection_basic import connect_to_database as connect_basic
from pipelinecloud.dbconnection_sqlalchemy import (
    connect_to_database as connect_sqlalchemy,
)

# Set up logging to display debug information
logging.basicConfig(level=logging.INFO)


def full_check():
    """
    Run the precheck and both database connection methods.
    """
    logging.info("Running precheck...")
    run_precheck()

    logging.info("Running basic database connection...")
    connect_basic()

    logging.info("Running SQLAlchemy database connection...")
    connect_sqlalchemy()


if __name__ == "__main__":
    full_check()
